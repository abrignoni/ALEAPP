"""
Multiprocessing helpers for ALEAPP.

Importable in a spawned subprocess — no side effects at import time.
Rehydrates minimal per-plugin state and returns picklable deltas
(icons + LAVA artifact metadata) back to the parent.
"""
from __future__ import annotations

import os
import traceback
import warnings

import scripts.lavafuncs as lavafuncs
import scripts.plugin_loader as plugin_loader
from scripts.ilapfuncs import (
    check_output_types,
    icons,
    output_params_from_existing_output_folder_base,
)
from scripts.search_files import FileInfo, FileSeekerBase


class SeekerProxy(FileSeekerBase):
    """Minimal seeker for subprocess use.

    The parent resolves files_found before spawning — the child never
    needs to search. This proxy exposes file_infos so media helpers
    (check_in_media) can look up FileInfo by extracted path.

    ``data_folder`` mirrors the real FileSeekerDir/Tar/Zip attribute that
    plugins use to strip the extraction-root prefix from copied file paths
    (e.g. ``file_found.replace(seeker.data_folder, '')``).  It equals the
    ``data/`` sub-directory under the report folder base — the same value
    the parent sets when constructing the real seeker.
    """

    def __init__(
        self,
        file_infos_subset: dict[str, tuple[str, float, float]],
        all_files: list[str],
        data_folder: str = "",
    ):
        self.file_infos: dict[str, FileInfo] = {
            path: FileInfo(src, ctime, mtime)
            for path, (src, ctime, mtime) in file_infos_subset.items()
        }
        self._all_files = all_files
        self.data_folder: str = data_folder

    def search(self, filepattern, return_on_first_hit=False):
        return []

    def cleanup(self):
        pass


def run_one_plugin(payload: dict, result_queue) -> None:
    """Run a single plugin inside a subprocess.

    Expected payload keys:
        plugin_key          str
        files_found         list[str]
        category_folder     str
        wrap_text           bool
        output_folder_base  str
        input_path          str
        extracttype         str
        file_infos_subset   dict[str, tuple[str, float, float]]
        seeker_all_files    list[str]
    """
    # Ignore SIGINT in the child — Ctrl+C sends SIGINT to the whole process group,
    # which would otherwise kill the child AND trigger the parent's handler twice.
    # The parent manages child termination explicitly via proc.terminate().
    import signal as _signal
    _signal.signal(_signal.SIGINT, _signal.SIG_IGN)

    # Scope the suppression to pkg_resources only — process-global suppression
    # would mask real deprecation warnings from other modules.
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources")

    try:
        plugin_key: str = payload["plugin_key"]
        files_found: list[str] = payload.get("files_found") or []
        category_folder: str = payload["category_folder"]
        wrap_text: bool = bool(payload.get("wrap_text", True))
        output_folder_base: str = payload["output_folder_base"]
        input_path: str = payload.get("input_path") or ""
        extracttype: str = payload.get("extracttype") or ""
        file_infos_subset: dict = payload.get("file_infos_subset") or {}
        seeker_all_files: list[str] = payload.get("seeker_all_files") or []

        # Let logfunc() write to the correct file
        output_params_from_existing_output_folder_base(output_folder_base)

        # Reload PluginLoader — avoids pickling LazyLoader callables
        loader = plugin_loader.PluginLoader()
        plugin_spec = loader[plugin_key]

        seeker = SeekerProxy(
            file_infos_subset,
            seeker_all_files,
            data_folder=os.path.join(output_folder_base, "data"),
        )

        artifact_info = plugin_spec.artifact_info or {}
        output_types = artifact_info.get(
            "output_types", ["html", "tsv", "timeline", "lava", "kml"]
        )
        wants_lava = check_output_types("lava", output_types)

        if wants_lava:
            lavafuncs.lava_open_existing(output_folder_base)

        # ALEAPP plugin signature — no time_offset (Android, not iOS)
        plugin_spec.method(files_found, category_folder, seeker, wrap_text)

        # icons is the module-level dict in ilapfuncs; artifact_processor mutates it.
        # Spawn-context guarantee: each subprocess starts a fresh Python interpreter,
        # so ilapfuncs.icons begins as {} — it cannot contain entries from prior
        # plugins run in other subprocesses. dict(icons) therefore captures only
        # the icons registered by this plugin.
        icons_delta: dict[str, dict[str, str]] = dict(icons)

        # Collect LAVA artifact entries written by this plugin.
        # Picklability: each artifact dict contains only plain Python primitives.
        #   column_map       → {str: str}  (sanitized_name → original_name)
        #   object_columns   → list of {"name": str, "type": str} dicts
        #   data_views       → {str: str/bool} after sanitize_sql_name processing
        #   All other fields (name, tablename, module, record_count) are str/int.
        # No tuple keys, no non-primitive values — safe to pass through a Queue.
        lava_artifacts_delta: dict = {}
        if wants_lava and lavafuncs.lava_data:
            lava_artifacts_delta = {
                cat: list(arts)
                for cat, arts in lavafuncs.lava_data.get("artifacts", {}).items()
            }

        result_queue.put({
            "ok": True,
            "plugin_key": plugin_key,
            "icons_delta": icons_delta,
            "lava_artifacts_delta": lava_artifacts_delta,
        })

    except Exception as ex:
        result_queue.put({
            "ok": False,
            "plugin_key": payload.get("plugin_key"),
            "error": str(ex),
            "traceback": traceback.format_exc(),
        })
    finally:
        try:
            lavafuncs.lava_close_db()
        except Exception:
            pass

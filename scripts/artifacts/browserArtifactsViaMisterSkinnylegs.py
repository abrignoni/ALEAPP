import io
import pathlib
import re
import sqlite3

import mister_skinnylegs.util.profile_folder_protocols
from mister_skinnylegs import MisterSkinnylegs, iter_plugins, BrowserType
from mister_skinnylegs.util import ArtifactStorage, ArtifactStorageBinaryStream, ArtifactStorageTextStream

from scripts.ilapfuncs import artifact_processor, logfunc, check_in_embedded_media
from scripts.context import Context


class ProfileFolderType:
    app_chrome = 1
    webview = 2


PROFILE_PATH_ROW_HEADER = "Profile Path"

# Dynamically generate artifacts from Skinnylegs' plugins at runtime
__artifacts_v2__ = {
    skinny_plugin.name: {
        "name": f"Mister Skinnylegs - {skinny_plugin.name}",  # adding the prefix as some artifacts are shadowed currently
        "description": skinny_plugin.description,
        "author": "Mister Skinnylegs Contributors",   # TODO, this should also be available in skinnylegs plugins
        "creation_date": "2026-07-16",  # TODO, this should also be available in skinnylegs plugins
        "last_update_date": "2026-07-16",  # TODO, this should also be available in skinnylegs plugins
        "requirements": "mister_skinnylegs @ git+https://github.com/cclgroupltd/mister-skinnylegs.git@v0.0.15",
        "category": "Browser Artifacts",
        "notes": "Plugin automatically generated from Mister Skinnylegs plugins",
        # the path feels a bit general... but should get all the non-browser browser stuff - can make more specific if
        #  required
        "paths": "*/Default/Web Data",  # this is a good marker for any Chromium profile folder, but there may be others
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "globe"
    } for skinny_plugin, plugin_path in iter_plugins()
}

_SPEC_LOOKUP = {
    skinny_plugin.name: skinny_plugin for skinny_plugin, _ in iter_plugins()
}


def __dir__():
    return ["__artifacts_v2__"] + list(__artifacts_v2__.keys())


def __getattr__(name):
    if name in __artifacts_v2__:
        return artifact_processor(
            lambda context: process(name, context),
            injected_globals=globals(),
            injected_module_name=process.__module__,
            injected_custom_func_name=name
        )


class LeappArtifactStorageBinaryStream(ArtifactStorageBinaryStream):
    def __init__(self, source_file: str):
        super().__init__(source_file)
        self._stream = io.BytesIO()
        self._reference = None

    def write(self, data: bytes) -> int:
        return self._stream.write(data)

    def close(self) -> None:
        self._reference = check_in_embedded_media(self.source_file, self._stream.getvalue())
        self._stream.close()

    def get_file_location_reference(self) -> str:
        if not self._reference:
            raise ValueError("stream is not closed and completed")
        return self._reference

    def __enter__(self) -> "ArtifactStorageBinaryStream":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class LeappArtifactStorageTextStream(ArtifactStorageTextStream):
    def __init__(self, source_file: str):
        super().__init__(source_file)
        self._stream = io.StringIO()
        self._reference = None

    def write(self, data: str) -> int:
        return self._stream.write(data)

    def close(self) -> None:
        self._reference = check_in_embedded_media(self.source_file, self._stream.getvalue().encode("utf-8"))
        self._stream.close()

    def get_file_location_reference(self) -> str:
        if not self._reference:
            raise ValueError("stream is not closed and completed")
        return self._reference

    def __enter__(self) -> "ArtifactStorageTextStream":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class LeappArtifactStorage(ArtifactStorage):
    def get_binary_stream(self, file_name: str, source_file: str) -> ArtifactStorageBinaryStream:
        return LeappArtifactStorageBinaryStream(source_file)

    def get_text_stream(self, file_name: str, source_file: str) -> ArtifactStorageTextStream:
        return LeappArtifactStorageTextStream(source_file)


def process(plugin_name: str, context: Context):
    data_headers = [PROFILE_PATH_ROW_HEADER]
    data_rows = []
    source_files = []
    seeker = context.get_seeker()
    for hit_path in context.get_files_found():
        profile_folder = pathlib.Path(hit_path).parent

        # force the seeker to get what we need for processing
        rel_profile_path = context.get_relative_path(str(profile_folder))
        seeker.search(str(pathlib.Path("*", rel_profile_path, "**")))

        # We have to attempt to locate the cache folder as we don't know what app we're looking at
        # On modern devices they should be at:
        #   <package folder>/cache/Cache/Cache_Data
        #   <package folder>/cache/WebView/Default/HTTP Cache/Cache_Data
        # On older devices they will be at:
        #  <package folder>/cache/Cache
        #  <package folder>/cache/WebView/Default/HTTP Cache

        path_parts = list(pathlib.Path(rel_profile_path).parts)
        profile_folder_type = None
        while path_parts:
            part = path_parts.pop()
            if part == "app_chrome":
                profile_folder_type = ProfileFolderType.app_chrome
                break
            elif re.match(r"^app_\w*webview", part):
                profile_folder_type = ProfileFolderType.webview
                break

        package_path_hopefully = pathlib.Path(*path_parts)
        cache_path = None
        cache_rel_path = None
        if profile_folder_type is None:
            logfunc(f"Couldn't determine a browser profile folder type for {rel_profile_path}")
        else:
            # Try Modern location first
            if profile_folder_type == ProfileFolderType.app_chrome:
                cache_rel_path = package_path_hopefully / "cache" / "Cache" / "Cache_Data"
            elif profile_folder_type == ProfileFolderType.webview:
                cache_rel_path = package_path_hopefully / "cache" / "WebView" / "Default" / "HTTP Cache" / "Cache_Data"

            dir_set = {pathlib.Path(x).parent for x in seeker.search(str("*" / cache_rel_path / "*")) if pathlib.Path(x).is_file()}
            for d in dir_set:
                if d.name == "Cache_Data":
                    cache_path = d
                    break

            if not cache_path:
                # Try legacy location
                if profile_folder_type == ProfileFolderType.app_chrome:
                    cache_rel_path = package_path_hopefully / "cache" / "Cache"
                elif profile_folder_type == ProfileFolderType.webview:
                    cache_rel_path = package_path_hopefully / "cache" / "WebView" / "Default" / "HTTP Cache"

                dir_set = {pathlib.Path(x).parent for x in seeker.search(str("*" / cache_rel_path / "*")) if
                           pathlib.Path(x).is_file()}
                for d in dir_set:
                    if ((profile_folder_type == ProfileFolderType.app_chrome and  d.name == "Cache")
                            or (profile_folder_type == ProfileFolderType.webview and d.name == "HTTP Cache")):
                        cache_path = d
                        break

        spec = _SPEC_LOOKUP[plugin_name]
        context.get_output_params()
        try:
            result = MisterSkinnylegs.run_plugin_on_path(
                spec=spec,
                profile_path=profile_folder,
                cache_path=cache_path,
                browser_type=BrowserType.chromium,
                storage=LeappArtifactStorage(),
                log_callback=logfunc)
        except (sqlite3.Error, ValueError) as ex:
            logfunc(f"Error from {spec.name} running against {rel_profile_path}: {ex}, skipping")
            continue

        if not result.result:
            continue

        if not isinstance(result.result, list):
            raise ValueError("Can't deal with non-list results currently - contact mister_skinnylegs devs")

        for o in result.result:
            if not isinstance(o, dict):
                raise ValueError(
                    "Can't deal with anything but dictionaries results currently - contact mister_skinnylegs devs")

            for k in o.keys():
                if k not in data_headers:
                    if k in (spec.media_field_names or []):
                        data_headers.append(("Media", k))
                    else:
                        data_headers.append(k)

            o[PROFILE_PATH_ROW_HEADER] = rel_profile_path  # add the profile path in for reporting
            row = tuple(
                o[k].friendly_string
                if isinstance(o[k], mister_skinnylegs.util.profile_folder_protocols.ArtifactLocationProtocol)
                else o[k]
                for k in data_headers)
            data_rows.append(row)
            source_files.append(profile_folder)

    return data_headers, data_rows, ", ".join(str(x) for x in source_files)


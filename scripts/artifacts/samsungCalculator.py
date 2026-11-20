"""Samsung Calculator (com.sec.android.app.popupcalculator): calculation history."""

__artifacts_v2__ = {
    "samsungCalculatorHistory": {
        "name": "Samsung Calculator - History",
        "description": "Calculations kept in the Samsung Calculator history file, with the expression, the result and the angle mode. The app keeps at most 20.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-20",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Samsung Calculator",
        "notes": (
            "Read from files/calculator.data in the app private data folder of "
            "com.sec.android.app.popupcalculator, the Samsung Calculator's history list. Layout from "
            "the app's own reader and writer (the HistoriesData and History classes, decompiled with "
            "jadx from the APK in both tested images): a format version (2 on both tested files) and "
            "the entry count, both big-endian 32-bit integers, then per entry three Java writeUTF "
            "strings (modified UTF-8) followed, in version 2, by two 2-byte characters, then a list "
            "position. A file is read only when this layout ends exactly at its last byte and its "
            "version is 1 or 2; otherwise it is skipped and named in the run log. No version 1 file "
            "was available. Expression and Result are the formula and result strings the app stores "
            "(CalculatorUtils.updateHistory passes the formula, then the result). Angle Mode (as "
            "stored) is the first string: in the samsung_a166u_a16_known_20261117 app version it is 0 "
            "for a formula with no sin, cos or tan, 1 when it has one and the app is in degree mode, "
            "and 2 otherwise; Angle Mode (as stored) held 0 on every row of the tested images. Entry "
            "is the position in the file, starting at 1: the app appends new entries at the end and "
            "drops the oldest at 20, so entry 1 is the oldest kept. The app does not store a "
            "calculation whose formula repeats the last entry with the same angle mode, or a result "
            "of Infinity or NaN, so the list is not every calculation made. The history holds no "
            "time. Not reported: the two characters, which are the thousands separator and decimal "
            "character in use when the entry was saved (a comma and a full stop in every tested "
            "entry), the format version, and the list position, which the app sets to the entry count "
            "when it adds an entry (equal to the count on both tested files). Known data "
            "(samsung_a166u_a16_known_20261117): two calculations were made on 2026-11-17 at 06:25:54 "
            "and 06:26:01 UTC, per the session record, with a screenshot of the result after each. "
            "The file held the two calculations in the order made, and each result matched its "
            "screenshot. sharon_a14 held 3 entries. files/rList beside it on that image is a Java "
            "serialized list and is not read. Android User is the user of the app data folder the "
            "file is in, taken from its path (data/data is user 0); it is blank for a path outside an "
            "app data folder, and Android User held 0 on every row of the tested images."
        ),
        "paths": ("*/com.sec.android.app.popupcalculator/files/calculator.data",),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "hash",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.sec.android.app.popupcalculator | 2 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.popupcalculator | 3 rows",
        },
    },
}

import os
import struct

from scripts.artifacts.storagePathViews import canonical_path, unique_files
from scripts.ilapfuncs import artifact_processor, logfunc


class _Reader:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def take(self, size):
        if self.pos + size > len(self.data):
            raise ValueError("short file")
        chunk = self.data[self.pos:self.pos + size]
        self.pos += size
        return chunk

    def int32(self):
        return struct.unpack(">i", self.take(4))[0]

    def utf(self):
        raw = self.take(struct.unpack(">H", self.take(2))[0])
        # Java modified UTF-8: NUL as C0 80 and characters outside the BMP as surrogate pairs.
        text = raw.replace(b"\xc0\x80", b"\x00").decode("utf-8", "surrogatepass")
        return text.encode("utf-16", "surrogatepass").decode("utf-16", "replace")


def _parse(data):
    """[(angle mode, expression, result)] or None when the file does not follow the layout to its end.

    HistoriesData.save writes the version, the count, each History, then the list position; History.write
    writes three writeUTF strings and, from version 2, the grouping and decimal characters.
    """
    reader = _Reader(data)
    try:
        version = reader.int32()
        count = reader.int32()
        if version not in (1, 2) or count < 0:
            return None
        entries = []
        for _ in range(count):
            angle_mode = reader.utf()
            expression = reader.utf()
            result = reader.utf()
            if version == 2:
                reader.take(4)  # thousands separator and decimal character
            entries.append((angle_mode, expression, result))
        reader.int32()
    except (ValueError, struct.error, UnicodeDecodeError):
        return None
    return entries if reader.pos == len(data) else None


@artifact_processor
def samsungCalculatorHistory(context):
    data_list = []
    source_paths = []
    for path in unique_files(context):
        path = str(path)
        if not path.replace("\\", "/").endswith("/com.sec.android.app.popupcalculator/files/calculator.data"):
            continue
        if not os.path.isfile(path):
            continue
        with open(path, "rb") as handle:
            entries = _parse(handle.read())
        if entries is None:
            logfunc(f"Samsung Calculator: history file not read: {path}")
            continue
        source_paths.append(path)
        key, _rank = canonical_path(context.get_relative_path(path))
        parts = key.split("\x00")
        user = parts[1].rsplit(":", 1)[-1] if len(parts) >= 3 else ""
        for index, (angle_mode, expression, result) in enumerate(entries, 1):
            data_list.append((index, expression, result, angle_mode, user))
    data_headers = ("Entry", "Expression", "Result", "Angle Mode (as stored)", "Android User")
    return data_headers, data_list, "\n".join(source_paths)

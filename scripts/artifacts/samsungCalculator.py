"""Samsung Calculator (com.sec.android.app.popupcalculator): calculation history."""

__artifacts_v2__ = {
    "samsungCalculatorHistory": {
        "name": "Samsung Calculator - History",
        "description": "Calculations in the Samsung Calculator history file, with the expression and the result.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-20",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Samsung Calculator",
        "notes": (
            "Read from files/calculator.data in the app private data folder of "
            "com.sec.android.app.popupcalculator, the Samsung Calculator's history list. The app's "
            "code was not read (it is a system app and no tested extraction holds its APK), so the "
            "layout is inferred from the two tested files and checked as follows: two big-endian "
            "32-bit integers (the second is the entry count), then per entry three length-prefixed "
            "UTF-8 strings and two 2-byte characters, then one more integer. A file is read only when "
            "this layout ends exactly at its last byte; otherwise it is skipped and named in the run "
            "log. Expression and Result are the second and third strings. Entry is the position in "
            "the file, starting at 1. Not reported: the first string (0 in every tested entry), the "
            "two characters (a comma and a full stop in every tested entry), and the first and last "
            "integers, whose meaning is not established (2 and the entry count on both tested files). "
            "The history holds no time. Known data (samsung_a166u_a16_known_20261117): two "
            "calculations were made on 2026-11-17 at 06:25:54 and 06:26:01 UTC, per the session "
            "record, and the on-screen result of the second was captured in a screenshot showing 120. "
            "The file held 12+3 = 15 as entry 1 and 15×8 = 120 as entry 2, so entries are in the "
            "order made on this data. The session record names the second calculation as 7x8; the "
            "screenshot and the file both show 15×8. sharon_a14 held 3 entries. files/rList beside it "
            "on that image is a Java serialized list and is not read. Android User is the user of the "
            "app data folder the file is in, taken from its path (data/data is user 0); it held 0 on "
            "every row of the tested images."
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
        return self.take(struct.unpack(">H", self.take(2))[0]).decode("utf-8")


def _parse(data):
    """[(expression, result)] or None when the file does not follow the layout to its end."""
    reader = _Reader(data)
    try:
        reader.int32()
        count = reader.int32()
        if count < 0:
            return None
        entries = []
        for _ in range(count):
            reader.utf()
            expression = reader.utf()
            result = reader.utf()
            reader.take(4)  # two 2-byte characters
            entries.append((expression, result))
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
        for index, (expression, result) in enumerate(entries, 1):
            data_list.append((index, expression, result, user))
    data_headers = ("Entry", "Expression", "Result", "Android User")
    return data_headers, data_list, "\n".join(source_paths)

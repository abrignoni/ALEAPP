__artifacts_v2__ = {
    "SamsungGalleryLogEncodedStrings": {
        "name": "Samsung Gallery Log Encoded Strings",
        "description":  "Finds and decodes obfuscated strings in the Samsung Gallery application's "
                        "'local.db' file and its companion WAL. '#G$E' (V2/V3) strings are searched "
                        "for in each text column of each table in the database; on the tested images "
                        "they were found only in the 'log' table's '__log' column. Each row gives "
                        "the log entry's stored timestamp and category, the cell with its strings "
                        "decoded in place to preserve context, and the same cell as stored, to "
                        "compare and validate. Each Android user's copy of the database found in "
                        "the extraction (e.g. user 0 and user 150) is searched.",
        "author": "@dantitto, Claude",
        "creation_date": "2026-11-09",
        "last_update_date": "2026-11-15",
        "requirements": "none",
        "category": "Samsung Gallery",
        "notes":        "The base APKs from several versions of com.sec.android.gallery3d were "
                        "reviewed using JADX. Three encoding methods were identified within the "
                        "APKs. The earliest (V1), present in the reviewed v7.0.00.9 and v10.0.01.17 "
                        "APKs, is Base64 of the text mixed with what the code refers to as 'dummy' "
                        "characters, between a random prefix and suffix. The V2 and V3 methods use "
                        "both XOR and Base64 to obfuscate the strings, with the '#G$E' prefix "
                        "immediately followed by an integer naming the XOR key required to decode "
                        "them (reviewed v14.0.00.10 to v15.9.00.52 APKs). These keys are defined in "
                        "the code of the logging function.\n"
                        "On the tested images the strings decoded with V3 keys 4 to 7 and V2 key 3. "
                        "The other keys were not exercised.\n"
                        "When both key tables give readable text for one string, the V3 reading is "
                        "shown and Note lists both.\n"
                        "V1 has no marker, so it is searched for only in the log table's log column "
                        "(any column name ending in 'log', e.g. __log). A value is accepted only "
                        "when the decoded text holds the dummy characters, so short values can be "
                        "missed. A missed value stays as stored when another value in the same cell "
                        "decodes. Otherwise the cell is not reported.\n"
                        "No tested image held a V1 value. V1 decoding was tested only on synthetic "
                        "data built from the decompiled code.\n"
                        "Timestamp (as stored) and Category (as stored) are the log row's __timestamp "
                        "and __category values, reported as stored and not converted.\n"
                        "In the decompiled v15.9.02.2 code, DebugLogger.insertLog writes __timestamp "
                        "from System.currentTimeMillis() through TimeUtil.getIsoLocalDateTimeWithMillis "
                        "which builds the text from java.util.Date's date and time fields and sets no "
                        "time zone. On that code the value is the device's local time in the time zone "
                        "set on the device when the row was written, and no zone or offset appears to be "
                        "stored with it. A change of time zone or of daylight saving on the device "
                        "would likely change the zone of later rows, and times in the hour repeated "
                        "when a clock time zone changes could not be differentiated between. The tested "
                        "images ran earlier application versions, whose code was not reviewed for this.\n"
                        "In the same code, __category is the number the logger instance was created "
                        "with: 1 getDecodeInstance, 2 getDeleteInstance, 4 getMdeInstance, "
                        "5 getInstance(), 6 getMtpInstance, 7 getEditLocationInstance, "
                        "8 getEditDateAndTimeInstance, 9 getPppInstance, 10 getRecapInstance. These "
                        "are method names in the code, not documented meanings. No method appears to "
                        "write 3 in this version of the application.\n"
                        "Timestamp (as stored) and Category (as stored) are blank for a row from a "
                        "table without __timestamp and __category columns.\n"
                        "On the anne_a15 and sharon_a14 images, Category held the same value (2) on "
                        "every row.\n"
                        "On the tested images, Table held the same value (log) on every row, as the "
                        "strings were found only in the log table.\n"
                        "On the tested images, Column held the same value (__log) on every row, as "
                        "the strings were found only in that column.\n"
                        "On the tested images, Note was empty on every row, as every string decoded "
                        "under one key table only.\n"
                        "Android User is blank unless databases from more than one user are read.\n"
                        "The application's other databases are not searched. The decoded text is an "
                        "interpretation; the raw value is shown beside it.",
        "paths": ('*/com.sec.android.gallery3d/databases/local.db*',),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.gallery3d vc 1560100018 | 4 rows",
            "sharon_a14": "Android 14 | com.sec.android.gallery3d vc 1500100001 | 24 rows",
            "cookbook_a11": "Android 11 | com.sec.android.gallery3d vc 1410400002 | 1 row",
        },
    }
}

import base64
import binascii
import fnmatch
import re
import sqlite3

from scripts.ilapfuncs import (
    artifact_processor,
    open_sqlite_db_readonly,
    logfunc,
)
from scripts.artifacts.storagePathViews import unique_files

_APP_FOLDER_USER = (
    re.compile(r'(?:^|/)(?:user)?data/data/com\.sec\.android\.gallery3d/'),
    re.compile(r'(?:^|/)(?:user)?data/user(?:_de)?/(\d+)/com\.sec\.android\.gallery3d/'),
    re.compile(r'(?:^|/)data_mirror/data_(?:ce|de)/[^/]+/(\d+)/com\.sec\.android\.gallery3d/'),
)


def _android_user(relative_path):
    path = str(relative_path).replace('\\', '/')
    for pattern in _APP_FOLDER_USER:
        match = pattern.search(path)
        if match:
            return match.group(1) if pattern.groups else '0'
    return ''

_V2_KEYS_HEX = [
    "1122ffdf", # index 0
    "df3422d1", # index 1
    "73dd333f", # index 2
    "caccaa84", # index 3
    "1521dfdf", # index 4
    "5112fffd", # index 5
    "34333f73", # index 6
    "5ff21fea", # index 7
]

_V3_KEYS_HEX = [
    "00",   # index 0
    "01",   # index 1
    "02",   # index 2
    "03",   # index 3
    (   # index 4 (256 bytes)
        "ed464c09c7852e151056dd7a62061b79447b9965f3300c60b8b44d82be9024af",
        "ad553c64791af3ec8d749458112b38897d0180880d0f6ec65cd6fad1f10a53d4",
        "321b0ade71b9fbfffd248a8ffdf6e4ef702f02d2e992c3e39aabd948ddf0e6ec",
        "c8217feb9dfe50eebf7cee21f002c9ed69247c15988397e87c5399698ae4b4f7",
        "0b28c9713c4ed5fa0b17f243bb42c27cbee4c3cf6e7b27a0b0bfd00fe8ba2a50",
        "5dd8d641c6e1d4cbd7a56093cae58ed4ddfc037b8540bba5958139459005da82",
        "aff0eadf2b204db8249d942e3326632beedd246fdcbd106ff0ff804146cf3e8e",
        "1a6ce30bfbca9236458e4331c68df51f85711daea4f844b4d67f2e08b9fc1a20",
    ),
    (   # index 5 (256 bytes)
        "ca33c48fee6aacd18a84a81fa0155b60e377c95422a3d49f4e8c2c3008de0e47",
        "bcb5eed24692053eec127ea4bfcb68085111a9f1b4b0165d15415d508272cc14",
        "c70f96b29872e5fd1e795d49154fe32dfc15327d8177ce7b24ebd58b2fcc77b7",
        "7e2cf721792d2b1c9666e8829ec63022f39dfd423be4369d588626c99233b48c",
        "5b5bb8078380d680fed456a7f5bcdaf3ac4c85558f3d270bd39d49133260d49e",
        "c2ec0ee8453edb4da583dd54ec6f91909ad9cd0cabe4b58a9106988b6278b825",
        "4f4416d4890bb9e04f9765a6a506043759528c0270b9e118a4f46d99c728d16c",
        "fbeee51585ec60e006c922e3aa3c2f83e8994c17bb77d3f1a7efd3ac2371cfbc",
    ),
    (   # index 6 (256 bytes)
        "8b2cdc296829dedc52ba840887ef8cc373a9fff857af1971e726cd2fe2a579ad",
        "d784a47acaee510c64e5fbb76723adf4310a95b20abe7042b297be18e30b2e78",
        "5ec7715f7946a69ab6a9180e2fefc3fecf0f04c14564966b5ea463a204b48ab4",
        "aa19fce52ddea40498f58ae49ad38b9ff1454c29f953aba98170ebabf4fcbd12",
        "0a75aad69912b71a2d0e6ae2d808238940a9f513055e8da6d6afa632bc380184",
        "172d7f885ccc0e075df06c10302b493e8a16826fcdaad07c5a40ca85940dc263",
        "8fe53af558b079f038d461381ce489187572641c6b6aab13102fd8876fffebff",
        "fc923291e50e96b4424994ba6bf3c6083d12dd120ab47fd5ff9311a4d0a0d830",
    ),
    (   # index 7 (256 bytes)
        "b3ec6b69692ac8303f6f813ae72bbc8f0ee66113d4d55b32dec58fe95df37950",
        "9be9610acb4e70a2ddd366c0f2dadf6662d9f56312bf137bef7569baae7c1933",
        "4ea810a44f24f4a3e15f28aeb11f2a5efbf1fb03dff653978b2182b8e87b4c92",
        "0463b3fd4de4122d3aec16282bab52f3e6ad00ee06994b03e5625c428ed58f68",
        "d3d9bb9e4bc9f33e88f4065bf371e819131e05e275ea57b0769998231b2a07c4",
        "c0b780cff95c908c92da4428cec4ddb6013cb324e0ef3432a07e7fddd696eb97",
        "1d7f2ed18bffdacf3657dfb5dc5ff458f2ff1dd7fb9643c5fcfe301f70a41eeb",
        "bc6664e1f95031243a78d369c0d89c9b37aa664ad6ee4da6e10adfe2d6e96a1f",
    ),
]

_V2_KEYS = [bytes.fromhex(h if isinstance(h, str) else "".join(h)) for h in _V2_KEYS_HEX]
_V3_KEYS = [bytes.fromhex(h if isinstance(h, str) else "".join(h)) for h in _V3_KEYS_HEX]

_SCHEMES = [("V3", _V3_KEYS), ("V2", _V2_KEYS)]

_MARKERS = ["#G$E"]

_MARKER_TOKEN_RE = re.compile(
    r'(?:' + "|".join(re.escape(m) for m in _MARKERS) + r')'
    r'(\d{1,2})([A-Za-z0-9+/]+={0,2})'
)

_V1_DUMMY = ("●", "★", "◆")
_V1_FINGERPRINT_RE = re.compile(r'4peP|4piF|4peG|KXj|KYh|KXh|il4|imI')
_V1_PREFIX_LENS = (3, 4, 5, 6)
_V1_SUFFIX_LEN = 7
V1_TARGETS = frozenset({("log", "*log")})


def _is_v1_target(table, column):
    t, c = table.lower(), column.lower()
    return any(fnmatch.fnmatchcase(t, tp.lower()) and fnmatch.fnmatchcase(c, cp.lower())
               for tp, cp in V1_TARGETS)

_V1_TOKEN_RE = re.compile(
    r'(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{7,}(?:={1,2}[A-Za-z0-9+/]{7})?(?![A-Za-z0-9+/])'
)


def _xor(data, key):
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def _valid_utf8(raw):
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if any(ord(c) < 9 or (13 < ord(c) < 32) for c in text):
        return None
    return text


def _candidate_splits(digits, b64):
    if len(digits) == 1:
        yield int(digits), b64
    else:
        yield int(digits), b64
        yield int(digits[0]), digits[1:] + b64


def _decode_payload(idx, b64):
    try:
        raw = base64.b64decode(b64, validate=True)
    except (binascii.Error, ValueError):
        return None
    hits = []
    for label, table in _SCHEMES:
        if idx < len(table):
            text = _valid_utf8(_xor(raw, table[idx]))
            if text is not None:
                hits.append((text, label))
    return hits


def _decode_marker(digits, b64):
    for idx, payload in _candidate_splits(digits, b64):
        hits = _decode_payload(idx, payload)
        if hits:
            if len(hits) == 1:
                return hits[0][0], hits[0][1], idx, ""
            joined = " | ".join(f"{s}:{t}" for t, s in hits)
            return hits[0][0], hits[0][1], idx, f"ambiguous, candidates: {joined}"
    idx = int(digits)
    return None, "", idx, "no valid UTF-8 for any key at this index"


def _decode_cell(value):
    plain_parts = []
    scheme_keys = []
    notes = []
    last = 0
    for m in _MARKER_TOKEN_RE.finditer(value):
        gap = value[last:m.start()]
        plain_parts.append(gap)
        decoded, scheme, idx, note = _decode_marker(m.group(1), m.group(2))
        if decoded is None:
            token = m.group(0)
            plain_parts.append(token)
            scheme_keys.append(f"?[{idx}]")
            notes.append(f"index {idx}: {note}")
        else:
            plain_parts.append(decoded)
            scheme_keys.append(f"{scheme}[{idx}]")
            if note:
                notes.append(f"{scheme}[{idx}]: {note}")
        last = m.end()
    if not scheme_keys:
        return None
    tail = value[last:]
    plain_parts.append(tail)
    return "".join(plain_parts), scheme_keys, notes

def _strip_v1_dummies(text):
    for d in _V1_DUMMY:
        text = text.replace(d, "")
    return text

def _decode_v1_parts(value):
    if len(value) < (3 + 4 + _V1_SUFFIX_LEN):
        return None, "too short for V1"
    core = value[:-_V1_SUFFIX_LEN]
    for n in _V1_PREFIX_LENS:
        middle = core[n:]
        if len(middle) % 4 != 0:
            continue
        if not re.fullmatch(r'[A-Za-z0-9+/]+={0,2}', middle):
            continue
        try:
            raw = base64.b64decode(middle, validate=True)
        except (binascii.Error, ValueError):
            continue
        text = _valid_utf8(raw)
        if text is not None and any(d in text for d in _V1_DUMMY):
            cleaned = _strip_v1_dummies(text)
            if cleaned:
                return cleaned, n
    return None, "no V1 interpretation"


def _find_v1_in_run(run):
    text, n = _decode_v1_parts(run)
    if text is not None:
        return 0, len(run), text, f"V1 (prefix={n})"
    if "=" in run:
        head = run.split("=", 1)[0]
        text, n = _decode_v1_parts(head)
        if text is not None:
            return 0, len(head), text, f"V1 (prefix={n})"
    return None


def _decode_cell_v1(value):
    plain_parts = []
    scheme_keys = []
    notes = []
    last = 0
    for m in _V1_TOKEN_RE.finditer(value):
        run = m.group(0)
        if not _V1_FINGERPRINT_RE.search(run):
            continue
        found = _find_v1_in_run(run)
        if found is None:
            continue
        s, e, decoded, note = found
        start, end = m.start() + s, m.start() + e
        gap = value[last:start]
        plain_parts.append(gap)
        plain_parts.append(decoded)
        scheme_keys.append("V1")
        notes.append(note)
        last = end
    if not scheme_keys:
        return None
    tail = value[last:]
    plain_parts.append(tail)
    return "".join(plain_parts), scheme_keys, notes


@artifact_processor
def SamsungGalleryLogEncodedStrings(context):
    data_list = []
    sources = []
    users_read = []
    marker_substrings = tuple(_MARKERS)
    for file_found in unique_files(context):
        file_found = str(file_found)
        if file_found.endswith("-wal") or file_found.endswith("-shm"):
            continue
        if not file_found.lower().endswith(".db"):
            continue
        user = _android_user(context.get_relative_path(file_found))

        db = open_sqlite_db_readonly(file_found)
        if db is None:
            continue
        try:
            db.text_factory = lambda b: b.decode("utf-8", "replace")
            cur = db.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cur.fetchall()]
        except sqlite3.Error as exc:
            logfunc(f"[SamsungGalleryLogEncodedStrings] could not read {file_found}: {exc}")
            db.close()
            continue
        users_read.append(user)

        for table in tables:
            try:
                cur.execute(f'PRAGMA table_info("{table}")')
                cols = [r[1] for r in cur.fetchall()]
                lower = [c.lower() for c in cols]
                ts_at = lower.index("__timestamp") if "__timestamp" in lower else None
                cat_at = lower.index("__category") if "__category" in lower else None
                v1_cols = {c for c in cols if _is_v1_target(table, c)}
                try:
                    cur.execute(f'SELECT rowid, * FROM "{table}"')
                except sqlite3.Error:
                    cur.execute(f'SELECT NULL AS rowid, * FROM "{table}"')
                rows = cur.fetchall()
            except sqlite3.Error as exc:
                logfunc(f"[SamsungGalleryLogEncodedStrings] skip {file_found}:{table}: {exc}")
                continue

            for row in rows:
                rowid = row[0]
                stamp = row[1 + ts_at] if ts_at is not None else ""
                category = row[1 + cat_at] if cat_at is not None else ""
                for col, val in zip(cols, row[1:]):
                    if not isinstance(val, str):
                        continue
                    if any(mk in val for mk in marker_substrings):
                        result = _decode_cell(val)
                        if result is not None:
                            decoded, scheme_keys, notes = result
                            if file_found not in sources:
                                sources.append(file_found)
                            data_list.append((stamp, category, table, col, rowid, decoded, val,
                                              ", ".join(scheme_keys), " | ".join(notes), user))

                    if col in v1_cols \
                            and not any(mk in val for mk in marker_substrings):
                        result = _decode_cell_v1(val)
                        if result is not None:
                            decoded, scheme_keys, notes = result
                            if file_found not in sources:
                                sources.append(file_found)
                            data_list.append((stamp, category, table, col, rowid, decoded, val,
                                              ", ".join(scheme_keys), " | ".join(notes), user))
        db.close()

    data_headers = (
        "Timestamp (as stored)",
        "Category (as stored)",
        "Table",
        "Column",
        "Row ID",
        "Decoded (in context)",
        "Raw (obfuscated)",
        "Scheme/key",
        "Note",
        "Android User",
    )
    if len(set(users_read)) < 2:
        data_list = [row[:-1] + ('',) for row in data_list]
    source_path = "\n".join(sources)
    return data_headers, data_list, source_path

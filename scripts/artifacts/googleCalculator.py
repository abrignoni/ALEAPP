__artifacts_v2__ = {
    "google_calculator_history": {
        "name": "Google Calculator - History",
        "description": "Expressions the Google Calculator app saved in Expressions.db, "
                       "decoded to text, with the timeStamp stored on each row.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Google Calculator",
        "notes": "Read from the expressions table of "
                 "com.google.android.calculator/databases/Expressions.db; the path pattern "
                 "also stages the database's sidecar files. On the tested images the database"
                 " was in rollback-journal mode with an empty journal, so reading with a "
                 "write-ahead log was not exercised. Google Calculator is closed source. On "
                 "the tested images the table definition is the same as that of the AOSP "
                 "calculator app (packages/apps/ExactCalculator, branch pie-release, commit "
                 "b1a9847d7a15762ff421ab4cff5caebf5a895257: ExpressionDB.java, "
                 "CalculatorExpr.java, KeyMaps.java, Evaluator.java) and every stored "
                 "expression parses as its format, so the rows are decoded with that source; "
                 "the source is the open-source app, not the one on the devices. The "
                 "expression column is a java.io.DataOutput serialization: a token count, "
                 "then for each token a constant (kind 0: the whole part, a flags byte, the "
                 "fraction when the flags have 0x1, the exponent when they have 0x2), an "
                 "operator (one byte from KeyMaps.toByte), or an earlier result (kind 2: an "
                 "index and its short text, shown in square brackets). An operator byte that "
                 "is not in KeyMaps.toByte is shown as [operator X]. 'Expression' joins the "
                 "tokens with no separator. Arithmetic operators, parentheses, ! and % are "
                 "the stored characters; functions and the pi constant are shown by their "
                 "KeyMaps key names (sqrt, sin, ln and so on), and the square key as ^2. The "
                 "expressions table has no result column, so no result is shown. 'Decode "
                 "Status' says whether every byte was read; a row that stops early shows the "
                 "text read before it stopped. 'Saved' is timeStamp, shown in UTC; in AOSP, "
                 "ExpressionDB sets it to System.currentTimeMillis() when the row is added, "
                 "and the times were not compared with known data. 'In History' is Yes for a "
                 "positive row id; in AOSP, Evaluator adds an expression with a positive id "
                 "when it goes into the history and a negative one otherwise. This was not "
                 "checked against the Google app's history screen, and no negative id occurs "
                 "on the tested images. 'Degree Mode' and 'Long Timeout' are the values 2 and"
                 " 1 in flags (ExpressionDB.RowData). When more than one database is found, a"
                 " Source File column names the database of each row. Only numeric constants "
                 "and the + and - operators occur on the tested images; a decimal fraction "
                 "occurs on samsungs20_a13. The exponent, function and earlier-result tokens "
                 "are decoded from the source and were not exercised. The decode reads every "
                 "stored byte on the 5 tested rows. On the tested images every row has a "
                 "positive id, the degree-mode value set and the long-timeout value clear, so"
                 " the No side of In History and Degree Mode and the Yes side of Long Timeout"
                 " were not exercised.",
        "paths": ('*/com.google.android.calculator/databases/Expressions.db*',),
        "output_types": "standard",
        "artifact_icon": "hash",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | com.google.android.calculator | 3 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.calculator | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | com.google.android.calculator | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.calculator | 2 rows",
        },
    },
}

import os
import struct
from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records

# Token kinds (CalculatorExpr.TokenKind) and the operator bytes KeyMaps.toByte writes.
_CONSTANT, _PRE_EVAL = 0, 2
_SAW_DECIMAL, _HAS_EXPONENT = 0x1, 0x2
# Named after the KeyMaps key ids (const_pi, op_sqrt, fun_sin, ...); the arithmetic
# operators are the stored characters themselves.
_OPERATORS = {
    'p': 'pi', 'e': 'e', 'r': 'sqrt', '!': '!', '%': '%', 's': 'sin', 'c': 'cos',
    't': 'tan', 'S': 'arcsin', 'C': 'arccos', 'T': 'arctan', 'l': 'ln', 'L': 'log',
    'E': 'exp', '(': '(', ')': ')', '^': '^', '*': '*', '/': '/', '+': '+', '-': '-',
    '2': '^2',
}
_DEGREE_MODE, _LONG_TIMEOUT = 2, 1


class _Reader:
    """java.io.DataInput, big-endian, for the fields the expression format uses."""

    def __init__(self, data):
        self.data, self.pos = data, 0

    def take(self, n):
        if self.pos + n > len(self.data):
            raise ValueError('expression ends early')
        chunk = self.data[self.pos:self.pos + n]
        self.pos += n
        return chunk

    def byte(self):
        return struct.unpack('>b', self.take(1))[0]

    def int(self):
        return struct.unpack('>i', self.take(4))[0]

    def utf(self):
        # writeUTF stores modified UTF-8; the strings here are digits and short forms.
        length = struct.unpack('>H', self.take(2))[0]
        return self.take(length).decode('utf-8', 'replace')


class _DecodeError(ValueError):
    """A decode that stopped; carries the text read before it stopped."""

    def __init__(self, message, partial):
        super().__init__(message)
        self.partial = partial


def _decode(blob):
    """(text, ok) for one serialized CalculatorExpr."""
    reader = _Reader(bytes(blob))
    parts = []
    try:
        return _decode_tokens(reader, parts)
    except (ValueError, struct.error) as error:
        raise _DecodeError(str(error), ''.join(parts)) from error


def _decode_tokens(reader, parts):
    for _ in range(reader.int()):
        kind = reader.byte()
        if kind == _CONSTANT:
            whole = reader.utf()
            flags = reader.byte()
            text = whole
            if flags & _SAW_DECIMAL:
                text += '.' + reader.utf()
            if flags & _HAS_EXPONENT:
                text += f'E{reader.int()}'
            parts.append(text)
        elif kind == _PRE_EVAL:
            reader.int()  # index of the earlier expression whose result this is
            parts.append(f'[{reader.utf()}]')
        elif kind >= 0x20:
            char = chr(kind)
            parts.append(_OPERATORS.get(char, f'[operator {char}]'))
        else:
            raise ValueError(f'unknown token kind {kind}')
    return ''.join(parts), reader.pos == len(reader.data)


def _utc_ms(value):
    if not isinstance(value, int) or value <= 0:
        return ''
    try:
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


@artifact_processor
def google_calculator_history(context):
    data_headers = (('Saved', 'datetime'), 'Expression', 'In History', 'Degree Mode',
                    'Long Timeout', 'Row ID', 'Decode Status')
    data_list, sources = [], []
    for file_found in unique_files(context):
        path = str(file_found)
        if os.path.basename(path) != 'Expressions.db':
            continue
        sources.append(path)
        relative = str(context.get_relative_path(path))
        rows = get_sqlite_db_records(
            path, 'SELECT _id, expression, flags, timeStamp FROM expressions ORDER BY _id')
        for row_id, blob, flags, stamp in rows:
            if isinstance(blob, str):
                blob = blob.encode('latin-1', 'replace')
            try:
                text, complete = _decode(blob or b'')
                status = 'decoded' if complete else 'decoded, bytes left over'
            except _DecodeError as error:
                text, status = error.partial, f'not decoded: {error}'
            flags = flags if isinstance(flags, int) else 0
            data_list.append((
                _utc_ms(stamp), text, 'Yes' if isinstance(row_id, int) and row_id > 0 else 'No',
                'Yes' if flags & _DEGREE_MODE else 'No',
                'Yes' if flags & _LONG_TIMEOUT else 'No', row_id, status, relative,
            ))
    if len(sources) > 1:
        data_headers += ('Source File',)
    else:
        data_list = [row[:-1] for row in data_list]
    return data_headers, data_list, '\n'.join(sources)

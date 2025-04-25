"""
Copyright 2022, CCL Forensics

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys
import pathlib
import io
import os
import datetime
import typing
import dataclasses
from scripts.ccl import ccl_leveldb
from scripts.ccl import ccl_protobuff


__version__ = "1.0"
__description__ = """
Module for raw reading of the fcm_queued_messages.ldb leveldb in com.google.android.gms
Use this module to write parsers for individual apps"""
__contact__ = "Alex Caithness"


ProtoDecoder = ccl_protobuff.ProtoDecoder

FCM_PROTOBUFF_STRUCTURE = {
    0x08: ccl_protobuff.read_le_varint,
    0x12: lambda x: ccl_protobuff.read_embedded_protobuf(x, {

        0x12: ccl_protobuff.read_string,
        0x1A: ccl_protobuff.read_string,
        0x2A: ccl_protobuff.read_string,
        0x32: ccl_protobuff.read_string,
        0x3a: lambda y: ccl_protobuff.read_embedded_protobuf(y, {
            0x0A: ccl_protobuff.read_string,  # key
            0x12: ccl_protobuff.read_string   # value
        }),
        0x4A: ccl_protobuff.read_string,  # should be the key from leveldb
        0x88: ccl_protobuff.read_le_varint,  # ?
        0x90: ccl_protobuff.read_le_varint,  # ?
        0xE8: ccl_protobuff.read_le_varint   # ?
    }),
    0x18: ccl_protobuff.read_le_varint
}


@dataclasses.dataclass(frozen=True)
class FcmRecord:
    key: str
    timestamp: datetime.datetime
    package: str
    key_values: dict
    originating_file: os.PathLike
    is_deleted: bool


class FcmIterator:
    EPOCH = datetime.datetime(1970, 1, 1)

    def __init__(self, db_path: os.PathLike):
        self._db = ccl_leveldb.RawLevelDb(db_path)
        # Pre-populate a list of deleted keys, although that's likely to be all of them really...
        self._deleted_keys = frozenset(
            rec.key for rec in self._db.iterate_records_raw() if rec.state == ccl_leveldb.KeyState.Deleted)

    def __iter__(self) -> typing.Iterable[FcmRecord]:
        for rec in self._db.iterate_records_raw():
            if rec.state == ccl_leveldb.KeyState.Deleted:
                continue
            with io.BytesIO(rec.value) as value_f:
                # Todo: go back to ccl_protobuff and have it return objects at the top level?
                value_obj = ccl_protobuff.ProtoObject(
                    0x02, None, ccl_protobuff.read_protobuff(value_f, FCM_PROTOBUFF_STRUCTURE))

            package = value_obj[0x12][0][0x2A][0].value
            key_values = {x[0x0A][0].value: x[0x12][0].value for x in value_obj[0x12][0][0x3A]}
            key = rec.key[0:-8].decode("utf-8")

            timestamp_raw = int(key.split(":", 1)[1].split("%", 1)[0])
            timestamp = FcmIterator.EPOCH + datetime.timedelta(microseconds=timestamp_raw)

            yield FcmRecord(key, timestamp, package, key_values, rec.origin_file, rec.key in self._deleted_keys)

    def close(self):
        self._db.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main(args):
    in_dir_path = pathlib.Path(args[0])

    with FcmIterator(in_dir_path) as record_iterator:
        for x in record_iterator:
            print(x)


if __name__ == '__main__':
    main(sys.argv[1:])

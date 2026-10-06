"""Constructed reader-format Realm v10 fixtures, not SDK-produced databases.

Layout is limited to aligned scalar/reference arrays and ArrayStringShort columns
as documented in the pinned repository reader. This is a test-only emitter,
not a general Realm writer or independent confirmation of Realm Core compatibility.
"""
import pathlib
import struct


class RealmFixture:
    def __init__(self):
        self.data = bytearray(24)

    def array(self, values, refs=False):
        payload = b''.join(struct.pack('<q', v) for v in values)
        return self.node(0x47 if refs else 0x07, len(values), payload)

    def node(self, flags, count, payload):
        offset = len(self.data)
        assert offset % 8 == 0
        self.data += b'AAAA' + bytes([flags]) + count.to_bytes(3, 'big') + payload
        self.data += b'\0' * (-len(self.data) % 8)
        return offset

    def strings(self, values):
        # 64-byte slots; final byte is the Realm short-string padding count.
        width = 64
        payload = bytearray()
        for value in values:
            encoded = value.encode('utf-8')
            assert len(encoded) < width
            pad = width - 1 - len(encoded)
            payload += encoded + b'\0' * pad + bytes([pad])
        return self.node(0x0f, len(values), payload)

    def table(self, schema, rows, table_key):
        names = self.strings([name for name, _ in schema])
        codes = {'int':0, 'bool':1, 'str':2}
        types = self.array([codes[kind] for _, kind in schema])
        colkeys = self.array([i | (codes[kind] << 16) for i, (_, kind) in enumerate(schema)])
        spec = self.array([types, names, 0, 0, 0, colkeys], refs=True)
        columns = []
        for name, kind in schema:
            values = [row[name] for row in rows]
            columns.append(self.strings(values) if kind == 'str'
                           else self.array([int(value) for value in values]))
        cluster = self.array([(len(rows) << 1) | 1, *columns], refs=True)
        return self.array([spec, 0, cluster, (table_key << 1) | 1], refs=True)

    def write(self, path, tables):
        names = self.strings([name for name, _, _ in tables])
        refs = self.array([self.table(schema, rows, key) for key, (_, schema, rows) in enumerate(tables)], refs=True)
        group = self.array([names, refs], refs=True)
        self.data[:24] = struct.pack('<QQ4sBBBB', group, 0, b'T-DB', 10, 10, 0, 0)
        path = pathlib.Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self.data)
        return path


CALL_SCHEMA = [('timestamp','int'), ('type','str'), ('incoming','bool'), ('content','str'),
               ('name','str'), ('uid','str'), ('senderName','str'), ('senderUid','str'),
               ('duration','int'), ('serverCallId','str'), ('logId','str'), ('imdnId','str'),
               ('state','int'), ('readState','int'), ('reason','int')]


def call_row(label, kind, timestamp, incoming):
    # Independently declared input values; no values obtained from the parser.
    return {'timestamp':timestamp, 'type':kind, 'incoming':incoming, 'content':label,
            'name':'partner-'+label, 'uid':'uid-'+label, 'senderName':'sender-'+label,
            'senderUid':'sender-uid-'+label, 'duration':2500, 'serverCallId':'call-'+label,
            'logId':'log-'+label, 'imdnId':'imdn-'+label, 'state':1, 'readState':0, 'reason':0}


def emit(path, call_rows):
    tables = [('metadata',[('value','str')],[{'value':'synthetic'}]),
              ('class_CallLog',CALL_SCHEMA,call_rows),
              ('class_ServerFriend',[('name','str')],[{'name':'synthetic-contact'}])]
    RealmFixture().write(path, tables)
    return {name:rows for name, _, rows in tables}

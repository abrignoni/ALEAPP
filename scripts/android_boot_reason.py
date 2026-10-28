"""Boot reason entries and the persistent property store, read by Persistent Properties - Matched Text Observations.

``/data/property/persistent_properties`` is a protobuf file written by ``init`` (``PersistentProperties`` in the
Android source: a repeated field 1 of records, each record with the property name as field 1 and the value as
field 2, both strings). This module reads it directly, with no protobuf library.

The property ``persist.sys.boot.reason.history`` holds one entry per line: ``reason[,subreason],epoch seconds``
(for example ``reboot,userrequested,<seconds>``). The properties ``sys.boot.reason``, ``sys.boot.reason.last``,
``ro.boot.bootreason`` and ``persist.sys.boot.reason`` hold one ``reason[,subreason]`` without a time.

Nothing here depends on the rest of ALEAPP, and nothing is judged: an entry says what text the platform kept.
"""
from collections import namedtuple
from datetime import datetime, timezone

HISTORY_PROPERTY = 'persist.sys.boot.reason.history'
SINGLE_PROPERTIES = ('sys.boot.reason', 'sys.boot.reason.last', 'ro.boot.bootreason', 'persist.sys.boot.reason')
MAX_RECORDS = 200000
MAX_VALUE_BYTES = 1 << 20
EPOCH_FLOOR = 1230768000       # 2009-01-01
EPOCH_CEILING = 4102444800     # 2100-01-01
FACTORY_RESET_WORD = 'factory_reset'

Record = namedtuple('Record', 'name value')
BootRow = namedtuple('BootRow', 'property entry reason subreason epoch_text moment position factory_reset')


class StoreError(ValueError):
    """The bytes are not a persistent property store."""


def _varint(data, at):
    """``(value, next position)`` of the varint at ``at``."""
    value = 0
    shift = 0
    while True:
        if at >= len(data) or shift > 63:
            raise StoreError('truncated varint')
        byte = data[at]
        at += 1
        value |= (byte & 0x7F) << shift
        if byte < 0x80:
            return value, at
        shift += 7


def _fields(data):
    """``(field number, wire type, value)`` for each field of a protobuf message; value is bytes or an int."""
    at = 0
    while at < len(data):
        key, at = _varint(data, at)
        number, wire = key >> 3, key & 7
        if wire == 0:
            value, at = _varint(data, at)
        elif wire == 2:
            size, at = _varint(data, at)
            if at + size > len(data):
                raise StoreError('field longer than the data')
            value = data[at:at + size]
            at += size
        elif wire == 1:
            value, at = data[at:at + 8], at + 8
        elif wire == 5:
            value, at = data[at:at + 4], at + 4
        else:
            raise StoreError('unsupported wire type %d' % wire)
        yield number, wire, value


def read_persistent_properties(data):
    """``(records, warning)`` for the bytes of a persistent_properties file.

    ``records`` is a list of :class:`Record` in file order; ``warning`` is '' or a text saying that reading stopped early.
    Raises :class:`StoreError` when the first bytes are not a record of the store at all (an empty file gives no records).
    """
    records = []
    warning = ''
    try:
        for number, wire, value in _fields(data):
            if number != 1 or wire != 2:
                if not records:
                    raise StoreError('the first field is not a record')
                continue
            name = ''
            text = b''
            for inner_number, inner_wire, inner in _fields(value):
                if inner_wire != 2:
                    continue
                if inner_number == 1:
                    name = inner.decode('utf-8', 'replace')
                elif inner_number == 2:
                    text = inner[:MAX_VALUE_BYTES]
            if name:
                records.append(Record(name, text.decode('utf-8', 'replace')))
            if len(records) >= MAX_RECORDS:
                warning = 'more than %d records, the rest were not read' % MAX_RECORDS
                break
    except StoreError as error:
        if not records:
            raise
        warning = 'reading stopped after %d records: %s' % (len(records), error)
    return records, warning


def epoch_moment(text):
    """UTC datetime for a decimal epoch in seconds between 2009 and 2100, else None."""
    text = str(text).strip()
    if not (text.isascii() and text.isdigit()):
        return None
    seconds = int(text)
    if seconds < EPOCH_FLOOR or seconds >= EPOCH_CEILING:
        return None
    return datetime.fromtimestamp(seconds, timezone.utc)


def split_entry(text, with_time):
    """``(reason, subreason, epoch text)`` for one entry.

    Entries of the history are ``reason[,subreason],epoch``; the last item is the epoch when it is all digits. For the
    single-value properties (``with_time`` False) there is no epoch. The reason is the text before the first comma and the
    subreason is the text between the first comma and the epoch, with further commas kept.
    """
    parts = [part.strip() for part in str(text).strip().split(',')]
    epoch = ''
    if with_time and len(parts) > 1 and parts[-1].isascii() and parts[-1].isdigit():
        epoch = parts.pop()
    reason = parts[0] if parts else ''
    return reason, ','.join(parts[1:]), epoch


def has_factory_reset(text):
    """True when the entry text contains the word factory_reset (ignoring case)."""
    return FACTORY_RESET_WORD in str(text).lower()


def history_rows(value, name=HISTORY_PROPERTY):
    """BootRows for the lines of a history property value (newest first as stored), position 0 for the first line."""
    rows = []
    position = 0
    for line in str(value).replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        line = line.strip()
        if not line:
            continue
        reason, subreason, epoch = split_entry(line, True)
        rows.append(BootRow(name, line, reason, subreason, epoch, epoch_moment(epoch), position, has_factory_reset(line)))
        position += 1
    return rows


def single_rows(name, value):
    """BootRows (zero or one) for a single-value boot reason property; an empty value gives no row."""
    value = str(value).strip()
    if not value:
        return []
    reason, subreason, _epoch = split_entry(value, False)
    return [BootRow(name, value, reason, subreason, '', None, 0, has_factory_reset(value))]


def rows_from_records(records):
    """BootRows for the boot reason properties among the records of a persistent store, in the order of the store.

    Only the history property and ``persist.sys.boot.reason`` are kept in that store; ``SINGLE_PROPERTIES`` is applied so a
    record of any of the four names gives its row.
    """
    rows = []
    for record in records:
        if record.name == HISTORY_PROPERTY:
            rows += history_rows(record.value, record.name)
        elif record.name in SINGLE_PROPERTIES:
            rows += single_rows(record.name, record.value)
    return rows

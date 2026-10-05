# pylint: disable=W0613
__artifacts_v2__ = {
    'Life360_NoShowAlerts': {
        'name': 'Life360 No Show Alerts',
        'description': 'Parses Life360 No Show Alerts including records recovered from WAL',
        'author': '@AlexisBrignoni, Codex',
        'creation_date': '2026-07-01',
        'last_update_date': '2026-10-05',
        'requirements': 'none',
        'category': 'Life360',
        'notes': 'Original parser by Heather Charpentier. Live rows come from no_show_alerts. '
                 'WAL rows are observations in salt/checksum-validated frames, resolved using '
                 'the schema of a main-file plus WAL-prefix replay copy. They are not evidence '
                 'of deletion or transaction commitment, and repetitions are retained. Only '
                 'table-root leaf pages with complete inline records are supported; integer primary '
                 'key, child and overflow layouts or unresolved schemas are skipped with diagnostics. Prefix '
                 'replay cannot reconstruct pages predating earlier checkpoints. Run At is '
                 'read as Unix nanoseconds and Last Updated as Unix milliseconds; these units '
                 'remain unverified. Stored values and evidence provenance are retained.',
        'paths': ('*/com.life360.android.safetymapd/databases/NoShowAlertRoomDatabase*',),
        'output_types': 'standard',
        'artifact_icon': 'alert-triangle',
        'sample_data': {
            'hc_pixel8pro_a16': 'Android 16 | com.life360.android.safetymapd vc 2897710 | 9 rows',
        }
    }
}

import datetime
from pathlib import Path
import sqlite3
import struct

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, logfunc
from scripts.artifacts.storagePathViews import unique_files


def _date(value, divisor):
    try:
        return datetime.datetime.fromtimestamp(int(value) / divisor, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return None


def _checksum(data, endian, state=(0, 0)):
    first, second = state
    words = struct.unpack(endian + str(len(data) // 4) + 'I', data)
    for index in range(0, len(words), 2):
        first = (first + words[index] + second) & 0xffffffff
        second = (second + words[index + 1] + first) & 0xffffffff
    return first, second


def _read_varint(data, pos, end):
    value = 0
    for index in range(9):
        if pos >= end:
            raise ValueError('truncated varint')
        byte = data[pos]
        pos += 1
        if index == 8:
            return (value << 8) | byte, pos
        value = (value << 7) | (byte & 0x7f)
        if not byte & 0x80:
            return value, pos
    raise ValueError('invalid varint')


def _decode_value(data, pos, serial, end):
    sizes = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 6, 6: 8, 7: 8, 8: 0, 9: 0}
    if serial in (10, 11):
        raise ValueError('reserved serial type')
    size = sizes[serial] if serial < 10 else (serial - 12) // 2
    if pos + size > end:
        raise ValueError('truncated serial value')
    raw = data[pos:pos + size]
    if serial == 0:
        value = None
    elif serial in (8, 9):
        value = serial - 8
    elif serial == 7:
        value = struct.unpack('>d', raw)[0]
    elif serial < 7:
        value = int.from_bytes(raw, 'big', signed=True)
    elif serial % 2:
        value = raw.decode('utf-8', errors='replace')
    else:
        value = raw
    return value, pos + size


def parse_leaf_records(page, columns, usable_size):
    records = []
    failures = []
    if len(page) < 8 or page[0] != 13:
        return records, ['unsupported interior/child-page layout']
    cells = int.from_bytes(page[3:5], 'big')
    pointer_end = 8 + cells * 2
    if pointer_end > usable_size:
        return records, ['truncated cell-pointer array']
    for index in range(cells):
        try:
            ptr = int.from_bytes(page[8 + 2 * index:10 + 2 * index], 'big')
            if not pointer_end <= ptr < usable_size:
                raise ValueError('cell pointer outside payload area')
            payload, pos = _read_varint(page, ptr, usable_size)
            _, pos = _read_varint(page, pos, usable_size)
            # Table-leaf payloads larger than this use overflow pages.
            if payload > usable_size - 35 or pos + payload > usable_size:
                raise ValueError('unsupported overflow or truncated payload')
            payload_end = pos + payload
            header_start = pos
            header_size, pos = _read_varint(page, pos, payload_end)
            header_end = header_start + header_size
            if not pos <= header_end <= payload_end:
                raise ValueError('invalid record header bounds')
            serials = []
            while pos < header_end:
                serial, pos = _read_varint(page, pos, header_end)
                serials.append(serial)
            if len(serials) != len(columns):
                raise ValueError('record/schema column-count mismatch')
            record = {}
            for column, serial in zip(columns, serials):
                record[column], pos = _decode_value(page, pos, serial, payload_end)
            if pos != payload_end:
                raise ValueError('record payload length mismatch')
            record['_cell_offset'] = ptr
            records.append(record)
        except (ValueError, struct.error) as exc:
            failures.append(f'cell {index}: {exc}')
    return records, failures


def _snapshot_schema(image):
    copy = bytearray(image)
    copy[18:20] = b'\x01\x01'  # Private deserialize image; evidence remains untouched.
    db = sqlite3.connect(':memory:')
    try:
        db.deserialize(bytes(copy))
        table = db.execute("SELECT rootpage, sql FROM sqlite_master "
                           "WHERE type='table' AND name='no_show_alerts'").fetchone()
        if not table or 'WITHOUT ROWID' in table[1].upper():
            return None
        info = db.execute('PRAGMA table_info(no_show_alerts)').fetchall()
        columns = [row[1] for row in info]
        unsupported = any(row[2].upper() == 'INTEGER' and row[5] for row in info)
        required = {'id', 'last_updated', 'run_at', 'trigger_condition', 'type',
                    'place_id', 'observed_user_id', 'creator_id'}
        if not required.issubset(columns):
            return None
        return table[0], columns, unsupported
    except sqlite3.Error:
        return None
    finally:
        db.close()


def recover_wal_observations(main_path, wal_path):
    """Recover root-leaf observations using validated prefix-local schema only."""
    image = bytearray(Path(main_path).read_bytes())
    data = Path(wal_path).read_bytes()
    recovered = []

    def diagnostic(message):
        logfunc(f'Life360 WAL skipped/limited {wal_path}: {message}')

    if len(image) < 100 or image[:16] != b'SQLite format 3\x00' or len(data) < 32:
        diagnostic('truncated or invalid database/WAL header')
        return recovered
    magic, version, page_size = struct.unpack('>3I', data[:12])
    encoded_size = int.from_bytes(image[16:18], 'big')
    main_page_size = 65536 if encoded_size == 1 else encoded_size
    if (magic not in (0x377f0682, 0x377f0683) or version != 3007000 or
            page_size != main_page_size or page_size < 512 or page_size > 65536 or
            page_size & (page_size - 1) or int.from_bytes(image[56:60], 'big') not in (0, 1)):
        diagnostic('unsupported WAL version, page size, or database encoding')
        return recovered
    endian = '<' if magic == 0x377f0682 else '>'
    state = _checksum(data[:24], endian)
    if state != struct.unpack('>2I', data[24:32]):
        diagnostic('WAL header checksum mismatch')
        return recovered
    frame_size = page_size + 24
    frames, remainder = divmod(len(data) - 32, frame_size)
    max_page = len(image) // page_size + frames
    unresolved = 0
    for index in range(frames):
        offset = 32 + index * frame_size
        frame = data[offset:offset + frame_size]
        number = index + 1
        next_state = _checksum(frame[:8] + frame[24:], endian, state)
        if frame[8:16] != data[16:24] or next_state != struct.unpack('>2I', frame[16:24]):
            diagnostic(f'frame {number}: salt/checksum mismatch; stopped validated prefix')
            break
        state = next_state
        page_number = int.from_bytes(frame[:4], 'big')
        if not 1 <= page_number <= max_page:
            diagnostic(f'frame {number}: page number outside bounded replay image')
            break
        end = page_number * page_size
        if len(image) < end:
            image.extend(bytes(end - len(image)))
        image[(page_number - 1) * page_size:end] = frame[24:]
        schema = _snapshot_schema(image)
        if not schema:
            unresolved += 1
            continue
        root, columns, unsupported_pk = schema
        if page_number != root:
            continue
        if unsupported_pk:
            diagnostic(f'frame {number}: unsupported INTEGER PRIMARY KEY record layout')
            continue
        usable = page_size - image[20]
        records, failures = parse_leaf_records(frame[24:], columns, usable)
        for failure in failures:
            diagnostic(f'frame {number}, page {page_number}: {failure}')
        for record in records:
            record['_wal_frame'] = number
            record['_wal_page'] = page_number
            record['_wal_offset'] = offset + 24 + record['_cell_offset']
            recovered.append(record)
    if unresolved:
        diagnostic(f'{unresolved} frame snapshots lacked a resolvable alert schema')
    if remainder:
        diagnostic(f'truncated trailing frame ({remainder} bytes)')
    return recovered


@artifact_processor
def Life360_NoShowAlerts(context):
    files = unique_files(context)
    mains = [str(path) for path in files if Path(path).name == 'NoShowAlertRoomDatabase']
    found = {str(path) for path in files}
    data_list = []
    sources = []
    for source in mains:
        relative = context.get_relative_path(source)
        sources.append(relative)
        wal_path = source + '-wal'
        wal_relative = context.get_relative_path(wal_path) if wal_path in found else ''
        db = open_sqlite_db_readonly(source)
        if db is not None:
            try:
                records = db.execute('SELECT last_updated, run_at, trigger_condition, type, '
                                     'place_id, observed_user_id, creator_id, id '
                                     'FROM no_show_alerts').fetchall()
                for row in records:
                    data_list.append((_date(row[0], 1000), _date(row[1], 1_000_000_000),
                                      row[7], row[0], row[1], *row[2:7], 'Live', '', '', '',
                                      relative, ''))
            except sqlite3.Error as exc:
                logfunc(f'Life360_NoShowAlerts DB error for {relative}: {exc}')
            finally:
                db.close()
        if wal_relative:
            sources.append(wal_relative)
            try:
                records = recover_wal_observations(source, wal_path)
            except OSError as exc:
                logfunc(f'Life360_NoShowAlerts WAL read error for {wal_relative}: {exc}')
                continue
            for record in records:
                updated, run_at = record.get('last_updated'), record.get('run_at')
                data_list.append((_date(updated, 1000), _date(run_at, 1_000_000_000),
                                  record.get('id'), updated, run_at,
                                  *[record.get(key) for key in ('trigger_condition', 'type',
                                    'place_id', 'observed_user_id', 'creator_id')],
                                  'Recovered from WAL', f'WAL Frame {record["_wal_frame"]}',
                                  record['_wal_offset'], record['_wal_page'], relative, wal_relative))
    data_headers = (
        ('Last Updated', 'datetime'), ('Run At', 'datetime'), 'Alert ID',
        'Raw Last Updated', 'Raw Run At', 'Trigger Condition', 'Type',
        'Place ID', 'Observed User ID', 'Creator ID', 'Source', 'WAL Location',
        'WAL Offset', 'WAL Page', 'Source File', 'WAL Source File'
    )
    return data_headers, data_list, '\n'.join(sources)

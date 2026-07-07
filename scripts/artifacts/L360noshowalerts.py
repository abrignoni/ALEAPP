# pylint: disable=W0613
__artifacts_v2__ = {
    'Life360_NoShowAlerts': {
        'name': 'Life360 No Show Alerts',
        'description': 'Parses Life360 No Show Alerts including records recovered from WAL',
        'author': 'Heather Charpentier',
        'creation_date': '2026-07-01',
        'last_update_date': '2026-07-01',
        'requirements': 'none',
        'category': 'Life360',
        'notes': 'WAL file recovery',
        'paths': ('*/com.life360.android.safetymapd/databases/NoShowAlertRoomDatabase*',),
        'output_types': 'standard',
        'artifact_icon': 'alert-triangle'
    }
}

import datetime
import struct

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, logfunc


COL_NAMES = [
    'id', 'type', 'last_updated', 'trigger_condition',
    'critical_alert', 'run_at', 'place_id',
    'observed_user_id', 'creator_id', 'circle_id', 'daily'
]


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _ns_to_utc(value):
    """run_at is stored in nanoseconds."""
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1_000_000_000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _find(context, suffix):
    for file_found in context.get_files_found():
        if str(file_found).endswith(suffix):
            return str(file_found)
    return ''


def _read_varint(data, pos):
    result = 0
    for i in range(9):
        byte = data[pos + i]
        result = (result << 7) | (byte & 0x7f)
        if not (byte & 0x80):
            return result, pos + i + 1
    return result, pos + 9


def _decode_value(cell, pos, stype):
    """Decode a SQLite serial type value from cell data."""
    if stype == 0:
        return None, pos
    elif stype == 1:
        return int.from_bytes(cell[pos:pos+1], 'big', signed=True), pos + 1
    elif stype == 2:
        return int.from_bytes(cell[pos:pos+2], 'big', signed=True), pos + 2
    elif stype == 3:
        return int.from_bytes(cell[pos:pos+3], 'big', signed=True), pos + 3
    elif stype == 4:
        return int.from_bytes(cell[pos:pos+4], 'big', signed=True), pos + 4
    elif stype == 5:
        return int.from_bytes(cell[pos:pos+6], 'big', signed=True), pos + 6
    elif stype == 6:
        return int.from_bytes(cell[pos:pos+8], 'big', signed=True), pos + 8
    elif stype == 7:
        return struct.unpack('>d', cell[pos:pos+8])[0], pos + 8
    elif stype == 8:
        return 0, pos   # integer 0, no bytes
    elif stype == 9:
        return 1, pos   # integer 1, no bytes
    elif stype >= 13 and stype % 2 == 1:
        length = (stype - 13) // 2
        return cell[pos:pos+length].decode('utf-8', errors='replace'), pos + length
    elif stype >= 12 and stype % 2 == 0:
        length = (stype - 12) // 2
        return bytes(cell[pos:pos+length]), pos + length
    return None, pos


def _parse_leaf_page(page_data, page_offset=0):
    """Parse a SQLite B-tree leaf table page and return list of record dicts."""
    records = []
    if not page_data or page_data[0] != 13:
        return records  # not a leaf table page

    num_cells = struct.unpack('>H', page_data[3:5])[0]
    if num_cells == 0:
        return records

    for i in range(num_cells):
        try:
            ptr = struct.unpack('>H', page_data[8 + i * 2: 10 + i * 2])[0]
            cell = page_data[ptr:]

            _, pos = _read_varint(cell, 0)
            _, pos = _read_varint(cell, pos)

            header_start = pos
            header_size, pos = _read_varint(cell, pos)
            header_end = header_start + header_size

            col_types = []
            while pos < header_end:
                stype, pos = _read_varint(cell, pos)
                col_types.append(stype)

            record = {}
            data_pos = pos
            for j, stype in enumerate(col_types):
                col_name = COL_NAMES[j] if j < len(COL_NAMES) else f'col{j}'
                val, data_pos = _decode_value(cell, data_pos, stype)
                record[col_name] = val

            if record.get('id'):
                record['_cell_offset'] = page_offset + ptr
                records.append(record)
        except Exception:  # pylint: disable=broad-exception-caught
            continue

    return records


def _recover_from_wal(wal_path, data_page_num=4):
    """
    Parse all WAL frames and collect every record from every version of
    the data page, including frames before deletion. Each frame version
    represents a separate update with a different last_updated timestamp,
    so all are returned as individual rows rather than deduplicated.
    """
    recovered = []
    try:
        with open(wal_path, 'rb') as f:
            wal_data = f.read()

        if len(wal_data) < 32:
            return recovered

        magic = struct.unpack('>I', wal_data[:4])[0]
        if magic not in (0x377f0682, 0x377f0683):
            return recovered

        page_size = struct.unpack('>I', wal_data[8:12])[0]
        frame_size = 24 + page_size
        num_frames = (len(wal_data) - 32) // frame_size

        for i in range(num_frames):
            frame_offset = 32 + i * frame_size
            page_num = struct.unpack('>I', wal_data[frame_offset:frame_offset + 4])[0]
            if page_num != data_page_num:
                continue

            page_data = wal_data[frame_offset + 24: frame_offset + 24 + page_size]
            page_offset = frame_offset + 24
            for record in _parse_leaf_page(page_data, page_offset):
                if record.get('id'):
                    record['_wal_frame'] = i + 1
                    record['_wal_offset'] = record.get('_cell_offset', '')
                    recovered.append(record)

    except Exception as e:  # pylint: disable=broad-exception-caught
        logfunc(f'Life360_NoShowAlerts WAL parse error: {e}')

    return recovered


def _find_wal(context):
    """Find the WAL file — it may have a timestamp prefix."""
    for file_found in context.get_files_found():
        path = str(file_found)
        if path.endswith('NoShowAlertRoomDatabase-wal'):
            return path
    return ''


@artifact_processor
def Life360_NoShowAlerts(context):
    source = _find(context, 'NoShowAlertRoomDatabase')
    wal_path = _find_wal(context)
    data_list = []

    # --- Live records from the main database ---
    live_ids = set()
    if source:
        try:
            db = open_sqlite_db_readonly(source)
            cursor = db.cursor()
            cursor.execute('''
                SELECT
                    last_updated,
                    run_at,
                    trigger_condition,
                    type,
                    place_id,
                    observed_user_id,
                    creator_id,
                    id
                FROM no_show_alerts
            ''')
            for row in cursor.fetchall():
                live_ids.add(row[7])
                data_list.append((
                    _ms_to_utc(row[0]),
                    _ns_to_utc(row[1]),
                    row[2], row[3], row[4], row[5], row[6],
                    'Live', '', ''
                ))
            db.close()
        except Exception as e:  # pylint: disable=broad-exception-caught
            logfunc(f'Life360_NoShowAlerts DB error: {e}')

    # --- Deleted records recovered from WAL ---
    if wal_path:
        recovered = _recover_from_wal(wal_path)
        wal_count = 0
        for rec in recovered:
            data_list.append((
                _ms_to_utc(rec.get('last_updated')),
                _ns_to_utc(rec.get('run_at')),
                rec.get('trigger_condition', ''),
                rec.get('type', ''),
                rec.get('place_id', ''),
                rec.get('observed_user_id', ''),
                rec.get('creator_id', ''),
                'Recovered from WAL',
                f'WAL Frame {rec.get("_wal_frame", "")}',
                rec.get('_wal_offset', '')
            ))
            wal_count += 1
        logfunc(f'Life360_NoShowAlerts: {wal_count} record(s) recovered from WAL')

    logfunc(f'Life360_NoShowAlerts: Total records = {len(data_list)}')

    data_headers = (
        ('Last Updated', 'datetime'), ('Run At', 'datetime'),
        'Trigger Condition', 'Type',
        'Place ID', 'Observed User ID', 'Creator ID',
        'Source', 'WAL Location', 'WAL Offset'
    )
    return data_headers, data_list, source
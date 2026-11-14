"""Builds the synthetic App Ops history databases used by the appOpsHistoryDb test cases.

Every value is invented: package names are under example.*, uids are made up, times are
fixed. The table definitions are the ones AOSP's AppOpHistoryTable writes for Android 16
(aggregated: app_op_history_short_interval.db and app_op_history_long_interval.db) and
DiscreteOpsTable writes for the Android 16.0 release (app_op_history.db, one row per
access). The long database is left with a real write-ahead log: rows are inserted and
checkpointed into the database file first, then a later transaction deletes two of them,
changes one and adds two, and the files are copied while the connection is still open so
that the -wal is not checkpointed away.

Usage: python appops_history_fixture.py <output folder>
Writes one zip per test case into the folder and prints their names.
"""
import datetime
import os
import shutil
import sqlite3
import sys
import tempfile
import zipfile

APPOPS_DIR = 'Dump/data/system/appops/'
ZIP_TIME = (2026, 10, 25, 0, 0, 0)

AGGREGATED_SCHEMA = (
    'CREATE TABLE app_op_accesses(id INTEGER PRIMARY KEY,uid INTEGER,package_name TEXT,device_id TEXT,'
    'op_code INTEGER,attribution_tag TEXT,uid_state INTEGER,op_flags INTEGER,attribution_flags INTEGER,'
    'chain_id INTEGER,access_time INTEGER,access_duration INTEGER,total_duration INTEGER,'
    'access_count INTEGER,reject_count INTEGER)')
AGGREGATED_COLUMNS = ('id', 'uid', 'package_name', 'device_id', 'op_code', 'attribution_tag', 'uid_state',
                      'op_flags', 'attribution_flags', 'chain_id', 'access_time', 'access_duration',
                      'total_duration', 'access_count', 'reject_count')
DISCRETE_SCHEMA = (
    'CREATE TABLE app_op_accesses(id INTEGER PRIMARY KEY,uid INTEGER,package_name TEXT,device_id TEXT NOT NULL,'
    'op_code INTEGER,attribution_tag TEXT,access_time INTEGER,access_duration INTEGER,uid_state INTEGER,'
    'op_flags INTEGER,attribution_flags INTEGER,chain_id INTEGER)')
DISCRETE_COLUMNS = ('id', 'uid', 'package_name', 'device_id', 'op_code', 'attribution_tag', 'access_time',
                    'access_duration', 'uid_state', 'op_flags', 'attribution_flags', 'chain_id')
INDEX_SQL = 'CREATE INDEX app_op_access_index ON app_op_accesses (access_time)'


def ms(year, month, day, hour, minute, second=0, milli=0):
    moment = datetime.datetime(year, month, day, hour, minute, second, milli * 1000, datetime.timezone.utc)
    return int(moment.timestamp() * 1000)


def new_database(path, schema, index=False):
    connection = sqlite3.connect(path)
    connection.execute('PRAGMA journal_mode=WAL')
    connection.execute('PRAGMA wal_autocheckpoint=0')
    connection.execute('CREATE TABLE android_metadata (locale TEXT)')
    connection.execute("INSERT INTO android_metadata VALUES ('en_US')")
    connection.execute(schema)
    if index:
        connection.execute(INDEX_SQL)
    connection.execute('PRAGMA user_version=1')
    connection.commit()
    return connection


def insert(connection, columns, rows):
    marks = ','.join('?' * len(columns))
    connection.executemany(f'INSERT INTO app_op_accesses({",".join(columns)}) VALUES ({marks})', rows)
    connection.commit()


def short_rows():
    # id, uid, package, device, op, tag, uid_state, op_flags, attr_flags, chain, time, duration, total, count, reject
    return [
        (1, 10101, 'com.example.recorder', None, 27, None, 200, 1, 0, -1, ms(2026, 8, 24, 9, 0, 5, 120), -1, 0, 1, 0),
        (2, 10101, 'com.example.recorder', None, 27, None, 200, 1, 0, 7, ms(2026, 8, 24, 9, 0, 5, 120), 8000, 8000, 0, 0),
        (3, 15010101, 'com.example.recorder', None, 27, None, 700, 1, 0, -1, ms(2026, 8, 24, 9, 30, 0, 5), 0, 0, 3, 0),
        (4, 10102, 'com.example.camera', None, 26, 'viewfinder', 200, 1, 0, -1, ms(2026, 8, 24, 10, 15, 0, 900), -1, 0, 1, 0),
        (5, 10103, 'com.example.maps', None, 1, 'nav', 400, 1, 0, -1, ms(2026, 8, 24, 11, 0, 1, 1), 0, 0, 12, 0),
        (6, 10103, 'com.example.maps', None, 0, 'nav', 600, 1, 0, -1, ms(2026, 8, 24, 11, 1, 0, 0), -1, 0, 4, 2),
        (7, 10104, 'com.example.proxy', 'virtual:example-1', 26, 'tag-b', 500, 8, 9, 31, ms(2026, 8, 24, 12, 0, 0, 77), 0, 0, 1, 0),
        (8, 10105, 'com.example.helper', None, 26, None, 500, 2, 12, 31, ms(2026, 8, 24, 12, 0, 0, 78), 0, 0, 1, 0),
        (9, 1000, 'com.example.system', None, 73, None, 2147483647, 1, 0, -1, ms(2026, 8, 25, 0, 0, 3, 3), -1, 0, 2, 0),
        (10, 10106, None, None, 999, None, 500, 1, 0, -1, ms(2026, 8, 25, 1, 0, 0, 0), -1, 0, 1, 0),
    ]


def long_rows_initial():
    base = ms(2026, 8, 20, 0, 0)
    return [
        (1, 1000, 'com.example.system', None, 40, None, 100, 1, 0, -1, base + 1000, 0, 0, 2, 0),
        (2, 1000, 'com.example.system', None, 40, None, 100, 1, 0, -1, base + 901000, 5, 5, 0, 0),
        (3, 10101, 'com.example.recorder', None, 43, None, 700, 1, 0, -1, base + 1800000, -1, 0, 6, 1),
        (4, 10103, 'com.example.maps', None, 41, 'nav', 400, 1, 0, -1, base + 2700000, 0, 0, 3, 0),
        (5, 15010101, 'com.example.recorder', None, 4, None, 600, 1, 0, -1, base + 3600000, -1, 0, 1, 4),
        (6, 10102, 'com.example.camera', None, 163, None, 500, 2, 0, -1, base + 4500000, -1, 0, 2, 17),
        (7, 10107, 'com.example.mail', None, 166, None, 100, 1, 0, -1, base + 5400000, -1, 0, 1, 0),
        (8, 10107, 'com.example.mail', None, 24, None, 200, 4, 0, -1, base + 6300000, 0, 0, 1, 0),
    ]


def long_rows_later():
    base = ms(2026, 8, 28, 0, 0)
    return [
        (9, 10101, 'com.example.recorder', None, 43, None, 700, 1, 0, -1, base + 1000, -1, 0, 9, 0),
        (10, 15010101, 'com.example.recorder', None, 8, None, 600, 16, 0, -1, base + 901000, -1, 0, 1, 0),
    ]


def copy_with_log(path, target_dir, name):
    """Copy the database file and the -wal and -shm that sit beside it while it is still open."""
    for suffix in ('', '-wal', '-shm'):
        if os.path.exists(path + suffix):
            shutil.copy(path + suffix, os.path.join(target_dir, name + suffix))


def write_zip(zip_path, members):
    """members: list of (archive name, file path)."""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for archive_name, file_path in members:
            info = zipfile.ZipInfo(archive_name, ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            with open(file_path, 'rb') as handle:
                archive.writestr(info, handle.read())


def build_history(work):
    """Short database without a log (clean close), long database with a live log."""
    out = os.path.join(work, 'history')
    os.makedirs(out)
    short_path = os.path.join(work, 'short.db')
    connection = new_database(short_path, AGGREGATED_SCHEMA, index=True)
    insert(connection, AGGREGATED_COLUMNS, short_rows())
    connection.close()
    # A clean close leaves the database file in WAL mode with no -wal beside it.
    shutil.copy(short_path, os.path.join(out, 'app_op_history_short_interval.db'))

    long_path = os.path.join(work, 'long.db')
    connection = new_database(long_path, AGGREGATED_SCHEMA)
    insert(connection, AGGREGATED_COLUMNS, long_rows_initial())
    connection.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    connection.execute('DELETE FROM app_op_accesses WHERE id IN (1, 2)')
    connection.execute('UPDATE app_op_accesses SET access_count = 7, reject_count = 0 WHERE id = 3')
    connection.commit()
    insert(connection, AGGREGATED_COLUMNS, long_rows_later())
    copy_with_log(long_path, out, 'app_op_history_long_interval.db')
    connection.close()
    return out


def build_odd(work):
    """Values the platform does not write: unreadable times, text where numbers belong, unknown codes."""
    out = os.path.join(work, 'odd')
    os.makedirs(out)
    path = os.path.join(work, 'odd.db')
    connection = new_database(path, AGGREGATED_SCHEMA)
    good = ms(2026, 8, 24, 8, 0)
    rows = [
        (1, 10201, 'com.example.odd', None, 27, None, 500, 1, 0, -1, good, 0, 0, 1, 0),
        (2, 10201, 'com.example.odd', None, 27, None, 500, 1, 0, -1, 9223372036854775807, 0, 0, 1, 0),
        (3, 10201, 'com.example.odd', None, 27, None, 500, 1, 0, -1, 'not a time', 0, 0, 1, 0),
        (4, 10201, 'com.example.odd', None, 27, None, 500, 1, 0, -1, None, 0, 0, 1, 0),
        (5, 10201, 'com.example.odd', None, 27, None, 500, 1, 0, -1, -86400000, 0, 0, 1, 0),
        (6, 10201, 'com.example.odd', None, 27, None, 500, 1, 0, -1, good // 1000, 0, 0, 1, 0),
        (7, 'x', 'com.example.odd', None, 'y', None, 'z', 'w', 'v', 'u', good + 1, 't', 's', 'r', 'q'),
        (8, None, None, None, None, None, None, None, None, None, good + 2, None, None, None, None),
        (9, 10201, 'com.example.odd', None, 170, None, 12345, 32, 16, -1, good + 3, 0, 0, 2 ** 40, 2 ** 40),
        (10, 10201, 'com.example.odd', None, 96, None, 500, 0, 0, -1, good + 4, 0, 0, 1, 0),
    ]
    insert(connection, AGGREGATED_COLUMNS, rows)
    connection.close()
    shutil.copy(path, os.path.join(out, 'app_op_history_long_interval.db'))
    return out


def build_empty(work):
    out = os.path.join(work, 'empty')
    os.makedirs(out)
    for name, index in (('app_op_history_short_interval.db', True), ('app_op_history_long_interval.db', False)):
        path = os.path.join(work, name)
        connection = new_database(path, AGGREGATED_SCHEMA, index=index)
        connection.close()
        shutil.copy(path, os.path.join(out, name))
    return out


def build_no_table(work):
    out = os.path.join(work, 'notable')
    os.makedirs(out)
    path = os.path.join(work, 'notable.db')
    connection = sqlite3.connect(path)
    connection.execute('CREATE TABLE android_metadata (locale TEXT)')
    connection.execute("INSERT INTO android_metadata VALUES ('en_US')")
    connection.execute('CREATE TABLE something_else (id INTEGER PRIMARY KEY, note TEXT)')
    connection.commit()
    connection.close()
    shutil.copy(path, os.path.join(out, 'app_op_history_short_interval.db'))
    return out


def build_discrete(work):
    """The Android 16.0 release database: one row per access, no aggregate columns, device id not null."""
    out = os.path.join(work, 'discrete')
    os.makedirs(out)
    path = os.path.join(work, 'discrete.db')
    connection = new_database(path, DISCRETE_SCHEMA, index=True)
    day = ms(2026, 8, 24, 13, 0)
    rows = [
        (1, 10301, 'com.example.camera', 'default:0', 26, None, day, 4200, 200, 1, 0, -1),
        (2, 10301, 'com.example.camera', 'default:0', 26, 'viewfinder', day + 60000, -1, 200, 1, 0, -1),
        (3, 15010301, 'com.example.recorder', 'default:0', 27, None, day + 120000, 0, 700, 1, 0, -1),
        (4, 10302, 'com.example.maps', 'virtual:example-2', 1, 'nav', day + 180000, -1, 400, 8, 9, 3),
    ]
    insert(connection, DISCRETE_COLUMNS, rows)
    connection.close()
    shutil.copy(path, os.path.join(out, 'app_op_history.db'))
    return out


def build_unreadable(work, history):
    """A short database whose content is zeroed (as an extraction taken before first unlock can hold),
    beside a readable long database with its -wal."""
    out = os.path.join(work, 'unreadable')
    os.makedirs(out)
    with open(os.path.join(out, 'app_op_history_short_interval.db'), 'wb') as handle:
        handle.write(bytes(8192))
    for suffix in ('', '-wal', '-shm'):
        shutil.copy(os.path.join(history, 'app_op_history_long_interval.db' + suffix), out)
    return out


def members_for(folder, prefix=APPOPS_DIR):
    return [(prefix + name, os.path.join(folder, name)) for name in sorted(os.listdir(folder))]


def main(output):
    os.makedirs(output, exist_ok=True)
    with tempfile.TemporaryDirectory() as work:
        history = build_history(work)
        write_zip(os.path.join(output, 'synthetic_appops_history.zip'), members_for(history))
        write_zip(os.path.join(output, 'synthetic_appops_two_copies.zip'),
                  members_for(history) + members_for(history, 'Dump2/data/system/appops/'))
        write_zip(os.path.join(output, 'synthetic_appops_unreadable.zip'), members_for(build_unreadable(work, history)))
        write_zip(os.path.join(output, 'synthetic_appops_odd_values.zip'), members_for(build_odd(work)))
        write_zip(os.path.join(output, 'synthetic_appops_empty.zip'), members_for(build_empty(work)))
        write_zip(os.path.join(output, 'synthetic_appops_no_table.zip'), members_for(build_no_table(work)))
        write_zip(os.path.join(output, 'synthetic_appops_discrete_a16.zip'), members_for(build_discrete(work)))
    for name in sorted(os.listdir(output)):
        print(name, os.path.getsize(os.path.join(output, name)))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'appops_fixture_out')

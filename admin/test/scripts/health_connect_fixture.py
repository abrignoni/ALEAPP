"""Builds a synthetic Health Connect database (healthconnect.db) for tests.

Nothing here comes from a real device. The table and column names are those of the AOSP
HealthFitness module's storage helpers (commit 45168a88ae2a7e1abafe1cc81001d97ff00194e2) and
the same names appear in the healthconnect.db of Android 16 images; every value below is made up.
"""
import pathlib
import sqlite3

RECORD_BASE = ('row_id INTEGER PRIMARY KEY AUTOINCREMENT, uuid BLOB NOT NULL UNIQUE, '
               'last_modified_time INTEGER, client_record_id TEXT, client_record_version TEXT, '
               'device_info_id INTEGER, app_info_id INTEGER, recording_method INTEGER, '
               'dedupe_hash BLOB UNIQUE')
INTERVAL = (', start_time INTEGER, start_zone_offset INTEGER, end_time INTEGER, '
            'end_zone_offset INTEGER, local_date INTEGER')
INSTANT = ', time INTEGER, zone_offset INTEGER, local_date INTEGER'

INTERVAL_TABLES = {
    'steps_record_table': 'count INTEGER',
    'distance_record_table': 'distance REAL',
    'active_calories_burned_record_table': 'energy REAL',
    'total_calories_burned_record_table': 'energy REAL',
    'floors_climbed_record_table': 'floors REAL',
    'elevation_gained_record_table': 'elevation REAL',
    'hydration_record_table': 'volume REAL',
    'wheelchair_pushes_record_table': 'count INTEGER',
    'heart_rate_record_table': None,
    'sleep_session_record_table': 'notes TEXT, title TEXT',
    'exercise_session_record_table': ('notes TEXT, exercise_type INTEGER, title TEXT, '
                                      'has_route INTEGER, session_rate_of_perceived_exertion REAL'),
}
INSTANT_TABLES = {
    'weight_record_table': 'weight REAL',
    'height_record_table': 'height REAL',
    'body_fat_record_table': 'percentage REAL',
    'lean_body_mass_record_table': 'mass REAL',
    'bone_mass_record_table': 'mass REAL',
    'body_water_mass_record_table': 'body_water_mass REAL',
    'resting_heart_rate_record_table': 'beats_per_minute INTEGER',
    'oxygen_saturation_record_table': 'percentage REAL',
    'respiratory_rate_record_table': 'rate REAL',
    'heart_rate_variability_rmssd_record_table': 'heart_rate_variability_millis REAL',
    'vo2_max_record_table': 'measurement_method INTEGER, vo2_milliliters_per_minute_kilogram REAL',
    'blood_pressure_record_table': ('measurement_location TEXT NOT NULL, systolic REAL, '
                                    'diastolic REAL, body_position TEXT NOT NULL'),
    'blood_glucose_record_table': ('specimen_source TEXT NOT NULL, level REAL, '
                                   'relation_to_meal TEXT NOT NULL, meal_type TEXT NOT NULL'),
    'body_temperature_record_table': 'measurement_location TEXT NOT NULL, temperature REAL',
    'basal_body_temperature_record_table': 'measurement_location TEXT NOT NULL, temperature REAL',
    'basal_metabolic_rate_record_table': 'basal_metabolic_rate REAL',
}
OTHER = {
    'application_info_table': (
        'CREATE TABLE application_info_table (row_id INTEGER PRIMARY KEY, '
        'package_name TEXT NOT NULL UNIQUE, app_name TEXT, app_icon BLOB, record_types_used TEXT)'),
    'device_info_table': (
        'CREATE TABLE device_info_table (row_id INTEGER PRIMARY KEY, manufacturer TEXT, '
        'model TEXT, device_type INTEGER)'),
    'preference_table': 'CREATE TABLE preference_table (key TEXT NOT NULL UNIQUE, value TEXT)',
    'heart_rate_record_series_table': (
        'CREATE TABLE heart_rate_record_series_table (parent_key INTEGER, '
        'beats_per_minute INTEGER, epoch_millis INTEGER)'),
    'sleep_stages_table': (
        'CREATE TABLE sleep_stages_table (parent_key INTEGER NOT NULL, '
        'stage_start_time INTEGER NOT NULL, stage_end_time INTEGER NOT NULL, '
        'stage_type INTEGER NOT NULL)'),
    'exercise_route_table': (
        'CREATE TABLE exercise_route_table (parent_key INTEGER NOT NULL, '
        'timestamp_millis INTEGER NOT NULL, longitude REAL NOT NULL, latitude REAL NOT NULL, '
        'horizontal_accuracy REAL NOT NULL, vertical_accuracy REAL NOT NULL, '
        'altitude REAL NOT NULL)'),
    'exercise_laps_table': (
        'CREATE TABLE exercise_laps_table (parent_key INTEGER NOT NULL, '
        'lap_start_time INTEGER NOT NULL, lap_end_time INTEGER NOT NULL, '
        'lap_length REAL NOT NULL)'),
    'exercise_segments_table': (
        'CREATE TABLE exercise_segments_table (parent_key INTEGER NOT NULL, '
        'segment_start_time INTEGER NOT NULL, segment_end_time INTEGER NOT NULL, '
        'segment_type INTEGER NOT NULL, repetitions_count INTEGER NOT NULL, weight_grams REAL, '
        'set_index INTEGER, rate_of_perceived_exertion REAL)'),
    'access_logs_table': (
        'CREATE TABLE access_logs_table (row_id INTEGER PRIMARY KEY AUTOINCREMENT, '
        'app_id INTEGER NOT NULL, record_type TEXT NOT NULL, access_time INTEGER NOT NULL, '
        'operation_type INTEGER NOT NULL, medical_resource_type TEXT, '
        'medical_data_source_accessed INTEGER)'),
    'read_access_logs_table': (
        'CREATE TABLE read_access_logs_table (row_id INTEGER PRIMARY KEY AUTOINCREMENT, '
        'reader_app_id INTEGER NOT NULL, writer_app_id INTEGER NOT NULL, '
        'record_type TEXT NOT NULL, read_time INTEGER NOT NULL, write_time INTEGER NOT NULL)'),
    'change_logs_table': (
        'CREATE TABLE change_logs_table (row_id INTEGER PRIMARY KEY AUTOINCREMENT, '
        'record_type INTEGER, app_id INTEGER, uuids BLOB NOT NULL, operation_type INTEGER, '
        'time INTEGER, medical_resource_type INTEGER, medical_data_source_id INTEGER)'),
}

# 2026-01-01 00:00:00 UTC in milliseconds, and made-up identifiers.
T0 = 1767225600000
HOUR = 3600000
UUID_A = bytes(range(16))
UUID_B = bytes(range(16, 32))
ICON = bytes.fromhex(
    '89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d4944415478'
    '9c63f8ffff3f0005fe02fea79aa0a00000000049454e44ae426082')


def make_database(path, rich=True, drop=()):
    """Create the database at path. rich=False leaves every record table empty.

    drop names tables to leave out, to stand for an older schema version."""
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute('PRAGMA page_size = 512')  # small pages keep the committed test case small
    for table, extra in INTERVAL_TABLES.items():
        if table not in drop:
            con.execute(f'CREATE TABLE {table} ({RECORD_BASE}{INTERVAL}'
                        + (f', {extra}' if extra else '') + ')')
    for table, extra in INSTANT_TABLES.items():
        if table not in drop:
            con.execute(f'CREATE TABLE {table} ({RECORD_BASE}{INSTANT}, {extra})')
    for table, statement in OTHER.items():
        if table not in drop:
            con.execute(statement)
    if rich:
        _fill(con)
    con.commit()
    con.close()
    return path


def _record(seed, app=2, device=1, method=3):
    return (bytes([seed]) * 16, T0 + 5000, f'client-{seed}', '1', device, app, method,
            bytes([seed]) * 8)


def _insert(con, table, record, times, extra):
    base = ('uuid, last_modified_time, client_record_id, client_record_version, '
            'device_info_id, app_info_id, recording_method, dedupe_hash')
    columns = [base] + list(times) + list(extra)
    values = record + tuple(times.values()) + tuple(extra.values())
    con.execute(f'INSERT INTO {table} ({", ".join(columns)}) '
                f'VALUES ({",".join("?" * len(values))})', values)
    return con.execute('SELECT last_insert_rowid()').fetchone()[0]


def _interval(start, end, offset=3600):
    return {'start_time': start, 'start_zone_offset': offset, 'end_time': end,
            'end_zone_offset': offset, 'local_date': 20454}


def _instant(when, offset=-18000):
    return {'time': when, 'zone_offset': offset, 'local_date': 20454}


def _fill(con):
    con.execute("INSERT INTO application_info_table VALUES "
                "(1, 'com.example.syntheticfit', 'Synthetic Fit', ?, '1,7,11,99')", (ICON,))
    con.execute("INSERT INTO application_info_table VALUES "
                "(2, 'com.example.synthetictracker', 'Synthetic Tracker', NULL, NULL)")
    con.execute("INSERT INTO device_info_table VALUES (1, 'MakerX', 'Model-1', 1)")
    con.execute("INSERT INTO device_info_table VALUES (2, 'MakerY', 'Model-2', 77)")
    for key, value in (('migration_state', '5'),
                       ('current_state_start_time', '2026-01-01T00:00:00.000000Z')):
        con.execute('INSERT INTO preference_table VALUES (?, ?)', (key, value))
    one = _interval(T0, T0 + HOUR)
    _insert(con, 'steps_record_table', _record(1), one, {'count': 1200})
    _insert(con, 'steps_record_table', _record(2, app=1, device=2, method=1),
            _interval(T0 + HOUR, T0 + 2 * HOUR, -3600), {'count': 345})
    _insert(con, 'distance_record_table', _record(3), one, {'distance': 812.5})
    _insert(con, 'active_calories_burned_record_table', _record(4), one, {'energy': 55000.0})
    _insert(con, 'total_calories_burned_record_table', _record(5), one, {'energy': 90000.0})
    _insert(con, 'floors_climbed_record_table', _record(6), one, {'floors': 4.0})
    _insert(con, 'elevation_gained_record_table', _record(7), one, {'elevation': 12.5})
    _insert(con, 'hydration_record_table', _record(8), one, {'volume': 0.25})
    _insert(con, 'wheelchair_pushes_record_table', _record(9), one, {'count': 10})
    _insert(con, 'weight_record_table', _record(10), _instant(T0), {'weight': 70500.0})
    _insert(con, 'height_record_table', _record(11), _instant(T0), {'height': 1.75})
    _insert(con, 'oxygen_saturation_record_table', _record(12), _instant(T0 + 1000),
            {'percentage': 97.0})
    _insert(con, 'resting_heart_rate_record_table', _record(13), _instant(T0 + 2000),
            {'beats_per_minute': 58})
    _insert(con, 'blood_pressure_record_table', _record(14), _instant(T0 + 3000),
            {'measurement_location': '1', 'systolic': 120.0, 'diastolic': 80.0,
             'body_position': '2'})
    heart = _insert(con, 'heart_rate_record_table', _record(15), _interval(T0, T0 + 60000), {})
    for offset, bpm in ((0, 70), (30000, 74), (60000, 71)):
        con.execute('INSERT INTO heart_rate_record_series_table VALUES (?, ?, ?)',
                    (heart, bpm, T0 + offset))
    sleep = _insert(con, 'sleep_session_record_table', _record(16),
                    _interval(T0, T0 + 8 * HOUR), {'notes': 'n', 'title': 'Night'})
    for index, (stage, length) in enumerate(((1, 1), (4, 3), (5, 2), (6, 2), (42, 0))):
        con.execute('INSERT INTO sleep_stages_table VALUES (?, ?, ?, ?)',
                    (sleep, T0 + index * HOUR, T0 + (index + length) * HOUR, stage))
    exercise = _insert(con, 'exercise_session_record_table', _record(17), one, {
        'notes': None, 'exercise_type': 33, 'title': 'Morning run', 'has_route': 1,
        'session_rate_of_perceived_exertion': 6.0})
    _insert(con, 'exercise_session_record_table', _record(18), one, {
        'notes': 'x', 'exercise_type': 9999, 'title': None, 'has_route': 0,
        'session_rate_of_perceived_exertion': None})
    for index in range(3):
        con.execute('INSERT INTO exercise_route_table VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (exercise, T0 + index * 1000, 10.0 + index / 100, 50.0 + index / 100,
                     5.0, 3.0, 100.0 + index))
    con.execute('INSERT INTO exercise_laps_table VALUES (?, ?, ?, ?)',
                (exercise, T0, T0 + 1000, 400.0))
    con.execute('INSERT INTO exercise_segments_table VALUES (?, ?, ?, ?, ?, NULL, NULL, NULL)',
                (exercise, T0, T0 + 1000, 1, 10))
    con.execute('INSERT INTO access_logs_table (app_id, record_type, access_time, '
                'operation_type) VALUES (1, ?, ?, 2)', ('1,11', T0 + 9000))
    con.execute('INSERT INTO access_logs_table (app_id, record_type, access_time, '
                'operation_type) VALUES (2, ?, ?, 0)', ('7', T0 + 8000))
    con.execute('INSERT INTO read_access_logs_table (reader_app_id, writer_app_id, record_type, '
                'read_time, write_time) VALUES (1, 2, 11, ?, ?)', (T0 + 9500, T0 + 100))
    con.execute('INSERT INTO change_logs_table (record_type, app_id, uuids, operation_type, '
                'time) VALUES (1, 2, ?, 0, ?)', (UUID_A + UUID_B, T0 + 7000))

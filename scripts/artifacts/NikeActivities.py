__artifacts_v2__ = {
    "get_nike_activities": {
        "name": "Nike - Activities",
        "description": "Activity records from the Nike Run Club app database (com.nike.nrc.room)",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}, @AlexisBrignoni, Codex",
        "creation_date": "2023-03-18",
        "last_update_date": "2026-10-05",
        "requirements": "none",
        "category": "Nike-Run",
        "notes": "Activity, tag and summary projections use explicit column names verified in the "
                 "registered Samsung schema; its tables were empty, so positive real activity-value "
                 "validation remains unavailable. Activity App ID holds as2_sa_app_id, formerly "
                 "reported as Source. Source File identifies the evidence database. Canonical storage "
                 "aliases select a preferred path; other users and evidence roots remain separate. "
                 "The main filename is com.nike.nrc.room.database; SQLite sidecars are not parsed as "
                 "main inputs. Optional absent fields are reported blank with source-specific diagnostics; "
                 "a missing required activity identity/time/duration column skips that source with a "
                 "diagnostic. Start and end preserve the existing Unix-millisecond conversion. Duration "
                 "(min) preserves as2_sa_active_duration_ms divided by 60000. Speed, distance and pace "
                 "units are not established; existing numeric rounding to two decimals is retained. "
                 "Tag and metric selectors and last matching value precedence are unchanged. Records "
                 "are not filtered by stored lifecycle/status fields and no lifecycle meaning is inferred.",
        "paths": ('*/com.nike.plusgps/databases/com.nike.nrc.room*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "samsunga53_a14": "Android 14 | com.nike.plusgps vc 1717605525 | 0 rows",
            "userb2_a13": "Android 13 | com.nike.plusgps vc 1717303105 | 0 rows",
        },
    }
}

import datetime
import sqlite3
from pathlib import Path

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _round(value):
    try:
        return round(float(value), 2)
    except (ValueError, TypeError):
        return value


ACTIVITY_FIELDS = ('as2_sa_id', 'as2_sa_start_utc_ms', 'as2_sa_end_utc_ms',
                   'as2_sa_active_duration_ms', 'as2_sa_app_id')
TAG_FIELDS = ('as2_t_type', 'as2_t_value')
SUMMARY_FIELDS = ('as2_s_metric_type', 'as2_s_type', 'as2_s_value')


def _q(cursor, sql, params, source):
    try:
        cursor.execute(sql, params)
        return cursor.fetchall()
    except sqlite3.Error as error:
        logfunc(f'Nike query error for {source}: {error}')
        return []


def _projection(fields, columns):
    return ', '.join(field if field in columns else f'NULL AS {field}' for field in fields)


@artifact_processor
def get_nike_activities(context):
    data_list = []
    sources = []
    for source_path in unique_files(context):
        source_path = str(source_path)
        if Path(source_path).name != 'com.nike.nrc.room.database':
            continue
        relative = context.get_relative_path(source_path)
        db = open_sqlite_db_readonly(source_path)
        if db is None:
            logfunc(f'Nike database unavailable for {relative}; source skipped')
            continue
        try:
            cursor = db.cursor()
            columns = {table: {r[1] for r in cursor.execute(f'PRAGMA table_info({table})')}
                       for table in ('activity', 'activity_tag', 'activity_summary')}
            required = set(ACTIVITY_FIELDS[:-1]) - columns['activity']
            if required:
                logfunc(f'Nike activity schema skipped for {relative}: missing required columns '
                        + ', '.join(sorted(required)))
                continue
            for table, fields in [('activity', ACTIVITY_FIELDS), ('activity_tag', TAG_FIELDS),
                                  ('activity_summary', SUMMARY_FIELDS)]:
                missing = set(fields) - columns[table]
                if table != 'activity':
                    missing |= {('as2_t_activity_id' if table == 'activity_tag'
                                 else 'as2_s_activity_id')} - columns[table]
                if missing:
                    logfunc(f'Nike optional fields absent in {table} for {relative}: '
                            + ', '.join(sorted(missing)))
            sources.append(source_path)
            activities = _q(cursor, 'SELECT '+_projection(ACTIVITY_FIELDS, columns['activity'])
                            +' FROM activity', (), relative)
            for act_id, raw_start, raw_end, active_duration, app_id in activities:
                start_time, end_time = _ms_to_utc(raw_start), _ms_to_utc(raw_end)
                duration = _round(active_duration / 60000) if active_duration else ''
                name = location = version = temperature = weather = None
                calories = max_speed = mean_speed = steps = distance = pace = cadence = None
                tags = []
                if 'as2_t_activity_id' in columns['activity_tag']:
                    tags = _q(cursor, 'SELECT '+_projection(TAG_FIELDS, columns['activity_tag'])
                              +' FROM activity_tag WHERE as2_t_activity_id = ?', (act_id,), relative)
                for key, value in tags:
                    if key == 'com.nike.name':
                        name = value
                    elif key == 'location':
                        location = value
                    elif key == 'com.nike.running.recordingappversion':
                        version = value
                    elif key == 'com.nike.temperature':
                        temperature = value
                    elif key == 'com.nike.weather':
                        weather = value
                summaries = []
                if 'as2_s_activity_id' in columns['activity_summary']:
                    summaries = _q(cursor, 'SELECT '+_projection(SUMMARY_FIELDS, columns['activity_summary'])
                                   +' FROM activity_summary WHERE as2_s_activity_id = ?', (act_id,), relative)
                for metric, kind, value in summaries:
                    if metric == 'calories':
                        calories = _round(value)
                    elif metric == 'speed' and kind == 'max':
                        max_speed = _round(value)
                    elif metric == 'speed' and kind == 'mean':
                        mean_speed = _round(value)
                    elif metric == 'steps':
                        steps = value
                    elif metric == 'distance':
                        distance = _round(value)
                    elif metric == 'pace':
                        pace = _round(value)
                    elif metric == 'cadence':
                        cadence = _round(value)
                data_list.append((start_time, end_time, act_id, name, location, app_id, version,
                                  temperature, weather, duration, calories, max_speed, mean_speed,
                                  steps, distance, pace, cadence, relative))
        except sqlite3.Error as error:
            logfunc(f'Nike database error for {relative}: {error}')
        finally:
            db.close()
    data_headers = (('Start Time UTC', 'datetime'), ('End Time UTC', 'datetime'), 'Activity ID',
                    'Name', 'Location', 'Activity App ID', 'Version', 'Temperature', 'Weather',
                    'Duration (min)', 'Calories', 'Max Speed (unit unknown)',
                    'Mean Speed (unit unknown)', 'Steps', 'Distance (unit unknown)',
                    'Pace (unit unknown)', 'Cadence', 'Source File')
    return data_headers, data_list, '\n'.join(sources)

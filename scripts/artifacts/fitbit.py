# pylint: disable=W0718
__artifacts_v2__ = {'get_fitbit_activity': {'name': 'Fitbit - Activity',
                         'description': 'Activity log (phone)',
                         'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, Codex',
                         'creation_date': '2021-04-23',
                         'last_update_date': '2026-08-01',
                         'requirements': 'none',
                         'category': 'Fitbit',
                         'notes': 'ACTIVITY_LOG_ENTRY.DURATION is reported as stored and again divided '
                                  'by 60. The sleep summary in this same module divides its own '
                                  'DURATION column by 60000, so the unit of the activity DURATION '
                                  'column is not established and the divided column is labelled '
                                  "'Duration / 60' rather than as minutes. No sample_data is recorded "
                                  'for this artifact; its timestamps are read as Unix milliseconds '
                                  'without a tested sample, and only the first matching database is '
                                  'read.',
                         'paths': ('*/com.fitbit.FitbitMobile/databases/activity_db*',),
                         'output_types': 'standard',
                         'artifact_icon': 'activity'},
 'get_fitbit_device': {'name': 'Fitbit - Device Info',
                       'description': 'Device records from the core_device table (phone)',
                       'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, Codex',
                       'creation_date': '2021-04-23',
                       'last_update_date': '2026-01-12',
                       'requirements': 'none',
                       'category': 'Fitbit',
                       'notes': 'No sample_data is recorded for this artifact; its timestamps are read '
                                'as Unix milliseconds without a tested sample, and only the first '
                                'matching database is read.',
                       'paths': ('*/com.fitbit.FitbitMobile/databases/device_database*',),
                       'output_types': 'standard',
                       'artifact_icon': 'device-watch'},
 'get_fitbit_exercise': {'name': 'Fitbit - Exercise GPS',
                         'description': 'Exercise GPS trackpoints (phone)',
                         'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, Codex',
                         'creation_date': '2021-04-23',
                         'last_update_date': '2026-01-12',
                         'requirements': 'none',
                         'category': 'Fitbit',
                         'notes': 'No sample_data is recorded for this artifact; its timestamps are '
                                  'read as Unix milliseconds without a tested sample, and only the '
                                  'first matching database is read.',
                         'paths': ('*/com.fitbit.FitbitMobile/databases/exercise_db*',),
                         'output_types': 'all',
                         'artifact_icon': 'map-pin'},
 'get_fitbit_routes': {'name': 'Fitbit - Exercise Routes',
                       'description': 'Per-session exercise route map (phone)',
                       'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, Codex',
                       'creation_date': '2021-04-23',
                       'last_update_date': '2026-01-12',
                       'requirements': 'none',
                       'category': 'Fitbit',
                       'notes': 'No sample_data is recorded for this artifact; its timestamps are read '
                                'as Unix milliseconds without a tested sample, and only the first '
                                'matching database is read.',
                       'paths': ('*/com.fitbit.FitbitMobile/databases/exercise_db*',),
                       'output_types': 'standard',
                       'artifact_icon': 'map'},
 'get_fitbit_heart': {'name': 'Fitbit - Heart Rate Summary',
                      'description': 'Daily heart-rate summary (phone)',
                      'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, Codex',
                      'creation_date': '2021-04-23',
                      'last_update_date': '2026-01-12',
                      'requirements': 'none',
                      'category': 'Fitbit',
                      'notes': 'No sample_data is recorded for this artifact; its timestamps are read '
                               'as Unix milliseconds without a tested sample, and only the first '
                               'matching database is read.',
                      'paths': ('*/com.fitbit.FitbitMobile/databases/heart_rate_db*',),
                      'output_types': 'standard',
                      'artifact_icon': 'heart'},
 'get_fitbit_sleep_detail': {'name': 'Fitbit - Sleep Detail',
                             'description': 'Sleep level data (phone)',
                             'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, '
                                       'Codex',
                             'creation_date': '2021-04-23',
                             'last_update_date': '2026-01-12',
                             'requirements': 'none',
                             'category': 'Fitbit',
                             'notes': 'No sample_data is recorded for this artifact; its timestamps are '
                                      'read as Unix milliseconds without a tested sample, and only the '
                                      'first matching database is read.',
                             'paths': ('*/com.fitbit.FitbitMobile/databases/sleep*',),
                             'output_types': 'standard',
                             'artifact_icon': 'moon'},
 'get_fitbit_sleep_summary': {'name': 'Fitbit - Sleep Summary',
                              'description': 'Sleep log summary (phone)',
                              'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, '
                                        'Codex',
                              'creation_date': '2021-04-23',
                              'last_update_date': '2026-08-01',
                              'requirements': 'none',
                              'category': 'Fitbit',
                              'notes': 'SLEEP_LOG.DURATION is reported as stored and again divided by '
                                       '60000. The divisor assumes the column holds milliseconds; the '
                                       'activity log in this same module divides its own DURATION '
                                       'column by 60, and the two have not been reconciled against a '
                                       'sample database. No sample_data is recorded for this artifact; '
                                       'its timestamps are read as Unix milliseconds without a tested '
                                       'sample, and only the first matching database is read.',
                              'paths': ('*/com.fitbit.FitbitMobile/databases/sleep*',),
                              'output_types': 'standard',
                              'artifact_icon': 'moon'},
 'get_fitbit_friends': {'name': 'Fitbit - Friends',
                        'description': 'Rows of the FRIEND table (phone)',
                        'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, Codex',
                        'creation_date': '2021-04-23',
                        'last_update_date': '2026-01-12',
                        'requirements': 'none',
                        'category': 'Fitbit',
                        'notes': "The table's own FRIEND column is shown in the Friend column as "
                                 'stored, so a row is not by itself a friend. No sample_data is '
                                 'recorded for this artifact, and only the first matching database is '
                                 'read.',
                        'paths': ('*/com.fitbit.FitbitMobile/databases/social_db*',),
                        'output_types': 'standard',
                        'artifact_icon': 'users'},
 'get_fitbit_user': {'name': 'Fitbit - User Profile',
                     'description': 'User profile (phone)',
                     'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, Codex',
                     'creation_date': '2021-04-23',
                     'last_update_date': '2026-10-04',
                     'requirements': 'none',
                     'category': 'Fitbit',
                     'notes': 'Joined Date (UTC) and Date of Birth (UTC) show USER_PROFILE.JOINED_DATE '
                              'and DATE_OF_BIRTH read as Unix milliseconds and written out in UTC as '
                              'plain text. The two columns are not typed as date-times, so a report '
                              "viewer does not shift them to another time zone. Fitbit's Web API "
                              'documents the matching profile fields, memberSince and dateOfBirth, as '
                              'dates (https://dev.fitbit.com/build/reference/web-api/user/get-profile/, '
                              'read 2026-10-04). On the three registered images whose USER_PROFILE '
                              'table held a row (kevin_pocox7_a15, russell_pixel6a_a13 and russell_a14, '
                              'one row each, read from copies of social_db) both values fell on a whole '
                              'hour that was not midnight in UTC (05:00 on one image, 04:00 on the '
                              'other two), and TIMEZONE and TIMEZONE_OFFSET were empty. That is '
                              'consistent with a calendar date stored at midnight in a zone the row '
                              'does not record; which zone is not established. Under that reading the '
                              'time of day shown is not a time of an event, and for a zone ahead of UTC '
                              'the UTC rendering would fall on the previous calendar day; no tested row '
                              'showed that. The Timezone and Timezone Offset columns show TIMEZONE and '
                              'TIMEZONE_OFFSET as stored; the unit of TIMEZONE_OFFSET is not '
                              'established. Last Updated was not on a whole hour on the three rows. '
                              'Five more registered images hold the table with no row (pixel7a_a14, '
                              'hc_pixel8pro_a16, hc_pixel8pro_a17, samsunga53_a14, pixel3_a12), and two '
                              'more that carry the file were not read (userb2_a13, pixel3_a11). No '
                              'sample_data is recorded for this artifact, and only the first matching '
                              'database is read.',
                     'paths': ('*/com.fitbit.FitbitMobile/databases/social_db*',),
                     'output_types': 'standard',
                     'artifact_icon': 'user'},
 'get_fitbit_steps': {'name': 'Fitbit - Steps',
                      'description': 'Pedometer minute data (phone)',
                      'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, Codex',
                      'creation_date': '2021-04-23',
                      'last_update_date': '2026-01-12',
                      'requirements': 'none',
                      'category': 'Fitbit',
                      'notes': 'No sample_data is recorded for this artifact; its timestamps are read '
                               'as Unix milliseconds without a tested sample, and only the first '
                               'matching database is read.',
                      'paths': ('*/com.fitbit.FitbitMobile/databases/mobile_track_db*',),
                      'output_types': 'standard',
                      'artifact_icon': 'activity'},
 'get_fitbit_wearos_profile': {'name': 'Fitbit - User Profile (Wear OS)',
                               'description': 'User profile (Wear OS)',
                               'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, '
                                         'Codex',
                               'creation_date': '2021-04-23',
                               'last_update_date': '2026-01-12',
                               'requirements': 'none',
                               'category': 'Fitbit',
                               'notes': 'No sample_data is recorded for this artifact; its values are '
                                        'reported as stored, and only the first matching database is '
                                        'read.',
                               'paths': ('*/com.fitbit.FitbitMobile/databases/user.db*',),
                               'output_types': 'standard',
                               'artifact_icon': 'user'},
 'get_fitbit_wearos_activity': {'name': 'Fitbit - Activity History (Wear OS)',
                                'description': 'Activity/workout history (Wear OS)',
                                'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, '
                                          'Codex',
                                'creation_date': '2021-04-23',
                                'last_update_date': '2026-10-04',
                                'requirements': 'none',
                                'category': 'Fitbit',
                                'notes': 'ActivityExerciseEntity.duration is reported as stored under '
                                         "'Duration (as stored)' and again divided by 60000 under "
                                         "'Duration / 60000', with any remainder dropped. The divisor "
                                         'gives minutes only if the column holds milliseconds; the unit '
                                         'is not established, so the divided column is not labelled as '
                                         'minutes. No registered image was found to hold this database '
                                         '(20 zip images and 2 phone tar images listed on 2026-10-04). '
                                         'No sample_data is recorded for this artifact; its timestamps '
                                         'are read as Unix milliseconds without a tested sample, and '
                                         'only the first matching database is read.',
                                'paths': ('*/com.fitbit.FitbitMobile/databases/user.db*',),
                                'output_types': 'standard',
                                'artifact_icon': 'activity'},
 'get_fitbit_wearos_daily': {'name': 'Fitbit - Daily Activity (Wear OS)',
                             'description': 'Daily sedentary summary (Wear OS)',
                             'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, '
                                       'Codex',
                             'creation_date': '2021-04-23',
                             'last_update_date': '2026-08-01',
                             'requirements': 'none',
                             'category': 'Fitbit',
                             'notes': 'SedentaryDataEntity.longestDuration is reported as stored; the '
                                      'database does not record its unit, so it is not labelled as '
                                      'minutes. The two totalMinutes* columns are named as minutes by '
                                      'the columns themselves. No sample_data is recorded for this '
                                      'artifact; its values are reported as stored, and only the first '
                                      'matching database is read.',
                             'paths': ('*/com.fitbit.FitbitMobile/databases/user.db*',),
                             'output_types': 'standard',
                             'artifact_icon': 'activity'},
 'get_fitbit_wearos_hourly': {'name': 'Fitbit - Hourly Steps (Wear OS)',
                              'description': 'Hourly steps from JSON (Wear OS)',
                              'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, '
                                        'Codex',
                              'creation_date': '2021-04-23',
                              'last_update_date': '2026-01-12',
                              'requirements': 'none',
                              'category': 'Fitbit',
                              'notes': 'No sample_data is recorded for this artifact; its values are '
                                       'reported as stored, and only the first matching database is '
                                       'read.',
                              'paths': ('*/com.fitbit.FitbitMobile/databases/user.db*',),
                              'output_types': 'standard',
                              'artifact_icon': 'activity'},
 'get_fitbit_wearos_sleep_logs': {'name': 'Fitbit - Sleep Logs (Wear OS)',
                                  'description': 'Sleep session logs (Wear OS)',
                                  'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, '
                                            'Codex',
                                  'creation_date': '2021-04-23',
                                  'last_update_date': '2026-01-12',
                                  'requirements': 'none',
                                  'category': 'Fitbit',
                                  'notes': 'No sample_data is recorded for this artifact; its '
                                           'timestamps are read as Unix milliseconds without a tested '
                                           'sample, and only the first matching database is read.',
                                  'paths': ('*/com.fitbit.FitbitMobile/databases/user.db*',),
                                  'output_types': 'standard',
                                  'artifact_icon': 'moon'},
 'get_fitbit_wearos_workouts': {'name': 'Fitbit - Workouts (Wear OS)',
                                'description': 'Workout summaries (Wear OS)',
                                'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, '
                                          'Codex',
                                'creation_date': '2021-04-23',
                                'last_update_date': '2026-10-04',
                                'requirements': 'none',
                                'category': 'Fitbit',
                                'notes': 'The column headed Time is ExerciseSummaryEntity.time; what '
                                         'that time marks is not established. No registered image was '
                                         'found to hold this database (20 zip images and 2 phone tar '
                                         'images listed on 2026-10-04). No sample_data is recorded for '
                                         'this artifact; its timestamps are read as Unix milliseconds '
                                         'without a tested sample, and only the first matching database '
                                         'is read.',
                                'paths': ('*/com.fitbit.FitbitMobile/databases/passive_stats.db*',),
                                'output_types': 'standard',
                                'artifact_icon': 'activity'},
 'get_fitbit_wearos_gps': {'name': 'Fitbit - GPS Trackpoints (Wear OS)',
                           'description': 'GPS trackpoints (Wear OS)',
                           'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, Codex',
                           'creation_date': '2021-04-23',
                           'last_update_date': '2026-01-12',
                           'requirements': 'none',
                           'category': 'Fitbit',
                           'notes': 'No sample_data is recorded for this artifact; its timestamps are '
                                    'read as Unix milliseconds without a tested sample, and only the '
                                    'first matching database is read.',
                           'paths': ('*/com.fitbit.FitbitMobile/databases/passive_stats.db*',),
                           'output_types': 'all',
                           'artifact_icon': 'map-pin'},
 'get_fitbit_wearos_gps_route': {'name': 'Fitbit - GPS Route (Wear OS)',
                                 'description': 'A route drawn through ExerciseGpsEntity trackpoints with nonzero latitude and longitude, as selected by the parser.',
                                 'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, '
                                           'Codex',
                                 'creation_date': '2021-04-23',
                                 'last_update_date': '2026-01-12',
                                 'requirements': 'none',
                                 'category': 'Fitbit',
                                 'notes': 'No sample_data is recorded for this artifact; its timestamps '
                                          'are read as Unix milliseconds without a tested sample, and '
                                          'only the first matching database is read. Every selected '
                                          'trackpoint in the table is drawn as one route in time order; '
                                          'the query reads no session column, so the route is not split '
                                          'by exercise session and can join points from separate '
                                          'sessions. Latitude and Longitude are those of the first '
                                          'selected trackpoint.',
                                 'paths': ('*/com.fitbit.FitbitMobile/databases/passive_stats.db*',),
                                 'output_types': 'standard',
                                 'artifact_icon': 'map'},
 'get_fitbit_wearos_hr': {'name': 'Fitbit - Heart Rate Stats (Wear OS)',
                          'description': 'Heart-rate stats (Wear OS)',
                          'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, Codex',
                          'creation_date': '2021-04-23',
                          'last_update_date': '2026-08-01',
                          'requirements': 'none',
                          'category': 'Fitbit',
                          'notes': 'HeartRateStatEntity.value is reported as stored under the header '
                                   "'Value'; the database does not record its unit, so it is not "
                                   'published as BPM. No sample_data is recorded for this artifact; its '
                                   'timestamps are read as Unix milliseconds without a tested sample, '
                                   'and only the first matching database is read.',
                          'paths': ('*/com.fitbit.FitbitMobile/databases/passive_stats.db*',),
                          'output_types': 'standard',
                          'artifact_icon': 'heart'},
 'get_fitbit_wearos_pace': {'name': 'Fitbit - Live Pace (Wear OS)',
                            'description': 'LivePaceEntity rows (Wear OS)',
                            'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, Codex',
                            'creation_date': '2021-04-23',
                            'last_update_date': '2026-08-01',
                            'requirements': 'none',
                            'category': 'Fitbit',
                            'notes': 'LivePaceEntity.timeSeconds is decoded as a Unix epoch in seconds, '
                                     'following the column name; this decoding has not been checked '
                                     'against a sample database. LivePaceEntity.value is reported as '
                                     'stored; the database does not record its unit. No sample_data is '
                                     'recorded for this artifact, and only the first matching database '
                                     'is read.',
                            'paths': ('*/com.fitbit.FitbitMobile/databases/passive_stats.db*',),
                            'output_types': 'standard',
                            'artifact_icon': 'activity'},
 'get_fitbit_wearos_sleep': {'name': 'Fitbit - Sleep (Wear OS)',
                             'description': 'Local sleep periods (Wear OS)',
                             'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, '
                                       'Codex',
                             'creation_date': '2021-04-23',
                             'last_update_date': '2026-01-12',
                             'requirements': 'none',
                             'category': 'Fitbit',
                             'notes': 'No sample_data is recorded for this artifact; its timestamps are '
                                      'read as Unix milliseconds without a tested sample, and only the '
                                      'first matching database is read.',
                             'paths': ('*/com.fitbit.FitbitMobile/databases/passive_stats.db*',),
                             'output_types': 'standard',
                             'artifact_icon': 'moon'},
 'get_fitbit_wearos_azm': {'name': 'Fitbit - Active Zones (Wear OS)',
                           'description': 'PassiveAzmEntity rows (Wear OS)',
                           'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, Codex',
                           'creation_date': '2021-04-23',
                           'last_update_date': '2026-08-01',
                           'requirements': 'none',
                           'category': 'Fitbit',
                           'notes': 'PassiveAzmEntity.value is reported as stored under the header '
                                    "'Value'; the database does not record what it counts, so it is not "
                                    'published as points. No sample_data is recorded for this artifact; '
                                    'its timestamps are read as Unix milliseconds without a tested '
                                    'sample, and only the first matching database is read.',
                           'paths': ('*/com.fitbit.FitbitMobile/databases/passive_stats.db*',),
                           'output_types': 'standard',
                           'artifact_icon': 'heart'},
 'get_fitbit_wearos_splits': {'name': 'Fitbit - Workout Splits (Wear OS)',
                              'description': 'Workout split metrics (Wear OS)',
                              'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, '
                                        'Codex',
                              'creation_date': '2021-04-23',
                              'last_update_date': '2026-01-12',
                              'requirements': 'none',
                              'category': 'Fitbit',
                              'notes': 'No sample_data is recorded for this artifact; its timestamps '
                                       'are read as Unix milliseconds without a tested sample, and only '
                                       'the first matching database is read.',
                              'paths': ('*/com.fitbit.FitbitMobile/databases/passive_stats.db*',),
                              'output_types': 'standard',
                              'artifact_icon': 'activity'},
 'get_fitbit_wearos_opaque_hr': {'name': 'Fitbit - Opaque HR (Wear OS)',
                                 'description': 'OpaqueHeartRateEntity rows: baseHeartRate and '
                                                'confidence as stored (Wear OS)',
                                 'author': '@AlexisBrignoni / @segumarc / Ganeshbs17, @AlexisBrignoni, '
                                           'Codex',
                                 'creation_date': '2021-04-23',
                                 'last_update_date': '2026-01-12',
                                 'requirements': 'none',
                                 'category': 'Fitbit',
                                 'notes': 'No sample_data is recorded for this artifact; its timestamps '
                                          'are read as Unix milliseconds without a tested sample, and '
                                          'only the first matching database is read.',
                                 'paths': ('*/com.fitbit.FitbitMobile/databases/passive_stats.db*',),
                                 'output_types': 'standard',
                                 'artifact_icon': 'heart'}}

import datetime
import json
import sqlite3

from scripts.geo_utils import render_gps_track_png, build_track_kml
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, check_in_embedded_media


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _ms_to_utc_text(value):
    # A stored date read as Unix milliseconds, shown as plain text and not typed as a date-time.
    moment = _ms_to_utc(value)
    return moment.strftime('%Y-%m-%d %H:%M:%S') if moment else ''


def _sec_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _find(files_found, suffix):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith(suffix):
            return file_found
    return ''


def _run(source_path, sql):
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


def _route_media(source, coords, title, subtitle, base):
    route_map = ''
    png = render_gps_track_png(coords, title=title, subtitle=subtitle)
    if png:
        route_map = check_in_embedded_media(source, png, f'{base}.png', force_type='image/png',
                                            force_extension='png') or ''
    route_kml = ''
    kml = build_track_kml(coords, name=base)
    if kml:
        route_kml = check_in_embedded_media(source, kml, f'{base}.kml',
                                            force_type='application/vnd.google-earth.kml+xml',
                                            force_extension='kml') or ''
    return route_map, route_kml


@artifact_processor
def get_fitbit_activity(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'activity_db')
    rows = _run(src, '''SELECT LOG_DATE, TIME_CREATED, NAME, LOG_TYPE, ACTIVE_DURATION, SPEED, PACE,
        ELEVATION_GAIN, AVERAGE_HEART_RATE, DISTANCE, DISTANCE_UNIT, DURATION, DURATION/60, STEPS,
        DETAILS_TYPE, CALORIES, MANUAL_CALORIES_POPULATED, SOURCE_NAME, SOURCE_TYPE, HAS_GPS,
        SWIM_LENGTHS, POOL_LENGTH, POOL_LENGTH_UNIT, VERY_ACTIVE_MINUTES, MODERATELY_ACTIVE_MINUTES,
        FAT_BURN_HEART_RATE_ZONE, CARDIO_HEART_RATE_ZONE, PEAK_HEART_RATE_ZONE FROM ACTIVITY_LOG_ENTRY''')
    rel = context.get_relative_path(src)
    data_list = [(_ms_to_utc(r[0]), _ms_to_utc(r[1])) + tuple(r[2:]) + (rel,) for r in rows]
    data_headers = (('Timestamp', 'datetime'), ('Time Created', 'datetime'), 'Name', 'Log Type',
                    'Active Duration', 'Speed', 'Pace', 'Elevation Gain', 'Avg Heart Rate', 'Distance',
                    'Distance Unit', 'Duration (as stored)', 'Duration / 60', 'Steps', 'Details Type',
                    'Calories', 'Manual Calories Populated', 'Source Name', 'Source Type', 'Has GPS',
                    'Swim Lengths', 'Pool Length', 'Pool Length Unit', 'Very Active Minutes',
                    'Moderately Active Minutes', 'Fat Burn HR Zone', 'Cardio HR Zone', 'Peak HR Zone',
                    'Source File')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_device(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'device_database')
    rows = _run(src, '''SELECT lastsynctime, deviceName, bleMacAddress, batteryPercent, deviceType
        FROM core_device''')
    rel = context.get_relative_path(src)
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], rel) for r in rows]
    data_headers = (('Last Synced Timestamp', 'datetime'), 'Device Name', 'Bluetooth MAC Address',
                    'Battery Percentage', 'Device Type', 'Source File')
    return data_headers, data_list, src


def _phone_gps_rows(src):
    return _run(src, '''SELECT TIME, LABEL, LATITUDE, LONGITUDE, ACCURACY, ALTITUDE, SPEED, PACE,
        SESSION_ID FROM EXERCISE_EVENT ORDER BY SESSION_ID, TIME''')


@artifact_processor
def get_fitbit_exercise(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'exercise_db')
    rel = context.get_relative_path(src)
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], rel)
                 for r in _phone_gps_rows(src)]
    data_headers = (('Timestamp', 'datetime'), 'Label', 'Latitude', 'Longitude', 'Accuracy',
                    'Altitude', 'Speed', 'Pace', 'Session ID', 'Source File')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_routes(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'exercise_db')
    sessions = {}
    for r in _phone_gps_rows(src):
        if r[2] and r[3]:
            sessions.setdefault(r[8], []).append((r[2], r[3], r[0]))
    data_list = []
    for session_id, pts in sessions.items():
        coords = [(p[0], p[1]) for p in pts]
        start = _ms_to_utc(pts[0][2])
        end = _ms_to_utc(pts[-1][2])
        title = f'Fitbit session {session_id}'
        subtitle = start.strftime('%Y-%m-%d %H:%M UTC') if start else ''
        route_map, route_kml = _route_media(src, coords, title, subtitle, f'{session_id}_route')
        data_list.append((session_id, len(coords), start, end, coords[0][0], coords[0][1],
                          route_map, route_kml))
    data_headers = ('Session ID', 'Points', ('Start Time', 'datetime'), ('End Time', 'datetime'),
                    'Latitude', 'Longitude', ('Route Map', 'media'), ('Route KML', 'media'))
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_heart(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'heart_rate_db')
    rows = _run(src, 'SELECT DATE_TIME, AVERAGE_HEART_RATE, RESTING_HEART_RATE FROM HEART_RATE_DAILY_SUMMARY')
    rel = context.get_relative_path(src)
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], rel) for r in rows]
    data_headers = (('Timestamp', 'datetime'), 'Avg Heart Rate', 'Resting Heart Rate', 'Source File')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_sleep_detail(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'sleep')
    rows = _run(src, 'SELECT DATE_TIME, SECONDS, LEVEL_STRING, LOG_ID FROM SLEEP_LEVEL_DATA')
    rel = context.get_relative_path(src)
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], rel) for r in rows]
    data_headers = (('Timestamp', 'datetime'), 'Seconds', 'Level', 'Log ID', 'Source File')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_sleep_summary(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'sleep')
    rows = _run(src, '''SELECT DATE_OF_SLEEP, START_TIME, SYNC_STATUS_STRING, DURATION, DURATION/60000,
        MINUTES_AFTER_WAKEUP, MINUTES_ASLEEP, MINUTES_AWAKE, MINUTES_TO_FALL_ASLEEP, LOG_ID FROM SLEEP_LOG''')
    rel = context.get_relative_path(src)
    data_list = [(_ms_to_utc(r[0]), _ms_to_utc(r[1]), r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], rel)
                 for r in rows]
    data_headers = (('Timestamp', 'datetime'), ('Start Time', 'datetime'), 'Sync Status',
                    'Duration (as stored)', 'Duration / 60000', 'Minutes After Wakeup', 'Minutes Asleep',
                    'Minutes Awake', 'Minutes to Fall Asleep', 'Log ID', 'Source File')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_friends(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'social_db')
    rows = _run(src, 'SELECT OWNING_USER_ID, ENCODED_ID, DISPLAY_NAME, AVATAR_URL, FRIEND, CHILD FROM FRIEND')
    rel = context.get_relative_path(src)
    data_list = [(r[0], r[1], r[2], r[3], r[4], r[5], rel) for r in rows]
    data_headers = ('Owning User ID', 'Encoded ID', 'Display Name', 'Avatar URL', 'Friend', 'Child',
                    'Source File')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_user(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'social_db')
    rows = _run(src, '''SELECT LAST_UPDATED, DISPLAY_NAME, FULL_NAME, ABOUT_ME, AVATAR_URL,
        COVER_PHOTO_URL, CITY, STATE, COUNTRY, JOINED_DATE, DATE_OF_BIRTH, HEIGHT, WEIGHT, GENDER, COACH,
        TIMEZONE, TIMEZONE_OFFSET
        FROM USER_PROFILE''')
    if not rows:
        # A table without the two time zone columns: read it without them.
        rows = _run(src, '''SELECT LAST_UPDATED, DISPLAY_NAME, FULL_NAME, ABOUT_ME, AVATAR_URL,
            COVER_PHOTO_URL, CITY, STATE, COUNTRY, JOINED_DATE, DATE_OF_BIRTH, HEIGHT, WEIGHT, GENDER,
            COACH, NULL, NULL
            FROM USER_PROFILE''')
    rel = context.get_relative_path(src)
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], _ms_to_utc_text(r[9]),
                  _ms_to_utc_text(r[10]), r[15], r[16], r[11], r[12], r[13], r[14], rel) for r in rows]
    data_headers = (('Last Updated', 'datetime'), 'Display Name', 'Full Name', 'About Me', 'Avatar URL',
                    'Cover Photo URL', 'City', 'State', 'Country', 'Joined Date (UTC)',
                    'Date of Birth (UTC)', 'Timezone', 'Timezone Offset', 'Height', 'Weight',
                    'Gender', 'Coach', 'Source File')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_steps(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'mobile_track_db')
    rows = _run(src, '''SELECT TIMESTAMP, STEPS_COUNT, METS_COUNT, TIME_CREATED, TIME_UPDATED
        FROM PEDOMETER_MINUTE_DATA''')
    rel = context.get_relative_path(src)
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], _ms_to_utc(r[3]), _ms_to_utc(r[4]), rel) for r in rows]
    data_headers = (('Timestamp', 'datetime'), 'Steps Count', 'Mets Count', ('Time Created', 'datetime'),
                    ('Time Updated', 'datetime'), 'Source File')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_wearos_profile(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'user.db')
    rows = _run(src, '''SELECT fullName, displayName, email, gender, dateOfBirth, height, weight,
        memberSince, userId FROM FitbitProfileEntity''')
    data_list = [tuple(r) for r in rows]
    data_headers = ('Full Name', 'Display Name', 'Email', 'Gender', 'DOB', 'Height', 'Weight',
                    'Member Since', 'User ID')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_wearos_activity(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'user.db')
    rows = _run(src, '''SELECT startTime, name, duration, duration/60000, distance, distanceUnit, steps,
        calories, averageHeartRate, elevationGain, activeZoneMinutes, logId FROM ActivityExerciseEntity
        ORDER BY startTime DESC''')
    data_list = [(_ms_to_utc(r[0]),) + tuple(r[1:]) for r in rows]
    data_headers = (('Start Time', 'datetime'), 'Activity Name', 'Duration (as stored)', 'Duration / 60000',
                    'Distance', 'Unit',
                    'Steps', 'Calories', 'Avg HR', 'Elevation', 'AZM', 'Log ID')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_wearos_daily(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'user.db')
    rows = _run(src, '''SELECT date, totalMinutesMoving, totalMinutesSedentary, longestDuration,
        longestStart FROM SedentaryDataEntity ORDER BY date DESC''')
    data_list = [tuple(r) for r in rows]
    data_headers = ('Date', 'Total Moving Mins', 'Total Sedentary Mins',
                    'Longest Sedentary Duration (as stored)', 'Longest Sedentary Start Time')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_wearos_hourly(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'user.db')
    data_list = []
    for r in _run(src, 'SELECT date, hourlyData FROM SedentaryDataEntity ORDER BY date DESC'):
        if not r[1]:
            continue
        try:
            entries = json.loads(r[1]).get('hourlyData', [])
        except (ValueError, TypeError):
            continue
        for entry in entries:
            time_str = entry.get('dateTime', '')
            data_list.append((f'{r[0]} {time_str}', r[0], time_str, entry.get('steps', '0')))
    data_headers = ('Full Timestamp', 'Date', 'Time', 'Steps')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_wearos_sleep_logs(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'user.db')
    rows = _run(src, '''SELECT startTime, endTime, dateOfSleep, minutesAsleep, minutesAwake,
        minutesToFallAsleep, minutesAfterWakeup, type, isMainSleep FROM FitbitSleepDateEntity
        ORDER BY startTime DESC''')
    data_list = [(_ms_to_utc(r[0]), _ms_to_utc(r[1])) + tuple(r[2:]) for r in rows]
    data_headers = (('Sleep Start', 'datetime'), ('Sleep End', 'datetime'), 'Date of Sleep',
                    'Mins Asleep', 'Mins Awake', 'Time to Fall Asleep', 'Time After Wakeup', 'Type',
                    'Is Main Sleep')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_wearos_workouts(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'passive_stats.db')
    rows = _run(src, '''SELECT time, sessionId, exerciseTypeId, totalDistanceMm/1000000.0, steps,
        caloriesBurned, avgHeartRate, elevationGainFt FROM ExerciseSummaryEntity ORDER BY time DESC''')
    data_list = [(_ms_to_utc(r[0]),) + tuple(r[1:]) for r in rows]
    data_headers = (('Time', 'datetime'), 'Session ID', 'Activity Type ID', 'Distance (km)',
                    'Steps', 'Calories', 'Avg HR', 'Elevation (ft)')
    return data_headers, data_list, src


def _wearos_gps_rows(src):
    return _run(src, '''SELECT time, latitude, longitude, altitude, speed, bearing,
        estimatedPositionError FROM ExerciseGpsEntity ORDER BY time ASC''')


@artifact_processor
def get_fitbit_wearos_gps(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'passive_stats.db')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[6]) for r in _wearos_gps_rows(src)]
    data_headers = (('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Altitude', 'Speed',
                    'Est. Error')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_wearos_gps_route(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'passive_stats.db')
    rows = _wearos_gps_rows(src)
    coords = [(r[1], r[2]) for r in rows if r[1] and r[2]]
    data_list = []
    if coords:
        start = _ms_to_utc(rows[0][0])
        end = _ms_to_utc(rows[-1][0])
        subtitle = start.strftime('%Y-%m-%d %H:%M UTC') if start else ''
        route_map, route_kml = _route_media(src, coords, 'Fitbit Wear OS GPS route', subtitle,
                                             'wearos_gps_route')
        data_list.append((len(coords), start, end, coords[0][0], coords[0][1], route_map, route_kml))
    data_headers = ('Points', ('Start Time', 'datetime'), ('End Time', 'datetime'), 'Latitude',
                    'Longitude', ('Route Map', 'media'), ('Route KML', 'media'))
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_wearos_hr(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'passive_stats.db')
    rows = _run(src, 'SELECT startTime, endTime, value, accuracy FROM HeartRateStatEntity ORDER BY startTime DESC')
    data_list = [(_ms_to_utc(r[0]), _ms_to_utc(r[1]), r[2], r[3]) for r in rows]
    data_headers = (('Start Time', 'datetime'), ('End Time', 'datetime'), 'Value', 'Accuracy')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_wearos_pace(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'passive_stats.db')
    rows = _run(src, 'SELECT timeSeconds, sessionId, statType, value FROM LivePaceEntity ORDER BY timeSeconds DESC')
    # decoded per the column name (timeSeconds), not as milliseconds
    data_list = [(_sec_to_utc(r[0]), r[1], r[2], r[3]) for r in rows]
    data_headers = (('Timestamp', 'datetime'), 'Session ID', 'Stat Type', 'Value')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_wearos_sleep(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'passive_stats.db')
    rows = _run(src, '''SELECT sleepStartTime, sleepEndTime, (sleepEndTime-sleepStartTime)/1000/60
        FROM LocalSleepPeriodsEntity ORDER BY sleepStartTime DESC''')
    data_list = [(_ms_to_utc(r[0]), _ms_to_utc(r[1]), r[2]) for r in rows]
    data_headers = (('Sleep Start', 'datetime'), ('Sleep End', 'datetime'), 'Duration (min)')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_wearos_azm(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'passive_stats.db')
    rows = _run(src, 'SELECT startTime, endTime, activeZone, value, lastBpm FROM PassiveAzmEntity ORDER BY startTime DESC')
    data_list = [(_ms_to_utc(r[0]), _ms_to_utc(r[1]), r[2], r[3], r[4]) for r in rows]
    data_headers = (('Start Time', 'datetime'), ('End Time', 'datetime'), 'Zone ID', 'Value', 'Last BPM')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_wearos_splits(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'passive_stats.db')
    rows = _run(src, '''SELECT time, sessionId, avgPaceMilliSecPerKm/1000/60.0, avgHeartRate, steps,
        caloriesBurned FROM ExerciseSplitAnnotationEntity ORDER BY time ASC''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5]) for r in rows]
    data_headers = (('Split Time', 'datetime'), 'Session ID', 'Avg Pace (Min/Km)', 'Avg HR', 'Steps',
                    'Calories')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_wearos_opaque_hr(context):
    files_found = context.get_files_found()
    src = _find(files_found, 'passive_stats.db')
    rows = _run(src, 'SELECT timestamp, baseHeartRate, confidence FROM OpaqueHeartRateEntity ORDER BY timestamp DESC')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2]) for r in rows]
    data_headers = (('Timestamp', 'datetime'), 'Base HR', 'Confidence')
    return data_headers, data_list, src

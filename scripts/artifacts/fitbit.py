# pylint: disable=W0613,W0718
_PATHS_PHONE_ACT = ('*/com.fitbit.FitbitMobile/databases/activity_db*',)
_PATHS_PHONE_DEV = ('*/com.fitbit.FitbitMobile/databases/device_database*',)
_PATHS_PHONE_EX = ('*/com.fitbit.FitbitMobile/databases/exercise_db*',)
_PATHS_PHONE_HR = ('*/com.fitbit.FitbitMobile/databases/heart_rate_db*',)
_PATHS_PHONE_SLEEP = ('*/com.fitbit.FitbitMobile/databases/sleep*',)
_PATHS_PHONE_SOCIAL = ('*/com.fitbit.FitbitMobile/databases/social_db*',)
_PATHS_PHONE_MOBILE = ('*/com.fitbit.FitbitMobile/databases/mobile_track_db*',)
_PATHS_USER = ('*/com.fitbit.FitbitMobile/databases/user.db*',)
_PATHS_PASSIVE = ('*/com.fitbit.FitbitMobile/databases/passive_stats.db*',)


def _art(name, desc, paths, icon='activity', outtypes='standard'):
    return {"name": name, "description": desc, "author": "@AlexisBrignoni / @segumarc / Ganeshbs17",
            "creation_date": "2021-04-23", "last_update_date": "2026-01-12", "requirements": "none",
            "category": "Fitbit", "notes": "", "paths": paths, "output_types": outtypes,
            "artifact_icon": icon}


__artifacts_v2__ = {
    "get_fitbit_activity": _art("Fitbit - Activity", "Activity log (phone)", _PATHS_PHONE_ACT),
    "get_fitbit_device": _art("Fitbit - Device Info", "Paired device info (phone)", _PATHS_PHONE_DEV, "watch"),
    "get_fitbit_exercise": _art("Fitbit - Exercise GPS", "Exercise GPS trackpoints (phone)", _PATHS_PHONE_EX, "map-pin", "all"),
    "get_fitbit_routes": _art("Fitbit - Exercise Routes", "Per-session exercise route map (phone)", _PATHS_PHONE_EX, "map"),
    "get_fitbit_heart": _art("Fitbit - Heart Rate Summary", "Daily heart-rate summary (phone)", _PATHS_PHONE_HR, "heart"),
    "get_fitbit_sleep_detail": _art("Fitbit - Sleep Detail", "Sleep level data (phone)", _PATHS_PHONE_SLEEP, "moon"),
    "get_fitbit_sleep_summary": _art("Fitbit - Sleep Summary", "Sleep log summary (phone)", _PATHS_PHONE_SLEEP, "moon"),
    "get_fitbit_friends": _art("Fitbit - Friends", "Friends (phone)", _PATHS_PHONE_SOCIAL, "users"),
    "get_fitbit_user": _art("Fitbit - User Profile", "User profile (phone)", _PATHS_PHONE_SOCIAL, "user"),
    "get_fitbit_steps": _art("Fitbit - Steps", "Pedometer minute data (phone)", _PATHS_PHONE_MOBILE, "activity"),
    "get_fitbit_wearos_profile": _art("Fitbit - User Profile (Wear OS)", "User profile (Wear OS)", _PATHS_USER, "user"),
    "get_fitbit_wearos_activity": _art("Fitbit - Activity History (Wear OS)", "Activity/workout history (Wear OS)", _PATHS_USER),
    "get_fitbit_wearos_daily": _art("Fitbit - Daily Activity (Wear OS)", "Daily sedentary summary (Wear OS)", _PATHS_USER),
    "get_fitbit_wearos_hourly": _art("Fitbit - Hourly Steps (Wear OS)", "Hourly steps from JSON (Wear OS)", _PATHS_USER),
    "get_fitbit_wearos_sleep_logs": _art("Fitbit - Sleep Logs (Wear OS)", "Sleep session logs (Wear OS)", _PATHS_USER, "moon"),
    "get_fitbit_wearos_workouts": _art("Fitbit - Workouts (Wear OS)", "Workout summaries (Wear OS)", _PATHS_PASSIVE),
    "get_fitbit_wearos_gps": _art("Fitbit - GPS Trackpoints (Wear OS)", "GPS trackpoints (Wear OS)", _PATHS_PASSIVE, "map-pin", "all"),
    "get_fitbit_wearos_gps_route": _art("Fitbit - GPS Route (Wear OS)", "Offline GPS route map (Wear OS)", _PATHS_PASSIVE, "map"),
    "get_fitbit_wearos_hr": _art("Fitbit - Heart Rate Stats (Wear OS)", "Heart-rate stats (Wear OS)", _PATHS_PASSIVE, "heart"),
    "get_fitbit_wearos_pace": _art("Fitbit - Live Pace (Wear OS)", "Live pace during workouts (Wear OS)", _PATHS_PASSIVE),
    "get_fitbit_wearos_sleep": _art("Fitbit - Sleep (Wear OS)", "Local sleep periods (Wear OS)", _PATHS_PASSIVE, "moon"),
    "get_fitbit_wearos_azm": _art("Fitbit - Active Zones (Wear OS)", "Active zone minutes (Wear OS)", _PATHS_PASSIVE, "heart"),
    "get_fitbit_wearos_splits": _art("Fitbit - Workout Splits (Wear OS)", "Workout split metrics (Wear OS)", _PATHS_PASSIVE),
    "get_fitbit_wearos_opaque_hr": _art("Fitbit - Opaque HR (Wear OS)", "Raw heart-rate readings (Wear OS)", _PATHS_PASSIVE, "heart"),
}

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
def get_fitbit_activity(files_found, report_folder, seeker, wrap_text):
    src = _find(files_found, 'activity_db')
    rows = _run(src, '''SELECT LOG_DATE, TIME_CREATED, NAME, LOG_TYPE, ACTIVE_DURATION, SPEED, PACE,
        ELEVATION_GAIN, AVERAGE_HEART_RATE, DISTANCE, DISTANCE_UNIT, DURATION, DURATION/60, STEPS,
        DETAILS_TYPE, CALORIES, MANUAL_CALORIES_POPULATED, SOURCE_NAME, SOURCE_TYPE, HAS_GPS,
        SWIM_LENGTHS, POOL_LENGTH, POOL_LENGTH_UNIT, VERY_ACTIVE_MINUTES, MODERATELY_ACTIVE_MINUTES,
        FAT_BURN_HEART_RATE_ZONE, CARDIO_HEART_RATE_ZONE, PEAK_HEART_RATE_ZONE FROM ACTIVITY_LOG_ENTRY''')
    data_list = [(_ms_to_utc(r[0]), _ms_to_utc(r[1])) + tuple(r[2:]) + (src,) for r in rows]
    data_headers = (('Timestamp', 'datetime'), ('Time Created', 'datetime'), 'Name', 'Log Type',
                    'Active Duration', 'Speed', 'Pace', 'Elevation Gain', 'Avg Heart Rate', 'Distance',
                    'Distance Unit', 'Duration', 'Duration in Minutes', 'Steps', 'Details Type',
                    'Calories', 'Manual Calories Populated', 'Source Name', 'Source Type', 'Has GPS',
                    'Swim Lengths', 'Pool Length', 'Pool Length Unit', 'Very Active Minutes',
                    'Moderately Active Minutes', 'Fat Burn HR Zone', 'Cardio HR Zone', 'Peak HR Zone',
                    'Source File')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_device(files_found, report_folder, seeker, wrap_text):
    src = _find(files_found, 'device_database')
    rows = _run(src, '''SELECT lastsynctime, deviceName, bleMacAddress, batteryPercent, deviceType
        FROM core_device''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], src) for r in rows]
    data_headers = (('Last Synced Timestamp', 'datetime'), 'Device Name', 'Bluetooth MAC Address',
                    'Battery Percentage', 'Device Type', 'Source File')
    return data_headers, data_list, src


def _phone_gps_rows(src):
    return _run(src, '''SELECT TIME, LABEL, LATITUDE, LONGITUDE, ACCURACY, ALTITUDE, SPEED, PACE,
        SESSION_ID FROM EXERCISE_EVENT ORDER BY SESSION_ID, TIME''')


@artifact_processor
def get_fitbit_exercise(files_found, report_folder, seeker, wrap_text):
    src = _find(files_found, 'exercise_db')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], src)
                 for r in _phone_gps_rows(src)]
    data_headers = (('Timestamp', 'datetime'), 'Label', 'Latitude', 'Longitude', 'Accuracy',
                    'Altitude', 'Speed', 'Pace', 'Session ID', 'Source File')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_routes(files_found, report_folder, seeker, wrap_text):
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
def get_fitbit_heart(files_found, report_folder, seeker, wrap_text):
    src = _find(files_found, 'heart_rate_db')
    rows = _run(src, 'SELECT DATE_TIME, AVERAGE_HEART_RATE, RESTING_HEART_RATE FROM HEART_RATE_DAILY_SUMMARY')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], src) for r in rows]
    data_headers = (('Timestamp', 'datetime'), 'Avg Heart Rate', 'Resting Heart Rate', 'Source File')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_sleep_detail(files_found, report_folder, seeker, wrap_text):
    src = _find(files_found, 'sleep')
    rows = _run(src, 'SELECT DATE_TIME, SECONDS, LEVEL_STRING, LOG_ID FROM SLEEP_LEVEL_DATA')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], src) for r in rows]
    data_headers = (('Timestamp', 'datetime'), 'Seconds', 'Level', 'Log ID', 'Source File')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_sleep_summary(files_found, report_folder, seeker, wrap_text):
    src = _find(files_found, 'sleep')
    rows = _run(src, '''SELECT DATE_OF_SLEEP, START_TIME, SYNC_STATUS_STRING, DURATION, DURATION/60000,
        MINUTES_AFTER_WAKEUP, MINUTES_ASLEEP, MINUTES_AWAKE, MINUTES_TO_FALL_ASLEEP, LOG_ID FROM SLEEP_LOG''')
    data_list = [(_ms_to_utc(r[0]), _ms_to_utc(r[1]), r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], src)
                 for r in rows]
    data_headers = (('Timestamp', 'datetime'), ('Start Time', 'datetime'), 'Sync Status',
                    'Duration (ms)', 'Duration (min)', 'Minutes After Wakeup', 'Minutes Asleep',
                    'Minutes Awake', 'Minutes to Fall Asleep', 'Log ID', 'Source File')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_friends(files_found, report_folder, seeker, wrap_text):
    src = _find(files_found, 'social_db')
    rows = _run(src, 'SELECT OWNING_USER_ID, ENCODED_ID, DISPLAY_NAME, AVATAR_URL, FRIEND, CHILD FROM FRIEND')
    data_list = [(r[0], r[1], r[2], r[3], r[4], r[5], src) for r in rows]
    data_headers = ('Owning User ID', 'Encoded ID', 'Display Name', 'Avatar URL', 'Friend', 'Child',
                    'Source File')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_user(files_found, report_folder, seeker, wrap_text):
    src = _find(files_found, 'social_db')
    rows = _run(src, '''SELECT LAST_UPDATED, DISPLAY_NAME, FULL_NAME, ABOUT_ME, AVATAR_URL,
        COVER_PHOTO_URL, CITY, STATE, COUNTRY, JOINED_DATE, DATE_OF_BIRTH, HEIGHT, WEIGHT, GENDER, COACH
        FROM USER_PROFILE''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], _ms_to_utc(r[9]),
                  _ms_to_utc(r[10]), r[11], r[12], r[13], r[14], src) for r in rows]
    data_headers = (('Last Updated', 'datetime'), 'Display Name', 'Full Name', 'About Me', 'Avatar URL',
                    'Cover Photo URL', 'City', 'State', 'Country', ('Joined Date', 'datetime'),
                    ('Date of Birth', 'datetime'), 'Height', 'Weight', 'Gender', 'Coach', 'Source File')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_steps(files_found, report_folder, seeker, wrap_text):
    src = _find(files_found, 'mobile_track_db')
    rows = _run(src, '''SELECT TIMESTAMP, STEPS_COUNT, METS_COUNT, TIME_CREATED, TIME_UPDATED
        FROM PEDOMETER_MINUTE_DATA''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], _ms_to_utc(r[3]), _ms_to_utc(r[4]), src) for r in rows]
    data_headers = (('Timestamp', 'datetime'), 'Steps Count', 'Mets Count', ('Time Created', 'datetime'),
                    ('Time Updated', 'datetime'), 'Source File')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_wearos_profile(files_found, report_folder, seeker, wrap_text):
    src = _find(files_found, 'user.db')
    rows = _run(src, '''SELECT fullName, displayName, email, gender, dateOfBirth, height, weight,
        memberSince, userId FROM FitbitProfileEntity''')
    data_list = [tuple(r) for r in rows]
    data_headers = ('Full Name', 'Display Name', 'Email', 'Gender', 'DOB', 'Height', 'Weight',
                    'Member Since', 'User ID')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_wearos_activity(files_found, report_folder, seeker, wrap_text):
    src = _find(files_found, 'user.db')
    rows = _run(src, '''SELECT startTime, name, duration/1000/60, distance, distanceUnit, steps,
        calories, averageHeartRate, elevationGain, activeZoneMinutes, logId FROM ActivityExerciseEntity
        ORDER BY startTime DESC''')
    data_list = [(_ms_to_utc(r[0]),) + tuple(r[1:]) for r in rows]
    data_headers = (('Start Time', 'datetime'), 'Activity Name', 'Duration (min)', 'Distance', 'Unit',
                    'Steps', 'Calories', 'Avg HR', 'Elevation', 'AZM', 'Log ID')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_wearos_daily(files_found, report_folder, seeker, wrap_text):
    src = _find(files_found, 'user.db')
    rows = _run(src, '''SELECT date, totalMinutesMoving, totalMinutesSedentary, longestDuration,
        longestStart FROM SedentaryDataEntity ORDER BY date DESC''')
    data_list = [tuple(r) for r in rows]
    data_headers = ('Date', 'Total Moving Mins', 'Total Sedentary Mins',
                    'Longest Sedentary Duration (min)', 'Longest Sedentary Start Time')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_wearos_hourly(files_found, report_folder, seeker, wrap_text):
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
def get_fitbit_wearos_sleep_logs(files_found, report_folder, seeker, wrap_text):
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
def get_fitbit_wearos_workouts(files_found, report_folder, seeker, wrap_text):
    src = _find(files_found, 'passive_stats.db')
    rows = _run(src, '''SELECT time, sessionId, exerciseTypeId, totalDistanceMm/1000000.0, steps,
        caloriesBurned, avgHeartRate, elevationGainFt FROM ExerciseSummaryEntity ORDER BY time DESC''')
    data_list = [(_ms_to_utc(r[0]),) + tuple(r[1:]) for r in rows]
    data_headers = (('Start Time', 'datetime'), 'Session ID', 'Activity Type ID', 'Distance (km)',
                    'Steps', 'Calories', 'Avg HR', 'Elevation (ft)')
    return data_headers, data_list, src


def _wearos_gps_rows(src):
    return _run(src, '''SELECT time, latitude, longitude, altitude, speed, bearing,
        estimatedPositionError FROM ExerciseGpsEntity ORDER BY time ASC''')


@artifact_processor
def get_fitbit_wearos_gps(files_found, report_folder, seeker, wrap_text):
    src = _find(files_found, 'passive_stats.db')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[6]) for r in _wearos_gps_rows(src)]
    data_headers = (('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Altitude', 'Speed',
                    'Est. Error')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_wearos_gps_route(files_found, report_folder, seeker, wrap_text):
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
def get_fitbit_wearos_hr(files_found, report_folder, seeker, wrap_text):
    src = _find(files_found, 'passive_stats.db')
    rows = _run(src, 'SELECT startTime, endTime, value, accuracy FROM HeartRateStatEntity ORDER BY startTime DESC')
    data_list = [(_ms_to_utc(r[0]), _ms_to_utc(r[1]), r[2], r[3]) for r in rows]
    data_headers = (('Start Time', 'datetime'), ('End Time', 'datetime'), 'BPM', 'Accuracy')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_wearos_pace(files_found, report_folder, seeker, wrap_text):
    src = _find(files_found, 'passive_stats.db')
    rows = _run(src, 'SELECT timeSeconds, sessionId, statType, value FROM LivePaceEntity ORDER BY timeSeconds DESC')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3]) for r in rows]
    data_headers = (('Timestamp', 'datetime'), 'Session ID', 'Stat Type', 'Value')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_wearos_sleep(files_found, report_folder, seeker, wrap_text):
    src = _find(files_found, 'passive_stats.db')
    rows = _run(src, '''SELECT sleepStartTime, sleepEndTime, (sleepEndTime-sleepStartTime)/1000/60
        FROM LocalSleepPeriodsEntity ORDER BY sleepStartTime DESC''')
    data_list = [(_ms_to_utc(r[0]), _ms_to_utc(r[1]), r[2]) for r in rows]
    data_headers = (('Sleep Start', 'datetime'), ('Sleep End', 'datetime'), 'Duration (min)')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_wearos_azm(files_found, report_folder, seeker, wrap_text):
    src = _find(files_found, 'passive_stats.db')
    rows = _run(src, 'SELECT startTime, endTime, activeZone, value, lastBpm FROM PassiveAzmEntity ORDER BY startTime DESC')
    data_list = [(_ms_to_utc(r[0]), _ms_to_utc(r[1]), r[2], r[3], r[4]) for r in rows]
    data_headers = (('Start Time', 'datetime'), ('End Time', 'datetime'), 'Zone ID', 'Points', 'Last BPM')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_wearos_splits(files_found, report_folder, seeker, wrap_text):
    src = _find(files_found, 'passive_stats.db')
    rows = _run(src, '''SELECT time, sessionId, avgPaceMilliSecPerKm/1000/60.0, avgHeartRate, steps,
        caloriesBurned FROM ExerciseSplitAnnotationEntity ORDER BY time ASC''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5]) for r in rows]
    data_headers = (('Split Time', 'datetime'), 'Session ID', 'Avg Pace (Min/Km)', 'Avg HR', 'Steps',
                    'Calories')
    return data_headers, data_list, src


@artifact_processor
def get_fitbit_wearos_opaque_hr(files_found, report_folder, seeker, wrap_text):
    src = _find(files_found, 'passive_stats.db')
    rows = _run(src, 'SELECT timestamp, baseHeartRate, confidence FROM OpaqueHeartRateEntity ORDER BY timestamp DESC')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2]) for r in rows]
    data_headers = (('Timestamp', 'datetime'), 'Base HR', 'Confidence')
    return data_headers, data_list, src

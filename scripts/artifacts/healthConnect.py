__artifacts_v2__ = {
    "healthconnect_apps": {
        "name": "Health Connect - Apps",
        "description": (
            "Apps registered with the Android Health Connect store, read from the "
            "application_info_table of healthconnect.db."
        ),
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Health Connect",
        "notes": (
            "Health Connect is the Android framework store that apps write health and fitness "
            "records to and read them from; its SQLite database is healthconnect.db in "
            "system_ce/<user>/healthconnect. Package, App Name and the stored App Icon come "
            "from application_info_table. Record Types Used is the comma separated list of "
            "numeric record type ids the table holds; each id is shown with the name the "
            "AOSP RecordTypeIdentifier class gives it, and an id that class does not name is "
            "shown as stored. The column is empty for an app that has not written a record. "
            "Android User is the number in the system_ce path. A row here shows that the "
            "platform kept an entry for the package; it does not show that the app wrote or "
            "read any record, which the record artifacts and the access log artifacts show. "
            "Verified on Android 16 full file system extractions of two Samsung phones (Health "
            "Connect database schema versions 20 and 23), on which the table held two "
            "platform packages and no fitness app, and on two further Samsung phones (schema "
            "version 26), on which it held those two and a third row whose package name starts "
            "com.android.healthconnect.phone, again with no fitness app. Android 14 and 15 are "
            "not verified."
            " On the four extractions tested Record Types Used was empty on every row, because no listed app had written a record, and Android User held one value (0) on every row."
        ),
        "paths": ('*/system_ce/*/healthconnect/healthconnect.db*',),
        "output_types": "standard",
        "artifact_icon": "heart",
        "sample_data": {
            "samsung_ffs_a16_set1": "Android 16 | Health Connect schema version 23 | 2 rows",
            "samsung_ffs_a16_set2": "Android 16 | Health Connect schema version 20 | 2 rows",
            "samsung_ffs_a16_set3": "Android 16 | Health Connect schema version 26 | 3 rows",
            "samsung_ffs_a16_set4": "Android 16 | Health Connect schema version 26 | 3 rows",
        },
    },
    "healthconnect_preferences": {
        "name": "Health Connect - Preferences",
        "description": (
            "Key and value pairs of the preference_table of healthconnect.db."
        ),
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Health Connect",
        "notes": (
            "Keys and values are reported as stored; the meaning of a key is not established "
            "here, and a key the store does not contain is not evidence about the setting it "
            "would hold. On the two Android 16 extractions tested first the table held seven keys "
            "(for example inactive_apps_added, migration_state, onboarding_state_0), one of "
            "them a UTC time written as text (current_state_start_time), which is shown as "
            "stored; on two further extractions (schema version 26) it held those seven and "
            "two more, app_icons_resize_completed_key and synthetic_package_name_salt. Android "
            "User is the number in the system_ce path."
            " On the four extractions tested Android User held one value (0) on every row."
        ),
        "paths": ('*/system_ce/*/healthconnect/healthconnect.db*',),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
            "samsung_ffs_a16_set1": "Android 16 | Health Connect schema version 23 | 7 rows",
            "samsung_ffs_a16_set2": "Android 16 | Health Connect schema version 20 | 7 rows",
            "samsung_ffs_a16_set3": "Android 16 | Health Connect schema version 26 | 9 rows",
            "samsung_ffs_a16_set4": "Android 16 | Health Connect schema version 26 | 9 rows",
        },
    },
    "healthconnect_first_grants": {
        "name": "Health Connect - Permission First Grant Times",
        "description": (
            "Per package times from health-permissions-first-grant-times.xml, which sits "
            "beside healthconnect.db."
        ),
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Health Connect",
        "notes": (
            "Each package or shared-user element carries a name and a first-grant-time written as "
            "an ISO 8601 UTC string, which is shown as stored and also converted to a time; Entry "
            "Type says which element the row came from, and the Package column holds the name "
            "attribute of either. The file is read as plain XML or as Android binary XML, "
            "whichever it is. On the two Android 16 extractions with store versions 20 and 23 the "
            "file held one package element; on two others (store version 26) it held one "
            "shared-user element and no package element, and what a shared-user name identifies is "
            "not established here. What the file records beyond its name is not established "
            "here: it is not evidence that the package wrote or read any health record. Android "
            "User is the number in the system_ce path. Entry Type held one value on the rows of "
            "each tested extraction."
        ),
        "paths": ('*/system_ce/*/healthconnect/health-permissions-first-grant-times.xml',),
        "output_types": "standard",
        "artifact_icon": "key",
        "sample_data": {
            "samsung_ffs_a16_set1": "Android 16 | Health Connect schema version 23 | 1 row",
            "samsung_ffs_a16_set2": "Android 16 | Health Connect schema version 20 | 2 rows",
            "samsung_ffs_a16_set3": "Android 16 | Health Connect schema version 26 | 2 rows",
            "samsung_ffs_a16_set4": "Android 16 | Health Connect schema version 26 | 1 row",
        },
    },
    "healthconnect_activity": {
        "name": "Health Connect - Activity Records",
        "description": (
            "Interval records of the Health Connect store that carry one quantity over a "
            "start and end time: steps, distance, active and total energy, floors climbed, "
            "elevation gained, hydration and wheelchair pushes."
        ),
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Health Connect",
        "notes": (
            "One row per record from steps_record_table, distance_record_table, "
            "active_calories_burned_record_table, total_calories_burned_record_table, "
            "floors_climbed_record_table, elevation_gained_record_table, "
            "hydration_record_table and wheelchair_pushes_record_table. Start and End are "
            "epoch milliseconds shown as UTC; the zone offsets are the seconds the writing "
            "app supplied and are shown as +HH:MM. Units follow the AOSP internal record "
            "classes: distance and elevation in metres, energy in calories (the unit of the "
            "AOSP Energy class, not kilocalories), hydration in litres; floors, steps and "
            "wheelchair pushes are counts. Package and App Name come from the record's "
            "app_info_id, Device Manufacturer, Model and Type from its device_info_id, and "
            "Recording Method is the number the record stores, shown with the "
            "Metadata.RECORDING_METHOD_* name. Last Modified is the time the store recorded "
            "for the row. Client Record ID is the identifier the writing app chose. Record "
            "UUID is the 16 byte uuid as hex. The values are what the writing app supplied; "
            "the store does not establish who or what produced them, so a manual entry or an "
            "app that imports from another source is a possibility the examiner has to rule "
            "out with Recording Method, the app and the device columns. Calories burned and "
            "distance totals may overlap between apps. Evidence tier: source-verified. The "
            "table and column names were checked against the database schema of two Android "
            "16 extractions and the units against the AOSP HealthFitness module (commit "
            "45168a88ae2a7e1abafe1cc81001d97ff00194e2), and the output was exercised on a "
            "synthetic database of the same schema; no tested extraction held a record in "
            "any of these tables, so the values on real data are unverified. Reproductive "
            "health, medical record and other record tables are not read."
        ),
        "paths": ('*/system_ce/*/healthconnect/healthconnect.db*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "samsung_ffs_a16_set1": "Android 16 | Health Connect schema version 23 | 0 rows",
            "samsung_ffs_a16_set2": "Android 16 | Health Connect schema version 20 | 0 rows",
            "samsung_ffs_a16_set3": "Android 16 | Health Connect schema version 26 | 0 rows",
            "samsung_ffs_a16_set4": "Android 16 | Health Connect schema version 26 | 0 rows",
        },
    },
    "healthconnect_measurements": {
        "name": "Health Connect - Measurements",
        "description": (
            "Single point in time records of the Health Connect store: weight, height, "
            "body composition, resting heart rate, oxygen saturation, respiratory rate, "
            "heart rate variability, VO2 max, blood pressure, blood glucose, body "
            "temperature and basal metabolic rate."
        ),
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Health Connect",
        "notes": (
            "One row per record from the instant record tables: weight, height, body_fat, "
            "lean_body_mass, bone_mass, body_water_mass, resting_heart_rate, "
            "oxygen_saturation, respiratory_rate, heart_rate_variability_rmssd, vo2_max, "
            "blood_pressure, blood_glucose, body_temperature, basal_body_temperature and "
            "basal_metabolic_rate. Units follow the AOSP internal record classes: weight and "
            "body masses in grams, height in metres, percentages as a percent number, blood "
            "pressure in mmHg, blood glucose in mmol/L, temperature in degrees Celsius, "
            "basal metabolic rate in watts, heart rate variability in milliseconds, "
            "resting heart rate in beats per minute, VO2 max in mL/min/kg and respiratory "
            "rate in breaths per minute. Detail holds the enumerated fields of a record "
            "(measurement location, body position, meal relation, measurement method) as "
            "stored numbers; their names are not decoded here. Time is epoch milliseconds "
            "shown as UTC with the zone offset the writing app supplied. The other columns "
            "work as in the Activity Records artifact, and so does its caution about the "
            "origin of a value. Evidence tier: source-verified, with no record present in "
            "any tested extraction, so the values on real data are unverified. Reproductive "
            "health records are not read."
        ),
        "paths": ('*/system_ce/*/healthconnect/healthconnect.db*',),
        "output_types": "standard",
        "artifact_icon": "heart",
        "sample_data": {
            "samsung_ffs_a16_set1": "Android 16 | Health Connect schema version 23 | 0 rows",
            "samsung_ffs_a16_set2": "Android 16 | Health Connect schema version 20 | 0 rows",
            "samsung_ffs_a16_set3": "Android 16 | Health Connect schema version 26 | 0 rows",
            "samsung_ffs_a16_set4": "Android 16 | Health Connect schema version 26 | 0 rows",
        },
    },
    "healthconnect_heart_rate": {
        "name": "Health Connect - Heart Rate Samples",
        "description": (
            "Heart rate samples of the Health Connect store, each with the record that "
            "holds it."
        ),
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Health Connect",
        "notes": (
            "heart_rate_record_series_table holds one row per sample (beats_per_minute and "
            "epoch_millis) and its parent_key names the row of heart_rate_record_table, which "
            "carries the record's start and end time, app, device and recording method. "
            "Sample Time is epoch milliseconds shown as UTC. The other columns work as in the "
            "Activity Records artifact. Evidence tier: source-verified; the tested "
            "extractions held no heart rate record, so values on real data are unverified. "
            "Resting heart rate records are in the Measurements artifact."
        ),
        "paths": ('*/system_ce/*/healthconnect/healthconnect.db*',),
        "output_types": "standard",
        "artifact_icon": "heart",
        "sample_data": {
            "samsung_ffs_a16_set1": "Android 16 | Health Connect schema version 23 | 0 rows",
            "samsung_ffs_a16_set2": "Android 16 | Health Connect schema version 20 | 0 rows",
            "samsung_ffs_a16_set3": "Android 16 | Health Connect schema version 26 | 0 rows",
            "samsung_ffs_a16_set4": "Android 16 | Health Connect schema version 26 | 0 rows",
        },
    },
    "healthconnect_sleep": {
        "name": "Health Connect - Sleep Sessions",
        "description": "Sleep session records of the Health Connect store.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Health Connect",
        "notes": (
            "One row per row of sleep_session_record_table, with the title and notes the "
            "writing app supplied and the number of rows sleep_stages_table holds for the "
            "session (Stage Count). Start and End are epoch milliseconds shown as UTC with the "
            "zone offsets the writing app supplied. The other columns work as in the Activity "
            "Records artifact. A session is what the writing app reported; it does not "
            "establish that the person slept. Evidence tier: source-verified; the tested "
            "extractions held no sleep record, so values on real data are unverified."
        ),
        "paths": ('*/system_ce/*/healthconnect/healthconnect.db*',),
        "output_types": "standard",
        "artifact_icon": "moon",
        "sample_data": {
            "samsung_ffs_a16_set1": "Android 16 | Health Connect schema version 23 | 0 rows",
            "samsung_ffs_a16_set2": "Android 16 | Health Connect schema version 20 | 0 rows",
            "samsung_ffs_a16_set3": "Android 16 | Health Connect schema version 26 | 0 rows",
            "samsung_ffs_a16_set4": "Android 16 | Health Connect schema version 26 | 0 rows",
        },
    },
    "healthconnect_sleep_stages": {
        "name": "Health Connect - Sleep Stages",
        "description": "Stage rows of sleep_stages_table with the session they belong to.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Health Connect",
        "notes": (
            "Stage Type is the number stored, shown with the SleepSessionRecord.StageType "
            "name of the AOSP framework (0 unknown, 1 awake, 2 sleeping, 3 awake out of bed, "
            "4 light, 5 deep, 6 REM, 7 awake in bed); a number that class does not name is "
            "shown as stored. Stage times are epoch milliseconds shown as UTC. Session Start, "
            "Session End and the app columns come from the parent session row. Evidence tier: "
            "source-verified; no tested extraction held a stage row."
        ),
        "paths": ('*/system_ce/*/healthconnect/healthconnect.db*',),
        "output_types": "standard",
        "artifact_icon": "moon",
        "sample_data": {
            "samsung_ffs_a16_set1": "Android 16 | Health Connect schema version 23 | 0 rows",
            "samsung_ffs_a16_set2": "Android 16 | Health Connect schema version 20 | 0 rows",
            "samsung_ffs_a16_set3": "Android 16 | Health Connect schema version 26 | 0 rows",
            "samsung_ffs_a16_set4": "Android 16 | Health Connect schema version 26 | 0 rows",
        },
    },
    "healthconnect_exercise": {
        "name": "Health Connect - Exercise Sessions",
        "description": "Exercise session records of the Health Connect store.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Health Connect",
        "notes": (
            "One row per row of exercise_session_record_table. Exercise Type is the number "
            "stored, shown with the name of the AOSP ExerciseSessionType class; a number that "
            "class does not name is shown as stored. Title and Notes are the text the writing "
            "app supplied. Has Route is the stored flag; Route Points, Lap Count and Segment "
            "Count are the number of rows the exercise_route_table, exercise_laps_table and "
            "exercise_segments_table hold for the session, and the route points themselves are "
            "in the Exercise Route artifact. Rate of Perceived Exertion is the stored "
            "session_rate_of_perceived_exertion where the column exists. The other columns "
            "work as in the Activity Records artifact. Evidence tier: source-verified; the "
            "tested extractions held no exercise record, so values on real data are "
            "unverified."
        ),
        "paths": ('*/system_ce/*/healthconnect/healthconnect.db*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "samsung_ffs_a16_set1": "Android 16 | Health Connect schema version 23 | 0 rows",
            "samsung_ffs_a16_set2": "Android 16 | Health Connect schema version 20 | 0 rows",
            "samsung_ffs_a16_set3": "Android 16 | Health Connect schema version 26 | 0 rows",
            "samsung_ffs_a16_set4": "Android 16 | Health Connect schema version 26 | 0 rows",
        },
    },
    "healthconnect_exercise_route": {
        "name": "Health Connect - Exercise Route",
        "description": (
            "Location points of exercise sessions, from exercise_route_table of the Health "
            "Connect store."
        ),
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Health Connect",
        "notes": (
            "One row per point: time (epoch milliseconds shown as UTC), latitude, longitude, "
            "altitude and the horizontal and vertical accuracy values the writing app "
            "supplied, with the parent session's type, start and end. The units of altitude "
            "and accuracy are not read from the database; the AOSP Location class they are "
            "copied from uses metres. A point is a position the writing app reported for the "
            "session; it does not by itself show where the device was. Evidence tier: "
            "source-verified; no tested extraction held a route point, so values on real data "
            "are unverified."
        ),
        "paths": ('*/system_ce/*/healthconnect/healthconnect.db*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "samsung_ffs_a16_set1": "Android 16 | Health Connect schema version 23 | 0 rows",
            "samsung_ffs_a16_set2": "Android 16 | Health Connect schema version 20 | 0 rows",
            "samsung_ffs_a16_set3": "Android 16 | Health Connect schema version 26 | 0 rows",
            "samsung_ffs_a16_set4": "Android 16 | Health Connect schema version 26 | 0 rows",
        },
    },
    "healthconnect_access_logs": {
        "name": "Health Connect - Access Logs",
        "description": (
            "access_logs_table of the Health Connect store: which app read, wrote or deleted "
            "which record types, and when."
        ),
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Health Connect",
        "notes": (
            "Access Time is epoch milliseconds shown as UTC. Operation is the stored "
            "operation_type shown with the name used by the AOSP Constants class (0 upsert, "
            "1 delete, 2 read). Record Types is the comma separated list of numeric record "
            "type ids stored, each shown with the name of the AOSP RecordTypeIdentifier "
            "class. Medical Resource Type and Medical Data Source Accessed are shown as "
            "stored where the columns exist. The app is the row of application_info_table "
            "that app_id points to. A log row records an access the platform logged; the "
            "log's retention period is not established here, so the absence of a row is not "
            "evidence that no access took place. Evidence tier: source-verified; the tested "
            "extractions held no access log row."
        ),
        "paths": ('*/system_ce/*/healthconnect/healthconnect.db*',),
        "output_types": "standard",
        "artifact_icon": "list",
        "sample_data": {
            "samsung_ffs_a16_set1": "Android 16 | Health Connect schema version 23 | 0 rows",
            "samsung_ffs_a16_set2": "Android 16 | Health Connect schema version 20 | 0 rows",
            "samsung_ffs_a16_set3": "Android 16 | Health Connect schema version 26 | 0 rows",
            "samsung_ffs_a16_set4": "Android 16 | Health Connect schema version 26 | 0 rows",
        },
    },
    "healthconnect_read_access_logs": {
        "name": "Health Connect - Read Access Logs",
        "description": (
            "read_access_logs_table of the Health Connect store: which app read data that "
            "which other app wrote."
        ),
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Health Connect",
        "notes": (
            "Reader and Writer are the packages that reader_app_id and writer_app_id point to "
            "in application_info_table. Record Type is the stored numeric id shown with the "
            "AOSP RecordTypeIdentifier name. Read Time and Write Time are epoch milliseconds "
            "shown as UTC; what Write Time denotes beyond its column name is not established "
            "here. The table is absent from older schema versions, where the artifact reports "
            "nothing. Evidence tier: source-verified; no tested extraction held a row."
        ),
        "paths": ('*/system_ce/*/healthconnect/healthconnect.db*',),
        "output_types": "standard",
        "artifact_icon": "list",
        "sample_data": {
            "samsung_ffs_a16_set1": "Android 16 | Health Connect schema version 23 | 0 rows",
            "samsung_ffs_a16_set2": "Android 16 | Health Connect schema version 20 | 0 rows",
            "samsung_ffs_a16_set3": "Android 16 | Health Connect schema version 26 | 0 rows",
            "samsung_ffs_a16_set4": "Android 16 | Health Connect schema version 26 | 0 rows",
        },
    },
    "healthconnect_change_logs": {
        "name": "Health Connect - Change Logs",
        "description": (
            "change_logs_table of the Health Connect store: upserts and deletes the store "
            "logged per app and record type."
        ),
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Health Connect",
        "notes": (
            "Record Type is the stored numeric id shown with the AOSP RecordTypeIdentifier "
            "name; Operation is shown with the name used by the AOSP Constants class (0 "
            "upsert, 1 delete). UUID Count is the number of 16 byte UUIDs the uuids blob holds "
            "and UUIDs lists them as hex. Time is epoch milliseconds shown as UTC. Medical "
            "Resource Type and Medical Data Source ID are shown as stored where the columns "
            "exist. The store trims this table, so the absence of a row is not evidence that "
            "no change took place. Evidence tier: source-verified; the tested extractions held "
            "no change log row."
        ),
        "paths": ('*/system_ce/*/healthconnect/healthconnect.db*',),
        "output_types": "standard",
        "artifact_icon": "list",
        "sample_data": {
            "samsung_ffs_a16_set1": "Android 16 | Health Connect schema version 23 | 0 rows",
            "samsung_ffs_a16_set2": "Android 16 | Health Connect schema version 20 | 0 rows",
            "samsung_ffs_a16_set3": "Android 16 | Health Connect schema version 26 | 0 rows",
            "samsung_ffs_a16_set4": "Android 16 | Health Connect schema version 26 | 0 rows",
        },
    },
}

import datetime
import os
import re
import sqlite3
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import (
    abxread,
    artifact_processor,
    check_in_embedded_media,
    checkabx,
    get_sqlite_db_records,
    logfunc,
    open_sqlite_db_readonly,
)

# Names below are the public constants of the AOSP HealthFitness module (commit
# 45168a88ae2a7e1abafe1cc81001d97ff00194e2): RecordTypeIdentifier, ExerciseSessionType,
# SleepSessionRecord.StageType, Metadata.RECORDING_METHOD_*, Device.DEVICE_TYPE_*,
# Constants (UPSERT, DELETE, READ). A number not listed is shown as stored.
RECORD_TYPES = {
    1: 'Steps', 2: 'Active calories burned', 3: 'Hydration', 4: 'Elevation gained',
    5: 'Floors climbed', 6: 'Wheelchair pushes', 7: 'Distance', 8: 'Nutrition',
    9: 'Total calories burned', 10: 'Menstruation period', 11: 'Heart rate',
    12: 'Cycling pedaling cadence', 13: 'Power', 14: 'Speed', 15: 'Steps cadence',
    16: 'Basal metabolic rate', 17: 'Body fat', 18: 'VO2 max', 19: 'Cervical mucus',
    20: 'Basal body temperature', 21: 'Menstruation flow', 22: 'Oxygen saturation',
    23: 'Blood pressure', 24: 'Height', 25: 'Blood glucose', 26: 'Weight',
    27: 'Lean body mass', 28: 'Sexual activity', 29: 'Body temperature', 30: 'Ovulation test',
    31: 'Respiratory rate', 32: 'Bone mass', 33: 'Resting heart rate', 34: 'Body water mass',
    35: 'Heart rate variability RMSSD', 36: 'Intermenstrual bleeding', 37: 'Exercise session',
    38: 'Sleep session', 39: 'Skin temperature', 40: 'Planned exercise session',
    41: 'Mindfulness session', 42: 'Activity intensity',
}
EXERCISE_TYPES = {
    1: 'Badminton', 2: 'Baseball', 3: 'Basketball', 4: 'Biking', 5: 'Biking stationary',
    6: 'Boot camp', 7: 'Boxing', 8: 'Calisthenics', 9: 'Cricket', 10: 'Dancing',
    11: 'Exercise class', 12: 'Fencing', 13: 'Football American', 14: 'Football Australian',
    15: 'Frisbee disc', 16: 'Golf', 17: 'Guided breathing', 18: 'Gymnastics', 19: 'Handball',
    20: 'High intensity interval training', 21: 'Hiking', 22: 'Ice hockey', 23: 'Ice skating',
    24: 'Martial arts', 25: 'Paddling', 26: 'Paragliding', 27: 'Pilates', 28: 'Racquetball',
    29: 'Rock climbing', 30: 'Roller hockey', 31: 'Rowing', 32: 'Rugby', 33: 'Running',
    34: 'Running treadmill', 35: 'Sailing', 36: 'Scuba diving', 37: 'Skating', 38: 'Skiing',
    39: 'Snowboarding', 40: 'Snowshoeing', 41: 'Soccer', 42: 'Softball', 43: 'Squash',
    44: 'Stair climbing', 45: 'Strength training', 46: 'Stretching', 47: 'Surfing',
    48: 'Swimming open water', 49: 'Swimming pool', 50: 'Table tennis', 51: 'Tennis',
    52: 'Volleyball', 53: 'Walking', 54: 'Water polo', 55: 'Weightlifting', 56: 'Wheelchair',
    57: 'Yoga', 58: 'Other workout', 59: 'Stair climbing machine', 60: 'Elliptical',
    61: 'Rowing machine', 0: 'Unknown',
}
STAGE_TYPES = {
    0: 'Unknown', 1: 'Awake', 2: 'Sleeping', 3: 'Awake out of bed', 4: 'Light', 5: 'Deep',
    6: 'REM', 7: 'Awake in bed',
}
RECORDING_METHODS = {0: 'Unknown', 1: 'Actively recorded', 2: 'Automatically recorded',
                     3: 'Manual entry'}
DEVICE_TYPES = {0: 'Unknown', 1: 'Watch', 2: 'Phone', 3: 'Scale', 4: 'Ring',
                5: 'Head mounted', 6: 'Fitness band', 7: 'Chest strap', 8: 'Smart display'}
OPERATIONS = {0: 'Upsert', 1: 'Delete', 2: 'Read'}

# (table, label, value column(s), unit). Interval records carry start and end time.
INTERVAL_TABLES = (
    ('steps_record_table', 'Steps', 'count', 'steps'),
    ('distance_record_table', 'Distance', 'distance', 'm'),
    ('active_calories_burned_record_table', 'Active calories burned', 'energy', 'cal'),
    ('total_calories_burned_record_table', 'Total calories burned', 'energy', 'cal'),
    ('floors_climbed_record_table', 'Floors climbed', 'floors', 'floors'),
    ('elevation_gained_record_table', 'Elevation gained', 'elevation', 'm'),
    ('hydration_record_table', 'Hydration', 'volume', 'L'),
    ('wheelchair_pushes_record_table', 'Wheelchair pushes', 'count', 'pushes'),
)
# (table, label, value column, unit, detail columns). Instant records carry one time.
INSTANT_TABLES = (
    ('weight_record_table', 'Weight', 'weight', 'g', ()),
    ('height_record_table', 'Height', 'height', 'm', ()),
    ('body_fat_record_table', 'Body fat', 'percentage', '%', ()),
    ('lean_body_mass_record_table', 'Lean body mass', 'mass', 'g', ()),
    ('bone_mass_record_table', 'Bone mass', 'mass', 'g', ()),
    ('body_water_mass_record_table', 'Body water mass', 'body_water_mass', 'g', ()),
    ('resting_heart_rate_record_table', 'Resting heart rate', 'beats_per_minute', 'bpm', ()),
    ('oxygen_saturation_record_table', 'Oxygen saturation', 'percentage', '%', ()),
    ('respiratory_rate_record_table', 'Respiratory rate', 'rate', 'breaths/min', ()),
    ('heart_rate_variability_rmssd_record_table', 'Heart rate variability RMSSD',
     'heart_rate_variability_millis', 'ms', ()),
    ('vo2_max_record_table', 'VO2 max', 'vo2_milliliters_per_minute_kilogram', 'mL/min/kg',
     ('measurement_method',)),
    ('blood_pressure_record_table', 'Blood pressure', 'systolic', 'mmHg',
     ('diastolic', 'measurement_location', 'body_position')),
    ('blood_glucose_record_table', 'Blood glucose', 'level', 'mmol/L',
     ('specimen_source', 'relation_to_meal', 'meal_type')),
    ('body_temperature_record_table', 'Body temperature', 'temperature', 'C',
     ('measurement_location',)),
    ('basal_body_temperature_record_table', 'Basal body temperature', 'temperature', 'C',
     ('measurement_location',)),
    ('basal_metabolic_rate_record_table', 'Basal metabolic rate', 'basal_metabolic_rate', 'W',
     ()),
)

COMMON_HEADERS = (
    'Android User', 'Record UUID', ('Last Modified', 'datetime'), 'Client Record ID',
    'Package', 'App Name', 'Recording Method', 'Device Manufacturer', 'Device Model',
    'Device Type',
)


def _name(mapping, value):
    """The stored number with its name from the AOSP class, or the number as stored."""
    if value is None or value == '':
        return ''
    try:
        key = int(value)
    except (TypeError, ValueError):
        return str(value)
    if key in mapping:
        return f'{key} ({mapping[key]})'
    return str(key)


def _names(mapping, text):
    """A comma separated list of numeric ids, each with its name."""
    if text is None or text == '':
        return ''
    return ', '.join(_name(mapping, part.strip()) for part in str(text).split(',')
                     if part.strip() != '')


def _ms(value):
    """Epoch milliseconds as an aware UTC datetime; empty or invalid is blank."""
    if value is None or value == '':
        return ''
    try:
        number = int(value)
    except (TypeError, ValueError):
        return ''
    try:
        return datetime.datetime.fromtimestamp(number / 1000, tz=datetime.timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _offset(value):
    """Zone offset in seconds as +HH:MM."""
    if value is None or value == '':
        return ''
    try:
        seconds = int(value)
    except (TypeError, ValueError):
        return ''
    sign = '-' if seconds < 0 else '+'
    seconds = abs(seconds)
    return f'{sign}{seconds // 3600:02d}:{seconds % 3600 // 60:02d}'


def _iso_utc(text):
    """An ISO 8601 string as an aware UTC datetime; blank when it does not parse."""
    try:
        moment = datetime.datetime.fromisoformat(str(text).replace('Z', '+00:00'))
    except ValueError:
        return ''
    if moment.tzinfo is None:
        return moment.replace(tzinfo=datetime.timezone.utc)
    return moment


def _hex(value):
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).hex()
    return '' if value is None else str(value)


def _uuid_list(value):
    """The 16 byte UUIDs a blob holds, as hex strings."""
    if not isinstance(value, (bytes, bytearray)):
        return []
    data = bytes(value)
    return [data[i:i + 16].hex() for i in range(0, len(data) - len(data) % 16, 16)]


def _stores(context):
    """Every healthconnect.db found, with its Android user. Sidecars are not databases."""
    stores = []
    for path in context.get_files_found():
        path = str(path)
        if os.path.basename(path) != 'healthconnect.db':
            continue
        relative = str(context.get_relative_path(path)).replace('\\', '/')
        match = re.search(r'(?:^|/)system_ce/(\d+)/healthconnect/', relative)
        user = match.group(1) if match else ''
        stores.append((path, user))
    return stores


def _schema(path):
    """{table: [columns]} for a database, read-only; {} when it cannot be read."""
    db = open_sqlite_db_readonly(path)
    if db is None:
        return {}
    schema = {}
    try:
        tables = [row[0] for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")]
        for table in tables:
            schema[table] = [row[1] for row in db.execute(f'PRAGMA table_info("{table}")')]
    except sqlite3.Error as error:
        logfunc(f'Health Connect: could not read the schema of {os.path.basename(path)}: {error}')
    finally:
        db.close()
    return schema


def _col(schema, table, column, alias='r'):
    """alias.column when the table has it, else NULL, so older schemas still read."""
    if column in schema.get(table, ()):
        return f'{alias}.{column}'
    return 'NULL'


def _joins(schema):
    """The app and device columns and joins every record query shares."""
    app = 'application_info_table' in schema
    device = 'device_info_table' in schema
    select = (
        f"{'a.package_name' if app else 'NULL'}, {'a.app_name' if app else 'NULL'}, "
        f"{'d.manufacturer' if device else 'NULL'}, {'d.model' if device else 'NULL'}, "
        f"{'d.device_type' if device else 'NULL'}"
    )
    joins = ''
    if app:
        joins += ' LEFT JOIN application_info_table a ON r.app_info_id = a.row_id'
    if device:
        joins += ' LEFT JOIN device_info_table d ON r.device_info_id = d.row_id'
    return select, joins


def _common(user, row):
    """The shared leading cells from (uuid, last_modified, client_id, package, app,
    recording method, manufacturer, model, device type)."""
    uuid, modified, client_id, package, app_name, method, maker, model, device_type = row
    return [user, _hex(uuid), _ms(modified), client_id or '', package or '', app_name or '',
            _name(RECORDING_METHODS, method), maker or '', model or '',
            _name(DEVICE_TYPES, device_type)]


def _run(path, query):
    return list(get_sqlite_db_records(path, query))


def _source(stores):
    return '\n'.join(path for path, _ in stores)


@artifact_processor
def healthconnect_apps(context):
    stores = _stores(context)
    data_list = []
    for path, user in stores:
        schema = _schema(path)
        if 'application_info_table' not in schema:
            continue
        query = (f"SELECT row_id, package_name, app_name, app_icon, "
                 f"{_col(schema, 'application_info_table', 'record_types_used', 'application_info_table')}"
                 f" FROM application_info_table ORDER BY row_id")
        for row_id, package, app_name, icon, used in _run(path, query):
            icon_ref = None
            if icon:
                icon_ref = check_in_embedded_media(path, bytes(icon),
                                                   name=f'{package or row_id}_icon')
            data_list.append((user, row_id, package or '', app_name or '', icon_ref,
                              _names(RECORD_TYPES, used)))
    headers = ('Android User', 'Row ID', 'Package', 'App Name', ('App Icon', 'media'),
               'Record Types Used')
    return headers, data_list, _source(stores)


@artifact_processor
def healthconnect_preferences(context):
    stores = _stores(context)
    data_list = []
    for path, user in stores:
        if 'preference_table' not in _schema(path):
            continue
        for key, value in _run(path, 'SELECT key, value FROM preference_table ORDER BY key'):
            data_list.append((user, key, value))
    return ('Android User', 'Key', 'Value'), data_list, _source(stores)


@artifact_processor
def healthconnect_first_grants(context):
    data_list = []
    paths = []
    for path in context.get_files_found():
        path = str(path)
        if os.path.basename(path) != 'health-permissions-first-grant-times.xml':
            continue
        paths.append(path)
        relative = str(context.get_relative_path(path)).replace('\\', '/')
        match = re.search(r'(?:^|/)system_ce/(\d+)/healthconnect/', relative)
        user = match.group(1) if match else ''
        try:
            if checkabx(path):
                root = abxread(path, False).getroot()
            else:
                root = ET.parse(path).getroot()
        except (ET.ParseError, OSError, ValueError) as error:
            logfunc(f'Health Connect: could not read {relative}: {error}')
            continue
        for entry in root.iter():
            if entry.tag not in ('package', 'shared-user'):
                continue
            stored = entry.get('first-grant-time') or ''
            parsed = _iso_utc(stored)
            data_list.append((user, entry.get('name') or '', stored, parsed, entry.tag))
    headers = ('Android User', 'Package', 'First Grant Time (as stored)',
               ('First Grant Time', 'datetime'), 'Entry Type')
    return headers, data_list, '\n'.join(paths)


@artifact_processor
def healthconnect_activity(context):
    stores = _stores(context)
    data_list = []
    for path, user in stores:
        schema = _schema(path)
        joins_select, joins = _joins(schema)
        for table, label, value_column, unit in INTERVAL_TABLES:
            if table not in schema or value_column not in schema[table]:
                continue
            query = (
                f"SELECT {_col(schema, table, 'uuid')}, {_col(schema, table, 'last_modified_time')}, "
                f"{_col(schema, table, 'client_record_id')}, {joins_select}, "
                f"{_col(schema, table, 'recording_method')}, r.start_time, r.start_zone_offset, "
                f"r.end_time, r.end_zone_offset, r.{value_column} "
                f"FROM {table} r{joins} ORDER BY r.start_time")
            for row in _run(path, query):
                (uuid, modified, client_id, package, app_name, maker, model, device_type,
                 method, start, start_offset, end, end_offset, value) = row
                cells = _common(user, (uuid, modified, client_id, package, app_name, method,
                                       maker, model, device_type))
                data_list.append(tuple(cells[:1] + [label, _ms(start), _ms(end),
                                                    _offset(start_offset), _offset(end_offset),
                                                    value, unit] + cells[1:]))
    headers = (('Android User', 'Record Type', ('Start', 'datetime'), ('End', 'datetime'),
                'Start Zone Offset', 'End Zone Offset', 'Value', 'Unit')
               + COMMON_HEADERS[1:])
    return headers, data_list, _source(stores)


@artifact_processor
def healthconnect_measurements(context):
    stores = _stores(context)
    data_list = []
    for path, user in stores:
        schema = _schema(path)
        joins_select, joins = _joins(schema)
        for table, label, value_column, unit, details in INSTANT_TABLES:
            if table not in schema or value_column not in schema[table]:
                continue
            detail_select = ''.join(f", {_col(schema, table, column)}" for column in details)
            query = (
                f"SELECT {_col(schema, table, 'uuid')}, {_col(schema, table, 'last_modified_time')}, "
                f"{_col(schema, table, 'client_record_id')}, {joins_select}, "
                f"{_col(schema, table, 'recording_method')}, r.time, r.zone_offset, "
                f"r.{value_column}{detail_select} FROM {table} r{joins} ORDER BY r.time")
            for row in _run(path, query):
                (uuid, modified, client_id, package, app_name, maker, model, device_type,
                 method, when, offset, value) = row[:12]
                detail = '; '.join(f'{name} (as stored) {stored}'
                                   for name, stored in zip(details, row[12:])
                                   if stored not in (None, ''))
                cells = _common(user, (uuid, modified, client_id, package, app_name, method,
                                       maker, model, device_type))
                data_list.append(tuple(cells[:1] + [label, _ms(when), _offset(offset), value,
                                                    unit, detail] + cells[1:]))
    headers = (('Android User', 'Record Type', ('Time', 'datetime'), 'Zone Offset', 'Value',
                'Unit', 'Detail') + COMMON_HEADERS[1:])
    return headers, data_list, _source(stores)


@artifact_processor
def healthconnect_heart_rate(context):
    stores = _stores(context)
    data_list = []
    for path, user in stores:
        schema = _schema(path)
        table = 'heart_rate_record_table'
        series = 'heart_rate_record_series_table'
        if table not in schema or series not in schema:
            continue
        joins_select, joins = _joins(schema)
        query = (
            f"SELECT s.epoch_millis, s.beats_per_minute, r.start_time, r.end_time, "
            f"{_col(schema, table, 'uuid')}, {_col(schema, table, 'last_modified_time')}, "
            f"{_col(schema, table, 'client_record_id')}, {joins_select}, "
            f"{_col(schema, table, 'recording_method')} "
            f"FROM {series} s JOIN {table} r ON s.parent_key = r.row_id{joins} "
            f"ORDER BY s.epoch_millis")
        for row in _run(path, query):
            (sample, bpm, start, end, uuid, modified, client_id, package, app_name, maker,
             model, device_type, method) = row
            cells = _common(user, (uuid, modified, client_id, package, app_name, method, maker,
                                   model, device_type))
            data_list.append(tuple(cells[:1] + [_ms(sample), bpm, _ms(start), _ms(end)]
                                   + cells[1:]))
    headers = (('Android User', ('Sample Time', 'datetime'), 'Beats Per Minute',
                ('Record Start', 'datetime'), ('Record End', 'datetime'))
               + COMMON_HEADERS[1:])
    return headers, data_list, _source(stores)


def _session_rows(path, schema, table, extra_columns):
    """Rows of a session table with the shared app and device columns."""
    joins_select, joins = _joins(schema)
    extras = ''.join(f", {_col(schema, table, column)}" for column in extra_columns)
    query = (
        f"SELECT r.row_id, {_col(schema, table, 'uuid')}, "
        f"{_col(schema, table, 'last_modified_time')}, {_col(schema, table, 'client_record_id')}, "
        f"{joins_select}, {_col(schema, table, 'recording_method')}, r.start_time, "
        f"r.start_zone_offset, r.end_time, r.end_zone_offset{extras} "
        f"FROM {table} r{joins} ORDER BY r.start_time")
    return _run(path, query)


def _count(path, schema, table):
    """{parent row id: row count} for a child table, empty when it is absent."""
    if table not in schema or 'parent_key' not in schema[table]:
        return {}
    return {key: count for key, count in
            _run(path, f'SELECT parent_key, COUNT(*) FROM {table} GROUP BY parent_key')}


@artifact_processor
def healthconnect_sleep(context):
    stores = _stores(context)
    data_list = []
    for path, user in stores:
        schema = _schema(path)
        table = 'sleep_session_record_table'
        if table not in schema:
            continue
        stage_counts = _count(path, schema, 'sleep_stages_table')
        for row in _session_rows(path, schema, table, ('title', 'notes')):
            (row_id, uuid, modified, client_id, package, app_name, maker, model, device_type,
             method, start, start_offset, end, end_offset, title, notes) = row
            cells = _common(user, (uuid, modified, client_id, package, app_name, method, maker,
                                   model, device_type))
            data_list.append(tuple(cells[:1] + [_ms(start), _ms(end), _offset(start_offset),
                                                _offset(end_offset), title or '', notes or '',
                                                stage_counts.get(row_id, 0)]
                                   + cells[1:]))
    headers = (('Android User', ('Start', 'datetime'), ('End', 'datetime'),
                'Start Zone Offset', 'End Zone Offset', 'Title', 'Notes', 'Stage Count')
               + COMMON_HEADERS[1:])
    return headers, data_list, _source(stores)


@artifact_processor
def healthconnect_sleep_stages(context):
    stores = _stores(context)
    data_list = []
    for path, user in stores:
        schema = _schema(path)
        table = 'sleep_session_record_table'
        stages = 'sleep_stages_table'
        if table not in schema or stages not in schema:
            continue
        joins_select, joins = _joins(schema)
        query = (
            f"SELECT g.stage_start_time, g.stage_end_time, g.stage_type, r.start_time, "
            f"r.end_time, {_col(schema, table, 'uuid')}, {_col(schema, table, 'last_modified_time')}, "
            f"{_col(schema, table, 'client_record_id')}, {joins_select}, "
            f"{_col(schema, table, 'recording_method')} "
            f"FROM {stages} g JOIN {table} r ON g.parent_key = r.row_id{joins} "
            f"ORDER BY g.stage_start_time")
        for row in _run(path, query):
            (stage_start, stage_end, stage_type, start, end, uuid, modified, client_id, package,
             app_name, maker, model, device_type, method) = row
            cells = _common(user, (uuid, modified, client_id, package, app_name, method, maker,
                                   model, device_type))
            data_list.append(tuple(cells[:1] + [_ms(stage_start), _ms(stage_end),
                                                _name(STAGE_TYPES, stage_type), _ms(start),
                                                _ms(end)] + cells[1:]))
    headers = (('Android User', ('Stage Start', 'datetime'), ('Stage End', 'datetime'),
                'Stage Type', ('Session Start', 'datetime'), ('Session End', 'datetime'))
               + COMMON_HEADERS[1:])
    return headers, data_list, _source(stores)


@artifact_processor
def healthconnect_exercise(context):
    stores = _stores(context)
    data_list = []
    for path, user in stores:
        schema = _schema(path)
        table = 'exercise_session_record_table'
        if table not in schema:
            continue
        route_counts = _count(path, schema, 'exercise_route_table')
        lap_counts = _count(path, schema, 'exercise_laps_table')
        segment_counts = _count(path, schema, 'exercise_segments_table')
        extras = ('exercise_type', 'title', 'notes', 'has_route',
                  'session_rate_of_perceived_exertion')
        for row in _session_rows(path, schema, table, extras):
            (row_id, uuid, modified, client_id, package, app_name, maker, model, device_type,
             method, start, start_offset, end, end_offset, exercise_type, title, notes,
             has_route, exertion) = row
            cells = _common(user, (uuid, modified, client_id, package, app_name, method, maker,
                                   model, device_type))
            data_list.append(tuple(cells[:1] + [
                _ms(start), _ms(end), _offset(start_offset), _offset(end_offset),
                _name(EXERCISE_TYPES, exercise_type), title or '', notes or '',
                '' if has_route is None else ('Yes' if has_route else 'No'),
                route_counts.get(row_id, 0), lap_counts.get(row_id, 0),
                segment_counts.get(row_id, 0), exertion] + cells[1:]))
    headers = (('Android User', ('Start', 'datetime'), ('End', 'datetime'),
                'Start Zone Offset', 'End Zone Offset', 'Exercise Type', 'Title', 'Notes',
                'Has Route', 'Route Points', 'Lap Count', 'Segment Count',
                'Rate of Perceived Exertion') + COMMON_HEADERS[1:])
    return headers, data_list, _source(stores)


@artifact_processor
def healthconnect_exercise_route(context):
    stores = _stores(context)
    data_list = []
    for path, user in stores:
        schema = _schema(path)
        table = 'exercise_session_record_table'
        route = 'exercise_route_table'
        if table not in schema or route not in schema:
            continue
        query = (
            f"SELECT p.timestamp_millis, p.latitude, p.longitude, p.altitude, "
            f"p.horizontal_accuracy, p.vertical_accuracy, {_col(schema, table, 'exercise_type')}, "
            f"r.start_time, r.end_time, {_col(schema, table, 'uuid')} "
            f"FROM {route} p JOIN {table} r ON p.parent_key = r.row_id "
            f"ORDER BY r.row_id, p.timestamp_millis")
        for (stamp, latitude, longitude, altitude, horizontal, vertical, exercise_type, start,
             end, uuid) in _run(path, query):
            data_list.append((user, _ms(stamp), latitude, longitude, altitude, horizontal,
                              vertical, _name(EXERCISE_TYPES, exercise_type), _ms(start),
                              _ms(end), _hex(uuid)))
    headers = ('Android User', ('Time', 'datetime'), 'Latitude', 'Longitude', 'Altitude',
               'Horizontal Accuracy', 'Vertical Accuracy', 'Session Exercise Type',
               ('Session Start', 'datetime'), ('Session End', 'datetime'), 'Session UUID')
    return headers, data_list, _source(stores)


def _app_lookup(path, schema):
    """{row id: (package, app name)} from application_info_table."""
    if 'application_info_table' not in schema:
        return {}
    return {row_id: (package or '', app_name or '') for row_id, package, app_name in
            _run(path, 'SELECT row_id, package_name, app_name FROM application_info_table')}


@artifact_processor
def healthconnect_access_logs(context):
    stores = _stores(context)
    data_list = []
    for path, user in stores:
        schema = _schema(path)
        table = 'access_logs_table'
        if table not in schema:
            continue
        apps = _app_lookup(path, schema)
        query = (f"SELECT row_id, app_id, record_type, access_time, operation_type, "
                 f"{_col(schema, table, 'medical_resource_type', table)}, "
                 f"{_col(schema, table, 'medical_data_source_accessed', table)} "
                 f"FROM {table} ORDER BY access_time")
        for row_id, app_id, record_type, when, operation, medical_type, medical_source in _run(
                path, query):
            package, app_name = apps.get(app_id, ('', ''))
            data_list.append((user, _ms(when), package, app_name, _name(OPERATIONS, operation),
                              _names(RECORD_TYPES, record_type), medical_type or '',
                              '' if medical_source is None else medical_source, row_id))
    headers = ('Android User', ('Access Time', 'datetime'), 'Package', 'App Name', 'Operation',
               'Record Types', 'Medical Resource Type', 'Medical Data Source Accessed',
               'Row ID')
    return headers, data_list, _source(stores)


@artifact_processor
def healthconnect_read_access_logs(context):
    stores = _stores(context)
    data_list = []
    for path, user in stores:
        schema = _schema(path)
        if 'read_access_logs_table' not in schema:
            continue
        apps = _app_lookup(path, schema)
        query = ('SELECT row_id, reader_app_id, writer_app_id, record_type, read_time, '
                 'write_time FROM read_access_logs_table ORDER BY read_time')
        for row_id, reader, writer, record_type, read_time, write_time in _run(path, query):
            reader_package, reader_name = apps.get(reader, ('', ''))
            writer_package, writer_name = apps.get(writer, ('', ''))
            data_list.append((user, _ms(read_time), reader_package, reader_name,
                              writer_package, writer_name, _name(RECORD_TYPES, record_type),
                              _ms(write_time), row_id))
    headers = ('Android User', ('Read Time', 'datetime'), 'Reader Package', 'Reader App Name',
               'Writer Package', 'Writer App Name', 'Record Type',
               ('Write Time', 'datetime'), 'Row ID')
    return headers, data_list, _source(stores)


@artifact_processor
def healthconnect_change_logs(context):
    stores = _stores(context)
    data_list = []
    for path, user in stores:
        schema = _schema(path)
        table = 'change_logs_table'
        if table not in schema:
            continue
        apps = _app_lookup(path, schema)
        query = (f"SELECT row_id, app_id, record_type, uuids, operation_type, time, "
                 f"{_col(schema, table, 'medical_resource_type', table)}, "
                 f"{_col(schema, table, 'medical_data_source_id', table)} "
                 f"FROM {table} ORDER BY time")
        for row_id, app_id, record_type, uuids, operation, when, medical_type, medical_source in \
                _run(path, query):
            package, app_name = apps.get(app_id, ('', ''))
            listed = _uuid_list(uuids)
            data_list.append((user, _ms(when), package, app_name, _name(OPERATIONS, operation),
                              _name(RECORD_TYPES, record_type), len(listed), ', '.join(listed),
                              '' if medical_type is None else medical_type,
                              '' if medical_source is None else medical_source, row_id))
    headers = ('Android User', ('Time', 'datetime'), 'Package', 'App Name', 'Operation',
               'Record Type', 'UUID Count', 'UUIDs', 'Medical Resource Type',
               'Medical Data Source ID', 'Row ID')
    return headers, data_list, _source(stores)

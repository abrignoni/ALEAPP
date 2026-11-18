__artifacts_v2__ = {
    "samsung_health_secure_user_profile": {
        "name": "Samsung Health - User Profile (Secure)",
        "description": "User profile keys and values from the encrypted SecureHealthData.db, decrypted with the "
                       "key in the extraction's Secrets/secrets.json.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Health",
        "notes": (
            'One row per com_samsung_health_user__profile row. Value is the first of the text, float, long, '
            'int, double and blob value columns that holds a value, and Value Type names it; a blob is shown '
            'as its length and is not decoded. Times are read as Unix milliseconds; a stored time inside the '
            'first day of 1970 is shown blank. Update Time and Create Time are blank on rows that store 1 '
            'there (6 Update Time and 8 Create Time rows of 17 on samsung_a166u_a16_known_20261116; 8 of 10 '
            'on sharon_a13 and sharon_a14), so Update Time leads the table and is filled on 11 of 17 rows of '
            'samsung_a166u_a16_known_20261116 and on 2 of 10 rows of sharon_a13 and sharon_a14. On '
            'samsung_a166u_a16_known_20261116 the 17 rows held 12 text, 2 float, 1 int and 2 blob values; the '
            'name key held the nickname set in the known-data session, and height and weight held 170.0 and '
            '70.0; their Update Time is 17:09:57 UTC and the mint log records the save at 17:10:01 UTC. Birth '
            'date and country are among the keys. On sharon_a13 and sharon_a14 the table held 10 rows each, '
            'and Value Type held text on all 10 rows of sharon_a13. What each key means is taken from its '
            'name only. Not reported from SecureHealthData.db: device_profile, height, weight, food_info, '
            'food_frequent, activity_level, activity_day_summary, badge, calories_burned, training program '
            'and schedule, preferences, service_preferences, social_service_status, step_daily_trend, the '
            'floors and pedometer day summaries, datasource and the empty tables (heart rate, sleep stage, '
            'blood pressure, blood glucose, oxygen saturation, water and food intake, stress, exercise route '
            'and others). SecureHealthData.db in com.sec.android.app.shealth/databases is not a plaintext '
            'SQLite file. It is read as SQLCipher with AES-256-CBC, 4096-byte pages, a 48-byte reserve and '
            "HMAC-SHA1, through scripts/sqlcipher_decrypt.py. The key comes from the extraction tool's "
            'Secrets/secrets.json, from the com.sec.android.app.shealth entry whose script_output payload is '
            "named SecureHealthData. The Samsung Health payload is a 99-character x'..' literal; its first 64 "
            'hex digits are used directly as the page key and the 32 hex digits after them are not used. '
            'These settings were found by testing, not from app source. Every page of every database opened '
            'on the images in sample_data authenticated its HMAC (samsung_a166u_a16_known_20261116: '
            'SecureHealthData.db 707 of 707 pages with its write-ahead log, inferenceengine_logging.db 79 of '
            '79, inferenceengine_monitoring.db 71 of 71), and no run logged a page that failed. A second '
            'SecureHealthData.db, in com.samsung.android.service.health/databases on sharon_a13 and '
            'sharon_a14, authenticated 0 of 317 pages with the only SecureHealthData key present and is not '
            "read. A key is taken from the entry whose user_id equals the database's Android user, then from "
            'entries with no user_id (no entry on sharon_a13 carries one; on sharon_a14 the Customization '
            'Service entry carries none), and is used only if at least one page authenticates under it; pages '
            'that fail are counted in a log line. With no such key the database is not read and a line is '
            'logged. The decrypted copy is written under the report folder (samsung_secure_decrypted) and '
            "read from there; the evidence file is only read. Android User is the user the database's path "
            'names. Android User held 0 on every row of the images in sample_data.'
        ),
        "paths": ('*/com.sec.android.app.shealth/databases/SecureHealthData.db*', '*/Secrets/secrets.json'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.sec.android.app.shealth | 17 rows",
            "sharon_a13": "Android 13 | com.sec.android.app.shealth | 10 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.shealth | 10 rows",
            "anne_a15": "Android 15 | com.sec.android.app.shealth | 0 rows, no SecureHealthData.db",
            "falken_a326u_a13": "Android 13 | com.sec.android.app.shealth | 0 rows, no SecureHealthData.db",
        },
    },
    "samsung_health_secure_step_count": {
        "name": "Samsung Health - Step Count (Secure)",
        "description": "Step count samples from the encrypted SecureHealthData.db, decrypted with the key in the "
                       "extraction's Secrets/secrets.json.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Health",
        "notes": (
            'One row per com_samsung_health_step__count row (a step sample). Times are read as Unix '
            'milliseconds; a stored time inside the first day of 1970 is shown blank. distance, calorie and '
            'speed are shown as stored and their units are not established. On '
            'samsung_a166u_a16_known_20261116 the 3 rows started at 17:39, 17:40 and 17:47 UTC, one minute '
            'each, with Count 16, 9 and 7, which add up to the 32 steps of the Daily Step Summary artifact; '
            'the short walk at about 17:02 to 17:04 UTC (mint log) has no sample. Walk Steps equal Count and '
            'Run Steps held 0 on all 3 rows, and Device UUID held one value on all 3 rows; time_offset held '
            'one value on all 3 rows, -18000000, which is 5 hours if the unit is milliseconds; the unit is '
            'not sourced. sharon_a13 and sharon_a14 had no rows. SecureHealthData.db in '
            'com.sec.android.app.shealth/databases is not a plaintext SQLite file. It is read as SQLCipher '
            'with AES-256-CBC, 4096-byte pages, a 48-byte reserve and HMAC-SHA1, through '
            "scripts/sqlcipher_decrypt.py. The key comes from the extraction tool's Secrets/secrets.json, "
            'from the com.sec.android.app.shealth entry whose script_output payload is named '
            "SecureHealthData. The Samsung Health payload is a 99-character x'..' literal; its first 64 hex "
            'digits are used directly as the page key and the 32 hex digits after them are not used. These '
            'settings were found by testing, not from app source. Every page of every database opened on the '
            'images in sample_data authenticated its HMAC (samsung_a166u_a16_known_20261116: '
            'SecureHealthData.db 707 of 707 pages with its write-ahead log, inferenceengine_logging.db 79 of '
            '79, inferenceengine_monitoring.db 71 of 71), and no run logged a page that failed. A second '
            'SecureHealthData.db, in com.samsung.android.service.health/databases on sharon_a13 and '
            'sharon_a14, authenticated 0 of 317 pages with the only SecureHealthData key present and is not '
            "read. A key is taken from the entry whose user_id equals the database's Android user, then from "
            'entries with no user_id (no entry on sharon_a13 carries one; on sharon_a14 the Customization '
            'Service entry carries none), and is used only if at least one page authenticates under it; pages '
            'that fail are counted in a log line. With no such key the database is not read and a line is '
            'logged. The decrypted copy is written under the report folder (samsung_secure_decrypted) and '
            "read from there; the evidence file is only read. Android User is the user the database's path "
            'names. Android User held 0 on every row of the images in sample_data.'
        ),
        "paths": ('*/com.sec.android.app.shealth/databases/SecureHealthData.db*', '*/Secrets/secrets.json'),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.sec.android.app.shealth | 3 rows",
            "sharon_a13": "Android 13 | com.sec.android.app.shealth | 0 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.shealth | 0 rows",
        },
    },
    "samsung_health_secure_sleep": {
        "name": "Samsung Health - Sleep (Secure)",
        "description": "Sleep records from the encrypted SecureHealthData.db, decrypted with the key in the "
                       "extraction's Secrets/secrets.json.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Health",
        "notes": (
            'One row per com_samsung_health_sleep row. Times are read as Unix milliseconds; a stored time '
            'inside the first day of 1970 is shown blank. On samsung_a166u_a16_known_20261116 the one row ran '
            'from 04:00 to 12:00 UTC, the manual entry of 11:00 PM to 7:00 AM local made in the known-data '
            'session; sleep_type (as stored) and Comment had no value on it. time_offset held -18000000 on '
            'every row on that image, which is 5 hours if the unit is milliseconds; the unit is not sourced. '
            "sharon_a13 and sharon_a14 had no rows. Of the table's 68 columns 7 are reported; the score, "
            'factor, efficiency, quality, goal and duration columns are not, and the '
            'com_samsung_health_sleep__stage table is not read. SecureHealthData.db in '
            'com.sec.android.app.shealth/databases is not a plaintext SQLite file. It is read as SQLCipher '
            'with AES-256-CBC, 4096-byte pages, a 48-byte reserve and HMAC-SHA1, through '
            "scripts/sqlcipher_decrypt.py. The key comes from the extraction tool's Secrets/secrets.json, "
            'from the com.sec.android.app.shealth entry whose script_output payload is named '
            "SecureHealthData. The Samsung Health payload is a 99-character x'..' literal; its first 64 hex "
            'digits are used directly as the page key and the 32 hex digits after them are not used. These '
            'settings were found by testing, not from app source. Every page of every database opened on the '
            'images in sample_data authenticated its HMAC (samsung_a166u_a16_known_20261116: '
            'SecureHealthData.db 707 of 707 pages with its write-ahead log, inferenceengine_logging.db 79 of '
            '79, inferenceengine_monitoring.db 71 of 71), and no run logged a page that failed. A second '
            'SecureHealthData.db, in com.samsung.android.service.health/databases on sharon_a13 and '
            'sharon_a14, authenticated 0 of 317 pages with the only SecureHealthData key present and is not '
            "read. A key is taken from the entry whose user_id equals the database's Android user, then from "
            'entries with no user_id (no entry on sharon_a13 carries one; on sharon_a14 the Customization '
            'Service entry carries none), and is used only if at least one page authenticates under it; pages '
            'that fail are counted in a log line. With no such key the database is not read and a line is '
            'logged. The decrypted copy is written under the report folder (samsung_secure_decrypted) and '
            "read from there; the evidence file is only read. Android User is the user the database's path "
            'names. Android User held 0 on every row of the images in sample_data.'
        ),
        "paths": ('*/com.sec.android.app.shealth/databases/SecureHealthData.db*', '*/Secrets/secrets.json'),
        "output_types": "standard",
        "artifact_icon": "moon",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.sec.android.app.shealth | 1 row",
            "sharon_a13": "Android 13 | com.sec.android.app.shealth | 0 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.shealth | 0 rows",
        },
    },
    "samsung_health_secure_exercise": {
        "name": "Samsung Health - Exercise (Secure)",
        "description": "Exercise records from the encrypted SecureHealthData.db, decrypted with the key in the "
                       "extraction's Secrets/secrets.json.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Health",
        "notes": (
            'One row per com_samsung_health_exercise row. Times are read as Unix milliseconds; a stored time '
            'inside the first day of 1970 is shown blank. duration is shown as stored; on the known-data row '
            '13003 matches 13 s of active time, so it reads as milliseconds there, and the unit is not '
            'sourced. distance, calorie and count are shown as stored. On samsung_a166u_a16_known_20261116 '
            'the one row started at 17:00:37 and ended at 17:01:07 UTC with duration 13003, exercise_type '
            '1001 and the workout note typed in the known-data session in Comment; the mint log records a '
            'walking workout of 13 s active, 29 s total. exercise_type held 1001 on that walking workout; no '
            'other value was seen and no value is sourced. time_offset held -18000000 on every row on that '
            'image, which is 5 hours if the unit is milliseconds; the unit is not sourced. sharon_a13 and '
            "sharon_a14 had no rows. 11 of the table's 79 columns are reported; the live data, location data "
            'and heart rate columns are not. SportTracker.db is not read; the secrets.json of '
            'samsung_a166u_a16_known_20261116 carries a SportTracker key that is not used. '
            'SecureHealthData.db in com.sec.android.app.shealth/databases is not a plaintext SQLite file. It '
            'is read as SQLCipher with AES-256-CBC, 4096-byte pages, a 48-byte reserve and HMAC-SHA1, through '
            "scripts/sqlcipher_decrypt.py. The key comes from the extraction tool's Secrets/secrets.json, "
            'from the com.sec.android.app.shealth entry whose script_output payload is named '
            "SecureHealthData. The Samsung Health payload is a 99-character x'..' literal; its first 64 hex "
            'digits are used directly as the page key and the 32 hex digits after them are not used. These '
            'settings were found by testing, not from app source. Every page of every database opened on the '
            'images in sample_data authenticated its HMAC (samsung_a166u_a16_known_20261116: '
            'SecureHealthData.db 707 of 707 pages with its write-ahead log, inferenceengine_logging.db 79 of '
            '79, inferenceengine_monitoring.db 71 of 71), and no run logged a page that failed. A second '
            'SecureHealthData.db, in com.samsung.android.service.health/databases on sharon_a13 and '
            'sharon_a14, authenticated 0 of 317 pages with the only SecureHealthData key present and is not '
            "read. A key is taken from the entry whose user_id equals the database's Android user, then from "
            'entries with no user_id (no entry on sharon_a13 carries one; on sharon_a14 the Customization '
            'Service entry carries none), and is used only if at least one page authenticates under it; pages '
            'that fail are counted in a log line. With no such key the database is not read and a line is '
            'logged. The decrypted copy is written under the report folder (samsung_secure_decrypted) and '
            "read from there; the evidence file is only read. Android User is the user the database's path "
            'names. Android User held 0 on every row of the images in sample_data.'
        ),
        "paths": ('*/com.sec.android.app.shealth/databases/SecureHealthData.db*', '*/Secrets/secrets.json'),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.sec.android.app.shealth | 1 row",
            "sharon_a13": "Android 13 | com.sec.android.app.shealth | 0 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.shealth | 0 rows",
        },
    },
    "samsung_customization_app_usage": {
        "name": "Samsung Customization Service - App Usage",
        "description": "The app_usage table of the encrypted Customization Service inferenceengine_logging.db, "
                       "decrypted with the key in the extraction's Secrets/secrets.json.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Samsung Customization Service",
        "notes": (
            "One row per app_usage row. Times are the table's millisecond values read as UTC. On sharon_a13, "
            'sharon_a14 and samsung_a166u_a16_known_20261116 they equal the text time stored beside them '
            "(time_string, or start_time_string and end_time_string in app_usage) in the row's timezone_id, "
            'on every row of the location, app usage, charging and motion tables; web_log has no timezone_id, '
            'and its time_string matches in the zone the other tables name. A stored time inside the first '
            'day of 1970 is shown blank. On sharon_a13 the 827 rows named 26 packages (2023-05-30 to '
            '2023-06-26) and on sharon_a14 the 211 rows named 23 (2024-08-02 to 2024-08-24); End Time held a '
            'value on every row. Time Zone held America/New_York on all 827 rows of sharon_a13. No known-data '
            'record for these images was used. On samsung_a166u_a16_known_20261116 the table held no rows, '
            'although three apps were opened at 17:38 UTC in the known-data session; the mint log records the '
            'service as already On at 17:36 UTC and does not record when it was turned on. A row records what '
            'the service logged, not by itself that a person used the app. Not reported from '
            'inferenceengine_logging.db: setting_change, api_call_log, profile (account '
            'fields), cpp_path_history_log, country_app_count, cmh_tag_log, keyboard_lang, '
            'general_real_time_collection_log, general_batch_collection_log, sa_raw_data, '
            'sa_personalized_log, screen_log, the Bluetooth, Wi-Fi, headset, gear, watch, notification, '
            'music, calendar and keyword tables. inferenceengine_logging.db in '
            'com.samsung.android.rubin.app/databases is not a plaintext SQLite file. It is read as SQLCipher '
            'with AES-256-CBC, 4096-byte pages, a 48-byte reserve and HMAC-SHA1, through '
            "scripts/sqlcipher_decrypt.py. The key comes from the extraction tool's Secrets/secrets.json, "
            'from the com.samsung.android.rubin.app entry whose script_output payload is named Logging. On '
            'the three exports seen the payload is 512 hex digits; their 256 bytes are the password to '
            "PBKDF2-HMAC-SHA1 with the database's first 16 bytes as salt and 4000 iterations. These settings "
            'were found by testing, not from app source. Every page of every database opened on the images in '
            'sample_data authenticated its HMAC (samsung_a166u_a16_known_20261116: SecureHealthData.db 707 of '
            '707 pages with its write-ahead log, inferenceengine_logging.db 79 of 79, '
            'inferenceengine_monitoring.db 71 of 71), and no run logged a page that failed. A key is taken '
            "from the entry whose user_id equals the database's Android user, then from entries with no "
            'user_id (no entry on sharon_a13 carries one; on sharon_a14 the Customization Service entry '
            'carries none), and is used only if at least one page authenticates under it; pages that fail are '
            'counted in a log line. With no such key the database is not read and a line is logged. The '
            'decrypted copy is written under the report folder (samsung_secure_decrypted) and read from '
            "there; the evidence file is only read. Android User is the user the database's path names. "
            'Android User held 0 on every row of the images in sample_data.'
        ),
        "paths": ('*/com.samsung.android.rubin.app/databases/inferenceengine_logging.db*', '*/Secrets/secrets.json'),
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.rubin.app | 0 rows",
            "sharon_a13": "Android 13 | com.samsung.android.rubin.app | 827 rows",
            "sharon_a14": "Android 14 | com.samsung.android.rubin.app | 211 rows",
            "anne_a15": "Android 15 | com.samsung.android.rubin.app | 0 rows, no key in secrets.json",
            "falken_a326u_a13": "Android 13 | com.samsung.android.rubin.app | 0 rows, no key in secrets.json",
        },
    },
    "samsung_customization_charging": {
        "name": "Samsung Customization Service - Charging Log",
        "description": "The charging_log table of the encrypted Customization Service inferenceengine_logging.db, "
                       "decrypted with the key in the extraction's Secrets/secrets.json.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Samsung Customization Service",
        "notes": (
            'One row per charging_log row. connected, plugged, level and place_id are shown as stored; their '
            "meanings are not sourced. Times are the table's millisecond values read as UTC. On sharon_a13, "
            'sharon_a14 and samsung_a166u_a16_known_20261116 they equal the text time stored beside them '
            "(time_string, or start_time_string and end_time_string in app_usage) in the row's timezone_id, "
            'on every row of the location, app usage, charging and motion tables; web_log has no timezone_id, '
            'and its time_string matches in the zone the other tables name. A stored time inside the first '
            'day of 1970 is shown blank. On samsung_a166u_a16_known_20261116 the 10 rows include connected 0 '
            'at 17:42:36 and connected 1 at 17:42:39 UTC, the cable unplugged and replugged at 17:42:36.3 and '
            '17:42:38.8 UTC in the mint log, and connected 0 at 17:02:54 and 1 at 17:03:51 UTC, inside the '
            'walk the mint log places at about 17:02 to 17:04; the mint log does not record a cable change '
            'then. place_id (as stored) held -1 on all 10 rows and Time Zone held America/New_York on all 10. '
            'plugged held 0, 1, 2 and 4 across the images. sharon_a13 had 30 rows and sharon_a14 24; Time '
            'Zone held America/New_York on all 30 rows of sharon_a13. Not reported from '
            'inferenceengine_logging.db: setting_change, api_call_log, profile (account '
            'fields), cpp_path_history_log, country_app_count, cmh_tag_log, keyboard_lang, '
            'general_real_time_collection_log, general_batch_collection_log, sa_raw_data, '
            'sa_personalized_log, screen_log, the Bluetooth, Wi-Fi, headset, gear, watch, notification, '
            'music, calendar and keyword tables. inferenceengine_logging.db in '
            'com.samsung.android.rubin.app/databases is not a plaintext SQLite file. It is read as SQLCipher '
            'with AES-256-CBC, 4096-byte pages, a 48-byte reserve and HMAC-SHA1, through '
            "scripts/sqlcipher_decrypt.py. The key comes from the extraction tool's Secrets/secrets.json, "
            'from the com.samsung.android.rubin.app entry whose script_output payload is named Logging. On '
            'the three exports seen the payload is 512 hex digits; their 256 bytes are the password to '
            "PBKDF2-HMAC-SHA1 with the database's first 16 bytes as salt and 4000 iterations. These settings "
            'were found by testing, not from app source. Every page of every database opened on the images in '
            'sample_data authenticated its HMAC (samsung_a166u_a16_known_20261116: SecureHealthData.db 707 of '
            '707 pages with its write-ahead log, inferenceengine_logging.db 79 of 79, '
            'inferenceengine_monitoring.db 71 of 71), and no run logged a page that failed. A key is taken '
            "from the entry whose user_id equals the database's Android user, then from entries with no "
            'user_id (no entry on sharon_a13 carries one; on sharon_a14 the Customization Service entry '
            'carries none), and is used only if at least one page authenticates under it; pages that fail are '
            'counted in a log line. With no such key the database is not read and a line is logged. The '
            'decrypted copy is written under the report folder (samsung_secure_decrypted) and read from '
            "there; the evidence file is only read. Android User is the user the database's path names. "
            'Android User held 0 on every row of the images in sample_data.'
        ),
        "paths": ('*/com.samsung.android.rubin.app/databases/inferenceengine_logging.db*', '*/Secrets/secrets.json'),
        "output_types": "standard",
        "artifact_icon": "battery-charging",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.rubin.app | 10 rows",
            "sharon_a13": "Android 13 | com.samsung.android.rubin.app | 30 rows",
            "sharon_a14": "Android 14 | com.samsung.android.rubin.app | 24 rows",
            "anne_a15": "Android 15 | com.samsung.android.rubin.app | 0 rows, no key in secrets.json",
            "falken_a326u_a13": "Android 13 | com.samsung.android.rubin.app | 0 rows, no key in secrets.json",
        },
    },
    "samsung_customization_screen_state": {
        "name": "Samsung Customization Service - Screen State Log",
        "description": "The screen_state_log table of the encrypted Customization Service inferenceengine_logging.db, "
                       "decrypted with the key in the extraction's Secrets/secrets.json: one row per stored screen "
                       "state entry with its screen_state, user_present and use_keyguard values.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Samsung Customization Service",
        "notes": (
            'One row per screen_state_log row. screen_state, user_present and '
            'use_keyguard are shown as stored; their meanings are not sourced. Time is '
            'the table\'s time column, milliseconds read as UTC; Time String (as stored) '
            'is the text time beside it, and on every row of the four images in '
            'sample_data with rows it equals Time cut to the whole second in the row\'s '
            'timezone_id (157, 106, 757 and 2,050 rows). created_at is not shown; it was '
            'within 2 seconds of time on every row of the four images. The lowest _id on '
            'those images was 22, 22, 734 and 3184, so earlier rows are no longer in the '
            'table. '
            'Known data (samsung_a166u_a16_known_20261117, lock tests timed by an adb '
            'watcher and from the phone\'s own power state): a wake of the locked screen '
            'logged at about 14:03:02 UTC has a row at 14:03:02 holding 1, 0, 1. A row at '
            '14:03:09 holding 1, 1, 0 follows it; the watcher first saw the phone '
            'unlocked at 14:03:12, and the unlock itself was not timed. The timeout '
            'screen-off was not watched live: a dumpsys power reading at 14:03:21 placed '
            'it about 31.6 s earlier (about 14:02:49). The only row between 13:50:11 and '
            '14:03:02 is at 14:01:39 and holds 0, 0, 0, about 70 seconds before that; '
            'whether that row records the timeout is not established. '
            'Two side-button screen-offs, two wakes and a PIN unlock were logged between '
            '13:47:56 and 13:50:10. No row has a time inside that span. The next row is '
            'at 13:50:11, about a second after the watcher saw the keyguard gone, and '
            'holds 1, 0, 0; the row before it is at 12:55:59. So on this image the table '
            'did not hold every screen change (the phone was on USB power with Stay awake '
            'on during that test), and a missing row does not show that the screen did '
            'not change. '
            'Value combinations seen (screen_state, user_present, use_keyguard): 1,0,0; '
            '0,0,0; 1,1,0; 1,0,1; 0,0,1 on the two A166U images and on sharon_a14; only '
            '1,0,0; 0,0,0; 1,1,0 on sharon_a13. Time Zone held America/New_York on every '
            'row except 252 rows of sharon_a14, which held America/Denver. '
            'inferenceengine_logging.db in com.samsung.android.rubin.app/databases is not '
            'a plaintext SQLite file. It is read as SQLCipher with AES-256-CBC, 4096-byte '
            'pages, a 48-byte reserve and HMAC-SHA1, through '
            'scripts/sqlcipher_decrypt.py, with the key from the extraction tool\'s '
            'Secrets/secrets.json entry for com.samsung.android.rubin.app whose '
            'script_output payload is named Logging. The payload is 512 hex digits on the '
            'four images read; their 256 bytes are the password to PBKDF2-HMAC-SHA1 with '
            'the database\'s first 16 bytes as salt and 4000 iterations. These settings '
            'were found by testing, not from app source. With no such key the database is '
            'not read and a line is logged. The decrypted copy is written under the '
            'report folder (samsung_secure_decrypted) and read from there; the evidence '
            'file is only read. Android User is the user the database\'s path names, and '
            'held 0 on every row of the images in sample_data.'
        ),
        "paths": ('*/com.samsung.android.rubin.app/databases/inferenceengine_logging.db*', '*/Secrets/secrets.json'),
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.samsung.android.rubin.app | 157 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.rubin.app | 106 rows",
            "sharon_a13": "Android 13 | com.samsung.android.rubin.app | 757 rows",
            "sharon_a14": "Android 14 | com.samsung.android.rubin.app | 2050 rows",
            "anne_a15": "Android 15 | com.samsung.android.rubin.app | 0 rows, no key in secrets.json",
            "falken_a326u_a13": "Android 13 | com.samsung.android.rubin.app | 0 rows, no key in secrets.json",
        },
    },
    "samsung_customization_location": {
        "name": "Samsung Customization Service - Location Log",
        "description": "The location_log table of the encrypted Customization Service inferenceengine_logging.db, "
                       "decrypted with the key in the extraction's Secrets/secrets.json.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Samsung Customization Service",
        "notes": (
            'One row per location_log row. Rows of the update_failed provider (488 on sharon_a13, 3 on '
            'sharon_a14) and the unknown provider (16 and 6) store 0 in both latitude and longitude, which is '
            'not a position; Latitude and Longitude are blank on those rows, and the KML output holds the '
            'other rows (1,814 of 2,318 on sharon_a13). Rows of the other eight providers held nonzero '
            'coordinates on every row. altitude, accuracy, speed and bearing are shown as stored. Provider is '
            'the stored provider name; on sharon_a13 and sharon_a14 it held fused, gps, network, '
            'passive_fused, passive_gps, passive_network, lastKnown_gps, lastKnown_network, unknown and '
            "update_failed. What update_failed denotes is not established. Times are the table's millisecond "
            'values read as UTC. On sharon_a13, sharon_a14 and samsung_a166u_a16_known_20261116 they equal '
            'the text time stored beside them (time_string, or start_time_string and end_time_string in '
            "app_usage) in the row's timezone_id, on every row of the location, app usage, charging and "
            'motion tables; web_log has no timezone_id, and its time_string matches in the zone the other '
            'tables name. A stored time inside the first day of 1970 is shown blank. sharon_a13 had 2318 rows '
            '(2023-05-30 to 2023-06-29) and sharon_a14 2033 (2024-08-02 to 2024-08-24); Time Zone held '
            'America/New_York on all 2318 rows of sharon_a13. No known-data record for these images was used. '
            'On samsung_a166u_a16_known_20261116 the table held no rows. A row records a fix the service '
            'logged, not by itself where a person was. Not reported from inferenceengine_logging.db: '
            'setting_change, api_call_log, profile (account fields), cpp_path_history_log, '
            'country_app_count, cmh_tag_log, keyboard_lang, general_real_time_collection_log, '
            'general_batch_collection_log, sa_raw_data, sa_personalized_log, screen_log, the Bluetooth, '
            'Wi-Fi, headset, gear, watch, notification, music, calendar and keyword tables. '
            'inferenceengine_logging.db in com.samsung.android.rubin.app/databases is not a plaintext SQLite '
            'file. It is read as SQLCipher with AES-256-CBC, 4096-byte pages, a 48-byte reserve and '
            "HMAC-SHA1, through scripts/sqlcipher_decrypt.py. The key comes from the extraction tool's "
            'Secrets/secrets.json, from the com.samsung.android.rubin.app entry whose script_output payload '
            'is named Logging. On the three exports seen the payload is 512 hex digits; their 256 bytes are '
            "the password to PBKDF2-HMAC-SHA1 with the database's first 16 bytes as salt and 4000 iterations. "
            'These settings were found by testing, not from app source. Every page of every database opened '
            'on the images in sample_data authenticated its HMAC (samsung_a166u_a16_known_20261116: '
            'SecureHealthData.db 707 of 707 pages with its write-ahead log, inferenceengine_logging.db 79 of '
            '79, inferenceengine_monitoring.db 71 of 71), and no run logged a page that failed. A key is '
            "taken from the entry whose user_id equals the database's Android user, then from entries with no "
            'user_id (no entry on sharon_a13 carries one; on sharon_a14 the Customization Service entry '
            'carries none), and is used only if at least one page authenticates under it; pages that fail are '
            'counted in a log line. With no such key the database is not read and a line is logged. The '
            'decrypted copy is written under the report folder (samsung_secure_decrypted) and read from '
            "there; the evidence file is only read. Android User is the user the database's path names. "
            'Android User held 0 on every row of the images in sample_data.'
        ),
        "paths": ('*/com.samsung.android.rubin.app/databases/inferenceengine_logging.db*', '*/Secrets/secrets.json'),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.rubin.app | 0 rows",
            "sharon_a13": "Android 13 | com.samsung.android.rubin.app | 2318 rows",
            "sharon_a14": "Android 14 | com.samsung.android.rubin.app | 2033 rows",
            "anne_a15": "Android 15 | com.samsung.android.rubin.app | 0 rows, no key in secrets.json",
            "falken_a326u_a13": "Android 13 | com.samsung.android.rubin.app | 0 rows, no key in secrets.json",
        },
    },
    "samsung_customization_motion": {
        "name": "Samsung Customization Service - Motion Log",
        "description": "The motion_log table of the encrypted Customization Service inferenceengine_logging.db, "
                       "decrypted with the key in the extraction's Secrets/secrets.json.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Samsung Customization Service",
        "notes": (
            "One row per motion_log row; motion_type is shown as stored. Times are the table's millisecond "
            'values read as UTC. On sharon_a13, sharon_a14 and samsung_a166u_a16_known_20261116 they equal '
            'the text time stored beside them (time_string, or start_time_string and end_time_string in '
            "app_usage) in the row's timezone_id, on every row of the location, app usage, charging and "
            'motion tables; web_log has no timezone_id, and its time_string matches in the zone the other '
            'tables name. A stored time inside the first day of 1970 is shown blank. On '
            'samsung_a166u_a16_known_20261116 the 39 rows include WALK at 17:02:55 and 17:03:25 UTC, inside '
            'the short walk with the phone at about 17:02 to 17:04 UTC (mint log), and VEHICLE at 17:03:49 '
            "UTC within the same minutes, so a motion_type is the service's classification and not "
            'established as what the person did. Time Zone held America/New_York on all 39 rows. Types seen '
            'across the images: LOGGING_START, STATIONARY, WALK, VEHICLE and RUN. sharon_a13 had 1476 rows '
            'and sharon_a14 524. Not reported from inferenceengine_logging.db: '
            'setting_change, api_call_log, profile (account fields), cpp_path_history_log, country_app_count, '
            'cmh_tag_log, keyboard_lang, general_real_time_collection_log, general_batch_collection_log, '
            'sa_raw_data, sa_personalized_log, screen_log, the Bluetooth, Wi-Fi, headset, gear, watch, '
            'notification, music, calendar and keyword tables. inferenceengine_logging.db in '
            'com.samsung.android.rubin.app/databases is not a plaintext SQLite file. It is read as SQLCipher '
            'with AES-256-CBC, 4096-byte pages, a 48-byte reserve and HMAC-SHA1, through '
            "scripts/sqlcipher_decrypt.py. The key comes from the extraction tool's Secrets/secrets.json, "
            'from the com.samsung.android.rubin.app entry whose script_output payload is named Logging. On '
            'the three exports seen the payload is 512 hex digits; their 256 bytes are the password to '
            "PBKDF2-HMAC-SHA1 with the database's first 16 bytes as salt and 4000 iterations. These settings "
            'were found by testing, not from app source. Every page of every database opened on the images in '
            'sample_data authenticated its HMAC (samsung_a166u_a16_known_20261116: SecureHealthData.db 707 of '
            '707 pages with its write-ahead log, inferenceengine_logging.db 79 of 79, '
            'inferenceengine_monitoring.db 71 of 71), and no run logged a page that failed. A key is taken '
            "from the entry whose user_id equals the database's Android user, then from entries with no "
            'user_id (no entry on sharon_a13 carries one; on sharon_a14 the Customization Service entry '
            'carries none), and is used only if at least one page authenticates under it; pages that fail are '
            'counted in a log line. With no such key the database is not read and a line is logged. The '
            'decrypted copy is written under the report folder (samsung_secure_decrypted) and read from '
            "there; the evidence file is only read. Android User is the user the database's path names. "
            'Android User held 0 on every row of the images in sample_data.'
        ),
        "paths": ('*/com.samsung.android.rubin.app/databases/inferenceengine_logging.db*', '*/Secrets/secrets.json'),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.rubin.app | 39 rows",
            "sharon_a13": "Android 13 | com.samsung.android.rubin.app | 1476 rows",
            "sharon_a14": "Android 14 | com.samsung.android.rubin.app | 524 rows",
            "anne_a15": "Android 15 | com.samsung.android.rubin.app | 0 rows, no key in secrets.json",
            "falken_a326u_a13": "Android 13 | com.samsung.android.rubin.app | 0 rows, no key in secrets.json",
        },
    },
    "samsung_customization_web": {
        "name": "Samsung Customization Service - Web Log",
        "description": "The web_log table of the encrypted Customization Service inferenceengine_logging.db with "
                       "the page each row names in web_info, decrypted with the key in the extraction's "
                       "Secrets/secrets.json.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Samsung Customization Service",
        "notes": (
            'One row per web_log row with the web_info row its web_info_id names (Title, URL, Page Update '
            "Time). Times are the table's millisecond values read as UTC. On sharon_a13, sharon_a14 and "
            'samsung_a166u_a16_known_20261116 they equal the text time stored beside them (time_string, or '
            "start_time_string and end_time_string in app_usage) in the row's timezone_id, on every row of "
            'the location, app usage, charging and motion tables; web_log has no timezone_id, and its '
            'time_string matches in the zone the other tables name. A stored time inside the first day of '
            '1970 is shown blank. sharon_a13 had 32 rows (URL on all 32, Title on 28) and sharon_a14 6. Page '
            'Update Time equalled Time on all 6 rows of sharon_a14 and on 18 of 32 on sharon_a13. No '
            'known-data record for these images was used. On samsung_a166u_a16_known_20261116 the table held '
            'no rows, although two pages were opened in Samsung Internet at 17:37 UTC in the known-data '
            'session, while the service showed On (mint log, 17:36 UTC); which visits the service records is '
            'not established. Not reported from inferenceengine_logging.db: setting_change, '
            'api_call_log, profile (account fields), cpp_path_history_log, country_app_count, cmh_tag_log, '
            'keyboard_lang, general_real_time_collection_log, general_batch_collection_log, sa_raw_data, '
            'sa_personalized_log, screen_log, the Bluetooth, Wi-Fi, headset, gear, watch, notification, '
            'music, calendar and keyword tables. inferenceengine_logging.db in '
            'com.samsung.android.rubin.app/databases is not a plaintext SQLite file. It is read as SQLCipher '
            'with AES-256-CBC, 4096-byte pages, a 48-byte reserve and HMAC-SHA1, through '
            "scripts/sqlcipher_decrypt.py. The key comes from the extraction tool's Secrets/secrets.json, "
            'from the com.samsung.android.rubin.app entry whose script_output payload is named Logging. On '
            'the three exports seen the payload is 512 hex digits; their 256 bytes are the password to '
            "PBKDF2-HMAC-SHA1 with the database's first 16 bytes as salt and 4000 iterations. These settings "
            'were found by testing, not from app source. Every page of every database opened on the images in '
            'sample_data authenticated its HMAC (samsung_a166u_a16_known_20261116: SecureHealthData.db 707 of '
            '707 pages with its write-ahead log, inferenceengine_logging.db 79 of 79, '
            'inferenceengine_monitoring.db 71 of 71), and no run logged a page that failed. A key is taken '
            "from the entry whose user_id equals the database's Android user, then from entries with no "
            'user_id (no entry on sharon_a13 carries one; on sharon_a14 the Customization Service entry '
            'carries none), and is used only if at least one page authenticates under it; pages that fail are '
            'counted in a log line. With no such key the database is not read and a line is logged. The '
            'decrypted copy is written under the report folder (samsung_secure_decrypted) and read from '
            "there; the evidence file is only read. Android User is the user the database's path names. "
            'Android User held 0 on every row of the images in sample_data.'
        ),
        "paths": ('*/com.samsung.android.rubin.app/databases/inferenceengine_logging.db*', '*/Secrets/secrets.json'),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.rubin.app | 0 rows",
            "sharon_a13": "Android 13 | com.samsung.android.rubin.app | 32 rows",
            "sharon_a14": "Android 14 | com.samsung.android.rubin.app | 6 rows",
            "anne_a15": "Android 15 | com.samsung.android.rubin.app | 0 rows, no key in secrets.json",
            "falken_a326u_a13": "Android 13 | com.samsung.android.rubin.app | 0 rows, no key in secrets.json",
        },
    },
    "samsung_customization_places": {
        "name": "Samsung Customization Service - Places",
        "description": "The analyzed_place_monitor and current_place_log tables of the encrypted Customization "
                       "Service inferenceengine_monitoring.db, decrypted with the key in the extraction's "
                       "Secrets/secrets.json.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Samsung Customization Service",
        "notes": (
            'Rows of two tables of inferenceengine_monitoring.db, named in Table: analyzed_place_monitor '
            '(with latitude, longitude and radius) and current_place_log (with registered_type and '
            'confidence, and no coordinates, so Latitude, Longitude, radius, geofence_type and geofence_state '
            'have no value on those rows). Time is geofence_registered_time or time, read as UTC '
            'milliseconds. place_category, registered_type, place_id, geofence_type, geofence_state and '
            'confidence are shown as stored. sharon_a13 had 2 analyzed and 46 current-place rows and '
            'sharon_a14 3 and 10; Time Zone held America/New_York on all 13 rows of sharon_a14. On '
            'samsung_a166u_a16_known_20261116 the one row is a current_place_log row of 16:53:09 UTC with '
            "place_category LOCATION_OFF. A place row is the service's analysis, not by itself where a person "
            'was. Not reported from this database: alt_place_log, tpo_context_event, '
            'collectable_context_event, home_context_event, the home and work in-out events, country_info, '
            'transporting_event_log, driving_event_log, exercise_place_log, appliance_event, '
            'calendar_event_context and the other monitor and event tables. The other Customization Service '
            'databases (inferenceengine_analytics.db, poi.db, odm.db, rubin_on_device.db, '
            'context_fence_database.db, HandDetectionDatabase.db, log_config.db, policy.db, '
            'rubin_access_control.db and upload.db, each with a -se file, and config.db and smp.db) have no '
            'payload in the exports seen or are not read. inferenceengine_monitoring.db in '
            'com.samsung.android.rubin.app/databases is not a plaintext SQLite file. It is read as SQLCipher '
            'with AES-256-CBC, 4096-byte pages, a 48-byte reserve and HMAC-SHA1, through '
            "scripts/sqlcipher_decrypt.py. The key comes from the extraction tool's Secrets/secrets.json, "
            'from the com.samsung.android.rubin.app entry whose script_output payload is named Monitoring. On '
            'the three exports seen the payload is 512 hex digits; their 256 bytes are the password to '
            "PBKDF2-HMAC-SHA1 with the database's first 16 bytes as salt and 4000 iterations. These settings "
            'were found by testing, not from app source. Every page of every database opened on the images in '
            'sample_data authenticated its HMAC (samsung_a166u_a16_known_20261116: SecureHealthData.db 707 of '
            '707 pages with its write-ahead log, inferenceengine_logging.db 79 of 79, '
            'inferenceengine_monitoring.db 71 of 71), and no run logged a page that failed. A key is taken '
            "from the entry whose user_id equals the database's Android user, then from entries with no "
            'user_id (no entry on sharon_a13 carries one; on sharon_a14 the Customization Service entry '
            'carries none), and is used only if at least one page authenticates under it; pages that fail are '
            'counted in a log line. With no such key the database is not read and a line is logged. The '
            'decrypted copy is written under the report folder (samsung_secure_decrypted) and read from '
            "there; the evidence file is only read. Android User is the user the database's path names. "
            'Android User held 0 on every row of the images in sample_data.'
        ),
        "paths": ('*/com.samsung.android.rubin.app/databases/inferenceengine_monitoring.db*',
                  '*/Secrets/secrets.json'),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.rubin.app | 1 row",
            "sharon_a13": "Android 13 | com.samsung.android.rubin.app | 48 rows",
            "sharon_a14": "Android 14 | com.samsung.android.rubin.app | 13 rows",
            "anne_a15": "Android 15 | com.samsung.android.rubin.app | 0 rows, no key in secrets.json",
            "falken_a326u_a13": "Android 13 | com.samsung.android.rubin.app | 0 rows, no key in secrets.json",
        },
    },
}

import datetime
import hashlib
import json
import os
import pathlib
import sqlite3

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.sqlcipher_decrypt import decrypt_sqlcipher_db
from scripts.artifacts.storagePathViews import android_user, unique_files

HEALTH = 'com.sec.android.app.shealth'
RUBIN = 'com.samsung.android.rubin.app'
# (package, database file name) -> the payload name the extraction tool gives its key
STORES = {
    (HEALTH, 'SecureHealthData.db'): 'SecureHealthData',
    (RUBIN, 'inferenceengine_logging.db'): 'Logging',
    (RUBIN, 'inferenceengine_monitoring.db'): 'Monitoring',
}
# SQLCipher 3 settings: every page of the tested databases verified its HMAC under them
PAGE_SIZE = 4096
RUBIN_KDF_ITERATIONS = 4000

_decrypted = {}


# A stored time inside the first day of 1970 is a placeholder (user_profile stores 1), not an event
_MIN_MS = 86400000


def _ms(value):
    if not isinstance(value, (int, float)) or value < _MIN_MS:
        return ''
    try:
        return datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(milliseconds=value)
    except OverflowError:
        return ''


def _keys(files_found, package):
    """{(payload name, user id as text or '' when absent): [payloads]} for one package."""
    keys = {}
    for path in files_found:
        if os.path.basename(str(path)) != 'secrets.json':
            continue
        try:
            with open(path, 'r', encoding='utf-8') as handle:
                entries = json.load(handle)
        except (OSError, ValueError) as ex:
            logfunc(f'Samsung secure stores: could not read {path}: {ex}')
            continue
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict) or entry.get('app') != package:
                continue
            for output in entry.get('script_output') or []:
                payload = output.get('payload') if isinstance(output, dict) else None
                if not isinstance(payload, dict):
                    continue
                for name, value in payload.items():
                    if isinstance(value, str) and value:
                        user_id = entry.get('user_id')
                        keys.setdefault((name, '' if user_id is None else str(user_id)), []).append(value)
    return keys


def _encryption_key(package, payload, database_path):
    """The 32-byte page key, or None when the payload has a shape this module does not handle."""
    if package == HEALTH:
        # x'<64 hex key><32 hex salt>'
        if payload.startswith("x'") and payload.endswith("'") and len(payload) == 99:
            try:
                return bytes.fromhex(payload[2:66])
            except ValueError:
                return None
        return None
    try:
        password = bytes.fromhex(payload)
    except ValueError:
        return None
    with open(database_path, 'rb') as handle:
        salt = handle.read(16)
    return hashlib.pbkdf2_hmac('sha1', password, salt, RUBIN_KDF_ITERATIONS, 32)


def _databases(context, package, file_name):
    """[(decrypted path, source path, Android user)] for every copy of one store the extraction holds."""
    files_found = unique_files(context)
    keys = _keys(files_found, package)
    payload_name = STORES[(package, file_name)]
    found = []
    for path in files_found:
        path = str(path)
        if os.path.basename(path) != file_name or os.path.isdir(path):
            continue
        if path in _decrypted:
            if _decrypted[path]:
                found.append((_decrypted[path], path, android_user(context.get_relative_path(path))))
            continue
        _decrypted[path] = None
        user = android_user(context.get_relative_path(path))
        # the key recorded for this Android user first, then keys recorded with no user; a key is
        # accepted only when it authenticates the database's pages, so a wrong guess is refused
        candidates = keys.get((payload_name, user), []) + (keys.get((payload_name, ''), []) if user else [])
        if not user:
            candidates = [value for (name, _user), values in keys.items() if name == payload_name for value in values]
        if not candidates:
            logfunc(f'Samsung secure stores: no {payload_name} key for Android user {user or "?"} in '
                    f'Secrets/secrets.json, so {file_name} stays encrypted')
            continue
        digest = hashlib.sha1(path.encode('utf-8', 'replace')).hexdigest()[:12]
        # the decrypted copy is the module's own output and stays with the case, never beside the evidence
        output = os.path.join(context.get_report_folder(), 'samsung_secure_decrypted', f'{digest}_{file_name}')
        os.makedirs(os.path.dirname(output), exist_ok=True)
        opened = False
        for payload in candidates:
            key = _encryption_key(package, payload, path)
            if key is None:
                logfunc(f'Samsung secure stores: a {payload_name} key has a shape this module does not read')
                continue
            try:
                pages, verified = decrypt_sqlcipher_db(path, key, output, page_size=PAGE_SIZE,
                                                       hmac_algorithm='sha1', kdf_algorithm='sha1', raw_key=True)
            except (OSError, ValueError) as ex:
                logfunc(f'Samsung secure stores: {file_name} not decrypted: {ex}')
                continue
            if not verified:
                continue
            if verified != pages:
                logfunc(f'Samsung secure stores: {pages - verified} of {pages} pages of {file_name} failed HMAC '
                        'verification; the recovered data may be incomplete')
            opened = True
            break
        if not opened:
            if os.path.exists(output):
                os.remove(output)  # this module's own unauthenticated output, not evidence
            logfunc(f'Samsung secure stores: no {payload_name} key in Secrets/secrets.json authenticated {file_name}')
            continue
        _decrypted[path] = output
        found.append((output, path, user))
    return found


def _rows(decrypted, table, columns, order):
    """Rows as dicts with every wanted column, None where this schema lacks one."""
    db = sqlite3.connect(pathlib.Path(decrypted).absolute().as_uri() + '?mode=ro', uri=True)
    try:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone():
            return []
        present = {row[1] for row in db.execute(f'PRAGMA table_info("{table}")')}
        select = ', '.join(f'"{c}"' if c in present else f'NULL AS "{c}"' for c in columns)
        ordering = order if order in present else 'rowid'
        return [dict(zip(columns, row)) for row in db.execute(f'SELECT {select} FROM "{table}" ORDER BY "{ordering}"')]
    except sqlite3.Error as ex:
        logfunc(f'Samsung secure stores: {table} not read: {ex}')
        return []
    finally:
        db.close()


def _health(context, short, fields, order='start__time'):
    """(rows, sources) for a com_samsung_health_<short> table, columns given without the prefix."""
    prefix = f'com_samsung_health_{short}_'
    out, sources = [], []
    for decrypted, source, user in _databases(context, HEALTH, 'SecureHealthData.db'):
        sources.append(source)
        for row in _rows(decrypted, f'com_samsung_health_{short}',
                         [f if f.startswith('com_samsung_shealth') else prefix + f for f in fields], prefix + order):
            row = {k.replace(prefix, ''): v for k, v in row.items()}
            row['_user'] = user
            out.append(row)
    return out, sources


@artifact_processor
def samsung_health_secure_user_profile(context):
    rows, sources = _health(context, 'user__profile', ['update__time', 'create__time', 'key', 'text__value',
                                                       'float__value', 'long__value', 'int__value', 'double__value',
                                                       'blob__value'],
                            order='key')
    data = []
    for r in rows:
        slot = next((name for name in ('text__value', 'float__value', 'long__value', 'int__value', 'double__value',
                                       'blob__value') if r[name] is not None), '')
        value = r[slot] if slot else ''
        if isinstance(value, (bytes, bytearray)):
            value = f'{len(value)} bytes (not decoded)'
        data.append((_ms(r['update__time']), _ms(r['create__time']), r['key'] or '', value,
                     slot.replace('__value', ''), r['_user']))
    data_headers = (('Update Time', 'datetime'), ('Create Time', 'datetime'), 'Key', 'Value', 'Value Type', 'Android User')
    return data_headers, data, '\n'.join(sources)


@artifact_processor
def samsung_health_secure_step_count(context):
    walk = 'com_samsung_shealth_tracker_pedometer__step__count_walk__step'
    run = 'com_samsung_shealth_tracker_pedometer__step__count_run__step'
    rows, sources = _health(context, 'step__count', ['start__time', 'end__time', 'count', walk, run, 'distance',
                                                     'calorie', 'speed', 'time__offset', 'deviceuuid'])
    data = [(_ms(r['start__time']), _ms(r['end__time']), r['count'], r[walk], r[run], r['distance'], r['calorie'],
             r['speed'], r['time__offset'], r['deviceuuid'] or '', r['_user']) for r in rows]
    data_headers = (('Start Time', 'datetime'), ('End Time', 'datetime'), 'Count', 'Walk Steps', 'Run Steps',
               'distance (as stored)', 'calorie (as stored)', 'speed (as stored)', 'time_offset (as stored)',
               'Device UUID', 'Android User')
    return data_headers, data, '\n'.join(sources)


@artifact_processor
def samsung_health_secure_sleep(context):
    sleep_type = 'com_samsung_shealth_sleep_sleep__type'
    rows, sources = _health(context, 'sleep', ['start__time', 'end__time', 'create__time', 'time__offset',
                                               sleep_type, 'comment', 'deviceuuid'])
    data = [(_ms(r['start__time']), _ms(r['end__time']), _ms(r['create__time']), r['time__offset'], r[sleep_type],
             r['comment'] or '', r['deviceuuid'] or '', r['_user']) for r in rows]
    data_headers = (('Start Time', 'datetime'), ('End Time', 'datetime'), ('Create Time', 'datetime'),
               'time_offset (as stored)', 'sleep_type (as stored)', 'Comment', 'Device UUID', 'Android User')
    return data_headers, data, '\n'.join(sources)


@artifact_processor
def samsung_health_secure_exercise(context):
    rows, sources = _health(context, 'exercise', ['start__time', 'end__time', 'create__time', 'duration',
                                                  'exercise__type', 'distance', 'calorie', 'count', 'comment',
                                                  'time__offset', 'deviceuuid'])
    data = [(_ms(r['start__time']), _ms(r['end__time']), _ms(r['create__time']), r['duration'], r['exercise__type'],
             r['distance'], r['calorie'], r['count'], r['comment'] or '', r['time__offset'], r['deviceuuid'] or '',
             r['_user']) for r in rows]
    data_headers = (('Start Time', 'datetime'), ('End Time', 'datetime'), ('Create Time', 'datetime'),
               'duration (ms, as stored)', 'exercise_type (as stored)', 'distance (as stored)', 'calorie (as stored)',
               'count (as stored)', 'Comment', 'time_offset (as stored)', 'Device UUID', 'Android User')
    return data_headers, data, '\n'.join(sources)


def _coordinates(latitude, longitude):
    if latitude in (0, 0.0, None) and longitude in (0, 0.0, None):
        return None, None
    return latitude, longitude


def _rubin(context, file_name, table, columns, order):
    out, sources = [], []
    for decrypted, source, user in _databases(context, RUBIN, file_name):
        sources.append(source)
        for row in _rows(decrypted, table, columns, order):
            row['_user'] = user
            out.append(row)
    return out, sources


@artifact_processor
def samsung_customization_app_usage(context):
    rows, sources = _rubin(context, 'inferenceengine_logging.db', 'app_usage',
                           ['start_time', 'end_time', 'package_name', 'class_name', 'timezone_id', '_id'], 'start_time')
    data = [(_ms(r['start_time']), _ms(r['end_time']), r['package_name'] or '', r['class_name'] or '',
             r['timezone_id'] or '', r['_id'], r['_user']) for r in rows]
    data_headers = (('Start Time', 'datetime'), ('End Time', 'datetime'), 'Package Name', 'Class Name', 'Time Zone',
               'Row ID', 'Android User')
    return data_headers, data, '\n'.join(sources)


@artifact_processor
def samsung_customization_charging(context):
    rows, sources = _rubin(context, 'inferenceengine_logging.db', 'charging_log',
                           ['time', 'connected', 'plugged', 'level', 'place_id', 'timezone_id', '_id'], 'time')
    data = [(_ms(r['time']), r['connected'], r['plugged'], r['level'], r['place_id'], r['timezone_id'] or '', r['_id'],
             r['_user']) for r in rows]
    data_headers = (('Time', 'datetime'), 'connected (as stored)', 'plugged (as stored)', 'level (as stored)',
               'place_id (as stored)', 'Time Zone', 'Row ID', 'Android User')
    return data_headers, data, '\n'.join(sources)


@artifact_processor
def samsung_customization_screen_state(context):
    rows, sources = _rubin(context, 'inferenceengine_logging.db', 'screen_state_log',
                           ['time', 'screen_state', 'user_present', 'use_keyguard', 'time_string', 'timezone_id',
                            '_id'], 'time')
    data = [(_ms(r['time']), r['screen_state'], r['user_present'], r['use_keyguard'], r['time_string'] or '',
             r['timezone_id'] or '', r['_id'], r['_user']) for r in rows]
    data_headers = (('Time', 'datetime'), 'screen_state (as stored)', 'user_present (as stored)',
                    'use_keyguard (as stored)', 'Time String (as stored)', 'Time Zone', 'Row ID', 'Android User')
    return data_headers, data, '\n'.join(sources)


@artifact_processor
def samsung_customization_location(context):
    rows, sources = _rubin(context, 'inferenceengine_logging.db', 'location_log',
                           ['time', 'latitude', 'longitude', 'altitude', 'accuracy', 'provider', 'speed', 'bearing',
                            'timezone_id', '_id'], 'time')
    # a row storing 0 in both coordinates is not a position; its coordinates are shown blank
    data = [(_ms(r['time']), *_coordinates(r['latitude'], r['longitude']), r['altitude'], r['accuracy'],
             r['provider'] or '',
             r['speed'], r['bearing'], r['timezone_id'] or '', r['_id'], r['_user']) for r in rows]
    data_headers = (('Time', 'datetime'), ('Latitude', 'latitude'), ('Longitude', 'longitude'), 'altitude (as stored)',
               'accuracy (as stored)', 'Provider', 'speed (as stored)', 'bearing (as stored)', 'Time Zone', 'Row ID', 'Android User')
    return data_headers, data, '\n'.join(sources)


@artifact_processor
def samsung_customization_motion(context):
    rows, sources = _rubin(context, 'inferenceengine_logging.db', 'motion_log',
                           ['time', 'motion_type', 'timezone_id', '_id'], 'time')
    data = [(_ms(r['time']), r['motion_type'] or '', r['timezone_id'] or '', r['_id'], r['_user']) for r in rows]
    data_headers = (('Time', 'datetime'), 'motion_type (as stored)', 'Time Zone', 'Row ID', 'Android User')
    return data_headers, data, '\n'.join(sources)


@artifact_processor
def samsung_customization_web(context):
    data, sources = [], []
    for decrypted, source, user in _databases(context, RUBIN, 'inferenceengine_logging.db'):
        sources.append(source)
        pages = {r['_id']: r for r in _rows(decrypted, 'web_info', ['_id', 'title', 'url', 'update_time'], '_id')}
        for r in _rows(decrypted, 'web_log', ['time', 'web_info_id'], 'time'):
            page = pages.get(r['web_info_id'], {})
            data.append((_ms(r['time']), page.get('title') or '', page.get('url') or '', _ms(page.get('update_time')),
                         r['web_info_id'], user))
    data_headers = (('Time', 'datetime'), 'Title', 'URL', ('Page Update Time', 'datetime'), 'web_info_id', 'Android User')
    return data_headers, data, '\n'.join(sources)


@artifact_processor
def samsung_customization_places(context):
    data, sources = [], []
    for decrypted, source, user in _databases(context, RUBIN, 'inferenceengine_monitoring.db'):
        sources.append(source)
        for r in _rows(decrypted, 'analyzed_place_monitor',
                       ['geofence_registered_time', 'place_category', 'place_id', 'geofence_type', 'geofence_state',
                        'latitude', 'longitude', 'radius', 'timezone_id'], 'geofence_registered_time'):
            data.append((_ms(r['geofence_registered_time']), 'analyzed_place_monitor', r['place_category'] or '', '',
                         r['place_id'], *_coordinates(r['latitude'], r['longitude']), r['radius'], r['geofence_type'],
                         r['geofence_state'], None, r['timezone_id'] or '', user))
        for r in _rows(decrypted, 'current_place_log',
                       ['time', 'place_category', 'registered_type', 'place_id', 'confidence', 'timezone_id'], 'time'):
            data.append((_ms(r['time']), 'current_place_log', r['place_category'] or '', r['registered_type'] or '',
                         r['place_id'], None, None, None, None, None, r['confidence'], r['timezone_id'] or '', user))
    data_headers = (('Time', 'datetime'), 'Table', 'place_category (as stored)', 'registered_type (as stored)',
               'place_id (as stored)', ('Latitude', 'latitude'), ('Longitude', 'longitude'), 'radius (as stored)',
               'geofence_type (as stored)', 'geofence_state (as stored)', 'confidence (as stored)', 'Time Zone', 'Android User')
    return data_headers, data, '\n'.join(sources)

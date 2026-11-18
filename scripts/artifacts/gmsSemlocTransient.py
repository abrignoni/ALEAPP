__artifacts_v2__ = {
    "gms_semloc_transient_visits": {
        "name": "Semantic Location Transient - Visits",
        "description": "Visit segments in Google Play services' transient semantic location "
                       "store: start and end time, place location, place semantic type and "
                       "probabilities.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Semantic Location",
        "notes": "Read from Google Play services' semloc_transient_database (Room database, table "
                 "TransientDataEntity, under com.google.android.gms/databases/). Two tested images "
                 "(anne_a15, kevin_pocox7_a15) also have a copy under com.google.android.gms/cache/. "
                 "Each row has a type and a protobuf data blob, decoded with the vendored "
                 "blackboxprotobuf and field types from the app's own message classes. Sources are "
                 "the decompiled Google Play services APK from dragna_pixel9a_a16 "
                 "(com.google.android.gms 26.39.33, versionCode 263933035, decompiled with jadx; the "
                 "code is obfuscated). The type values come from the code that writes the rows: 1 is "
                 "a visit segment, 2 an activity segment, 3 a frequent places list, 4 a path segment "
                 "and 5 a raw signal record; a segment with none of those payloads is written as "
                 "type 0. Field names come from Play services' location history export code, which "
                 "writes Timeline segments, the user location profile and raw signals to JSON under "
                 "names such as startTime, hierarchyLevel, topCandidate, placeLocation, "
                 "distanceMeters, frequentPlaces, label, position, accuracyMeters and "
                 "activityRecord. A converter in Play services fills the transient segment and "
                 "frequent place records from those Timeline records field by field. It does not "
                 "copy everything unchanged: see Activity Type and Finalization Status. Raw signal "
                 "records are the same message class the export writes. Coordinates are stored as "
                 "integers in units of 1e-7 degree, the scale the export code divides by. Row "
                 "Written is the row's creation_time_seconds, which the writing code sets from the "
                 "device clock when it stores the row. The code that reads the table back asks only "
                 "for rows written in the last 2 days. A cleanup job in the same code deletes rows "
                 "written more than 2 days before it runs, and rewritten segments and lists replace "
                 "earlier rows. When the job runs was not traced. On the tested images the rows span "
                 "up to 2.3 days. Field meaning was read from one Play services version. The other "
                 "images' versions were not decompiled. Their rows of types 1, 2, 3 and 5 use the "
                 "same field numbers; rows on anne_a15 and kevin_pocox7_a15 also carry a segment id "
                 "string in wrapper field 3, which is not read. On dragna_pixel9a_a16 the visits and "
                 "activities chain: all 7 activity end times equal a visit start time and 6 of 7 "
                 "activity start times equal a visit end time. Not reported: type 0 rows (start, "
                 "end, offsets and status only; seen on anne_a15 and kevin_pocox7_a15), type 4 path "
                 "rows and Wi-Fi scan records (none on any tested image), the part of the place "
                 "identifier the store keeps, and the segment_id, segment_start_time_seconds, "
                 "obfuscated_gaia_id and finalization_status columns. The decompiled version has two "
                 "writers for the last: one stores status 0 and an empty segment_id, the other "
                 "derives both from the segment. The Pixel images hold 0 on every row; anne_a15 and "
                 "kevin_pocox7_a15 hold 0 and 1. Each segment carries its own status, which is what "
                 "is reported. Rows are not deduplicated, so a segment written to both copies of the "
                 "database, or twice to one, appears on more than one row. When rows come from more "
                 "than one database, a Source File column names the database. Rows of type 1. Start "
                 "Time and End Time are the segment's startTime and endTime; the UTC offsets are "
                 "startTimeTimezoneUtcOffsetMinutes and endTimeTimezoneUtcOffsetMinutes as stored. "
                 "Latitude and Longitude are the top candidate's placeLocation. Semantic Type uses "
                 "the names of Play services' own enum (UNKNOWN, HOME, WORK, INFERRED_HOME, "
                 "INFERRED_WORK, SEARCHED_ADDRESS, ALIASED_LOCATION). Place Probability is the top "
                 "candidate's probability and Visit Probability the visit's probability; Hierarchy "
                 "Level is hierarchyLevel. Finalization Status uses the names of Play services' enum "
                 "for the segment (UNSPECIFIED_FINALIZATION_STATUS, STABILIZED, FINALIZED). The "
                 "converter stores the Timeline statuses USER_EDITED and BACKFILLED as 0, so "
                 "UNSPECIFIED_FINALIZATION_STATUS here can also be one of those. The store keeps "
                 "only part of the place identifier, so no place id is reported. A visit row comes "
                 "from the location service's Timeline segments. It is not a record of where the "
                 "user said they were, and the store does not show whether a segment was edited by "
                 "the user. Start UTC Offset (min) and End UTC Offset (min) held one value on all "
                 "rows of dragna_pixel9a_a16, hc_pixel8pro_a16, hc_pixel8pro_a17 and "
                 "kevin_pocox7_a15. anne_a15 held two values, and Start UTC Offset (min) and End UTC Offset (min) were identical on each row. "
                 "Semantic Type held one value, UNKNOWN, on all rows of every tested image with "
                 "rows. Hierarchy Level held 0 on all rows of dragna_pixel9a_a16.",
        "paths": ('*/com.google.android.gms/*/semloc_transient_database*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | com.google.android.gms 26.39.33 | 8 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms | 6 rows",
            "hc_pixel8pro_a17": "Android 17 | com.google.android.gms | 1 row",
            "anne_a15": "Android 15 | com.google.android.gms | 2 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 24 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.google.android.gms | 0 rows",
            "samsung_a166u_a16_known_20261117": "Android 16 | com.google.android.gms | 0 rows",
            "adams_ss135dl_a13": "Android 13 | com.google.android.gms | 0 rows",
            "falken_a326u_a13": "Android 13 | com.google.android.gms | 0 rows",
            "s20fe_a13": "Android 13 | com.google.android.gms | 0 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 0 rows",
        },
    },
    "gms_semloc_transient_activities": {
        "name": "Semantic Location Transient - Activities",
        "description": "Activity segments in Google Play services' transient semantic location "
                       "store: start and end time and location, distance, activity type and "
                       "probabilities.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Semantic Location",
        "notes": "Read from Google Play services' semloc_transient_database (Room database, table "
                 "TransientDataEntity, under com.google.android.gms/databases/). Two tested images "
                 "(anne_a15, kevin_pocox7_a15) also have a copy under com.google.android.gms/cache/. "
                 "Each row has a type and a protobuf data blob, decoded with the vendored "
                 "blackboxprotobuf and field types from the app's own message classes. Sources are "
                 "the decompiled Google Play services APK from dragna_pixel9a_a16 "
                 "(com.google.android.gms 26.39.33, versionCode 263933035, decompiled with jadx; the "
                 "code is obfuscated). The type values come from the code that writes the rows: 1 is "
                 "a visit segment, 2 an activity segment, 3 a frequent places list, 4 a path segment "
                 "and 5 a raw signal record; a segment with none of those payloads is written as "
                 "type 0. Field names come from Play services' location history export code, which "
                 "writes Timeline segments, the user location profile and raw signals to JSON under "
                 "names such as startTime, hierarchyLevel, topCandidate, placeLocation, "
                 "distanceMeters, frequentPlaces, label, position, accuracyMeters and "
                 "activityRecord. A converter in Play services fills the transient segment and "
                 "frequent place records from those Timeline records field by field. It does not "
                 "copy everything unchanged: see Activity Type and Finalization Status. Raw signal "
                 "records are the same message class the export writes. Coordinates are stored as "
                 "integers in units of 1e-7 degree, the scale the export code divides by. Row "
                 "Written is the row's creation_time_seconds, which the writing code sets from the "
                 "device clock when it stores the row. The code that reads the table back asks only "
                 "for rows written in the last 2 days. A cleanup job in the same code deletes rows "
                 "written more than 2 days before it runs, and rewritten segments and lists replace "
                 "earlier rows. When the job runs was not traced. On the tested images the rows span "
                 "up to 2.3 days. Field meaning was read from one Play services version. The other "
                 "images' versions were not decompiled. Their rows of types 1, 2, 3 and 5 use the "
                 "same field numbers; rows on anne_a15 and kevin_pocox7_a15 also carry a segment id "
                 "string in wrapper field 3, which is not read. On dragna_pixel9a_a16 the visits and "
                 "activities chain: all 7 activity end times equal a visit start time and 6 of 7 "
                 "activity start times equal a visit end time. Not reported: type 0 rows (start, "
                 "end, offsets and status only; seen on anne_a15 and kevin_pocox7_a15), type 4 path "
                 "rows and Wi-Fi scan records (none on any tested image), the part of the place "
                 "identifier the store keeps, and the segment_id, segment_start_time_seconds, "
                 "obfuscated_gaia_id and finalization_status columns. The decompiled version has two "
                 "writers for the last: one stores status 0 and an empty segment_id, the other "
                 "derives both from the segment. The Pixel images hold 0 on every row; anne_a15 and "
                 "kevin_pocox7_a15 hold 0 and 1. Each segment carries its own status, which is what "
                 "is reported. Rows are not deduplicated, so a segment written to both copies of the "
                 "database, or twice to one, appears on more than one row. When rows come from more "
                 "than one database, a Source File column names the database. Rows of type 2. Start "
                 "Time and End Time are the segment's startTime and endTime; the UTC offsets are as "
                 "stored in minutes. Start and End Latitude and Longitude are the activity's start "
                 "and end; Parking Latitude and Longitude the parking location the export writes "
                 "under parking. Distance (m) is distanceMeters and Segment Probability the "
                 "activity's probability. Activity Type uses the names of Play services' own "
                 "activity enum (for example WALKING, CYCLING, IN_PASSENGER_VEHICLE, IN_BUS, "
                 "IN_TRAIN); Activity Type Probability is the top candidate's probability. The "
                 "converter stores any Timeline activity type outside that 15-value enum as 0, so "
                 "UNKNOWN_ACTIVITY_TYPE here can be a type the Timeline names. Finalization Status "
                 "uses the names of Play services' enum for the segment "
                 "(UNSPECIFIED_FINALIZATION_STATUS, STABILIZED, FINALIZED). The converter stores the "
                 "Timeline statuses USER_EDITED and BACKFILLED as 0, so "
                 "UNSPECIFIED_FINALIZATION_STATUS here can also be one of those. An activity row "
                 "comes from the location service's Timeline segments. It is not a record of how the "
                 "user said they travelled, and the store does not show whether a segment was edited "
                 "by the user. Start UTC Offset (min) and End UTC Offset (min) held one value on all "
                 "rows of dragna_pixel9a_a16, hc_pixel8pro_a16 and kevin_pocox7_a15. On anne_a15 the "
                 "End UTC Offset (min) held two values. Activity Type held one value on all rows of "
                 "hc_pixel8pro_a16 and kevin_pocox7_a15. Finalization Status held one value on all "
                 "rows of anne_a15 and hc_pixel8pro_a16. Parking Latitude and Parking Longitude had "
                 "no value on any row of anne_a15 and kevin_pocox7_a15, whose records carry no "
                 "parking field.",
        "paths": ('*/com.google.android.gms/*/semloc_transient_database*',),
        "output_types": "standard",
        "artifact_icon": "navigation",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | com.google.android.gms 26.39.33 | 7 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms | 5 rows",
            "hc_pixel8pro_a17": "Android 17 | com.google.android.gms | 0 rows",
            "anne_a15": "Android 15 | com.google.android.gms | 3 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 18 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.google.android.gms | 0 rows",
            "samsung_a166u_a16_known_20261117": "Android 16 | com.google.android.gms | 0 rows",
            "adams_ss135dl_a13": "Android 13 | com.google.android.gms | 0 rows",
            "falken_a326u_a13": "Android 13 | com.google.android.gms | 0 rows",
            "s20fe_a13": "Android 13 | com.google.android.gms | 0 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 0 rows",
        },
    },
    "gms_semloc_transient_frequent_places": {
        "name": "Semantic Location Transient - Frequent Places",
        "description": "Frequent places lists in Google Play services' transient semantic "
                       "location store: place location and label (HOME, WORK or "
                       "UNKNOWN_TYPE).",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Semantic Location",
        "notes": "Read from Google Play services' semloc_transient_database (Room database, table "
                 "TransientDataEntity, under com.google.android.gms/databases/). Two tested images "
                 "(anne_a15, kevin_pocox7_a15) also have a copy under com.google.android.gms/cache/. "
                 "Each row has a type and a protobuf data blob, decoded with the vendored "
                 "blackboxprotobuf and field types from the app's own message classes. Sources are "
                 "the decompiled Google Play services APK from dragna_pixel9a_a16 "
                 "(com.google.android.gms 26.39.33, versionCode 263933035, decompiled with jadx; the "
                 "code is obfuscated). The type values come from the code that writes the rows: 1 is "
                 "a visit segment, 2 an activity segment, 3 a frequent places list, 4 a path segment "
                 "and 5 a raw signal record; a segment with none of those payloads is written as "
                 "type 0. Field names come from Play services' location history export code, which "
                 "writes Timeline segments, the user location profile and raw signals to JSON under "
                 "names such as startTime, hierarchyLevel, topCandidate, placeLocation, "
                 "distanceMeters, frequentPlaces, label, position, accuracyMeters and "
                 "activityRecord. A converter in Play services fills the transient segment and "
                 "frequent place records from those Timeline records field by field. It does not "
                 "copy everything unchanged: see Activity Type and Finalization Status. Raw signal "
                 "records are the same message class the export writes. Coordinates are stored as "
                 "integers in units of 1e-7 degree, the scale the export code divides by. Row "
                 "Written is the row's creation_time_seconds, which the writing code sets from the "
                 "device clock when it stores the row. The code that reads the table back asks only "
                 "for rows written in the last 2 days. A cleanup job in the same code deletes rows "
                 "written more than 2 days before it runs, and rewritten segments and lists replace "
                 "earlier rows. When the job runs was not traced. On the tested images the rows span "
                 "up to 2.3 days. Field meaning was read from one Play services version. The other "
                 "images' versions were not decompiled. Their rows of types 1, 2, 3 and 5 use the "
                 "same field numbers; rows on anne_a15 and kevin_pocox7_a15 also carry a segment id "
                 "string in wrapper field 3, which is not read. On dragna_pixel9a_a16 the visits and "
                 "activities chain: all 7 activity end times equal a visit start time and 6 of 7 "
                 "activity start times equal a visit end time. Not reported: type 0 rows (start, "
                 "end, offsets and status only; seen on anne_a15 and kevin_pocox7_a15), type 4 path "
                 "rows and Wi-Fi scan records (none on any tested image), the part of the place "
                 "identifier the store keeps, and the segment_id, segment_start_time_seconds, "
                 "obfuscated_gaia_id and finalization_status columns. The decompiled version has two "
                 "writers for the last: one stores status 0 and an empty segment_id, the other "
                 "derives both from the segment. The Pixel images hold 0 on every row; anne_a15 and "
                 "kevin_pocox7_a15 hold 0 and 1. Each segment carries its own status, which is what "
                 "is reported. Rows are not deduplicated, so a segment written to both copies of the "
                 "database, or twice to one, appears on more than one row. When rows come from more "
                 "than one database, a Source File column names the database. Rows of type 3, one "
                 "output row per place in the list. The list is built from the user location "
                 "profile's frequentPlaces, which the export writes with placeLocation and label. "
                 "Label uses the export's names: UNKNOWN_TYPE, HOME and WORK. The store does not "
                 "show whether a HOME or WORK label was inferred by the location service or set by "
                 "the user. Row Written held one value on all rows of each tested image, because "
                 "each image had one list row.",
        "paths": ('*/com.google.android.gms/*/semloc_transient_database*',),
        "output_types": "all",
        "artifact_icon": "home",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | com.google.android.gms 26.39.33 | 7 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms | 2 rows",
            "hc_pixel8pro_a17": "Android 17 | com.google.android.gms | 5 rows",
            "anne_a15": "Android 15 | com.google.android.gms | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 10 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.google.android.gms | 0 rows",
            "samsung_a166u_a16_known_20261117": "Android 16 | com.google.android.gms | 0 rows",
            "adams_ss135dl_a13": "Android 13 | com.google.android.gms | 0 rows",
            "falken_a326u_a13": "Android 13 | com.google.android.gms | 0 rows",
            "s20fe_a13": "Android 13 | com.google.android.gms | 0 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 0 rows",
        },
    },
    "gms_semloc_transient_positions": {
        "name": "Semantic Location Transient - Raw Positions",
        "description": "Position records among the raw signals in Google Play services' "
                       "transient semantic location store: time, latitude, longitude, "
                       "accuracy, altitude, source and speed.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Semantic Location",
        "notes": "Read from Google Play services' semloc_transient_database (Room database, table "
                 "TransientDataEntity, under com.google.android.gms/databases/). Two tested images "
                 "(anne_a15, kevin_pocox7_a15) also have a copy under com.google.android.gms/cache/. "
                 "Each row has a type and a protobuf data blob, decoded with the vendored "
                 "blackboxprotobuf and field types from the app's own message classes. Sources are "
                 "the decompiled Google Play services APK from dragna_pixel9a_a16 "
                 "(com.google.android.gms 26.39.33, versionCode 263933035, decompiled with jadx; the "
                 "code is obfuscated). The type values come from the code that writes the rows: 1 is "
                 "a visit segment, 2 an activity segment, 3 a frequent places list, 4 a path segment "
                 "and 5 a raw signal record; a segment with none of those payloads is written as "
                 "type 0. Field names come from Play services' location history export code, which "
                 "writes Timeline segments, the user location profile and raw signals to JSON under "
                 "names such as startTime, hierarchyLevel, topCandidate, placeLocation, "
                 "distanceMeters, frequentPlaces, label, position, accuracyMeters and "
                 "activityRecord. A converter in Play services fills the transient segment and "
                 "frequent place records from those Timeline records field by field. It does not "
                 "copy everything unchanged: see Activity Type and Finalization Status. Raw signal "
                 "records are the same message class the export writes. Coordinates are stored as "
                 "integers in units of 1e-7 degree, the scale the export code divides by. Row "
                 "Written is the row's creation_time_seconds, which the writing code sets from the "
                 "device clock when it stores the row. The code that reads the table back asks only "
                 "for rows written in the last 2 days. A cleanup job in the same code deletes rows "
                 "written more than 2 days before it runs, and rewritten segments and lists replace "
                 "earlier rows. When the job runs was not traced. On the tested images the rows span "
                 "up to 2.3 days. Field meaning was read from one Play services version. The other "
                 "images' versions were not decompiled. Their rows of types 1, 2, 3 and 5 use the "
                 "same field numbers; rows on anne_a15 and kevin_pocox7_a15 also carry a segment id "
                 "string in wrapper field 3, which is not read. On dragna_pixel9a_a16 the visits and "
                 "activities chain: all 7 activity end times equal a visit start time and 6 of 7 "
                 "activity start times equal a visit end time. Not reported: type 0 rows (start, "
                 "end, offsets and status only; seen on anne_a15 and kevin_pocox7_a15), type 4 path "
                 "rows and Wi-Fi scan records (none on any tested image), the part of the place "
                 "identifier the store keeps, and the segment_id, segment_start_time_seconds, "
                 "obfuscated_gaia_id and finalization_status columns. The decompiled version has two "
                 "writers for the last: one stores status 0 and an empty segment_id, the other "
                 "derives both from the segment. The Pixel images hold 0 on every row; anne_a15 and "
                 "kevin_pocox7_a15 hold 0 and 1. Each segment carries its own status, which is what "
                 "is reported. Rows are not deduplicated, so a segment written to both copies of the "
                 "database, or twice to one, appears on more than one row. When rows come from more "
                 "than one database, a Source File column names the database. Rows of type 5 that "
                 "hold a position. Field names are those the export writes under "
                 "rawSignals/position: timestamp (milliseconds, shown in UTC), LatLng, "
                 "accuracyMeters (the stored integer divided by 1000, the divisor the export uses; "
                 "the export keeps whole metres, this column keeps the fraction), altitudeMeters, "
                 "source and speedMetersPerSecond. Source uses the names of Play services' enum "
                 "(UNKNOWN, GPS, CELL, WIFI, WIFI_ONLY). Altitude and speed are not present on every "
                 "record and are blank where absent. Position rows also carry an integer in field 2 "
                 "of the raw signal message. Its meaning is not established and it is not reported.",
        "paths": ('*/com.google.android.gms/*/semloc_transient_database*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | com.google.android.gms 26.39.33 | 191 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms | 481 rows",
            "hc_pixel8pro_a17": "Android 17 | com.google.android.gms | 22 rows",
            "anne_a15": "Android 15 | com.google.android.gms | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 0 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.google.android.gms | 0 rows",
            "samsung_a166u_a16_known_20261117": "Android 16 | com.google.android.gms | 0 rows",
            "adams_ss135dl_a13": "Android 13 | com.google.android.gms | 0 rows",
            "falken_a326u_a13": "Android 13 | com.google.android.gms | 0 rows",
            "s20fe_a13": "Android 13 | com.google.android.gms | 0 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 0 rows",
        },
    },
    "gms_semloc_transient_activity_records": {
        "name": "Semantic Location Transient - Raw Activity Records",
        "description": "Activity records among the raw signals in Google Play services' "
                       "transient semantic location store: time and the probable activities "
                       "with their confidence.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Semantic Location",
        "notes": "Read from Google Play services' semloc_transient_database (Room database, table "
                 "TransientDataEntity, under com.google.android.gms/databases/). Two tested images "
                 "(anne_a15, kevin_pocox7_a15) also have a copy under com.google.android.gms/cache/. "
                 "Each row has a type and a protobuf data blob, decoded with the vendored "
                 "blackboxprotobuf and field types from the app's own message classes. Sources are "
                 "the decompiled Google Play services APK from dragna_pixel9a_a16 "
                 "(com.google.android.gms 26.39.33, versionCode 263933035, decompiled with jadx; the "
                 "code is obfuscated). The type values come from the code that writes the rows: 1 is "
                 "a visit segment, 2 an activity segment, 3 a frequent places list, 4 a path segment "
                 "and 5 a raw signal record; a segment with none of those payloads is written as "
                 "type 0. Field names come from Play services' location history export code, which "
                 "writes Timeline segments, the user location profile and raw signals to JSON under "
                 "names such as startTime, hierarchyLevel, topCandidate, placeLocation, "
                 "distanceMeters, frequentPlaces, label, position, accuracyMeters and "
                 "activityRecord. A converter in Play services fills the transient segment and "
                 "frequent place records from those Timeline records field by field. It does not "
                 "copy everything unchanged: see Activity Type and Finalization Status. Raw signal "
                 "records are the same message class the export writes. Coordinates are stored as "
                 "integers in units of 1e-7 degree, the scale the export code divides by. Row "
                 "Written is the row's creation_time_seconds, which the writing code sets from the "
                 "device clock when it stores the row. The code that reads the table back asks only "
                 "for rows written in the last 2 days. A cleanup job in the same code deletes rows "
                 "written more than 2 days before it runs, and rewritten segments and lists replace "
                 "earlier rows. When the job runs was not traced. On the tested images the rows span "
                 "up to 2.3 days. Field meaning was read from one Play services version. The other "
                 "images' versions were not decompiled. Their rows of types 1, 2, 3 and 5 use the "
                 "same field numbers; rows on anne_a15 and kevin_pocox7_a15 also carry a segment id "
                 "string in wrapper field 3, which is not read. On dragna_pixel9a_a16 the visits and "
                 "activities chain: all 7 activity end times equal a visit start time and 6 of 7 "
                 "activity start times equal a visit end time. Not reported: type 0 rows (start, "
                 "end, offsets and status only; seen on anne_a15 and kevin_pocox7_a15), type 4 path "
                 "rows and Wi-Fi scan records (none on any tested image), the part of the place "
                 "identifier the store keeps, and the segment_id, segment_start_time_seconds, "
                 "obfuscated_gaia_id and finalization_status columns. The decompiled version has two "
                 "writers for the last: one stores status 0 and an empty segment_id, the other "
                 "derives both from the segment. The Pixel images hold 0 on every row; anne_a15 and "
                 "kevin_pocox7_a15 hold 0 and 1. Each segment carries its own status, which is what "
                 "is reported. Rows are not deduplicated, so a segment written to both copies of the "
                 "database, or twice to one, appears on more than one row. When rows come from more "
                 "than one database, a Source File column names the database. Rows of type 5 that "
                 "hold an activity record. Field names are those the export writes under "
                 "rawSignals/activityRecord: timestamp (milliseconds, shown in UTC) and "
                 "probableActivities, each a type and a confidence. Types use the names of Play "
                 "services' enum (IN_VEHICLE, ON_BICYCLE, ON_FOOT, STILL, UNKNOWN, TILTING, "
                 "EXITING_VEHICLE, WALKING, RUNNING, IN_ROAD_VEHICLE, IN_RAIL_VEHICLE, "
                 "IN_TWO_WHEELER_VEHICLE). Top Activity is the type with the highest confidence; "
                 "Probable Activities lists every pair in stored order, with each confidence rounded "
                 "to 3 significant digits. A record is the activity classifier's output, not a "
                 "record of what the user did.",
        "paths": ('*/com.google.android.gms/*/semloc_transient_database*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | com.google.android.gms 26.39.33 | 395 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms | 610 rows",
            "hc_pixel8pro_a17": "Android 17 | com.google.android.gms | 130 rows",
            "anne_a15": "Android 15 | com.google.android.gms | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 0 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.google.android.gms | 0 rows",
            "samsung_a166u_a16_known_20261117": "Android 16 | com.google.android.gms | 0 rows",
            "adams_ss135dl_a13": "Android 13 | com.google.android.gms | 0 rows",
            "falken_a326u_a13": "Android 13 | com.google.android.gms | 0 rows",
            "s20fe_a13": "Android 13 | com.google.android.gms | 0 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 0 rows",
        },
    },
}

import os
from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.blackboxprotobuf import decode_message
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, logfunc

_DB_NAME = 'semloc_transient_database'
_INT = {'type': 'int', 'name': ''}
_FLOAT = {'type': 'float', 'name': ''}
_TIMESTAMP = {'type': 'message', 'name': '', 'message_typedef': {'1': _INT, '2': _INT}}
_LATLNG = {'type': 'message', 'name': '', 'message_typedef': {
    '1': {'type': 'sfixed32', 'name': ''}, '2': {'type': 'sfixed32', 'name': ''}}}
_PLACE_CANDIDATE = {'type': 'message', 'name': '', 'message_typedef': {
    '1': {'type': 'fixed64', 'name': ''}, '2': _INT, '3': _FLOAT, '4': _LATLNG,
    '8': {'type': 'double', 'name': ''}}}
_SEGMENT = {
    '1': _TIMESTAMP, '2': _TIMESTAMP, '3': _INT, '4': _INT,
    '5': {'type': 'message', 'name': '', 'message_typedef': {
        '1': _INT, '2': _FLOAT, '3': _PLACE_CANDIDATE, '4': _PLACE_CANDIDATE}},
    '6': {'type': 'message', 'name': '', 'message_typedef': {
        '1': _LATLNG, '2': _LATLNG, '3': _FLOAT, '4': _FLOAT,
        '6': {'type': 'message', 'name': '', 'message_typedef': {'1': _INT, '2': _FLOAT}},
        '7': _LATLNG}},
    '7': _INT,
}
_FREQUENT_PLACES = {'1': {'type': 'message', 'name': '', 'message_typedef': {
    '1': _LATLNG, '2': _INT}}}
# type 1, 2 and 4 rows hold the wrapper with the segment in field 1; type 3 with the list in 2
_WRAPPER = {
    '1': {'type': 'message', 'name': '', 'message_typedef': _SEGMENT},
    '2': {'type': 'message', 'name': '', 'message_typedef': _FREQUENT_PLACES},
}
# type 5 rows hold a raw signal record directly
_RAW_SIGNAL = {'1': {'type': 'message', 'name': '', 'message_typedef': {
    '1': {'type': 'message', 'name': '', 'message_typedef': {
        '1': _INT, '2': _INT, '3': _INT, '4': _FLOAT, '5': _INT, '6': _INT, '7': _FLOAT}},
    '2': {'type': 'message', 'name': '', 'message_typedef': {'1': _INT}},
    '3': {'type': 'message', 'name': '', 'message_typedef': {
        '2': _INT, '3': {'type': 'packed_int', 'name': ''},
        '4': {'type': 'packed_float', 'name': ''}}},
}}}

_FINALIZATION = {0: 'UNSPECIFIED_FINALIZATION_STATUS', 1: 'STABILIZED', 2: 'FINALIZED'}
_SEMANTIC_TYPES = {0: 'UNKNOWN', 1: 'HOME', 2: 'WORK', 3: 'INFERRED_HOME', 4: 'INFERRED_WORK',
                   5: 'SEARCHED_ADDRESS', 6: 'ALIASED_LOCATION'}
_ACTIVITY_TYPES = {0: 'UNKNOWN_ACTIVITY_TYPE', 1: 'STILL', 2: 'WALKING', 3: 'CYCLING',
                   5: 'FLYING', 6: 'RUNNING', 7: 'IN_BUS', 8: 'IN_TRAIN', 9: 'IN_SUBWAY',
                   10: 'IN_TRAM', 11: 'IN_FERRY', 18: 'SAILING', 20: 'SKIING',
                   29: 'IN_PASSENGER_VEHICLE', 30: 'MOTORCYCLING'}
_PLACE_LABELS = {0: 'UNKNOWN_TYPE', 1: 'HOME', 2: 'WORK'}
_POSITION_SOURCES = {0: 'UNKNOWN', 1: 'GPS', 2: 'CELL', 3: 'WIFI', 4: 'WIFI_ONLY'}
_RAW_ACTIVITY_TYPES = {0: 'IN_VEHICLE', 1: 'ON_BICYCLE', 2: 'ON_FOOT', 3: 'STILL', 4: 'UNKNOWN',
                       5: 'TILTING', 6: 'EXITING_VEHICLE', 7: 'WALKING', 8: 'RUNNING',
                       9: 'IN_ROAD_VEHICLE', 10: 'IN_RAIL_VEHICLE',
                       11: 'IN_TWO_WHEELER_VEHICLE'}
_DECODE_ERRORS = (ValueError, KeyError, TypeError, IndexError, EOFError)
_QUERY = 'SELECT id, type, creation_time_seconds, data FROM TransientDataEntity ORDER BY id'


def _as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _as_dict(value):
    if isinstance(value, list):
        value = value[0] if value else {}
    return value if isinstance(value, dict) else {}


def _name(names, value):
    if not isinstance(value, int):
        return ''
    return names.get(value, f'Unknown ({value})')


def _utc(seconds):
    if not isinstance(seconds, (int, float)) or seconds <= 0:
        return ''
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _timestamp(value):
    value = _as_dict(value)
    seconds = value.get('1')
    if not isinstance(seconds, int):
        return ''
    nanos = value.get('2') if isinstance(value.get('2'), int) else 0
    return _utc(seconds + nanos / 1e9)


def _ms(value):
    return _utc(value / 1000) if isinstance(value, int) else ''


def _latlng(value):
    value = _as_dict(value)
    lat, lng = value.get('1'), value.get('2')
    if not isinstance(lat, int) or not isinstance(lng, int):
        return '', ''
    return lat / 1e7, lng / 1e7


def _num(value):
    return value if isinstance(value, (int, float)) else ''


def _databases(context):
    """Every staged copy of the database, as (path, relative path)."""
    return [(str(found), context.get_relative_path(str(found))) for found in unique_files(context)
            if os.path.basename(str(found)) == _DB_NAME]


def _db_rows(databases):
    """Yield (relative source, row type, row written, data) for every row of every database."""
    for path, rel in databases:
        for row in get_sqlite_db_records(path, _QUERY):
            yield rel, row[1], row[2], row[3]


def _decode(data, typedef, label, counts):
    if not data:
        return None
    try:
        message, _ = decode_message(data, typedef)
    except _DECODE_ERRORS as error:
        counts[label] = counts.get(label, 0) + 1
        logfunc(f'Semantic Location Transient: could not decode a type {label} row: '
                f'{type(error).__name__}')
        return None
    return message


def _segments(context, wanted):
    databases = _databases(context)
    sources, rows, counts = [path for path, _ in databases], [], {}
    for rel, row_type, written, data in _db_rows(databases):
        if row_type != wanted:
            continue
        message = _decode(data, _WRAPPER, wanted, counts)
        segment = _as_dict(_as_dict(message).get('1')) if message else {}
        if not segment:
            continue
        rows.append((rel, written, segment))
    return sources, rows


def _finish(headers, data_list, sources):
    """Add Source File only when this artifact's rows come from more than one database."""
    if len({row[-1] for row in data_list}) > 1:
        headers = headers + ('Source File',)
    else:
        data_list = [row[:-1] for row in data_list]
    return headers, data_list, '\n'.join(sources)


@artifact_processor
def gms_semloc_transient_visits(context):
    headers = (('Start Time', 'datetime'), ('End Time', 'datetime'), ('Row Written', 'datetime'),
               'Start UTC Offset (min)', 'End UTC Offset (min)', ('Latitude', 'latitude'),
               ('Longitude', 'longitude'), 'Semantic Type', 'Place Probability',
               'Visit Probability', 'Hierarchy Level', 'Finalization Status')
    sources, rows = _segments(context, 1)
    data_list = []
    for rel, written, segment in rows:
        visit = _as_dict(segment.get('5'))
        top = _as_dict(visit.get('3'))
        lat, lng = _latlng(top.get('4'))
        data_list.append((
            _timestamp(segment.get('1')), _timestamp(segment.get('2')), _utc(written),
            _num(segment.get('3')), _num(segment.get('4')), lat, lng,
            _name(_SEMANTIC_TYPES, top.get('2', 0)), _num(top.get('3')), _num(visit.get('2')),
            _num(visit.get('1', 0)), _name(_FINALIZATION, segment.get('7', 0)), rel,
        ))
    return _finish(headers, data_list, sources)


@artifact_processor
def gms_semloc_transient_activities(context):
    headers = (('Start Time', 'datetime'), ('End Time', 'datetime'), ('Row Written', 'datetime'),
               'Start UTC Offset (min)', 'End UTC Offset (min)', 'Activity Type',
               'Activity Type Probability', 'Segment Probability', 'Distance (m)',
               ('Start Latitude', 'latitude'), ('Start Longitude', 'longitude'),
               ('End Latitude', 'latitude'), ('End Longitude', 'longitude'),
               ('Parking Latitude', 'latitude'), ('Parking Longitude', 'longitude'),
               'Finalization Status')
    sources, rows = _segments(context, 2)
    data_list = []
    for rel, written, segment in rows:
        activity = _as_dict(segment.get('6'))
        top = _as_dict(activity.get('6'))
        start = _latlng(activity.get('1'))
        end = _latlng(activity.get('2'))
        parking = _latlng(activity.get('7'))
        data_list.append((
            _timestamp(segment.get('1')), _timestamp(segment.get('2')), _utc(written),
            _num(segment.get('3')), _num(segment.get('4')),
            _name(_ACTIVITY_TYPES, top.get('1', 0)) if top else '', _num(top.get('2')),
            _num(activity.get('4')), _num(activity.get('3')), *start, *end, *parking,
            _name(_FINALIZATION, segment.get('7', 0)), rel,
        ))
    return _finish(headers, data_list, sources)


@artifact_processor
def gms_semloc_transient_frequent_places(context):
    headers = (('Row Written', 'datetime'), 'Label', ('Latitude', 'latitude'),
               ('Longitude', 'longitude'))
    databases = _databases(context)
    sources, data_list, counts = [path for path, _ in databases], [], {}
    for rel, row_type, written, data in _db_rows(databases):
        if row_type != 3:
            continue
        message = _decode(data, _WRAPPER, 3, counts)
        places = _as_dict(_as_dict(message).get('2')) if message else {}
        for place in _as_list(places.get('1')):
            if not isinstance(place, dict):
                continue
            lat, lng = _latlng(place.get('1'))
            data_list.append((_utc(written), _name(_PLACE_LABELS, place.get('2', 0)), lat, lng,
                              rel))
    return _finish(headers, data_list, sources)


def _raw_signals(context, kind):
    databases = _databases(context)
    sources, rows, counts = [path for path, _ in databases], [], {}
    for rel, row_type, written, data in _db_rows(databases):
        if row_type != 5:
            continue
        message = _decode(data, _RAW_SIGNAL, 5, counts)
        record = _as_dict(_as_dict(message).get('1')) if message else {}
        if record.get(kind) is not None:
            rows.append((rel, written, _as_dict(record.get(kind))))
    return sources, rows


@artifact_processor
def gms_semloc_transient_positions(context):
    headers = (('Timestamp', 'datetime'), ('Row Written', 'datetime'), ('Latitude', 'latitude'),
               ('Longitude', 'longitude'), 'Accuracy (m)', 'Altitude (m)', 'Source',
               'Speed (m/s)')
    sources, rows = _raw_signals(context, '1')
    data_list = []
    for rel, written, position in rows:
        lat, lng = ('', '')
        if isinstance(position.get('1'), int) and isinstance(position.get('2'), int):
            lat, lng = position['1'] / 1e7, position['2'] / 1e7
        accuracy = position.get('3')
        data_list.append((
            _ms(position.get('6')), _utc(written), lat, lng,
            accuracy / 1000 if isinstance(accuracy, int) else '', _num(position.get('4')),
            _name(_POSITION_SOURCES, position.get('5')) if '5' in position else '',
            _num(position.get('7')), rel,
        ))
    return _finish(headers, data_list, sources)


@artifact_processor
def gms_semloc_transient_activity_records(context):
    headers = (('Timestamp', 'datetime'), ('Row Written', 'datetime'), 'Top Activity',
               'Top Confidence', 'Probable Activities')
    sources, rows = _raw_signals(context, '3')
    data_list = []
    for rel, written, record in rows:
        types = _as_list(record.get('3'))
        confidences = _as_list(record.get('4'))
        pairs = [(_name(_RAW_ACTIVITY_TYPES, kind), conf)
                 for kind, conf in zip(types, confidences)
                 if isinstance(kind, int) and isinstance(conf, float)]
        top_name, top_conf = max(pairs, key=lambda pair: pair[1]) if pairs else ('', '')
        listing = ', '.join(f'{name} {conf:.3g}' for name, conf in pairs)
        data_list.append((_ms(record.get('2')), _utc(written), top_name, top_conf, listing, rel))
    return _finish(headers, data_list, sources)

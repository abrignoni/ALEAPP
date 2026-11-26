import datetime
import hashlib
import os
import re
import sqlite3
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

__artifacts_v2__ = {
    "adServicesMeasurementSources": {
        "name": "AdServices - Attribution Sources",
        "description": "Rows of the msmt_source table of adservices_msmt.db (Android AdServices, Privacy Sandbox Attribution Reporting): event and expiry times converted to UTC, publisher, registering app, source type, app and web destinations, registration origin, enrollment ID and status, one row per source.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "adservices_msmt.db is the Attribution Reporting database of the AdServices module (package com.google.android.adservices.api; com.android.adservices.api is also matched, but no image read had it, so that path is unexercised). Table and column names are from MeasurementTables at AOSP commit 593832a5 (https://android.googlesource.com/platform/packages/modules/AdServices/+/593832a5beabbc740974dc6c07f3294cd8a3bc6d/adservices/service-core/java/com/android/adservices/data/measurement/MeasurementTables.java#104 for msmt_source, #159 for msmt_source_destination, #183 for msmt_trigger). The images ran other module builds (database schema versions 8 to 50; the commit is version 45, https://android.googlesource.com/platform/packages/modules/AdServices/+/593832a5beabbc740974dc6c07f3294cd8a3bc6d/adservices/service-core/java/com/android/adservices/data/measurement/MeasurementDbHelper.java#88). A column a build lacks is read as blank; on the images read only registration_origin was missing, on two databases with no rows, so no reported row used this path. Each copy of the database is read: the live one under the package's data folder and any copy under data/misc_ce/<n>/rollback/<id>/<package>/, shown in Copy as live or rollback <id>. A row present in several copies with the same values is shown once with every copy listed. Byte-identical storage views (data/data, data/user/0, data_mirror) are read once. Android User is n from data/user/<n>, data/user_de/<n>, userdata/user/<n>, data_mirror/data_ce/<volume>/<n> or data/misc_ce/<n>, 0 under data/data or userdata/data, otherwise blank, and a store with a blank Android User is never merged with another path's store. A folder tree with the same database under data/data and data/user/0, a changed copy under data/user/10 with one source and one trigger removed, and a copy under another package name gave exactly the single-copy rows plus the user 10 rows, and nothing from the other package. The report and attribution tables (msmt_event_report, msmt_attribution, msmt_aggregate_report) had no rows on any image, so they are not reported; nor are msmt_aggregate_encryption_key (keys, 5 rows on 5 images) and msmt_async_registration_contract (4 queued registration requests in a rollback copy on falken_a326u_a13). The platform_ad_id column is not shown: on the seven images where it was filled (six in msmt_source, two in msmt_trigger) it held one value per image, equal on all seven to adid_key in Play services' adid_settings.xml on the same image (AOSP describes it as the AdID from an app registration, https://android.googlesource.com/platform/packages/modules/AdServices/+/593832a5beabbc740974dc6c07f3294cd8a3bc6d/adservices/service-core/java/com/android/adservices/service/measurement/registration/AsyncRegistration.java#207). The other AdServices stores are left out: the topics tables in adservices.db and data/system/adservices_topics.db (topics_epoch_origin held 1 row on 11 real-device images and on the emulator known data, and every other topics table was empty), enrollment_data, which adservices.db held on three images and adservices_shared.db on 11 (90 to 99 rows there; its columns are enrollment and company IDs, SDK names and registration, reporting and key URLs, https://android.googlesource.com/platform/packages/modules/AdServices/+/593832a5beabbc740974dc6c07f3294cd8a3bc6d/adservices/service-core/java/com/android/adservices/data/enrollment/EnrollmentTables.java#29), customaudience.db, adselection.db and adselectionserver.db (no rows) and cobalt_db (not reported). The emulator known data (emu_a15_adservices_on_known_20261116, emu_a15_adservices_topicsoff_known_20261116) has an adservices_msmt.db with no rows and a 0-byte adservices_shared.db; why no rows were written there is not established, so the rows reported come only from the real-device images. One row per distinct msmt_source row across the copies; Source ID is _id. Event Time (UTC) and Expiry Time (UTC) are event_time and expiry_time read as milliseconds since 1970. Publisher is publisher, Publisher Type is publisher_type with its EventSurfaceType name (https://android.googlesource.com/platform/packages/modules/AdServices/+/593832a5beabbc740974dc6c07f3294cd8a3bc6d/adservices/service-core/java/com/android/adservices/service/measurement/EventSurfaceType.java#27: 0 App, 1 Web), Registrant is registrant, Source Type is source_type as stored (https://android.googlesource.com/platform/packages/modules/AdServices/+/593832a5beabbc740974dc6c07f3294cd8a3bc6d/adservices/service-core/java/com/android/adservices/service/measurement/Source.java#454 defines EVENT and NAVIGATION), App Destinations and Web Destinations are the msmt_source_destination rows of that source with destination_type 0 and 1, one per line (a repeated destination is listed once), Registration Origin is registration_origin, Enrollment ID is enrollment_id and Status is status with its Source.Status name (https://android.googlesource.com/platform/packages/modules/AdServices/+/593832a5beabbc740974dc6c07f3294cd8a3bc6d/adservices/service-core/java/com/android/adservices/service/measurement/Source.java#406: 0 ACTIVE, 1 IGNORED, 2 MARKED_TO_DELETE). Cross-check with Chrome: every one of the 38 sources whose Publisher Type was Web (32 on russell_a14, 4 on kevin_pocox7_a15, 1 on anne_a15, 1 on sharon_a14; 5 distinct publisher hosts) had a visit to the publisher's host (exact host match) in that image's Chrome History, 35 of them 1.4 to 39.3 seconds before Event Time (UTC), 2 about 650 seconds before and 1 1.6 seconds after. This agrees with reading the time as milliseconds, and with the publisher being the site the source was registered from. For an app registration AOSP passes the registering app as both the registrant and the top origin (https://android.googlesource.com/platform/packages/modules/AdServices/+/593832a5beabbc740974dc6c07f3294cd8a3bc6d/adservices/service-core/java/com/android/adservices/service/measurement/registration/EnqueueAsyncRegistration.java#64), and Publisher and Registrant were identical on all 58 rows whose Publisher Type is App. That a source was registered does not show that anyone looked at or clicked the ad. Source Type and Status are reported as stored and not tested further. On russell_a14 all 32 sources were only in a rollback copy; the live database held none. Uniform per image, varying across images: Android User held 0 on every row of every image; Status held ACTIVE (0) on all 96 rows; Copy held live on every image except russell_a14 (one rollback copy on all 32 rows); App Destinations was empty on all rows of russell_a14; Publisher, Publisher Type, Registrant, Source Type, Registration Origin and Enrollment ID were each one value on all rows of russell_a14, and Publisher Type, Source Type, Registration Origin and Enrollment ID were one value on all rows of pixel7a_a14.",
        "paths": ('*/com.google.android.adservices.api/databases/adservices_msmt.db*',
                  '*/com.android.adservices.api/databases/adservices_msmt.db*'),
        "output_types": "standard",
        "artifact_icon": "target",
        "sample_data": {
            "russell_a14": "Android 14 | 32 rows (all in a rollback copy)",
            "kevin_pocox7_a15": "Android 15 | 20 rows",
            "anne_a15": "Android 15 | 18 rows",
            "samsunga53_a14": "Android 14 | 14 rows",
            "falken_a326u_a13": "Android 13 | 7 rows",
            "pixel7a_a14": "Android 14 | 3 rows",
            "adams_ss135dl_a13": "Android 13 | 1 row",
            "sharon_a14": "Android 14 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | 0 rows (msmt_source empty)",
            "hc_pixel8pro_a17": "Android 17 | 0 rows (msmt_source empty)",
            "s20fe_a13": "Android 13 | 0 rows (msmt_source empty)",
            "userb2_a13": "Android 13 | 0 rows (msmt_source empty)",
            "emu_a15_adservices_on_known_20261116": "Android 15 emulator | 0 rows (known data; msmt_source empty)",
        },
    },
    "adServicesMeasurementTriggers": {
        "name": "AdServices - Attribution Triggers",
        "description": "Rows of the msmt_trigger table of adservices_msmt.db (Android AdServices, Privacy Sandbox Attribution Reporting): trigger time converted to UTC, attribution destination, registering app, registration origin, enrollment ID and status, one row per trigger.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "adservices_msmt.db is the Attribution Reporting database of the AdServices module (package com.google.android.adservices.api; com.android.adservices.api is also matched, but no image read had it, so that path is unexercised). Table and column names are from MeasurementTables at AOSP commit 593832a5 (https://android.googlesource.com/platform/packages/modules/AdServices/+/593832a5beabbc740974dc6c07f3294cd8a3bc6d/adservices/service-core/java/com/android/adservices/data/measurement/MeasurementTables.java#104 for msmt_source, #159 for msmt_source_destination, #183 for msmt_trigger). The images ran other module builds (database schema versions 8 to 50; the commit is version 45, https://android.googlesource.com/platform/packages/modules/AdServices/+/593832a5beabbc740974dc6c07f3294cd8a3bc6d/adservices/service-core/java/com/android/adservices/data/measurement/MeasurementDbHelper.java#88). A column a build lacks is read as blank; on the images read only registration_origin was missing, on two databases with no rows, so no reported row used this path. Each copy of the database is read: the live one under the package's data folder and any copy under data/misc_ce/<n>/rollback/<id>/<package>/, shown in Copy as live or rollback <id>. A row present in several copies with the same values is shown once with every copy listed. Byte-identical storage views (data/data, data/user/0, data_mirror) are read once. Android User is n from data/user/<n>, data/user_de/<n>, userdata/user/<n>, data_mirror/data_ce/<volume>/<n> or data/misc_ce/<n>, 0 under data/data or userdata/data, otherwise blank, and a store with a blank Android User is never merged with another path's store. A folder tree with the same database under data/data and data/user/0, a changed copy under data/user/10 with one source and one trigger removed, and a copy under another package name gave exactly the single-copy rows plus the user 10 rows, and nothing from the other package. The report and attribution tables (msmt_event_report, msmt_attribution, msmt_aggregate_report) had no rows on any image, so they are not reported; nor are msmt_aggregate_encryption_key (keys, 5 rows on 5 images) and msmt_async_registration_contract (4 queued registration requests in a rollback copy on falken_a326u_a13). The platform_ad_id column is not shown: on the seven images where it was filled (six in msmt_source, two in msmt_trigger) it held one value per image, equal on all seven to adid_key in Play services' adid_settings.xml on the same image (AOSP describes it as the AdID from an app registration, https://android.googlesource.com/platform/packages/modules/AdServices/+/593832a5beabbc740974dc6c07f3294cd8a3bc6d/adservices/service-core/java/com/android/adservices/service/measurement/registration/AsyncRegistration.java#207). The other AdServices stores are left out: the topics tables in adservices.db and data/system/adservices_topics.db (topics_epoch_origin held 1 row on 11 real-device images and on the emulator known data, and every other topics table was empty), enrollment_data, which adservices.db held on three images and adservices_shared.db on 11 (90 to 99 rows there; its columns are enrollment and company IDs, SDK names and registration, reporting and key URLs, https://android.googlesource.com/platform/packages/modules/AdServices/+/593832a5beabbc740974dc6c07f3294cd8a3bc6d/adservices/service-core/java/com/android/adservices/data/enrollment/EnrollmentTables.java#29), customaudience.db, adselection.db and adselectionserver.db (no rows) and cobalt_db (not reported). The emulator known data (emu_a15_adservices_on_known_20261116, emu_a15_adservices_topicsoff_known_20261116) has an adservices_msmt.db with no rows and a 0-byte adservices_shared.db; why no rows were written there is not established, so the rows reported come only from the real-device images. One row per distinct msmt_trigger row across the copies; Trigger ID is _id. Trigger Time (UTC) is trigger_time read as milliseconds since 1970, the unit established for event_time in AdServices - Attribution Sources; trigger_time itself was not cross-checked against another record. Attribution Destination is attribution_destination, Destination Type is destination_type with its EventSurfaceType name (https://android.googlesource.com/platform/packages/modules/AdServices/+/593832a5beabbc740974dc6c07f3294cd8a3bc6d/adservices/service-core/java/com/android/adservices/service/measurement/EventSurfaceType.java#27: 0 App, 1 Web), Registrant is registrant, Registration Origin is registration_origin, Enrollment ID is enrollment_id and Status is status with its Trigger.Status name (https://android.googlesource.com/platform/packages/modules/AdServices/+/593832a5beabbc740974dc6c07f3294cd8a3bc6d/adservices/service-core/java/com/android/adservices/service/measurement/Trigger.java#95: 0 PENDING, 1 IGNORED, 2 ATTRIBUTED, 3 MARKED_TO_DELETE), reported as stored and not tested further. That a trigger was registered by an app or site does not show what the person did there. On russell_a14 the live database held 29 triggers and a rollback copy 43; 28 were in both with the same values, so 44 rows are shown, 15 only in the rollback copy. Uniform per image, varying across images: Android User held 0 on every row of every image; Status held IGNORED (1) on all 146 rows; Destination Type held App (0) on every row of russell_a14 and pixel7a_a14 and Web (1) on samsunga53_a14, kevin_pocox7_a15 and sharon_a14; Copy held live on all rows of every image except russell_a14; Attribution Destination, Registrant, Registration Origin and Enrollment ID were each one value on all rows of kevin_pocox7_a15, and Attribution Destination and Registrant were one value on all rows of samsunga53_a14. Attribution Destination and Registrant were identical on all 127 rows whose Destination Type is App; for an app registration AOSP passes the registering app as both the registrant and the top origin (https://android.googlesource.com/platform/packages/modules/AdServices/+/593832a5beabbc740974dc6c07f3294cd8a3bc6d/adservices/service-core/java/com/android/adservices/service/measurement/registration/EnqueueAsyncRegistration.java#64).",
        "paths": ('*/com.google.android.adservices.api/databases/adservices_msmt.db*',
                  '*/com.android.adservices.api/databases/adservices_msmt.db*'),
        "output_types": "standard",
        "artifact_icon": "crosshair",
        "sample_data": {
            "pixel7a_a14": "Android 14 | 83 rows",
            "russell_a14": "Android 14 | 44 rows (15 only in a rollback copy)",
            "samsunga53_a14": "Android 14 | 12 rows",
            "kevin_pocox7_a15": "Android 15 | 4 rows",
            "sharon_a14": "Android 14 | 3 rows",
            "anne_a15": "Android 15 | 0 rows (msmt_trigger empty)",
            "falken_a326u_a13": "Android 13 | 0 rows (msmt_trigger empty)",
            "adams_ss135dl_a13": "Android 13 | 0 rows (msmt_trigger empty)",
            "hc_pixel8pro_a16": "Android 16 | 0 rows (msmt_trigger empty)",
            "hc_pixel8pro_a17": "Android 17 | 0 rows (msmt_trigger empty)",
            "s20fe_a13": "Android 13 | 0 rows (msmt_trigger empty)",
            "userb2_a13": "Android 13 | 0 rows (msmt_trigger empty)",
            "emu_a15_adservices_on_known_20261116": "Android 15 emulator | 0 rows (known data; msmt_trigger empty)",
        },
    },
    "adServicesConsent": {
        "name": "AdServices - Ad Privacy Consent",
        "description": "Keys and values of the AdServices consent stores (ConsentManagerStorageIdentifier.xml) kept by the AdServices system service under data/system/adservices/<user>/consent and by the AdServices app under its files folder, one row per key, values as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "Two stores hold the Ad privacy consent of AdServices: the system service's ConsentManagerStorageIdentifier.xml under data/system/adservices/<user>/consent (https://android.googlesource.com/platform/packages/modules/AdServices/+/593832a5beabbc740974dc6c07f3294cd8a3bc6d/adservices/service/java/com/android/server/adservices/consent/ConsentManager.java#97 gives the per-user folder, #67 names the file) and the AdServices app's own copy of the same name under its files folder (https://android.googlesource.com/platform/packages/modules/AdServices/+/593832a5beabbc740974dc6c07f3294cd8a3bc6d/adservices/service-core/java/com/android/adservices/service/consent/ConsentConstants.java#54; package com.google.android.adservices.api; com.android.adservices.api is also matched, but no image read had it). Both are plain XML on every image read (45 files on 14 images and 4 in the known data, first bytes '<bun'). One row per element: Key is its name, Value its value as stored, Value Type its element name (boolean and int on the images read). API names the consent a key holds where AOSP defines it at commit 593832a5: in the system service's store the key is CONSENT_API_TYPE_ followed by a ConsentParcel type (https://android.googlesource.com/platform/packages/modules/AdServices/+/593832a5beabbc740974dc6c07f3294cd8a3bc6d/adservices/service/java/com/android/server/adservices/consent/ConsentManager.java#63 and #522; https://android.googlesource.com/platform/packages/modules/AdServices/+/593832a5beabbc740974dc6c07f3294cd8a3bc6d/adservices/framework/java/android/app/adservices/consent/ConsentParcel.java#46 to #55: 1 ALL_API, 2 TOPICS, 3 FLEDGE, 4 MEASUREMENT); in the app's store CONSENT, CONSENT-TOPICS, CONSENT-FLEDGE and CONSENT-MEASUREMENT are AdServicesApiType keys (https://android.googlesource.com/platform/packages/modules/AdServices/+/593832a5beabbc740974dc6c07f3294cd8a3bc6d/adservices/service-core/java/com/android/adservices/service/consent/AdServicesApiType.java#32 to #37), whose names include MEASUREMENTS; both spellings are AOSP's. Other keys are reported without a name. A copy under data/misc_ce/<n>/rollback/<id>/ is shown with Copy rollback <id>; byte-identical storage views (data/data, data/user/0, data_mirror) are read once. Android User is n from data/system/adservices/<n>, data/user/<n>, userdata/user/<n>, data_mirror/data_ce/<volume>/<n> or data/misc_ce/<n>, 0 under data/data or userdata/data, otherwise blank, and a store with a blank Android User is never merged with another path's store (samsungs20_a13 holds a second user, 150, in both stores). Known data on an Android 15 emulator signed in to a Google account recorded as a test account in the mint record (emu_a15_adservices_on_known_20261116 and emu_a15_adservices_topicsoff_known_20261116, times in the mint log): the mint log records every AdServices folder as empty before any change (that state was not captured). After Ad topics, App-suggested ads and Ad measurement were turned On in Settings, CONSENT_API_TYPE_1 to _4 were true in the system service's store, CONSENT-TOPICS, CONSENT-FLEDGE and CONSENT-MEASUREMENT were true in the app's store, and MANUAL_INTERACTION_WITH_CONSENT_RECORDED was true in both. In the second capture, taken after Ad topics was turned Off and Reset measurement data was then pressed, CONSENT_API_TYPE_2 and CONSENT_API_TYPE_1 were false in the system service's store and CONSENT-TOPICS false in the app's, while the app's CONSENT changed from false to true, so the two stores do not agree on ALL_API and each is read as stored; IS_MEASUREMENT_DATA_RESET, absent in the first capture, was true in both (https://android.googlesource.com/platform/packages/modules/AdServices/+/593832a5beabbc740974dc6c07f3294cd8a3bc6d/adservices/service-core/java/com/android/adservices/service/consent/ConsentConstants.java#104). The three settings were turned On together, so which key follows App-suggested ads and which Ad measurement was not separated. No key in either file held a time on the images read. On the real-device images MANUAL_INTERACTION_WITH_CONSENT_RECORDED was false on all 28 rows that hold it, while CONSENT-TOPICS, CONSENT-FLEDGE and CONSENT-MEASUREMENT were true wherever present and CONSENT_API_TYPE_1 to _4 were true except on s20fe_a13 and samsungs20_a13, where all four were false. A true consent value with that key false is not evidence that anyone turned a setting On. Left out, in the same folders: adservices.uxstates.xml (booleans named for UX channels), AdserviceStatusSharedPreference.xml (a long named firstEntryRequestTimestamp, whose meaning is not established, and an int), PPAPI_Consent.xml and PPAPI_Blocked_Topics.xml (one migration flag each), adservices.appconsent.xml (a version number on the images read), MeasurementRollbackHandlingStorageIdentifier.xml, PPAPI_Background_Jobs.xml, adservices_enrollment.xml and user_profile_id.xml. Android User held 0 and Copy held live on every row of 10 of the 16 images.",
        "paths": ('*/system/adservices/*/consent/ConsentManagerStorageIdentifier.xml',
                  '*/com.google.android.adservices.api/files/ConsentManagerStorageIdentifier.xml',
                  '*/com.android.adservices.api/files/ConsentManagerStorageIdentifier.xml'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "shield",
        "sample_data": {
            "emu_a15_adservices_on_known_20261116": "Android 15 emulator | 21 rows (known data)",
            "emu_a15_adservices_topicsoff_known_20261116": "Android 15 emulator | 23 rows (known data)",
            "russell_a14": "Android 14 | 119 rows",
            "falken_a326u_a13": "Android 13 | 80 rows",
            "hc_pixel8pro_a17": "Android 17 | 72 rows",
            "adams_ss135dl_a13": "Android 13 | 62 rows",
            "pixel7a_a14": "Android 14 | 59 rows",
            "sharon_a14": "Android 14 | 59 rows",
            "anne_a15": "Android 15 | 52 rows",
            "hc_pixel8pro_a16": "Android 16 | 52 rows",
            "kevin_pocox7_a15": "Android 15 | 52 rows",
            "userb2_a13": "Android 13 | 49 rows",
            "samsunga53_a14": "Android 14 | 47 rows",
            "emu_a15_oss_v17": "Android 15 emulator | 30 rows",
            "samsungs20_a13": "Android 13 | 28 rows",
            "s20fe_a13": "Android 13 | 19 rows",
        },
    },
}

_PACKAGES = ('com.google.android.adservices.api', 'com.android.adservices.api')
_USER_PATTERNS = (
    re.compile(r'/data/user(?:_de)?/(\d+)/'),
    re.compile(r'/userdata/user(?:_de)?/(\d+)/'),
    re.compile(r'/data_mirror/data_(?:ce|de)/[^/]+/(\d+)/'),
    re.compile(r'/misc_ce/(\d+)/rollback/'),
    re.compile(r'/system/adservices/(\d+)/consent/'),
)
_ROLLBACK = re.compile(r'/misc_ce/\d+/rollback/(\d+)/')

# EventSurfaceType: APP = 0, WEB = 1
_SURFACE = {0: 'App', 1: 'Web'}
# Source.Status: ACTIVE = 0, IGNORED = 1, MARKED_TO_DELETE = 2
_SOURCE_STATUS = {0: 'ACTIVE', 1: 'IGNORED', 2: 'MARKED_TO_DELETE'}
# Trigger.Status: PENDING = 0, IGNORED = 1, ATTRIBUTED = 2, MARKED_TO_DELETE = 3
_TRIGGER_STATUS = {0: 'PENDING', 1: 'IGNORED', 2: 'ATTRIBUTED', 3: 'MARKED_TO_DELETE'}
# ConsentParcel API types, used by the system service as CONSENT_API_TYPE_<n>
_CONSENT_PARCEL = {'1': 'ALL_API', '2': 'TOPICS', '3': 'FLEDGE', '4': 'MEASUREMENT'}
# AdServicesApiType keys in the AdServices app's own store
_APP_API_KEYS = {'CONSENT': 'ALL_API', 'CONSENT-TOPICS': 'TOPICS', 'CONSENT-FLEDGE': 'FLEDGE',
                 'CONSENT-MEASUREMENT': 'MEASUREMENTS'}


def _norm(path):
    return '/' + path.replace(os.sep, '/').lstrip('/')


def _ms_to_utc(value):
    if not isinstance(value, int) or value <= 0:
        return None
    try:
        return datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(milliseconds=value)
    except OverflowError:
        return None


def _android_user(rel_path):
    '''n for a path under a per-user folder, 0 under data/data, else blank; rel_path is evidence-relative.'''
    norm = _norm(rel_path)
    for pattern in _USER_PATTERNS:
        match = pattern.search(norm)
        if match:
            return int(match.group(1))
    return 0 if ('/data/data/' in norm or '/userdata/data/' in norm) else ''


def _copy(rel_path):
    match = _ROLLBACK.search(_norm(rel_path))
    return f'rollback {match.group(1)}' if match else 'live'


def _in_package(path, leaf_dir):
    norm = _norm(path)
    return any(f'/{pkg}/{leaf_dir}/' in norm for pkg in _PACKAGES)


def _labelled(value, names):
    if value is None:
        return ''
    name = names.get(value)
    return f'{name} ({value})' if name else str(value)


def _digest(paths):
    sha = hashlib.sha1()
    for path in paths:
        try:
            with open(path, 'rb') as handle:
                sha.update(handle.read())
        except OSError as ex:
            logfunc(f'AdServices: could not hash {path}: {ex}')
            sha.update(path.encode('utf-8', 'replace'))
        sha.update(b'\0')
    return sha.hexdigest()


def _unique(context, candidates, sidecar=False):
    '''Each store once per (user, copy): byte-identical storage views (data/data, data/user/0, data_mirror) are read once.'''
    seen = set()
    found = []
    order = sorted(candidates, key=lambda p: ('/data/data/' not in _norm(p), _norm(p)))
    for path in order:
        rel = context.get_relative_path(path)
        parts = [path] + ([path + '-wal'] if sidecar and os.path.exists(path + '-wal') else [])
        user = _android_user(rel)
        # A store whose user is not known is never merged with another path's store.
        key = (user if user != '' else _norm(rel), _copy(rel), _digest(parts))
        if key not in seen:
            seen.add(key)
            found.append((path, rel))
    return found


def _measurement_dbs(context):
    candidates = [p for p in context.get_files_found()
                  if _norm(p).endswith('/adservices_msmt.db') and _in_package(p, 'databases')]
    return _unique(context, candidates, sidecar=True)


def _columns(db, table):
    return {row[1] for row in db.execute(f'PRAGMA table_info("{table}")')}


def _merge(rows_by_key, key, values, copy):
    if key in rows_by_key:
        if copy not in rows_by_key[key][1]:
            rows_by_key[key][1].append(copy)
    else:
        rows_by_key[key] = (values, [copy])


def _read_table(context, label, table, wanted, extra=None):
    '''Rows of table from every measurement database, one per (user, _id, values), with the copies that hold it.'''
    rows_by_key = {}
    sources = []
    for path, rel in _measurement_dbs(context):
        db = open_sqlite_db_readonly(path)
        if db is None:
            logfunc(f'{label}: could not open {path}')
            continue
        sources.append(path)
        try:
            if table not in {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}:
                logfunc(f'{label}: no {table} table in {path}')
                continue
            present = _columns(db, table)
            select = ', '.join(c if c in present else 'NULL' for c in wanted)
            extras = extra(db) if extra else {}
            user = _android_user(rel)
            for row in db.execute(f'SELECT {select} FROM "{table}"'):
                values = tuple(row) + (extras.get(row[0], ('', '')) if extra else ())
                _merge(rows_by_key, (user, row[0], values), (user, values), _copy(rel))
        except sqlite3.Error as ex:
            logfunc(f'{label}: could not read {path}: {ex}')
        finally:
            db.close()
    return list(rows_by_key.values()), '\n'.join(sources)


def _destinations(db):
    '''source_id -> (app destinations, web destinations) from msmt_source_destination.'''
    if 'msmt_source_destination' not in {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}:
        return {}
    grouped = {}
    for source_id, dest_type, dest in db.execute(
            'SELECT source_id, destination_type, destination FROM msmt_source_destination ORDER BY rowid'):
        app, web = grouped.setdefault(source_id, ([], []))
        bucket = app if dest_type == 0 else web if dest_type == 1 else None
        if bucket is None:
            web.append(f'{dest} (type {dest_type})')
        elif dest not in bucket:
            bucket.append(dest)
    return {k: ('\n'.join(a), '\n'.join(w)) for k, (a, w) in grouped.items()}


def _v(value):
    return '' if value is None else value


@artifact_processor
def adServicesMeasurementSources(context):
    wanted = ('_id', 'event_time', 'expiry_time', 'publisher', 'publisher_type', 'registrant', 'source_type',
              'registration_origin', 'enrollment_id', 'status')
    rows, source = _read_table(context, 'AdServices - Attribution Sources', 'msmt_source', wanted, _destinations)
    data_list = []
    for (user, values), copies in rows:
        (row_id, event_time, expiry, publisher, pub_type, registrant, source_type, origin, enrollment, status,
         app_dest, web_dest) = values
        data_list.append((_ms_to_utc(event_time), _ms_to_utc(expiry), user, _v(publisher),
                          _labelled(pub_type, _SURFACE), _v(registrant), _v(source_type), app_dest, web_dest,
                          _v(origin), _v(enrollment), _labelled(status, _SOURCE_STATUS), '\n'.join(copies),
                          _v(row_id)))
    data_list.sort(key=lambda r: (r[0] is None, r[0] or datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)))
    data_headers = (('Event Time (UTC)', 'datetime'), ('Expiry Time (UTC)', 'datetime'), 'Android User',
                    'Publisher', 'Publisher Type', 'Registrant', 'Source Type', 'App Destinations',
                    'Web Destinations', 'Registration Origin', 'Enrollment ID', 'Status', 'Copy', 'Source ID')
    return data_headers, data_list, source


@artifact_processor
def adServicesMeasurementTriggers(context):
    wanted = ('_id', 'trigger_time', 'attribution_destination', 'destination_type', 'registrant',
              'registration_origin', 'enrollment_id', 'status')
    rows, source = _read_table(context, 'AdServices - Attribution Triggers', 'msmt_trigger', wanted)
    data_list = []
    for (user, values), copies in rows:
        row_id, trigger_time, destination, dest_type, registrant, origin, enrollment, status = values
        data_list.append((_ms_to_utc(trigger_time), user, _v(destination), _labelled(dest_type, _SURFACE),
                          _v(registrant), _v(origin), _v(enrollment), _labelled(status, _TRIGGER_STATUS),
                          '\n'.join(copies), _v(row_id)))
    data_list.sort(key=lambda r: (r[0] is None, r[0] or datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)))
    data_headers = (('Trigger Time (UTC)', 'datetime'), 'Android User', 'Attribution Destination',
                    'Destination Type', 'Registrant', 'Registration Origin', 'Enrollment ID', 'Status', 'Copy',
                    'Trigger ID')
    return data_headers, data_list, source


def _consent_api(store, key):
    if store == 'System service' and key.startswith('CONSENT_API_TYPE_'):
        return _CONSENT_PARCEL.get(key[len('CONSENT_API_TYPE_'):], '')
    if store == 'AdServices app':
        return _APP_API_KEYS.get(key, '')
    return ''


@artifact_processor
def adServicesConsent(context):
    candidates = []
    for path in context.get_files_found():
        norm = _norm(path)
        if not norm.endswith('/ConsentManagerStorageIdentifier.xml'):
            continue
        if re.search(r'/system/adservices/\d+/consent/ConsentManagerStorageIdentifier\.xml$', norm) or \
                _in_package(path, 'files'):
            candidates.append(path)
    data_list = []
    sources = []
    for path, rel in _unique(context, candidates):
        store = 'System service' if re.search(r'/system/adservices/\d+/consent/', _norm(rel)) else 'AdServices app'
        try:
            with open(path, 'rb') as handle:
                root = ET.fromstring(handle.read())
        except (OSError, ET.ParseError) as ex:
            logfunc(f'AdServices - Ad Privacy Consent: could not read {path}: {ex}')
            continue
        sources.append(path)
        user = _android_user(rel)
        copy = _copy(rel)
        for element in root:
            key = element.get('name')
            if key is None:
                continue
            value = element.get('value')
            if value is None:
                value = element.text or ''
            data_list.append((user, store, key, value, element.tag, _consent_api(store, key), copy))
    data_list.sort(key=lambda r: (str(r[0]), r[1], r[6], r[2]))
    data_headers = ('Android User', 'Store', 'Key', 'Value', 'Value Type', 'API', 'Copy')
    return data_headers, data_list, '\n'.join(sources)

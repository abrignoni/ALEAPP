__artifacts_v2__ = {
    "chrome_sync_sessions": {
        "name": "Chrome Sync - Synced Tabs",
        "description": "Pages in the tabs Chromium-based browsers synced, from this browser and from other sync clients on the account, with the address, title, navigation time and the name of the device the tab belongs to.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-04",
        "last_update_date": "2026-10-17",
        "requirements": "none",
        "category": "Chrome Sync",
        "notes": "Reads the Sync Data/LevelDB folder of Chromium-based browsers: app_chrome/<profile>/Sync Data/LevelDB, and app_opera/Sync Data/LevelDB for Opera, read only when the directory directly above app_chrome or app_opera is shaped like a package name. Read with the vendored ccl_leveldb through scripts/chromium_sync_data.py, ported from DLEAPP (https://github.com/abrignoni/DLEAPP/blob/6ea23d789a10fc2ffcd09eb374c76423705de9b1/scripts/chromium/sync_data.py). Browser is that package and Source File names the folder a row came from; Browser does not separate a second Android user's store of the same browser, which Source File does. The storage views one Android extraction can hold for an app data directory (data/data, data/user/0, data_mirror) are collapsed so a store is read once; a second Android user's store is read as its own store, as on russell_a14, russell_pixel6a_a13, samsungs20_a13, emu_a15_oss_v4 to emu_a15_oss_v17, emu_a15_oss2_v2 and emu_a15_oss2_v3. Chromium keeps each sync data type's records under the keys <type>-dt-<storage key>, with A- in front for account storage, and the type's sync state under <type>-GlobalMetadata (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/model/blocking_data_type_store_impl.cc#L26-L63 and https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/model/blocking_data_type_store_impl.cc#L172-L183); no tested store held an account storage data record, and 5 held only an account storage sync state record, for reading_list. LevelDB numbers each write and orders the versions of a key by decreasing sequence number, the newest first (https://github.com/google/leveldb/blob/bb74ef739973a70ca9f0d90788a1da89b788c0ad/db/dbformat.cc#L47-L63). Only the newest version of each key is read, and a key whose newest version is a deletion is not reported; earlier versions are not reported by any artifact, and the run log counts them for each folder. Across the 85 stores on the tested images that left 1,333 of 63,174 records as the newest version of a key, 190 of them deletions. Earlier releases of these artifacts reported older versions of tab records, so their Synced Tabs counts were larger. Values are decoded with the field numbers and types of the messages Chromium publishes under components/sync/protocol at commit 5926523bcfedb77ba2533ace1dd93b477673f72a, transcribed into scripts/chromium_sync_data.py, not by guessing at field types; a record that does not decode is not reported and the run log names its store and data type; none failed to decode on the tested images. Not read: the -md- metadata records and the data types other than device_info, sessions and send_tab_to_self. Of those, the tested stores held preferences, priority_preferences and account_setting data records; reading_list, saved_tab_group, history_delete_directives and the others held no live data record, only their sync state. No tested image held a Sync Data folder under app_webview or app_sbrowser, and those are not read. One row per navigation entry in each live sessions record that holds a SessionTab (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/session_specifics.proto#L69-L91), whose entries are TabNavigation messages (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/tab_navigation.proto#L19-L51). URL is virtual_url, the URL as displayed to the user (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/tab_navigation.proto#L20-L24); Title and Referrer are title and referrer decoded as UTF-8 and HTTP Status is http_status_code as stored; Transition is page_transition, the core transition type, named with sync_enums.proto (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/sync_enums.proto#L63-L74); From Address Bar is navigation_from_address_bar (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/tab_navigation.proto#L40-L41). Navigation Time is timestamp_msec, described as when the navigation last occurred, in client time, and as able to refresh when the user goes back or forward (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/tab_navigation.proto#L35-L37), written with TimeToProtoTime (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync_sessions/synced_session.cc#L136), milliseconds since 1970-01-01 UTC (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/base/time.cc#L14-L16). Of the 377 tested rows with This Device Yes, 200 were within 1 second of a visit to the same address in the same browser's History, 13 within 60 seconds and 7 further; of the other 157, 30 were chrome: or chrome-native: pages, 122 were older than the oldest visit left in that History and 5 had no visit to the address within it. Navigation Index is the entry's position in the tab and Current Entry is Yes on the entry at current_navigation_index (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/session_specifics.proto#L77-L79). Tab Last Active is last_active_time_unix_epoch_millis (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/session_specifics.proto#L89-L91), blank on 303 of the 431 tested rows; Pinned is pinned shown as Yes or No, and Pinned held No on all 431 tested rows; Tab ID and Window ID are tab_id and window_id as stored. Device Name is the client_name of the session header with the same session tag, or of the device with that Cache GUID when no header is stored; it held a value on every tested row. Session Tag is the record's session_tag, which the proto describes as sync's cache GUID since M89 (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/session_specifics.proto#L21-L24). This Device is Yes when the session tag equals the cache_guid in the sessions sync state, the GUID of the sync client that wrote the store (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/data_type_state.proto#L58-L64), No when it equals the Cache GUID of another device the store lists, and blank when the store records no cache_guid or the tag matches no listed GUID. On cookbook_a11 and pixel3_a11 every session tag began with session_sync and matched no Cache GUID, so This Device is blank on their 48 rows. A row whose This Device is No came from another sync client on the account; it is not a page opened in this browser. The 6 No rows, all on samsungs20_a13, came from another client whose device_info lists it as OS_TYPE_WINDOWS (1). Browser held one value on the rows of every image but pixel7a_a14.",
        "paths": ('*/app_chrome/*/Sync Data/LevelDB/*', '*/app_opera/Sync Data/LevelDB/*'),
        "output_types": "standard",
        "artifact_icon": "cloud-computing",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows (no Sync Data folder matched)",
            "adams_ss135dl_a13": "Android 13 | 0 rows (no live tab record in the Sync Data folders)",
            "anne_a15": "Android 15 | 1 row",
            "cookbook_a11": "Android 11 | 41 rows",
            "df020_mavic_pro_android": "0 rows (no Sync Data folder matched)",
            "dfrws2011_case1_a855": "0 rows (no Sync Data folder matched)",
            "dfrws2011_case2_droid_a201": "Android 2.0.1 | 0 rows (no Sync Data folder matched)",
            "emu_a15_oss2_v1": "Android 15 | 0 rows (no Sync Data folder matched)",
            "emu_a15_oss2_v2": "Android 15 | 0 rows (no live tab record in the Sync Data folders)",
            "emu_a15_oss2_v3": "Android 15 | 0 rows (no live tab record in the Sync Data folders)",
            "emu_a15_oss_v1": "Android 15 | 0 rows (no live tab record in the Sync Data folders)",
            "emu_a15_oss_v10": "Android 15 | 0 rows (no live tab record in the Sync Data folders)",
            "emu_a15_oss_v11": "Android 15 | 0 rows (no live tab record in the Sync Data folders)",
            "emu_a15_oss_v12": "Android 15 | 0 rows (no live tab record in the Sync Data folders)",
            "emu_a15_oss_v13": "Android 15 | 0 rows (no live tab record in the Sync Data folders)",
            "emu_a15_oss_v14": "Android 15 | 0 rows (no live tab record in the Sync Data folders)",
            "emu_a15_oss_v15": "Android 15 | 0 rows (no live tab record in the Sync Data folders)",
            "emu_a15_oss_v16": "Android 15 | 0 rows (no live tab record in the Sync Data folders)",
            "emu_a15_oss_v17": "Android 15 | 0 rows (no live tab record in the Sync Data folders)",
            "emu_a15_oss_v2": "Android 15 | 0 rows (no live tab record in the Sync Data folders)",
            "emu_a15_oss_v3": "Android 15 | 0 rows (no live tab record in the Sync Data folders)",
            "emu_a15_oss_v4": "Android 15 | 0 rows (no live tab record in the Sync Data folders)",
            "emu_a15_oss_v5": "Android 15 | 0 rows (no live tab record in the Sync Data folders)",
            "emu_a15_oss_v6": "Android 15 | 0 rows (no live tab record in the Sync Data folders)",
            "emu_a15_oss_v7": "Android 15 | 0 rows (no live tab record in the Sync Data folders)",
            "emu_a15_oss_v8": "Android 15 | 0 rows (no live tab record in the Sync Data folders)",
            "emu_a15_oss_v9": "Android 15 | 0 rows (no live tab record in the Sync Data folders)",
            "falken_a326u_a13": "Android 13 | 0 rows (no live tab record in the Sync Data folders)",
            "galaxys10_a10": "Android 10 | 0 rows (no live tab record in the Sync Data folders)",
            "hc_pixel8pro_a16": "Android 16 | 6 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows (no live tab record in the Sync Data folders)",
            "hc_pixel8pro_a17_ail": "Android 17 | 0 rows (no Sync Data folder matched)",
            "hickman_a13": "Android 13 | 12 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows (no live tab record in the Sync Data folders)",
            "pixel3_a11": "Android 11 | 7 rows",
            "pixel3_a12": "Android 12 | 20 rows",
            "pixel7a_a14": "Android 14 | 18 rows",
            "russell_a14": "Android 14 | 48 rows",
            "russell_pixel6a_a13": "Android 13 | 27 rows",
            "s20fe_a13": "Android 13 | 0 rows (no live tab record in the Sync Data folders)",
            "samsunga53_a14": "Android 14 | 0 rows (no live tab record in the Sync Data folders)",
            "samsungs20_a13": "Android 13 | 20 rows",
            "sharon_a13": "Android 13 | 83 rows",
            "sharon_a14": "Android 14 | 148 rows",
            "userb2_a13": "Android 13 | 0 rows (no live tab record in the Sync Data folders)",
        },
    },
    "chrome_sync_devices": {
        "name": "Chrome Sync - Session Devices",
        "description": "The session header each device synced to Chromium-based browsers: the device name and form factor and how many windows and tabs it listed.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-04",
        "last_update_date": "2026-10-17",
        "requirements": "none",
        "category": "Chrome Sync",
        "notes": "Reads the Sync Data/LevelDB folder of Chromium-based browsers: app_chrome/<profile>/Sync Data/LevelDB, and app_opera/Sync Data/LevelDB for Opera, read only when the directory directly above app_chrome or app_opera is shaped like a package name. Read with the vendored ccl_leveldb through scripts/chromium_sync_data.py, ported from DLEAPP (https://github.com/abrignoni/DLEAPP/blob/6ea23d789a10fc2ffcd09eb374c76423705de9b1/scripts/chromium/sync_data.py). Browser is that package and Source File names the folder a row came from; Browser does not separate a second Android user's store of the same browser, which Source File does. The storage views one Android extraction can hold for an app data directory (data/data, data/user/0, data_mirror) are collapsed so a store is read once; a second Android user's store is read as its own store, as on russell_a14, russell_pixel6a_a13, samsungs20_a13, emu_a15_oss_v4 to emu_a15_oss_v17, emu_a15_oss2_v2 and emu_a15_oss2_v3. Chromium keeps each sync data type's records under the keys <type>-dt-<storage key>, with A- in front for account storage, and the type's sync state under <type>-GlobalMetadata (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/model/blocking_data_type_store_impl.cc#L26-L63 and https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/model/blocking_data_type_store_impl.cc#L172-L183); no tested store held an account storage data record, and 5 held only an account storage sync state record, for reading_list. LevelDB numbers each write and orders the versions of a key by decreasing sequence number, the newest first (https://github.com/google/leveldb/blob/bb74ef739973a70ca9f0d90788a1da89b788c0ad/db/dbformat.cc#L47-L63). Only the newest version of each key is read, and a key whose newest version is a deletion is not reported; earlier versions are not reported by any artifact, and the run log counts them for each folder. Across the 85 stores on the tested images that left 1,333 of 63,174 records as the newest version of a key, 190 of them deletions. Earlier releases of these artifacts reported older versions of tab records, so their Synced Tabs counts were larger. Values are decoded with the field numbers and types of the messages Chromium publishes under components/sync/protocol at commit 5926523bcfedb77ba2533ace1dd93b477673f72a, transcribed into scripts/chromium_sync_data.py, not by guessing at field types; a record that does not decode is not reported and the run log names its store and data type; none failed to decode on the tested images. Not read: the -md- metadata records and the data types other than device_info, sessions and send_tab_to_self. Of those, the tested stores held preferences, priority_preferences and account_setting data records; reading_list, saved_tab_group, history_delete_directives and the others held no live data record, only their sync state. No tested image held a Sync Data folder under app_webview or app_sbrowser, and those are not read. One row per live sessions record that holds a SessionHeader (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/session_specifics.proto#L21-L36 and https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/session_specifics.proto#L40-L56). Earlier releases gave one row per window. Device Name is the header's client_name, Form Factor its device_form_factor and Device Type its deprecated device_type, named with sync_enums.proto (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/sync_enums.proto#L143-L177). Windows is the number of SessionWindow entries, Tabs Listed the number of tab ids they list, and Window Types the browser_type names of the windows (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/session_specifics.proto#L58-L66, https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/sync_enums.proto#L180-L186); a header that lists no window has Windows 0 and Window Types blank, as on 2 of the 16 tested rows. Session Start is session_start_time_unix_epoch_millis, which the proto says was introduced in M130 and is not populated for sessions started before it (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/session_specifics.proto#L41-L44); it was blank on 11 of the 16 tested rows, and Form Factor on 4. Session Tag is session_tag, sync's cache GUID since M89 (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/session_specifics.proto#L21-L24). This Device is Yes when the session tag equals the cache_guid in the sessions sync state (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/data_type_state.proto#L58-L64), No when it equals the Cache GUID of another device the store lists, and blank when the store records no cache_guid or the tag matches no listed GUID; on the tested rows it was Yes on 13, No on 1 and blank on 2, the headers of cookbook_a11 and pixel3_a11 whose tags began with session_sync. A device appears here because it synced a session to this account, not because it was used at the device this extraction came from.",
        "paths": ('*/app_chrome/*/Sync Data/LevelDB/*', '*/app_opera/Sync Data/LevelDB/*'),
        "output_types": "standard",
        "artifact_icon": "devices",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows (no Sync Data folder matched)",
            "adams_ss135dl_a13": "Android 13 | 0 rows (no live session header record in the Sync Data folders)",
            "anne_a15": "Android 15 | 1 row",
            "cookbook_a11": "Android 11 | 1 row",
            "df020_mavic_pro_android": "0 rows (no Sync Data folder matched)",
            "dfrws2011_case1_a855": "0 rows (no Sync Data folder matched)",
            "dfrws2011_case2_droid_a201": "Android 2.0.1 | 0 rows (no Sync Data folder matched)",
            "emu_a15_oss2_v1": "Android 15 | 0 rows (no Sync Data folder matched)",
            "emu_a15_oss2_v2": "Android 15 | 0 rows (no live session header record in the Sync Data folders)",
            "emu_a15_oss2_v3": "Android 15 | 0 rows (no live session header record in the Sync Data folders)",
            "emu_a15_oss_v1": "Android 15 | 0 rows (no live session header record in the Sync Data folders)",
            "emu_a15_oss_v10": "Android 15 | 0 rows (no live session header record in the Sync Data folders)",
            "emu_a15_oss_v11": "Android 15 | 0 rows (no live session header record in the Sync Data folders)",
            "emu_a15_oss_v12": "Android 15 | 0 rows (no live session header record in the Sync Data folders)",
            "emu_a15_oss_v13": "Android 15 | 0 rows (no live session header record in the Sync Data folders)",
            "emu_a15_oss_v14": "Android 15 | 0 rows (no live session header record in the Sync Data folders)",
            "emu_a15_oss_v15": "Android 15 | 0 rows (no live session header record in the Sync Data folders)",
            "emu_a15_oss_v16": "Android 15 | 0 rows (no live session header record in the Sync Data folders)",
            "emu_a15_oss_v17": "Android 15 | 0 rows (no live session header record in the Sync Data folders)",
            "emu_a15_oss_v2": "Android 15 | 0 rows (no live session header record in the Sync Data folders)",
            "emu_a15_oss_v3": "Android 15 | 0 rows (no live session header record in the Sync Data folders)",
            "emu_a15_oss_v4": "Android 15 | 0 rows (no live session header record in the Sync Data folders)",
            "emu_a15_oss_v5": "Android 15 | 0 rows (no live session header record in the Sync Data folders)",
            "emu_a15_oss_v6": "Android 15 | 0 rows (no live session header record in the Sync Data folders)",
            "emu_a15_oss_v7": "Android 15 | 0 rows (no live session header record in the Sync Data folders)",
            "emu_a15_oss_v8": "Android 15 | 0 rows (no live session header record in the Sync Data folders)",
            "emu_a15_oss_v9": "Android 15 | 0 rows (no live session header record in the Sync Data folders)",
            "falken_a326u_a13": "Android 13 | 0 rows (no live session header record in the Sync Data folders)",
            "galaxys10_a10": "Android 10 | 0 rows (no live session header record in the Sync Data folders)",
            "hc_pixel8pro_a16": "Android 16 | 1 row",
            "hc_pixel8pro_a17": "Android 17 | 1 row",
            "hc_pixel8pro_a17_ail": "Android 17 | 0 rows (no Sync Data folder matched)",
            "hickman_a13": "Android 13 | 1 row",
            "kevin_pocox7_a15": "Android 15 | 1 row",
            "pixel3_a11": "Android 11 | 1 row",
            "pixel3_a12": "Android 12 | 1 row",
            "pixel7a_a14": "Android 14 | 2 rows",
            "russell_a14": "Android 14 | 1 row",
            "russell_pixel6a_a13": "Android 13 | 1 row",
            "s20fe_a13": "Android 13 | 0 rows (no live session header record in the Sync Data folders)",
            "samsunga53_a14": "Android 14 | 0 rows (no live session header record in the Sync Data folders)",
            "samsungs20_a13": "Android 13 | 2 rows",
            "sharon_a13": "Android 13 | 1 row",
            "sharon_a14": "Android 14 | 1 row",
            "userb2_a13": "Android 13 | 0 rows (no live session header record in the Sync Data folders)",
        },
    },
    "chrome_sync_device_info": {
        "name": "Chrome Sync - Device Info",
        "description": "Devices listed in the sync device information of Chromium-based browsers, with the name, operating system, model, browser version and last update time each device recorded.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-17",
        "last_update_date": "2026-10-17",
        "requirements": "none",
        "category": "Chrome Sync",
        "notes": "Reads the Sync Data/LevelDB folder of Chromium-based browsers: app_chrome/<profile>/Sync Data/LevelDB, and app_opera/Sync Data/LevelDB for Opera, read only when the directory directly above app_chrome or app_opera is shaped like a package name. Read with the vendored ccl_leveldb through scripts/chromium_sync_data.py, ported from DLEAPP (https://github.com/abrignoni/DLEAPP/blob/6ea23d789a10fc2ffcd09eb374c76423705de9b1/scripts/chromium/sync_data.py). Browser is that package and Source File names the folder a row came from; Browser does not separate a second Android user's store of the same browser, which Source File does. The storage views one Android extraction can hold for an app data directory (data/data, data/user/0, data_mirror) are collapsed so a store is read once; a second Android user's store is read as its own store, as on russell_a14, russell_pixel6a_a13, samsungs20_a13, emu_a15_oss_v4 to emu_a15_oss_v17, emu_a15_oss2_v2 and emu_a15_oss2_v3. Chromium keeps each sync data type's records under the keys <type>-dt-<storage key>, with A- in front for account storage, and the type's sync state under <type>-GlobalMetadata (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/model/blocking_data_type_store_impl.cc#L26-L63 and https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/model/blocking_data_type_store_impl.cc#L172-L183); no tested store held an account storage data record, and 5 held only an account storage sync state record, for reading_list. LevelDB numbers each write and orders the versions of a key by decreasing sequence number, the newest first (https://github.com/google/leveldb/blob/bb74ef739973a70ca9f0d90788a1da89b788c0ad/db/dbformat.cc#L47-L63). Only the newest version of each key is read, and a key whose newest version is a deletion is not reported; earlier versions are not reported by any artifact, and the run log counts them for each folder. Across the 85 stores on the tested images that left 1,333 of 63,174 records as the newest version of a key, 190 of them deletions. Earlier releases of these artifacts reported older versions of tab records, so their Synced Tabs counts were larger. Values are decoded with the field numbers and types of the messages Chromium publishes under components/sync/protocol at commit 5926523bcfedb77ba2533ace1dd93b477673f72a, transcribed into scripts/chromium_sync_data.py, not by guessing at field types; a record that does not decode is not reported and the run log names its store and data type; none failed to decode on the tested images. Not read: the -md- metadata records and the data types other than device_info, sessions and send_tab_to_self. Of those, the tested stores held preferences, priority_preferences and account_setting data records; reading_list, saved_tab_group, history_delete_directives and the others held no live data record, only their sync state. No tested image held a Sync Data folder under app_webview or app_sbrowser, and those are not read. One row per live device_info record, a DeviceInfoSpecifics message (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L24-L110). Last Updated is last_updated_timestamp, which the proto describes as updated to the current time periodically and whenever another field changes (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L53-L57); the client sets it with TimeToProtoTime from its own clock (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync_device_info/device_info_sync_bridge.cc#L322-L325), milliseconds since 1970-01-01 UTC (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/base/time.cc#L14-L16). Device Name is client_name, a non-unique human readable name (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L28-L29), and equalled Model on 38 of the 41 tested rows; Cache GUID is cache_guid, which identifies a sync client (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L25-L26). This Device is Yes when the row's cache GUID equals the cache_guid in the type's sync state record, the GUID of the sync client that wrote the store (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/data_type_state.proto#L58-L64), No when it differs, and blank when the store records none; each of the 20 tested stores with device rows had one Yes row. OS Type, Form Factor and Device Type are os_type and device_form_factor (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L96-L100) and the deprecated device_type (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L31-L34), named with sync_enums.proto (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/sync_enums.proto#L143-L177); OS Type and Form Factor were blank on 8 of the 41 tested rows. Chrome Version is chrome_version_info.version_number (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L91-L92, https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L263-L266), or the deprecated chrome_version when that is absent (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L40-L42); it was blank on 10 rows, as were Sync User Agent and Signin Scoped Device ID. Manufacturer, Model, Sync User Agent and Signin Scoped Device ID are manufacturer, model, sync_user_agent and signin_scoped_device_id (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L67-L71, https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L36-L38, https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/device_info_specifics.proto#L49-L51). A row records that a device was listed in the browser's sync data; it does not establish who used the device.",
        "paths": ('*/app_chrome/*/Sync Data/LevelDB/*', '*/app_opera/Sync Data/LevelDB/*'),
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows (no Sync Data folder matched)",
            "adams_ss135dl_a13": "Android 13 | 8 rows",
            "anne_a15": "Android 15 | 2 rows",
            "cookbook_a11": "Android 11 | 1 row",
            "df020_mavic_pro_android": "0 rows (no Sync Data folder matched)",
            "dfrws2011_case1_a855": "0 rows (no Sync Data folder matched)",
            "dfrws2011_case2_droid_a201": "Android 2.0.1 | 0 rows (no Sync Data folder matched)",
            "emu_a15_oss2_v1": "Android 15 | 0 rows (no Sync Data folder matched)",
            "emu_a15_oss2_v2": "Android 15 | 0 rows (no live device_info record in the Sync Data folders)",
            "emu_a15_oss2_v3": "Android 15 | 0 rows (no live device_info record in the Sync Data folders)",
            "emu_a15_oss_v1": "Android 15 | 0 rows (no live device_info record in the Sync Data folders)",
            "emu_a15_oss_v10": "Android 15 | 0 rows (no live device_info record in the Sync Data folders)",
            "emu_a15_oss_v11": "Android 15 | 0 rows (no live device_info record in the Sync Data folders)",
            "emu_a15_oss_v12": "Android 15 | 0 rows (no live device_info record in the Sync Data folders)",
            "emu_a15_oss_v13": "Android 15 | 0 rows (no live device_info record in the Sync Data folders)",
            "emu_a15_oss_v14": "Android 15 | 0 rows (no live device_info record in the Sync Data folders)",
            "emu_a15_oss_v15": "Android 15 | 0 rows (no live device_info record in the Sync Data folders)",
            "emu_a15_oss_v16": "Android 15 | 0 rows (no live device_info record in the Sync Data folders)",
            "emu_a15_oss_v17": "Android 15 | 0 rows (no live device_info record in the Sync Data folders)",
            "emu_a15_oss_v2": "Android 15 | 0 rows (no live device_info record in the Sync Data folders)",
            "emu_a15_oss_v3": "Android 15 | 0 rows (no live device_info record in the Sync Data folders)",
            "emu_a15_oss_v4": "Android 15 | 0 rows (no live device_info record in the Sync Data folders)",
            "emu_a15_oss_v5": "Android 15 | 0 rows (no live device_info record in the Sync Data folders)",
            "emu_a15_oss_v6": "Android 15 | 0 rows (no live device_info record in the Sync Data folders)",
            "emu_a15_oss_v7": "Android 15 | 0 rows (no live device_info record in the Sync Data folders)",
            "emu_a15_oss_v8": "Android 15 | 0 rows (no live device_info record in the Sync Data folders)",
            "emu_a15_oss_v9": "Android 15 | 0 rows (no live device_info record in the Sync Data folders)",
            "falken_a326u_a13": "Android 13 | 0 rows (no live device_info record in the Sync Data folders)",
            "galaxys10_a10": "Android 10 | 0 rows (no live device_info record in the Sync Data folders)",
            "hc_pixel8pro_a16": "Android 16 | 2 rows",
            "hc_pixel8pro_a17": "Android 17 | 2 rows",
            "hc_pixel8pro_a17_ail": "Android 17 | 0 rows (no Sync Data folder matched)",
            "hickman_a13": "Android 13 | 1 row",
            "kevin_pocox7_a15": "Android 15 | 3 rows",
            "pixel3_a11": "Android 11 | 6 rows",
            "pixel3_a12": "Android 12 | 1 row",
            "pixel7a_a14": "Android 14 | 2 rows",
            "russell_a14": "Android 14 | 2 rows",
            "russell_pixel6a_a13": "Android 13 | 2 rows",
            "s20fe_a13": "Android 13 | 0 rows (no live device_info record in the Sync Data folders)",
            "samsunga53_a14": "Android 14 | 3 rows",
            "samsungs20_a13": "Android 13 | 4 rows",
            "sharon_a13": "Android 13 | 1 row",
            "sharon_a14": "Android 14 | 1 row",
            "userb2_a13": "Android 13 | 0 rows (no live device_info record in the Sync Data folders)",
        },
    },
    "chrome_sync_send_tab_to_self": {
        "name": "Chrome Sync - Send Tab To Self",
        "description": "Pages sent between devices with send tab to self, from the sync data of Chromium-based browsers: the title and address, when it was shared, the sending device's name and the target device.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-17",
        "last_update_date": "2026-10-17",
        "requirements": "none",
        "category": "Chrome Sync",
        "notes": "Reads the Sync Data/LevelDB folder of Chromium-based browsers: app_chrome/<profile>/Sync Data/LevelDB, and app_opera/Sync Data/LevelDB for Opera, read only when the directory directly above app_chrome or app_opera is shaped like a package name. Read with the vendored ccl_leveldb through scripts/chromium_sync_data.py, ported from DLEAPP (https://github.com/abrignoni/DLEAPP/blob/6ea23d789a10fc2ffcd09eb374c76423705de9b1/scripts/chromium/sync_data.py). Browser is that package and Source File names the folder a row came from; Browser does not separate a second Android user's store of the same browser, which Source File does. The storage views one Android extraction can hold for an app data directory (data/data, data/user/0, data_mirror) are collapsed so a store is read once; a second Android user's store is read as its own store, as on russell_a14, russell_pixel6a_a13, samsungs20_a13, emu_a15_oss_v4 to emu_a15_oss_v17, emu_a15_oss2_v2 and emu_a15_oss2_v3. Chromium keeps each sync data type's records under the keys <type>-dt-<storage key>, with A- in front for account storage, and the type's sync state under <type>-GlobalMetadata (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/model/blocking_data_type_store_impl.cc#L26-L63 and https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/model/blocking_data_type_store_impl.cc#L172-L183); no tested store held an account storage data record, and 5 held only an account storage sync state record, for reading_list. LevelDB numbers each write and orders the versions of a key by decreasing sequence number, the newest first (https://github.com/google/leveldb/blob/bb74ef739973a70ca9f0d90788a1da89b788c0ad/db/dbformat.cc#L47-L63). Only the newest version of each key is read, and a key whose newest version is a deletion is not reported; earlier versions are not reported by any artifact, and the run log counts them for each folder. Across the 85 stores on the tested images that left 1,333 of 63,174 records as the newest version of a key, 190 of them deletions. Earlier releases of these artifacts reported older versions of tab records, so their Synced Tabs counts were larger. Values are decoded with the field numbers and types of the messages Chromium publishes under components/sync/protocol at commit 5926523bcfedb77ba2533ace1dd93b477673f72a, transcribed into scripts/chromium_sync_data.py, not by guessing at field types; a record that does not decode is not reported and the run log names its store and data type; none failed to decode on the tested images. Not read: the -md- metadata records and the data types other than device_info, sessions and send_tab_to_self. Of those, the tested stores held preferences, priority_preferences and account_setting data records; reading_list, saved_tab_group, history_delete_directives and the others held no live data record, only their sync state. No tested image held a Sync Data folder under app_webview or app_sbrowser, and those are not read. One row per live send_tab_to_self record, a SendTabToSelfLocal message whose field 1 is the SendTabToSelfSpecifics (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/send_tab_to_self/proto/send_tab_to_self.proto#L17-L19, https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/send_tab_to_self_specifics.proto#L23-L43). Shared Time is shared_time_usec, the time the tab was shared as measured by the client, in microseconds since 1601-01-01 (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/send_tab_to_self_specifics.proto#L32-L34). Received Time, Opened Time and Activated Time are the received, opened and activated times in the same unit, which the proto says the receiving device sets (https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/protocol/send_tab_to_self_specifics.proto#L70-L85). Title, URL, Sending Device Name and Target Cache GUID are title, url, device_name and target_device_sync_cache_guid decoded as UTF-8; Opened and Notification Dismissed are opened and notification_dismissed shown as Yes or No, blank when not stored; Target Device Name is the name of the device in the store's device_info records with that Cache GUID, blank when the store lists none. No tested store held a send_tab_to_self data record; 19 held only the type's sync state. The field layout comes from Chromium's published proto and is exercised only by synthetic test data; no tested image exercises it.",
        "paths": ('*/app_chrome/*/Sync Data/LevelDB/*', '*/app_opera/Sync Data/LevelDB/*'),
        "output_types": "standard",
        "artifact_icon": "send",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows (no Sync Data folder matched)",
            "adams_ss135dl_a13": "Android 13 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "anne_a15": "Android 15 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "cookbook_a11": "Android 11 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "df020_mavic_pro_android": "0 rows (no Sync Data folder matched)",
            "dfrws2011_case1_a855": "0 rows (no Sync Data folder matched)",
            "dfrws2011_case2_droid_a201": "Android 2.0.1 | 0 rows (no Sync Data folder matched)",
            "emu_a15_oss2_v1": "Android 15 | 0 rows (no Sync Data folder matched)",
            "emu_a15_oss2_v2": "Android 15 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "emu_a15_oss2_v3": "Android 15 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "emu_a15_oss_v1": "Android 15 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "emu_a15_oss_v10": "Android 15 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "emu_a15_oss_v11": "Android 15 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "emu_a15_oss_v12": "Android 15 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "emu_a15_oss_v13": "Android 15 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "emu_a15_oss_v14": "Android 15 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "emu_a15_oss_v15": "Android 15 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "emu_a15_oss_v16": "Android 15 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "emu_a15_oss_v17": "Android 15 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "emu_a15_oss_v2": "Android 15 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "emu_a15_oss_v3": "Android 15 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "emu_a15_oss_v4": "Android 15 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "emu_a15_oss_v5": "Android 15 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "emu_a15_oss_v6": "Android 15 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "emu_a15_oss_v7": "Android 15 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "emu_a15_oss_v8": "Android 15 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "emu_a15_oss_v9": "Android 15 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "falken_a326u_a13": "Android 13 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "galaxys10_a10": "Android 10 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "hc_pixel8pro_a16": "Android 16 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "hc_pixel8pro_a17": "Android 17 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "hc_pixel8pro_a17_ail": "Android 17 | 0 rows (no Sync Data folder matched)",
            "hickman_a13": "Android 13 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "kevin_pocox7_a15": "Android 15 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "pixel3_a11": "Android 11 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "pixel3_a12": "Android 12 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "pixel7a_a14": "Android 14 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "russell_a14": "Android 14 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "russell_pixel6a_a13": "Android 13 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "s20fe_a13": "Android 13 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "samsunga53_a14": "Android 14 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "samsungs20_a13": "Android 13 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "sharon_a13": "Android 13 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "sharon_a14": "Android 14 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
            "userb2_a13": "Android 13 | 0 rows (no live send_tab_to_self record in the Sync Data folders)",
        },
    },
}

import datetime
import os
import re

from scripts.artifacts.storagePathViews import canonical_path
from scripts.chromium_sync_data import (BROWSER_TYPES, DEVICE_TYPES, FORM_FACTORS, OS_TYPES,
                                        PAGE_TRANSITIONS, ProtoError, SyncStore, decode,
                                        enum_label, webkit_time)
from scripts.ilapfuncs import artifact_processor, logfunc

# Chromium builds keep a profile's Sync Data under app_chrome/<profile>; Opera keeps it
# directly under app_opera. The app package directory above it is the only part of the
# path that names the browser, so it must sit directly above app_chrome or app_opera and
# be shaped like a package name, as in chrome.py's _package_from_path.
_STORE = re.compile(r'(?:^|/)([A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)+)/'
                    r'(?:app_chrome/[^/]+|app_opera)/Sync Data/LevelDB$')


def _ms_time(value):
    """Milliseconds since 1970-01-01 UTC as a datetime; '' for missing, zero or out of range."""
    try:
        milliseconds = int(value)
    except (TypeError, ValueError):
        return ''
    if milliseconds <= 0:
        return ''
    try:
        return datetime.datetime.fromtimestamp(milliseconds / 1000, tz=datetime.timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _yes_no(value):
    if value is None:
        return ''
    return 'Yes' if value else 'No'


def _browser(relative):
    """The package a Sync Data/LevelDB folder belongs to, or '' when the folder is not a
    browser profile's store."""
    match = _STORE.search(relative)
    return match.group(1) if match else ''


def _folders(context):
    """(staged folder, evidence relative folder) for each Sync Data/LevelDB store.

    Files are grouped by the folder that holds them, so a store is read once however
    many of its files matched. The storage views an Android extraction can carry for one
    app data directory (data/data, data/user/0, data_mirror and the rest, see
    storagePathViews) are collapsed at the folder, keeping the preferred spelling, so a
    store is not read once per view and a file missing from one view cannot split it.
    A second Android user's store keeps its own key and is read as its own store.
    """
    best = {}
    for found in context.get_files_found():
        path = str(found)
        if not os.path.isfile(path):
            continue
        folder = os.path.dirname(path)
        relative = str(context.get_relative_path(folder)).replace('\\', '/')
        if not _browser(relative):
            continue
        key, rank = canonical_path(relative + '/')
        held = best.get(key)
        if held is None or rank < held[0]:
            best[key] = (rank, folder, relative)
    return sorted(((folder, relative) for _rank, folder, relative in best.values()),
                  key=lambda item: item[1])


def _stores(context, label):
    """(folder, relative folder, SyncStore) for each store that could be read."""
    out = []
    for folder, relative in _folders(context):
        try:
            sync = SyncStore(folder)
        except (OSError, ValueError, EOFError) as ex:
            logfunc(f'{label}: could not read {relative}: {ex}')
            continue
        logfunc(f'{label}: {relative}: {sync.records} records, {sync.superseded} older '
                f'versions of a key not read, {sync.deleted} keys whose newest version is a '
                f'deletion')
        out.append((folder, relative, sync))
    return out


def _decoded(sync, root_tag, message, label, relative):
    """(storage key, decoded message) for each live data record of one type that decodes."""
    out = []
    for _account, storage_key, value in sync.records_of(root_tag):
        try:
            out.append((storage_key, decode(value, message)))
        except ProtoError as ex:
            logfunc(f'{label}: {relative}: a {root_tag} record did not decode as '
                    f'{message} and is not reported: {ex}')
    return out


def _devices(sync, label, relative):
    """{cache GUID: DeviceInfoSpecifics} from the live device_info records."""
    devices = {}
    for _key, device in _decoded(sync, 'device_info', 'DeviceInfoSpecifics', label, relative):
        devices.setdefault(device.get('cache_guid', ''), device)
    return devices


def _local_guid(sync, root_tag, label, relative):
    try:
        return sync.local_cache_guid(root_tag)
    except ProtoError as ex:
        logfunc(f'{label}: {relative}: the {root_tag} sync state did not decode, so '
                f'This Device is blank: {ex}')
        return ''


def _this_device(guid, local_guid):
    if not local_guid:
        return ''
    return 'Yes' if guid == local_guid else 'No'


def _session_this_device(tag, local_guid, devices):
    """Yes when a session tag is this client's cache GUID, No when it is the cache GUID of
    another device the store lists, blank otherwise. A session tag has been the cache GUID
    only since M89, so a tag that matches no listed GUID establishes nothing about whose
    session it is."""
    if not local_guid or not tag:
        return ''
    if tag == local_guid:
        return 'Yes'
    return 'No' if tag in devices else ''


def _sessions(sync, label, relative):
    """(headers {session tag: SessionHeader}, tabs [(session tag, SessionTab)])."""
    headers, tabs = {}, []
    for _key, session in _decoded(sync, 'sessions', 'SessionSpecifics', label, relative):
        tag = session.get('session_tag', '')
        if 'header' in session:
            headers[tag] = session['header']
        elif 'tab' in session:
            tabs.append((tag, session['tab']))
    return headers, tabs


def _device_name(tag, headers, devices):
    name = headers.get(tag, {}).get('client_name')
    if name is None:
        name = devices.get(tag, {}).get('client_name', '')
    return name


@artifact_processor
def chrome_sync_sessions(context):
    label = 'Chrome Sync - Synced Tabs'
    data_list = []
    sources = []
    for folder, relative, sync in _stores(context, label):
        local_guid = _local_guid(sync, 'sessions', label, relative)
        devices = _devices(sync, label, relative)
        headers, tabs = _sessions(sync, label, relative)
        browser = _browser(relative)
        rows = 0
        for tag, tab in sorted(tabs, key=lambda item: (item[0], item[1].get('window_id', 0),
                                                        item[1].get('tab_id', 0))):
            current = tab.get('current_navigation_index')
            for index, navigation in enumerate(tab.get('navigation', [])):
                data_list.append((
                    _ms_time(navigation.get('timestamp_msec')),
                    _ms_time(tab.get('last_active_time_unix_epoch_millis')),
                    _device_name(tag, headers, devices),
                    _session_this_device(tag, local_guid, devices),
                    navigation.get('virtual_url', ''),
                    navigation.get('title', ''),
                    navigation.get('referrer', ''),
                    navigation.get('http_status_code', ''),
                    enum_label(PAGE_TRANSITIONS, navigation.get('page_transition')),
                    _yes_no(navigation.get('navigation_from_address_bar')),
                    index,
                    '' if current is None else ('Yes' if index == current else 'No'),
                    _yes_no(tab.get('pinned')),
                    tab.get('tab_id', ''),
                    tab.get('window_id', ''),
                    tag,
                    browser,
                    relative,
                ))
                rows += 1
        if rows:
            sources.append(folder)
    data_headers = (('Navigation Time', 'datetime'), ('Tab Last Active', 'datetime'),
                    'Device Name', 'This Device', 'URL', 'Title', 'Referrer', 'HTTP Status',
                    'Transition', 'From Address Bar', 'Navigation Index', 'Current Entry',
                    'Pinned', 'Tab ID', 'Window ID', 'Session Tag', 'Browser', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def chrome_sync_devices(context):
    label = 'Chrome Sync - Session Devices'
    data_list = []
    sources = []
    for folder, relative, sync in _stores(context, label):
        local_guid = _local_guid(sync, 'sessions', label, relative)
        devices = _devices(sync, label, relative)
        headers, _tabs = _sessions(sync, label, relative)
        browser = _browser(relative)
        rows = 0
        for tag, header in sorted(headers.items()):
            windows = header.get('window', [])
            browser_types = sorted({enum_label(BROWSER_TYPES, window.get('browser_type'))
                                    for window in windows if 'browser_type' in window})
            data_list.append((
                _ms_time(header.get('session_start_time_unix_epoch_millis')),
                header.get('client_name', ''),
                _session_this_device(tag, local_guid, devices),
                enum_label(FORM_FACTORS, header.get('device_form_factor')),
                enum_label(DEVICE_TYPES, header.get('device_type')),
                len(windows),
                sum(len(window.get('tab', [])) for window in windows),
                ', '.join(browser_types),
                tag,
                browser,
                relative,
            ))
            rows += 1
        if rows:
            sources.append(folder)
    data_headers = (('Session Start', 'datetime'), 'Device Name', 'This Device', 'Form Factor',
                    'Device Type', 'Windows', 'Tabs Listed', 'Window Types', 'Session Tag',
                    'Browser', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def chrome_sync_device_info(context):
    label = 'Chrome Sync - Device Info'
    data_list = []
    sources = []
    for folder, relative, sync in _stores(context, label):
        local_guid = _local_guid(sync, 'device_info', label, relative)
        browser = _browser(relative)
        rows = 0
        for _key, device in _decoded(sync, 'device_info', 'DeviceInfoSpecifics', label,
                                     relative):
            guid = device.get('cache_guid', '')
            version = (device.get('chrome_version_info') or {}).get('version_number')
            if version is None:
                version = device.get('chrome_version', '')
            data_list.append((
                _ms_time(device.get('last_updated_timestamp')),
                device.get('client_name', ''),
                _this_device(guid, local_guid),
                device.get('manufacturer', ''),
                device.get('model', ''),
                enum_label(OS_TYPES, device.get('os_type')),
                enum_label(FORM_FACTORS, device.get('device_form_factor')),
                enum_label(DEVICE_TYPES, device.get('device_type')),
                version,
                device.get('sync_user_agent', ''),
                guid,
                device.get('signin_scoped_device_id', ''),
                browser,
                relative,
            ))
            rows += 1
        if rows:
            sources.append(folder)
    data_headers = (('Last Updated', 'datetime'), 'Device Name', 'This Device', 'Manufacturer',
                    'Model', 'OS Type', 'Form Factor', 'Device Type', 'Chrome Version',
                    'Sync User Agent', 'Cache GUID', 'Signin Scoped Device ID', 'Browser',
                    'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def chrome_sync_send_tab_to_self(context):
    label = 'Chrome Sync - Send Tab To Self'
    data_list = []
    sources = []
    for folder, relative, sync in _stores(context, label):
        devices = _devices(sync, label, relative)
        browser = _browser(relative)
        rows = 0
        for _key, local in _decoded(sync, 'send_tab_to_self', 'SendTabToSelfLocal', label,
                                    relative):
            entry = local.get('specifics', {})
            target = entry.get('target_device_sync_cache_guid', '')
            data_list.append((
                webkit_time(entry.get('shared_time_usec')),
                webkit_time(entry.get('received_time_windows_epoch_micros')),
                webkit_time(entry.get('opened_time_windows_epoch_micros')),
                webkit_time(entry.get('activated_time_windows_epoch_micros')),
                entry.get('title', ''),
                entry.get('url', ''),
                entry.get('device_name', ''),
                devices.get(target, {}).get('client_name', '') if target else '',
                target,
                _yes_no(entry.get('opened')),
                _yes_no(entry.get('notification_dismissed')),
                entry.get('guid', ''),
                browser,
                relative,
            ))
            rows += 1
        if rows:
            sources.append(folder)
    data_headers = (('Shared Time', 'datetime'), ('Received Time', 'datetime'),
                    ('Opened Time', 'datetime'), ('Activated Time', 'datetime'), 'Title', 'URL',
                    'Sending Device Name', 'Target Device Name', 'Target Cache GUID', 'Opened',
                    'Notification Dismissed', 'GUID', 'Browser', 'Source File')
    return data_headers, data_list, '\n'.join(sources)

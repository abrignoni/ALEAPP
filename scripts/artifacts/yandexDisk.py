__artifacts_v2__ = {
    "yandex_disk_cloud_files": {
        "name": "Yandex Disk Cloud Files",
        "description": "Cloud files and folders the Yandex Disk app had listed for each signed-in account",
        "author": "@AlexisBrignoni, @4n6Wizard, Claude",
        "creation_date": "2026-10-21",
        "last_update_date": "2026-10-21",
        "requirements": "none",
        "category": "Yandex Disk",
        "notes": "One row per row of the DISK and FOREIGN_DISK tables in "
                 "ru.yandex.disk/databases/<uid>_disk, one database per signed-in account. Account "
                 "UID is the number in the file name, which the app builds from the signed-in "
                 "account's numeric uid. Android User is taken from the storage path the database "
                 "came from, so the same account signed in on two Android users is reported once per "
                 "user.\n"
                 "Field meanings were sourced from the decompiled Yandex Disk 6.90.0 app "
                 "(versionCode 690000, database version 85). The committed test data is synthetic: "
                 "databases built from the app's own schema with invented values. The app's upgrade step from database version 84 adds two tables this "
                 "artifact does not read; a fresh 6.90.0 install orders the DISK columns differently "
                 "and adds LATITUDE and LONGITUDE to FOREIGN_DISK, so columns are read by name and a missing "
                 "column reads blank.\n"
                 "These rows are what the app had synced from the server, not a record of what was "
                 "on the device. The app deletes DISK rows by folder path, the folder and everything "
                 "below it, and DISK has no deleted flag; which sync events trigger that delete was "
                 "not traced. A file absent here is not evidence it never existed in the account.\n"
                 "Last Modified is the server's modified time for the resource and EXIF Date is the "
                 "EXIF date the server reported for the resource; both are stored in milliseconds "
                 "and reported in UTC, and EXIF Date is blank when the app stored 0. Local Copy Last "
                 "Access is set to the current time when the app touches a cached local copy, and the "
                 "one caller found in 6.90.0 opens the file in an external viewer; the app resets it "
                 "to 0 when it deletes the local copy and orders cached copies by it when freeing "
                 "space. It is blank when 0. PHOTOSLICE_TIME, which places a photo on the app's "
                 "timeline, is not reported.\n"
                 "ETag holds the server's md5 field on rows from the app's REST and album sync, and "
                 "the file index's MD5 field on rows from its index sync. On rows written by its "
                 "WebDAV sync it holds the server's getetag. That these all equal the MD5 of the "
                 "file's content was not established from the app's code; one of the app's own views "
                 "joins the upload queue's content MD5 to this column. Local Copy MD5 is an MD5 the "
                 "app computed over a local copy. The app clears it for rows that are not offline "
                 "marked when it clears its cache. Where local copies are kept was not established, "
                 "so they are not resolved or shown.\n"
                 "Owner UID is blank for the account's own items (DISK). It is filled only for "
                 "FOREIGN_DISK rows, which the app's album sync writes for items whose owner is "
                 "another account; those rows carry no coordinates.\n"
                 "Shared is 1 when the server marked the item shared (a share object on the album "
                 "path, a shared flag on the WebDAV and index paths); the REST update does not write "
                 "it, so it can be stale. On the REST path Read Only is 1 when shared, not owned and "
                 "without rw rights; other sync paths store the server's readonly flag. Share Group "
                 "reads Family (1), Other (0) or blank when no group was recorded. Offline Mark reads "
                 "Not marked (0), Marked (1) or In marked folder (2), from the app's own enum. Public "
                 "URL is reported as stored; the file-index sync writes the literal FAKE LINK when an "
                 "item is public.\n"
                 "Latitude and Longitude are reported as stored. The app's own queries treat -1 as "
                 "missing, so -1 and NULL are reported blank and left out of the KML. Duration (as "
                 "stored) is milliseconds on the WebDAV sync path; its unit on the album path was not "
                 "established. Width and Height are reported as stored; their unit was not "
                 "established.\n"
                 "Not read by this artifact: the upload queue (see Yandex Disk Uploads), the local "
                 "MediaItems, MediaHashes, MediaDownloads and RECENT_AUTOUPLOADS tables, Album and "
                 "AlbumItem, MOMENTS, FEED and SEARCH tables, pending shared-folder invites, and the "
                 "trash, notes, download queue and account stores beside this database.",
        "paths": ('*/ru.yandex.disk/databases/*_disk*',),
        "output_types": "all",
        "artifact_icon": "cloud",
    },
    "yandex_disk_uploads": {
        "name": "Yandex Disk Uploads",
        "description": "Uploads in the Yandex Disk queue: retained camera autoupload history and pending uploads",
        "author": "@AlexisBrignoni, @4n6Wizard, Claude",
        "creation_date": "2026-10-21",
        "last_update_date": "2026-10-21",
        "requirements": "none",
        "category": "Yandex Disk",
        "notes": "One row per row of the DISK_QUEUE table in ru.yandex.disk/databases/<uid>_disk, "
                 "joined to DISK_QUEUE_EXT on upload_id. Account UID is the number in the file name "
                 "and Account is the queue's own user column; Android User is taken from the storage "
                 "path the database came from. Field meanings were sourced from the decompiled Yandex "
                 "Disk 6.90.0 app. The committed test data is synthetic: databases built from the "
                 "app's own schema with invented values.\n"
                 "What the table keeps matters more than any column. The app deletes completed "
                 "manual uploads (from_autoupload 0 with state 3 or higher). That cleanup does not "
                 "touch completed camera autoupload rows, though other paths can remove them, for "
                 "example when the same file is queued again. So this is mostly a history of "
                 "autouploads plus whatever was still pending, and it holds no history of finished "
                 "manual uploads. Rows can also be copied in from another installed Yandex app that "
                 "shares the queue, so a row is not proof that this app performed the upload.\n"
                 "Times are read as milliseconds and reported in UTC. The writers checked for Date "
                 "Taken, Queued, Autoupload Queued and File Modified When Hashed store milliseconds; "
                 "the others were not traced. Uploaded is the time the app wrote when it marked an "
                 "upload done, so Uploaded is blank on every row that had not finished (Status Queued "
                 "or Paused or failed). A row can also carry Done (3) with a blank Uploaded: the app "
                 "writes 3 without a time when it marks queued manual uploads done and for folder "
                 "rows. The stored date column means different things by upload type: for camera "
                 "autoupload it is the MediaStore date taken (or date added), reported as Date Taken; "
                 "for a manual upload it is the time the upload was queued, reported as Queued. For "
                 "any other upload type its meaning was not established and it is reported only as "
                 "Date (ms, as stored). ETIME is reported as stored; when it is 0 at hashing time the "
                 "app fills it from a time reader whose sources were not traced. Autoupload Queued "
                 "and Upload Started come from DISK_QUEUE_EXT. File Modified When Hashed is the local "
                 "file's last modified time recorded when the app hashed it.\n"
                 "Local Path is the absolute device path the app read; for a folder row it is the "
                 "folder name only. Destination is the folder and name as queued; camera autouploads "
                 "use the folder /photostream and are renamed to yyyy-MM-dd HH-mm-ss with the "
                 "extension upper-cased, and the zone of that name was not established. Uploaded Path "
                 "is the server location the upload returned. MD5 and SHA-256 are hashes the app "
                 "computed over the local file's content.\n"
                 "Labels are derived from the code that writes each value, and the stored number is "
                 "kept in brackets. Status: Queued (1), Paused or failed (2), Done (3); 0 and 4 are "
                 "reported as Legacy code, because the app's migrations rewrite them to 3 and no "
                 "current writer of either was found. Upload Type: Manual (0), Camera autoupload (1), "
                 "Re-upload (3); a completed type 3 row is stored as 1, and no writer of 4 was found. "
                 "Error: Generic (0), Name conflict (1), File too big (2), Local file unavailable "
                 "(3), Local file not readable (4), Files limit or paused (5), Shared folder files "
                 "limit (6), Disk read-only (8); no writer of 7 was found. Media Type: Image (100), "
                 "Video (200), Other (0). Local Cleanup is the app's free-up-space state: Unchecked "
                 "(0), Selected for check (1), Local file deleted (2), Not checked again (3), Error "
                 "(4), Waiting for indexing (5). Local file deleted (2) has two writers: the "
                 "free-up-space process after it deletes the local original, and the upload path when "
                 "the local file of an already uploaded duplicate is gone. So 2 shows the local file "
                 "was gone, not which of the two happened. Any code outside these lists is reported "
                 "as Unknown with its number.\n"
                 "Local File shows the file at Local Path when the extraction holds it. Local Path is "
                 "reported as stored; when it starts with /storage/emulated/<user> or /sdcard, the parser "
                 "searches the "
                 "extraction only for the folders the queue rows name, under media/<user> (the "
                 "data/media/<user> form an extraction holds) or storage/emulated/<user>, and only after "
                 "it has read queue rows, so no shared storage is staged on a device without them. Only "
                 "a file whose extraction path ends with the recorded path's shared-storage form is "
                 "shown, never one that merely shares the file name, and "
                 "the file type is taken from its bytes. A blank Local File means no file was found at "
                 "that path, or Local Path is a folder or not a shared-storage path; it is not evidence "
                 "the upload never happened. A file found at the "
                 "path is what the extraction holds there now, which need not be the bytes that were "
                 "uploaded; MD5 and SHA-256 are the hashes the app computed over the local file when it "
                 "hashed it. A separate "
                 "disk_queue_snapshot database, which the app uses while migrating queue rows, is "
                 "not read. The AUTOUPLOAD_SYNC_V2 tables that database version 85 added are not "
                 "read.",
        "paths": ('*/ru.yandex.disk/databases/*_disk*',),
        "output_types": "standard",
        "artifact_icon": "upload-cloud",
    },
    "yandex_disk_accounts": {
        "name": "Yandex Disk Accounts",
        "description": "Yandex accounts recorded by the Yandex Disk app, with the profile it stored for each",
        "author": "@AlexisBrignoni, @4n6Wizard, Claude",
        "creation_date": "2026-10-21",
        "last_update_date": "2026-10-22",
        "requirements": "none",
        "category": "Yandex Disk",
        "notes": "One row per row of the accounts table in ru.yandex.disk/databases/PassportInternal.db, "
                 "joined by account uid to accounts_last_action, tokens and gcm_subscriptions in the "
                 "same file and to CREDENTIAL in the SETTINGS database beside it. PassportInternal.db "
                 "belongs to the Yandex Passport library, and only the copy under ru.yandex.disk is "
                 "read; the library is shared code, so other Yandex apps may carry a file of the same "
                 "name. Android User is taken from "
                 "the storage path. Field meanings were sourced from the decompiled Yandex Disk 6.90.0 "
                 "app (PassportInternal.db version 13, SETTINGS version 16). The committed test data is "
                 "synthetic: databases built from the app's own schema with invented values.\n"
                 "The profile columns come from whichever of three stores the row carries and could be "
                 "parsed, named in Profile Source; a store that is present but does not parse as JSON "
                 "is not named, and the columns it would fill stay blank. legacy_extra_data_body is @jsn followed by JSON whose extra_data "
                 "object holds _uid, _display_name, _default_avatar, _is_avatar_empty, _is_staff and "
                 "_is_beta_tester, each as a val string; the app fills it from the account's user info. "
                 "user_info_body is the account's user info JSON (keys such as display_name, "
                 "public_name, display_login, native_default_email, firstname, lastname, birthday and "
                 "avatar_url). When the library's secure-blob flag is on it writes secure_blob and "
                 "nulls user_info_body, master_token_value and stash_body. A separate flag encrypts "
                 "what is written, so with it on and the blob flag off those three columns hold "
                 "ciphertext and the profile columns read blank. A plaintext secure_blob reads "
                 "v=1&masterToken=...&userInfo=...&stash=...; only its userInfo part is reported, and "
                 "its masterToken part is checked for presence and never shown. A secure_blob that "
                 "does not start with v=1& is reported as Encrypted, not readable; in 6.90.0 the only "
                 "other writer is AES-GCM encryption under a key in the Android keystore. Where user info and "
                 "the legacy data both give a display name or avatar, the user info value is shown. "
                 "Profile values are the account's user info as the library stored it; they are not "
                 "evidence of who used the device.\n"
                 "Secrets are never reported, only whether they are present: Master Token "
                 "(master_token_value or the masterToken in a plaintext secure_blob; blank when the "
                 "secure_blob is encrypted, since any token is inside the ciphertext), Pin Codes (the "
                 "disk.pincode and mail.pincode entries of the legacy data), Client Tokens (tokens "
                 "rows with a client_token) and Push Token Hash (gcm_subscriptions). Client IDs are the "
                 "client id the library stores beside each token, not the token, and are shown.\n"
                 "Last Action Time is accounts_last_action.local_timestamp, the device clock in "
                 "milliseconds when the library wrote the ADD or DELETE in Last Action. The library's "
                 "sign-in sync between Yandex apps can copy another Yandex app's action row in "
                 "unchanged, and then the time is that app's clock. Token Issued is "
                 "accounts_last_action.timestamp, which the library takes from the server's "
                 "x_token_issued_at and stores as a 32 bit integer with no conversion; it is read as "
                 "Unix seconds because a millisecond value would not fit, and that unit is not stated "
                 "in the code. On a DELETE the library keeps the previous value. User Info Time is the "
                 "seconds part of user_info_meta, which the library writes as <seconds>:<second "
                 "string> from the time it recorded with the user info. Added To Disk App is "
                 "CREDENTIAL.LAST_TIME_LOGGED_IN, the device clock in milliseconds when the app "
                 "inserted the account's credential row. The app does not update it in place; removing "
                 "the account and adding it again writes a new row with a new time. It is blank when 0.\n"
                 "Environment reads Production (1), Team production (2), Testing (3), Team testing (4) or RC (5) "
                 "from the first part of the stored uid. Account Type is stored as text (login, social, "
                 "phone, external_mail or team). legacy_affinity is not shown: the library derives it "
                 "from the environment (TEST for Testing and Team testing, PROD otherwise). Current Disk Account is "
                 "CREDENTIAL.IS_SELECTED. The app's select path clears it on every row before setting it "
                 "on one, but its insert path can also set it, so more than one row can carry it. "
                 "Accounts that have a "
                 "CREDENTIAL row but no accounts row are not reported. The app's per-account settings "
                 "(app open, registration, paid flags and storage) are in Yandex Disk Settings.\n"
                 "Not read: the children and local_uids tables, and passport-database, which holds "
                 "the library's auth cookies (secrets) and its method diary.",
        "paths": ('*/ru.yandex.disk/databases/PassportInternal.db*', '*/ru.yandex.disk/databases/SETTINGS*'),
        "output_types": "standard",
        "artifact_icon": "user",
    },
    "yandex_disk_settings": {
        "name": "Yandex Disk Settings",
        "description": "Per-account settings the Yandex Disk app stored: app open, registration, paid flags and storage",
        "author": "@AlexisBrignoni, @4n6Wizard, Claude",
        "creation_date": "2026-10-22",
        "last_update_date": "2026-10-22",
        "requirements": "none",
        "category": "Yandex Disk",
        "notes": "One row per account scope in PLAIN_SETTINGS_TABLE of ru.yandex.disk/databases/SETTINGS "
                 "that holds at least one of the settings below. The app scopes its per-account settings "
                 "as user@ followed by the account's CREDENTIAL.USER; Account is the scope with user@ "
                 "removed, and Account UID comes from the CREDENTIAL row whose USER matches it and is "
                 "blank when none does. Android User is taken from the storage path. Field meanings were "
                 "sourced from the decompiled Yandex Disk 6.90.0 app (SETTINGS version 16). The committed "
                 "test data is synthetic: databases built from the app's own schema with invented "
                 "values.\nLast App Open is last_open_app_time, the device clock in milliseconds that the "
                 "app writes on its user interface launch event; each write replaces the last. In 6.90.0 "
                 "that event is raised by the main screen when it is first created, by the login screen "
                 "after a login, by a base screen callback other screens inherit, and by the auto login "
                 "command, so it is not written on every return to the app. Registration Time is "
                 "registration_time, the text the app copies from the server's reg_time field at its user "
                 "settings fetch; the app names that field isoRegistrationTime and stores it as text. It "
                 "is read as an ISO 8601 time with an offset and reported in UTC, and left blank with the "
                 "value logged when it does not read that way. Paid is is_paid and Pro is IS_PRO, which "
                 "the app stores as 1 or 0; IS_PRO is copied from the server's disk_pro user feature "
                 "toggle, which the app's code names isPro, and what that toggle grants was not traced. "
                 "Storage Capacity, Storage Used, Disk Size, Mail Size and Trash Size are "
                 "capacity_info_total, capacity_info_used, capacity_info_disk_size, "
                 "capacity_info_mail_size and capacity_info_trash_size, the server's total_space, "
                 "used_space, disk_size, mail_size and trash_size as stored the last time the app fetched "
                 "its disk information from the server (two code paths write them); their unit is not "
                 "stated in the app's code. The app stores -1 for capacity or used when the server sent "
                 "none, and -1 is reported blank. It stores 0 for the disk, mail and trash sizes when the "
                 "server sent none, so a 0 there is not a measured zero. A setting the table does not "
                 "hold reads blank. The upload file size limits stored beside these (max_file_size, "
                 "paid_max_file_size and the upload_file_size_limits entries) are copied from the server "
                 "and are not reported. Saved video positions from the same table are in Yandex Disk "
                 "Video Playback Positions; the account profile is in Yandex Disk Accounts.",
        "paths": ('*/ru.yandex.disk/databases/SETTINGS*',),
        "output_types": "standard",
        "artifact_icon": "settings",
    },
    "yandex_disk_video_positions": {
        "name": "Yandex Disk Video Playback Positions",
        "description": "Saved playback positions the Yandex Disk app's video viewer kept for each account",
        "author": "@AlexisBrignoni, @4n6Wizard, Claude",
        "creation_date": "2026-10-22",
        "last_update_date": "2026-10-22",
        "requirements": "none",
        "category": "Yandex Disk",
        "notes": "One row per entry of the video_timecodes setting in PLAIN_SETTINGS_TABLE of "
                 "ru.yandex.disk/databases/SETTINGS, which holds one such setting per account scope "
                 "(user@ followed by the account). Account is the scope with user@ removed; Account UID "
                 "comes from the CREDENTIAL row whose USER matches it and is blank when none does. "
                 "Android User is taken from the storage path. Field meanings were sourced from the "
                 "decompiled Yandex Disk 6.90.0 app. The committed test data is synthetic: databases "
                 "built from the app's own schema with invented values.\n"
                 "The setting is a JSON list of entries, each keyed by a server path and an ETag with "
                 "a position in milliseconds; the ETag can be null and then reads blank. When the video "
                 "viewer screen stops (it is closed, left, or the app goes to the background) the app "
                 "takes the video's duration, from the stream information or the player, and the "
                 "playback position the player reports. It removes the video's entry when the duration "
                 "is 30 seconds or less, the position is 10 seconds or less, or the position is within "
                 "10 seconds of the end; otherwise it saves the position minus 5 seconds. When the "
                 "duration is unknown (0) it does neither. Stored Position is the saved value and "
                 "Position When Viewer Stopped adds the 5 seconds back. A removal changes only the "
                 "app's in-memory list and reaches the setting when the app next writes it, which a "
                 "later save or the path rewrite command below does, so a stored entry can belong to a "
                 "video that was later stopped near its end. A video with no entry may never have been "
                 "opened in the viewer, may have been stopped under a removal condition, or may have "
                 "been pushed out of the 11-entry cache by later videos.\n"
                 "The app keeps at most 11 entries in a least recently used cache and writes them in "
                 "the cache's order, least recently used first. Reading an entry, which the viewer does "
                 "when it opens a video, counts as a use. Recency Rank counts from the end of the "
                 "stored list, so 1 is the entry most recently used as of the last save. The setting "
                 "records no time, so the rank orders entries without dating them. A separate app "
                 "command rewrites an entry's path when it is given a path change and keeps the "
                 "position; which actions send it was not traced.\n"
                 "Cloud File Match compares each entry with the account's DISK table (see Yandex Disk "
                 "Cloud Files) by path: Same ETag, Different ETag, or Not listed when DISK holds no row "
                 "at that path or no DISK database was found for the account (for instance when Account "
                 "UID is blank). Duration (as stored) and Size (bytes) come from that DISK row. A saved "
                 "position shows that the viewer screen for that video stopped with the player at "
                 "Position When Viewer Stopped, under this account's settings on this device; it is not "
                 "evidence of who watched it or that it played continuously.",
        "paths": ('*/ru.yandex.disk/databases/SETTINGS*', '*/ru.yandex.disk/databases/*_disk*'),
        "output_types": "standard",
        "artifact_icon": "film",
    },
    "yandex_disk_trash": {
        "name": "Yandex Disk Trash",
        "description": "Items the Yandex Disk app listed in each account's server trash, with pending trash actions",
        "author": "@AlexisBrignoni, @4n6Wizard, Claude",
        "creation_date": "2026-10-22",
        "last_update_date": "2026-10-22",
        "requirements": "none",
        "category": "Yandex Disk",
        "notes": "One row per row of the TRASH table in ru.yandex.disk/databases/<uid>_trash.db, one "
                 "database per signed-in account; Account UID is the number in the file name and Android "
                 "User is taken from the storage path. Field meanings were sourced from the decompiled "
                 "Yandex Disk 6.90.0 app (trash database version 2). The committed test data is "
                 "synthetic: databases built from the app's own schema with invented values.\n"
                 "The app fills TRASH from the server's trash listing and, when a listing completes, "
                 "deletes local rows the listing did not return. A row is therefore an item that was in "
                 "the account's server trash at the app's last trash listing. Deleted is the server's "
                 "deleted time for the item, parsed from ISO 8601 to milliseconds and reported in UTC; "
                 "it is blank when the app stored 0, which it does when the server sent no time. Trash "
                 "Path is the server's path for the item inside the trash; the item's original location "
                 "is parsed by the app but not stored, so it is not available here. ETag is the server's "
                 "md5 field for the item.\n"
                 "Completed In App reads Yes (1) when the app finished a delete forever, restore or empty "
                 "trash for the item on the server, which hides it from the app's trash view, and No (0) "
                 "otherwise. Pending Action comes from the OPERATIONS table: Empty trash (0), Delete "
                 "forever (1) or Restore (2), with its state Queued (0), Sent (1) or Failed (2). An empty "
                 "trash action has no path and is shown on every row. OPERATIONS.added is an ordering "
                 "counter, not a time, and is not reported.",
        "paths": ('*/ru.yandex.disk/databases/*_trash.db*',),
        "output_types": "standard",
        "artifact_icon": "trash-2",
    },
    "yandex_disk_downloads": {
        "name": "Yandex Disk Downloads",
        "description": "Downloads in the Yandex Disk download queue, with the local file where the extraction holds it",
        "author": "@AlexisBrignoni, @4n6Wizard, Claude",
        "creation_date": "2026-10-22",
        "last_update_date": "2026-10-22",
        "requirements": "none",
        "category": "Yandex Disk",
        "notes": "One row per row of the queue table in ru.yandex.disk/databases/<uid>_download_queue, "
                 "one database per signed-in account; Account UID is the number in the file name and "
                 "Android User is taken from the storage path. Field meanings were sourced from the "
                 "decompiled Yandex Disk 6.90.0 app (download queue database version 5). The committed "
                 "test data is synthetic: databases built from the app's own schema with invented "
                 "values.\n"
                 "The table has no time column, so the rows carry no times. Cloud Path is the path of "
                 "the item to download; for a public file or folder the form of the stored path was "
                 "not traced. Local Folder is the local destination folder the app recorded; it is blank "
                 "on sync downloads and on some downloads started in the app. Type reads Audio (50), UI "
                 "download (100), Foreign album item (110), Public file (150), Public folder (200), Sync "
                 "(300) or None (-1), and State reads Queued (0), Done (1) or Inactive (2), the stored "
                 "number kept in brackets. Public Link Key is the key of the public link the download "
                 "came from. Password Token is the token for a password-protected public link and is "
                 "reported only as Present or Absent. The albumId and albumItemId columns, which foreign "
                 "album downloads fill, are not reported.\n"
                 "Local File shows the file at Local Folder and File Name (the cloud file name when File "
                 "Name is blank) when the extraction holds it. The parser searches only the folders the "
                 "queue rows name, under media/<user> (the data/media/<user> form an extraction holds) "
                 "or storage/emulated/<user>, and only after it has read queue rows; only a file whose "
                 "extraction path ends with that path's shared-storage form is shown, and its type is "
                 "taken from its bytes. A file found "
                 "there is what the extraction holds at that path now, which need not be the downloaded "
                 "copy. A blank Local File means no file was found at that path, or Local Folder is "
                 "blank or not a shared-storage path.",
        "paths": ('*/ru.yandex.disk/databases/*_download_queue*',),
        "output_types": "standard",
        "artifact_icon": "cloud-download",
    },
    "yandex_disk_notes": {
        "name": "Yandex Disk Notes",
        "description": "Notes stored by the Yandex Disk app, with their text and attachment names",
        "author": "@AlexisBrignoni, @4n6Wizard, Claude",
        "creation_date": "2026-10-22",
        "last_update_date": "2026-10-22",
        "requirements": "none",
        "category": "Yandex Disk",
        "notes": "One row per row of the note table in ru.yandex.disk/databases/<uid>_notes.db, joined "
                 "to content and attach on the note's local_id; one database per signed-in account. "
                 "Account UID is the number in the file name and Android User is taken from the storage "
                 "path. Field meanings were sourced from the decompiled Yandex Disk 6.90.0 app (notes "
                 "database version 2). The committed test data is synthetic: databases built from the "
                 "app's own schema with invented values.\n"
                 "Modified is note.mtime in milliseconds, reported in UTC: the time the app wrote on a "
                 "local edit, or the server's modified time for a note it synced. Title is the note's "
                 "title. Snippet is the stored snippet; on a local edit the app builds it from the first "
                 "two non-blank lines of the text. Text is built from content.body, which the app "
                 "stores as a JSON tree of nodes with attributes, name, children and data; Text joins the "
                 "data values in document order, one line per top-level node, and drops the formatting "
                 "the tree carries. Pinned reads Yes when the note is pinned. Hidden is reported as "
                 "stored (Yes or No); the app sets it from server tags, whose meaning was not "
                 "established, and on a local hide action. Local Changes reads None (0), Pin or hide changed (1) or Content and meta "
                 "changed (2), for changes made on the device and not yet synced.\n"
                 "Attachments lists each attach row's name with its file state: Waiting download (0), "
                 "Waiting upload (1), Waiting delete (2) or OK (3). Attachment Resource IDs are the "
                 "resource ids the notes service gave the attachments; no join from them to the cloud "
                 "file listing was found, so whether they match a Yandex Disk Cloud Files Resource ID "
                 "was not established. Local copies of attachments are not resolved or shown in this "
                 "version.",
        "paths": ('*/ru.yandex.disk/databases/*_notes.db*',),
        "output_types": "standard",
        "artifact_icon": "file-text",
    },
}

import json
import os
import re
from datetime import datetime, timezone
from urllib.parse import parse_qs

from scripts.ilapfuncs import artifact_processor, check_in_media, convert_unix_ts_to_utc, \
    get_sqlite_db_records, logfunc
from scripts.artifacts.storagePathViews import canonical_path, unique_files

PASSPORT_STORE = re.compile(r'(?:^|/)ru\.yandex\.disk/databases/(PassportInternal\.db|SETTINGS)$')
ENVIRONMENT = {1: 'Production', 2: 'Team production', 3: 'Testing', 4: 'Team testing', 5: 'RC'}

DISK_DB = re.compile(r'(?:^|/)ru\.yandex\.disk/databases/(\d+)_disk$')
TRASH_DB = re.compile(r'(?:^|/)ru\.yandex\.disk/databases/(\d+)_trash\.db$')
DOWNLOAD_DB = re.compile(r'(?:^|/)ru\.yandex\.disk/databases/(\d+)_download_queue$')
NOTES_DB = re.compile(r'(?:^|/)ru\.yandex\.disk/databases/(\d+)_notes\.db$')
# A path the app recorded as the device sees shared storage, and the folder an extraction holds it in.
SHARED_STORAGE = re.compile(r'^/(?:storage/emulated|sdcard)/?(\d*)/')
STORAGE_USER = re.compile(r'\x00(?:ce|de):(\d+)\x00')

OFFLINE_MARK = {0: 'Not marked', 1: 'Marked', 2: 'In marked folder'}
SHARE_GROUP = {0: 'Other', 1: 'Family'}
QUEUE_STATE = {0: 'Legacy code', 1: 'Queued', 2: 'Paused or failed', 3: 'Done', 4: 'Legacy code'}
UPLOAD_TYPE = {0: 'Manual', 1: 'Camera autoupload', 3: 'Re-upload'}
ERROR_REASON = {0: 'Generic', 1: 'Name conflict', 2: 'File too big', 3: 'Local file unavailable',
                4: 'Local file not readable', 5: 'Files limit or paused',
                6: 'Shared folder files limit', 8: 'Disk read-only'}
QUEUE_MEDIA_TYPE = {0: 'Other', 100: 'Image', 200: 'Video'}
CLEANUP_STATE = {0: 'Unchecked', 1: 'Selected for check', 2: 'Local file deleted',
                 3: 'Not checked again', 4: 'Error', 5: 'Waiting for indexing'}

DISK_COLUMNS = ('PARENT', 'NAME', 'IS_DIR', 'SIZE', 'ETAG', 'ETAG_LOCAL', 'LAST_MODIFIED', 'ETIME',
                'LAST_ACCESS', 'MIME_TYPE', 'MEDIA_TYPE', 'PUBLIC_URL', 'SHARED', 'READONLY',
                'SHARE_GROUP_TYPE', 'OFFLINE_MARK', 'LATITUDE', 'LONGITUDE', 'WIDTH', 'HEIGHT',
                'DURATION', 'RESOURCE_ID')
QUEUE_COLUMNS = ('_id', 'src_name', 'dest_dir', 'dest_name', 'date', 'uploaded_size', 'state',
                 'error_reason', 'md5', 'md5_time', 'is_dir', 'from_autoupload', 'ETIME', 'SIZE',
                 'MEDIA_TYPE', 'sha256', 'uploaded_time', 'user')
QUEUE_EXT_COLUMNS = ('cleanup_state', 'uploaded_path', 'added_to_queue_time', 'upload_started_time',
                     'enqueued_network')


def _disk_databases(context, pattern=DISK_DB):
    """(Android user, account uid, path) for every per-account database, one copy per storage view.

    An Android extraction carries the app's private directory under data/data, data/user/0
    and data_mirror, so the seeker's list would open each database once per view. The
    Android user comes from the storage view, so one Yandex account signed in on two
    Android users (a work profile, for instance) stays two sets of rows.
    """
    found = []
    for path in unique_files(context):
        path = str(path)
        if os.path.isdir(path):
            continue
        match = pattern.search(path.replace('\\', '/'))
        if not match:
            continue
        key, _ = canonical_path(context.get_relative_path(path))
        user = STORAGE_USER.search(key)
        found.append((user.group(1) if user else '', match.group(1), path))
    return sorted(found)


def _columns(db_path, table):
    """The column names a table has in this database, empty when the table is absent."""
    return {r[1] for r in get_sqlite_db_records(db_path, f'PRAGMA table_info("{table}")')}


def _select(present, wanted, alias=''):
    """A select list naming every wanted column, NULL for the ones this schema lacks."""
    prefix = f'{alias}.' if alias else ''
    return ', '.join(f'{prefix}"{c}"' if c in present else 'NULL' for c in wanted)


def _ms(value):
    """A stored millisecond epoch as a UTC datetime, blank for NULL or 0."""
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value) / 1000)
    except (TypeError, ValueError, OverflowError):
        return ''


def _label(mapping, value):
    if value is None or value == '':
        return ''
    try:
        code = int(value)
    except (TypeError, ValueError):
        return f'Unknown ({value})'
    return f'{mapping[code]} ({code})' if code in mapping else f'Unknown ({code})'


def _coordinate(value):
    """A stored coordinate, blank for NULL or the app's -1 marker for a missing value."""
    if value is None or value == '' or value == -1:
        return ''
    return value


def _path(parent, name):
    if not parent:
        return name or ''
    return f'{parent.rstrip("/")}/{name or ""}'


@artifact_processor
def yandex_disk_cloud_files(context):
    data_list = []
    sources = []
    for android_user, uid, db_path in _disk_databases(context):
        read_rows = False
        for table in ('DISK', 'FOREIGN_DISK'):
            present = _columns(db_path, table)
            if not present:
                continue
            owner = '"OWNER_UID"' if 'OWNER_UID' in present else 'NULL'
            query = f'SELECT {_select(present, DISK_COLUMNS)}, {owner} FROM "{table}"'
            for r in get_sqlite_db_records(db_path, query):
                read_rows = True
                data_list.append((
                    _ms(r[6]), _ms(r[7]), _ms(r[8]), android_user, uid, r[22] or '',
                    _path(r[0], r[1]), 'Folder' if r[2] else 'File', r[3],
                    r[9] or '', r[10] or '', r[4] or '', r[5] or '', r[11] or '',
                    r[12], r[13], _label(SHARE_GROUP, r[14]), _label(OFFLINE_MARK, r[15]),
                    _coordinate(r[16]), _coordinate(r[17]), r[18], r[19], r[20], r[21] or ''))
        if read_rows:
            sources.append(db_path)
        else:
            logfunc(f'Yandex Disk: no DISK rows read from {os.path.basename(db_path)}')

    data_headers = (
        ('Last Modified', 'datetime'), ('EXIF Date', 'datetime'),
        ('Local Copy Last Access', 'datetime'), 'Android User', 'Account UID', 'Owner UID', 'Path',
        'Type',
        'Size (bytes)', 'MIME Type', 'Media Type', 'ETag', 'Local Copy MD5', 'Public URL',
        'Shared', 'Read Only', 'Share Group', 'Offline Mark', 'Latitude', 'Longitude', 'Width',
        'Height', 'Duration (as stored)', 'Resource ID')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def yandex_disk_uploads(context):
    data_list = []
    sources = []
    pending = []
    for android_user, uid, db_path in _disk_databases(context):
        present = _columns(db_path, 'DISK_QUEUE')
        if not present:
            continue
        ext = _columns(db_path, 'DISK_QUEUE_EXT')
        if ext and 'upload_id' in ext:
            query = (f'SELECT {_select(present, QUEUE_COLUMNS, "q")}, '
                     f'{_select(ext, QUEUE_EXT_COLUMNS, "e")} '
                     'FROM DISK_QUEUE q LEFT JOIN DISK_QUEUE_EXT e ON e.upload_id = q._id '
                     'ORDER BY q._id')
        else:
            nulls = ', '.join('NULL' for _ in QUEUE_EXT_COLUMNS)
            query = f'SELECT {_select(present, QUEUE_COLUMNS)}, {nulls} FROM DISK_QUEUE ORDER BY _id'
        read_rows = False
        for r in get_sqlite_db_records(db_path, query):
            read_rows = True
            upload_type = r[11]
            stored_date = r[4]
            date_taken = _ms(stored_date) if upload_type == 1 else ''
            queued = _ms(stored_date) if upload_type == 0 else ''
            other_date = stored_date if upload_type not in (0, 1) and stored_date else ''
            destination = _path(r[2], r[3])
            pending.append((None if r[10] else r[1], (
                _ms(r[16]), date_taken, queued, _ms(r[12]), _ms(r[20]), _ms(r[21]), _ms(r[9]),
                android_user, uid, r[17] or '', _label(UPLOAD_TYPE, upload_type), _label(QUEUE_STATE, r[6]),
                _label(ERROR_REASON, r[7]), 'Folder' if r[10] else 'File',
                _label(QUEUE_MEDIA_TYPE, r[14]), r[1] or ''), (destination, r[19] or '',
                r[13], r[5], r[8] or '', r[15] or '', _label(CLEANUP_STATE, r[18]),
                r[22] or '', other_date, r[0])))
        if read_rows:
            sources.append(db_path)

    staged = _stage_shared(context, [local for local, _, _ in pending if local])
    for local, head, tail in pending:
        data_list.append(head + (_local_media(staged, local) if local else '',) + tail)

    data_headers = (
        ('Uploaded', 'datetime'), ('Date Taken', 'datetime'), ('Queued', 'datetime'),
        ('ETIME', 'datetime'), ('Autoupload Queued', 'datetime'),
        ('Upload Started', 'datetime'), ('File Modified When Hashed', 'datetime'),
        'Android User', 'Account UID', 'Account', 'Upload Type', 'Status', 'Error', 'Type',
        'Media Type',
        'Local Path', ('Local File', 'media'), 'Destination', 'Uploaded Path', 'Size (bytes)',
        'Uploaded (bytes)', 'MD5',
        'SHA-256', 'Local Cleanup', 'Network', 'Date (ms, as stored)', 'Queue ID')
    return data_headers, data_list, '\n'.join(sources)


def _passport_containers(context):
    """{container key: {'user': Android user, 'PassportInternal.db': path, 'SETTINGS': path}}.

    The key is the database folder with the storage view folded, so the Passport store and the
    SETTINGS database of one app data directory pair up, and two Android users stay apart.
    """
    found = {}
    for path in unique_files(context):
        path = str(path)
        if os.path.isdir(path):
            continue
        match = PASSPORT_STORE.search(path.replace('\\', '/'))
        if not match:
            continue
        key, _ = canonical_path(context.get_relative_path(path))
        folder = key.rsplit('/', 1)[0]
        user = STORAGE_USER.search(key)
        entry = found.setdefault(folder, {'user': user.group(1) if user else ''})
        entry[match.group(1)] = path
    return found


def _rows_by_name(db_path, table, wanted):
    """Rows of a table as dicts of the wanted columns, NULL for columns this schema lacks."""
    present = _columns(db_path, table)
    if not present:
        return []
    return [dict(zip(wanted, r))
            for r in get_sqlite_db_records(db_path, f'SELECT {_select(present, wanted)} FROM "{table}"')]


def _legacy_extra(value):
    """The extra_data values of legacy_extra_data_body: "@jsn" + {"extra_data": {key: {"val": ...}}}."""
    if not value:
        return {}
    text = value[4:] if value.startswith('@jsn') else value
    try:
        extra = json.loads(text).get('extra_data') or {}
    except (ValueError, AttributeError):
        return {}
    return {k: v.get('val') for k, v in extra.items() if isinstance(v, dict)}


def _json_object(text):
    """A JSON object from text, or {} when the text is not one (ciphertext, for instance)."""
    try:
        value = json.loads(text)
    except ValueError:
        return {}
    return value if isinstance(value, dict) else {}


def _user_info(body, secure_blob):
    """(user info dict, store it came from, secure blob state, master token present in the blob)."""
    info = _json_object(body) if body else {}
    source = 'user info' if info else ''
    if not secure_blob:
        return info, source, 'Absent', False
    if not secure_blob.startswith('v=1&'):
        return info, source, 'Encrypted, not readable', False
    parts = parse_qs(secure_blob, keep_blank_values=True)
    blob_info = (parts.get('userInfo') or [''])[0]
    master = (parts.get('masterToken') or [''])[0] not in ('', '~')
    if not info and blob_info and blob_info != '~':
        info = _json_object(blob_info)
        source = 'secure blob user info' if info else ''
    return info, source, 'Plaintext', master


def _seconds(value):
    """A stored Unix seconds value as a UTC datetime, blank for NULL or 0."""
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value))
    except (TypeError, ValueError, OverflowError):
        return ''


# capacity_info_<key> settings, in the column order the Accounts artifact reports them.
CAPACITY_KEYS = ('total', 'used', 'disk_size', 'mail_size', 'trash_size')


def _user_settings(settings_path):
    """{scope: {name: value}} for the per-account (user@...) scopes of PLAIN_SETTINGS_TABLE."""
    scoped = {}
    for r in _rows_by_name(settings_path, 'PLAIN_SETTINGS_TABLE', ('SCOPE', 'NAME', 'VALUE')):
        scope = str(r['SCOPE'] or '')
        if scope.startswith('user@'):
            scoped.setdefault(scope, {})[r['NAME']] = r['VALUE']
    return scoped


def _iso(value):
    """An ISO 8601 text time with an offset as a UTC datetime; blank, and logged, otherwise."""
    if not value:
        return ''
    text = str(value).strip()
    try:
        parsed = datetime.fromisoformat(text[:-1] + '+00:00' if text.endswith('Z') else text)
    except ValueError:
        parsed = None
    if parsed is None or parsed.tzinfo is None:
        logfunc(f'Yandex Disk: registration_time not read as an ISO 8601 time with an offset: {text}')
        return ''
    return parsed.astimezone(timezone.utc)


def _capacity(value):
    """A stored byte count, blank when absent or the app's -1 for a value the server did not send."""
    if value is None or value == '':
        return ''
    try:
        number = int(value)
    except (TypeError, ValueError):
        return value
    return '' if number == -1 else number


def _present(flag):
    return 'Present' if flag else 'Absent'


def _yes_no(value):
    if value is None or value == '':
        return ''
    return 'Yes' if str(value).lower() in ('1', 'true') else 'No'


@artifact_processor
def yandex_disk_accounts(context):
    data_list = []
    sources = []
    for _, stores in sorted(_passport_containers(context).items()):
        passport = stores.get('PassportInternal.db')
        if not passport:
            continue
        settings = stores.get('SETTINGS')
        credentials = {}
        if settings:
            for c in _rows_by_name(settings, 'CREDENTIAL', ('UID', 'LAST_TIME_LOGGED_IN', 'IS_SELECTED')):
                credentials[str(c['UID'])] = c
        actions = {a['uid']: a for a in _rows_by_name(
            passport, 'accounts_last_action', ('uid', 'timestamp', 'last_action', 'local_timestamp'))}
        tokens = {}
        for t in _rows_by_name(passport, 'tokens', ('uid', 'client_id', 'client_token')):
            tokens.setdefault(t['uid'], []).append(t)
        push = {g['uid'] for g in _rows_by_name(passport, 'gcm_subscriptions', ('uid', 'gcm_token_hash'))
                if g['gcm_token_hash']}
        accounts = _rows_by_name(passport, 'accounts', (
            'name', 'master_token_value', 'uid', 'user_info_body', 'user_info_meta', 'stash_body',
            'legacy_account_type', 'legacy_affinity', 'legacy_extra_data_body', 'secure_blob'))
        for a in accounts:
            stored_uid = str(a['uid'] or '')
            env, _, uid_value = stored_uid.partition(':') if ':' in stored_uid else ('', '', stored_uid)
            legacy = _legacy_extra(a['legacy_extra_data_body'])
            info, info_source, blob_state, blob_master = _user_info(a['user_info_body'], a['secure_blob'])
            profile_source = '; '.join(x for x in (info_source, 'legacy extra data' if legacy else '') if x)
            # An encrypted blob holds any master token inside the ciphertext, so absence is unknown.
            master_token = '' if blob_state.startswith('Encrypted') else \
                _present(a['master_token_value'] or blob_master)
            action = actions.get(stored_uid, {})
            cred = credentials.get(uid_value, {})
            account_tokens = tokens.get(stored_uid, [])
            meta = str(a['user_info_meta'] or '')
            data_list.append((
                _ms(action.get('local_timestamp')), _seconds(action.get('timestamp')),
                _seconds(meta.split(':', 1)[0]) if meta.split(':', 1)[0].isdigit() else '',
                _ms(cred.get('LAST_TIME_LOGGED_IN')),
                stores['user'], uid_value, _label(ENVIRONMENT, env) if env else '', a['name'] or '',
                info.get('display_name') or legacy.get('_display_name') or '',
                info.get('public_name') or '', info.get('display_login') or '',
                info.get('native_default_email') or '', info.get('firstname') or '',
                info.get('lastname') or '', info.get('birthday') or '',
                info.get('avatar_url') or legacy.get('_default_avatar') or '',
                a['legacy_account_type'] or '',
                action.get('last_action') or '', _yes_no(cred.get('IS_SELECTED')),
                _yes_no(legacy.get('_is_staff')), _yes_no(legacy.get('_is_beta_tester')),
                master_token, blob_state,
                _present(legacy.get('disk.pincode') or legacy.get('mail.pincode')),
                sum(1 for t in account_tokens if t['client_token']),
                ', '.join(sorted({t['client_id'] for t in account_tokens if t['client_id']})),
                _present(stored_uid in push), profile_source))
        if accounts:
            sources.append(passport)
            if settings:
                sources.append(settings)

    data_headers = (
        ('Last Action Time', 'datetime'), ('Token Issued', 'datetime'),
        ('User Info Time', 'datetime'), ('Added To Disk App', 'datetime'), 'Android User',
        'Account UID', 'Environment', 'Account Name', 'Display Name', 'Public Name', 'Display Login',
        'Default Email', 'First Name', 'Last Name', 'Birthday', 'Avatar URL', 'Account Type', 'Last Action',
        'Current Disk Account', 'Staff', 'Beta Tester', 'Master Token', 'Secure Blob',
        'Pin Codes', 'Client Tokens', 'Client IDs', 'Push Token Hash', 'Profile Source')
    return data_headers, data_list, '\n'.join(sources)


# Settings the Settings artifact reports; a scope holding none of them gets no row.
SETTINGS_KEYS = ('last_open_app_time', 'registration_time', 'is_paid', 'IS_PRO') + \
    tuple(f'capacity_info_{k}' for k in CAPACITY_KEYS)


@artifact_processor
def yandex_disk_settings(context):
    data_list = []
    sources = []
    for _, stores in sorted(_passport_containers(context).items()):
        settings = stores.get('SETTINGS')
        if not settings:
            continue
        uids = {str(c['USER']): str(c['UID'] or '')
                for c in _rows_by_name(settings, 'CREDENTIAL', ('USER', 'UID')) if c['USER']}
        read_rows = False
        for scope, pref in sorted(_user_settings(settings).items()):
            if not any(k in pref for k in SETTINGS_KEYS):
                continue
            read_rows = True
            account = scope[len('user@'):]
            data_list.append((
                _ms(pref.get('last_open_app_time')), _iso(pref.get('registration_time')), stores['user'],
                uids.get(account, ''), account, _yes_no(pref.get('is_paid')), _yes_no(pref.get('IS_PRO')),
                *(_capacity(pref.get(f'capacity_info_{k}')) for k in CAPACITY_KEYS)))
        if read_rows:
            sources.append(settings)

    data_headers = (
        ('Last App Open', 'datetime'), ('Registration Time', 'datetime'), 'Android User', 'Account UID',
        'Account', 'Paid', 'Pro', 'Storage Capacity (as stored)', 'Storage Used (as stored)',
        'Disk Size (as stored)', 'Mail Size (as stored)', 'Trash Size (as stored)')
    return data_headers, data_list, '\n'.join(sources)

def _hms(ms):
    """Milliseconds as HH:MM:SS.mmm."""
    ms = int(ms)
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d}.{ms % 1000:03d}'


def _timecodes(raw, scope):
    """(path, etag, position ms) for each well-formed entry of a video_timecodes value, in stored order."""
    try:
        entries = json.loads(raw)
    except ValueError:
        logfunc(f'Yandex Disk: video_timecodes for {scope} is not JSON, not read')
        return []
    if not isinstance(entries, list):
        logfunc(f'Yandex Disk: video_timecodes for {scope} is not a list, not read')
        return []
    found = []
    for entry in entries:
        key = entry.get('key') if isinstance(entry, dict) else None
        value = entry.get('value') if isinstance(entry, dict) else None
        if not isinstance(key, dict) or not key.get('path') or isinstance(value, bool) \
                or not isinstance(value, int):
            logfunc(f'Yandex Disk: an entry of video_timecodes for {scope} has an unexpected shape, not read')
            continue
        found.append((key['path'], key.get('etag'), value))
    return found


def _disk_listing(db_path):
    """{path: DISK row} for one account's cloud file listing."""
    return {_path(r['PARENT'], r['NAME']): r
            for r in _rows_by_name(db_path, 'DISK', ('PARENT', 'NAME', 'ETAG', 'DURATION', 'SIZE'))}


@artifact_processor
def yandex_disk_video_positions(context):
    data_list = []
    sources = []
    disks = {(user, uid): path for user, uid, path in _disk_databases(context)}
    for _, stores in sorted(_passport_containers(context).items()):
        settings = stores.get('SETTINGS')
        if not settings:
            continue
        uids = {str(c['USER']): str(c['UID'] or '')
                for c in _rows_by_name(settings, 'CREDENTIAL', ('USER', 'UID')) if c['USER']}
        read_rows = False
        for scope, prefs in sorted(_user_settings(settings).items()):
            if not prefs.get('video_timecodes'):
                continue
            entries = _timecodes(prefs['video_timecodes'], scope)
            account = scope[len('user@'):]
            uid = uids.get(account, '')
            disk_path = disks.get((stores['user'], uid)) if uid else None
            listing = _disk_listing(disk_path) if disk_path else {}
            for rank, (path, etag, stored) in zip(range(len(entries), 0, -1), entries):
                read_rows = True
                cloud = listing.get(path)
                if cloud is None:
                    match = 'Not listed'
                else:
                    match = 'Same ETag' if (cloud['ETAG'] or None) == (etag or None) else 'Different ETag'
                data_list.append((
                    rank, stores['user'], uid, account, path, _hms(stored), stored, _hms(stored + 5000),
                    cloud['DURATION'] if cloud else '', cloud['SIZE'] if cloud else '', etag or '', match))
            if entries and disk_path and disk_path not in sources:
                sources.append(disk_path)
        if read_rows:
            sources.insert(0, settings)

    data_headers = (
        'Recency Rank', 'Android User', 'Account UID', 'Account', 'Video Path', 'Stored Position',
        'Stored Position (ms)', 'Position When Viewer Stopped', 'Duration (as stored)', 'Size (bytes)', 'ETag',
        'Cloud File Match')
    return data_headers, data_list, '\n'.join(sources)

def _shared_tails(recorded):
    """The forms a recorded /storage/emulated/<user>/... path takes inside an extraction.

    A full file system extraction holds shared storage under data/media/<user> (or
    userdata/media/<user>); a logical one can keep storage/emulated/<user>. Both are
    matched as path endings.
    """
    text = str(recorded or '').replace('\\', '/')
    match = SHARED_STORAGE.match(text)
    if not match:
        return ()
    user, rest = match.group(1) or '0', text[match.end():]
    return (f'media/{user}/{rest}', f'emulated/{user}/{rest}')


def _fn_escape(text):
    """Escape fnmatch metacharacters so a folder name is matched literally."""
    return ''.join(f'[{c}]' if c in '*?[' else c for c in text)


def _stage_shared(context, recorded_paths):
    """Extraction-relative path -> staged path for the folders the recorded paths name.

    Only those folders are searched, and only when there are recorded paths, so an
    extraction without Yandex Disk rows stages no shared storage.
    """
    folders = set()
    for recorded in recorded_paths:
        for tail in _shared_tails(recorded):
            if '/' in tail:
                folders.add(tail.rsplit('/', 1)[0])
    if not folders:
        return {}
    seeker = context.get_seeker()
    staged = {}
    for folder in sorted(folders):
        for found in seeker.search(f'*/{_fn_escape(folder)}/*'):
            found = str(found)
            if os.path.isdir(found):
                continue
            relative = str(context.get_relative_path(found)).replace('\\', '/').lstrip('/')
            staged.setdefault(relative, found)
    return staged


def _local_media(staged, recorded):
    """The checked-in media for the file at a recorded device path, or ''.

    Only a file whose extraction path ends with the recorded path's shared-storage form is
    taken. A file that only shares the name is not.
    """
    for tail in _shared_tails(recorded):
        for relative, candidate in staged.items():
            if relative == tail or relative.endswith('/' + tail):
                return check_in_media(candidate, os.path.basename(candidate)) or ''
    return ''


TRASH_OPERATION = {0: 'Empty trash', 1: 'Delete forever', 2: 'Restore'}
TRASH_OPERATION_STATE = {0: 'Queued', 1: 'Sent', 2: 'Failed'}
DOWNLOAD_TYPE = {-1: 'None', 50: 'Audio', 100: 'UI download', 110: 'Foreign album item',
                 150: 'Public file', 200: 'Public folder', 300: 'Sync'}
DOWNLOAD_STATE = {0: 'Queued', 1: 'Done', 2: 'Inactive'}
NOTE_MODIFIED = {0: 'None', 1: 'Pin or hide changed', 2: 'Content and meta changed'}
ATTACH_STATE = {0: 'Waiting download', 1: 'Waiting upload', 2: 'Waiting delete', 3: 'OK'}


@artifact_processor
def yandex_disk_trash(context):
    data_list = []
    sources = []
    for android_user, uid, db_path in _disk_databases(context, TRASH_DB):
        operations = _rows_by_name(db_path, 'OPERATIONS', ('path', 'type', 'state'))
        rows = _rows_by_name(db_path, 'TRASH', (
            'path', 'dir', 'etag', 'displayName', 'size', 'deleted', 'mimeType', 'mediaType',
            'onlyForSync'))
        for t in rows:
            pending = '; '.join(
                f"{_label(TRASH_OPERATION, o['type'])}: {_label(TRASH_OPERATION_STATE, o['state'])}"
                for o in operations if o['path'] == t['path'] or (o['path'] is None and o['type'] == 0))
            data_list.append((
                _ms(t['deleted']), android_user, uid, t['path'] or '', t['displayName'] or '',
                'Folder' if t['dir'] else 'File', t['size'], t['mimeType'] or '', t['mediaType'] or '',
                t['etag'] or '', _label({0: 'No', 1: 'Yes'}, t['onlyForSync']), pending))
        if rows:
            sources.append(db_path)

    data_headers = (
        ('Deleted', 'datetime'), 'Android User', 'Account UID', 'Trash Path', 'Name', 'Type',
        'Size (bytes)', 'MIME Type', 'Media Type', 'ETag', 'Completed In App', 'Pending Action')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def yandex_disk_downloads(context):
    data_list = []
    sources = []
    pending = []
    for android_user, uid, db_path in _disk_databases(context, DOWNLOAD_DB):
        rows = _rows_by_name(db_path, 'queue', (
            'id', 'serverPath', 'destinationDirectory', 'type', 'size', 'downloadedSize', 'state',
            'publicKey', 'token', 'destinationName'))
        for q in rows:
            name = q['destinationName'] or os.path.basename(str(q['serverPath'] or '').rstrip('/'))
            local = (f"{str(q['destinationDirectory']).rstrip('/')}/{name}"
                     if q['destinationDirectory'] and name else None)
            pending.append((local, (
                android_user, uid, q['serverPath'] or '', q['destinationDirectory'] or '',
                q['destinationName'] or ''), (_label(DOWNLOAD_TYPE, q['type']),
                _label(DOWNLOAD_STATE, q['state']), q['size'], q['downloadedSize'],
                q['publicKey'] or '', _present(q['token']), q['id'])))
        if rows:
            sources.append(db_path)

    staged = _stage_shared(context, [local for local, _, _ in pending if local])
    for local, head, tail in pending:
        data_list.append(head + (_local_media(staged, local) if local else '',) + tail)

    data_headers = (
        'Android User', 'Account UID', 'Cloud Path', 'Local Folder', 'File Name',
        ('Local File', 'media'), 'Type', 'State', 'Size (bytes)', 'Downloaded (bytes)',
        'Public Link Key', 'Password Token', 'Queue ID')
    return data_headers, data_list, '\n'.join(sources)


def _note_text(body):
    """The data values of a ContentJson tree in document order, one line per top-level node."""
    root = _json_object(body) if body else {}

    def collect(node, out):
        if isinstance(node, dict):
            if isinstance(node.get('data'), str):
                out.append(node['data'])
            for child in node.get('children') or []:
                collect(child, out)
        return out

    lines = []
    for top in root.get('children') or []:
        text = ''.join(collect(top, []))
        if text:
            lines.append(text)
    if not lines and isinstance(root.get('data'), str):
        lines.append(root['data'])
    return '\n'.join(lines)


@artifact_processor
def yandex_disk_notes(context):
    data_list = []
    sources = []
    for android_user, uid, db_path in _disk_databases(context, NOTES_DB):
        bodies = {c['local_id']: c['body'] for c in _rows_by_name(db_path, 'content', ('local_id', 'body'))}
        attachments = {}
        for a in _rows_by_name(db_path, 'attach', ('note_local_id', 'name', 'resource_id', 'file_status')):
            attachments.setdefault(a['note_local_id'], []).append(a)
        notes = _rows_by_name(db_path, 'note', (
            'local_id', 'remote_id', 'title', 'snippet', 'mtime', 'revision', 'pinned', 'hidden',
            'modified'))
        for n in notes:
            attached = attachments.get(n['local_id'], [])
            data_list.append((
                _ms(n['mtime']), android_user, uid, n['title'] or '', _note_text(bodies.get(n['local_id'])),
                n['snippet'] or '', _yes_no(n['pinned']), _yes_no(n['hidden']),
                _label(NOTE_MODIFIED, n['modified']),
                '\n'.join(f"{a['name'] or ''} ({_label(ATTACH_STATE, a['file_status'])})" for a in attached),
                '\n'.join(a['resource_id'] or '' for a in attached), n['remote_id'] or '', n['revision']))
        if notes:
            sources.append(db_path)

    data_headers = (
        ('Modified', 'datetime'), 'Android User', 'Account UID', 'Title', 'Text', 'Snippet',
        'Pinned', 'Hidden', 'Local Changes', 'Attachments', 'Attachment Resource IDs', 'Remote ID',
        'Revision')
    return data_headers, data_list, '\n'.join(sources)

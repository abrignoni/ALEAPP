# pylint: disable=W0718
__artifacts_v2__ = {
    "get_snapchat_feeds": {
        "name": "Snapchat - Feeds",
        "description": "Snapchat feed (last interaction per conversation)",
        "author": "@A-725-K", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat", "notes": "",
        "paths": ('*/com.snapchat.android/databases/main.db*', '*/com.snapchat.android/databases/tcspahn.db*'),
        "output_types": "standard", "artifact_icon": "rss",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.snapchat.android vc 238022 | 0 rows",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 0 rows",
            "samsungs20_a13": "Android 13 | com.snapchat.android vc 260222 | 0 rows",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android vc 101539 | 0 rows",
        },
    },
    "get_snapchat_friends": {
        "name": "Snapchat - Friends",
        "description": "Snapchat friends / contacts",
        "author": "@A-725-K", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat", "notes": "",
        "paths": ('*/com.snapchat.android/databases/main.db*', '*/com.snapchat.android/databases/tcspahn.db*'),
        "output_types": "standard", "artifact_icon": "users",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 4 rows",
            "kevin_pocox7_a15": "Android 15 | com.snapchat.android vc 238022 | 0 rows",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 4 rows",
            "samsungs20_a13": "Android 13 | com.snapchat.android vc 260222 | 0 rows",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 6 rows",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android vc 101539 | 5 rows",
        },
    },
    "get_snapchat_messages": {
        "name": "Snapchat - Messages",
        "description": "Snapchat chat messages",
        "author": "@A-725-K", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat", "notes": "",
        "paths": ('*/com.snapchat.android/databases/main.db*', '*/com.snapchat.android/databases/tcspahn.db*'),
        "output_types": "standard", "artifact_icon": "message",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.snapchat.android vc 238022 | 0 rows",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 0 rows",
            "samsungs20_a13": "Android 13 | com.snapchat.android vc 260222 | 0 rows",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android vc 101539 | 0 rows",
        },
    },
    "get_snapchat_arroyo_messages": {
        "name": "Snapchat - Messages (arroyo.db)",
        "description": "Chat message records from the conversation_message table in arroyo.db, "
                       "both the rows a normal read returns and rows that are present only before "
                       "the write-ahead log is applied, distinguished by the Record Origin column. "
                       "Sender and participant UUIDs are resolved against the Friend table in "
                       "main.db, and message text is decoded from the message_content protobuf on "
                       "rows where content_type is 1. WAL frames are not parsed, so absence of a "
                       "message here is not evidence it did not exist.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07", "last_update_date": "2026-08-11",
        "requirements": "blackboxprotobuf", "category": "Snapchat",
        "notes": "Newer Snapchat builds keep conversations in arroyo.db; the older Snapchat - "
                 "Messages artifact reads main.db and tcspahn.db and returns nothing on them.\n"
                 "Record Origin. Live rows come back from a normal read. Recovered rows do not: "
                 "they sit in the database file as of its last checkpoint and are gone once the "
                 "write-ahead log is applied. Recovery Method and Recovery Location are filled in "
                 "only on Recovered rows. The two sets cannot overlap.\n"
                 "Why a Recovered row is absent is not established here. Removal by the app, a "
                 "server re-sync, and deletion all produce the same result. Most Recovered rows on "
                 "the tested image held Team Snapchat broadcast content, which is one image rather "
                 "than a general property.\n"
                 "Method. The file is read twice through SQLite, immutable=1 to ignore the log and "
                 "mode=ro to apply it, then compared on primary key rather than row count. SQLite "
                 "does the decoding, so column names, type affinity and overflow pages are handled "
                 "for us. The glob keeps the -wal and -shm sidecars: this database reads 11 "
                 "conversation_message rows alone and 8 with its log applied.\n"
                 "Message text comes from the message_content protobuf at 4 > 4 > 2 > 1, derived "
                 "from observed structure rather than a published schema. It is cross-checked "
                 "against the same row's SQL columns: 2 > 1 matches sender_id, 3 > 1 > 1 > 1 "
                 "client_conversation_id, 4 > 2 content_type, 6 > 1 and 6 > 2 the timestamps. Only "
                 "content_type 1 carried text (6 of 16 rows); other values carried media metadata "
                 "and encryption keys but no plaintext body. Media is not decrypted, and "
                 "content_type is reported as stored because no source for the enum was verified.\n"
                 "Message Direction compares sender_id against the local account id, from "
                 "key_user_id in user_session_shared_pref.xml, else LAST_LOGGED_IN_USERNAME "
                 "in identity_persistent_store.xml resolved through Friend.userId, else the "
                 "single distinct sender of rows where created_on_device is set. The "
                 "sources agreed on the tested images. Blank when none resolves.\n"
                 "Older Snapchat builds carry a strict subset of the current columns (the "
                 "tested vc 147872 build lacks created_on_device and replies_count); absent "
                 "columns are substituted with NULL under the same name so the remaining "
                 "columns still report, and the affected fields are blank on those rows. On "
                 "such builds the direction fallback uses local_message_content_id, which "
                 "that generation's schema comments describe as nullable if the message was "
                 "not created on this device.\n"
                 "Media. When a message references cached media, the Media column renders it. "
                 "The link is by the media key the message_content protobuf carries, matched "
                 "to the trailing token of an EXTERNAL_KEY in "
                 "native_content_manager/cache_controller.db (chat_snap, snap or "
                 "chat_media_thumbnail claims), whose CACHE_KEY is the file name under "
                 "files/native_content_manager/com.snap.file_manager_*_SCContent_*/. A message "
                 "may render both a full snap and its thumbnail. The bytes are read from disk "
                 "as stored: on the tested image they were unencrypted MP4 and JPEG. A media "
                 "message whose local copy is absent (evicted or never downloaded) reports a "
                 "blank Media cell rather than being dropped. See the Snapchat - Chat Media "
                 "artifact for the file-centric view including orphans.\n"
                 "Limits. WAL frames are not parsed, so a message absent here is not evidence it "
                 "did not exist: a development-only frame parser read a further 29 rows across 10 "
                 "conversations on this image, 9 of them absent from the conversation table. This "
                 "is not carving, and a row whose key survived while its content changed is not "
                 "detected. Reactions, message_state history and Kraken epoch content are not "
                 "parsed. The run log reports the image's WAL frame count.\n"
                 "Verify a Recovered row independently: sqlite3 \"file:arroyo.db?immutable=1\" "
                 "\"SELECT * FROM conversation_message WHERE client_message_id = 962\", then "
                 "confirm it is absent from a normal read.",
        "paths": ('*/com.snapchat.android/databases/arroyo.db*',
                  '*/com.snapchat.android/databases/main.db*',
                  '*/com.snapchat.android/shared_prefs/identity_persistent_store.xml',
                  '*/com.snapchat.android/shared_prefs/user_session_shared_pref.xml',
                  '*/com.snapchat.android/databases/native_content_manager/cache_controller.db*',
                  '*/com.snapchat.android/files/native_content_manager/*SCContent*/*'),
        "output_types": "standard", "artifact_icon": "message",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.snapchat.android vc 302522 | 16 rows "
                                "(8 Live, 8 Recovered)",
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 27 rows "
                                "(9 Live, 18 Recovered)",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 21 rows (all Live)",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 31 rows (all Live)",
            "russell_a14": "Android 14 | 7 rows (all Live)",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android vc 101539 | 41 rows "
                                   "(28 Live, 13 Recovered)",
            "pixel3_a12": "Android 12 | 13 rows (all Live)",
            "pixel3_a11": "Android 11 | 0 rows (conversation_message table empty)",
            "kevin_pocox7_a15": "Android 15 | no Snapchat arroyo.db found",
            "samsungs20_a13": "Android 13 | no Snapchat arroyo.db found",
            "sharon_a13": "Android 13 | no Snapchat arroyo.db found",
            "cookbook_a11": "Android 11 | no Snapchat arroyo.db found",
            "galaxys10_a10": "Android 10 | no Snapchat data found",
            "anne_a15": "Android 15 | no Snapchat data found",
            "samsunga53_a14": "Android 14 | no Snapchat data found",
            "s20fe_a13": "Android 13 | no Snapchat data found",
            "userb2_a13": "Android 13 | no Snapchat data found",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation ID",
                "textColumn": "Message Text",
                "directionColumn": "Message Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Creation Timestamp",
                "senderColumn": "Sender Username",
                "mediaColumn": "Media",
                # Shows Live or Recovered under every bubble, so a recovered row cannot be
                # read as a live message. Record Origin is populated on every row, unlike
                # Recovery Method and Recovery Location, which stay available in the picker.
                "extraColumns": ["Record Origin"],
            }
        },
    },
    "get_snapchat_arroyo_conversations": {
        "name": "Snapchat - Conversations (arroyo.db)",
        "description": "Conversation records from the conversation and feed_entry tables in "
                       "arroyo.db, both the rows a normal read returns and rows that are present "
                       "only before the write-ahead log is applied, distinguished by the Record "
                       "Origin column. Participant UUIDs are decoded from the conversation_metadata "
                       "protobuf and resolved against the Friend table in main.db. WAL frames are "
                       "not parsed, so absence of a conversation here is not evidence it did not "
                       "exist.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07", "last_update_date": "2026-08-10",
        "requirements": "blackboxprotobuf", "category": "Snapchat",
        "notes": "Record Origin. Live rows come back from a normal read. Recovered rows are "
                 "conversations whose client_conversation_id is present in conversation or "
                 "feed_entry as of the last checkpoint and in neither once the write-ahead log is "
                 "applied. Method and limits match Snapchat - Messages (arroyo.db); see its notes, "
                 "including that why a Recovered row is absent is not established. Row counts "
                 "would miss these: all three tables held 4 rows in both reads here, and only the "
                 "keys showed one identifier had been replaced.\n"
                 "Rows are the union of client_conversation_id across conversation and feed_entry, "
                 "so a conversation in only one of them is still reported. For Recovered rows the "
                 "participants, message count and title come from the pre-checkpoint view and "
                 "describe the conversation as it stood then. A participant missing from Friend in "
                 "main.db shows as a bare UUID, an unresolved identifier rather than a finding.\n"
                 "Participant IDs come from the conversation_metadata protobuf at repeated field "
                 "3, sub-path 1 > 1, as 16 raw bytes formatted as a UUID. This agreed with "
                 "feed_entry.participants, which stores the same UUIDs as plain concatenated "
                 "16-byte values, for all 4 conversations on the tested image.\n"
                 "Conversation Type is reported as stored, since no source for the enum was "
                 "verified. Tombstoned At Timestamp is conversation.tombstoned_at_timestamp, which "
                 "the arroyo.db schema comments describe as when the conversation was locally left "
                 "by the user. Message Count counts conversation_message rows in the matching "
                 "view, not messages exchanged.\n"
                 "Limits. WAL frames are not parsed, so a conversation absent here is not evidence "
                 "it did not exist. A development-only frame parser found message rows for 9 "
                 "conversations appearing in neither view.",
        "paths": ('*/com.snapchat.android/databases/arroyo.db*',
                  '*/com.snapchat.android/databases/main.db*'),
        "output_types": "standard", "artifact_icon": "messages",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.snapchat.android vc 302522 | 5 rows "
                                "(4 Live, 1 Recovered)",
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 4 rows "
                                "(3 Live, 1 Recovered)",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 3 rows (all Live)",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 6 rows (all Live)",
            "russell_a14": "Android 14 | 4 rows (all Live)",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android vc 101539 | 3 rows "
                                   "(all Live)",
            "pixel3_a12": "Android 12 | 3 rows (all Live)",
            "pixel3_a11": "Android 11 | 2 rows (all Live)",
        },
    },
    "get_snapchat_chat_media": {
        "name": "Snapchat - Chat Media",
        "description": "Cached conversation media (snaps, sent media and their thumbnails) "
                       "referenced by cache_controller.db, each rendered from the file on "
                       "disk where present, with the message it belongs to when the media "
                       "key resolves to one.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16", "last_update_date": "2026-08-16",
        "requirements": "blackboxprotobuf", "category": "Snapchat",
        "notes": "Rows come from CACHE_FILE_CLAIM in "
                 "databases/native_content_manager/cache_controller.db, limited to the "
                 "chat_snap, snap and chat_media_thumbnail external-key prefixes; the rest "
                 "of that store is lens, bitmoji and UI assets. Each claim's CACHE_KEY is "
                 "the file name under "
                 "files/native_content_manager/com.snap.file_manager_*_SCContent_*/, and the "
                 "Media column renders that file when it is present. The bytes are read as "
                 "stored: on the tested image the files were unencrypted MP4 and JPEG.\n"
                 "A claim whose file is not on disk is still reported, with an empty Media "
                 "cell and On Disk set to NO, so evicted or server-only media is visible "
                 "rather than dropped. The Conversation ID and Client Message ID columns are "
                 "filled when the media key is found inside a conversation_message protobuf "
                 "in arroyo.db; a claim referenced by no surviving message leaves them "
                 "blank. Media Type, File Size and the timestamps are reported as stored "
                 "from the claim and metadata tables.",
        "paths": ('*/com.snapchat.android/databases/native_content_manager/cache_controller.db*',
                  '*/com.snapchat.android/files/native_content_manager/*SCContent*/*',
                  '*/com.snapchat.android/databases/arroyo.db*'),
        "output_types": "standard", "artifact_icon": "photo",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 6 rows, all on "
                           "disk, all joined to messages",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 4 rows",
            "russell_a14": "Android 14 | 3 rows",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android vc 101539 | 6 rows "
                                   "(4 on disk, 2 referenced but absent)",
            "hc_pixel8pro_a17": "Android 17 | com.snapchat.android vc 302522 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 0 rows "
                                "(no chat media claims in cache_controller.db)",
            "pixel3_a12": "Android 12 | 0 rows (no chat media claims in cache_controller.db)",
        },
    },
    "get_snapchat_memories": {
        "name": "Snapchat - Memories",
        "description": "Snapchat memories entries",
        "author": "@A-725-K", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat", "notes": "",
        "paths": ('*/com.snapchat.android/databases/memories.db*',),
        "output_types": "standard", "artifact_icon": "photo",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 4 rows",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 1 row",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 3 rows",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android vc 101539 | 0 rows",
        },
    },
    "get_snapchat_meo": {
        "name": "Snapchat - MEO My Eyes Only",
        "description": "Snapchat My Eyes Only confidential data; recovers the 4-digit passcode via bcrypt",
        "author": "@A-725-K", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat",
        "notes": "Passcode recovery brute-forces the 4-digit MEO code (bcrypt); can be slow.",
        "paths": ('*/com.snapchat.android/databases/memories.db*',),
        "output_types": "standard", "artifact_icon": "eye-off",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 1 row",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 1 row",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android vc 101539 | 0 rows",
        },
    },
    "get_snapchat_snap_media": {
        "name": "Snapchat - Snap Media",
        "description": "Snapchat memories snap media (incl. geolocation)",
        "author": "@A-725-K", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat", "notes": "",
        "paths": ('*/com.snapchat.android/databases/memories.db*',),
        "output_types": "all", "artifact_icon": "photo",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 5 rows",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 1 row",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 3 rows",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android vc 101539 | 0 rows",
        },
    },
    "get_snapchat_identity": {
        "name": "Snapchat - Identity Persistent Store",
        "description": "Snapchat identity_persistent_store.xml",
        "author": "@A-725-K", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat", "notes": "",
        "paths": ('*/com.snapchat.android/shared_prefs/identity_persistent_store.xml',),
        "output_types": "standard", "artifact_icon": "user",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 12 rows",
            "kevin_pocox7_a15": "Android 15 | com.snapchat.android vc 238022 | 10 rows",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 12 rows",
            "samsungs20_a13": "Android 13 | com.snapchat.android vc 260222 | 13 rows",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 12 rows",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android vc 101539 | 12 rows",
        },
    },
    "get_snapchat_login_signup": {
        "name": "Snapchat - Login Signup Store",
        "description": "Snapchat LoginSignupStore.xml",
        "author": "@A-725-K", "creation_date": "2021-11-10", "last_update_date": "2021-11-10",
        "requirements": "none", "category": "Snapchat", "notes": "",
        "paths": ('*/com.snapchat.android/shared_prefs/LoginSignupStore.xml',),
        "output_types": "standard", "artifact_icon": "login-2",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 2 rows",
            "kevin_pocox7_a15": "Android 15 | com.snapchat.android vc 238022 | 2 rows",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 3 rows",
            "samsungs20_a13": "Android 13 | com.snapchat.android vc 260222 | 2 rows",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 1 row",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android vc 101539 | 3 rows",
        },
    },
    "get_snapchat_user_session": {
        "name": "Snapchat - User Session Store",
        "description": "Values from user_session_shared_pref.xml, reported as stored under "
                       "the app's own key names.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16", "last_update_date": "2026-08-16",
        "requirements": "none", "category": "Snapchat",
        "notes": "On the tested image the file carried key_user_id (the signed-in "
                 "account's user id, matching the sender of outgoing arroyo.db messages "
                 "and the LAST_LOGGED_IN_USERNAME account in identity_persistent_store), "
                 "a session refresh token, and the advertising id with its timestamp. "
                 "Keys ending _TIMESTAMP_SEC are converted from Unix seconds; other "
                 "values are reported as stored.",
        "paths": ('*/com.snapchat.android/shared_prefs/user_session_shared_pref.xml',),
        "output_types": "standard", "artifact_icon": "user-check",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.snapchat.android vc 302522 | 8 rows",
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 8 rows",
            "kevin_pocox7_a15": "Android 15 | com.snapchat.android vc 238022 | 1 row",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 8 rows",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 8 rows",
            "russell_a14": "Android 14 | 8 rows",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android vc 101539 | 7 rows",
            "samsungs20_a13": "Android 13 | com.snapchat.android vc 260222 | 2 rows",
            "sharon_a13": "Android 13 | 0 rows (file holds an empty map)",
            "pixel3_a12": "Android 12 | 5 rows",
            "pixel3_a11": "Android 11 | 13 rows",
            "cookbook_a11": "Android 11 | 8 rows",
        },
    },
    "get_snapchat_core_preferences": {
        "name": "Snapchat - Core Preferences",
        "description": "Rows from the Preferences table in core.db: key and stored value.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16", "last_update_date": "2026-08-16",
        "requirements": "none", "category": "Snapchat",
        "notes": "Each row reports the key and whichever typed value column is populated, "
                 "with the column's name. Keys are the app's own; what a setting means is "
                 "not established here.",
        "paths": ('*/com.snapchat.android/databases/core.db*',),
        "output_types": "standard", "artifact_icon": "settings",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.snapchat.android vc 302522 | 255 rows",
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 247 rows",
            "kevin_pocox7_a15": "Android 15 | com.snapchat.android vc 238022 | 7 rows",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 235 rows",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 229 rows",
            "russell_a14": "Android 14 | 235 rows",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android vc 101539 | 301 rows",
            "samsungs20_a13": "Android 13 | com.snapchat.android vc 260222 | 6 rows",
            "pixel3_a12": "Android 12 | 590 rows",
            "pixel3_a11": "Android 11 | 1112 rows",
            "cookbook_a11": "Android 11 | no core.db found",
        },
    },
    "get_snapchat_core_user_store": {
        "name": "Snapchat - Core User Store",
        "description": "Rows from the SnapUserStore table in core.db: per-user stored "
                       "values with the store group and user id decoded from each row's "
                       "key, values reported as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16", "last_update_date": "2026-08-16",
        "requirements": "blackboxprotobuf", "category": "Snapchat",
        "notes": "Each row's itemKey protobuf names the store group (CoreData, UserScore) "
                 "and the user id it belongs to, and those are decoded and reported. The "
                 "property NAME of each value is not stored in the database (the itemKey "
                 "blobs are identical within a group), so values are reported in row "
                 "order without labels: on the tested image the CoreData group's text "
                 "values included the account's username, display name, a date, a phone "
                 "number and a country code, in that row order. Do not read a meaning "
                 "into a value's position across app versions.\n"
                 "The SnapchatUserProperties table is not parsed: its rows are keyed by "
                 "bare numeric property ids with no name source in the file.",
        "paths": ('*/com.snapchat.android/databases/core.db*',),
        "output_types": "standard", "artifact_icon": "database",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.snapchat.android vc 302522 | 32 rows",
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android vc 295722 | 32 rows",
            "kevin_pocox7_a15": "Android 15 | com.snapchat.android vc 238022 | 0 rows "
                                "(SnapUserStore table empty)",
            "pixel7a_a14": "Android 14 | com.snapchat.android vc 147872 | 31 rows",
            "sharon_a14": "Android 14 | com.snapchat.android vc 151972 | 31 rows",
            "russell_a14": "Android 14 | 31 rows",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android vc 101539 | 27 rows",
            "samsungs20_a13": "Android 13 | com.snapchat.android vc 260222 | 0 rows "
                              "(SnapUserStore table empty)",
            "pixel3_a12": "Android 12 | 22 rows",
            "pixel3_a11": "Android 11 | 18 rows",
        },
    }
}

import datetime
import os
import sqlite3
import struct
import xml.etree.ElementTree as ET

import bcrypt

from scripts.ilapfuncs import artifact_processor, check_in_media, decode_protobuf, \
    get_sqlite_db_path, logfunc, open_sqlite_db_readonly

_MEO_CODES = {}
_XML_UNIX_KEYS = {'INSTALL_ON_DEVICE_TIMESTAMP', 'LONG_CLIENT_ID_DEVICE_TIMESTAMP',
                  'FIRST_LOGGED_IN_ON_DEVICE_TIMESTAMP'}
# blackboxprotobuf raises these when a blob does not decode as protobuf.
_PB_ERRORS = (ValueError, TypeError, IndexError, KeyError, AttributeError)


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _find(files_found, *suffixes):
    for f in files_found:
        f = str(f)
        if f.endswith(suffixes):
            return f
    return ''


def _rows(source_path, sql):
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


def _text_from_blob(blob, start_byte, len_byte, type_=None):
    if type_ is not None and type_ != 'text':
        return ''
    try:
        length = blob[len_byte]
        return blob[start_byte:start_byte + length].decode('utf-8', 'replace')
    except (TypeError, IndexError, AttributeError):
        return ''


def _decrypt_meo_code(hashed):
    if hashed in _MEO_CODES:
        return _MEO_CODES[hashed]
    try:
        hash_bytes = hashed.encode()
    except (AttributeError, UnicodeEncodeError):
        return ''
    for code in range(10000):  # 4-digit numeric passcode, O(10^4)
        psw = f'{code:04d}'
        try:
            if bcrypt.checkpw(psw.encode(), hash_bytes):
                _MEO_CODES[hashed] = psw
                return psw
        except (ValueError, TypeError):
            return ''
    return 'Could not find any passcode'


@artifact_processor
def get_snapchat_feeds(context):
    files_found = context.get_files_found()
    source_path = _find(files_found, 'main.db', 'tcspahn.db')
    rows = _rows(source_path, '''
        SELECT lastInteractionTimestamp, key, displayInteractionType, lastReadTimestamp, lastReader,
               lastWriteTimestamp, lastWriter, lastWriteType FROM Feed
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], _ms_to_utc(r[3]), r[4], _ms_to_utc(r[5]), r[6], r[7])
                 for r in rows]
    data_headers = (('Last Interaction Timestamp', 'datetime'), 'Key', 'Display Interaction Type',
                    ('Last Read Timestamp', 'datetime'), 'Last Reader',
                    ('Last Write Timestamp', 'datetime'), 'Last Writer', 'Last Write Type')
    return data_headers, data_list, source_path


@artifact_processor
def get_snapchat_friends(context):
    files_found = context.get_files_found()
    source_path = _find(files_found, 'main.db', 'tcspahn.db')
    rows = _rows(source_path, '''
        SELECT addedTimestamp, username, userId, displayName, phone, birthday
        FROM Friend WHERE addedTimestamp IS NOT NULL
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5]) for r in rows]
    data_headers = (('Added Timestamp', 'datetime'), 'Username', 'User ID', 'Display Name',
                    'Phone Nr', 'Birthday')
    return data_headers, data_list, source_path


@artifact_processor
def get_snapchat_messages(context):
    files_found = context.get_files_found()
    source_path = _find(files_found, 'main.db', 'tcspahn.db')
    rows = _rows(source_path, '''
        SELECT timestamp, seenTimestamp, senderId, username, displayName, type, content
        FROM Message JOIN Friend on senderId = Friend._id
    ''')
    data_list = [(_ms_to_utc(r[0]), _ms_to_utc(r[1]), r[2], r[3], r[4], r[5],
                  _text_from_blob(r[6], 0x2c, 0x28, r[5])) for r in rows]
    data_headers = (('Creation Timestamp', 'datetime'), ('Seen Timestamp', 'datetime'), 'Sender ID',
                    'Sender Username', 'Sender Display Name', 'Message Type', 'Text')
    return data_headers, data_list, source_path


def _pb_get(node, key):
    '''Read one field out of a blackboxprotobuf dict.

    blackboxprotobuf splits a field whose repeats decode to different typedefs into
    'N-1', 'N-2' keys, so fall back to the first such variant when the plain key is absent.
    '''
    if not isinstance(node, dict):
        return None
    if key in node:
        return node[key]
    for name in sorted(node):
        if name.startswith(f'{key}-'):
            return node[name]
    return None


def _pb_walk(node, *path):
    '''Walk a blackboxprotobuf dict, taking the first element of any repeated field.'''
    current = node
    for key in path:
        if isinstance(current, list):
            current = current[0] if current else None
        current = _pb_get(current, key)
    if isinstance(current, list):
        current = current[0] if current else None
    return current


def _pb_text(node, *path):
    value = _pb_walk(node, *path)
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).decode('utf-8', 'replace')
    if isinstance(value, str):
        return value
    return ''


def _uuid_from_bytes(value):
    '''Format a 16-byte protobuf value as a canonical UUID string.'''
    if not isinstance(value, (bytes, bytearray)) or len(value) != 16:
        return ''
    digits = bytes(value).hex()
    return (f'{digits[0:8]}-{digits[8:12]}-{digits[12:16]}-'
            f'{digits[16:20]}-{digits[20:32]}')


def _decode(blob):
    if not blob:
        return None
    try:
        values, _typedef = decode_protobuf(bytes(blob))
    except _PB_ERRORS:
        return None
    return values if isinstance(values, dict) else None


def _friends(main_db_path):
    '''Map Friend.userId to (username, displayName) from main.db.'''
    friends = {}
    for user_id, username, display_name in _rows(
            main_db_path, 'SELECT userId, username, displayName FROM Friend'):
        if user_id:
            friends[user_id] = (username or '', display_name or '')
    return friends


def _friend_name(friends, user_id, index=0):
    return friends.get(user_id, ('', ''))[index]


def _table_columns(source_path, table):
    return {row[1] for row in _rows(source_path, f'PRAGMA table_info({table})')}


def _tolerant_select(source_path, table, columns, tail=''):
    '''A SELECT that names every requested column, substituting NULL AS <name> for columns
    the file's schema generation does not have, so one absent column does not silently drop
    every row. Older Snapchat builds carry strict subsets of the current columns; on the
    tested images nothing was renamed, only absent.
    '''
    present = _table_columns(source_path, table)
    select_list = ', '.join(
        column if column in present else f'NULL AS {column}' for column in columns)
    return f'SELECT {select_list} FROM {table} {tail}'


def _rows_pre_wal(source_path, sql):
    '''Run sql against the database file as of its last checkpoint, ignoring the WAL.

    immutable=1 is strictly read-only. Unlike mode=ro it does not even create a -shm
    sidecar, so no evidence file is altered. Path handling goes through the same
    get_sqlite_db_path() that open_sqlite_db_readonly() uses, so Windows long paths and
    URI-special characters behave identically.
    '''
    if not source_path:
        return []
    try:
        db = sqlite3.connect(f'file:{get_sqlite_db_path(source_path)}?immutable=1', uri=True)
    except sqlite3.Error:
        return []
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


def _superseded(source_path, sql, key_indexes):
    '''Rows present at the last checkpoint and absent once the write-ahead log is applied.

    Both sides are consistent SQLite views of the same file, one ignoring the WAL and one
    applying it, compared on the columns at key_indexes. Comparing row counts is not enough:
    on the tested image counting flagged 2 of 30 tables in arroyo.db while comparing primary
    keys flagged 6, because four tables held the same number of rows with different keys.

    Empty when the file has no WAL alongside it. Why a row did not survive into the
    committed state is not established here.
    '''
    def key(row):
        return tuple(row[index] for index in key_indexes)

    committed = {key(row) for row in _rows(source_path, sql)}
    return [row for row in _rows_pre_wal(source_path, sql) if key(row) not in committed]


def _participants(arroyo_path, friends, reader=_rows):
    '''Map client_conversation_id to (participant ids, participant usernames).'''
    participants = {}
    for conversation_id, blob in reader(
            arroyo_path, 'SELECT client_conversation_id, conversation_metadata FROM conversation'):
        entries = _pb_get(_decode(blob), '3')
        if isinstance(entries, dict):
            entries = [entries]
        ids = []
        for entry in entries if isinstance(entries, list) else []:
            user_id = _uuid_from_bytes(_pb_walk(entry, '1', '1'))
            if user_id and user_id not in ids:
                ids.append(user_id)
        names = [_friend_name(friends, user_id) or user_id for user_id in ids]
        participants[conversation_id] = (', '.join(ids), ', '.join(names))
    return participants


def _local_user_id(files_found, arroyo_path, friends):
    '''The signed-in account's user id, or '' when it cannot be established.

    Preferred source is key_user_id in user_session_shared_pref.xml, which carries the id
    directly. Next is LAST_LOGGED_IN_USERNAME in identity_persistent_store.xml resolved
    through Friend.userId. Failing that, the single distinct sender of the messages the
    arroyo.db schema comments describe as created on this device.
    '''
    for key, value in _parse_xml_rows(_find(files_found, 'user_session_shared_pref.xml')):
        if key == 'key_user_id' and value:
            return value
    username = ''
    for key, value in _parse_xml_rows(_find(files_found, 'identity_persistent_store.xml')):
        if key == 'LAST_LOGGED_IN_USERNAME' and value:
            username = value
    if username:
        for user_id, (friend_username, _display) in friends.items():
            if friend_username == username:
                return user_id
    message_columns = _table_columns(arroyo_path, 'conversation_message')
    if 'created_on_device' in message_columns:
        origin_filter = 'created_on_device = 1'
    elif 'local_message_content_id' in message_columns:
        # Older builds lack created_on_device; their schema comments describe
        # local_message_content_id as nullable if the message wasn't created on this device.
        origin_filter = 'local_message_content_id IS NOT NULL'
    else:
        return ''
    senders = {row[0] for row in _rows(
        arroyo_path,
        f'SELECT DISTINCT sender_id FROM conversation_message WHERE {origin_filter}') if row[0]}
    return senders.pop() if len(senders) == 1 else ''


def _yes_no(value):
    return 'YES' if value else 'NO'


# Conversation media external keys in cache_controller.db carry one of these prefixes; the
# rest of the store is lens, bitmoji and UI assets. Each external key is
# '<prefix>.<prefix>-<media key>', and the trailing media key is what the conversation_message
# protobuf carries, so a message can be joined to its cached file without a message id in the
# cache tables.
_CHAT_MEDIA_PREFIXES = ('chat_snap', 'snap.', 'chat_media_thumbnail')


def _blob_string_leaves(node):
    '''Every string and utf-8-decodable bytes leaf in a decoded protobuf, flattened.'''
    leaves = []
    if isinstance(node, dict):
        for value in node.values():
            leaves.extend(_blob_string_leaves(value))
    elif isinstance(node, list):
        for value in node:
            leaves.extend(_blob_string_leaves(value))
    elif isinstance(node, (bytes, bytearray)):
        try:
            leaves.append(bytes(node).decode('utf-8'))
        except UnicodeDecodeError:
            pass
    elif isinstance(node, str):
        leaves.append(node)
    return leaves


def _chat_media_index(files_found):
    '''Index the cached conversation media referenced by cache_controller.db.

    Returns (claims, ondisk):
      claims: media key -> dict(cache_key, media_type, external_key, created, deleted, size)
              for chat_snap / snap / chat_media_thumbnail claims only.
      ondisk: cache_key -> the extracted file path whose name is that cache_key.

    The media key is the trailing token of the claim's external key, which is also what the
    message protobuf carries, so the two join on that token. The on-disk file is named after
    the cache_key under files/native_content_manager/com.snap.file_manager_*_SCContent_*/.
    '''
    claims = {}
    cache_db = _find(files_found, 'cache_controller.db')
    sizes = {row[0]: row[1] for row in _rows(
        cache_db, 'SELECT CACHE_KEY, FILE_SIZE_BYTES FROM CACHE_FILE_METADATA')}
    for cache_key, external_key, created, deleted in _rows(cache_db, '''
            SELECT CACHE_KEY, EXTERNAL_KEY, CREATION_TIMESTAMP_MILLIS, DELETED_TIMESTAMP_MILLIS
            FROM CACHE_FILE_CLAIM WHERE EXTERNAL_KEY IS NOT NULL'''):
        if not external_key.startswith(_CHAT_MEDIA_PREFIXES):
            continue
        media_key = external_key.rsplit('-', 1)[-1]
        claims[media_key] = {
            'cache_key': cache_key,
            'media_type': external_key.split('.', 1)[0],
            'external_key': external_key,
            'created': created,
            'deleted': deleted,
            'size': sizes.get(cache_key),
        }
    ondisk = {}
    for file_found in files_found:
        file_found = str(file_found)
        if 'native_content_manager' in file_found and os.path.isfile(file_found):
            ondisk.setdefault(os.path.basename(file_found), file_found)
    return claims, ondisk


def _message_media_keys(decoded, claims):
    '''The claim media keys referenced by a decoded message, de-duplicated in order.'''
    if not decoded:
        return []
    seen, keys = set(), []
    for leaf in _blob_string_leaves(decoded):
        if leaf in claims and leaf not in seen:
            seen.add(leaf)
            keys.append(leaf)
    return keys


def _message_media_cell(media_keys, claims, ondisk):
    '''check_in_media each on-disk file for the message's media keys; return the LAVA cell.'''
    refs = []
    for media_key in media_keys:
        cache_key = claims[media_key]['cache_key']
        path = ondisk.get(cache_key)
        if not path:
            continue
        ref = check_in_media(path, cache_key)
        if ref:
            refs.append(ref)
    if len(refs) == 1:
        return refs[0]
    return refs if refs else ''


_MESSAGE_COLUMNS = ('creation_timestamp', 'read_timestamp', 'sender_id', 'content_type',
                    'message_content', 'message_state_type', 'is_saved', 'is_viewed_by_user',
                    'created_on_device', 'remote_media_count', 'replies_count',
                    'quoted_server_message_id', 'client_conversation_id',
                    'client_message_id', 'server_message_id')


def _message_sql(source_path):
    return _tolerant_select(source_path, 'conversation_message', _MESSAGE_COLUMNS,
                            'ORDER BY creation_timestamp')


# conversation_message primary key (client_conversation_id, client_message_id), as offsets
# into _MESSAGE_COLUMNS.
_MESSAGE_KEY = (12, 13)

_MESSAGE_HEADERS = (('Creation Timestamp', 'datetime'), ('Read Timestamp', 'datetime'),
                    'Record Origin',
                    'Sender Username', 'Sender Display Name', 'Sender ID', 'Message Direction',
                    'Conversation Participants', 'Message Text', ('Media', 'media'),
                    'Content Type (as stored)',
                    'Message State Type', 'Is Saved', 'Is Viewed By User', 'Created On Device',
                    'Remote Media Count', 'Replies Count', 'Quoted Server Message ID',
                    'Conversation ID', 'Client Message ID', 'Server Message ID',
                    'Recovery Method', 'Recovery Location')

_CONVERSATION_HEADERS = (('Creation Timestamp', 'datetime'), ('Last Updated Timestamp', 'datetime'),
                         ('Display Timestamp', 'datetime'), ('Tombstoned At Timestamp', 'datetime'),
                         ('Streak Expiration Timestamp', 'datetime'),
                         'Record Origin',
                         'Conversation Title',
                         'Participants', 'Participant IDs', 'Message Count', 'Streak Count',
                         'Conversation Type (as stored)', 'Send State Type', 'Feed Item Creator',
                         'Feed Item Creator ID', 'Last Chat Sender', 'Last Chat Sender ID',
                         'Tombstoned', 'Conversation ID',
                         'Recovery Method', 'Recovery Location')

# Provenance vocabulary. Record Origin is a closed two-value set so a viewer can branch on it;
# Recovery Method names the technique and is empty on live rows; Recovery Location says where in
# the evidence the row came from. Keep these strings stable, they are read by people and may be
# read by LAVA.
_ORIGIN_LIVE = 'Live'
_ORIGIN_RECOVERED = 'Recovered'
_METHOD_WAL_DIFF = 'WAL diff'


def _provenance(source_path, origin):
    '''The three provenance values for a row, as (origin, method, location).'''
    if origin == _ORIGIN_LIVE:
        return (_ORIGIN_LIVE, '', '')
    name = os.path.basename(source_path) if source_path else 'database'
    return (_ORIGIN_RECOVERED, _METHOD_WAL_DIFF, f'{name} (pre-checkpoint)')


def _log_wal_extent(files_found):
    '''Log how much write-ahead log this artifact leaves unparsed, per image.

    Reads the WAL header and the 24-byte frame headers only; no page images are loaded.
    A frame whose salt pair does not match the WAL header belongs to a previous log
    generation that the current one has cycled past, so it holds older content still on
    disk. Reporting both counts gives the examiner the size of what is not covered here.
    '''
    wal_path = _find(files_found, 'arroyo.db-wal')
    if not wal_path:
        return
    try:
        with open(wal_path, 'rb') as handle:
            header = handle.read(32)
            if len(header) < 32:
                return
            magic, page_size = struct.unpack('>I', header[:4])[0], struct.unpack('>I', header[8:12])[0]
            if magic not in (0x377F0682, 0x377F0683) or page_size < 512:
                return
            salts = struct.unpack('>2I', header[16:24])
            frame_size = 24 + page_size
            total = max(0, (os.path.getsize(wal_path) - 32) // frame_size)
            current = 0
            for index in range(total):
                handle.seek(32 + index * frame_size)
                frame_header = handle.read(24)
                if len(frame_header) < 24:
                    total = index
                    break
                if struct.unpack('>2I', frame_header[8:16]) == salts:
                    current += 1
    except (OSError, struct.error, ValueError):
        return
    logfunc(f'Snapchat arroyo.db-wal holds {total} frames of {page_size} bytes '
            f'({current} in the current log generation, {total - current} from previous '
            f'generations). This artifact does not parse WAL frames, so records held only in '
            f'them are not reported and absence of a message from the Snapchat arroyo.db '
            f'artifacts is not evidence that it did not exist.')


def _by_creation(row):
    '''Sort key on the first column, tolerating rows whose timestamp is blank.

    The blank flag comes first so a datetime is never compared against a string.
    '''
    return (row[0] == '', row[0])


def _message_rows(rows, friends, participants, local_user_id, provenance, media_index):
    origin, method, location = provenance
    claims, ondisk = media_index
    data_list = []
    for row in rows:
        (created, read, sender_id, content_type, blob, state, saved, viewed, on_device,
         media_count, replies, quoted_id, conversation_id, client_message_id, server_message_id) = row
        decoded = _decode(blob)
        text = _pb_text(decoded, '4', '4', '2', '1') if content_type == 1 else ''
        media_cell = _message_media_cell(_message_media_keys(decoded, claims), claims, ondisk)
        if not local_user_id or not sender_id:
            direction = ''
        else:
            direction = 'Outgoing' if sender_id == local_user_id else 'Incoming'
        data_list.append((
            _ms_to_utc(created), _ms_to_utc(read), origin,
            _friend_name(friends, sender_id), _friend_name(friends, sender_id, 1), sender_id,
            direction, participants.get(conversation_id, ('', ''))[1], text, media_cell,
            content_type, state,
            _yes_no(saved), _yes_no(viewed), _yes_no(on_device), media_count, replies, quoted_id,
            conversation_id, client_message_id, server_message_id, method, location))
    return data_list


def _conversation_rows(source_path, friends, reader, provenance, only_ids=None):
    participants = _participants(source_path, friends, reader)
    conversations = {row[0]: row[1:] for row in reader(source_path, '''
        SELECT client_conversation_id, creation_timestamp, tombstoned_at_timestamp, send_state_type
        FROM conversation
    ''')}
    feeds = {row[0]: row[1:] for row in reader(source_path, '''
        SELECT client_conversation_id, last_updated_timestamp, display_timestamp,
               streak_expiration_timestamp_ms, conversation_title, conversation_type, streak_count,
               feedItemCreator, last_chat_sender, tombstoned
        FROM feed_entry
    ''')}
    counts = dict(reader(source_path, '''
        SELECT client_conversation_id, COUNT(*) FROM conversation_message
        GROUP BY client_conversation_id
    '''))

    origin, method, location = provenance
    wanted = set(conversations) | set(feeds)
    if only_ids is not None:
        wanted &= set(only_ids)

    data_list = []
    for conversation_id in sorted(wanted):
        created, tombstoned_at, send_state = conversations.get(conversation_id, (None, None, ''))
        (updated, displayed, streak_expiry, title, conversation_type, streak, creator,
         last_sender, tombstoned) = feeds.get(conversation_id, (None,) * 9)
        data_list.append((
            _ms_to_utc(created), _ms_to_utc(updated), _ms_to_utc(displayed),
            _ms_to_utc(tombstoned_at), _ms_to_utc(streak_expiry), origin, title,
            participants.get(conversation_id, ('', ''))[1],
            participants.get(conversation_id, ('', ''))[0],
            counts.get(conversation_id, 0), streak, conversation_type, send_state,
            _friend_name(friends, creator), creator, _friend_name(friends, last_sender), last_sender,
            _yes_no(tombstoned), conversation_id, method, location))
    return data_list


def _superseded_conversation_ids(source_path):
    '''client_conversation_id values that the WAL removes from conversation or feed_entry.'''
    pre, committed = set(), set()
    for sql in ('SELECT client_conversation_id FROM conversation',
                'SELECT client_conversation_id FROM feed_entry'):
        pre |= {row[0] for row in _rows_pre_wal(source_path, sql)}
        committed |= {row[0] for row in _rows(source_path, sql)}
    return pre - committed


@artifact_processor
def get_snapchat_arroyo_messages(context):
    '''Live conversation_message rows, plus rows the write-ahead log removes.

    Both sets are in one table so the recovered rows sit in chronological context. They are
    disjoint by construction: _superseded only returns primary keys absent from the live read.
    '''
    files_found = context.get_files_found()
    source_path = _find(files_found, 'arroyo.db')
    friends = _friends(_find(files_found, 'main.db'))
    local_user_id = _local_user_id(files_found, source_path, friends)
    media_index = _chat_media_index(files_found)
    _log_wal_extent(files_found)

    data_list = _message_rows(
        _rows(source_path, _message_sql(source_path)), friends,
        _participants(source_path, friends),
        local_user_id, _provenance(source_path, _ORIGIN_LIVE), media_index)
    data_list += _message_rows(
        _superseded(source_path, _message_sql(source_path), _MESSAGE_KEY), friends,
        _participants(source_path, friends, _rows_pre_wal), local_user_id,
        _provenance(source_path, _ORIGIN_RECOVERED), media_index)
    data_list.sort(key=_by_creation)
    return _MESSAGE_HEADERS, data_list, source_path


@artifact_processor
def get_snapchat_arroyo_conversations(context):
    '''Live conversation and feed_entry rows, plus rows the write-ahead log removes.'''
    files_found = context.get_files_found()
    source_path = _find(files_found, 'arroyo.db')
    friends = _friends(_find(files_found, 'main.db'))

    data_list = _conversation_rows(source_path, friends, _rows,
                                   _provenance(source_path, _ORIGIN_LIVE))
    data_list += _conversation_rows(source_path, friends, _rows_pre_wal,
                                    _provenance(source_path, _ORIGIN_RECOVERED),
                                    _superseded_conversation_ids(source_path))
    data_list.sort(key=_by_creation)
    return _CONVERSATION_HEADERS, data_list, source_path


def _media_key_to_message(arroyo_path, claims):
    '''Map each claim media key to the (conversation_id, message_id) that references it.'''
    mapping = {}
    for blob, conversation_id, message_id in _rows(arroyo_path, '''
            SELECT message_content, client_conversation_id, client_message_id
            FROM conversation_message'''):
        for media_key in _message_media_keys(_decode(blob), claims):
            mapping.setdefault(media_key, (conversation_id, message_id))
    return mapping


@artifact_processor
def get_snapchat_chat_media(context):
    '''Cached conversation media from cache_controller.db, rendered and joined to messages.'''
    files_found = context.get_files_found()
    claims, ondisk = _chat_media_index(files_found)
    cache_db = _find(files_found, 'cache_controller.db')
    key_to_message = _media_key_to_message(_find(files_found, 'arroyo.db'), claims)

    data_list = []
    for media_key, info in claims.items():
        cache_key = info['cache_key']
        path = ondisk.get(cache_key)
        media_cell = check_in_media(path, cache_key) if path else ''
        conversation_id, message_id = key_to_message.get(media_key, ('', ''))
        data_list.append((
            _ms_to_utc(info['created']), media_cell, info['media_type'],
            conversation_id, message_id, info['size'], _yes_no(path),
            _ms_to_utc(info['deleted']) if info['deleted'] else '',
            cache_key, info['external_key']))
    data_headers = (('Creation Timestamp', 'datetime'), ('Media', 'media'), 'Media Type',
                    'Conversation ID', 'Client Message ID', 'File Size (bytes)', 'On Disk',
                    ('Deleted Timestamp', 'datetime'), 'Cache Key', 'External Key')
    return data_headers, data_list, cache_db


@artifact_processor
def get_snapchat_memories(context):
    files_found = context.get_files_found()
    source_path = _find(files_found, 'memories.db')
    rows = _rows(source_path, '''
        SELECT create_time, _id, snap_ids, CASE is_private WHEN 1 THEN 'YES' ELSE 'NO' END,
               cached_servlet_media_formats FROM memories_entry
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], _text_from_blob(r[2], 0x20, 0x1c), r[3],
                  _text_from_blob(r[4], 0x20, 0x1c)) for r in rows]
    data_headers = (('Timestamp', 'datetime'), 'Memory ID', 'Snap ID', 'Is Private', 'Media Format')
    return data_headers, data_list, source_path


@artifact_processor
def get_snapchat_meo(context):
    files_found = context.get_files_found()
    source_path = _find(files_found, 'memories.db')
    rows = _rows(source_path,
                 'SELECT user_id, hashed_passcode, master_key, master_key_iv FROM memories_meo_confidential')
    data_list = [(r[0], r[1], _decrypt_meo_code(r[1]), r[2], r[3]) for r in rows]
    data_headers = ('User ID', 'Hashed Passcode', 'Passcode', 'Master Key', 'Master Key IV')
    return data_headers, data_list, source_path


@artifact_processor
def get_snapchat_snap_media(context):
    files_found = context.get_files_found()
    source_path = _find(files_found, 'memories.db')
    rows = _rows(source_path, '''
        SELECT create_time, memories_snap._id, media_id, memories_entry_id, time_zone_id, format,
               width, height, duration,
               CASE has_overlay_image WHEN 1 THEN 'YES' ELSE 'NO' END,
               overlay_size, overlay_redirect_info,
               CASE front_facing WHEN 1 THEN 'YES' ELSE 'NO' END, size,
               CASE has_location WHEN 1 THEN 'YES' ELSE 'NO' END, latitude, longitude,
               snap_create_user_agent, thumbnail_size, thumbnail_redirect_info
        FROM memories_snap JOIN memories_media ON memories_media._id = media_id
    ''')
    data_list = [(_ms_to_utc(r[0]),) + tuple(r[1:]) for r in rows]
    data_headers = (('Create Time', 'datetime'), 'ID', 'Media ID', 'Memories Entry ID', 'Time Zone ID',
                    'Format', 'Width', 'Height', 'Duration', 'Has Overlay', 'Overlay Size',
                    'Overlay Info', 'Front Facing', 'Size', 'Has Location Info', 'Latitude',
                    'Longitude', 'Snap User Agent', 'Thumbnail Size', 'Thumbnail Info')
    return data_headers, data_list, source_path


def _parse_xml_rows(xml_file):
    data_list = []
    if not xml_file:
        return data_list
    try:
        root = ET.parse(xml_file).getroot()
    except (ET.ParseError, OSError, ValueError):
        return data_list
    for node in root:
        name = node.attrib.get('name', '')
        value = node.attrib.get('value', node.text)
        if name in _XML_UNIX_KEYS and value:
            try:
                value = datetime.datetime.fromtimestamp(
                    int(value) / 1000, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            except (ValueError, TypeError, OverflowError, OSError):
                pass
        data_list.append((name, value))
    return data_list


@artifact_processor
def get_snapchat_identity(context):
    files_found = context.get_files_found()
    source_path = _find(files_found, 'identity_persistent_store.xml')
    return ('Key', 'Value'), _parse_xml_rows(source_path), source_path


@artifact_processor
def get_snapchat_login_signup(context):
    files_found = context.get_files_found()
    source_path = _find(files_found, 'LoginSignupStore.xml')
    return ('Key', 'Value'), _parse_xml_rows(source_path), source_path


_SESSION_SECONDS_SUFFIX = '_TIMESTAMP_SEC'


@artifact_processor
def get_snapchat_user_session(context):
    files_found = context.get_files_found()
    source_path = _find(files_found, 'user_session_shared_pref.xml')
    data_list = []
    for key, value in _parse_xml_rows(source_path):
        if key.endswith(_SESSION_SECONDS_SUFFIX) and value:
            try:
                value = datetime.datetime.fromtimestamp(
                    int(value), datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            except (ValueError, TypeError, OverflowError, OSError):
                pass
        data_list.append((key, value))
    return ('Key', 'Value'), data_list, source_path


@artifact_processor
def get_snapchat_core_preferences(context):
    files_found = context.get_files_found()
    source_path = _find(files_found, 'core.db')
    data_list = []
    value_columns = ('booleanValue', 'intValue', 'longValue', 'floatValue',
                     'doubleValue', 'stringValue')
    for row in _rows(source_path, f'''
            SELECT key, {', '.join(value_columns)} FROM Preferences ORDER BY key'''):
        key = row[0]
        value = value_type = ''
        for name, column_value in zip(value_columns, row[1:]):
            if column_value is not None:
                value, value_type = column_value, name
                break
        data_list.append((key, value, value_type))
    data_headers = ('Key', 'Value', 'Value Column')
    return data_headers, data_list, source_path


@artifact_processor
def get_snapchat_core_user_store(context):
    files_found = context.get_files_found()
    source_path = _find(files_found, 'core.db')
    data_list = []
    for rowid, item_key, int_value, real_value, boolean_value, text_value, blob_value in _rows(
            source_path, '''
            SELECT _id, itemKey, intVal, realVal, booleanVal, textVal, blobVal
            FROM SnapUserStore ORDER BY _id'''):
        decoded_key = _decode(item_key)
        group = _pb_text(decoded_key, '1', '1')
        user_id = _pb_text(decoded_key, '1', '2')
        store = _pb_text(decoded_key, '3', '2')
        value = value_type = ''
        for name, column_value in (('intVal', int_value), ('realVal', real_value),
                                   ('booleanVal', boolean_value), ('textVal', text_value)):
            if column_value is not None:
                value, value_type = column_value, name
                break
        if not value_type and blob_value is not None:
            value, value_type = f'{len(blob_value)} byte blob', 'blobVal'
        data_list.append((group, user_id, store, value, value_type, rowid))
    data_headers = ('Group', 'User ID', 'Store', 'Value (as stored)', 'Value Column',
                    'Row ID')
    return data_headers, data_list, source_path

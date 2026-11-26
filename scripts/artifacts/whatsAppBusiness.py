__artifacts_v2__ = {
    "get_whatsapp_business_contacts": {
        "name": "WhatsApp Business - Contacts",
        "description": "WhatsApp Business wa.db wa_contacts rows, excluding channel (@newsletter) and "
                       "status@broadcast jids, read the same way as WhatsApp - Contacts",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-25",
        "requirements": "none",
        "category": "Messaging",
        "notes": "Runs the same reader as WhatsApp - Contacts on com.whatsapp.w4b files only, so "
                 "WhatsApp and WhatsApp Business are never read together. The columns are those of "
                 "WhatsApp - Contacts. Its notes describe the columns it documents. Those notes were "
                 "measured on WhatsApp images, not on WhatsApp Business. Tested on the WhatsApp "
                 "Business 2.26.45.80 known-data keys in sample_data (emu_a16_w4b_kd). No logged "
                 "action was compared for this table. Each key gave 7 rows: 4 @s.whatsapp.net jids, 1 "
                 "@g.us, 1 @bot and 1 ending in @broadcast. On each key 15 rows were left out (14 "
                 "@newsletter, 1 status@broadcast). Status Timestamp was blank on every row. Only the "
                 "first wa.db matched is read, as in the WhatsApp module. Which copy is first follows "
                 "the order of the input's file listing. On a constructed tree with Android users 0 "
                 "and 10, the user 0 databases were read and the user 10 databases gave no rows. "
                 "Running the WhatsApp readers for WhatsApp Business through a wrapper was proposed in "
                 "PR #1499 by @prcharan592 and again in PR #1785 by @danjethh. Credit to both. Both "
                 "PRs were closed without merging.",
        "paths": ('*/com.whatsapp.w4b/databases/wa.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "emu_a16_w4b_kd_w1_channel_followed": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 7 rows",
            "emu_a16_w4b_kd_w2_channel_deleted": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 7 rows",
            "emu_a16_w4b_kd_w3_status_viewed": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 7 rows",
            "emu_a16_w4b_kd_w4_custom_away": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 7 rows",
        },
    },
    "get_whatsapp_business_call_logs": {
        "name": "WhatsApp Business - Call Logs",
        "description": "WhatsApp Business call logs from msgstore.db, read the same way as WhatsApp - Call "
                       "Logs",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-25",
        "requirements": "none",
        "category": "Messaging",
        "notes": "Runs the same reader as WhatsApp - Call Logs on com.whatsapp.w4b files only, so "
                 "WhatsApp and WhatsApp Business are never read together. The columns are those of "
                 "WhatsApp - Call Logs. Its notes describe the columns it documents. Those notes were "
                 "measured on WhatsApp images, not on WhatsApp Business. Tested on the WhatsApp "
                 "Business 2.26.45.80 known-data keys in sample_data (emu_a16_w4b_kd), against actions "
                 "logged while the data was made. The action log records a voice call to a test phone "
                 "placed as a retry and answered. Each key gave 2 rows, both Outgoing and Audio. The "
                 "earlier has a Call Duration of zero and the later a nonzero one. Incoming and video "
                 "calls were not exercised. Group Name and Caller JID were blank on every tested row: "
                 "no call was a group call, and Caller JID is blank on an outgoing call. Only the "
                 "first msgstore.db and wa.db matched is read, as in the WhatsApp module. Which copy "
                 "is first follows the order of the input's file listing. On a constructed tree with "
                 "Android users 0 and 10, the user 0 databases were read and the user 10 databases "
                 "gave no rows. Running the WhatsApp readers for WhatsApp Business through a wrapper "
                 "was proposed in PR #1499 by @prcharan592 and again in PR #1785 by @danjethh. Credit "
                 "to both. Both PRs were closed without merging.",
        "paths": ('*/com.whatsapp.w4b/databases/msgstore.db*', '*/com.whatsapp.w4b/databases/wa.db*'),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "emu_a16_w4b_kd_w1_channel_followed": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 2 rows",
            "emu_a16_w4b_kd_w2_channel_deleted": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 2 rows",
            "emu_a16_w4b_kd_w3_status_viewed": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 2 rows",
            "emu_a16_w4b_kd_w4_custom_away": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 2 rows",
        },
    },
    "get_whatsapp_business_one_to_one_messages": {
        "name": "WhatsApp Business - One To One Messages",
        "description": "WhatsApp Business messages in chats that are not groups or channels, read the same "
                       "way as WhatsApp - One To One Messages",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-25",
        "requirements": "none",
        "category": "Messaging",
        "notes": "Runs the same reader as WhatsApp - One To One Messages on com.whatsapp.w4b files "
                 "only, so WhatsApp and WhatsApp Business are never read together. The columns are "
                 "those of WhatsApp - One To One Messages. Its notes describe the columns it "
                 "documents. Those notes were measured on WhatsApp images, not on WhatsApp Business. "
                 "Tested on the WhatsApp Business 2.26.45.80 known-data keys in sample_data "
                 "(emu_a16_w4b_kd), against actions logged while the data was made. The keys gave 12, "
                 "12, 12 and 13 rows. All but one are in the test chat. The other is one Outgoing "
                 "system message in a chat keyed by an @lid jid that matched no contact. The logged "
                 "messages of the test chat came through: 3 incoming texts, one incoming photo whose "
                 "file shows in Media, 2 outgoing replies, and on the last key one more outgoing text "
                 "sent as a quick reply. Each key also gave 1 Incoming text that is not in the action "
                 "log and 2 Outgoing system messages. 3 Outgoing rows stored message_type 90 (2) or "
                 "124 (1), which are shown as stored because their meaning was not established. "
                 "Location messages, static or live, were not exercised. Final Location Timestamp, "
                 "Shared Latitude/Starting Latitude (Live Location), Shared Longitude/Starting "
                 "Longitude (Live Location), Duration Live Location Shared (Seconds), Final Live "
                 "Latitude and Final Live Longitude were blank on every tested row. Only the first "
                 "msgstore.db and wa.db matched is read, as in the WhatsApp module. Which copy is "
                 "first follows the order of the input's file listing. On a constructed tree with "
                 "Android users 0 and 10, the user 0 databases were read and the user 10 databases "
                 "gave no rows. Running the WhatsApp readers for WhatsApp Business through a wrapper "
                 "was proposed in PR #1499 by @prcharan592 and again in PR #1785 by @danjethh. Credit "
                 "to both. Both PRs were closed without merging.",
        "paths": ('*/com.whatsapp.w4b/databases/msgstore.db*', '*/com.whatsapp.w4b/databases/wa.db*',
                  '*/com.whatsapp.w4b/WhatsApp Business/Media/*', '*/com.whatsapp.w4b/files/Media/*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "emu_a16_w4b_kd_w1_channel_followed": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 12 rows",
            "emu_a16_w4b_kd_w2_channel_deleted": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 12 rows",
            "emu_a16_w4b_kd_w3_status_viewed": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 12 rows",
            "emu_a16_w4b_kd_w4_custom_away": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 13 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Other Participant JID",
                "conversationLabelColumn": "Other Participant WA User Name",
                "textColumn": "Message",
                "directionColumn": "Message Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Message Timestamp",
                "senderColumn": "Other Participant WA User Name",
                "sentMessageStaticLabel": "Local User",
                "mediaColumn": "Media"
            }
        },
    },
    "get_whatsapp_business_group_messages": {
        "name": "WhatsApp Business - Group Messages",
        "description": "WhatsApp Business messages in group chats, read the same way as WhatsApp - Group "
                       "Messages",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-25",
        "requirements": "none",
        "category": "Messaging",
        "notes": "Runs the same reader as WhatsApp - Group Messages on com.whatsapp.w4b files only, so "
                 "WhatsApp and WhatsApp Business are never read together. The columns are those of "
                 "WhatsApp - Group Messages. Its notes describe the columns it documents. Those notes "
                 "were measured on WhatsApp images, not on WhatsApp Business. Tested on the WhatsApp "
                 "Business 2.26.45.80 known-data keys in sample_data (emu_a16_w4b_kd), against actions "
                 "logged while the data was made. The test account made one group and each side sent "
                 "one text in it. Each key gave 5 rows: 1 Incoming text, 1 Outgoing text and 3 "
                 "Outgoing system messages. Group media was not exercised. Conversation Name and Group "
                 "JID held one value on every tested row, because each key holds one group. Media, "
                 "Local Path To Media, Media File Size, Final Location Timestamp, Shared "
                 "Latitude/Starting Latitude (Live Location), Shared Longitude/Starting Longitude "
                 "(Live Location), Duration Live Location Shared (Seconds), Final Live Latitude and "
                 "Final Live Longitude were blank on every tested row. Only the first msgstore.db and "
                 "wa.db matched is read, as in the WhatsApp module. Which copy is first follows the "
                 "order of the input's file listing. On a constructed tree with Android users 0 and "
                 "10, the user 0 databases were read and the user 10 databases gave no rows. Running "
                 "the WhatsApp readers for WhatsApp Business through a wrapper was proposed in PR "
                 "#1499 by @prcharan592 and again in PR #1785 by @danjethh. Credit to both. Both PRs "
                 "were closed without merging.",
        "paths": ('*/com.whatsapp.w4b/databases/msgstore.db*', '*/com.whatsapp.w4b/databases/wa.db*',
                  '*/com.whatsapp.w4b/WhatsApp Business/Media/*', '*/com.whatsapp.w4b/files/Media/*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "emu_a16_w4b_kd_w1_channel_followed": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 5 rows",
            "emu_a16_w4b_kd_w2_channel_deleted": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 5 rows",
            "emu_a16_w4b_kd_w3_status_viewed": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 5 rows",
            "emu_a16_w4b_kd_w4_custom_away": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 5 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Group JID",
                "conversationLabelColumn": "Conversation Name",
                "textColumn": "Message",
                "directionColumn": "Message Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Message Timestamp",
                "senderColumn": "Sending Party",
                "mediaColumn": "Media"
            }
        },
    },
    "get_whatsapp_business_group_details": {
        "name": "WhatsApp Business - Group Details",
        "description": "WhatsApp Business group chats with their creator and picture where stored, read the "
                       "same way as WhatsApp - Group Details",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-25",
        "requirements": "none",
        "category": "Messaging",
        "notes": "Runs the same reader as WhatsApp - Group Details on com.whatsapp.w4b files only, so "
                 "WhatsApp and WhatsApp Business are never read together. The columns are those of "
                 "WhatsApp - Group Details. Its notes describe the columns it documents. Those notes "
                 "were measured on WhatsApp images, not on WhatsApp Business. Tested on the WhatsApp "
                 "Business 2.26.45.80 known-data keys in sample_data (emu_a16_w4b_kd), against actions "
                 "logged while the data was made. Each key gave 1 row, the known group, with a Creator "
                 "JID. Group Picture was blank. files/Avatars held no file named for the group's jid, "
                 "and no group picture was set in the logged actions. Creator JID (via jid_map), "
                 "Creator WA User Name, Creator WA Number and Creator WA Profile Picture were blank on "
                 "every tested row. Only the first msgstore.db and wa.db matched is read, as in the "
                 "WhatsApp module. Which copy is first follows the order of the input's file listing. "
                 "On a constructed tree with Android users 0 and 10, the user 0 databases were read "
                 "and the user 10 databases gave no rows. Running the WhatsApp readers for WhatsApp "
                 "Business through a wrapper was proposed in PR #1499 by @prcharan592 and again in PR "
                 "#1785 by @danjethh. Credit to both. Both PRs were closed without merging.",
        "paths": ('*/com.whatsapp.w4b/databases/msgstore.db*', '*/com.whatsapp.w4b/databases/wa.db*',
                  '*/com.whatsapp.w4b/files/Avatars/*'),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "emu_a16_w4b_kd_w1_channel_followed": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 1 row",
            "emu_a16_w4b_kd_w2_channel_deleted": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 1 row",
            "emu_a16_w4b_kd_w3_status_viewed": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 1 row",
            "emu_a16_w4b_kd_w4_custom_away": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 1 row",
        },
    },
    "get_whatsapp_business_channels": {
        "name": "WhatsApp Business - Channels",
        "description": "WhatsApp Business channels with a row in msgstore.db's newsletter table, read the "
                       "same way as WhatsApp - Channels",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-25",
        "requirements": "none",
        "category": "Messaging",
        "notes": "Runs the same reader as WhatsApp - Channels on com.whatsapp.w4b files only, so "
                 "WhatsApp and WhatsApp Business are never read together. The columns are those of "
                 "WhatsApp - Channels. Its notes describe the columns it documents. Those notes were "
                 "measured on WhatsApp images, not on WhatsApp Business. Tested on the WhatsApp "
                 "Business 2.26.45.80 known-data keys in sample_data (emu_a16_w4b_kd), against actions "
                 "logged while the data was made. The test account created one channel and followed "
                 "one verified channel. emu_a16_w4b_kd_w1_channel_followed gave 2 rows: the created "
                 "channel with Verified (as stored) 0 and 5 Messages Stored, and the followed one with "
                 "1 and 14. On the followed channel, Chat Created Timestamp was years earlier than the "
                 "logged follow, so it does not mark when the channel was followed. The created "
                 "channel was then deleted in the app. emu_a16_w4b_kd_w2_channel_deleted and the later "
                 "keys still gave 2 rows: the deleted channel's newsletter row remained, with Messages "
                 "Stored 1. A row here does not establish that the channel still exists in the "
                 "account. Verified (as stored), Membership (as stored) and Muted (as stored) were 1, "
                 "1 and 1 on the followed channel. On the created channel they were 0, 3 and 0 before "
                 "it was deleted and 0, 0 and 0 after. What a Membership (as stored) of 3 records was "
                 "not established. Only the first msgstore.db matched is read, as in the WhatsApp "
                 "module. Which copy is first follows the order of the input's file listing. On a "
                 "constructed tree with Android users 0 and 10, the user 0 databases were read and the "
                 "user 10 databases gave no rows. Running the WhatsApp readers for WhatsApp Business "
                 "through a wrapper was proposed in PR #1499 by @prcharan592 and again in PR #1785 by "
                 "@danjethh. Credit to both. Both PRs were closed without merging.",
        "paths": ('*/com.whatsapp.w4b/databases/msgstore.db*',),
        "output_types": "standard",
        "artifact_icon": "broadcast",
        "sample_data": {
            "emu_a16_w4b_kd_w1_channel_followed": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 2 rows",
            "emu_a16_w4b_kd_w2_channel_deleted": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 2 rows",
            "emu_a16_w4b_kd_w3_status_viewed": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 2 rows",
            "emu_a16_w4b_kd_w4_custom_away": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 2 rows",
        },
    },
    "get_whatsapp_business_channel_messages": {
        "name": "WhatsApp Business - Channel Messages",
        "description": "Messages stored in WhatsApp Business channel chats, read the same way as WhatsApp - "
                       "Channel Messages",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-25",
        "requirements": "none",
        "category": "Messaging",
        "notes": "Runs the same reader as WhatsApp - Channel Messages on com.whatsapp.w4b files only, "
                 "so WhatsApp and WhatsApp Business are never read together. The columns are those of "
                 "WhatsApp - Channel Messages. Its notes describe the columns it documents. Those "
                 "notes were measured on WhatsApp images, not on WhatsApp Business. Tested on the "
                 "WhatsApp Business 2.26.45.80 known-data keys in sample_data (emu_a16_w4b_kd), "
                 "against actions logged while the data was made. emu_a16_w4b_kd_w1_channel_followed "
                 "gave 19 rows, among them 2 Outgoing texts that match the two known posts to the "
                 "created channel and 5 Outgoing system messages. After that channel was deleted, "
                 "emu_a16_w4b_kd_w2_channel_deleted and the later keys gave 15 rows: the two posts "
                 "were gone and 3 Outgoing system messages remained. Incoming rows on the followed "
                 "channel include message_type 13, 15, 20 and 81, shown as stored because their "
                 "meaning was not established. Media and Local Path To Media were blank on every row, "
                 "including 2 Picture rows. Received Timestamp and Reaction From Me were blank on "
                 "every tested row. Only the first msgstore.db matched is read, as in the WhatsApp "
                 "module. Which copy is first follows the order of the input's file listing. On a "
                 "constructed tree with Android users 0 and 10, the user 0 databases were read and the "
                 "user 10 databases gave no rows. Running the WhatsApp readers for WhatsApp Business "
                 "through a wrapper was proposed in PR #1499 by @prcharan592 and again in PR #1785 by "
                 "@danjethh. Credit to both. Both PRs were closed without merging.",
        "paths": ('*/com.whatsapp.w4b/databases/msgstore.db*', '*/com.whatsapp.w4b/WhatsApp Business/Media/*',
                  '*/com.whatsapp.w4b/files/Media/*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "emu_a16_w4b_kd_w1_channel_followed": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 19 rows",
            "emu_a16_w4b_kd_w2_channel_deleted": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 15 rows",
            "emu_a16_w4b_kd_w3_status_viewed": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 15 rows",
            "emu_a16_w4b_kd_w4_custom_away": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 15 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Channel JID",
                "conversationLabelColumn": "Channel Name",
                "textColumn": "Message",
                "directionColumn": "Message Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Message Timestamp",
                "senderColumn": "Channel Name",
                "sentMessageStaticLabel": "Local User",
                "mediaColumn": "Media"
            }
        },
    },
    "get_whatsapp_business_user_profile": {
        "name": "WhatsApp Business - User Profile",
        "description": "Values of five keys in WhatsApp Business's shared_prefs XML files, one row per "
                       "shared_prefs folder",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-25",
        "requirements": "none",
        "category": "Messaging",
        "notes": "Runs the same reader as WhatsApp - User Profile on com.whatsapp.w4b files only, so "
                 "WhatsApp and WhatsApp Business are never read together. The columns are those of "
                 "WhatsApp - User Profile. Its notes describe the columns it documents. Those notes "
                 "were measured on WhatsApp images, not on WhatsApp Business. Tested on the WhatsApp "
                 "Business 2.26.45.80 known-data keys in sample_data (emu_a16_w4b_kd), against actions "
                 "logged while the data was made. On the tested version WhatsApp Business names its "
                 "file com.whatsapp.w4b_preferences_light.xml, and the WhatsApp reader now reads that "
                 "name too. Each key gave 1 row. Version and Name came from startup_prefs.xml. Country "
                 "Code and Mobile Number came from com.whatsapp.w4b_preferences_light.xml. User Status "
                 "showed blank. The stored my_current_status value is one whitespace character, which "
                 "the reader does not show. On a constructed tree a second user's shared_prefs folder "
                 "gave its own row. Running the WhatsApp readers for WhatsApp Business through a "
                 "wrapper was proposed in PR #1499 by @prcharan592 and again in PR #1785 by @danjethh. "
                 "Credit to both. Both PRs were closed without merging.",
        "paths": ('*/com.whatsapp.w4b/shared_prefs/com.whatsapp.w4b_preferences_light.xml',
                  '*/com.whatsapp.w4b/shared_prefs/startup_prefs.xml'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "emu_a16_w4b_kd_w1_channel_followed": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 1 row",
            "emu_a16_w4b_kd_w2_channel_deleted": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 1 row",
            "emu_a16_w4b_kd_w3_status_viewed": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 1 row",
            "emu_a16_w4b_kd_w4_custom_away": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 1 row",
        },
    },
    "get_whatsapp_business_disappearing_mode": {
        "name": "WhatsApp Business - Default Disappearing Messages Timer",
        "description": "disappearing_mode_duration_int and disappearing_mode_timestamp from WhatsApp "
                       "Business's disappearing_mode_prefs.xml, one row per shared_prefs folder",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-25",
        "requirements": "none",
        "category": "Messaging",
        "notes": "Runs the same reader as WhatsApp - Default Disappearing Messages Timer on "
                 "com.whatsapp.w4b files only, so WhatsApp and WhatsApp Business are never read "
                 "together. The columns are those of WhatsApp - Default Disappearing Messages Timer. "
                 "Its notes describe the columns it documents. Those notes were measured on WhatsApp "
                 "images, not on WhatsApp Business. Tested on the WhatsApp Business 2.26.45.80 "
                 "known-data keys in sample_data (emu_a16_w4b_kd). The timer was not changed in the "
                 "logged actions. Each key gave 1 row with Duration (seconds) 0, Timer Off and "
                 "Timestamp blank. Other timer values were not exercised. That WhatsApp Business uses "
                 "this file for its default message timer is read from the key names. It was not shown "
                 "on the tested keys. Running the WhatsApp readers for WhatsApp Business through a "
                 "wrapper was proposed in PR #1499 by @prcharan592 and again in PR #1785 by @danjethh. "
                 "Credit to both. Both PRs were closed without merging.",
        "paths": ('*/com.whatsapp.w4b/shared_prefs/disappearing_mode_prefs.xml',),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "emu_a16_w4b_kd_w1_channel_followed": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 1 row",
            "emu_a16_w4b_kd_w2_channel_deleted": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 1 row",
            "emu_a16_w4b_kd_w3_status_viewed": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 1 row",
            "emu_a16_w4b_kd_w4_custom_away": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 1 row",
        },
    },
}

from scripts.artifacts import WhatsApp
from scripts.ilapfuncs import artifact_processor

# Each artifact runs the WhatsApp module's reader for the same table on this artifact's own
# files, which are only com.whatsapp.w4b paths, so the two apps are never read together.


@artifact_processor
def get_whatsapp_business_contacts(context):
    return WhatsApp.get_whatsapp_contacts.__wrapped__(context)


@artifact_processor
def get_whatsapp_business_call_logs(context):
    return WhatsApp.get_whatsapp_call_logs.__wrapped__(context)


@artifact_processor
def get_whatsapp_business_one_to_one_messages(context):
    return WhatsApp.get_whatsapp_one_to_one_messages.__wrapped__(context)


@artifact_processor
def get_whatsapp_business_group_messages(context):
    return WhatsApp.get_whatsapp_group_messages.__wrapped__(context)


@artifact_processor
def get_whatsapp_business_group_details(context):
    return WhatsApp.get_whatsapp_group_details.__wrapped__(context)


@artifact_processor
def get_whatsapp_business_channels(context):
    return WhatsApp.get_whatsapp_channels.__wrapped__(context)


@artifact_processor
def get_whatsapp_business_channel_messages(context):
    return WhatsApp.get_whatsapp_channel_messages.__wrapped__(context)


@artifact_processor
def get_whatsapp_business_user_profile(context):
    return WhatsApp.get_whatsapp_user_profile.__wrapped__(context)


@artifact_processor
def get_whatsapp_business_disappearing_mode(context):
    return WhatsApp.get_whatsapp_disappearing_mode.__wrapped__(context)

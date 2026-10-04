__artifacts_v2__ = {
    "get_whatsapp_contacts": {
        "name": "WhatsApp - Contacts",
        "description": "Rows of WhatsApp's wa.db wa_contacts table (name columns, wa_name, jid, number and status text), excluding channel (@newsletter) and status@broadcast jids",
        "author": "@abrignoni",
        "creation_date": "2021-03-11",
        "last_update_date": "2026-09-27",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "Reads the first wa.db matched and reports its wa_contacts rows, except rows whose jid ends in @newsletter, the jid form of the chats msgstore.db's newsletter table describes, and the row whose jid is status@broadcast. When any rows are left out, their number is written to the run log. On the 12 tested images the rows left out numbered 791 (781 @newsletter, 10 status@broadcast); none held a given name, family name, display name or number, so each would have shown its jid as Name and JID, with no Number. wa.db holds more @newsletter jids than msgstore.db's newsletter table holds channels: 275 against 10 channels on kevin_pocox7_a15, 191 against 5 on russell_a14, and 255 on anne_a15, whose newsletter table is empty. The @newsletter jids with no chat in msgstore.db appeared in no other TEXT column of wa.db or msgstore.db on any tested image (full-text index tables were not searched). What those rows record was not established, and an @newsletter jid in wa.db does not show that a channel was followed. Name is given_name and family_name when either is not null, otherwise display_name, otherwise the jid; 1,722 of the 1,809 reported rows across the tested images showed the jid as Name. WhatsApp Name is the wa_name column as stored, and it is never used to fill Name. It was set on 230 of the 1,809 rows, 210 of them rows whose Name was the jid; on the 20 rows where both it and one of given_name, family_name or display_name were set, it differed from Name on 15. In 20 pairs of tested images, one device's own account appeared in the other device's wa_contacts; wa_name was set in 10 of them, and in all 10 it equalled the push_name value in the first device's own WhatsApp preferences (startup_prefs.xml, or com.whatsapp_preferences_light.xml on pixel3_a11 and pixel3_a12). A published description of wa_name is 'WhatsApp name of the contact (as set in their profile)'. Reference: Igor Mikhailov, 'WhatsApp in Plain Sight: Where and How You Can Collect Forensic Artifacts', https://www.group-ib.com/blog/whatsapp-forensic-artifacts/. When wa_name was written, and whether it follows later changes to the contact's profile name, was not established. Number is the number column as stored, with no fallback to the jid; it was empty on 1,731 of the 1,809 rows. Status Text is the status column as stored, and Status Timestamp is status_timestamp read as milliseconds since 1970-01-01 UTC, shown blank where the stored value is 0. Status Text was set on 730 of the 1,809 rows and Status Timestamp on 531, all of them rows with a Status Text; the other 199 rows with a Status Text stored a timestamp of 0. Of the 20 pairs of tested images above, status was set in 15; in the 11 of those whose first device stores a my_current_status value in its own com.whatsapp_preferences_light.xml, status equalled that value in all 11. Where one contact carried the same Status Text on two different tested phones with a timestamp on both (4 contacts), Status Timestamp was identical on both. What event Status Timestamp marks was not established. A published description of status is 'Text in the status line of the contact'. Reference: Igor Mikhailov, 'WhatsApp in Plain Sight: Where and How You Can Collect Forensic Artifacts', https://www.group-ib.com/blog/whatsapp-forensic-artifacts/. Rows whose jid ends in @g.us, @lid or @bot are reported as stored.",
        "paths": ('*/com.whatsapp/databases/wa.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 12 rows",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 13 rows",
            "hc_pixel8pro_a17": "Android 17 | com.whatsapp vc 262907320 | 13 rows",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 19 rows",
            "pixel3_a11": "Android 11 | com.whatsapp vc 204815003 | 3 rows",
            "pixel3_a12": "Android 12 | com.whatsapp vc 212020004 | 4 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 72 rows",
            "russell_a14": "Android 14 | com.whatsapp vc 241676004 | 714 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 1 row",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 8 rows",
            "sharon_a13": "Android 13 | com.whatsapp vc 231278007 | 333 rows",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 617 rows",
        },
    },
    "get_whatsapp_call_logs": {
        "name": "WhatsApp - Call Logs",
        "description": "WhatsApp call logs (msgstore.db)",
        "author": "@abrignoni",
        "creation_date": "2021-03-11",
        "last_update_date": "2026-09-28",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "A call whose jid is a LID jid (...@lid) is matched to wa.db contacts through msgstore.db jid_map when that table exists. Calls that match no contact are still reported when a wa.db is present. With no wa.db the query cannot run and no calls are reported; the run log says so. Call End Timestamp is not stored: it is the call's timestamp plus its duration read as seconds. On an outgoing call Caller reads Self and Caller JID is blank. For an incoming call that matches no contact, or whose contact has no WhatsApp name, Caller is shown by jid. The LID-keyed case and the no-contact case are exercised by a constructed test (admin/test/scripts/test_whatsapp_lid_contacts.py); whether any image listed in sample_data holds such a call is not stated here.",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*'),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | com.whatsapp vc 262907320 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 0 rows",
            "pixel3_a11": "Android 11 | com.whatsapp vc 204815003 | 4 rows",
            "pixel3_a12": "Android 12 | com.whatsapp vc 212020004 | 4 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 4 rows",
            "russell_a14": "Android 14 | com.whatsapp vc 241676004 | 3 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 0 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 0 rows",
            "sharon_a13": "Android 13 | com.whatsapp vc 231278007 | 1 row",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 3 rows",
        },
    },
    "get_whatsapp_messages": {
        "name": "WhatsApp - Messages",
        "description": "WhatsApp messages (legacy msgstore.db schema with messages.data)",
        "author": "@abrignoni",
        "creation_date": "2021-03-11",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "Legacy schema only (a messages table with a data column); modern databases are "
                 "covered by the One To One / Group Messages artifacts. Key Remote JID is "
                 "messages.key_remote_jid as stored; it is not a message identifier. Only "
                 "messages whose key_remote_jid has a row in wa.db's wa_contacts are reported, and "
                 "none are reported when wa.db is absent. Every image listed in sample_data "
                 "reports 0 rows, so this artifact is not exercised by the listed data.",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 0 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 0 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 0 rows",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 0 rows",
        },
    },
    "get_whatsapp_one_to_one_messages": {
        "name": "WhatsApp - One To One Messages",
        "description": "WhatsApp messages whose recipient_count is 0, outside channel chats (modern msgstore.db schema)",
        "author": "@abrignoni",
        "creation_date": "2021-03-11",
        "last_update_date": "2026-09-28",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "Rows are selected by message.recipient_count = 0, not by the type of the chat's jid. Message Type shows this module's label for message_type 0, 1, 2, 3, 5, 7, 9 and 16; other values are shown as stored and no source for the labels is cited here. A chat keyed by a LID jid (...@lid) is matched to wa.db contacts through msgstore.db jid_map when that table exists. Messages whose chat matches no contact are still reported when a wa.db is present. With no wa.db the query cannot run and no messages are reported; the run log says so. When no contact matches, or the contact has no WhatsApp name, the participant is shown by jid. The conversation view groups rows by Other Participant WA User Name, so a LID-keyed chat and the phone-number chat that jid_map links it to are shown as one conversation. Two different contacts that share a WhatsApp name are grouped the same way; the Sending Party JID column tells them apart on incoming rows. On sharon_a14, 48 LID-keyed chats each had such a phone-number chat. Messages in channel (newsletter) chats are not reported here; WhatsApp - Channel Messages reports them.",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*', '*/WhatsApp/Media/*', '*/com.whatsapp/files/Media/*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 31 rows",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 29 rows",
            "hc_pixel8pro_a17": "Android 17 | com.whatsapp vc 262907320 | 29 rows",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 154 rows",
            "pixel3_a11": "Android 11 | com.whatsapp vc 204815003 | 0 rows",
            "pixel3_a12": "Android 12 | com.whatsapp vc 212020004 | 0 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 73 rows",
            "russell_a14": "Android 14 | com.whatsapp vc 241676004 | 491 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 71 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 14 rows",
            "sharon_a13": "Android 13 | com.whatsapp vc 231278007 | 435 rows",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 788 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Other Participant WA User Name",
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
    "get_whatsapp_group_messages": {
        "name": "WhatsApp - Group Messages",
        "description": "WhatsApp messages whose recipient_count is 1 or more (modern msgstore.db schema)",
        "author": "@abrignoni",
        "creation_date": "2021-03-11",
        "last_update_date": "2026-09-26",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "Rows are selected by message.recipient_count >= 1, not by the type of the chat's jid. Message Type shows this module's label for message_type 0, 1, 2, 3, 5, 7, 9 and 16; other values are shown as stored and no source for the labels is cited here. A sender keyed by a LID jid (...@lid) is matched to wa.db contacts through msgstore.db jid_map when that table exists. A sender that matches no contact, or has no WhatsApp name, is shown by jid. On outgoing rows Sending Party reads Self and Sending Party JID is blank. With no wa.db the query cannot run and no messages are reported; the run log says so.",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*', '*/WhatsApp/Media/*', '*/com.whatsapp/files/Media/*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 7 rows",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 39 rows",
            "hc_pixel8pro_a17": "Android 17 | com.whatsapp vc 262907320 | 39 rows",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 0 rows",
            "pixel3_a11": "Android 11 | com.whatsapp vc 204815003 | 0 rows",
            "pixel3_a12": "Android 12 | com.whatsapp vc 212020004 | 0 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 156 rows",
            "russell_a14": "Android 14 | com.whatsapp vc 241676004 | 76 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 0 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 0 rows",
            "sharon_a13": "Android 13 | com.whatsapp vc 231278007 | 2383 rows",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 4730 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation Name",
                "textColumn": "Message",
                "directionColumn": "Message Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Message Timestamp",
                "senderColumn": "Sending Party",
                "mediaColumn": "Media"
            }
        },
    },
    "get_whatsapp_group_details": {
        "name": "WhatsApp - Group Details",
        "description": "WhatsApp group chats (chats with a subject in msgstore.db other than channels), with the group creator where wa.db records one and the group picture where the app stored one",
        "author": "@abrignoni",
        "creation_date": "2021-03-11",
        "last_update_date": "2026-09-27",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": (
            "Reads msgstore.db's chat table joined to jid, one row per chat that carries a subject "
            "and whose jid_row_id names a jid row; all 27 chats with a subject on the tested "
            "images had one. The chat table is read directly rather than through chat_view, "
            "because chat_view has no jid_row_id column on 7 of the 12 tested images (pixel3_a11, "
            "pixel3_a12, pixel7a_a14, russell_a14, russell_pixel6a_a13, sharon_a13, sharon_a14); "
            "on the other 5, reading chat gives the same rows as reading chat_view. Chats keyed by "
            "a newsletter jid (...@newsletter) also carry a subject and are not reported here; "
            "WhatsApp - Channels reports them. Of the 27 chats with a subject on the tested "
            "images, 18 are newsletter chats (10 on kevin_pocox7_a15, 5 on russell_a14, 3 on "
            "samsungs20_a13) and the 9 reported are groups (...@g.us). Group Creation Timestamp is "
            "chat.created_timestamp as stored. Whether it marks when the group was created or when "
            "the chat was created on this device is not established here. Creator JID is wa.db's "
            "wa_group_admin_settings.creator_jid for the chat's jid. Creator JID held a value on 4 "
            "of the 9 group rows and was blank for all 5 groups on pixel7a_a14, russell_a14 and "
            "sharon_a14. It is also blank when wa.db lacks the creator_jid column, as on "
            "pixel3_a11, or when no wa.db is found (exercised on a constructed database only). "
            "Creator JID (via jid_map) is the jid that msgstore.db's jid_map links to a Creator "
            "JID recorded as a LID jid (...@lid). Creator JID (via jid_map) held a value on the 3 "
            "group rows whose Creator JID is a LID jid (anne_a15, hc_pixel8pro_a16, "
            "hc_pixel8pro_a17), each a ...@s.whatsapp.net jid, and was blank on the other 6. "
            "Creator JID (via jid_map) is also blank when msgstore.db has no jid_map table "
            "(exercised on a constructed database only). Creator WA User Name and Creator WA "
            "Number come from the wa.db wa_contacts row whose jid equals Creator JID (via jid_map) "
            "when that holds a value, and Creator JID otherwise. Creator WA User Name was blank on "
            "8 of the 9 group rows, all but anne_a15, and Creator WA Number was blank on all 9: "
            "the matching wa_contacts row stores a name and no number on anne_a15, and no name or "
            "number on hc_pixel8pro_a16, hc_pixel8pro_a17 and sharon_a13. Group Picture is the "
            "file in com.whatsapp/files/Avatars, in the same app container as the msgstore.db "
            "read, whose name is the group's jid followed by .j. Group Picture was blank on 7 of "
            "the 9 group rows and held a value on 2 (sharon_a13 and sharon_a14), both JPEG images. "
            "The file name is the only link between the file and the group; when the file was "
            "written is not established. Creator WA Profile Picture is the file in the same folder "
            "named after Creator JID or Creator JID (via jid_map), followed by .j. Creator WA "
            "Profile Picture was blank on every tested image, because none of the four images with "
            "a Creator JID holds such a file; the lookup was exercised on constructed files only. "
            "Only the first msgstore.db matched is read, as in the module's other artifacts."
        ),
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*',
                  '*/com.whatsapp/files/Avatars/*'),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 1 row",
            "hc_pixel8pro_a17": "Android 17 | com.whatsapp vc 262907320 | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 0 rows",
            "pixel3_a11": "Android 11 | com.whatsapp vc 204815003 | 0 rows",
            "pixel3_a12": "Android 12 | com.whatsapp vc 212020004 | 0 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 3 rows",
            "russell_a14": "Android 14 | com.whatsapp vc 241676004 | 1 row",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 0 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 0 rows",
            "sharon_a13": "Android 13 | com.whatsapp vc 231278007 | 1 row",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 1 row",
        },
    },
    "get_whatsapp_channels": {
        "name": "WhatsApp - Channels",
        "description": "WhatsApp channels with a row in msgstore.db's newsletter table",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-27",
        "last_update_date": "2026-09-27",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "Reads msgstore.db's newsletter table, one row per channel, joined to the channel's chat. Local Chat Created Timestamp is chat.created_timestamp. On the three tested images holding channels (kevin_pocox7_a15, russell_a14, samsungs20_a13; 18 channels), each channel's earliest stored message was one of two system messages with from_me=1 (message_system action_type 132 and 134) carrying that same millisecond value, and no message in the channel was older. What those two system messages record, and whether the timestamp marks when the channel was followed, was not established. Verified (as stored), Membership (as stored) and Muted (as stored) are the newsletter table's integers, reported without an interpretation. Membership (as stored) and Muted (as stored) each held the same value, 1, on all 18 channels. Verified (as stored) held 1 on 15 channels and 0 on 3, and held the same value, 1, on all 3 channels of samsungs20_a13. Subscriber Count is newsletter.subscribers_count as stored. Messages Stored counts the chat's rows in the message table. Newsletter chats with no newsletter row are not reported: pixel7a_a14 and sharon_a14 each hold 20, with no name, no timestamps and no messages. wa.db lists newsletter jids for channels absent from this table (275 newsletter jids on kevin_pocox7_a15 against its 10 channels), so a newsletter jid in wa.db does not show that the channel was followed. wa.db's wa_newsletter_props, whose property names are keyed by a numeric id or a two-letter code, is not reported. Only the first msgstore.db matched is read, as in the module's other artifacts.",
        "paths": ('*/com.whatsapp/databases/msgstore.db*',),
        "output_types": "standard",
        "artifact_icon": "broadcast",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | com.whatsapp vc 262907320 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 10 rows",
            "pixel3_a11": "Android 11 | com.whatsapp vc 204815003 | 0 rows",
            "pixel3_a12": "Android 12 | com.whatsapp vc 212020004 | 0 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 0 rows",
            "russell_a14": "Android 14 | com.whatsapp vc 241676004 | 5 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 0 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 3 rows",
            "sharon_a13": "Android 13 | com.whatsapp vc 231278007 | 0 rows",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 0 rows",
        },
    },
    "get_whatsapp_channel_messages": {
        "name": "WhatsApp - Channel Messages",
        "description": "Messages stored in WhatsApp channel (newsletter) chats",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-27",
        "last_update_date": "2026-09-27",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "Every message in a channel (newsletter) chat in msgstore.db. Channel Name comes from the newsletter table, falling back to the chat subject and then the jid. On the three tested images holding channel messages (kevin_pocox7_a15, russell_a14, samsungs20_a13; 5,217 rows), sender_jid_row_id was 0 on every message, so msgstore.db records no author and the channel is shown as the sender. Message Direction shows Incoming where from_me is 0 and Outgoing where it is 1; the conversation view shows Outgoing rows under the label Local User, which does not establish that the account posted them. The 36 Outgoing rows on those images were all system messages (message_type 7, message_system action_type 132 or 134), two per channel, carrying the channel chat's created timestamp; what they record was not established. Message Type shows this module's label for message_type 0 (Text), 1 (Picture), 2 (Audio), 3 (Video), 5 (Static Location), 7 (System Message), 9 (Document) and 16 (Live Location); no source for the labels is cited here, and other values are reported as stored. Server Message ID is newsletter_message.server_message_id and is blank on the 106 rows with no newsletter_message row; newsletter_message rows with no message row (one on each of the three images) are not reported. Reaction From Me is newsletter_message.reaction_from_me and held no value on any tested image. Of the 2,276 channel messages with a message_media row, 29 recorded a local file path, all on kevin_pocox7_a15, and all 29 render in Media; the others record no local file. Media and Local Path To Media held no value on any row of russell_a14 or samsungs20_a13. Reaction totals from other followers (newsletter_message_reaction) and the channel message search index (the message_newsletter_fts tables) are not reported. Only the first msgstore.db matched is read, as in the module's other artifacts.",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/WhatsApp/Media/*', '*/com.whatsapp/files/Media/*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | com.whatsapp vc 262907320 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 3731 rows",
            "pixel3_a11": "Android 11 | com.whatsapp vc 204815003 | 0 rows",
            "pixel3_a12": "Android 12 | com.whatsapp vc 212020004 | 0 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 0 rows",
            "russell_a14": "Android 14 | com.whatsapp vc 241676004 | 1291 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 0 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 195 rows",
            "sharon_a13": "Android 13 | com.whatsapp vc 231278007 | 0 rows",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 0 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Channel Name",
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
    "get_whatsapp_user_profile": {
        "name": "WhatsApp - User Profile",
        "description": "Values of five keys in WhatsApp's shared_prefs XML files",
        "author": "@abrignoni",
        "creation_date": "2021-03-11",
        "last_update_date": "2021-03-11",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "One row. Name is the push_name key, User Status my_current_status, Country Code "
                 "cc, Mobile Number ph and Version version, each as stored in "
                 "com.whatsapp_preferences_light.xml or startup_prefs.xml. The first non-empty "
                 "value found for each key across the matched files is used, so where more than "
                 "one copy of the app is present the row can combine values from different copies.",
        "paths": ('*/com.whatsapp/shared_prefs/com.whatsapp_preferences_light.xml',
                  '*/com.whatsapp/shared_prefs/startup_prefs.xml'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 1 row",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 1 row",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 1 row",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 1 row",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 1 row",
        },
    }
}

import datetime
import os
import sqlite3

import xmltodict

from scripts.ilapfuncs import artifact_processor, attach_sqlite_db_readonly, open_sqlite_db_readonly, check_in_media, \
    logfunc

# Re-used location columns shared by the one-to-one and group message queries.
_LOCATION_HEADERS = ('Shared Latitude/Starting Latitude (Live Location)',
                     'Shared Longitude/Starting Longitude (Live Location)',
                     'Duration Live Location Shared (Seconds)', 'Final Live Latitude',
                     'Final Live Longitude')

_MESSAGE_TYPE_CASE = '''CASE
        WHEN message.message_type=0 THEN "Text"
        WHEN message.message_type=1 THEN "Picture"
        WHEN message.message_type=2 THEN "Audio"
        WHEN message.message_type=3 THEN "Video"
        WHEN message.message_type=5 THEN "Static Location"
        WHEN message.message_type=7 THEN "System Message"
        WHEN message.message_type=9 THEN "Document"
        WHEN message.message_type=16 THEN "Live Location"
        ELSE message.message_type
        END'''


def _str_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S').replace(
            tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError):
        return ''


def _find(files_found, suffix):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith(('-wal', '-shm', '-journal')):
            continue
        if file_found.endswith(suffix):
            return file_found
    return ''


def _media(file_path):
    if not file_path:
        return ''
    ref = check_in_media(str(file_path), name=os.path.basename(str(file_path)))
    return ref or ''


def _open_msgstore(files_found):
    """Open msgstore.db with wa.db attached as wadb (when present)."""
    msg = _find(files_found, 'msgstore.db')
    wa = _find(files_found, 'wa.db')
    if not msg:
        return None, None, '', ''
    db = open_sqlite_db_readonly(msg)
    cursor = db.cursor()
    if wa:
        try:
            cursor.execute(attach_sqlite_db_readonly(wa, 'wadb'))
        except sqlite3.Error:
            pass
    return db, cursor, msg, wa


def _run(cursor, sql):
    try:
        cursor.execute(sql)
        return cursor.fetchall()
    except sqlite3.Error as exc:
        logfunc(f'WhatsApp: query not run against this database schema, no rows read: {exc}')
        return []


def _has_table(cursor, name):
    try:
        cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,))
        return cursor.fetchone() is not None
    except sqlite3.Error:
        return False


def _avatars(files_found, msgstore):
    """Map file name to path for files/Avatars in the same app container as msgstore."""
    marker = '/databases/msgstore.db'
    msgstore = str(msgstore).replace('\\', '/')
    if not msgstore.endswith(marker):
        return {}
    folder = msgstore[:-len(marker)] + '/files/Avatars/'
    avatars = {}
    for file_found in files_found:
        path = str(file_found)
        rest = path.replace('\\', '/')
        if rest.startswith(folder) and '/' not in rest[len(folder):] and not os.path.isdir(path):
            avatars[rest[len(folder):]] = path
    return avatars


def _has_column(cursor, schema, table, column):
    try:
        return column in [row[1] for row in cursor.execute(f'PRAGMA {schema}.table_info({table})')]
    except sqlite3.Error:
        return False


def _contact_jid(cursor, jid_alias):
    """Return (joins, expression) giving the jid to match wa_contacts.jid against.

    Newer msgstore.db files can key a 1:1 chat or a group sender by a LID jid
    (``...@lid``), while wa_contacts.jid holds the ``...@s.whatsapp.net`` form.
    msgstore.db's jid_map table links the two jid rows (lid_row_id -> jid_row_id).
    When jid_map is absent (older databases) the jid's own raw_string is used.
    """
    if not _has_table(cursor, 'jid_map'):
        return '', f'{jid_alias}.raw_string'
    joins = f'''LEFT JOIN jid_map ON jid_map.lid_row_id={jid_alias}._id
        LEFT JOIN jid AS mapped_jid ON mapped_jid._id=jid_map.jid_row_id'''
    return joins, f'COALESCE(mapped_jid.raw_string, {jid_alias}.raw_string)'


def _ms_to_utc(value):
    """A millisecond Unix time as a UTC datetime; 0, empty or non-integer values give None."""
    if not isinstance(value, int) or value <= 0:
        return None
    return datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(milliseconds=value)


@artifact_processor
def get_whatsapp_contacts(context):
    files_found = context.get_files_found()
    source = _find(files_found, 'wa.db')
    data_list = []
    if source:
        db = open_sqlite_db_readonly(source)
        cursor = db.cursor()
        # wa_name is present on every tested wa.db; an older one without it still reports its rows.
        wa_name = 'WC.wa_name' if _has_column(cursor, 'main', 'wa_contacts', 'wa_name') else 'NULL'
        status = 'WC.status' if _has_column(cursor, 'main', 'wa_contacts', 'status') else 'NULL'
        status_ts = ('WC.status_timestamp' if _has_column(cursor, 'main', 'wa_contacts', 'status_timestamp')
                     else 'NULL')
        rows = _run(cursor, f'''
        SELECT
            CASE
                WHEN WC.given_name IS NULL AND WC.family_name IS NULL AND WC.display_name IS NULL THEN WC.jid
                WHEN WC.given_name IS NULL AND WC.family_name IS NULL THEN WC.display_name
                WHEN WC.given_name IS NULL THEN WC.family_name
                WHEN WC.family_name IS NULL THEN WC.given_name
                ELSE WC.given_name || " " || WC.family_name
            END,
            {wa_name},
            jid,
            WC.number,
            {status},
            {status_ts}
        FROM wa_contacts AS WC
        WHERE WC.jid NOT LIKE '%@newsletter' AND WC.jid <> 'status@broadcast'
        ''')
        for row in rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], _ms_to_utc(row[5])))
        skipped = _run(cursor, '''
        SELECT SUM(jid LIKE '%@newsletter'), SUM(jid = 'status@broadcast') FROM wa_contacts
        ''')
        if skipped and any(skipped[0]):
            logfunc(f'WhatsApp - Contacts: not reported {skipped[0][0] or 0} channel (@newsletter) '
                    f'and {skipped[0][1] or 0} status@broadcast wa_contacts rows')
        db.close()

    data_headers = ('Name', 'WhatsApp Name', 'JID', 'Number', 'Status Text', ('Status Timestamp', 'datetime'))
    return data_headers, data_list, source


@artifact_processor
def get_whatsapp_call_logs(context):
    files_found = context.get_files_found()
    db, cursor, source, _wa = _open_msgstore(files_found)
    data_list = []
    if db:
        lid_joins, contact_jid = _contact_jid(cursor, 'jid')
        rows = _run(cursor, f'''
        SELECT
            datetime(call_log.timestamp/1000,'unixepoch'),
            datetime((call_log.timestamp/1000 + call_log.duration),'unixepoch'),
            strftime('%H:%M:%S', call_log.duration ,'unixepoch'),
            chat.subject,
            CASE WHEN call_log.from_me=0 THEN "Incoming" WHEN call_log.from_me=1 THEN "Outgoing" END,
            CASE WHEN call_log.from_me=1 THEN "Self" ELSE COALESCE(NULLIF(wa_contacts.wa_name, ''), {contact_jid}) END,
            CASE WHEN call_log.from_me=1 THEN "" ELSE COALESCE(wa_contacts.jid, {contact_jid}) END,
            CASE WHEN call_log.video_call=0 THEN "Audio" WHEN call_log.video_call=1 THEN "Video" END
        FROM call_log
        LEFT JOIN jid ON jid._id=call_log.jid_row_id
        {lid_joins}
        LEFT JOIN wa_contacts ON wa_contacts.jid={contact_jid}
        LEFT JOIN chat ON chat.jid_row_id=call_log.group_jid_row_id
        ORDER BY call_log.timestamp ASC
        ''')
        for row in rows:
            data_list.append((_str_to_utc(row[0]), _str_to_utc(row[1]), row[2], row[3], row[4],
                              row[5], row[6], row[7]))
        db.close()

    data_headers = (('Call Start Timestamp', 'datetime'), ('Call End Timestamp', 'datetime'),
                    'Call Duration', 'Group Name', 'Call Direction', 'Caller', 'Caller JID',
                    'Call Type')
    return data_headers, data_list, source


@artifact_processor
def get_whatsapp_messages(context):
    files_found = context.get_files_found()
    db, cursor, source, _wa = _open_msgstore(files_found)
    data_list = []
    if db:
        rows = _run(cursor, '''
        SELECT
            datetime(messages.timestamp/1000,'unixepoch'),
            CASE messages.received_timestamp WHEN 0 THEN ''
                ELSE datetime(messages.received_timestamp/1000,'unixepoch') END,
            messages.key_remote_jid,
            CASE WHEN contact_book_w_groups.recipients IS NULL THEN messages.key_remote_jid
                ELSE contact_book_w_groups.recipients END,
            CASE key_from_me WHEN 0 THEN "Incoming" WHEN 1 THEN "Outgoing" END,
            messages.data,
            CASE WHEN messages.remote_resource IS NULL THEN messages.key_remote_jid
                ELSE messages.remote_resource END,
            messages.media_url
        FROM (SELECT jid, recipients FROM wadb.wa_contacts AS contacts
            LEFT JOIN (SELECT gjid, group_concat(CASE WHEN jid == "" THEN NULL ELSE jid END) AS recipients
                FROM group_participants GROUP BY gjid) AS groups ON contacts.jid = groups.gjid
            GROUP BY jid) AS contact_book_w_groups
        JOIN messages ON messages.key_remote_jid = contact_book_w_groups.jid
        ''')
        for row in rows:
            data_list.append((_str_to_utc(row[0]), _str_to_utc(row[1]), row[2], row[3], row[4],
                              row[5], row[6], row[7]))
        db.close()

    data_headers = (('Message Timestamp', 'datetime'), ('Received Timestamp', 'datetime'),
                    'Key Remote JID', 'Recipients', 'Direction', 'Message', 'Group Sender', 'Attachment')
    return data_headers, data_list, source


@artifact_processor
def get_whatsapp_one_to_one_messages(context):
    files_found = context.get_files_found()
    db, cursor, source, _wa = _open_msgstore(files_found)
    data_list = []
    if db:
        lid_joins, contact_jid = _contact_jid(cursor, 'jid')
        rows = _run(cursor, f'''
        SELECT
            CASE WHEN message.timestamp = 0 THEN '' ELSE datetime(message.timestamp/1000,'unixepoch') END,
            CASE WHEN message.received_timestamp = 0 THEN ''
                ELSE datetime(message.received_timestamp/1000,'unixepoch') END,
            COALESCE(NULLIF(wa_contacts.wa_name, ''), {contact_jid}),
            CASE WHEN message.from_me=0 THEN COALESCE(wa_contacts.jid, {contact_jid}) ELSE "" END,
            CASE WHEN message.from_me=0 THEN "Incoming" WHEN message.from_me=1 THEN "Outgoing" END,
            ''' + _MESSAGE_TYPE_CASE + f''',
            message.text_data,
            message_media.file_path,
            message_media.file_size,
            message_location.latitude,
            message_location.longitude,
            message_location.live_location_share_duration,
            message_location.live_location_final_latitude,
            message_location.live_location_final_longitude,
            datetime(message_location.live_location_final_timestamp/1000,'unixepoch')
        FROM message
        JOIN chat ON chat._id=message.chat_row_id
        JOIN jid ON jid._id=chat.jid_row_id
        {lid_joins}
        LEFT JOIN message_media ON message_media.message_row_id=message._id
        LEFT JOIN message_location ON message_location.message_row_id=message._id
        LEFT JOIN wa_contacts ON wa_contacts.jid={contact_jid}
        WHERE message.recipient_count=0
            AND COALESCE(jid.raw_string, '') NOT LIKE '%@newsletter'
        ORDER BY message.timestamp ASC
        ''')
        for row in rows:
            data_list.append((_str_to_utc(row[0]), _str_to_utc(row[1]), _str_to_utc(row[14]),
                              row[4], row[2], row[6], _media(row[7]), row[3],
                              row[5], row[7], row[8], row[9], row[10], row[11],
                              row[12], row[13]))
        db.close()

    data_headers = (('Message Timestamp', 'datetime'), ('Received Timestamp', 'datetime'),
                    ('Final Location Timestamp', 'datetime'), 'Message Direction',
                    'Other Participant WA User Name', 'Message', ('Media', 'media'),
                    'Sending Party JID', 'Message Type', 'Local Path To Media',
                    'Media File Size') + _LOCATION_HEADERS
    return data_headers, data_list, source


@artifact_processor
def get_whatsapp_group_messages(context):
    files_found = context.get_files_found()
    db, cursor, source, _wa = _open_msgstore(files_found)
    data_list = []
    if db:
        lid_joins, contact_jid = _contact_jid(cursor, 'jid')
        rows = _run(cursor, f'''
        SELECT
            CASE WHEN message.timestamp = 0 THEN '' ELSE datetime(message.timestamp/1000,'unixepoch') END,
            CASE WHEN message.received_timestamp = 0 THEN ''
                ELSE datetime(message.received_timestamp/1000,'unixepoch') END,
            chat.subject,
            CASE WHEN message.from_me=1 THEN "Self" ELSE COALESCE(NULLIF(wa_contacts.wa_name, ''), {contact_jid}) END,
            CASE WHEN message.from_me=0 THEN COALESCE(wa_contacts.jid, {contact_jid}) ELSE "" END,
            CASE WHEN message.from_me=0 THEN "Incoming" WHEN message.from_me=1 THEN "Outgoing" END,
            ''' + _MESSAGE_TYPE_CASE + f''',
            message.text_data,
            message_media.file_path,
            message_media.file_size,
            message_location.latitude,
            message_location.longitude,
            message_location.live_location_share_duration,
            message_location.live_location_final_latitude,
            message_location.live_location_final_longitude,
            datetime(message_location.live_location_final_timestamp/1000,'unixepoch')
        FROM message
        JOIN chat ON chat._id=message.chat_row_id
        LEFT JOIN jid ON jid._id=message.sender_jid_row_id
        {lid_joins}
        LEFT JOIN message_media ON message_media.message_row_id=message._id
        LEFT JOIN message_location ON message_location.message_row_id=message._id
        LEFT JOIN wa_contacts ON wa_contacts.jid={contact_jid}
        WHERE message.recipient_count>=1
        ORDER BY message.timestamp ASC, message.rowid, chat.rowid, jid.rowid, message_media.rowid,
            message_location.rowid, wa_contacts.rowid
        ''')
        for row in rows:
            data_list.append((_str_to_utc(row[0]), _str_to_utc(row[1]), _str_to_utc(row[15]),
                              row[5], row[3], row[7], _media(row[8]), row[2], row[4],
                              row[6], row[8], row[9], row[10], row[11],
                              row[12], row[13], row[14]))
        db.close()

    data_headers = (('Message Timestamp', 'datetime'), ('Received Timestamp', 'datetime'),
                    ('Final Location Timestamp', 'datetime'), 'Message Direction',
                    'Sending Party', 'Message', ('Media', 'media'), 'Conversation Name',
                    'Sending Party JID', 'Message Type', 'Local Path To Media',
                    'Media File Size') + _LOCATION_HEADERS
    return data_headers, data_list, source


@artifact_processor
def get_whatsapp_group_details(context):
    files_found = context.get_files_found()
    db, cursor, source, _wa = _open_msgstore(files_found)
    data_list = []
    if db:
        # The chat table, not chat_view: the view has no jid_row_id column on older schemas.
        # The creator columns come from wa.db and are NULL when it lacks creator_jid or is absent.
        creator = mapped = name = number = 'NULL'
        if _has_column(cursor, 'wadb', 'wa_group_admin_settings', 'creator_jid'):
            creator = ('''(SELECT creator_jid FROM wadb.wa_group_admin_settings
                WHERE wadb.wa_group_admin_settings.jid = jid.raw_string)''')
            contact = creator
            # A creator recorded by a LID jid (...@lid) is matched to wa.db contacts through
            # msgstore.db jid_map (lid_row_id -> jid_row_id) when that table exists.
            if _has_table(cursor, 'jid_map'):
                mapped = f'''(SELECT mapped_jid.raw_string FROM jid AS lid_jid
                JOIN jid_map ON jid_map.lid_row_id = lid_jid._id
                JOIN jid AS mapped_jid ON mapped_jid._id = jid_map.jid_row_id
                WHERE lid_jid.raw_string = {creator})'''
                contact = f'COALESCE({mapped}, {creator})'
            name = f'(SELECT wa_name FROM wadb.wa_contacts WHERE wadb.wa_contacts.jid = {contact})'
            number = f'(SELECT number FROM wadb.wa_contacts WHERE wadb.wa_contacts.jid = {contact})'
        rows = _run(cursor, f'''
        SELECT
            datetime(chat.created_timestamp/1000,'unixepoch'),
            chat.subject,
            {creator},
            {mapped},
            {name},
            {number},
            jid.raw_string
        FROM chat
        JOIN jid ON jid._id = chat.jid_row_id
        WHERE chat.subject NOT NULL
            AND COALESCE(jid.raw_string, '') NOT LIKE '%@newsletter'
        ORDER BY chat.created_timestamp ASC, chat._id
        ''')
        avatars = _avatars(files_found, source)
        for row in rows:
            group_picture = _media(avatars.get(f'{row[6]}.j', ''))
            creator_picture = next((_media(avatars[f'{jid}.j']) for jid in (row[2], row[3])
                                    if jid and f'{jid}.j' in avatars), '')
            data_list.append((_str_to_utc(row[0]), row[1], group_picture, row[2], row[3], row[4],
                              row[5], creator_picture))
        db.close()

    data_headers = (('Group Creation Timestamp', 'datetime'), 'Group Name', ('Group Picture', 'media'),
                    'Creator JID', 'Creator JID (via jid_map)', 'Creator WA User Name',
                    'Creator WA Number', ('Creator WA Profile Picture', 'media'))
    return data_headers, data_list, source


def _newsletter_joins(cursor):
    """Return (joins, channel name expression), tolerating an absent newsletter table."""
    if not _has_table(cursor, 'newsletter'):
        return '', 'NULL'
    return ('\n        LEFT JOIN newsletter ON newsletter.chat_row_id=chat._id',
            "NULLIF(newsletter.name, '')")


@artifact_processor
def get_whatsapp_channels(context):
    files_found = context.get_files_found()
    db, cursor, source, _wa = _open_msgstore(files_found)
    data_list = []
    if db:
        if _has_table(cursor, 'newsletter'):
            rows = _run(cursor, '''
            SELECT
                CASE WHEN COALESCE(chat.created_timestamp, 0) = 0 THEN ''
                    ELSE datetime(chat.created_timestamp/1000,'unixepoch') END,
                COALESCE(NULLIF(newsletter.name, ''), NULLIF(chat.subject, ''), jid.raw_string),
                jid.raw_string,
                newsletter.description,
                newsletter.invite_code,
                newsletter.verified,
                newsletter.membership,
                newsletter.muted,
                newsletter.subscribers_count,
                (SELECT COUNT(*) FROM message WHERE message.chat_row_id=chat._id)
            FROM newsletter
            JOIN chat ON chat._id=newsletter.chat_row_id
            JOIN jid ON jid._id=chat.jid_row_id
            ORDER BY chat.created_timestamp ASC
            ''')
            for row in rows:
                data_list.append((_str_to_utc(row[0]),) + tuple(row[1:]))
        db.close()

    data_headers = (('Local Chat Created Timestamp', 'datetime'), 'Channel Name', 'Channel JID',
                    'Description', 'Invite Code', 'Verified (as stored)', 'Membership (as stored)',
                    'Muted (as stored)', 'Subscriber Count', 'Messages Stored')
    return data_headers, data_list, source


@artifact_processor
def get_whatsapp_channel_messages(context):
    files_found = context.get_files_found()
    db, cursor, source, _wa = _open_msgstore(files_found)
    data_list = []
    if db:
        joins, name = _newsletter_joins(cursor)
        server_id, reaction = "''", "''"
        if _has_table(cursor, 'newsletter_message'):
            joins += '\n        LEFT JOIN newsletter_message ON newsletter_message.message_row_id=message._id'
            server_id = 'newsletter_message.server_message_id'
            reaction = 'newsletter_message.reaction_from_me'
        rows = _run(cursor, f'''
        SELECT
            CASE WHEN message.timestamp = 0 THEN '' ELSE datetime(message.timestamp/1000,'unixepoch') END,
            CASE WHEN message.received_timestamp = 0 THEN ''
                ELSE datetime(message.received_timestamp/1000,'unixepoch') END,
            CASE WHEN message.from_me=0 THEN "Incoming" WHEN message.from_me=1 THEN "Outgoing" END,
            COALESCE({name}, NULLIF(chat.subject, ''), jid.raw_string),
            message.text_data,
            message_media.file_path,
            ''' + _MESSAGE_TYPE_CASE + f''',
            jid.raw_string,
            {server_id},
            {reaction},
            message_media.file_size
        FROM message
        JOIN chat ON chat._id=message.chat_row_id
        JOIN jid ON jid._id=chat.jid_row_id{joins}
        LEFT JOIN message_media ON message_media.message_row_id=message._id
        WHERE jid.raw_string LIKE '%@newsletter'
        ORDER BY message.timestamp ASC, message._id ASC
        ''')
        for row in rows:
            data_list.append((_str_to_utc(row[0]), _str_to_utc(row[1]), row[2], row[3], row[4],
                              _media(row[5]), row[6], row[7], row[8], row[9], row[5], row[10]))
        db.close()

    data_headers = (('Message Timestamp', 'datetime'), ('Received Timestamp', 'datetime'),
                    'Message Direction', 'Channel Name', 'Message', ('Media', 'media'),
                    'Message Type', 'Channel JID', 'Server Message ID', 'Reaction From Me',
                    'Local Path To Media', 'Media File Size')
    return data_headers, data_list, source


@artifact_processor
def get_whatsapp_user_profile(context):
    files_found = context.get_files_found()
    keys = ('push_name', 'my_current_status', 'version', 'ph', 'cc')
    data = {k: '' for k in keys}
    source = ''
    for file_found in files_found:
        file_found = str(file_found)
        if 'com.whatsapp_preferences_light.xml' not in file_found and 'startup_prefs.xml' not in file_found:
            continue
        source = source or file_found
        try:
            with open(file_found, encoding='utf-8') as fd:
                xml_dict = xmltodict.parse(fd.read())
        except (OSError, ValueError):
            continue
        strings = (xml_dict.get('map') or {}).get('string') or []
        if isinstance(strings, dict):
            strings = [strings]
        for entry in strings:
            if not isinstance(entry, dict):
                continue
            name = entry.get('@name')
            if name in data and not data[name]:
                data[name] = entry.get('#text', '')

    data_list = []
    if any(data.values()):
        data_list.append((data['version'], data['push_name'], data['my_current_status'], data['cc'],
                          data['ph']))

    data_headers = ('Version', 'Name', 'User Status', 'Country Code', 'Mobile Number')
    return data_headers, data_list, source

__artifacts_v2__ = {
    "get_telegramMessages": {
        "name": "Telegram - Messages",
        "description": (
            "Parses Telegram messages from the cache4.db messages_v2 table. Message text is "
            "decoded from the TL-serialised message blob stored in the data column; the "
            "timestamp, direction and read state are read from the table's own columns. "
            "System events such as calls, screenshot notifications and auto-delete timer "
            "changes are named, with the detail they carry. Messages whose blob uses a "
            "constructor this parser does not cover are still reported, with that "
            "constructor named in the message column. A message whose blob cannot be "
            "walked is still reported from the table's columns."
        ),
        "author": "Alexis Brignoni, John Hyla, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-10-01",
        "requirements": "none",
        "category": "Telegram",
        "notes": "The data column holds a TL-serialised TLRPC message object. One cache4.db is "
                 "read per run, the first one matched under files/. The client keeps the databases "
                 "of account slots 1 to 3 under files/account1 to files/account3, which the "
                 "declared paths do not match, so messages of those slots are not reported. "
                 "Reference: Telegram-Android, 'MessagesStorage.java (database directory per "
                 "account)', "
                 "https://github.com/DrKLO/Telegram/blob/45ab8f4308496e1f01026a97fcdb0d58a5274474/"
                 "TMessagesProj/src/main/java/org/telegram/messenger/"
                 "MessagesStorage.java#L309-L313. "
                 "The message "
                 "constructors and their field order are taken from the open-source Telegram "
                 "Android client; constructors from layer 179 onward read a second flags "
                 "integer before the message id, which this parser accounts for. The "
                 "constructors 0x3ae56482, 0x95ef6f2b and 0x7600b9d3 can carry a sender rank "
                 "string ahead of the dialog peer, and the last two a further peer ahead of "
                 "the reply header; both are stepped over. No image listed in sample_data "
                 "holds a message stored under any of those three constructors, so that "
                 "handling is exercised by round-trip tests only. "
                 "Six older constructors differ in fields that sit ahead of the text, and are "
                 "read as the client's own readers read them. 0xbce383d2, 0x58ae39c9 and "
                 "0xf52e6b7f read via_bot_id as a 32-bit integer where the newer constructors "
                 "this parser covers read 64 bits. 0xf52e6b7f also reads from_id as a bare "
                 "32-bit user id and reply_to as a bare 32-bit message id. 0x1e4c8a69 and "
                 "0xa66c7efc read from_boosts_applied after from_id. 0xa4e97f37 is read with "
                 "the layout of 0x2357bf25, the class the client maps it to. No image listed in "
                 "sample_data holds a message stored under any of those six constructors, so "
                 "these layouts are verified against the client source and by round-trip tests, "
                 "not against an image. Reference: Telegram-Android, 'TL_legacy_message.java "
                 "(TL_message_layer118 readParams)', "
                 "https://github.com/DrKLO/Telegram/blob/"
                 "f2908b14133bbffbf7ab04f641ecb5bfaf533242/TMessagesProj/src/main/java/"
                 "org/telegram/tgnet/tl/legacy/TL_legacy_message.java#L3091-L3104"
                 ". Reference: Telegram-Android, 'TL_legacy_message.java (via_bot_id in "
                 "TL_message_layer131 and TL_message_layer123)', "
                 "https://github.com/DrKLO/Telegram/blob/"
                 "f2908b14133bbffbf7ab04f641ecb5bfaf533242/TMessagesProj/src/main/java/"
                 "org/telegram/tgnet/tl/legacy/TL_legacy_message.java#L2835"
                 " and "
                 "https://github.com/DrKLO/Telegram/blob/"
                 "f2908b14133bbffbf7ab04f641ecb5bfaf533242/TMessagesProj/src/main/java/"
                 "org/telegram/tgnet/tl/legacy/TL_legacy_message.java#L2970"
                 ". Reference: Telegram-Android, 'TL_legacy_message.java (from_boosts_applied "
                 "in TL_message_layer176 and TL_message_layer175)', "
                 "https://github.com/DrKLO/Telegram/blob/"
                 "f2908b14133bbffbf7ab04f641ecb5bfaf533242/TMessagesProj/src/main/java/"
                 "org/telegram/tgnet/tl/legacy/TL_legacy_message.java#L2080"
                 " and "
                 "https://github.com/DrKLO/Telegram/blob/"
                 "f2908b14133bbffbf7ab04f641ecb5bfaf533242/TMessagesProj/src/main/java/"
                 "org/telegram/tgnet/tl/legacy/TL_legacy_message.java#L2243"
                 ". Reference: Telegram-Android, 'TLRPC.java (Message.fromConstructor)', "
                 "https://github.com/DrKLO/Telegram/blob/"
                 "f2908b14133bbffbf7ab04f641ecb5bfaf533242/TMessagesProj/src/main/java/"
                 "org/telegram/tgnet/TLRPC.java#L57589-L57591"
                 ". "
                 "Seventeen further message classes are read from their readers in the client's "
                 "TLRPC.java: the four before layer 118 (0x452c0e65, 0x44f9b43d, 0x90dddc11, "
                 "0xc09be45f), which read the same fields ahead of the text as 0xf52e6b7f; ten "
                 "older ones (0xc992e15c, 0x5ba66c13, 0x2bebfa86, 0xf07814c8, 0xc3060325, "
                 "0xa7ab1991, 0x567699b3, 0x22eb6aba, 0xa367e716, 0x05f46804); and the three "
                 "secret chat classes (0x555555fa, 0x555555f9, 0x555555f8), which read a ttl "
                 "integer after the message id. The two TL_messageEmpty constructors "
                 "(0x90a6ca84, 0x83e5de54) are reported as '[Empty message record]'. No image "
                 "listed in sample_data holds a record under any of those nineteen "
                 "constructors, so they are verified against the client source and by "
                 "round-trip tests, not against an image. Where a record's media object carries "
                 "its own caption the client uses that caption as the message text; this parser "
                 "does not read media objects, so for such a record the Message column holds "
                 "the record's text field only. Reference: Telegram-Android, 'TLRPC.java "
                 "(Message.fromConstructor, the classes it names)', "
                 "https://github.com/DrKLO/Telegram/blob/"
                 "f2908b14133bbffbf7ab04f641ecb5bfaf533242/TMessagesProj/src/main/java/"
                 "org/telegram/tgnet/TLRPC.java#L57517-L57616"
                 ". Reference: Telegram-Android, 'TLRPC.java (caption taken from the media, "
                 "TL_message_layer117)', "
                 "https://github.com/DrKLO/Telegram/blob/"
                 "f2908b14133bbffbf7ab04f641ecb5bfaf533242/TMessagesProj/src/main/java/"
                 "org/telegram/tgnet/TLRPC.java#L58530-L58537"
                 ". "
                 "Forward and "
                 "reply headers are stepped over field by field using the same source, so "
                 "forwarded messages and replies are decoded structurally. A reply that "
                 "carries inline reply media, quoted entities or a poll option holds a "
                 "further object tree this parser does not implement; for those, and for any "
                 "header constructor not covered, the text is instead located by searching "
                 "the blob for the row's own date value, which sits immediately before the "
                 "text, and is accepted only when it is a well-formed TL string that decodes "
                 "as strict UTF-8. The same fallback is used when a structural walk ends on a "
                 "date that disagrees with the date column. Text that neither route recovers is "
                 "reported as not recovered rather than guessed at. A reply or forward that was "
                 "walked to its text and whose text is empty has an empty Message; the not "
                 "recovered labels are used only where the walk stopped before the text. "
                 "A record whose walk cannot be completed, because a field is not what the "
                 "layout expects or the record ends early, is still reported: the timestamp, "
                 "dialog, direction, read state and message id are the table's own columns, the "
                 "text is looked for after the row's date value as above, and where that finds "
                 "nothing the Message column reads '[Message not decoded]'. Each such record is "
                 "named in the run log. No record on the nine images listed in sample_data "
                 "ended its walk that way, so this handling is exercised by tests on "
                 "constructed records, not on an image. Sender ID is the from_id read from the "
                 "record, for a service message as for a message. Every from_id on the nine "
                 "images listed in sample_data is a user peer; a from_id that "
                 "is a chat or channel peer is reported by its bare id, without the sign a "
                 "dialog id carries, and no image exercises that. On an incoming row whose "
                 "record holds no from_id, Sender ID is the dialog id; in a group or channel "
                 "dialog that is the id of the chat. On those images each incoming row in a user "
                 "dialog whose record holds a from_id holds the dialog id there. "
                 "On an incoming row where from_id was not reached (a missing record or one "
                 "under 8 bytes, an unrecognised constructor, an empty message record, a walk "
                 "that could not be completed, or a service header that ends before from_id) "
                 "Sender ID is the dialog id when the dialog id is a user id by the client's "
                 "own test, a positive value with neither the secret chat bit nor the folder "
                 "bit set, and is blank otherwise. An outgoing row with no from_id read has a "
                 "blank Sender ID. Reference: Telegram-Android, 'DialogObject.java "
                 "(isUserDialog, isEncryptedDialog)', "
                 "https://github.com/DrKLO/Telegram/blob/"
                 "f2908b14133bbffbf7ab04f641ecb5bfaf533242/TMessagesProj/src/main/java/"
                 "org/telegram/messenger/DialogObject.java#L105-L111"
                 ". "
                 "All eight TL_messageService constructors are recognised; their header is "
                 "walked the same way, its from_id is read, and the action that follows is "
                 "named from the client's own action "
                 "constructors, so system events such as a phone call, a screenshot "
                 "notification, a cleared history or an auto-delete timer change are "
                 "identified rather than reported as an unlabelled service message. Detail "
                 "fields are read for the actions that carry them, including the outcome and "
                 "duration of a call and the new value of an auto-delete timer; an action "
                 "with no reader implemented is reported by name alone. When the client "
                 "stored the message's media at a known location it appends that path to the "
                 "record as a trailing string, which is reported as the recorded media path; "
                 "it is the path the app wrote, and the file is linked only when it is still "
                 "present in the extraction. On the nine images listed in sample_data Recorded "
                 "Media Path held a value on some rows; no "
                 "file of the recorded name is in those images' archives; and Media File had no "
                 "value on any row. "
                 "Reference: "
                 "Telegram-Android, "
                 "'TL_legacy_message.java (TL_message layer constructors)', "
                 "https://github.com/DrKLO/Telegram/blob/"
                 "45ab8f4308496e1f01026a97fcdb0d58a5274474/TMessagesProj/src/main/java/"
                 "org/telegram/tgnet/tl/legacy/TL_legacy_message.java. Reference: "
                 "Telegram-Android, 'generated TlGen_MessageReplyHeader.kt, "
                 "TlGen_MessageFwdHeader.kt, TlGen_Message.kt and TlGen_MessageAction.kt "
                 "(header field order, flag bits, service constructors and action "
                 "constructors)', https://github.com/DrKLO/Telegram/tree/"
                 "45ab8f4308496e1f01026a97fcdb0d58a5274474/TMessagesProj_AppTests/"
                 "src/androidTest/kotlin/org/telegram/tgnet/model/generated",
        "paths": ('*/org.telegram.messenger*/files/cache4.db*',
                  '*/org.telegram.messenger*/cache/**',
                  '*/org.telegram.messenger*/files/Telegram/**'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "anne_a15": "240 rows",
            "hc_pixel8pro_a16": "6 rows",
            "hc_pixel8pro_a17": "17 | 6 rows",
            "kevin_pocox7_a15": "1609 rows",
            "pixel3_a12": "76 rows",
            "pixel7a_a14": "34 rows",
            "russell_a14": "51 rows",
            "russell_pixel6a_a13": "3 rows",
            "sharon_a14": "1 row",
        },
    },
    "get_telegramContacts": {
        "name": "Telegram - Contacts",
        "description": (
            "Parses the device contact records Telegram stored, from the user_contacts_v7 and user_phones_v7 tables of cache4.db, including the first and last name as stored on the device and the phone numbers recorded for that contact key."
        ),
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-10-07",
        "requirements": "none",
        "category": "Telegram",
        "notes": "Both tables store their values as plain text. They are joined on the key column, so one "
                 "contact can carry several phone numbers. A phone row whose deleted column is set is not "
                 "listed. Imported is the integer the table stores, reported as stored. The uid column "
                 "holds the contact id the client assigned to the device contact when it read the address "
                 "book (contact_id in the client source). It is not a Telegram user id and is reported as "
                 "stored; the module heads that column User ID. Reference: Telegram-Android, "
                 "'MessagesStorage.java (user_contacts_v7 insert)', "
                 "https://github.com/DrKLO/Telegram/blob/45ab8f4308496e1f01026a97fcdb0d58a5274474/TMessagesProj/src/main/java/org/telegram/messenger/MessagesStorage.java#L8306-L8318"
                 " This artifact now reads every admitted exact cache4.db main in the supplied input "
                 "order, at the direct files path or the explicitly bounded account1, account2 and "
                 "account3 subdirectories. The subdirectory spelling is a source location, not proof of "
                 "account identity or a complete version-specific storage layout. Each main keeps its own "
                 "phone lookup and contact query; observations from repeated inputs and aliases are "
                 "retained without deduplication or cross-database joins. The Source File column is "
                 "appended only when returned rows combine more than one distinct contributing relative "
                 "input origin; the artifact source lists contributing mains in first-contribution order. "
                 "Empty or query-failing inputs contribute no origin unless their contacts query actually "
                 "returns rows. The existing truthy deleted-phone exclusion, duplicate phone sequence, "
                 "falsey name rendering and ORDER BY fname are unchanged; equal-name ordering is "
                 "unspecified. The historical client-source/identity interpretation above has not been "
                 "independently verified against vendor Java or private samples by this correction. "
                 "Original contribution credited to Alexis Brignoni. Seven other cache4 artifacts retain "
                 "their existing first-input/path limitations; this is not a whole-finding or module "
                 "repair.",
        "paths": (
            '*/org.telegram.messenger*/files/cache4.db*',
            '*/org.telegram.messenger*/files/account1/cache4.db*',
            '*/org.telegram.messenger*/files/account2/cache4.db*',
            '*/org.telegram.messenger*/files/account3/cache4.db*',
        ),
        "output_types": "standard",
        "artifact_icon": "address-book",
        "sample_data": {
            "anne_a15": "4 rows",
            "hc_pixel8pro_a16": "1 row",
            "hc_pixel8pro_a17": "17 | 1 row",
            "kevin_pocox7_a15": "9 rows",
            "pixel7a_a14": "4 rows",
            "russell_pixel6a_a13": "1 row",
            "sharon_a14": "15 rows",
        },
    },
    "get_telegramUsers": {
        "name": "Telegram - Users",
        "description": (
            "Parses the Telegram users cached in the users table of cache4.db, including the "
            "display name, username and last-seen status. A user can appear here without any "
            "exchanged "
            "messages."
        ),
        "author": "Alexis Brignoni, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "Telegram",
        "notes": "The name column stores the display name and username separated by ';;;'. "
                 "The status column holds the expires value of the user's cached status. The "
                 "client stores -100 for a 'recently' status, -101 for 'last week' and -102 for "
                 "'last month' (-1000, -1001 and -1002 when the status is flagged by_me), and "
                 "otherwise the status object's time: the last-online time of an offline status or "
                 "the expiry time of an online status. Only positive values are shown in Last "
                 "Seen, so a Last Seen value can be an online status expiry, and the raw value is "
                 "kept alongside in Status Value. Reference: Telegram-Android, "
                 "'MessagesStorage.java (users insert)', "
                 "https://github.com/DrKLO/Telegram/blob/45ab8f4308496e1f01026a97fcdb0d58a5274474/"
                 "TMessagesProj/src/main/java/org/telegram/messenger/"
                 "MessagesStorage.java#L10666-L10675",
        "paths": ('*/org.telegram.messenger*/files/cache4.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "anne_a15": "111 rows",
            "hc_pixel8pro_a16": "48 rows",
            "hc_pixel8pro_a17": "17 | 80 rows",
            "kevin_pocox7_a15": "523 rows",
            "pixel7a_a14": "46 rows",
            "russell_pixel6a_a13": "2 rows",
            "samsungs20_a13": "4 rows",
            "sharon_a14": "8 rows",
        },
    },
    "get_telegramChats": {
        "name": "Telegram - Chats",
        "description": (
            "Parses the Telegram chat list from the dialogs table of cache4.db, including a chat name where the dialog id as stored equals an id in the users or chats table, the time of the last activity, unread counts and whether the chat is pinned or filed in the archive folder."
        ),
        "author": "Alexis Brignoni, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-03",
        "requirements": "none",
        "category": "Telegram",
        "notes": "The did column is the dialog peer id. It is looked up as stored in the users and "
                 "chats tables for a name; where an id is in both tables the chats name is used "
                 "when it is not empty. A "
                 "group or channel dialog id is stored negative and gets no name here: on anne_a15 "
                 "the 1 row with a negative Dialog ID and on kevin_pocox7_a15 the 4 such rows have "
                 "a blank Chat, and each of those ids matches a chats row once its sign is "
                 "dropped. No id was in both the users and chats tables on those two images "
                 "(counted on runs of 3 Oct 2026). A folder_id of 1 is labelled Archived and any "
                 "other value "
                 "Main; that mapping is not sourced here. The message "
                 "count is taken from the messages_v2 rows carrying the same dialog id.",
        "paths": ('*/org.telegram.messenger*/files/cache4.db*',),
        "output_types": "standard",
        "artifact_icon": "messages",
        "sample_data": {
            "anne_a15": "6 rows",
            "hc_pixel8pro_a16": "1 row",
            "hc_pixel8pro_a17": "17 | 1 row",
            "kevin_pocox7_a15": "42 rows",
            "pixel7a_a14": "4 rows",
            "russell_pixel6a_a13": "1 row",
            "sharon_a14": "1 row",
        },
    },
    "get_telegramAccounts": {
        "name": "Telegram - Accounts",
        "description": (
            "Reports the existing decoded user-record and per-file configuration projections from "
            "selected Telegram userconf XML files, including lastContactsSyncTime through the "
            "existing datetime conversion and the stored last_call_phone_number value. These keys "
            "alone do not establish a contacts-sync event or a dialled call."
        ),
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-08-04",
        "last_update_date": "2026-10-07",
        "requirements": "none",
        "category": "Telegram",
        "notes": "Telegram supports several accounts on one device; slot 0 is stored in userconfing.xml, "
                 "spelled that way by the client, and slots 1 to 3 in userconfig1.xml through "
                 "userconfig3.xml. The user key holds a base64-encoded TL user record, decoded here for "
                 "the account id, names, username and phone number. Two record constructors are read "
                 "(0x215C4438 and 0x31774388). A slot whose record uses another constructor is reported "
                 "with those fields blank, or not reported at all when it also holds no passcode hash and "
                 "no last_call_phone_number value. A passcode is in use when passcodeHash1 holds a value; "
                 "passcodeType 0 is a PIN and 1 is a password. The client keeps these keys, autoLockIn and"
                 " useFingerprint in userconfing.xml only and they apply to the whole app, so the "
                 "Passcode, Auto-Lock and Unlock With Fingerprint cells of a slot 1 to 3 row do not "
                 "describe that slot. Unlock With Fingerprint is blank when the key is absent or false; "
                 "the client's default for an absent key is true. The stored hash and salt are not "
                 "reported, only whether they are present. The lastContactsSyncTime (stored value) column "
                 "is the stored key passed through the existing integer/magnitude-normalizing UTC "
                 "conversion when nonzero; zero, missing and invalid integer text still render blank. The "
                 "datetime annotation and conversion are unchanged. Historical references below state: The"
                 " client sets it to the current time on a contacts sync and also to 23 hours before the "
                 "current time when no value exists, so it is not by itself the time of a sync. The "
                 "last_call_phone_number (as stored) column retains the existing XML-derived key value, "
                 "including existing attribute/text/empty fallback behavior, without inferring call "
                 "direction or an event. The historical CallReceiver reference below attributes that key "
                 "to an incoming ringing number; vendor-version applicability is not verified by this "
                 "header correction. The key was present in userconfing.xml on hc_pixel8pro_a16, "
                 "hc_pixel8pro_a17, kevin_pocox7_a15, pixel7a_a14, russell_pixel6a_a13 and sharon_a14 and "
                 "absent on samsungs20_a13 (counted on runs of 3 Oct 2026). Reference: Telegram-Android, "
                 "'SharedConfig.java (passcodeHash1, passcodeType, autoLockIn)', "
                 "https://github.com/DrKLO/Telegram/blob/45ab8f4308496e1f01026a97fcdb0d58a5274474/TMessagesProj/src/main/java/org/telegram/messenger/SharedConfig.java#L60-L61"
                 " and "
                 "https://github.com/DrKLO/Telegram/blob/45ab8f4308496e1f01026a97fcdb0d58a5274474/TMessagesProj/src/main/java/org/telegram/messenger/SharedConfig.java#L432-L444."
                 " Reference: Telegram-Android, 'UserConfig.java (preference file names)', "
                 "https://github.com/DrKLO/Telegram/blob/45ab8f4308496e1f01026a97fcdb0d58a5274474/TMessagesProj/src/main/java/org/telegram/messenger/UserConfig.java#L412-L416."
                 " Reference: Telegram-Android, 'UserConfig.java (lastContactsSyncTime default)', "
                 "https://github.com/DrKLO/Telegram/blob/45ab8f4308496e1f01026a97fcdb0d58a5274474/TMessagesProj/src/main/java/org/telegram/messenger/UserConfig.java#L304."
                 " Reference: Telegram-Android, 'CallReceiver.java', "
                 "https://github.com/DrKLO/Telegram/blob/45ab8f4308496e1f01026a97fcdb0d58a5274474/TMessagesProj/src/main/java/org/telegram/messenger/CallReceiver.java#L22-L30"
                 " Header neutralization only: all eleven native values, per-slot projection/defaults, two"
                 " admitted user constructors, selected input occurrences, row order and existing source "
                 "aggregation are unchanged. Historical vendor defaults/global configuration/private "
                 "sample observations and remaining constructor/source semantics are not newly verified or"
                 " repaired. Original contribution credited to Alexis Brignoni; cited Telegram-Android "
                 "research retained.",
        "paths": ('*/org.telegram.messenger*/shared_prefs/userconf*.xml',),
        "output_types": "standard",
        "artifact_icon": "user-circle",
        "sample_data": {
            "hc_pixel8pro_a16": "1 row",
            "hc_pixel8pro_a17": "17 | 1 row",
            "kevin_pocox7_a15": "1 row",
            "pixel7a_a14": "1 row",
            "russell_pixel6a_a13": "1 row",
            "samsungs20_a13": "1 row",
            "sharon_a14": "1 row",
        },
    },
    "get_telegramPeerDetails": {
        "name": "Telegram - Peer Details",
        "description": (
            "Reports selected user_settings entries with existing user-name and TL-prefix enrichment."
            " The pinned column is displayed through the existing Python truthiness rule; this report"
            " does not establish pin activity, state or ownership."
        ),
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-08-04",
        "last_update_date": "2026-10-07",
        "requirements": "none",
        "category": "Telegram",
        "notes": "The info column holds a TL user full record. Across the record versions this parser "
                 "covers, the about field follows the id and precedes the nested objects, so it is read "
                 "directly; blocked is flag bit 0 (mask value 1) and needs no field read. Fields that sit "
                 "after the nested settings and notification objects, such as the common chat count, are "
                 "not read because those objects are not implemented. Names are resolved from the users "
                 "table. The pinned column is displayed as Yes when its fetched Python value is truthy, "
                 "and as an empty string otherwise. This is the existing rendering, not a raw value, SQL "
                 "non-zero comparison, or verified pin state. Native NULL, numeric zero and empty "
                 "text/bytes render blank; nonempty text such as '0', negative numbers and nonempty bytes "
                 "render Yes. Historical research attributes this column to the record's pinned message "
                 "id; that vendor attribution is retained but not independently verified here. Reference: "
                 "Telegram-Android, 'MessagesStorage.java (user_settings insert)', "
                 "https://github.com/DrKLO/Telegram/blob/45ab8f4308496e1f01026a97fcdb0d58a5274474/TMessagesProj/src/main/java/org/telegram/messenger/MessagesStorage.java#L7294-L7299."
                 " Reference: Telegram-Android, 'generated TlGen_UserFull.kt (record layout and flag "
                 "bits)', "
                 "https://github.com/DrKLO/Telegram/tree/45ab8f4308496e1f01026a97fcdb0d58a5274474/TMessagesProj_AppTests/src/androidTest/kotlin/org/telegram/tgnet/model/generated"
                 " The decoder/profile/blocked-layout claims and client-source links above are retained "
                 "historical research, not newly verified. All six native values, users dictionary and "
                 "TL-prefix decoder, SQL row occurrences/order, first selected main, headers other than "
                 "the pinned qualifier, source paths and eleven sibling artifacts are unchanged. Raw "
                 "pinned values and NULL/zero/type distinctions are not added by this header change. "
                 "First-source/account-state selection, peer/name association and constructor/version "
                 "meanings remain unresolved. Original contribution credited to Alexis Brignoni.",
        "paths": ('*/org.telegram.messenger*/files/cache4.db*',),
        "output_types": "standard",
        "artifact_icon": "address-book",
        "sample_data": {
            "anne_a15": "6 rows",
            "hc_pixel8pro_a16": "2 rows",
            "hc_pixel8pro_a17": "17 | 2 rows",
            "kevin_pocox7_a15": "45 rows",
            "pixel7a_a14": "3 rows",
            "russell_pixel6a_a13": "2 rows",
            "samsungs20_a13": "1 row",
            "sharon_a14": "3 rows",
        },
    },
    "get_telegramChatDetails": {
        "name": "Telegram - Chat Details",
        "description": (
            "Parses the cached group and channel detail Telegram stores in the "
            "chat_settings_v2 table of cache4.db, reporting the description and, where the "
            "record carries them, the participant, administrator, removed, banned and online "
            "member counts."
        ),
        "author": "Alexis Brignoni, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-04",
        "last_update_date": "2026-08-15",
        "requirements": "none",
        "category": "Telegram",
        "notes": "The info column holds a TL chat full or channel full record. The "
                 "description follows the id and the member counts follow it behind flags. The id "
                 "is read as 64 bits for every record version. The client reads a 32-bit id for "
                 "older record versions, for example channel full layer 132 (0x2f532f3c) and chat "
                 "full layer 132 (0x49a0a5d9), so a record stored under one of those is not read "
                 "correctly by this artifact. The 5 tested records (1 on anne_a15, 4 on "
                 "kevin_pocox7_a15, counted on runs of 3 Oct 2026) are channel full layer 225 (4) "
                 "and layer 204 (1), which the client reads with a 64-bit id, so no tested record "
                 "is of an affected version. Fields that sit after "
                 "the record's nested photo and notification objects are not read because "
                 "those objects are not implemented. Basic group records carry a description "
                 "but no counts. Names are resolved from the chats table. Reference: "
                 "Telegram-Android, 'generated TlGen_ChatFull.kt (record layouts and flag "
                 "bits)', https://github.com/DrKLO/Telegram/tree/"
                 "45ab8f4308496e1f01026a97fcdb0d58a5274474/TMessagesProj_AppTests"
                 "/src/androidTest/kotlin/org/telegram/tgnet/model/generated",
        "paths": ('*/org.telegram.messenger*/files/cache4.db*',),
        "output_types": "standard",
        "artifact_icon": "users-group",
        "sample_data": {
            "anne_a15": "1 row",
            "kevin_pocox7_a15": "4 rows",
        },
    },
    "get_telegramSaveToGallery": {
        "name": "Telegram - Save to Gallery Settings",
        "description": (
            "Parses the Telegram save-to-gallery configuration from the mainconfig.xml shared preferences file, reporting for each category of chat whether incoming photos and videos are saved to the device gallery and the video size limit. The client writes these keys when a setting is saved or when it migrates the older save_gallery setting. A category reported as not set had no key, and the client then applies its defaults: photos and videos off, video limit 100 MB."
        ),
        "author": "Alexis Brignoni, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-04",
        "last_update_date": "2026-08-15",
        "requirements": "none",
        "category": "Telegram",
        "notes": "Keys are <prefix>_save_gallery_photo, <prefix>_save_gallery_video and "
                 "<prefix>_save_gallery_limitVideo, where the prefix is user, groups or "
                 "channels. The client reads the photo and video keys with a default of false and "
                 "the limitVideo key with a default of 104,857,600 bytes (100 MB), so an absent "
                 "key means that default applied. The module prints 'Not set (app default, off)' "
                 "in Video Size Limit when the limit key is absent; the client's default for that "
                 "key is 100 MB, not off. Per-chat exceptions, which the client keeps in separate "
                 "preference files, are not read. The older single "
                 "save_gallery key is reported when present. Reference: Telegram-Android, "
                 "'SaveToGallerySettingsHelper.java (preference key names and defaults)', "
                 "https://github.com/DrKLO/Telegram/blob/"
                 "45ab8f4308496e1f01026a97fcdb0d58a5274474/TMessagesProj/src/main/java/"
                 "org/telegram/messenger/SaveToGallerySettingsHelper.java"
                 "#L161-L167",
        "paths": ('*/org.telegram.messenger*/shared_prefs/mainconfig.xml',),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "anne_a15": "3 rows",
            "hc_pixel8pro_a16": "3 rows",
            "hc_pixel8pro_a17": "17 | 3 rows",
            "kevin_pocox7_a15": "3 rows",
            "pixel7a_a14": "3 rows",
            "russell_pixel6a_a13": "3 rows",
            "samsungs20_a13": "3 rows",
            "sharon_a14": "3 rows",
        },
    },
    "get_telegramChannelMembers": {
        "name": "Telegram - Channel & Group Members",
        "description": (
            "Parses the channel and group membership Telegram cached, from the channel_users_v2 table of cache4.db, reporting the chat, the member and the date value stored with each row, which the client sets from the time it cached the list, with names resolved from the users and chats tables."
        ),
        "author": "Alexis Brignoni, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-05",
        "last_update_date": "2026-08-05",
        "requirements": "none",
        "category": "Telegram",
        "notes": "The dialog id, user id and date columns are stored as plain integers and "
                 "are reported as such. The client sets date to the time it cached the participant "
                 "list and lowers it by one second for each participant in list order, so it is "
                 "not the date a member joined. Reference: Telegram-Android, 'MessagesStorage.java "
                 "(updateChannelUsers)', "
                 "https://github.com/DrKLO/Telegram/blob/45ab8f4308496e1f01026a97fcdb0d58a5274474/"
                 "TMessagesProj/src/main/java/org/telegram/messenger/"
                 "MessagesStorage.java#L7063-L7084. "
                 "The data column holds a TL channel participant "
                 "record; the creator constructor is named where it appears and any other "
                 "constructor is reported by its id rather than guessed at. The membership "
                 "cached here is what the client had retrieved, which is not necessarily "
                 "the full member list of the chat.",
        "paths": ('*/org.telegram.messenger*/files/cache4.db*',),
        "output_types": "standard",
        "artifact_icon": "users-group",
        "sample_data": {
            "anne_a15": "32 rows",
            "kevin_pocox7_a15": "64 rows",
        },
    },
    "get_telegramChatHints": {
        "name": "Telegram - Chat Hint Entries",
        "description": (
            "Reports the selected cache4.db chat_hints table entries with existing name enrichment "
            "and date conversion, ordered by stored rating descending. The stored rating and type do "
            "not establish chat frequency, use, scale or ownership."
        ),
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-08-05",
        "last_update_date": "2026-10-07",
        "requirements": "none",
        "category": "Telegram",
        "notes": "The did, rating and date columns are stored as plain values. The type column is reported"
                 " as stored because its values are not documented in the client source that was checked. "
                 "The rating value is reported as stored. What it measures and its scale are not "
                 "established. Artifact naming describes table entries only, not frequent chat events. "
                 "Existing name lookup, positive-date conversion, first selected main, row occurrences and"
                 " query ordering are unchanged. Negative/zero/missing dates remain blank under the "
                 "existing policy; table/schema/version coverage, rating/type meanings, name/peer "
                 "association and source-state selection remain unresolved. Original contribution credited"
                 " to Alexis Brignoni; historical client-source and private sample observations are "
                 "retained but not newly verified.",
        "paths": ('*/org.telegram.messenger*/files/cache4.db*',),
        "output_types": "standard",
        "artifact_icon": "star",
        "sample_data": {
            "anne_a15": "4 rows",
            "hc_pixel8pro_a16": "1 row",
            "hc_pixel8pro_a17": "17 | 1 row",
            "pixel7a_a14": "1 row",
            "russell_pixel6a_a13": "1 row",
            "sharon_a14": "1 row",
        },
    },
    "get_telegramVoipLogs": {
        "name": "Telegram - VoIP Call Logs",
        "description": (
            "Parses the per-call WebRTC logs Telegram writes under cache/voip_logs. Each log "
            "is named for the call it belongs to, so the file records a call id and the span of "
            "its logged timestamps, independently of the message "
            "history."
        ),
        "author": "Alexis Brignoni, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-05",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Telegram",
        "notes": "The client names each log <call id>.log and each statistics log <call "
                 "id>_stats.log (Reference: Telegram-Android, 'VoIPHelper.java (getLogFilePath)', "
                 "https://github.com/DrKLO/Telegram/blob/45ab8f4308496e1f01026a97fcdb0d58a5274474/"
                 "TMessagesProj/src/main/java/org/telegram/ui/Components/voip/"
                 "VoIPHelper.java#L795-L816); "
                 "where a phone call service message in the chat "
                 "carries the same id, the two can be tied together. The timestamps inside the "
                 "log are local-time strings with no timezone, so they are reported as recorded "
                 "and only their difference is used for the logged span. Log Last Modified (UTC) "
                 "is the modification time the extraction records for the log file as seconds "
                 "since 1970 UTC: a zip member's extended timestamp field, a tar member's time, or "
                 "the file's own time for a folder input. It is blank when a zip member carries "
                 "no extended timestamp, because the member's other stored time has no zone. "
                 "On pixel7a_a14 the log's zip member carries an extended timestamp. "
                 "The logged span is the difference "
                 "between the first and last timestamp in the log and is not a call duration. "
                 "Approach adapted from a Telegram parser contributed by WriteBlocked in "
                 "ALEAPP pull request 716.",
        "paths": ('*/org.telegram.messenger*/cache/voip_logs/*',),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "pixel7a_a14": "1 row",
        },
    },
    "get_telegramAutoDownload": {
        "name": "Telegram - Auto-Download Settings",
        "description": (
            "Parses the Telegram media auto-download configuration from the mainconfig.xml shared preferences file. Reports the stored mobilePreset, wifiPreset and roamingPreset strings: the enabled flag, the media types set for each category of chat and the size limits. The client applies these strings only while currentMobilePreset, currentWifiPreset or currentRoamingPreset is not 0, 1 or 2 (the default is 3); for 0, 1 or 2 it applies preset0, preset1 or preset2, which are not reported here."
        ),
        "author": "Alexis Brignoni, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-08-15",
        "requirements": "none",
        "category": "Telegram",
        "notes": "Each preset is an underscore-separated string. The first four values are "
                 "auto-download masks for contacts, other private chats, groups and channels "
                 "in that order, and each mask is a bit field of photo 1, audio 2, video 4 "
                 "and document 8. The next four values are the photo, video, document and "
                 "audio size limits in bytes, followed by preload video, preload music and "
                 "the enabled flag. Reference: Telegram-Android, 'DownloadController.java "
                 "(Preset string layout and AUTODOWNLOAD_TYPE masks)', "
                 "https://github.com/DrKLO/Telegram/blob/"
                 "45ab8f4308496e1f01026a97fcdb0d58a5274474/TMessagesProj/src/main/java/"
                 "org/telegram/messenger/DownloadController.java",
        "paths": ('*/org.telegram.messenger*/shared_prefs/mainconfig.xml',),
        "output_types": "standard",
        "artifact_icon": "download",
        "sample_data": {
            "anne_a15": "12 rows",
            "hc_pixel8pro_a16": "12 rows",
            "hc_pixel8pro_a17": "17 | 12 rows",
            "kevin_pocox7_a15": "12 rows",
            "pixel7a_a14": "12 rows",
            "russell_pixel6a_a13": "12 rows",
            "samsungs20_a13": "12 rows",
            "sharon_a14": "12 rows",
        },
    },
}

import base64
import datetime
import io
import os
import re
import struct
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc, convert_unix_ts_to_utc, \
    get_sqlite_db_records, get_file_path, check_in_media


# --- TL deserialisation ------------------------------------------------------
# Telegram stores message objects in the data column using the TL wire format:
# a 4-byte little-endian constructor id followed by the object's fields.

_PEER_USER = 0x59511722
_PEER_CHAT = 0x36C6019A
_PEER_CHANNEL = 0xA2A5371E
# Layer 132 and older wrote the peer id as an Int32 under its own constructor.
# A device on an older Telegram build stores messages with these, and reading
# them as the 64-bit form misaligns every field that follows.
_PEER_USER_LEGACY = 0x9DB1BC6D
_PEER_CHAT_LEGACY = 0xBAD0E5BB
_PEER_CHANNEL_LEGACY = 0xBDDDE532

# TL_message constructors that read a second flags integer before the id:
# the current TL_message in TLRPC.java (0x7600B9D3, layer 227 on) and
# TL_legacy_message.java, classes TL_message_layer179 and newer. 0xA4E97F37 is
# not a class of its own: Message.TLdeserialize in TLRPC.java maps it to
# TL_message_layer179 beside 0x2357BF25, so it is read with that layout.
_MSG_WITH_FLAGS2 = {
    0x7600B9D3,
    0x95EF6F2B, 0x3AE56482, 0x9CB490E9, 0xB92F76CF, 0x9815CEC8,
    0xEABCDD4D, 0x96FDBBE9, 0x94345242, 0xBDE09C2E, 0x2357BF25,
    0xA4E97F37,
}
# Constructors that write from_rank (flags2 bit 12) after from_boosts_applied:
# TL_message_layer224, TL_message_layer226 and the current TL_message.
_MSG_WITH_FROM_RANK = {0x3AE56482, 0x95EF6F2B, 0x7600B9D3}
# Constructors that write guestchat_via_from (flags2 bit 19) after
# via_business_bot_id: TL_message_layer226 and the current TL_message.
_MSG_WITH_GUESTCHAT = {0x95EF6F2B, 0x7600B9D3}

# TL_message constructors without the second flags integer.
_MSG_NO_FLAGS2 = {
    0xA66C7EFC, 0x1E4C8A69, 0x76BEC211, 0x38116EE0, 0x85D6CBE2,
    0xBCE383D2, 0x58AE39C9, 0xF52E6B7F,
    0x452C0E65, 0x44F9B43D, 0x90DDDC11, 0xC09BE45F,
}
_MSG_ALL = _MSG_WITH_FLAGS2 | _MSG_NO_FLAGS2
# Constructors that read from_boosts_applied (flags bit 29) after from_id:
# TL_message_layer175 and TL_message_layer176 as well as every constructor
# that reads the second flags integer.
_MSG_WITH_FROM_BOOSTS = _MSG_WITH_FLAGS2 | {0xA66C7EFC, 0x1E4C8A69}
# Constructors that read saved_peer_id (flags bit 28) after peer_id:
# TL_message_layer173 and newer. The older readers have no such field.
_MSG_WITH_SAVED_PEER = _MSG_WITH_FLAGS2 | {0xA66C7EFC, 0x1E4C8A69, 0x76BEC211}
# TL_message_layer118 and the four classes before it in TLRPC.java
# (TL_message_layer117, TL_message_layer104, TL_message_layer72 and
# TL_message_layer68) read the same fields ahead of the text.
_MSG_LAYER118_AND_OLDER = {0xF52E6B7F, 0x452C0E65, 0x44F9B43D, 0x90DDDC11, 0xC09BE45F}
# TL_message_layer131, TL_message_layer123 and those read via_bot_id as an
# Int32; every newer constructor reads an Int64.
_MSG_VIA_BOT_INT32 = {0xBCE383D2, 0x58AE39C9} | _MSG_LAYER118_AND_OLDER
# TL_message_layer118 and older read from_id as a bare Int32 user id, with no
# peer constructor in front of it, and reply_to as a bare Int32
# reply_to_msg_id in place of a MessageReplyHeader object.
_MSG_BARE_FROM_AND_REPLY = _MSG_LAYER118_AND_OLDER

# Older message classes and the secret chat classes, as the fields their
# readers in TLRPC.java take before the date and the text. 'from' is a bare
# Int32 user id; a trailing '?' marks a field read only under its flag bit
# (from: 8, fwd: 2, via: 11, reply: 3). 'fwd_peer' is a Peer and an Int32
# date, 'fwd_user' an Int32 user id and an Int32 date, 'bool' a 4-byte Bool.
_OLD6 = ('flags', 'int32', 'from', 'peer', 'fwd_user?', 'reply?')
_SECRET = ('flags', 'int32', 'int32', 'from', 'peer')          # id, then ttl
_MSG_OLD_LAYOUTS = {
    0xC992E15C: ('flags', 'int32', 'from?', 'peer', 'fwd_peer?', 'via?', 'reply?'),  # TL_message_layer47
    0x5BA66C13: ('flags', 'int32', 'from?', 'peer', 'fwd_peer?', 'reply?'),   # TL_message_old7
    0x2BEBFA86: _OLD6,                                           # TL_message_old6
    0xF07814C8: _OLD6,                                           # TL_message_old5
    0xC3060325: _OLD6,                                           # TL_message_old4
    0xA7AB1991: _OLD6,                                           # TL_message_old3
    0x567699B3: ('flags', 'int32', 'from', 'peer'),              # TL_message_old2
    0x22EB6ABA: ('int32', 'from', 'peer', 'bool', 'bool'),       # TL_message_old
    0xA367E716: ('flags', 'int32', 'fwd_user', 'from', 'peer'),  # TL_messageForwarded_old2
    0x05F46804: ('int32', 'fwd_user', 'from', 'peer', 'bool', 'bool'),  # TL_messageForwarded_old
    0x555555FA: _SECRET,                                         # TL_message_secret
    0x555555F9: _SECRET,                                         # TL_message_secret_layer72
    0x555555F8: _SECRET,                                         # TL_message_secret_old
}
_OLD_FLAG_BITS = {'from?': 1 << 8, 'fwd_peer?': 1 << 2, 'fwd_user?': 1 << 2,
                  'via?': 1 << 11, 'reply?': 1 << 3}
# TL_messageEmpty and TL_messageEmpty_layer122: an id and at most a peer.
_MSG_EMPTY = {0x90A6CA84, 0x83E5DE54}

# What a walk over a record that does not match the layout it was read with
# raises: a short read, an index past the end, or a peer constructor that is
# not one.
_WALK_ERRORS = (struct.error, IndexError, UnicodeDecodeError, ValueError)

# Every TL_messageService constructor defined by the client.
_MSG_SERVICE = {
    0x7A800E0A,   # TL_messageService
    0xD3D28540,   # TL_messageService_layer204
    0x2B085862,   # TL_messageService_layer195
    0x286FA604,   # TL_messageService_layer123
    0x9E19A1F6,   # TL_messageService_layer118
    0xC06B9607,   # TL_messageService_layer48
    0x1D86F70E,   # TL_messageService_old2
    0x9F8D60BB,   # TL_messageService_old
}

# Forward headers, as (constructor: (flag, kind) steps). A flag of 0 marks an
# unconditional field. Every field is a scalar, string or peer, so a forward
# header can always be stepped over.
_FWD_HEADERS = {
    0x4E4DF4BB: (   # TL_messageFwdHeader
        (1, 'peer'), (32, 'string'), (0, 'int32'), (4, 'int32'), (8, 'string'),
        (16, 'peer'), (16, 'int32'), (256, 'peer'), (512, 'string'),
        (1024, 'int32'), (64, 'string'),
    ),
    0x5F777DCE: (   # TL_messageFwdHeader_layer169
        (1, 'peer'), (32, 'string'), (0, 'int32'), (4, 'int32'), (8, 'string'),
        (16, 'peer'), (16, 'int32'), (64, 'string'),
    ),
}

# Reply headers. 'media', 'entities' and 'bytes' mark fields whose payload is a
# further object tree this parser does not implement; hitting one stops the
# structural walk and the text is recovered by anchoring on the date instead.
_REPLY_HEADERS = {
    0x1B97DD66: (   # TL_messageReplyHeader
        (16, 'int32'), (1, 'peer'), (32, 'fwd'), (256, 'media'), (2, 'int32'),
        (64, 'string'), (128, 'entities'), (1024, 'int32'), (2048, 'int32'),
        (4096, 'bytes'),
    ),
    0x6917560B: (   # TL_messageReplyHeader_layer223
        (16, 'int32'), (1, 'peer'), (32, 'fwd'), (256, 'media'), (2, 'int32'),
        (64, 'string'), (128, 'entities'), (1024, 'int32'), (2048, 'int32'),
    ),
    0xAFBC09DB: (   # TL_messageReplyHeader_layer207
        (16, 'int32'), (1, 'peer'), (32, 'fwd'), (256, 'media'), (2, 'int32'),
        (64, 'string'), (128, 'entities'), (1024, 'int32'),
    ),
    0x6EEBCABD: (   # TL_messageReplyHeader_layer166
        (16, 'int32'), (1, 'peer'), (32, 'fwd'), (256, 'media'), (2, 'int32'),
        (64, 'string'), (128, 'entities'),
    ),
    0xA6D57763: (   # TL_messageReplyHeader_layer165; the id is unconditional
        (0, 'int32'), (1, 'peer'), (2, 'int32'),
    ),
}

# Story reply headers carry no flags field.
_REPLY_STORY_HEADERS = {
    0x0E5AF939: (('peer',), ('int32',)),    # TL_messageReplyStoryHeader
    0x9C98BFC1: (('int64',), ('int32',)),   # TL_messageReplyStoryHeader_layer173
}


class _TLReader:
    """Minimal reader for the TL wire format."""

    def __init__(self, data):
        self.stream = io.BytesIO(data)

    def read_int32(self):
        return struct.unpack('<i', self.stream.read(4))[0]

    def read_uint32(self):
        return struct.unpack('<I', self.stream.read(4))[0]

    def read_int64(self):
        return struct.unpack('<q', self.stream.read(8))[0]

    def read_string(self):
        length = self.stream.read(1)[0]
        if length < 254:
            data = self.stream.read(length)
            consumed = length + 1
        else:
            length = int.from_bytes(self.stream.read(3), 'little')
            data = self.stream.read(length)
            consumed = length + 4
        self.stream.read((4 - consumed % 4) % 4)   # TL pads to a 4-byte boundary
        return data.decode('utf-8', 'replace')

    def read_peer(self):
        constructor = self.read_uint32()
        if constructor in (_PEER_USER, _PEER_CHAT, _PEER_CHANNEL):
            return self.read_int64()
        if constructor in (_PEER_USER_LEGACY, _PEER_CHAT_LEGACY,
                           _PEER_CHANNEL_LEGACY):
            return self.read_int32()
        raise ValueError(f'unexpected peer constructor {constructor:#x}')


# Service message headers, as (reads_flags, steps) up to but excluding the
# action. Layouts from the client's generated TL model.
_SERVICE_HEADERS = {
    0x7A800E0A: (True, ((0, 'int32'), (256, 'peer'), (0, 'peer'),
                        (268435456, 'peer'), (8, 'reply'), (0, 'int32'))),
    0xD3D28540: (True, ((0, 'int32'), (256, 'peer'), (0, 'peer'),
                        (8, 'reply'), (0, 'int32'))),
    0x2B085862: (True, ((0, 'int32'), (256, 'peer'), (0, 'peer'),
                        (8, 'reply'), (0, 'int32'))),
    0x286FA604: (True, ((0, 'int32'), (256, 'peer'), (0, 'peer'),
                        (8, 'reply'), (0, 'int32'))),
    0x9E19A1F6: (True, ((0, 'int32'), (256, 'int32'), (0, 'peer'),
                        (8, 'int32'), (0, 'int32'))),
    0xC06B9607: (True, ((0, 'int32'), (256, 'int32'), (0, 'peer'), (0, 'int32'))),
    0x1D86F70E: (True, ((0, 'int32'), (0, 'int32'), (0, 'peer'), (0, 'int32'))),
    0x9F8D60BB: (False, ((0, 'int32'), (0, 'int32'), (0, 'peer'), (0, 'int32'),
                         (0, 'int32'), (0, 'int32'))),
}

# Human labels for every TL_messageAction constructor the client defines.
_ACTION_NAMES = {
    0x031224c3: 'Joined chat by invite link',
    0x08557637: 'Star gift',
    0x0d999256: 'Topic created',
    0x15cefd00: 'User added to chat',
    0x16605e3e: 'Managed bot created',
    0x26077b99: 'Star gift unique',
    0x2a9fadc5: 'Giveaway results',
    0x2c8f2a25: 'Suggest birthday',
    0x2e3ae60e: 'Star gift unique',
    0x2ffe2f7a: 'Conference call',
    0x31518e9b: 'Requested peer',
    0x31c48347: 'Gift code',
    0x332ba9ed: 'Giveaway launch',
    0x34f762f3: 'Star gift unique',
    0x399674dc: 'Poll delete answer',
    0x3c134d7b: 'Auto-delete timer changed',
    0x3e2793ba: 'No forwards request',
    0x40699cd0: 'Payment sent',
    0x41b3e202: 'Payment refunded',
    0x45d5b021: 'Gift stars',
    0x4717e8a5: 'Star gift',
    0x4792929b: 'Screenshot taken',
    0x47dd8079: 'Web view data sent me',
    0x488a7337: 'User added to chat',
    0x48e91302: 'Gift premium',
    0x502f92f7: 'Invited to group call',
    0x5060a3f4: 'Chat wallpaper changed',
    0x51bdb021: 'Group upgraded to supergroup',
    0x56d03994: 'Gift code',
    0x57de635e: 'Profile photo suggested',
    0x5d20bae8: 'Change community',
    0x5e3cfc4b: 'User added to chat',
    0x678c2e09: 'Gift code',
    0x69f916f8: 'Suggested post refund',
    0x6c6274fa: 'Gift premium',
    0x70ef8294: 'Contact joined Telegram',
    0x73ada76b: 'Star gift purchase offer declined',
    0x76b9f11a: 'Invited to group call',
    0x774278d4: 'Star gift purchase offer',
    0x7a0d7f42: 'Group call',
    0x7fcb13a8: 'Chat photo changed',
    0x80e11a7f: 'Phone call',
    0x84b88578: 'Paid messages price',
    0x87e2f155: 'Giveaway results',
    0x8f31b327: 'Payment sent me',
    0x92a72876: 'Game score',
    0x94bd38ed: 'Message pinned',
    0x95728543: 'Star gift unique',
    0x95d2ac92: 'Channel created',
    0x95ddcf69: 'Suggested post success',
    0x95e3f807: 'Chat photo removed',
    0x95e3fbef: 'Chat photo removed',
    0x96163f56: 'Payment sent',
    0x98e0d697: 'Proximity alert triggered',
    0x9bb3ef44: 'Star gift',
    0x9da1cd6c: 'Poll append answer',
    0x9fbab604: 'History cleared',
    0xa43f30cc: 'User removed from chat',
    0xa6638b9a: 'Group created',
    0xa80f51e4: 'Giveaway launch',
    0xa8a3c699: 'Gift ton',
    0xaa1afbfd: 'Auto-delete timer changed',
    0xaa786345: 'Chat theme changed',
    0xaba0f5c6: 'Gift premium',
    0xabe9affe: 'Bot allowed',
    0xac1f1fcd: 'Paid messages refunded',
    0xacdfcb81: 'Star gift unique',
    0xb00c47a2: 'Prize stars',
    0xb055eaee: 'Migrated from group',
    0xb07ed085: 'New creator pending',
    0xb18a431c: 'Topic edited',
    0xb2ae9b0c: 'User removed from chat',
    0xb3a07661: 'Group call scheduled',
    0xb4c38cb5: 'Web view data sent',
    0xb5a1ce5a: 'Chat title changed',
    0xb6aef7b0: 'Empty action',
    0xb91bbd3a: 'Chat theme changed',
    0xbc44a927: 'Chat wallpaper changed',
    0xbcd71419: 'Paid messages price',
    0xbd47cbad: 'Group created',
    0xbf7d6572: 'Content protection toggled',
    0xc0787d6d: 'Set same chat wall paper',
    0xc0944820: 'Topic edited',
    0xc516d679: 'Bot allowed',
    0xc624b16e: 'Payment sent',
    0xc7edbc83: 'Todo append tasks',
    0xc83d6aec: 'Gift premium',
    0xcc02aa6d: 'Boost apply',
    0xcc7c5c89: 'Todo completions',
    0xd2cfdb0e: 'Gift code',
    0xd8f4f0a7: 'Star gift',
    0xd95c6154: 'Telegram Passport data sent',
    0xdb596550: 'Star gift',
    0xe1037f92: 'Group upgraded to supergroup',
    0xe188503b: 'Chat owner changed',
    0xe6c31522: 'Star gift unique',
    0xe7e75f97: 'Attach menu bot allowed',
    0xea2c31d3: 'Star gift',
    0xea3948e9: 'Migrated from group',
    0xebbca3cb: 'Joined chat by request',
    0xee7a1596: 'Suggested post approval',
    0xf24de7fa: 'Star gift',
    0xf3f25f76: 'Contact joined Telegram',
    0xf89cf5e8: 'Joined chat by invite link',
    0xfae69f56: 'Custom action',
    0xfe77345d: 'Requested peer',
    0xffa00ccc: 'Payment sent me',
}

# TlGen_Vector writes this constructor, then a count, then the elements.
_VECTOR = 0x1CB5C415

# InputGroupCall variants carried by TL_messageActionInviteToGroupCall.
_INPUT_GROUP_CALLS = {
    0xD8AA840F: ('int64', 'int64'),   # TL_inputGroupCall: id, access_hash
    0xFE06823F: ('string',),          # TL_inputGroupCallSlug: slug
    0x8C10603F: ('int32',),           # TL_inputGroupCallInviteMessage: msg_id
}

# Bare constructors carried by TL_messageActionPhoneCall.
_DISCARD_REASONS = {
    0x85E42301: 'missed',
    0xE095C1A0: 'disconnected',
    0x57ADC690: 'hung up',
    0xFAF7E8C9: 'busy',
}

# Payload readers for the actions that carry detail worth reporting. Each entry
# is (flags?, steps); a step of (flag, kind, label) with flag 0 is unconditional.
_ACTION_PAYLOADS = {
    0xB5A1CE5A: (False, ((0, 'string', 'title'),)),                  # ChatEditTitle
    0xBD47CBAD: (False, ((0, 'string', 'title'),
                         (0, 'vector-int64', 'members'))),           # ChatCreate
    0xA6638B9A: (False, ((0, 'string', 'title'),
                         (0, 'vector-int32', 'members'))),           # ChatCreate_layer132
    0x15CEFD00: (False, ((0, 'vector-int64', 'users'),)),            # ChatAddUser
    0x488A7337: (False, ((0, 'vector-int32', 'users'),)),            # ChatAddUser_layer132
    0x502F92F7: (False, ((0, 'groupcall', 'call'),
                         (0, 'vector-int64', 'users'))),             # InviteToGroupCall
    0x76B9F11A: (False, ((0, 'groupcall', 'call'),
                         (0, 'vector-int32', 'users'))),             # InviteToGroupCall_layer132
    0xA43F30CC: (False, ((0, 'int64', 'user'),)),                    # ChatDeleteUser
    0x031224C3: (False, ((0, 'int64', 'inviter'),)),                 # ChatJoinedByLink
    0xFAE69F56: (False, ((0, 'string', 'message'),)),                # CustomAction
    0x92A72876: (False, ((0, 'int64', 'game'), (0, 'int32', 'score'))),  # GameScore
    0x3C134D7B: (True, ((0, 'int32', 'timer seconds'),)),                  # SetMessagesTTL
    0x80E11A7F: (True, ((0, 'int64', 'call id'), (1, 'reason', 'outcome'),
                        (2, 'int32', 'duration seconds'))),          # PhoneCall
    0x98E0D697: (False, ((0, 'peer', 'from'), (0, 'peer', 'to'),
                         (0, 'int32', 'metres'))),                   # GeoProximityReached
    0xC624B16E: (True, ((0, 'string', 'currency'), (0, 'int64', 'amount'))),  # PaymentSent
}


def _read_action_payload(reader, constructor):
    """Read the detail fields of an action, when one is implemented for it."""
    entry = _ACTION_PAYLOADS.get(constructor)
    if entry is None:
        return ''
    reads_flags, steps = entry
    flags = reader.read_uint32() if reads_flags else 0
    parts = []
    for flag, kind, label in steps:
        if flag and not flags & flag:
            continue
        if kind == 'int32':
            value = reader.read_int32()
        elif kind == 'int64':
            value = reader.read_int64()
        elif kind == 'string':
            value = reader.read_string()
        elif kind == 'peer':
            value = reader.read_peer()
        elif kind == 'reason':
            value = _DISCARD_REASONS.get(reader.read_uint32(), 'unknown')
        elif kind in ('vector-int64', 'vector-int32'):
            if reader.read_uint32() != _VECTOR:
                return ', '.join(parts)
            count = reader.read_int32()
            if count < 0 or count > 10000:
                return ', '.join(parts)
            read = reader.read_int64 if kind == 'vector-int64' else reader.read_int32
            members = [str(read()) for _ in range(count)]
            if not members:
                continue
            value = ', '.join(members)
        elif kind == 'groupcall':
            fields = _INPUT_GROUP_CALLS.get(reader.read_uint32())
            if fields is None:
                return ', '.join(parts)
            values = []
            for field in fields:
                if field == 'int64':
                    values.append(str(reader.read_int64()))
                elif field == 'int32':
                    values.append(str(reader.read_int32()))
                else:
                    values.append(reader.read_string())
            value = values[0] if values else ''
        else:
            return ''
        if kind == 'string' and not value:
            continue
        parts.append(f'{label} {value}')
    return ', '.join(parts)


def _decode_service(reader, constructor, result):
    """Walk a service message header into result: its from_id and its action.

    result is filled as the walk goes, so a header that cannot be walked to
    its end still gives the fields read before that point. In every header
    the second field is from_id; result['sender'] is set once that slot has
    been passed, to None when the record's flags say it holds no from_id.
    """
    entry = _SERVICE_HEADERS.get(constructor)
    if entry is None:
        return
    reads_flags, steps = entry
    flags = reader.read_uint32() if reads_flags else 0
    for position, (flag, kind) in enumerate(steps):
        value = None
        if flag and not flags & flag:
            pass
        elif kind == 'int32':
            value = reader.read_int32()
        elif kind == 'peer':
            value = reader.read_peer()
        elif kind == 'reply':
            if not _skip_reply_header(reader):
                return
        if position == 1:
            result['sender'] = value
    action = reader.read_uint32()
    name = _ACTION_NAMES.get(action)
    if name is None:
        result['action'] = f'Unrecognised action {action:#010x}'
        return
    try:
        detail = _read_action_payload(reader, action)
    except (struct.error, IndexError, UnicodeDecodeError, ValueError):
        detail = ''
    result['action'] = f'{name} ({detail})' if detail else name


def _attach_path(blob):
    """The local media path the client appends when it stores a message.

    Telegram writes the message record and then the attachment path as a
    trailing TL string, so the path is read from the end of the blob. Walking
    forward to it would require decoding the media objects, which this parser
    does not implement. A candidate is accepted only when its length byte, its
    contents and the TL padding account for the blob exactly to its final byte,
    which is what distinguishes the real trailing field from a coincidental
    run of bytes.
    """
    if not isinstance(blob, bytes) or len(blob) < 6:
        return ''
    end = len(blob)
    while end > 0 and blob[end - 1] == 0:        # TL pads to a 4-byte boundary
        end -= 1
    for length in range(1, 255):
        start = end - length
        marker = start - 1
        if marker < 0:
            break
        if blob[marker] != length:
            continue
        consumed = length + 1
        if marker + consumed + ((4 - consumed % 4) % 4) != len(blob):
            continue
        try:
            text = blob[start:end].decode('utf-8')
        except UnicodeDecodeError:
            continue
        if text.startswith('/'):
            return text
    return ''


def _skip_fields(reader, flags, steps):
    """Step over a flag-driven field list. False when a field is not implemented."""
    for flag, kind in steps:
        if flag and not flags & flag:
            continue
        if kind == 'int32':
            reader.read_int32()
        elif kind == 'int64':
            reader.read_int64()
        elif kind == 'string':
            reader.read_string()
        elif kind == 'peer':
            reader.read_peer()
        elif kind == 'fwd':
            if not _skip_fwd_header(reader):
                return False
        else:                       # media, entities, bytes
            return False
    return True


def _skip_fwd_header(reader):
    """Step over a MessageFwdHeader. False when the constructor is unknown."""
    constructor = reader.read_uint32()
    steps = _FWD_HEADERS.get(constructor)
    if steps is None:
        return False
    return _skip_fields(reader, reader.read_uint32(), steps)


def _skip_reply_header(reader):
    """Step over a MessageReplyHeader. False when it cannot be fully stepped."""
    constructor = reader.read_uint32()
    story = _REPLY_STORY_HEADERS.get(constructor)
    if story is not None:
        for (kind,) in story:
            if kind == 'peer':
                reader.read_peer()
            elif kind == 'int64':
                reader.read_int64()
            else:
                reader.read_int32()
        return True
    steps = _REPLY_HEADERS.get(constructor)
    if steps is None:
        return False
    return _skip_fields(reader, reader.read_uint32(), steps)


def _text_after_date(blob, start, date):
    """Recover the message text of a blob whose header could not be walked.

    A forward or reply header nests further optional objects, so the offset of
    the text cannot be reached by walking the structure without implementing
    those objects as well. The date field sits immediately before the text and
    its value is known independently, from the row's own date column, so the
    text is located by finding that value and reading the string that follows.
    The candidate is accepted only when it is a well-formed TL string that
    decodes as strict UTF-8, and the first match is used; when nothing
    validates the text is reported as unavailable rather than guessed at.
    """
    if not date:
        return None
    needle = struct.pack('<i', date)
    position = blob.find(needle, start)
    while position != -1:
        try:
            reader = _TLReader(blob[position + 4:])
            length = blob[position + 4]
            if length < 254 and position + 5 + length <= len(blob):
                candidate = blob[position + 5:position + 5 + length]
                candidate.decode('utf-8')          # strict: rejects a bad offset
                return reader.read_string()
        except (UnicodeDecodeError, IndexError, struct.error):
            pass
        position = blob.find(needle, position + 1)
    return None


def _decode_old_message(reader, blob, constructor, date):
    """Walk one of the _MSG_OLD_LAYOUTS records, positioned after its constructor."""
    flags = 0
    sender = None
    forwarded = False
    reply = False
    for kind in _MSG_OLD_LAYOUTS[constructor]:
        if kind == 'flags':
            flags = reader.read_uint32()
            continue
        bit = _OLD_FLAG_BITS.get(kind)
        if bit is not None and not flags & bit:
            continue
        kind = kind.rstrip('?')
        if kind == 'from':
            sender = reader.read_int32()
        elif kind == 'peer':
            reader.read_peer()
        elif kind == 'fwd_peer':
            reader.read_peer()
            reader.read_int32()
            forwarded = True
        elif kind == 'fwd_user':
            reader.read_int32()
            reader.read_int32()
            forwarded = True
        else:                       # int32, bool, via, reply: four bytes each
            reader.read_int32()
            reply = reply or kind == 'reply'
    stored_date = reader.read_int32()
    if date and stored_date != date:
        return {'sender': sender, 'forwarded': forwarded, 'reply': reply,
                'text': _text_after_date(blob, 0, date)}
    return {'sender': sender, 'date': stored_date, 'text': reader.read_string(),
            'forwarded': forwarded, 'reply': reply, 'structural': True}


def _decode_message_blob(blob, date=None):
    """Decode a messages_v2 data blob.

    Returns a dict with the sender id and message text when the constructor is
    known. Messages carrying a forward or reply header fall back to
    _text_after_date, because those headers nest further optional objects.
    """
    if not isinstance(blob, bytes) or len(blob) < 8:
        return {}
    reader = _TLReader(blob)
    constructor = reader.read_uint32()
    if constructor in _MSG_SERVICE:
        service = {'service': True}
        try:
            _decode_service(reader, constructor, service)
        except _WALK_ERRORS:
            pass
        return service
    if constructor in _MSG_EMPTY:
        return {'empty': True}
    if constructor in _MSG_OLD_LAYOUTS:
        return _decode_old_message(reader, blob, constructor, date)
    if constructor not in _MSG_ALL:
        return {'unknown': constructor}

    flags = reader.read_uint32()
    flags2 = reader.read_uint32() if constructor in _MSG_WITH_FLAGS2 else 0
    reader.read_int32()                                  # message id
    sender = None
    if flags & (1 << 8):
        if constructor in _MSG_BARE_FROM_AND_REPLY:
            sender = reader.read_int32()                 # from_id, a bare user id
        else:
            sender = reader.read_peer()
    if constructor in _MSG_WITH_FROM_BOOSTS and flags & (1 << 29):
        reader.read_int32()                              # from_boosts_applied
    if constructor in _MSG_WITH_FROM_RANK and flags2 & (1 << 12):
        reader.read_string()                             # from_rank
    reader.read_peer()                                   # peer_id
    if constructor in _MSG_WITH_SAVED_PEER and flags & (1 << 28):
        reader.read_peer()                               # saved_peer_id
    forwarded = bool(flags & (1 << 2))
    if forwarded:
        position = reader.stream.tell()
        if not _skip_fwd_header(reader):
            return {'sender': sender, 'forwarded': True,
                    'text': _text_after_date(blob, position, date)}
    if flags & (1 << 11):
        if constructor in _MSG_VIA_BOT_INT32:
            reader.read_int32()                          # via_bot_id
        else:
            reader.read_int64()                          # via_bot_id
    if constructor in _MSG_WITH_FLAGS2 and flags2 & 1:
        reader.read_int64()                              # via_business_bot_id
    if constructor in _MSG_WITH_GUESTCHAT and flags2 & (1 << 19):
        reader.read_peer()                               # guestchat_via_from
    reply = bool(flags & (1 << 3))
    if reply and constructor in _MSG_BARE_FROM_AND_REPLY:
        reader.read_int32()                              # reply_to_msg_id
    elif reply:
        position = reader.stream.tell()
        if not _skip_reply_header(reader):
            return {'sender': sender, 'reply': True,
                    'text': _text_after_date(blob, position, date)}
    stored_date = reader.read_int32()
    if date and stored_date != date:
        # The walk drifted; the date column is authoritative, so fall back.
        return {'sender': sender, 'forwarded': forwarded, 'reply': reply,
                'text': _text_after_date(blob, 0, date)}
    return {'sender': sender, 'date': stored_date, 'text': reader.read_string(),
            'forwarded': forwarded, 'reply': reply, 'structural': True}


def _decode_message_row(blob, date=None):
    """_decode_message_blob for one table row, which must not cost the table.

    A record that does not match the layout its constructor is read with ends
    the walk with one of _WALK_ERRORS. The row is still reported from the
    table's own columns: the text is looked for after the row's date value,
    and the error is returned so the caller can log it.
    """
    try:
        return _decode_message_blob(blob, date)
    except _WALK_ERRORS as exc:
        return {'undecoded': f'{type(exc).__name__}: {exc}',
                'text': _text_after_date(blob, 0, date)}


def _is_user_dialog(dialog_id):
    """Whether a dialog id names a user, as the client's DialogObject.isUserDialog.

    A group or channel dialog id is negative. A secret chat and a folder are
    positive with bit 62 or bit 61 set, and neither is a user id.
    """
    if not isinstance(dialog_id, int) or dialog_id <= 0:
        return False
    return not dialog_id & 0x6000000000000000


# --- shared helpers ----------------------------------------------------------

def _split_user_name(name):
    """users.name stores 'display name;;;username'."""
    if not name:
        return '', ''
    parts = name.split(';;;')
    display = parts[0].strip() if parts else ''
    username = parts[-1].strip() if len(parts) > 1 else ''
    return display, username


def _name_lookup(db_file):
    """Map peer id to a display name using the users and chats tables."""
    names = {}
    for uid, name in get_sqlite_db_records(db_file, 'SELECT uid, name FROM users') or []:
        display, username = _split_user_name(name)
        names[uid] = f'{display} (@{username})' if username else display
    try:
        for uid, name in get_sqlite_db_records(db_file, 'SELECT uid, name FROM chats') or []:
            if name:
                names[uid] = name
    except Exception:      # pylint: disable=broad-except
        pass               # older databases may not carry a chats table
    return names


# --- artifacts ---------------------------------------------------------------

@artifact_processor
def get_telegramMessages(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Dialog ID',
        'Chat',
        'Direction',
        'Sender ID',
        'Sender',
        'Message',
        'Recorded Media Path',
        ('Media File', 'media'),
        'Read State',
        'Message ID',
    )
    data_list = []
    db_file = get_file_path(context.get_files_found(), 'cache4.db')
    if not db_file:
        return data_headers, data_list, ''

    names = _name_lookup(db_file)

    # Basename index of whatever media directories the extraction carried.
    media_index = {}
    for found in context.get_files_found():
        path = str(found)
        normalized = path.replace('\\', '/')
        if '/org.telegram.messenger' not in normalized:
            continue
        if '/cache/' not in normalized and '/files/Telegram/' not in normalized:
            continue
        if os.path.isfile(path):
            media_index.setdefault(normalized.rsplit('/', 1)[-1], path)

    query = '''SELECT mid, uid, date, out, read_state, data
               FROM messages_v2 ORDER BY date'''
    for mid, uid, date, out, read_state, blob in get_sqlite_db_records(db_file, query) or []:
        decoded = _decode_message_row(blob, date)
        text = decoded.get('text') or ''
        if decoded.get('service'):
            action = decoded.get('action')
            text = f'[{action}]' if action else '[Service message]'
        elif decoded.get('unknown') is not None:
            text = f"[Unrecognised message constructor {decoded['unknown']:#010x}]"
        elif decoded.get('empty'):
            text = '[Empty message record]'
        elif 'sender' in decoded and not decoded.get('structural') and not text:
            # The walk stopped before the text and the search after the date
            # found none. A walked record whose text is empty stays empty.
            if decoded.get('forwarded'):
                text = '[Forwarded message, text not recovered]'
            elif decoded.get('reply'):
                text = '[Reply, text not recovered]'
            else:
                text = '[Message text not recovered]'
        elif decoded.get('undecoded'):
            logfunc(f'Telegram - Messages: message {mid} in dialog {uid} could not be '
                    f"walked ({decoded['undecoded']}); the row is reported from the "
                    'table columns'
                    + (', with the text found after its date' if text else ''))
            if not text:
                text = '[Message not decoded]'
        sender_id = decoded.get('sender')
        if sender_id is None and not out:
            # The record gave no from_id. Where the walk read past the from_id
            # slot the dialog id is used. Where it did not, the dialog id is
            # used only when it names a user: in a group or channel it names
            # the chat.
            if 'sender' in decoded or _is_user_dialog(uid):
                sender_id = uid
        attach = _attach_path(blob)
        media_ref = ''
        if attach:
            local = media_index.get(attach.replace('\\', '/').rsplit('/', 1)[-1])
            if local:
                media_ref = check_in_media(file_path=local)

        data_list.append((
            convert_unix_ts_to_utc(date),
            uid,
            names.get(uid, ''),
            'Outgoing' if out else 'Incoming',
            sender_id if sender_id is not None else '',
            names.get(sender_id, '') if sender_id is not None else '',
            text,
            attach,
            media_ref,
            read_state,
            mid,
        ))
    return data_headers, data_list, db_file


@artifact_processor
def get_telegramContacts(context):
    data_headers = (
        'User ID',
        'First Name',
        'Last Name',
        'Phone Numbers',
        'Imported',
        'Device Contact Key',
    )
    data_list = []
    origins = []
    contributors = []
    for db_file in context.get_files_found():
        relative = context.get_relative_path(db_file)
        parts = relative.replace('\\', '/').split('/')
        if not parts or parts[-1] != 'cache4.db':
            continue
        if len(parts) >= 3 and parts[-2] == 'files':
            package = parts[-3]
        elif len(parts) >= 4 and parts[-2] in ('account1', 'account2', 'account3') and parts[-3] == 'files':
            package = parts[-4]
        else:
            continue
        if not package.startswith('org.telegram.messenger'):
            continue
        phones = {}
        for key, phone, deleted in get_sqlite_db_records(
                db_file, 'SELECT key, phone, deleted FROM user_phones_v7') or []:
            if deleted:
                continue
            phones.setdefault(key, []).append(phone)
        query = 'SELECT key, uid, fname, sname, imported FROM user_contacts_v7 ORDER BY fname'
        contributed = False
        for key, uid, fname, sname, imported in get_sqlite_db_records(db_file, query) or []:
            data_list.append((
                uid,
                fname or '',
                sname or '',
                ', '.join(phones.get(key, [])),
                imported,
                key,
            ))
            origins.append(relative)
            contributed = True
        if contributed:
            contributors.append(db_file)
    if len(set(origins)) > 1:
        data_headers += ('Source File',)
        data_list = [row + (origin,) for row, origin in zip(data_list, origins)]
    return data_headers, data_list, '\n'.join(dict.fromkeys(contributors))


@artifact_processor
def get_telegramUsers(context):
    data_headers = (
        ('Last Seen', 'datetime'),
        'User ID',
        'Display Name',
        'Username',
        'Status Value',
    )
    data_list = []
    db_file = get_file_path(context.get_files_found(), 'cache4.db')
    if not db_file:
        return data_headers, data_list, ''

    for uid, name, status in get_sqlite_db_records(
            db_file, 'SELECT uid, name, status FROM users') or []:
        display, username = _split_user_name(name)
        last_seen = convert_unix_ts_to_utc(status) if status and status > 0 else ''
        data_list.append((last_seen, uid, display, username, status))
    return data_headers, data_list, db_file


@artifact_processor
def get_telegramChats(context):
    data_headers = (
        ('Last Activity', 'datetime'),
        'Dialog ID',
        'Chat',
        'Messages Stored',
        'Unread Count',
        'Pinned',
        'Folder',
    )
    data_list = []
    db_file = get_file_path(context.get_files_found(), 'cache4.db')
    if not db_file:
        return data_headers, data_list, ''

    names = _name_lookup(db_file)
    counts = {}
    for uid, total in get_sqlite_db_records(
            db_file, 'SELECT uid, count(*) FROM messages_v2 GROUP BY uid') or []:
        counts[uid] = total

    query = '''SELECT did, date, unread_count, pinned, folder_id
               FROM dialogs ORDER BY date DESC'''
    for did, date, unread, pinned, folder_id in get_sqlite_db_records(db_file, query) or []:
        data_list.append((
            convert_unix_ts_to_utc(date),
            did,
            names.get(did, ''),
            counts.get(did, 0),
            unread,
            'Yes' if pinned else '',
            'Archived' if folder_id == 1 else 'Main',
        ))
    return data_headers, data_list, db_file


# TL_user constructors whose prefix is flags, flags2, id, then the optional
# access hash, names, username and phone. TL_user_layer184 and _layer227.
_USER_RECORDS = {0x215C4438, 0x31774388}

_PASSCODE_TYPES = {0: 'PIN', 1: 'Password'}


def _decode_account_user(raw):
    """Decode the base64 TL user record stored under the 'user' key."""
    try:
        blob = base64.b64decode(raw)
    except (ValueError, TypeError):
        return {}
    if len(blob) < 16:
        return {}
    reader = _TLReader(blob)
    if reader.read_uint32() not in _USER_RECORDS:
        return {}
    try:
        flags = reader.read_uint32()
        reader.read_uint32()                       # flags2
        user = {'id': reader.read_int64()}
        if flags & 1:
            reader.read_int64()                    # access_hash
        for bit, name in ((2, 'first_name'), (4, 'last_name'),
                          (8, 'username'), (16, 'phone')):
            if flags & bit:
                user[name] = reader.read_string()
        return user
    except (struct.error, IndexError, UnicodeDecodeError):
        return {}


@artifact_processor
def get_telegramAccounts(context):
    data_headers = (
        ("lastContactsSyncTime (stored value)", 'datetime'),
        'Account Slot',
        'User ID',
        'First Name',
        'Last Name',
        'Username',
        'Phone',
        'Passcode',
        'Auto-Lock',
        'Unlock With Fingerprint',
        "last_call_phone_number (as stored)",
    )
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        path = str(file_found)
        name = os.path.basename(path.replace('\\', '/'))
        if not name.startswith('userconf') or not name.endswith('.xml'):
            continue
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as err:
            logfunc(f'Telegram accounts: could not parse {path}: {err}')
            continue
        values = {element.get('name'): (element.get('value') or element.text or '')
                  for element in root}
        user = _decode_account_user(values.get('user', ''))
        digits = ''.join(ch for ch in name if ch.isdigit())
        slot = digits if digits else '0'

        if not user and not values.get('passcodeHash1') \
                and not values.get('last_call_phone_number'):
            continue                                # an unused account slot

        passcode_hash = values.get('passcodeHash1', '')
        if passcode_hash:
            kind = _PASSCODE_TYPES.get(_as_int(values.get('passcodeType')), 'Unknown')
            passcode = f'Set ({kind})'
        else:
            passcode = 'Not set'
        auto_lock = _as_int(values.get('autoLockIn'))
        sync = _as_int(values.get('lastContactsSyncTime'))

        data_list.append((
            convert_unix_ts_to_utc(sync) if sync else '',
            slot,
            user.get('id', ''),
            user.get('first_name', ''),
            user.get('last_name', ''),
            user.get('username', ''),
            user.get('phone', ''),
            passcode,
            f'{auto_lock} seconds' if auto_lock else '',
            'Yes' if values.get('useFingerprint') == 'true' else '',
            values.get('last_call_phone_number', ''),
        ))
        sources.append(path)

    return data_headers, data_list, '\n'.join(sources) if sources else ''


def _as_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


# TL user full records whose prefix is flags, then optionally flags2, then the
# id and the about string. Layouts from the generated TlGen_UserFull.kt.
_USER_FULL_FLAGS2 = {
    0x06CBE645, 0x22FF3E85, 0xCC997720, 0x1F58E369, 0x979D2376, 0x4D975BBC,
    0xD2234EA0, 0x99E78045, 0x29DE80BE, 0x7E63CE1F, 0x3FD81E28, 0xC577B5AD,
    0xA02BC13E,
}
_USER_FULL_NO_FLAGS2 = {
    0xCF366521, 0x8C72EA81, 0xC4B1FC3F, 0xF8D32AED, 0x93EADB53, 0x4FE1CC86,
    0xB9B12C6C,
}
_USER_FULL = _USER_FULL_FLAGS2 | _USER_FULL_NO_FLAGS2


def _decode_user_full(blob):
    """Read the about text and blocked flag from a TL user full record."""
    if not isinstance(blob, bytes) or len(blob) < 12:
        return {}
    reader = _TLReader(blob)
    constructor = reader.read_uint32()
    if constructor not in _USER_FULL:
        return {'unknown': constructor}
    try:
        flags = reader.read_uint32()
        if constructor in _USER_FULL_FLAGS2:
            reader.read_uint32()
        reader.read_int64()                              # id
        about = reader.read_string() if flags & 2 else ''
        return {'about': about, 'blocked': bool(flags & 1)}
    except (struct.error, IndexError, UnicodeDecodeError):
        return {}


@artifact_processor
def get_telegramPeerDetails(context):
    data_headers = (
        'User ID',
        'Name',
        'Username',
        'Bio',
        'Blocked',
        "pinned (existing truthiness rendering)",
    )
    data_list = []
    db_file = get_file_path(context.get_files_found(), 'cache4.db')
    if not db_file:
        return data_headers, data_list, ''

    names = {}
    for uid, name in get_sqlite_db_records(db_file, 'SELECT uid, name FROM users') or []:
        names[uid] = _split_user_name(name)

    query = 'SELECT uid, info, pinned FROM user_settings'
    for uid, blob, pinned in get_sqlite_db_records(db_file, query) or []:
        decoded = _decode_user_full(blob)
        if decoded.get('unknown') is not None:
            bio = f"[Unrecognised record {decoded['unknown']:#010x}]"
            blocked = ''
        else:
            bio = decoded.get('about', '')
            blocked = 'Yes' if decoded.get('blocked') else 'No' if decoded else ''
        display, username = names.get(uid, ('', ''))
        data_list.append((uid, display, username, bio, blocked, 'Yes' if pinned else ''))
    return data_headers, data_list, db_file


# TL chat/channel full records, grouped by the shape of the readable prefix.
# A: flags, flags2, id, about, then the counts.
# B: flags, id, about, then the counts.
# C: flags, id, about only, which is the basic group record.
_CHAT_FULL_A = {
    0x0F2BCB6F,
    0x44C054A7,
    0x52D6806B,
    0x723027BD,
    0x9FF3B858,
    0xA04E8D3A,
    0xBBAB348D,
    0xE07429DE,
    0xE4E0B29D,
    0xEA68A619,
    0xF2355507,
}
_CHAT_FULL_B = {
    0x03648977,
    0x10916653,
    0x17F45FCF,
    0x1C87A71A,
    0x2548C037,
    0x2D895C74,
    0x2F532F3C,
    0x548C3F93,
    0x56662E2E,
    0x59CFF963,
    0x76AF5481,
    0x7A7DE4F7,
    0x95CB5F57,
    0x97BEE562,
    0x9882E516,
    0x9E341DDF,
    0xC3D5512F,
    0xE13C3D20,
    0xE9B27A17,
    0xEF3A6ACD,
    0xF0E6672A,
    0xFAB31AA3,
}
_CHAT_FULL_C = {
    0x0DC8C181,
    0x1B7C9DB3,
    0x22A235DA,
    0x2633421B,
    0x46A6FFB4,
    0x49A0A5D9,
    0x4DBDC099,
    0x8A1E2983,
    0xC9D31138,
    0xCBB7A507,
    0xD18EE226,
    0xF06C4018,
    0xF3474AF6,
}
_CHAT_FULL = _CHAT_FULL_A | _CHAT_FULL_B | _CHAT_FULL_C


def _decode_chat_full(blob):
    """Read the description and member counts from a chat or channel record."""
    if not isinstance(blob, bytes) or len(blob) < 12:
        return {}
    reader = _TLReader(blob)
    constructor = reader.read_uint32()
    if constructor not in _CHAT_FULL:
        return {'unknown': constructor}
    try:
        flags = reader.read_uint32()
        if constructor in _CHAT_FULL_A:
            reader.read_uint32()                         # flags2
        reader.read_int64()                              # id
        record = {'about': reader.read_string()}
        if constructor in _CHAT_FULL_C:
            return record                                # basic group: no counts
        if flags & 1:
            record['participants'] = reader.read_int32()
        if flags & 2:
            record['admins'] = reader.read_int32()
        if flags & 4:
            record['kicked'] = reader.read_int32()
            record['banned'] = reader.read_int32()
        if flags & 8192:
            record['online'] = reader.read_int32()
        return record
    except (struct.error, IndexError, UnicodeDecodeError):
        return {}


@artifact_processor
def get_telegramChatDetails(context):
    data_headers = (
        'Chat ID',
        'Chat',
        'Description',
        'Participants',
        'Administrators',
        'Removed',
        'Banned',
        'Online',
    )
    data_list = []
    db_file = get_file_path(context.get_files_found(), 'cache4.db')
    if not db_file:
        return data_headers, data_list, ''

    names = {}
    try:
        for uid, name in get_sqlite_db_records(
                db_file, 'SELECT uid, name FROM chats') or []:
            names[uid] = name or ''
    except Exception:      # pylint: disable=broad-except
        pass

    query = 'SELECT uid, info FROM chat_settings_v2'
    for uid, blob in get_sqlite_db_records(db_file, query) or []:
        record = _decode_chat_full(blob)
        if record.get('unknown') is not None:
            description = f"[Unrecognised record {record['unknown']:#010x}]"
        else:
            description = record.get('about', '')
        data_list.append((
            uid,
            names.get(uid, ''),
            description,
            record.get('participants', ''),
            record.get('admins', ''),
            record.get('kicked', ''),
            record.get('banned', ''),
            record.get('online', ''),
        ))
    return data_headers, data_list, db_file


# SaveToGallerySettingsHelper.java: one settings group per category of chat.
_GALLERY_PREFIXES = (('user', 'Private chats'), ('groups', 'Groups'),
                     ('channels', 'Channels'))
_GALLERY_DEFAULT = 'Not set (app default, off)'


@artifact_processor
def get_telegramSaveToGallery(context):
    data_headers = (
        'Chat Category',
        'Save Photos',
        'Save Videos',
        'Video Size Limit',
    )
    data_list = []
    xml_file = get_file_path(context.get_files_found(), 'mainconfig.xml')
    if not xml_file:
        return data_headers, data_list, ''
    try:
        root = ET.parse(xml_file).getroot()
    except ET.ParseError as err:
        logfunc(f'Telegram save to gallery: could not parse {xml_file}: {err}')
        return data_headers, data_list, xml_file
    values = {element.get('name'): (element.get('value') or element.text or '')
              for element in root}

    def flag(key):
        if key not in values:
            return _GALLERY_DEFAULT
        return 'Yes' if values[key] == 'true' else 'No'

    for prefix, label in _GALLERY_PREFIXES:
        limit_key = f'{prefix}_save_gallery_limitVideo'
        limit = values.get(limit_key, '')
        data_list.append((
            label,
            flag(f'{prefix}_save_gallery_photo'),
            flag(f'{prefix}_save_gallery_video'),
            limit if limit else _GALLERY_DEFAULT,
        ))
    if 'save_gallery' in values:
        data_list.append((
            'All chats (legacy setting)',
            'Yes' if values['save_gallery'] == 'true' else 'No', '', '',
        ))
    return data_headers, data_list, xml_file


# Channel participant constructors seen in the corpus. Only the creator form is
# present in the client's generated model; anything else is reported by id.
_CHANNEL_PARTICIPANTS = {0x2FE601D3: 'Creator'}


@artifact_processor
def get_telegramChannelMembers(context):
    data_headers = (
        ('Date', 'datetime'),
        'Chat ID',
        'Chat',
        'User ID',
        'User',
        'Role',
    )
    data_list = []
    db_file = get_file_path(context.get_files_found(), 'cache4.db')
    if not db_file:
        return data_headers, data_list, ''

    names = _name_lookup(db_file)
    query = 'SELECT did, uid, date, data FROM channel_users_v2 ORDER BY did, date'
    for did, uid, date, blob in get_sqlite_db_records(db_file, query) or []:
        role = ''
        if isinstance(blob, bytes) and len(blob) >= 4:
            constructor = struct.unpack('<I', blob[:4])[0]
            role = _CHANNEL_PARTICIPANTS.get(constructor, f'{constructor:#010x}')
        data_list.append((
            convert_unix_ts_to_utc(date) if date else '',
            did,
            names.get(did, '') or names.get(abs(did), ''),
            uid,
            names.get(uid, ''),
            role,
        ))
    return data_headers, data_list, db_file


@artifact_processor
def get_telegramChatHints(context):
    data_headers = (
        ('Date', 'datetime'),
        'Chat ID',
        'Chat',
        'Rating (as stored)',
        'Type (as stored)',
    )
    data_list = []
    db_file = get_file_path(context.get_files_found(), 'cache4.db')
    if not db_file:
        return data_headers, data_list, ''

    names = _name_lookup(db_file)
    query = 'SELECT did, type, rating, date FROM chat_hints ORDER BY rating DESC'
    for did, kind, rating, date in get_sqlite_db_records(db_file, query) or []:
        # chat_hints has been seen holding a negative date, which is not a Unix
        # timestamp and made the conversion raise, losing every row of the
        # artifact. What such a value means is not established, so it is left
        # blank rather than guessed at, and the other columns still report.
        try:
            timestamp = convert_unix_ts_to_utc(date) if date and date > 0 else ''
        except (ValueError, OSError, OverflowError):
            timestamp = ''
        data_list.append((
            timestamp,
            did,
            names.get(did, '') or names.get(abs(did), ''),
            rating,
            kind,
        ))
    return data_headers, data_list, db_file


# Telegram writes one WebRTC log per call under cache/voip_logs, named for the
# call id. Entries look like: 2024-1-31 12:36:34:849 <file>: (line N): <text>
_VOIP_ENTRY = re.compile(r'^(\d{4})-(\d+)-(\d+) (\d+):(\d+):(\d+):(\d+)')


def _voip_log_span(path):
    """First and last entry times in a voip log, as recorded (device local)."""
    first = last = None
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as handle:
            for line in handle:
                match = _VOIP_ENTRY.match(line)
                if not match:
                    continue
                stamp = datetime.datetime(*[int(match.group(i)) for i in range(1, 7)])
                if first is None:
                    first = stamp
                last = stamp
    except OSError:
        return None, None
    return first, last


@artifact_processor
def get_telegramVoipLogs(context):
    data_headers = (
        ('Log Last Modified (UTC)', 'datetime'),
        'Call ID',
        'Logged Span (seconds)',
        'First Entry (device local time)',
        'Last Entry (device local time)',
        'Log Size (bytes)',
        'Stats Log Present',
        'Log File',
    )
    data_list = []
    sources = []
    seeker = context.get_seeker()

    logs, stats = {}, set()
    for found in context.get_files_found():
        path = str(found)
        name = os.path.basename(path.replace('\\', '/'))
        if '/voip_logs/' not in path.replace('\\', '/') or not os.path.isfile(path):
            continue
        if name.endswith('_stats.log'):
            stats.add(name[:-len('_stats.log')])
        elif name.endswith('.log'):
            logs[name[:-len('.log')]] = path

    for call_id, path in sorted(logs.items()):
        first, last = _voip_log_span(path)
        span = int((last - first).total_seconds()) if first and last else ''
        # The time the extraction records for the file, not the staged copy's own
        # time: for a zip member the seeker sets the copy's time from the member's
        # zone-less date and time read in the examiner machine's zone.
        info = seeker.file_infos.get(path) if seeker else None
        modified = ''
        if info and info.modification_date:
            modified = convert_unix_ts_to_utc(int(info.modification_date))
        try:
            size = os.path.getsize(path)
        except OSError:
            size = ''
        data_list.append((
            modified,
            call_id,
            span,
            first.strftime('%Y-%m-%d %H:%M:%S') if first else '',
            last.strftime('%Y-%m-%d %H:%M:%S') if last else '',
            size,
            'Yes' if call_id in stats else '',
            context.get_relative_path(path),
        ))
        sources.append(path)

    return data_headers, data_list, '\n'.join(sources) if sources else ''


# DownloadController.java: mask index is the chat category, mask bits the media type.
_MASK_CATEGORIES = ('Contacts', 'Other private chats', 'Groups', 'Channels')
_MASK_TYPES = ((1, 'Photos'), (2, 'Audio'), (4, 'Videos'), (8, 'Documents'))
_PRESET_KEYS = (
    ('mobilePreset', 'Mobile data'),
    ('wifiPreset', 'Wi-Fi'),
    ('roamingPreset', 'Roaming'),
)


def _describe_mask(mask):
    enabled = [label for bit, label in _MASK_TYPES if mask & bit]
    return ', '.join(enabled) if enabled else 'None'


@artifact_processor
def get_telegramAutoDownload(context):
    data_headers = (
        'Network',
        'Auto-Download Enabled',
        'Chat Category',
        'Media Auto-Downloaded',
        'Photo Size Limit',
        'Video Size Limit',
        'Document Size Limit',
    )
    data_list = []
    xml_file = get_file_path(context.get_files_found(), 'mainconfig.xml')
    if not xml_file:
        return data_headers, data_list, ''

    try:
        root = ET.parse(xml_file).getroot()
    except ET.ParseError as err:
        logfunc(f'Telegram auto-download: could not parse {xml_file}: {err}')
        return data_headers, data_list, xml_file

    values = {element.get('name'): (element.get('value') or element.text or '')
              for element in root}

    for key, network in _PRESET_KEYS:
        raw = values.get(key, '')
        parts = raw.split('_')
        if len(parts) < 11:
            continue
        try:
            masks = [int(parts[index]) for index in range(4)]
            sizes = [int(parts[index]) for index in range(4, 8)]
            enabled = int(parts[10]) == 1
        except ValueError:
            continue
        for index, category in enumerate(_MASK_CATEGORIES):
            data_list.append((
                network,
                'Yes' if enabled else 'No',
                category,
                _describe_mask(masks[index]),
                sizes[0],
                sizes[1],
                sizes[2],
            ))
    return data_headers, data_list, xml_file

__artifacts_v2__ = {
    "get_wire_profile": {
        "name": "Wire User Profile",
        "description": "Parses details about the user profile for Wire Messenger",
        "author": "@cf-eglendye",
        "creation_date": "2024-04-24",
        "last_update_date": "2026-08-15",
        "requirements": "None",
        "category": "Messaging",
        "notes": (
                 'The module records a test on Android 13 with Wire 3.81.35; the image used is not recorded. Rows were produced '
                 'on pixel3_a11 and pixel3_a12 (see sample_data). Only the first client in the stored clients list (clients[0]) '
                 'is reported; the order of that list is not established, and any further clients in it are not listed. Applies '
                 'to the legacy app generation that keeps a plain-SQLite database named by the account id next to '
                 'com.wire.preferences.xml. Newer app versions store user data in databases/user-db-<account id>-wirecom, whose '
                 "content is not plain SQLite (the app's own log records a database keying operation, and the app's published "
                 'core wireapp/kalium carries '
                 'data/persistence/src/androidMain/kotlin/com/wire/kalium/persistence/db/support/SqlCipherKey.kt at commit '
                 'e9ac68451ad88f9e67dd41216df926ba47b3a581), and their shared preferences are encrypted, so this artifact '
                 'reports nothing for those versions; when the extraction carries the com.wire preference keysets in '
                 'Secrets/secrets.json and the derived key authenticates, the Wire (Secure Store) artifacts read that database.'
        ),
        "paths": ('*/com.wire/**',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "pixel3_a11": "Android 11 | com.wire | 1 row",
            "pixel3_a12": "Android 12 | com.wire | 1 row",
            "pixel7a_a14": "Android 14 | com.wire vc 9369190 | 0 rows, user database not plain SQLite",
            "hc_pixel8pro_a16": "Android 16 | com.wire vc 100206242 | 0 rows, user database not plain SQLite",
            "hc_pixel8pro_a17": "Android 17 | com.wire | 0 rows, user database not plain SQLite",
        },
    },
    "get_wire_contacts": {
        "name": "Wire Contacts",
        "description": "Parses user contacts for Wire Messenger",
        "author": "@cf-eglendye",
        "creation_date": "2024-04-24",
        "last_update_date": "2026-08-15",
        "requirements": "None",
        "category": "Messaging",
        "notes": (
                 'The module records a test on Android 13 with Wire 3.81.35; the image used is not recorded. Rows were produced '
                 'on pixel3_a11 and pixel3_a12 (see sample_data). Applies to the legacy app generation that keeps a plain-SQLite '
                 'database named by the account id next to com.wire.preferences.xml. Newer app versions store user data in '
                 "databases/user-db-<account id>-wirecom, whose content is not plain SQLite (the app's own log records a "
                 "database keying operation, and the app's published core wireapp/kalium carries "
                 'data/persistence/src/androidMain/kotlin/com/wire/kalium/persistence/db/support/SqlCipherKey.kt at commit '
                 'e9ac68451ad88f9e67dd41216df926ba47b3a581), and their shared preferences are encrypted, so this artifact '
                 'reports nothing for those versions; when the extraction carries the com.wire preference keysets in '
                 'Secrets/secrets.json and the derived key authenticates, the Wire (Secure Store) artifacts read that database.'
        ),
        "paths": ('*/com.wire/**',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "pixel3_a11": "Android 11 | com.wire | 2 rows",
            "pixel3_a12": "Android 12 | com.wire | 2 rows",
            "pixel7a_a14": "Android 14 | com.wire vc 9369190 | 0 rows, user database not plain SQLite",
            "hc_pixel8pro_a16": "Android 16 | com.wire vc 100206242 | 0 rows, user database not plain SQLite",
            "hc_pixel8pro_a17": "Android 17 | com.wire | 0 rows, user database not plain SQLite",
        },
    },
    "get_wire_messages": {
        "name": "Wire Messages",
        "description": "Parses messages and call history for Wire Messenger",
        "author": "@cf-eglendye, @AlexisBrignoni, Codex",
        "creation_date": "2024-04-24",
        "last_update_date": "2026-10-04",
        "requirements": "None",
        "category": "Messaging",
        "notes": (
                 'The module records a test on Android 13 with Wire 3.81.35; the image used is not recorded. Rows were produced '
                 'on pixel3_a11 and pixel3_a12 (see sample_data). Rows taken from the MsgDeletion table are given the Message '
                 "Type Deleted by this parser and carry the table's timestamp column in Date / Time Deleted. These rows have no "
                 'sent time. On pixel3_a12 the table held 2 rows and neither message id was present in Messages; on pixel3_a11 '
                 "it held none. In a public copy of the legacy Wire sync engine source dated 2018 (not the vendor's own "
                 'repository; the app versions on the tested images are not recorded) the insert into MsgDeletion found there '
                 'stores the device clock time at which the app removed the message, and it is called for a deletion made by the '
                 'user, a deletion received from another device and an expired timed message '
                 '(https://github.com/wireappru/wire-android-sync-engine/blob/d42492b5713255f618165ad24da0bde4704b84f7/zmessaging/src/main/scala/com/waz/service/messages/MessagesContentUpdater.scala#L55-L60, '
                 'https://github.com/wireappru/wire-android-sync-engine/blob/d42492b5713255f618165ad24da0bde4704b84f7/zmessaging/src/main/scala/com/waz/service/GenericMessageService.scala#L59-L73, '
                 'https://github.com/wireappru/wire-android-sync-engine/blob/d42492b5713255f618165ad24da0bde4704b84f7/zmessaging/src/main/scala/com/waz/service/messages/EphemeralMessagesService.scala#L86-L88); '
                 'the same copy removes MsgDeletion rows older than 14 days at app start '
                 '(https://github.com/wireappru/wire-android-sync-engine/blob/d42492b5713255f618165ad24da0bde4704b84f7/zmessaging/src/main/scala/com/waz/content/MsgDeletionStorage.scala#L33-L50). '
                 'Whether the app versions on the tested images behave the same way is not established. Reaction reads Liked '
                 'where Likings.action is 1 and Unliked where it is 0, the two values that copy of the source defines as Like '
                 'and Unlike '
                 '(https://github.com/wireappru/wire-android-sync-engine/blob/d42492b5713255f618165ad24da0bde4704b84f7/zmessaging/src/main/scala/com/waz/model/Liking.scala#L42-L47); '
                 'any other value is shown as stored. Likings has one row per message and reacting user (its primary key is '
                 'message_id, user_id), so a message with rows from more than one user appears once per user, each row naming '
                 'that user in Reacted By. Date / Time Reacted is blank where Likings.timestamp is 0: the column defaults to 0 '
                 'and that copy of the source stores the epoch for a reaction made on the device until the server time replaces '
                 'it '
                 '(https://github.com/wireappru/wire-android-sync-engine/blob/d42492b5713255f618165ad24da0bde4704b84f7/zmessaging/src/main/scala/com/waz/service/messages/ReactionsService.scala#L40-L52). '
                 'Likings held no rows on pixel3_a11 or pixel3_a12, so the Reaction columns were exercised only on a constructed '
                 'database. The call duration column is rendered by dividing the stored duration by 1000, which assumes the '
                 'value is milliseconds; that unit has not been independently verified. Applies to the legacy app generation '
                 'that keeps a plain-SQLite database named by the account id next to com.wire.preferences.xml. Newer app '
                 'versions store user data in databases/user-db-<account id>-wirecom, whose content is not plain SQLite (the '
                 "app's own log records a database keying operation, and the app's published core wireapp/kalium carries "
                 'data/persistence/src/androidMain/kotlin/com/wire/kalium/persistence/db/support/SqlCipherKey.kt at commit '
                 'e9ac68451ad88f9e67dd41216df926ba47b3a581), and their shared preferences are encrypted, so this artifact '
                 'reports nothing for those versions; when the extraction carries the com.wire preference keysets in '
                 'Secrets/secrets.json and the derived key authenticates, the Wire (Secure Store) artifacts read that database.'
        ),
        "paths": ('*/com.wire/**',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "pixel3_a11": "Android 11 | com.wire | 15 rows",
            "pixel3_a12": "Android 12 | com.wire | 30 rows",
            "pixel7a_a14": "Android 14 | com.wire vc 9369190 | 0 rows, user database not plain SQLite",
            "hc_pixel8pro_a16": "Android 16 | com.wire vc 100206242 | 0 rows, user database not plain SQLite",
            "hc_pixel8pro_a17": "Android 17 | com.wire | 0 rows, user database not plain SQLite",
        },
    },
    "get_wire_cached_files": {
        "name": "Wire Cached Files",
        "description": "Reports selected Wire cached files and existing media references. PNG/JPEG prefixes "
                       "retain their existing export suffixes; the ftyp-only branch uses a generic bin suffix "
                       "without inferring a specific container or codec.",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-08-15",
        "last_update_date": "2026-10-07",
        "requirements": "None",
        "category": "Messaging",
        "notes": (
                 'One row per file under files/wire.com/<account id>/ and cache/wire.com/<account id>/ inside the app sandbox. '
                 'On tested images these directories hold PNG and JPEG content, some of it in files without an extension; the '
                 'type is read from the first bytes of the file: a PNG signature, a JPEG signature, or ftyp at bytes 4 to 8, '
                 'whose surviving branch requests the generic bin export suffix. That marker alone does not establish a specific '
                 'container or codec. These files sit outside the databases newer app versions encrypt, so they remain readable '
                 'whether or not the message store is, and the Wire (Secure Store) artifacts read that store when the extraction '
                 'carries the com.wire preference keysets in Secrets/secrets.json. What each file was used for by the app is not '
                 'asserted. Only the ftyp branch export-suffix request changed; PNG/JPEG prefix precedence, all four native '
                 'fields, selected row occurrences/order, existing canonical alias selection and source aggregation are '
                 'unchanged. Native File contains a media reference ID, not a type label. Shared media MIME sniffing is '
                 'independent of this suffix and is not changed or certified here. Existing media reference or item reuse can '
                 'retain an earlier registered extension; this change does not rename existing media items or force a new '
                 'registration. Newly registered surviving ftyp candidates request bin even if independent MIME sniffing '
                 'recognizes a format. Prefix tests do not verify complete media integrity, and no file bytes are transcoded. '
                 'Historical app/database encryption/private sample counts and account-path meanings are not newly verified. '
                 'Original contribution credited to @AlexisBrignoni and Claude.'
        ),
        "paths": ('*/com.wire/files/wire.com/*/*',
                  '*/com.wire/cache/wire.com/*/*'),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "pixel3_a11": "Android 11 | com.wire | 0 rows, no wire.com file directories",
            "pixel3_a12": "Android 12 | com.wire | 0 rows, no wire.com file directories",
            "pixel7a_a14": "Android 14 | com.wire vc 9369190 | 14 rows",
            "hc_pixel8pro_a16": "Android 16 | com.wire vc 100206242 | 11 rows",
            "hc_pixel8pro_a17": "Android 17 | com.wire | 20 rows",
        },
    },
    "get_wire_proteus_sessions": {
        "name": "Wire Proteus Sessions",
        "description": "Proteus end-to-end encryption sessions stored by the Wire app, with the "
                       "other party's user id, domain and client id taken from the session file "
                       "name",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-15",
        "last_update_date": "2026-08-16",
        "requirements": "None",
        "category": "Messaging",
        "notes": (
                 'One row per file under app_accounts/<domain>/<account id>/proteus/sessions/ in current app versions, or '
                 'files/otr/<account id>/sessions/ in the legacy generation. The file name is the Proteus session id, which the '
                 "app's published core builds as <user id>_<client id> with the user id rendered as <value>@<domain> "
                 '(CryptoSessionId in core/cryptography/src/commonMain/kotlin/com/wire/kalium/cryptography/ProteusClient.kt and '
                 'CryptoQualifiedID in the IDs.kt beside it, wireapp/kalium commit e9ac68451ad88f9e67dd41216df926ba47b3a581). '
                 'Session names in the legacy store carried no domain on the tested images (pixel3_a11, pixel3_a12), which is '
                 'reported empty rather than assumed. These files sit outside the databases current app versions encrypt, so '
                 'they remain readable whether or not the message store is, and the Wire (Secure Store) artifacts read that '
                 'store when the extraction carries the com.wire preference keysets in Secrets/secrets.json. A session file '
                 'records that a cryptographic session exists with that client. It does not establish that a message was sent, '
                 'received or read, it carries no message content, and the session contents are not decoded here. An extraction '
                 'can hold the same store under more than one path (/data/data, /data/user/0, data_mirror); each session file is '
                 'reported once, from the /data/data copy where present.'
        ),
        "paths": ('*/com.wire/app_accounts/*/*/proteus/sessions/*',
                  '*/com.wire/files/otr/*/sessions/*'),
        "output_types": "standard",
        "artifact_icon": "key",
        "sample_data": {
            "pixel3_a11": "Android 11 | com.wire | 7 rows, legacy otr store, no domain in the "
                          "stored names",
            "pixel3_a12": "Android 12 | com.wire | 9 rows, legacy otr store, no domain in the "
                          "stored names",
            "pixel7a_a14": "Android 14 | com.wire vc 9369190 | 5 rows, qualified ids with domain",
            "hc_pixel8pro_a16": "Android 16 | com.wire vc 100206242 | 0 rows, proteus store "
                                "present with no session files",
            "hc_pixel8pro_a17": "Android 17 | com.wire | 0 rows, proteus store present with no "
                                "session files",
        },
    },
    "get_wire_secure_messages": {
        "name": "Wire Messages (Secure Store)",
        "description": "Message rows, including system events, from the SQLCipher user database of newer Wire app "
                       "generations, read when the extraction carries the com.wire preference keysets in Secrets/secrets.json",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "None",
        "category": "Messaging",
        "notes": (
                 "These rows come from a database that newer Wire app generations encrypt with SQLCipher. The extraction's "
                 'Secrets/secrets.json com.wire entry holds the two Tink keysets that decrypt shared_prefs/app-preference.xml. '
                 'The database secret is read from that file. That file is an androidx EncryptedSharedPreferences store: the '
                 'preference name is AES-SIV with the file name app-preference as associated data, and the value is AES-256-GCM '
                 'with the encrypted name as associated data (androidx security-crypto EncryptedSharedPreferences.java at commit '
                 '83d0df9197c5320ac2e10d92afaf9ee839cec144). The decrypted preferences hold the database secret under '
                 'global_db_passphrase_alias[_v2] for global-db and user_db_secret_alias[_v2]_<account> for the user database. A '
                 '_v2 secret is 32 bytes used directly as the SQLCipher raw key (wireapp/kalium SecurityHelper.kt at commit '
                 'e9ac68451ad88f9e67dd41216df926ba47b3a581). A secret without _v2 is passed without the raw-key form in that '
                 'file; this parser derives its key with PBKDF2-HMAC-SHA512, 256,000 iterations, over the database salt, the '
                 'SQLCipher 4 defaults. A key that authenticates no page is refused; if only some pages authenticate, the copy '
                 'is used and the log says how many failed. This parser decrypts the preference names and only the two database '
                 'secret values; it does not decrypt or emit the values of the login tokens, the notification token, or the MLS '
                 "and Proteus secrets stored in the same preferences, and it contacts no server. The write-ahead log's committed "
                 'frames are applied when present; on samsung_a166u_a16_known_20261116 the log added 1 message, 1 text row and 2 '
                 'receipts. The decrypted copy is written under the report folder and read from there; the evidence file is only '
                 'read. On samsung_a166u_a16_known_20261116, hc_pixel8pro_a16 and hc_pixel8pro_a17 every page of both databases '
                 'authenticated under these settings. Android User is the user whose storage path holds the database, and it '
                 'held one value, 0, on every row of the single-user images in sample_data. One row per Message row. Message '
                 'Timestamp is Message.creation_date read as Unix milliseconds. Direction is derived in this parser: Outgoing '
                 'when the sender equals the SelfUser row id, otherwise Incoming. The Message table on the tested images has no '
                 'direction column. Sender Name is the User.name joined on sender_user_id, and Outgoing rows show This Device, '
                 "the account's own user; a message the same account sent from another device would carry the same label, and "
                 'Sender Client ID is on the row. System event rows (for example a protocol change or a member change) are '
                 'included and carry the self user as sender, so they read Outgoing; that does not mean a message was sent. '
                 'Message Type (content_type), Status and Visibility are shown as stored. Message is '
                 'MessageTextContent.text_body joined on (message_id, conversation_id). Latitude and Longitude come from '
                 'MessageConversationLocationContent for location messages and are blank otherwise. Media is the on-disk file '
                 'that MessageAssetContent.asset_id resolves to through Asset.data_path; the file is matched by its path below '
                 'com.wire/ and its type is read from the first bytes, not the name. Only PNG, JPEG and GIF signatures and an '
                 'ftyp marker are recognised; an ftyp file is exported with a bin suffix and no container is asserted, and any '
                 'other file leaves Media blank. On hc_pixel8pro_a16 and hc_pixel8pro_a17 the one DELETED row carries no text; '
                 'this parser does not report who deleted it. On hc_pixel8pro_a17 two video messages have no Asset row, so their '
                 'Media is blank. Latitude, Longitude, Location Name and Media are blank on rows that have no such value. The '
                 "Samsung image's Wire messages are not in that image's activity log, so they are not known-data verified; the "
                 "hc_pixel8pro_a16 message times fall within the range of that image's activity-log Wire entries, which is not "
                 'the same as a per-message check. Reactions, receipts, calls and per-conversation fields are their own '
                 'artifacts. Visibility held VISIBLE on all 34 rows of samsung_a166u_a16_known_20261116; hc_pixel8pro_a16 and '
                 'hc_pixel8pro_a17 each also hold a DELETED row. Latitude, Longitude, Location Name and Media have no value on '
                 'any row of the Samsung image because it has no location or asset messages; hc_pixel8pro_a16 and '
                 'hc_pixel8pro_a17 each fill Latitude and Longitude on 2 rows and Media on 5 rows. Conversation is the '
                 'conversation Name, or the Conversation ID when the conversation has no name, so the two columns are identical '
                 'for the one-to-one and self conversations that have no name, and differ for named group conversations. Status '
                 'is shown as stored and held one value, SENT, on all rows of hc_pixel8pro_a16, and took other values '
                 '(DELIVERED, READ) on hc_pixel8pro_a17.'
        ),
        "paths": ('*/com.wire/**', '*/Secrets/secrets.json'),
        "output_types": "all",
        "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation ID",
                "conversationLabelColumn": "Conversation",
                "textColumn": "Message",
                "senderColumn": "Sender Name",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Message Timestamp",
                "sentMessageStaticLabel": "This Device",
                "mediaColumn": "Media",
            }
        },
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.wire | 34 rows",
            "hc_pixel8pro_a16": "Android 16 | com.wire | 24 rows",
            "hc_pixel8pro_a17": "Android 17 | com.wire | 48 rows",
            "pixel7a_a14": "Android 14 | com.wire | 0 rows, no com.wire key in Secrets/secrets.json",
        },
    },
    "get_wire_secure_conversations": {
        "name": "Wire Conversations (Secure Store)",
        "description": "Per-conversation metadata from the SQLCipher user database of newer Wire app "
                       "generations, read when the extraction carries the com.wire preference keysets in Secrets/secrets.json",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "None",
        "category": "Messaging",
        "notes": (
                 "These rows come from a database that newer Wire app generations encrypt with SQLCipher. The extraction's "
                 'Secrets/secrets.json com.wire entry holds the two Tink keysets that decrypt shared_prefs/app-preference.xml. '
                 'The database secret is read from that file. That file is an androidx EncryptedSharedPreferences store: the '
                 'preference name is AES-SIV with the file name app-preference as associated data, and the value is AES-256-GCM '
                 'with the encrypted name as associated data (androidx security-crypto EncryptedSharedPreferences.java at commit '
                 '83d0df9197c5320ac2e10d92afaf9ee839cec144). The decrypted preferences hold the database secret under '
                 'global_db_passphrase_alias[_v2] for global-db and user_db_secret_alias[_v2]_<account> for the user database. A '
                 '_v2 secret is 32 bytes used directly as the SQLCipher raw key (wireapp/kalium SecurityHelper.kt at commit '
                 'e9ac68451ad88f9e67dd41216df926ba47b3a581). A secret without _v2 is passed without the raw-key form in that '
                 'file; this parser derives its key with PBKDF2-HMAC-SHA512, 256,000 iterations, over the database salt, the '
                 'SQLCipher 4 defaults. A key that authenticates no page is refused; if only some pages authenticate, the copy '
                 'is used and the log says how many failed. This parser decrypts the preference names and only the two database '
                 'secret values; it does not decrypt or emit the values of the login tokens, the notification token, or the MLS '
                 "and Proteus secrets stored in the same preferences, and it contacts no server. The write-ahead log's committed "
                 'frames are applied when present; on samsung_a166u_a16_known_20261116 the log added 1 message, 1 text row and 2 '
                 'receipts. The decrypted copy is written under the report folder and read from there; the evidence file is only '
                 'read. On samsung_a166u_a16_known_20261116, hc_pixel8pro_a16 and hc_pixel8pro_a17 every page of both databases '
                 'authenticated under these settings. Android User is the user whose storage path holds the database, and it '
                 'held one value, 0, on every row of the single-user images in sample_data. One row per Conversation row, '
                 'holding the fields fixed by the conversation rather than repeated on every message: Name, Type, Protocol, '
                 'Member Count (a count of Member rows), Archived, Muted Status and Creator ID. Last Modified and Last Read are '
                 'read as Unix milliseconds; Last Read is 0, shown blank, on some rows. Name is empty on every one-to-one and '
                 'self conversation of the tested images, so Name has no value on any of the 4 rows of the Samsung image, whose '
                 'conversations are all one-to-one or self; it carries the group title on hc_pixel8pro_a16 and hc_pixel8pro_a17. '
                 'Archived held 0 on all 4 rows of the Samsung image and Muted Status held ALL_ALLOWED on every row of all three '
                 'images; both are the schema defaults. Last Modified is 0, shown blank, on 2 of 4, 3 of 5 and 3 of 8 rows of '
                 'the tested images; one such row on hc_pixel8pro_a17 has a Message row. Last Read equals Last Modified on the 2 '
                 'filled rows of hc_pixel8pro_a16 and differs on 3 of 5 filled rows of hc_pixel8pro_a17. Creator ID held one '
                 "value on all 5 rows of hc_pixel8pro_a16, the self user's id, and is stored without a domain; what the app "
                 'records as creator for one-to-one and self conversations is not established.'
        ),
        "paths": ('*/com.wire/**', '*/Secrets/secrets.json'),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.wire | 4 rows",
            "hc_pixel8pro_a16": "Android 16 | com.wire | 5 rows",
            "hc_pixel8pro_a17": "Android 17 | com.wire | 8 rows",
        },
    },
    "get_wire_secure_calls": {
        "name": "Wire Calls (Secure Store)",
        "description": "Call history from the SQLCipher user database of newer Wire app generations, read "
                       "when the extraction carries the com.wire preference keysets in Secrets/secrets.json",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "None",
        "category": "Messaging",
        "notes": (
                 "These rows come from a database that newer Wire app generations encrypt with SQLCipher. The extraction's "
                 'Secrets/secrets.json com.wire entry holds the two Tink keysets that decrypt shared_prefs/app-preference.xml. '
                 'The database secret is read from that file. That file is an androidx EncryptedSharedPreferences store: the '
                 'preference name is AES-SIV with the file name app-preference as associated data, and the value is AES-256-GCM '
                 'with the encrypted name as associated data (androidx security-crypto EncryptedSharedPreferences.java at commit '
                 '83d0df9197c5320ac2e10d92afaf9ee839cec144). The decrypted preferences hold the database secret under '
                 'global_db_passphrase_alias[_v2] for global-db and user_db_secret_alias[_v2]_<account> for the user database. A '
                 '_v2 secret is 32 bytes used directly as the SQLCipher raw key (wireapp/kalium SecurityHelper.kt at commit '
                 'e9ac68451ad88f9e67dd41216df926ba47b3a581). A secret without _v2 is passed without the raw-key form in that '
                 'file; this parser derives its key with PBKDF2-HMAC-SHA512, 256,000 iterations, over the database salt, the '
                 'SQLCipher 4 defaults. A key that authenticates no page is refused; if only some pages authenticate, the copy '
                 'is used and the log says how many failed. This parser decrypts the preference names and only the two database '
                 'secret values; it does not decrypt or emit the values of the login tokens, the notification token, or the MLS '
                 "and Proteus secrets stored in the same preferences, and it contacts no server. The write-ahead log's committed "
                 'frames are applied when present; on samsung_a166u_a16_known_20261116 the log added 1 message, 1 text row and 2 '
                 'receipts. The decrypted copy is written under the report folder and read from there; the evidence file is only '
                 'read. On samsung_a166u_a16_known_20261116, hc_pixel8pro_a16 and hc_pixel8pro_a17 every page of both databases '
                 'authenticated under these settings. Android User is the user whose storage path holds the database, and it '
                 'held one value, 0, on every row of the single-user images in sample_data. One row per Call row. Call Timestamp '
                 'is Call.created_at, a 13-digit millisecond value stored as text, read as Unix milliseconds. Status, Call Type '
                 'and Conversation Type are shown as stored. Caller Name is the User.name joined on caller_id. The Call table '
                 'held no rows on the Samsung image. Status is shown as stored and held one value, CLOSED, on all 5 rows of '
                 'hc_pixel8pro_a16 and hc_pixel8pro_a17; its meaning is not established here.'
        ),
        "paths": ('*/com.wire/**', '*/Secrets/secrets.json'),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.wire | 0 rows, Call table empty",
            "hc_pixel8pro_a16": "Android 16 | com.wire | 2 rows",
            "hc_pixel8pro_a17": "Android 17 | com.wire | 3 rows",
        },
    },
    "get_wire_secure_contacts": {
        "name": "Wire Contacts (Secure Store)",
        "description": "Known users from the SQLCipher user database of newer Wire app generations, read "
                       "when the extraction carries the com.wire preference keysets in Secrets/secrets.json",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "None",
        "category": "Messaging",
        "notes": (
                 "These rows come from a database that newer Wire app generations encrypt with SQLCipher. The extraction's "
                 'Secrets/secrets.json com.wire entry holds the two Tink keysets that decrypt shared_prefs/app-preference.xml. '
                 'The database secret is read from that file. That file is an androidx EncryptedSharedPreferences store: the '
                 'preference name is AES-SIV with the file name app-preference as associated data, and the value is AES-256-GCM '
                 'with the encrypted name as associated data (androidx security-crypto EncryptedSharedPreferences.java at commit '
                 '83d0df9197c5320ac2e10d92afaf9ee839cec144). The decrypted preferences hold the database secret under '
                 'global_db_passphrase_alias[_v2] for global-db and user_db_secret_alias[_v2]_<account> for the user database. A '
                 '_v2 secret is 32 bytes used directly as the SQLCipher raw key (wireapp/kalium SecurityHelper.kt at commit '
                 'e9ac68451ad88f9e67dd41216df926ba47b3a581). A secret without _v2 is passed without the raw-key form in that '
                 'file; this parser derives its key with PBKDF2-HMAC-SHA512, 256,000 iterations, over the database salt, the '
                 'SQLCipher 4 defaults. A key that authenticates no page is refused; if only some pages authenticate, the copy '
                 'is used and the log says how many failed. This parser decrypts the preference names and only the two database '
                 'secret values; it does not decrypt or emit the values of the login tokens, the notification token, or the MLS '
                 "and Proteus secrets stored in the same preferences, and it contacts no server. The write-ahead log's committed "
                 'frames are applied when present; on samsung_a166u_a16_known_20261116 the log added 1 message, 1 text row and 2 '
                 'receipts. The decrypted copy is written under the report folder and read from there; the evidence file is only '
                 'read. On samsung_a166u_a16_known_20261116, hc_pixel8pro_a16 and hc_pixel8pro_a17 every page of both databases '
                 'authenticated under these settings. Android User is the user whose storage path holds the database, and it '
                 'held one value, 0, on every row of the single-user images in sample_data. One row per User row. Name, Handle, '
                 'Email and Phone are as stored and are blank where the app held no value. Connection Status, User Type and '
                 'Account Deleted are shown as stored. Phone has no value on any row of the tested images; Email is filled only '
                 "on the account's own user row. Connection Status held ACCEPTED and Account Deleted held 0 on every row of all "
                 "three images, including the account's own user row; both are shown as stored. Account Deleted is User.deleted."
        ),
        "paths": ('*/com.wire/**', '*/Secrets/secrets.json'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.wire | 2 rows",
            "hc_pixel8pro_a16": "Android 16 | com.wire | 2 rows",
            "hc_pixel8pro_a17": "Android 17 | com.wire | 3 rows",
        },
    },
    "get_wire_secure_receipts": {
        "name": "Wire Receipts (Secure Store)",
        "description": "Delivery and read receipts from the SQLCipher user database of newer Wire app "
                       "generations, read when the extraction carries the com.wire preference keysets in Secrets/secrets.json",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "None",
        "category": "Messaging",
        "notes": (
                 "These rows come from a database that newer Wire app generations encrypt with SQLCipher. The extraction's "
                 'Secrets/secrets.json com.wire entry holds the two Tink keysets that decrypt shared_prefs/app-preference.xml. '
                 'The database secret is read from that file. That file is an androidx EncryptedSharedPreferences store: the '
                 'preference name is AES-SIV with the file name app-preference as associated data, and the value is AES-256-GCM '
                 'with the encrypted name as associated data (androidx security-crypto EncryptedSharedPreferences.java at commit '
                 '83d0df9197c5320ac2e10d92afaf9ee839cec144). The decrypted preferences hold the database secret under '
                 'global_db_passphrase_alias[_v2] for global-db and user_db_secret_alias[_v2]_<account> for the user database. A '
                 '_v2 secret is 32 bytes used directly as the SQLCipher raw key (wireapp/kalium SecurityHelper.kt at commit '
                 'e9ac68451ad88f9e67dd41216df926ba47b3a581). A secret without _v2 is passed without the raw-key form in that '
                 'file; this parser derives its key with PBKDF2-HMAC-SHA512, 256,000 iterations, over the database salt, the '
                 'SQLCipher 4 defaults. A key that authenticates no page is refused; if only some pages authenticate, the copy '
                 'is used and the log says how many failed. This parser decrypts the preference names and only the two database '
                 'secret values; it does not decrypt or emit the values of the login tokens, the notification token, or the MLS '
                 "and Proteus secrets stored in the same preferences, and it contacts no server. The write-ahead log's committed "
                 'frames are applied when present; on samsung_a166u_a16_known_20261116 the log added 1 message, 1 text row and 2 '
                 'receipts. The decrypted copy is written under the report folder and read from there; the evidence file is only '
                 'read. On samsung_a166u_a16_known_20261116, hc_pixel8pro_a16 and hc_pixel8pro_a17 every page of both databases '
                 'authenticated under these settings. Android User is the user whose storage path holds the database, and it '
                 'held one value, 0, on every row of the single-user images in sample_data. One row per Receipt row. Receipt '
                 'Timestamp is Receipt.date, an ISO-8601 UTC string ending in Z, parsed to a timestamp. Receipt Type is shown as '
                 'stored (DELIVERY or READ on the tested images). Conversation ID and User ID each held one value on all 32 rows '
                 "of the Samsung image; on every receipt row of the tested images User ID is a user other than the account's own "
                 'and the message is an Outgoing one. The Receipt table held no rows on hc_pixel8pro_a16.'
        ),
        "paths": ('*/com.wire/**', '*/Secrets/secrets.json'),
        "output_types": "standard",
        "artifact_icon": "check-circle",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.wire | 32 rows",
            "hc_pixel8pro_a16": "Android 16 | com.wire | 0 rows, Receipt table empty",
            "hc_pixel8pro_a17": "Android 17 | com.wire | 3 rows",
        },
    },
    "get_wire_secure_reactions": {
        "name": "Wire Reactions (Secure Store)",
        "description": "Message reactions from the SQLCipher user database of newer Wire app generations, "
                       "read when the extraction carries the com.wire preference keysets in Secrets/secrets.json",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "None",
        "category": "Messaging",
        "notes": (
                 "These rows come from a database that newer Wire app generations encrypt with SQLCipher. The extraction's "
                 'Secrets/secrets.json com.wire entry holds the two Tink keysets that decrypt shared_prefs/app-preference.xml. '
                 'The database secret is read from that file. That file is an androidx EncryptedSharedPreferences store: the '
                 'preference name is AES-SIV with the file name app-preference as associated data, and the value is AES-256-GCM '
                 'with the encrypted name as associated data (androidx security-crypto EncryptedSharedPreferences.java at commit '
                 '83d0df9197c5320ac2e10d92afaf9ee839cec144). The decrypted preferences hold the database secret under '
                 'global_db_passphrase_alias[_v2] for global-db and user_db_secret_alias[_v2]_<account> for the user database. A '
                 '_v2 secret is 32 bytes used directly as the SQLCipher raw key (wireapp/kalium SecurityHelper.kt at commit '
                 'e9ac68451ad88f9e67dd41216df926ba47b3a581). A secret without _v2 is passed without the raw-key form in that '
                 'file; this parser derives its key with PBKDF2-HMAC-SHA512, 256,000 iterations, over the database salt, the '
                 'SQLCipher 4 defaults. A key that authenticates no page is refused; if only some pages authenticate, the copy '
                 'is used and the log says how many failed. This parser decrypts the preference names and only the two database '
                 'secret values; it does not decrypt or emit the values of the login tokens, the notification token, or the MLS '
                 "and Proteus secrets stored in the same preferences, and it contacts no server. The write-ahead log's committed "
                 'frames are applied when present; on samsung_a166u_a16_known_20261116 the log added 1 message, 1 text row and 2 '
                 'receipts. The decrypted copy is written under the report folder and read from there; the evidence file is only '
                 'read. On samsung_a166u_a16_known_20261116, hc_pixel8pro_a16 and hc_pixel8pro_a17 every page of both databases '
                 'authenticated under these settings. Android User is the user whose storage path holds the database, and it '
                 'held one value, 0, on every row of the single-user images in sample_data. One row per Reaction row. Reaction '
                 'Timestamp is Reaction.date, an ISO-8601 UTC string ending in Z, parsed to a timestamp. Emoji is the stored '
                 'reaction value. The Reaction table held no rows on the Samsung image.'
        ),
        "paths": ('*/com.wire/**', '*/Secrets/secrets.json'),
        "output_types": "standard",
        "artifact_icon": "heart",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.wire | 0 rows, Reaction table empty",
            "hc_pixel8pro_a16": "Android 16 | com.wire | 2 rows",
            "hc_pixel8pro_a17": "Android 17 | com.wire | 4 rows",
        },
    },
    "get_wire_secure_accounts": {
        "name": "Wire Accounts (Secure Store)",
        "description": "Accounts from the SQLCipher global database of newer Wire app "
                       "generations, read when the extraction carries the com.wire preference keysets in Secrets/secrets.json",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "None",
        "category": "Messaging",
        "notes": (
                 "These rows come from a database that newer Wire app generations encrypt with SQLCipher. The extraction's "
                 'Secrets/secrets.json com.wire entry holds the two Tink keysets that decrypt shared_prefs/app-preference.xml. '
                 'The database secret is read from that file. That file is an androidx EncryptedSharedPreferences store: the '
                 'preference name is AES-SIV with the file name app-preference as associated data, and the value is AES-256-GCM '
                 'with the encrypted name as associated data (androidx security-crypto EncryptedSharedPreferences.java at commit '
                 '83d0df9197c5320ac2e10d92afaf9ee839cec144). The decrypted preferences hold the database secret under '
                 'global_db_passphrase_alias[_v2] for global-db and user_db_secret_alias[_v2]_<account> for the user database. A '
                 '_v2 secret is 32 bytes used directly as the SQLCipher raw key (wireapp/kalium SecurityHelper.kt at commit '
                 'e9ac68451ad88f9e67dd41216df926ba47b3a581). A secret without _v2 is passed without the raw-key form in that '
                 'file; this parser derives its key with PBKDF2-HMAC-SHA512, 256,000 iterations, over the database salt, the '
                 'SQLCipher 4 defaults. A key that authenticates no page is refused; if only some pages authenticate, the copy '
                 'is used and the log says how many failed. This parser decrypts the preference names and only the two database '
                 'secret values; it does not decrypt or emit the values of the login tokens, the notification token, or the MLS '
                 "and Proteus secrets stored in the same preferences, and it contacts no server. The write-ahead log's committed "
                 'frames are applied when present; on samsung_a166u_a16_known_20261116 the log added 1 message, 1 text row and 2 '
                 'receipts. The decrypted copy is written under the report folder and read from there; the evidence file is only '
                 'read. On samsung_a166u_a16_known_20261116, hc_pixel8pro_a16 and hc_pixel8pro_a17 every page of both databases '
                 'authenticated under these settings. Android User is the user whose storage path holds the database, and it '
                 'held one value, 0, on every row of the single-user images in sample_data. One row per Accounts row in the '
                 'global-db database. Current Account is Yes for the account named in the CurrentAccount table. Logout Reason '
                 'was blank on the one row of each tested image. Subject and Tenant have no value on the single row of each '
                 'tested image; what an empty value means is not established here.'
        ),
        "paths": ('*/com.wire/**', '*/Secrets/secrets.json'),
        "output_types": "standard",
        "artifact_icon": "key",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.wire | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.wire | 1 row",
            "hc_pixel8pro_a17": "Android 17 | com.wire | 1 row",
        },
    }
}

import base64
import datetime
import hashlib
import json
import os
import pathlib
import re
import sqlite3
import struct
import xml.etree.ElementTree as ET
from os.path import basename, isdir

from Crypto.Cipher import AES

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, check_in_media, logfunc
from scripts.sqlcipher_decrypt import decrypt_sqlcipher_db
from scripts.artifacts.storagePathViews import unique_files, android_user

UUID_RE = re.compile(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')

MESSAGES_SQL = '''
    SELECT datetime(Messages.time/1000,'unixepoch'), Messages._id, Users.name, Messages.msg_type,
    json_extract(Messages.content, '$[0].content'),
    CASE Likings."action" WHEN 1 THEN 'Liked' WHEN 0 THEN 'Unliked'
    ELSE CAST(Likings."action" AS TEXT) END,
    CASE WHEN Likings."timestamp" > 0 THEN datetime(Likings."timestamp"/1000,'unixepoch') END,
    Users1.name,
    time(Messages.duration/1000,'unixepoch'), {asset_name}
    FROM Messages
    LEFT JOIN Users ON Users._id = Messages.user_id
    LEFT JOIN Likings ON Messages._id = Likings.message_id
    LEFT JOIN Users Users1 ON Likings.user_id = Users1._id
    {asset_join}
    ORDER BY Messages.time
'''


def _asset_source(source_path):
    """Resolve the asset table this Wire release uses.

    Newer databases keep attachments in Assets2, older ones in Assets, and a
    Messages table without asset_id has nothing to join. Returns the SELECT
    expression and JOIN clause for MESSAGES_SQL. Only the Assets2 shape is
    corpus-verified; the Assets fallback comes from a community-reported
    older database (PR #633) and has not been exercised here.
    """
    db = open_sqlite_db_readonly(source_path)
    try:
        cursor = db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        cursor.execute('PRAGMA table_info(Messages)')
        has_asset_id = 'asset_id' in {row[1] for row in cursor.fetchall()}
    except sqlite3.Error:
        tables, has_asset_id = set(), False
    finally:
        db.close()
    for table in ('Assets2', 'Assets'):
        if has_asset_id and table in tables:
            db = open_sqlite_db_readonly(source_path)
            try:
                has_name = 'name' in {row[1] for row in db.execute(f'PRAGMA table_info({table})')}
            except sqlite3.Error:
                has_name = False
            finally:
                db.close()
            name_expr = f'{table}.name' if has_name else "''"
            return name_expr, f'LEFT JOIN {table} ON Messages.asset_id = {table}._id'
    return "''", ''


def _str_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError):
        return ''


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _user_id(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('com.wire.preferences.xml'):
            try:
                root = ET.parse(file_found).getroot()
            except (ET.ParseError, OSError):
                continue
            for elem in root:
                if 'active_account' in str(elem.attrib):
                    return elem.text
    return None


def _user_db(files_found):
    user_id = _user_id(files_found)
    if not user_id or not UUID_RE.match(user_id):
        return ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith(user_id) or isdir(file_found):
            continue
        try:
            with open(file_found, 'rb') as fh:
                if fh.read(16) == b'SQLite format 3\x00':
                    return file_found
        except OSError:
            continue
    return ''


def _run(source_path, sql):
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


@artifact_processor
def get_wire_profile(context):
    files_found = unique_files(context)
    source_path = _user_db(files_found)
    rows = _run(source_path, '''
        SELECT Users._id, Users.name, Users.email, Users.phone,
        json_extract(data, '$.clients[0].verification'),
        json_extract(data, '$.clients[0].label'),
        json_extract(data, '$.clients[0].model'),
        datetime(json_extract(data, '$.clients[0].regTime') / 1000, 'unixepoch'),
        Users.picture
        FROM Users LEFT JOIN Clients ON Users._id = Clients._id
        WHERE Users."connection" = "self"
    ''')
    data_list = []
    for row in rows:
        picture_id = str(row[8]) if row[8] is not None else ''
        thumb = ''
        if picture_id:
            match = next((str(f) for f in files_found if picture_id in str(f) and not isdir(str(f))), None)
            if match:
                thumb = check_in_media(match, basename(match))
        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], _str_to_utc(row[7]),
                          row[8], thumb))

    data_headers = ('User ID', 'Display Name', 'Email Address', 'Phone Number', 'Verification Status',
                    'First Client Label', 'Device Model', ('Date Registered', 'datetime'),
                    'Profile Picture ID', ('Profile Picture', 'media'))
    return data_headers, data_list, source_path


@artifact_processor
def get_wire_contacts(context):
    files_found = unique_files(context)
    source_path = _user_db(files_found)
    rows = _run(source_path, '''
        SELECT Users._id, Users.name, Users.handle, Users.connection,
        datetime(Users.conn_timestamp/1000,'unixepoch'), Users.picture
        FROM Users WHERE Users.connection != 'self'
    ''')
    data_list = [(r[0], r[1], r[2], r[3], _str_to_utc(r[4]), r[5]) for r in rows]
    data_headers = ('User ID', 'Display Name', 'Handle ID', 'Connection Status',
                    ('Connection Time', 'datetime'), 'Profile Picture ID')
    return data_headers, data_list, source_path


@artifact_processor
def get_wire_messages(context):
    files_found = unique_files(context)
    source_path = _user_db(files_found)
    data_list = []
    asset_name, asset_join = _asset_source(source_path) if source_path else ("''", '')
    for r in _run(source_path, MESSAGES_SQL.format(asset_name=asset_name, asset_join=asset_join)):
        data_list.append((_str_to_utc(r[0]), _str_to_utc(r[6]), '', r[1], r[2], r[3], r[4], r[5], r[7], r[8], r[9]))

    # Surface deleted messages from MsgDeletion read-only (the original modified the source DB to do this).
    # MsgDeletion.timestamp is not a sent time, so it gets its own column (see the notes for what
    # the legacy source stores in it).
    for d in _run(source_path, 'SELECT message_id, timestamp FROM MsgDeletion'):
        data_list.append(('', '', _ms_to_utc(d[1]), d[0], '', 'Deleted', '', '', '', '', ''))

    data_headers = (('Date / Time Sent', 'datetime'), ('Date / Time Reacted', 'datetime'),
                    ('MsgDeletion.timestamp', 'datetime'), 'Message ID', 'User Name', 'Message Type',
                    'Message Content', 'Reaction', 'Reacted By', 'Call Duration (assumes ms)', 'Asset Name')
    return data_headers, data_list, source_path


_WIRE_ACCOUNT_DIR_RE = re.compile(r'[/\\]wire\.com[/\\]([^/\\]+)[/\\]')


@artifact_processor
def get_wire_cached_files(context):
    data_list = []
    source_paths = set()

    for file_found in unique_files(context):
        file_found = str(file_found)
        match = _WIRE_ACCOUNT_DIR_RE.search(file_found)
        if not match or isdir(file_found):
            continue
        source_paths.add(file_found)
        account_id = match.group(1)

        extension = None
        try:
            with open(file_found, 'rb') as handle:
                magic = handle.read(8)
        except OSError:
            magic = b''
        if magic.startswith(b'\x89PNG'):
            extension = 'png'
        elif magic.startswith(b'\xff\xd8'):
            extension = 'jpg'
        elif magic[4:8] == b'ftyp':
            extension = 'bin'
        media_ref = ''
        if extension:
            media_ref = check_in_media(file_found, basename(file_found),
                                       force_extension=extension) or ''

        data_list.append((
            basename(file_found),
            media_ref,
            account_id,
            context.get_relative_path(file_found),
        ))

    data_headers = (
        'File Name',
        ('File', 'media'),
        'Account ID',
        'Source Path',
    )
    return data_headers, data_list, '\n'.join(sorted(source_paths))


_PROTEUS_SESSION_RE = re.compile(
    r'[/\\]com\.wire[/\\]app_accounts[/\\][^/\\]+[/\\]([^/\\]+)[/\\]proteus[/\\]sessions[/\\]([^/\\]+)$')
_OTR_SESSION_RE = re.compile(
    r'[/\\]com\.wire[/\\]files[/\\]otr[/\\]([^/\\]+)[/\\]sessions[/\\]([^/\\]+)$')


@artifact_processor
def get_wire_proteus_sessions(context):
    data_list = []
    source_paths = set()

    for file_found in unique_files(context):
        file_found = str(file_found)
        if isdir(file_found):
            continue
        match = _PROTEUS_SESSION_RE.search(file_found) or _OTR_SESSION_RE.search(file_found)
        if not match:
            continue
        source_paths.add(file_found)
        account_id = match.group(1)
        session_id = match.group(2)

        # The session id is "<user id>_<client id>", and the user id is
        # "<value>@<domain>" once the app started qualifying ids. Legacy names
        # carry no domain, so it stays empty rather than being assumed.
        remote_user, _, remote_client = session_id.rpartition('_')
        if not remote_user:
            remote_user, remote_client = session_id, ''
        user_value, _, domain = remote_user.partition('@')

        data_list.append((
            user_value,
            domain,
            remote_client,
            account_id,
            session_id,
            context.get_relative_path(file_found),
        ))

    data_headers = (
        'Other Party User ID',
        'Other Party Domain',
        'Other Party Client ID',
        'Local Account ID',
        'Session ID (as stored)',
        'Source Path',
    )
    return data_headers, data_list, '\n'.join(sorted(source_paths))


# ---------------------------------------------------------------------------
# Newer Wire generations (wireapp/kalium) keep user data in SQLCipher databases
# databases/user-db-<id>-<domain> and databases/global-db, and keep the database
# secrets in androidx EncryptedSharedPreferences (shared_prefs/app-preference.xml).
# When the extraction tool exported the two Tink keysets for that file in
# Secrets/secrets.json, the preferences decrypt, the database secret is read from
# them, and the databases open. Nothing here contacts a server, and the message
# content keys, tokens and proteus/mls secrets are never read or emitted.
# ---------------------------------------------------------------------------
WIRE_PACKAGE = 'com.wire'
WIRE_PREF_FILE = 'app-preference'
_TINK_PREFIX_LEN = 5
_AES_SIV_TYPE = 'type.googleapis.com/google.crypto.tink.AesSivKey'
_AES_GCM_TYPE = 'type.googleapis.com/google.crypto.tink.AesGcmKey'
# SQLCipher 4 settings (kalium opens with the library defaults): HMAC-SHA512, 4096-byte pages.
_WIRE_PAGE_SIZE = 4096
_WIRE_KDF_ITERATIONS = 256000
# androidx EncryptedSharedPreferences value type ids (EncryptedSharedPreferences.EncryptedType)
_ESP_STRING = 0

_wire_decrypted = {}
_wire_media_cache = {}


def _read_varint(blob, index):
    result = shift = 0
    while index < len(blob):
        byte = blob[index]
        result |= (byte & 0x7F) << shift
        index += 1
        if not byte & 0x80:
            return result, index
        shift += 7
    raise ValueError('truncated varint')


def _protobuf_fields(blob):
    """{field number: [value, ...]}; value is an int for varints and bytes for length-delimited."""
    fields = {}
    index = 0
    while index < len(blob):
        tag, index = _read_varint(blob, index)
        field, wire = tag >> 3, tag & 7
        if wire == 0:
            value, index = _read_varint(blob, index)
        elif wire == 2:
            length, index = _read_varint(blob, index)
            value, index = blob[index:index + length], index + length
        elif wire == 5:
            value, index = blob[index:index + 4], index + 4
        elif wire == 1:
            value, index = blob[index:index + 8], index + 8
        else:
            raise ValueError(f'unsupported wire type {wire}')
        fields.setdefault(field, []).append(value)
    return fields


def _tink_keyset(raw):
    """(key material bytes, 5-byte Tink prefix, type url) from a serialized Tink keyset, or None."""
    try:
        keyset = _protobuf_fields(base64.b64decode(raw))
        primary = keyset[1][0]
        chosen = None
        for key_blob in keyset.get(2, []):
            key = _protobuf_fields(key_blob)
            if key.get(3, [None])[0] == primary:
                chosen = key
                break
        chosen = chosen or _protobuf_fields(keyset[2][0])
        key_id = chosen[3][0]
        key_data = _protobuf_fields(chosen[1][0])
        type_url = key_data[1][0].decode('utf-8', 'replace')
        value = _protobuf_fields(key_data[2][0])
        # AesSivKey keeps key_value in field 2, AesGcmKey in field 3; select by the type url
        if type_url == _AES_SIV_TYPE:
            material = value[2][0]
        elif type_url == _AES_GCM_TYPE:
            material = value[3][0]
        else:
            return None
        return material, b'\x01' + struct.pack('>I', key_id), type_url
    except (ValueError, KeyError, IndexError, TypeError):
        return None


def _siv_decrypt(key, prefix, data, associated):
    if not data.startswith(prefix):
        return None
    body = data[_TINK_PREFIX_LEN:]
    cipher = AES.new(key, AES.MODE_SIV)
    cipher.update(associated)
    try:
        return cipher.decrypt_and_verify(body[16:], body[:16])
    except ValueError:
        return None


def _gcm_decrypt(key, prefix, data, associated):
    if not data.startswith(prefix):
        return None
    body = data[_TINK_PREFIX_LEN:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=body[:12])
    cipher.update(associated)
    try:
        return cipher.decrypt_and_verify(body[12:-16], body[-16:])
    except ValueError:
        return None


def _wire_keysets(files_found):
    """{Android user: (siv key, siv prefix, gcm key, gcm prefix)} from com.wire secrets.json entries."""
    out = {}
    for path in files_found:
        if os.path.basename(str(path)) != 'secrets.json':
            continue
        try:
            with open(path, 'r', encoding='utf-8') as handle:
                entries = json.load(handle)
        except (OSError, ValueError) as error:
            logfunc(f'Wire: could not read {path}: {error}')
            continue
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict) or entry.get('app') != WIRE_PACKAGE:
                continue
            payload = {}
            for output in entry.get('script_output') or []:
                if isinstance(output, dict) and isinstance(output.get('payload'), dict):
                    payload.update(output['payload'])
            keys_key = _tink_keyset(payload.get('encrypted_prefs_keys_key', ''))
            values_key = _tink_keyset(payload.get('encrypted_prefs_values_key', ''))
            if not keys_key or not values_key:
                continue
            user_id = entry.get('user_id')
            out[('' if user_id is None else str(user_id))] = (keys_key[0], keys_key[1],
                                                              values_key[0], values_key[1])
    return out


def _wire_prefs(prefs_path, keyset):
    """{preference name: raw base64 value} for one app-preference.xml, names decrypted, values left encrypted."""
    siv_key, siv_prefix, _gcm_key, _gcm_prefix = keyset
    associated = WIRE_PREF_FILE.encode('utf-8')
    names = {}
    try:
        root = ET.parse(prefs_path).getroot()
    except (ET.ParseError, OSError) as error:
        logfunc(f'Wire: could not read {prefs_path}: {error}')
        return names
    for element in root:
        encrypted_name = element.get('name') or ''
        if encrypted_name.startswith('__androidx_security_crypto') or element.text is None:
            continue
        try:
            raw_name = base64.b64decode(encrypted_name)
        except (ValueError, TypeError):
            continue
        plain = _siv_decrypt(siv_key, siv_prefix, raw_name, associated)
        if plain is not None:
            names[plain.decode('utf-8', 'replace')] = (encrypted_name, element.text)
    return names


def _wire_pref_string(keyset, encrypted_name, encrypted_value):
    """The plaintext of one EncryptedSharedPreferences STRING value, or None."""
    _siv_key, _siv_prefix, gcm_key, gcm_prefix = keyset
    try:
        raw_value = base64.b64decode(encrypted_value)
    except (ValueError, TypeError):
        return None
    plain = _gcm_decrypt(gcm_key, gcm_prefix, raw_value, encrypted_name.encode('utf-8'))
    if plain is None or len(plain) < 8:
        return None
    type_id, length = struct.unpack('>ii', plain[:8])
    if type_id != _ESP_STRING:
        return None
    return plain[8:8 + length].decode('utf-8', 'replace')


def _wire_db_key(secret_value, is_raw, database_path):
    """The 32-byte SQLCipher key: a _v2 secret is the key itself, a legacy secret is a passphrase."""
    try:
        material = base64.b64decode(secret_value)
    except (ValueError, TypeError):
        return None
    if len(material) != 32:
        return None
    if is_raw:
        return material
    with open(database_path, 'rb') as handle:
        salt = handle.read(16)
    return hashlib.pbkdf2_hmac('sha512', material, salt, _WIRE_KDF_ITERATIONS, 32)


def _wire_filter_name(value):
    return ''.join(ch for ch in value if ch.isalnum() or ch == '-')


def _wire_open(database_path, key, report_folder):
    """Decrypt one Wire database to the report folder; returns the path or '' when no key authenticates."""
    digest = hashlib.sha1(database_path.encode('utf-8', 'replace')).hexdigest()[:12]
    output = os.path.join(report_folder, 'wire_decrypted', f'{digest}_{os.path.basename(database_path)}')
    os.makedirs(os.path.dirname(output), exist_ok=True)
    try:
        pages, verified = decrypt_sqlcipher_db(database_path, key, output, page_size=_WIRE_PAGE_SIZE,
                                               hmac_algorithm='sha512', kdf_algorithm='sha512', raw_key=True)
    except (OSError, ValueError) as error:
        logfunc(f'Wire: {os.path.basename(database_path)} not decrypted: {error}')
        if os.path.exists(output):
            os.remove(output)
        return ''
    if not verified:
        os.remove(output)
        return ''
    if verified != pages:
        logfunc(f'Wire: {pages - verified} of {pages} pages of {os.path.basename(database_path)} '
                'failed HMAC verification; the recovered data may be incomplete')
    return output


def _wire_decrypt(context):
    """Decrypt every Wire container the extraction carries. Cached per run.

    Returns {'user': [(decrypted, source, android user)], 'global': [...]}.
    """
    files_found = unique_files(context)
    report_folder = context.get_report_folder()
    cache_key = id(files_found)
    if cache_key in _wire_decrypted:
        return _wire_decrypted[cache_key]
    result = {'user': [], 'global': []}
    keysets = _wire_keysets(files_found)
    if not keysets:
        if any(os.path.basename(str(p)).startswith('user-db-') and '/com.wire/' in str(p).replace('\\', '/')
               for p in files_found):
            logfunc('Wire: a user database is present but Secrets/secrets.json carries no com.wire key, '
                    'so it stays encrypted')
        _wire_decrypted[cache_key] = result
        return result

    prefs_by_user = {}
    user_dbs = []
    global_dbs = []
    for raw in files_found:
        path = str(raw)
        if isdir(path) or '/com.wire/' not in path.replace('\\', '/'):
            continue
        name = os.path.basename(path)
        user = android_user(context.get_relative_path(path))
        if name == f'{WIRE_PREF_FILE}.xml':
            prefs_by_user[user] = path
        elif name == 'global-db':
            global_dbs.append((path, user))
        elif name.startswith('user-db-') and not name.endswith(('-wal', '-shm', '-journal')):
            user_dbs.append((path, user))

    # the key material for a container, then for a user-less secrets entry when the container has no own user
    def keyset_for(user):
        return keysets.get(user) or (keysets.get('') if user else None)

    secrets_cache = {}

    def secrets_for(user, prefs_path):
        if user not in secrets_cache:
            keyset = keyset_for(user)
            secrets_cache[user] = (keyset, _wire_prefs(prefs_path, keyset) if keyset else {})
        return secrets_cache[user]

    for path, user in global_dbs:
        prefs_path = prefs_by_user.get(user)
        keyset = keyset_for(user)
        if not prefs_path or not keyset:
            continue
        _keyset, names = secrets_for(user, prefs_path)
        for alias, is_raw in (('global_db_passphrase_alias_v2', True), ('global_db_passphrase_alias', False)):
            if alias not in names:
                continue
            secret = _wire_pref_string(keyset, *names[alias])
            key = _wire_db_key(secret, is_raw, path) if secret else None
            if key and path not in _wire_decrypted:
                opened = _wire_open(path, key, report_folder)
                if opened:
                    result['global'].append((opened, path, user))
                    break

    for path, user in user_dbs:
        prefs_path = prefs_by_user.get(user)
        keyset = keyset_for(user)
        if not prefs_path or not keyset:
            logfunc(f'Wire: no secrets.json keys for {os.path.basename(path)}, so it stays encrypted')
            continue
        _keyset, names = secrets_for(user, prefs_path)
        opened = ''
        for alias, is_raw in (('user_db_secret_alias_v2', True), ('user_db_secret_alias', False)):
            for full_alias, value in names.items():
                if not full_alias.startswith(alias + '_'):
                    continue
                account = full_alias[len(alias) + 1:]
                local, _, domain = account.partition('@')
                expected = f'user-db-{_wire_filter_name(local)}-{_wire_filter_name(domain)}'
                if os.path.basename(path) != expected:
                    continue
                secret = _wire_pref_string(keyset, *value)
                key = _wire_db_key(secret, is_raw, path) if secret else None
                if key:
                    opened = _wire_open(path, key, report_folder)
                    if opened:
                        break
            if opened:
                break
        if opened:
            result['user'].append((opened, path, user))
        else:
            logfunc(f'Wire: no secrets.json key authenticated {os.path.basename(path)}')
    _wire_decrypted[cache_key] = result
    return result


def _wire_rows(decrypted, sql):
    db = sqlite3.connect(pathlib.Path(decrypted).absolute().as_uri() + '?mode=ro', uri=True)
    try:
        return db.execute(sql).fetchall()
    except sqlite3.Error as error:
        logfunc(f'Wire: query failed on {os.path.basename(decrypted)}: {error}')
        return []
    finally:
        db.close()


def _wire_iso_to_utc(value):
    if not value or not isinstance(value, str):
        return ''
    try:
        return datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return ''


def _wire_media_index(context):
    """{path after com.wire/: on-disk path} for files under files/wire.com and cache/wire.com."""
    files = unique_files(context)
    cache_key = id(files)
    if cache_key in _wire_media_cache:
        return _wire_media_cache[cache_key]
    index = {}
    for raw in files:
        path = str(raw).replace('\\', '/')
        if isdir(path):
            continue
        marker = '/com.wire/'
        at = path.find(marker)
        if at == -1:
            continue
        tail = path[at + len(marker):]
        if tail.startswith(('files/wire.com/', 'cache/wire.com/')):
            index.setdefault(tail, str(raw))
    _wire_media_cache[cache_key] = index
    return index


def _wire_media_reference(context, data_path):
    if not data_path:
        return ''
    marker = '/com.wire/'
    at = str(data_path).replace('\\', '/').find(marker)
    if at == -1:
        return ''
    on_disk = _wire_media_index(context).get(str(data_path).replace('\\', '/')[at + len(marker):])
    if not on_disk:
        return ''
    try:
        with open(on_disk, 'rb') as handle:
            magic = handle.read(8)
    except OSError:
        return ''
    extension = ('png' if magic.startswith(b'\x89PNG') else 'jpg' if magic.startswith(b'\xff\xd8')
                 else 'gif' if magic.startswith(b'GIF8') else 'bin' if magic[4:8] == b'ftyp' else None)
    if not extension:
        return ''
    return check_in_media(on_disk, basename(on_disk), force_extension=extension) or ''


@artifact_processor
def get_wire_secure_messages(context):
    data_list = []
    source_paths = []
    for decrypted, source, user in _wire_decrypt(context)['user']:
        source_paths.append(source)
        self_id = next(iter(_wire_rows(decrypted, 'SELECT id FROM SelfUser')), (None,))[0]
        rows = _wire_rows(decrypted, '''
            SELECT m.creation_date, c.qualified_id, COALESCE(NULLIF(c.name,''), c.qualified_id),
                   m.sender_user_id, u.name, m.content_type, m.status, m.visibility,
                   t.text_body, loc.latitude, loc.longitude, loc.name,
                   a.data_path, m.sender_client_id
            FROM Message m
            LEFT JOIN Conversation c ON c.qualified_id = m.conversation_id
            LEFT JOIN User u ON u.qualified_id = m.sender_user_id
            LEFT JOIN MessageTextContent t ON t.message_id = m.id AND t.conversation_id = m.conversation_id
            LEFT JOIN MessageConversationLocationContent loc
                   ON loc.message_id = m.id AND loc.conversation_id = m.conversation_id
            LEFT JOIN MessageAssetContent mac ON mac.message_id = m.id AND mac.conversation_id = m.conversation_id
            LEFT JOIN Asset a ON a.key = mac.asset_id
            ORDER BY m.creation_date
        ''')
        for row in rows:
            direction = 'Outgoing' if self_id is not None and row[3] == self_id else 'Incoming'
            sender_name = 'This Device' if direction == 'Outgoing' else (row[4] or '')
            media = _wire_media_reference(context, row[12])
            data_list.append((_ms_to_utc(row[0]), direction, sender_name, row[2], row[8], media,
                              row[1], row[3], row[5], row[6], row[7], row[9], row[10], row[11],
                              row[13], user))
    data_headers = (
        ('Message Timestamp', 'datetime'), 'Direction', 'Sender Name', 'Conversation', 'Message',
        ('Media', 'media'), 'Conversation ID', 'Sender ID', 'Message Type', 'Status', 'Visibility',
        ('Latitude', 'latitude'), ('Longitude', 'longitude'), 'Location Name', 'Sender Client ID',
        'Android User')
    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def get_wire_secure_conversations(context):
    data_list = []
    source_paths = []
    for decrypted, source, user in _wire_decrypt(context)['user']:
        source_paths.append(source)
        for row in _wire_rows(decrypted, '''
            SELECT c.last_modified_date, c.last_read_date, c.qualified_id, c.name, c.type, c.protocol,
                   (SELECT COUNT(*) FROM Member m WHERE m.conversation = c.qualified_id),
                   c.archived, c.muted_status, c.creator_id
            FROM Conversation c ORDER BY c.last_modified_date DESC
        '''):
            data_list.append((_ms_to_utc(row[0]), _ms_to_utc(row[1]), row[2], row[3], row[4], row[5],
                              row[6], row[7], row[8], row[9], user))
    data_headers = (
        ('Last Modified', 'datetime'), ('Last Read', 'datetime'), 'Conversation ID', 'Name',
        'Type', 'Protocol', 'Member Count', 'Archived', 'Muted Status', 'Creator ID', 'Android User')
    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def get_wire_secure_calls(context):
    data_list = []
    source_paths = []
    for decrypted, source, user in _wire_decrypt(context)['user']:
        source_paths.append(source)
        for row in _wire_rows(decrypted, '''
            SELECT call.created_at, call.conversation_id, call.status, call.type, call.conversation_type,
                   call.caller_id, u.name
            FROM Call call LEFT JOIN User u ON u.qualified_id = call.caller_id
            ORDER BY call.created_at
        '''):
            data_list.append((_ms_to_utc(row[0]), row[1], row[2], row[3], row[4], row[5], row[6], user))
    data_headers = (
        ('Call Timestamp', 'datetime'), 'Conversation ID', 'Status', 'Call Type', 'Conversation Type',
        'Caller ID', 'Caller Name', 'Android User')
    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def get_wire_secure_contacts(context):
    data_list = []
    source_paths = []
    for decrypted, source, user in _wire_decrypt(context)['user']:
        source_paths.append(source)
        for row in _wire_rows(decrypted, '''
            SELECT qualified_id, name, handle, email, phone, connection_status, user_type, deleted
            FROM User ORDER BY name
        '''):
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], user))
    data_headers = (
        'User ID', 'Name', 'Handle', 'Email', 'Phone', 'Connection Status', 'User Type',
        'Account Deleted', 'Android User')
    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def get_wire_secure_receipts(context):
    data_list = []
    source_paths = []
    for decrypted, source, user in _wire_decrypt(context)['user']:
        source_paths.append(source)
        for row in _wire_rows(decrypted, '''
            SELECT date, message_id, conversation_id, type, user_id FROM Receipt ORDER BY date
        '''):
            data_list.append((_wire_iso_to_utc(row[0]), row[1], row[2], row[3], row[4], user))
    data_headers = (
        ('Receipt Timestamp', 'datetime'), 'Message ID', 'Conversation ID', 'Receipt Type',
        'User ID', 'Android User')
    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def get_wire_secure_reactions(context):
    data_list = []
    source_paths = []
    for decrypted, source, user in _wire_decrypt(context)['user']:
        source_paths.append(source)
        for row in _wire_rows(decrypted, '''
            SELECT date, message_id, conversation_id, emoji, sender_id FROM Reaction ORDER BY date
        '''):
            data_list.append((_wire_iso_to_utc(row[0]), row[1], row[2], row[3], row[4], user))
    data_headers = (
        ('Reaction Timestamp', 'datetime'), 'Message ID', 'Conversation ID', 'Emoji',
        'Sender ID', 'Android User')
    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def get_wire_secure_accounts(context):
    data_list = []
    source_paths = []
    for decrypted, source, user in _wire_decrypt(context)['global']:
        source_paths.append(source)
        for row in _wire_rows(decrypted, '''
            SELECT a.id, a.subject, a.tenant, a.server_config_id, a.logout_reason,
                   (SELECT 1 FROM CurrentAccount ca WHERE ca.user_id = a.id)
            FROM Accounts a
        '''):
            data_list.append((row[0], row[1], row[2], row[3], row[4],
                              'Yes' if row[5] else 'No', user))
    data_headers = (
        'Account ID', 'Subject', 'Tenant', 'Server Config ID', 'Logout Reason',
        'Current Account', 'Android User')
    return data_headers, data_list, '\n'.join(sorted(source_paths))

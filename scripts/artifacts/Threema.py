__artifacts_v2__ = {
    "threema_account": {
        "name": "Threema - Account",
        "description": "The local Threema account's own Threema ID, nickname and any mobile "
                       "number linked to it, read from the app's default preferences file.",
        "author": "@Gear-I & Claude, @AlexisBrignoni, Codex, @kalink0",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-11-15",
        "requirements": "none",
        "category": "Threema",
        "notes": "Read from the client's default preferences file, which Android names after "
                 "the package. 'Linked Mobile Number' is blank when the file carries none; "
                 "absence is not evidence that no number was ever linked. 'Package' is the "
                 "app package the file belongs to: Threema (ch.threema.app), Threema Work "
                 "(ch.threema.app.work), Threema OnPrem (ch.threema.app.onprem) and Threema "
                 "Libre (ch.threema.app.libre) are among the build flavours of one source "
                 "(app/build.gradle.kts L74, L232-L236, L346-L351, L483-L489). The paths "
                 "match every folder beginning ch.threema.app; the code keeps ch.threema.app "
                 "and names that add dot-separated parts to it. 'Profile Picture' is the "
                 "account's own picture, which the client stores as the user-defined ('.c-') "
                 "picture of its own identity (UserServiceImpl.java L577-L598), encrypted "
                 "with the master key. It is decrypted with each key read from key.dat or "
                 "master_key.dat beside it (see Threema - Contacts) and taken only when it "
                 "decrypts to an image, so it is blank where no key file could be read, where"
                 " the file is not in the extraction, and where no picture was set. File "
                 "references are to Threema for Android at commit d44a2b53 "
                 "(github.com/threema-ch/threema-android/tree/d44a2b53b2ea2c0bf1065bdaa96987570e5b4e6d)."
                 " Only ch.threema.app is present on the test images in sample_data. Whether "
                 "the linked number was verified is not reported. The picture was found and "
                 "decrypted on pixel7a_a14 and hickman_a13; on pixel3_a12 'Profile Picture' "
                 "held no value.",
        "paths": (
            '*/ch.threema.app*/shared_prefs/ch.threema.app*_preferences.xml',
            '*/ch.threema.app*/files/key.dat',
            '*/ch.threema.app*/files/master_key.dat',
            '*/ch.threema.app*/files/user-data/.profile-pictures/.c-*',
            '*/Android/data/ch.threema.app*/files/data/.avatar/.c-*',
        ),
        "output_types": ["standard"],
        "artifact_icon": "user",
        "sample_data": {
            "pixel7a_a14": "Android 14 | Threema 5.4.1 (ch.threema.app) | 1 row",
            "pixel3_a12": "Android 12 | Threema 4.59 (ch.threema.app) | 1 row",
            "hickman_a13": "Android 13 | Threema 4.83 (ch.threema.app) | 1 row",
        },
    },
    "threema_contacts": {
        "name": "Threema - Contacts",
        "description": "Contacts recorded in Threema's local, SQLCipher-encrypted database, "
                       "with each one's stored verification level and the date the contact "
                       "record was created locally.",
        "author": "@Gear-I & Claude, @AlexisBrignoni, Codex, @kalink0",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-11-16",
        "requirements": "sqlcipher3",
        "category": "Threema",
        "notes": "threema4.db is SQLCipher-encrypted and is opened read-only with its "
                 "write-ahead log, with the master key from key.dat, version 1, read when "
                 "unprotected and its checksum verifies (Version1MasterKeyFileManager.kt "
                 "L18-L43; the checksum verified on pixel7a_a14, pixel3_a12 and hickman_a13),"
                 " or from master_key.dat, version 2, read when no layer is passphrase- or "
                 "remote-secret-protected (Version2MasterKeyStorageDecoder.kt L24-L123; no "
                 "test image in sample_data carries one, the constructed case "
                 "casesynthetic_v2 does). On pixel7a_a14 the database file without its "
                 "write-ahead log held 30 of the 33 messages and 2 of the 3 contacts; none of"
                 " the log's 36 committed states holds a message or contact the current "
                 "tables do not. Not read: enc_master_key_v2.dat, which the Android key store"
                 " protects (Version2MasterKeyFileManagerImpl.kt L31-L69), and "
                 "passphrase-protected keys. Such an install gives no rows and the log says "
                 "why; the case with no key file was run on pixel7a_a14 with key.dat removed,"
                 " and the key store and passphrase cases are not exercised. By client "
                 "version: key.dat up to 6.1.x, master_key.dat from 6.2.0 "
                 "(MasterKeyFileProvider.kt L35-L36 at commit 0437b046), "
                 "enc_master_key_v2.dat from 6.4.0 (same file L18-L20 at commit 65acf422), "
                 "except below Android 8.0, where the client keeps master_key.dat "
                 "(LocalCryptoFeatureModule.kt L43-L57). Once a 6.4.0 or later client has run"
                 " on Android 8.0 or later, it moves the key to enc_master_key_v2.dat and "
                 "deletes master_key.dat (Version2MasterKeyFileManagerImpl.kt L33-L66), and "
                 "such an install is not decrypted. A column a schema lacks is blank. "
                 "'Verification Level' maps verificationLevel 0=Unverified, "
                 "1=Server-verified, 2=Fully verified (VerificationLevel.java L10-L12); how a"
                 " level was reached is not reported. 'Group-Only / Removed' is Yes when "
                 "acquaintanceLevel (isHidden before schema version 94, same values; "
                 "DatabaseUpdateToVersion94.kt L18-L23) is set: the client's GROUP_OR_DELETED"
                 " covers a contact known only through a group, one removed from all common "
                 "groups, and one explicitly removed (Contact.kt L213-L231), which the field "
                 "cannot tell apart. The three cases are the current client's definition; "
                 "what an older client set isHidden for is not established beyond 'visible in"
                 " the contact list' (ContactModel.java L55 at tag 4.59). 'Date Created' is "
                 "dateCreated, written in Unix milliseconds (ContactModelFactory.java L405), "
                 "the date the record was created locally (ContactModel.java L57). 'Archived'"
                 " is Yes when the one-to-one chat is archived: isArchived until schema "
                 "version 126, conversationVisibility 1 from it "
                 "(DatabaseUpdateToVersion126.kt L95-L128; pinned, 2, is not reported). The "
                 "three profile picture columns are the three pictures the client can store "
                 "per contact (see Threema - Media for their names and locations), each taken"
                 " only when it decrypts to an image; which one the app displays is not "
                 "reported, and a blank means no such file was extracted or none decrypted. "
                 "The paths match every folder beginning ch.threema.app; the code keeps "
                 "ch.threema.app and names that add dot-separated parts to it. File "
                 "references are to Threema for Android at commit d44a2b53 "
                 "(github.com/threema-ch/threema-android/tree/d44a2b53b2ea2c0bf1065bdaa96987570e5b4e6d)."
                 " Only ch.threema.app is present on the test images in sample_data. isHidden"
                 " is read on pixel3_a12 (schema version 66) and hickman_a13 (72), with no "
                 "row set; acquaintanceLevel on pixel7a_a14 (97); conversationVisibility "
                 "follows the cited source. casesynthetic_v2 is a constructed install built "
                 "by admin/test/scripts/threema_fixture.py with invented values, in the file "
                 "layout, key file layers, table definitions of schema version 114, message "
                 "body shapes and database passphrase form the client uses. It exercises "
                 "master_key.dat, a group-only and an archived contact (3 rows). On "
                 "pixel7a_a14 (3 rows) one contact is level 2, and 'Group-Only / Removed', "
                 "'Archived' and 'Profile Picture (set locally)' held no value on any row. On"
                 " pixel3_a12 (2 rows) 'Profile Picture (from contact)' and 'Profile Picture "
                 "(Android contact)' held no value on any row; on hickman_a13 (2 rows) "
                 "'Profile Picture (Android contact)' held no value on any row. 'Profile "
                 "Picture (set locally)' and 'Archived' held no value on any row of any test "
                 "image; they are exercised only by casesynthetic_v2.",
        "paths": (
            '*/ch.threema.app*/files/key.dat',
            '*/ch.threema.app*/files/master_key.dat',
            '*/ch.threema.app*/files/enc_master_key_v2.dat',
            '*/ch.threema.app*/databases/threema4.db*',
            '*/ch.threema.app*/files/user-data/.profile-pictures/.[acp]-*',
            '*/Android/data/ch.threema.app*/files/data/.avatar/.[acp]-*',
        ),
        "output_types": ["standard"],
        "artifact_icon": "address-book",
        "sample_data": {
            "pixel7a_a14": "Android 14 | Threema 5.4.1 (ch.threema.app) | 3 rows",
            "pixel3_a12": "Android 12 | Threema 4.59 (ch.threema.app) | 2 rows",
            "hickman_a13": "Android 13 | Threema 4.83 (ch.threema.app) | 2 rows",
        },
    },
    "threema_messages": {
        "name": "Threema - Messages",
        "description": "One-to-one and group messages recorded in Threema's local, "
                       "SQLCipher-encrypted database: text, files and media, static "
                       "locations, calls and status messages, with direction, delivery/read "
                       "status, any quote-reply relationship between messages, and the "
                       "attached media where its file is in the extraction.",
        "author": "@Gear-I & Claude, @AlexisBrignoni, Codex, @kalink0",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-11-15",
        "requirements": "sqlcipher3",
        "category": "Threema",
        "notes": "The database is opened as for Threema - Contacts, with the same key files "
                 "and limits. Rows come from the message table (one-to-one chats) and "
                 "m_group_message (groups); a column a schema lacks is blank. 'Created', "
                 "'Delivered' and 'Read At' are createdAtUtc, deliveredAtUtc and readAtUtc, "
                 "written as Unix milliseconds (DatabaseUtil.java L21-L23); 'Edited' and "
                 "'Deleted' are editedAtUtc and deletedAtUtc. 'Read' is Yes when isRead is "
                 "set; what it means on a sent row is not established. 'Conversation' is the "
                 "contact's name and Threema ID, or 'Group:' with the group's name and local "
                 "id ('Group #id' when the group has no name). 'Direction' is Sent or "
                 "Received from outbox, or Status for a row with isStatusMessage set, a "
                 "notice the client writes into the chat (a group created, forward security "
                 "established). 'Sender' is the local account from the preferences file for a"
                 " sent row ('Local account' without that file), the contact for a received "
                 "one-to-one row, the stored member for a received group row, and blank for a"
                 " status row; 'Contact' is the conversation partner, or the stored identity "
                 "for a group row: on a received group row that is the sending member, and "
                 "what a sent group row holds there is not established. Content is decoded by"
                 " message type (MessageType.kt L3-L33): text; location, by the positions "
                 "LocationDataModel.kt L44-L51 writes: latitude, longitude, accuracy and "
                 "address (the place name after them is not reported; accuracy is in metres "
                 "per the protocol message, LocationMessage.kt L15); file "
                 "(FileDataModelSerializer.kt L29-L45; a body from before the rendering type "
                 "existed is read as the 5.8.2 reader read it, FileDataModel.java L327-L335 "
                 "at commit ab243097, unexercised); call, group call, forward security and "
                 "group status (StatusDataModel.kt L35-L57, names from VoipStatusDataModel.kt"
                 " L53-L56, GroupCallStatusDataModel.kt L31-L32, "
                 "ForwardSecurityStatusDataModel.kt L34-L51 and GroupStatusDataModel.kt "
                 "L22-L61); and the former image, video and voice types still held for old "
                 "messages (VideoDataModel.java L105-L116, AudioDataModel.java L83-L91 at "
                 "commit ab243097). Types 5, 6, 7 and 10 are not decoded and show as "
                 "Unrecognized with the stored body. 'Call Status' is the stored number, "
                 "'Message' its name; the stored call parameters hold no audio/video "
                 "distinction (VoipStatusDataModel.kt L38-L45), and the stored reason is not "
                 "reported. 'Message' is the text, a file's caption (blank when it has none),"
                 " a location's address, or the call or status notice. 'Media Duration (s)' "
                 "is a video or voice message's stored duration or a file's metadata key 'd' "
                 "(FileDataModel.java L21), a decimal number of seconds "
                 "(MessageServiceImpl.java L3686), rounded to whole seconds. 'Quoted Message'"
                 " resolves quotedMessageId against apiMessageId across both tables, not by "
                 "row order, and is blank when the quoted message is not a text message in "
                 "the database. 'Reactions' lists emoji, reacting account and time from "
                 "contact_reactions and group_reactions (schema version 106; the version 105 "
                 "tables contact_emoji_reactions and group_emoji_reactions are read by "
                 "message uid; DatabaseUpdateToVersion106.kt L73-L114). Older databases keep "
                 "a thumbs up or down as the message's state USERACK or USERDEC, sent by the "
                 "recipient (MessageState.java L54-L64), or per member in groupMessageStates;"
                 " these are reported as the client reads them (EmojiReactionsRepository.kt "
                 "L110-L168): on a sent one-to-one message as the contact's, on a received "
                 "one as the local account's, without a time. A reaction time equal to the "
                 "message's creation time is marked 'no reaction time stored'; this mark is "
                 "not exercised. A backup restore stores such a converted reaction with the "
                 "message's modified time, else its creation time, else the time of the "
                 "restore (RestoreService.java L1797-L1828), so a stored reaction time can be"
                 " the restore's guess; this is not exercised. 'Media' is the message's file,"
                 " else its thumbnail, decrypted in memory as described for Threema - Media. "
                 "'Gallery Copy' lists each file in a Threema gallery folder whose bytes are "
                 "identical to the message's decrypted file or thumbnail and to no other "
                 "message's (see Threema - Media; a name alone ties nothing), by its path in "
                 "the extraction and, in brackets, the 'Gallery Link' value of Threema - "
                 "Media; on pixel7a_a14, pixel3_a12 and hickman_a13 one row each holds one. "
                 "'Media Status' is File or Thumbnail only, with "
                 "'(type not recognised)' where no file type was recognised in the decrypted "
                 "bytes, Not on device where neither file is in the extraction (a file can be"
                 " missing for reasons the database does not record), or Decryption failed. "
                 "Not reported: whether a chat is archived, distribution lists and polls "
                 "(tables empty on every test image), and deletion inferred from a gap in the"
                 " numbering. File references are to Threema for Android at commit d44a2b53 "
                 "(see Threema - Contacts) unless stated. Only text, location, file and call "
                 "rows are exercised by the test images in sample_data; the constructed case "
                 "casesynthetic_v2 (see Threema - Contacts; 12 rows) also exercises a forward"
                 " security and a text status row, group rows, former image and voice rows, "
                 "reactions from the reaction tables and edited and deleted dates; video, "
                 "group call status and group status rows are not exercised. On pixel7a_a14 "
                 "(33 rows, one conversation) 3 messages, 2 location and 1 text, existed only"
                 " in the write-ahead log, and one received row holds state USERACK; "
                 "'Contact' holds one value on all 33 rows, 'Conversation' holds one value on"
                 " all 33 rows, 'Read' holds one value, Yes, on all 33 rows, 'Edited' held no"
                 " value on any row, 'Deleted' held no value on any row, and 'Media Duration "
                 "(s)' held no value on any row. On pixel3_a12 (18 rows, schema version 66) "
                 "'Delivered' and 'Read At' held no value on any row (the schema has neither "
                 "column), and 'Call ID', 'Quoted Message' and 'Reactions' held no value on "
                 "any row. On hickman_a13 (25 rows, schema version 72) 'Call ID' and "
                 "'Reactions' held no value on any row. 'Edited', 'Deleted' and 'Media "
                 "Duration (s)' held no value on any row of any test image (schema versions "
                 "66 and 72 have no editedAtUtc or deletedAtUtc), and 'Read' is Yes on every "
                 "row of all three.",
        "paths": (
            '*/ch.threema.app*/files/key.dat',
            '*/ch.threema.app*/files/master_key.dat',
            '*/ch.threema.app*/files/enc_master_key_v2.dat',
            '*/ch.threema.app*/databases/threema4.db*',
            '*/ch.threema.app*/shared_prefs/ch.threema.app*_preferences.xml',
            # Message files; the code keeps only '.' + 32 hex digits ('_T'
            # for a thumbnail), so pictures beside them are not used.
            '*/ch.threema.app*/files/user-data/.message-files/.*',
            '*/Android/data/ch.threema.app*/files/data/.*',
            # Gallery copies (FileServiceImpl.kt copyMediaFileToGallery): the public
            # directories hold one folder per MEDIA_PATH value, older Android one of its own.
            '*/Pictures/Threema*/*', '*/Movies/Threema*/*', '*/Music/Threema*/*',
            '*/Documents/Threema*/*', '*/Download/Threema*/*',
            '*/Threema*/Threema Pictures/*', '*/Threema*/Threema Videos/*',
            '*/Threema*/Threema Audio/*',
        ),
        "output_types": ["standard", "timeline"],
        "artifact_icon": "message-circle",
        "sample_data": {
            "pixel7a_a14": "Android 14 | Threema 5.4.1 (ch.threema.app) | 33 rows",
            "pixel3_a12": "Android 12 | Threema 4.59 (ch.threema.app) | 18 rows",
            "hickman_a13": "Android 13 | Threema 4.83 (ch.threema.app) | 25 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Sent",
                "timeColumn": "Created",
                "senderColumn": "Sender",
                "mediaColumn": "Media",
            }
        },
    },
    "threema_media": {
        "name": "Threema - Media",
        "description": "Media files Threema keeps encrypted on the device, decrypted: message"
                       " files and thumbnails, profile pictures, group pictures and "
                       "wallpapers, with what the app's database says each belongs to, "
                       "including files the database does not refer to, and the files in the "
                       "app's shared storage gallery folders, each tied to a message where its"
                       " bytes are identical to that message's file.",
        "author": "@kalink0",
        "creation_date": "2026-11-14",
        "last_update_date": "2026-11-16",
        "requirements": "sqlcipher3",
        "category": "Threema",
        "notes": "One row per file in the client's two user files directories, "
                 "files/user-data/ in the app data directory and files/data/ in external "
                 "storage (AppDirectoryProvider.kt L18-L22, L36-L38); an external directory "
                 "is paired with an app data directory only when both name the same Android "
                 "user and package. Every file is decrypted in memory with every master key "
                 "read beside it (key.dat or master_key.dat, see Threema - Contacts), "
                 "independently of the database, as AES-CBC with a 16-byte IV "
                 "(MasterKeyImpl.kt L31-L79), and its type is read from the decrypted bytes; "
                 "the sqlcipher3 module is still required, and without it no row is listed. "
                 "The name gives the kind: '.' + 32 hex digits, the message uid without "
                 "dashes, a message file, with '_T' its thumbnail "
                 "(MessageFileHandleProvider.kt L11-L39); '.p-', '.c-' or '.a-' + "
                 "Base32(SHA-256('c-' + Threema ID)) a profile picture from the contact, set "
                 "locally (for the account's own identity, its own picture) or from the "
                 "Android contact (ProfilePictureFileHandleProvider.kt L17-L54); '.gpp-' or "
                 "'.grp-avatar-' + a group's local id a group picture "
                 "(GroupProfilePictureFileHandleProvider.kt L11-L27); '.w-' + an obfuscated "
                 "conversation id, or wallpaper.jpg, a wallpaper "
                 "(WallpaperFileHandleProvider.kt L15-L45). In the external directory, "
                 "profile picture and wallpaper names end in '.nomedia' "
                 "(ProfilePictureFileHandleProvider.kt L32-L37), which 'Stored File Name' "
                 "leaves out. A file with any other name is listed as Other file only when it"
                 " decrypts. 'Belongs To' is resolved against the database: the message's "
                 "conversation, the contact or local account whose identity hashes to the "
                 "name, or the group; 'Not referenced by the database' when nothing matches "
                 "(for example a message no longer stored; why is not asserted), 'Database "
                 "not opened' when it could not be opened or was not extracted. Wallpapers "
                 "are not resolved, the id being obfuscated. 'Message Created' and 'Message' "
                 "are the message's createdAtUtc and its caption, file name or text. A file "
                 "in both directories is listed once per directory. 'Status' is Decrypted; "
                 "Decrypted, type not recognised (a type the sniffer does not know, or bytes "
                 "a wrong key unpadded by chance); Did not decrypt; or Not decrypted (no "
                 "usable master key). File references are to Threema for Android at commit "
                 "d44a2b53 (see Threema - Contacts). Only ch.threema.app is present on the "
                 "test images in sample_data; group pictures, wallpapers and other files are "
                 "not exercised, an unreferenced message file only in the constructed case "
                 "casesynthetic_v2 (see Threema - Contacts; 5 rows); the case with no key "
                 "file was run on pixel7a_a14 with key.dat removed (8 files, none decrypted),"
                 " the case with no database on constructed paths only. Gallery folders: when "
                 "a message's media is saved to the gallery, by the user or automatically for"
                 " a received picture or video when the save-media setting is on and the chat"
                 " is not private (MessageServiceImpl.java L2608-L2634), the client copies "
                 "the decrypted message file, or its thumbnail where the file is gone, "
                 "unchanged into a shared storage folder named by the build's MEDIA_PATH (for"
                 " example Threema, ThreemaWork, ThreemaLibre; app/build.gradle.kts): "
                 "Pictures, Movies, Music, Documents or Download/<folder> from Android 10, "
                 "<folder>/Threema Pictures, Videos or Audio before it (FileServiceImpl.kt "
                 "L235-L345). The copy is requested under the message's stored file name, or "
                 "else threema-<local time>-<apiMessageId> plus an extension (FileUtil.java "
                 "L503-L517); before Android 10 the client adds ' (n)' to a name already "
                 "taken (common FileExtensions.kt L111-L122), and a type other than picture, "
                 "video or audio goes to the Download folder itself, which is not read. With "
                 "the same setting, pictures and videos taken in the app's own camera for "
                 "sending are saved there as threema-<local time>, without an apiMessageId "
                 "and from the source file (FileServiceImpl.kt L347-L355, "
                 "MessageServiceImpl.java L4368-L4379), so a blank 'Gallery Link' does not "
                 "show that a file did not come from Threema. These references describe "
                 "client 6.5.3 (commit d44a2b53); the test images run 4.59, 4.83 and 5.4.1. "
                 "The folders are shared storage: the user, a file manager or any app with "
                 "storage access can write to them, so a file there is not by itself a file "
                 "Threema wrote; which app wrote it is for the MediaStore artifacts "
                 "(owner_package_name in external.db), not this one. Each file in those "
                 "folders is listed for every install of the same Android user whose package"
                 " uses that folder, as Kind 'File in gallery folder', Storage 'Shared "
                 "storage (<folder>)' and Status 'Not encrypted'. It is not listed when the "
                 "extraction holds no database or user files of such an install, or when the "
                 "Android user cannot be read off its path. Only content ties such a file to "
                 "a message: 'Gallery Link' is 'Identical to the message file' or 'Identical "
                 "to the message thumbnail' when its SHA-256 equals that of exactly one "
                 "message's decrypted file or thumbnail, and only then are 'Belongs To', "
                 "'Message Created' and 'Message' the message's. A match shows that the bytes"
                 " are the same, not who copied them or when. A file whose bytes the files "
                 "of several messages share shows 'Identical to the files of <n> messages' "
                 "with Belongs To 'Several messages'. A name is not taken as a tie: the "
                 "stored file name comes from the sender's client, and the generic name has "
                 "the same shape as that of a picture from the app's camera. When an untied "
                 "file's name has the form threema-<date>-<time>-<id>, 'Gallery Link' gives "
                 "the id and how many messages in the database carry it as apiMessageId, as "
                 "a pointer only; the file is still not tied. Otherwise Belongs To is 'No "
                 "identical message file', or 'Not compared (no usable master key)' when no "
                 "key was read, and 'Database not opened' where the database was not opened "
                 "(a file can still be shown as identical to a message file when a key was "
                 "read). A file identical to a message file whose message is not in the "
                 "database shows 'Not referenced by the database', and a file whose message "
                 "file and thumbnail are both gone cannot be tied. On pixel7a_a14, "
                 "pixel3_a12 and hickman_a13 the one file in Pictures/Threema on each is "
                 "identical to a message file; the thumbnail, several messages, apiMessageId "
                 "pointer and untied cases are exercised only by unit tests, and "
                 "casesynthetic_v2 holds one identical file and one unrelated picture. On "
                 "pixel7a_a14 (9 rows), pixel3_a12 (5 rows) and hickman_a13 (7 rows) every "
                 "file except the one in the gallery folder is in external storage and "
                 "Decrypted, and on "
                 "pixel3_a12 'Belongs To' holds one value on all 5 rows, the one conversation"
                 " the files belong to.",
        "paths": (
            '*/ch.threema.app*/files/key.dat',
            '*/ch.threema.app*/files/master_key.dat',
            '*/ch.threema.app*/files/enc_master_key_v2.dat',
            '*/ch.threema.app*/databases/threema4.db*',
            '*/ch.threema.app*/shared_prefs/ch.threema.app*_preferences.xml',
            # The two user files directories; the code sorts their files by name.
            '*/ch.threema.app*/files/user-data/*',
            '*/Android/data/ch.threema.app*/files/data/*',
            # Gallery copies (FileServiceImpl.kt copyMediaFileToGallery): the public
            # directories hold one folder per MEDIA_PATH value, older Android one of its own.
            '*/Pictures/Threema*/*', '*/Movies/Threema*/*', '*/Music/Threema*/*',
            '*/Documents/Threema*/*', '*/Download/Threema*/*',
            '*/Threema*/Threema Pictures/*', '*/Threema*/Threema Videos/*',
            '*/Threema*/Threema Audio/*',
        ),
        "output_types": ["standard"],
        "artifact_icon": "image",
        "sample_data": {
            "pixel7a_a14": "Android 14 | Threema 5.4.1 (ch.threema.app) | 9 rows",
            "pixel3_a12": "Android 12 | Threema 4.59 (ch.threema.app) | 5 rows",
            "hickman_a13": "Android 13 | Threema 4.83 (ch.threema.app) | 7 rows",
        },
    },
}

import base64
import functools
import hashlib
import json
import os
import re
import sqlite3
import xml.etree.ElementTree as ET
from collections import namedtuple
from datetime import datetime, timezone

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from scripts.ilapfuncs import (artifact_processor, check_in_embedded_media,
                               get_sqlite_db_path, logfunc)
from scripts.artifacts.storagePathViews import unique_files
from scripts.filetype import guess_mime

try:
    from sqlcipher3 import dbapi2 as sqlcipher
    _SQLCIPHER_AVAILABLE = True
    _DB_ERRORS = (sqlite3.Error, sqlcipher.Error)  # pylint: disable=no-member
except ImportError as _sqlcipher_import_error:
    # Without this guard a missing sqlcipher3 install would raise at
    # module-import time and abort loading of ALL ALEAPP artifacts, not just
    # these two - see browserArtifactsViaMisterSkinnylegs.py for the same
    # pattern already established in this project.
    _SQLCIPHER_AVAILABLE = False
    _DB_ERRORS = (sqlite3.Error,)
    logfunc(f"Threema: sqlcipher3 not available, encrypted-database "
            f"artifacts disabled: {_sqlcipher_import_error}")

_INVALID_XML_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
# Some binary values (e.g. a Threema Safe backup hash) get written out as
# per-byte numeric character references, including control-code bytes that
# are syntactically well-formed XML entities but not valid XML characters
# (only tab/LF/CR are valid below 0x20) - ElementTree rejects the whole file
# for these the same as it would a raw control byte, so they need the same
# stripping, just matched in their &#N; / &#xN; encoded form instead.
_INVALID_XML_NUMERIC_REF = re.compile(r'&#x?[0-9a-fA-F]+;')

# Threema and its build flavours (Libre, Work, OnPrem, HMS) share one client
# source and differ only in this package name.
_PACKAGE = re.compile(r'^ch\.threema\.app(?:\.[a-z0-9_]+)*$')
# Where an Android user id can be read off the directory above the package.
_INTERNAL_USER = (
    (re.compile(r'(?:^|/)data/data$'), None),
    (re.compile(r'(?:^|/)data/user(?:_de)?/(\d+)$'), 1),
    (re.compile(r'(?:^|/)data_mirror/data_(?:ce|de)/[^/]+/(\d+)$'), 1),
)
_EXTERNAL_USER = (
    (re.compile(r'(?:^|/)data/media/(\d+)/Android/data$'), 1),
    (re.compile(r'(?:^|/)storage/emulated/(\d+)/Android/data$'), 1),
    (re.compile(r'(?:^|/)(?:sdcard|storage/self/primary)/Android/data$'), None),
)
# '.' + the message uid, a UUID, with every non-alphanumeric character
# removed, '_T' for the thumbnail (MessageFileHandleProvider.kt).
_MEDIA_NAME = re.compile(r'^\.([0-9A-Fa-f]{32})(_T)?$')
# The gallery folder each flavour writes to (MEDIA_PATH, app/build.gradle.kts L97, L242,
# L273, L308, L362, L412, L462, L492) and the packages that use it.
_GALLERY_PACKAGES = {
    'Threema': ('ch.threema.app', 'ch.threema.app.hms'),
    'ThreemaWork': ('ch.threema.app.work', 'ch.threema.app.work.hms'),
    'ThreemaGreen': ('ch.threema.app.green',),
    'ThreemaWorkSandbox': ('ch.threema.app.sandbox.work',),
    'ThreemaOnPrem': ('ch.threema.app.onprem',),
    'ThreemaBlue': ('ch.threema.app.red',),
    'ThreemaLibre': ('ch.threema.app.libre',),
}
# copyMediaFileIntoPublicDirectory (FileServiceImpl.kt L235-L300): Android 10 and later
# put the copy in <public directory>/<MEDIA_PATH>/ (L254-L276), older Android
# (getPublicDirectory, L303-L312) in <storage>/<MEDIA_PATH>/Threema Pictures, Videos or
# Audio, and any other type in the Download folder itself, which is not read here.
_GALLERY_PUBLIC_DIRS = ('Pictures', 'Movies', 'Music', 'Documents', 'Download')
_GALLERY_LEGACY_DIRS = ('Threema Pictures', 'Threema Videos', 'Threema Audio')
_SHARED_STORAGE_USER = (
    (re.compile(r'(?:^|/)data/media/(\d+)$'), 1),
    (re.compile(r'(?:^|/)storage/emulated/(\d+)$'), 1),
    (re.compile(r'(?:^|/)(?:sdcard|storage/self/primary)$'), None),
)
# FileUtil.getMediaFilenamePrefix (FileUtil.java L503-L507): a copy of a message without a
# file name is named threema-<local time>-<apiMessageId>; the form without a message
# (L509-L512, used for camera media) carries no id.
_GALLERY_API_NAME = re.compile(r'^threema-\d{8}-\d{6}-([0-9A-Za-z]+)')


def _strip_invalid_numeric_refs(text):
    def _replace(match):
        ref = match.group(0)
        try:
            if ref[2:3] in ('x', 'X'):
                code_point = int(ref[3:-1], 16)
            else:
                code_point = int(ref[2:-1])
        except ValueError:
            return ref
        is_valid = (code_point in (0x09, 0x0A, 0x0D)
                    or 0x20 <= code_point <= 0xD7FF
                    or 0xE000 <= code_point <= 0xFFFD
                    or 0x10000 <= code_point <= 0x10FFFF)
        return ref if is_valid else ''
    return _INVALID_XML_NUMERIC_REF.sub(_replace, text)

# Fixed 32-byte XOR mask applied to a version-1 key.dat's stored key bytes,
# reverse engineered from github.com/wilzbach/threema-decrypt's cmg_clean.java
# and verified against this device's real key.dat (the file's own trailing
# SHA-1 checksum matched the derived key exactly).
_KEY_DAT_XOR_MASK = bytes([
    149, 13, 38, 122, 136, 234, 119, 16, 156, 80, 231, 63, 71, 224, 105, 114,
    218, 196, 57, 124, 153, 234, 126, 103, 175, 253, 221, 50, 218, 53, 247, 12,
])


def _parse_xml(file_found):
    try:
        return ET.parse(file_found).getroot()
    except ET.ParseError:
        try:
            with open(file_found, encoding='utf-8', errors='replace') as f:
                cleaned = _strip_invalid_numeric_refs(
                    _INVALID_XML_CHARS.sub('', f.read()))
            return ET.fromstring(cleaned)
        except ET.ParseError as ex:
            logfunc(f'Threema: could not parse {file_found}: {ex}')
            return ET.Element('empty')


def _xml_value(root, name):
    node = root.find(f".//*[@name='{name}']")
    if node is None:
        return None
    return node.get('value', node.text)


def _epoch_ms_to_utc(value):
    try:
        return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return None


# --- Containers -------------------------------------------------------------

# The client's user files directories (AppDirectoryProvider.kt and the file
# handle providers beside it): files/user-data/<dir>/ in the app's data
# directory, falling back to files/data/<legacy dir>/ in its external
# storage directory; message files sit directly in files/data/ there.
_CURRENT_MEDIA_DIRS = {'.message-files': 'media', '.profile-pictures': 'avatars',
                       '.group-profile-pictures': 'groups', '.wallpapers': 'wallpapers'}
_LEGACY_MEDIA_DIRS = {'.avatar': 'avatars', '.grp-avatar': 'groups', '.wallpaper': 'wallpapers'}
_MEDIA_CATEGORIES = ('media', 'avatars', 'groups', 'wallpapers', 'other')
_STORAGE_LABELS = {'internal': 'App data', 'external': 'External storage'}
_APP_DATA_FILES = {('files', 'key.dat'): 'key_v1', ('files', 'master_key.dat'): 'key_v2',
                   ('files', 'enc_master_key_v2.dat'): 'key_v2_keystore',
                   ('databases', 'threema4.db'): 'db'}


def _user_file(rest, legacy):
    """(category, name) of a file below a user files directory, given its path
    below that directory. A name the client's file handle providers do not
    define is category 'other'. Profile pictures and wallpapers in the
    legacy directory carry a '.nomedia' suffix the current one does not use."""
    if rest == ['wallpaper.jpg']:
        return 'wallpapers', rest[0]
    if legacy and len(rest) == 1 and _MEDIA_NAME.match(rest[0]):
        return 'media', rest[0]
    directories = _LEGACY_MEDIA_DIRS if legacy else _CURRENT_MEDIA_DIRS
    if len(rest) == 2 and rest[0] in directories:
        category = directories[rest[0]]
        name = rest[1].removesuffix('.nomedia') if legacy else rest[1]
        if category != 'media' or _MEDIA_NAME.match(name):
            return category, name
    return 'other', '/'.join(rest)


def _android_user(above, patterns):
    """The Android user id read off the directory above the package, or None."""
    for pattern, group in patterns:
        match = pattern.search(above)
        if match:
            return match.group(group) if group else '0'
    return None


def _locate(path):
    """(container key, kind, name) for a Threema file, or None.

    The container key is (Android user, package) wherever the user can be read
    off the path, so the app data directory and the external storage directory
    of one install pair up and another user's or flavour's install stays
    apart. Where the user cannot be read, the key is the directory itself and
    nothing pairs with it across storage areas.
    """
    parts = str(path).replace('\\', '/').split('/')
    index = next((i for i, part in enumerate(parts) if _PACKAGE.match(part)), None)
    if index is None:
        return None
    package, above, rest = parts[index], '/'.join(parts[:index]), parts[index + 1:]

    # The user files directories: files/data/ in the app's external storage
    # directory (the legacy one), files/user-data/ in its app data directory.
    if rest[:2] == ['files', 'data'] and len(rest) > 2:
        category, name = _user_file(rest[2:], legacy=True)
        kind, patterns = ('external', category), _EXTERNAL_USER
    elif rest[:2] == ['files', 'user-data'] and len(rest) > 2:
        category, name = _user_file(rest[2:], legacy=False)
        kind, patterns = ('internal', category), _INTERNAL_USER
    elif rest == ['shared_prefs', f'{package}_preferences.xml']:
        kind, name, patterns = 'prefs', None, _INTERNAL_USER
    elif tuple(rest) in _APP_DATA_FILES:
        kind, name, patterns = _APP_DATA_FILES[tuple(rest)], None, _INTERNAL_USER
    else:
        return None

    user = _android_user(above, patterns)
    if user is None and patterns is _EXTERNAL_USER and _android_user(above, _INTERNAL_USER):
        # files/data/ inside the app data directory is not the client's
        # legacy user files directory.
        return None
    key = (user, package) if user is not None else ('?', '/'.join(parts[:index + 1]))
    return key, kind, name


def _new_container(key):
    user, package = key
    if user == '?':
        package = package.rsplit('/', 1)[-1]
    return ({'user': user, 'package': package, 'files': [], 'gallery': []}
            | {c: {} for c in _MEDIA_CATEGORIES})


def _locate_gallery(path):
    """(Android user, gallery folder, its label, file name) for a file in a Threema
    gallery folder of shared storage, or None."""
    parts = str(path).replace('\\', '/').split('/')
    if len(parts) < 4:
        return None
    above, folder, name = parts[:-3], parts[-3:-1], parts[-1]
    if folder[0] in _GALLERY_PUBLIC_DIRS and folder[1] in _GALLERY_PACKAGES:
        flavour = folder[1]
    elif folder[0] in _GALLERY_PACKAGES and folder[1] in _GALLERY_LEGACY_DIRS:
        flavour = folder[0]
    else:
        return None
    user = _android_user('/'.join(above), _SHARED_STORAGE_USER)
    if user is None:
        return None
    return user, flavour, '/'.join(folder), name


def _containers(files_found):
    """{container key: {'user', 'package', kind: path, category: {name: path}, 'files': [...]}}.

    For lookups by name a file in the app data directory is preferred over
    the external storage copy of the same name, the order the client itself
    reads them in; 'files' keeps every file found, with its storage area.
    """
    containers = {}
    external = []
    gallery = []
    for file_found in files_found:
        # The user files globs also match the directories inside them.
        if os.path.isdir(file_found):
            continue
        located = _locate(file_found)
        if located is None:
            in_gallery = _locate_gallery(file_found)
            if in_gallery:
                gallery.append((in_gallery, str(file_found)))
            continue
        key, kind, name = located
        entry = containers.setdefault(key, _new_container(key))
        if isinstance(kind, tuple) and kind[0] == 'internal':
            entry[kind[1]][name] = str(file_found)
            entry['files'].append((kind[1], name, str(file_found), 'internal'))
        elif isinstance(kind, tuple):
            external.append((key, kind[1], name, str(file_found)))
        else:
            entry.setdefault(kind, str(file_found))
    for key, category, name, path in external:
        containers[key][category].setdefault(name, path)
        containers[key]['files'].append((category, name, path, 'external'))
    # A gallery copy goes to the installs of its Android user that write to its folder;
    # _gallery_links decides which message, if any, it is a copy of.
    for (user, flavour, label, name), path in sorted(gallery, key=lambda g: g[1]):
        for container in containers.values():
            if container['user'] == user and container['package'] in _GALLERY_PACKAGES[flavour]:
                container['gallery'].append((name, label, path))
    return containers


def _profile_picture_name(prefix, identity):
    """prefix + Base32(SHA-256('c-' + identity)) without padding, the client's
    file name for a profile picture (ProfilePictureFileHandleProvider.kt):
    '.c-' set by the local user (for the account's own identity, its own
    picture), '.p-' set by the contact, '.a-' taken from the Android contact."""
    digest = hashlib.sha256(f'c-{identity}'.encode()).digest()
    return prefix + base64.b32encode(digest).decode().rstrip('=')


def _profile_picture(container, identity, prefix):
    """The media reference of one stored profile picture, or ''. Only bytes
    that decrypt to an image are taken."""
    if not identity:
        return ''
    name = _profile_picture_name(prefix, identity)
    path = container['avatars'].get(name)
    if not path:
        return ''
    data, mime = _decrypt_file(path, _keys(container))
    if not (mime or '').startswith('image/'):
        logfunc(f"Threema: profile picture {name} did not decrypt to an image with any key file.")
        return ''
    return check_in_embedded_media(path, data, f'{identity}{prefix.rstrip("-")}') or ''


# --- Master key -------------------------------------------------------------

def _derive_sqlcipher_key(key_dat_path):
    """Unwrap a version-1 Threema key.dat into the raw 32-byte master key.

    Format (all fixed-size, 45 bytes total): 1-byte protection flag, 32-byte
    XOR-masked key, 8 reserved bytes, 4-byte SHA-1(key)[:4] checksum. Returns
    None (logging why) if the file is passphrase-protected, the wrong size,
    or its own checksum does not verify - never a guessed/partial key.
    """
    with open(key_dat_path, 'rb') as f:
        raw = f.read()

    if len(raw) != 45:
        logfunc(f"Threema: key.dat is {len(raw)} bytes, expected 45 for the "
                f"version-1 format; skipping.")
        return None

    protected = raw[0] != 0
    if protected:
        logfunc("Threema: key.dat is passphrase-protected; this module only "
                "supports the unprotected case, skipping.")
        return None

    masked_key = raw[1:33]
    checksum = raw[41:45]
    key = bytes(k ^ m for k, m in zip(masked_key, _KEY_DAT_XOR_MASK))

    if hashlib.sha1(key).digest()[:4] != checksum:
        logfunc("Threema: key.dat checksum did not verify; derived key "
                "rejected rather than used unverified.")
        return None

    return key


def _read_varint(buf, offset):
    value = shift = 0
    while offset < len(buf):
        byte = buf[offset]
        offset += 1
        value |= (byte & 0x7f) << shift
        if not byte & 0x80:
            return value, offset
        shift += 7
    raise ValueError('truncated varint')


def _v2_layer(buf, layer):
    """One layer of a version 2 key file: a 2-byte big-endian version (0 is
    the only one defined) and a protobuf holding exactly one length-delimited
    field. Returns (field number, field bytes)."""
    if len(buf) < 3:
        raise ValueError(f'{layer} layer is {len(buf)} bytes')
    version = int.from_bytes(buf[:2], 'big')
    if version != 0:
        raise ValueError(f'{layer} layer has version {version}')
    tag, offset = _read_varint(buf, 2)
    if tag & 7 != 2:
        raise ValueError(f'{layer} layer field is not length-delimited')
    length, offset = _read_varint(buf, offset)
    if offset + length != len(buf):
        raise ValueError(f'{layer} layer length does not match the file')
    return tag >> 3, buf[offset:offset + length]


def _read_v2_master_key(path):
    """The master key from an unprotected version 2 master_key.dat, or None
    (logging why). Layers per key-storage.proto: outer field 1 plaintext
    intermediate / 2 passphrase-protected; intermediate field 1 plaintext
    inner / 2 remote-secret-protected; inner field 1 the master key."""
    with open(path, 'rb') as f:
        raw = f.read()
    try:
        field, intermediate = _v2_layer(raw, 'outer')
        if field == 2:
            logfunc("Threema: master_key.dat is passphrase-protected; skipping.")
            return None
        field, inner = _v2_layer(intermediate, 'intermediate')
        if field == 2:
            logfunc("Threema: master_key.dat is remote-secret-protected; skipping.")
            return None
        field, key = _v2_layer(inner, 'inner')
    except (ValueError, IndexError) as ex:
        logfunc(f"Threema: master_key.dat not in the expected format ({ex}); skipping.")
        return None
    if field != 1 or len(key) != 32:
        logfunc(f"Threema: master_key.dat inner layer holds field {field} of "
                f"{len(key)} bytes, expected a 32-byte master key; skipping.")
        return None
    return key


def _master_key_candidates(container):
    candidates = []
    if 'key_v2' in container:
        key = _read_v2_master_key(container['key_v2'])
        if key is not None:
            candidates.append(key)
    if 'key_v1' in container:
        key = _derive_sqlcipher_key(container['key_v1'])
        if key is not None:
            candidates.append(key)
    if not candidates:
        if 'key_v2_keystore' in container:
            logfunc(f"Threema: {container['package']} has only enc_master_key_v2.dat, which "
                    f"the Android key store protects; its database and files stay undecrypted.")
        elif 'key_v1' not in container and 'key_v2' not in container:
            logfunc(f"Threema: {container['package']} has no key file; its database and "
                    f"files stay undecrypted.")
    return candidates


def _keys(container):
    """The container's master key candidates, read from its key files once.
    Each file and the database is tried with every candidate, since nothing
    guarantees that all of them were encrypted with the same key."""
    if 'keys' not in container:
        container['keys'] = _master_key_candidates(container)
    return container['keys']


def _open_decrypted_db(db_path, key):
    """Open threema4.db read-only through the master key. Returns a live
    connection on success, or None (logging why) on failure - an unverified
    or wrong key fails here with a clear SQLCipher error rather than silently
    returning garbage, since SQLCipher HMAC-checks every page it decrypts.

    Opened via a read-only file: URI (the same helper and URI form used
    project-wide by scripts.ilapfuncs.open_sqlite_db_readonly) rather than a
    plain path, so evidence is never at risk of being modified, while still
    letting SQLite fold in any not-yet-checkpointed write-ahead log content
    sitting alongside the file - which on the device this was validated
    against held real content the main file alone did not.
    """
    try:
        uri = f"file:{get_sqlite_db_path(db_path)}?mode=ro"
        con = sqlcipher.connect(uri, uri=True)  # pylint: disable=no-member
        cur = con.cursor()
        cur.execute(f"PRAGMA key = 'x\"{key.hex()}\"';")
        # Threema's own DatabaseOpenHelper sets the KDF iteration count to 1.
        cur.execute("PRAGMA kdf_iter = 1;")
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1;")
        cur.fetchall()
        return con
    except Exception as ex:  # pylint: disable=broad-exception-caught
        logfunc(f"Threema: could not open threema4.db with the derived key: {ex}")
        return None


# One app container as the artifacts see it: the open database connection,
# None where it could not be opened, and the container's files by kind (see
# _containers).
_Store = namedtuple('_Store', 'connection container')


def _decrypted_connections(files_found, include_without_db=False):
    """A _Store per app container, sorted by database path.

    An extraction can carry a container per Android user and per Threema
    flavour, each with its own key file and threema4.db. The pairing stays
    inside one container: a database only opens with the key file next to
    it, never another user's. A container whose key does not derive, or that
    has no usable key file, still reports its db path, so the report cites
    the store that could not be opened. With include_without_db, a container
    holding user files but no database is returned too, unopened.
    """
    if not _SQLCIPHER_AVAILABLE:
        return []
    stores = []
    for container in sorted(_containers(files_found).values(), key=lambda c: c.get('db', '')):
        if 'db' not in container:
            if include_without_db and container['files']:
                logfunc(f"Threema: files of {container['package']} with no threema4.db "
                        f"beside them; what they belong to is not resolved.")
                stores.append(_Store(None, container))
            continue
        con = None
        for key in _keys(container):
            con = _open_decrypted_db(container['db'], key)
            if con is not None:
                break
        stores.append(_Store(con, container))
    return stores


def _source_paths(stores):
    """The stores' databases, newline-joined for the artifact's source line;
    a store without a database cites its files."""
    paths = []
    for store in stores:
        if 'db' in store.container:
            paths.append(store.container['db'])
        else:
            paths.extend(path for _, _, path, _ in store.container['files'])
    return '\n'.join(paths)


# --- Schema-tolerant reads --------------------------------------------------

def _table_columns(cur, table):
    try:
        return {row[1] for row in cur.execute(f'PRAGMA table_info("{table}")')}
    except _DB_ERRORS:
        return set()


def _select(cur, table, columns, order_by=None, present=None):
    """Rows of table as dicts with every requested column; one this schema
    does not have is None rather than an error. present is the table's
    columns where the caller has already read them."""
    if present is None:
        present = _table_columns(cur, table)
    if not present:
        logfunc(f"Threema: no {table} table in this database.")
        return []
    missing = [c for c in columns if c not in present]
    if missing:
        logfunc(f"Threema: {table} has no {', '.join(missing)} in this schema; "
                f"reported blank.")
    exprs = ', '.join(f'"{c}"' if c in present else 'NULL' for c in columns)
    sql = f'SELECT {exprs} FROM "{table}"'
    if order_by in present:
        sql += f' ORDER BY "{order_by}"'
    try:
        return [dict(zip(columns, row)) for row in cur.execute(sql)]
    except _DB_ERRORS as ex:
        logfunc(f"Threema: could not read {table}: {ex}")
        return []


_VERIFICATION_LEVELS = {
    0: "Unverified",
    1: "Server-verified",
    2: "Fully verified",
}


@artifact_processor
def threema_account(context):
    data_headers = ("Threema ID", "Nickname", "Linked Mobile Number", "Package",
                    ("Profile Picture", "media"))

    files_found = unique_files(context)
    containers = [c for c in _containers(files_found).values() if 'prefs' in c]
    if not containers:
        return data_headers, [], ""

    data_list = []
    prefs = sorted(c['prefs'] for c in containers)
    for container in sorted(containers, key=lambda c: c['prefs']):
        root = _parse_xml(container['prefs'])
        identity = _xml_value(root, 'identity') or ''
        nickname = _xml_value(root, 'nickname') or ''
        linked_mobile = _xml_value(root, 'linked_mobile') or ''

        if not identity:
            continue

        picture = _profile_picture(container, identity, '.c-')
        logfunc(f"Threema Account: ID {identity} recovered.")
        data_list.append((identity, nickname, linked_mobile, container['package'], picture))

    return data_headers, data_list, '\n'.join(prefs)


@artifact_processor
def threema_contacts(context):
    data_headers = (
        ("Date Created", "datetime"), "Threema ID", "Display Name", "Verification Level",
        "Group-Only / Removed", "Archived",
        ("Profile Picture (from contact)", "media"), ("Profile Picture (set locally)", "media"),
        ("Profile Picture (Android contact)", "media"),
    )

    files_found = unique_files(context)
    stores = _decrypted_connections(files_found)
    if not stores:
        return data_headers, [], ""

    data_list = []
    for con, container in stores:
        if con is None:
            continue
        try:
            cur = con.cursor()
            present = _table_columns(cur, 'contacts')
            # acquaintanceLevel from schema version 94, isHidden before it.
            acquaintance_column = 'acquaintanceLevel' if 'acquaintanceLevel' in present else 'isHidden'
            # isArchived until schema version 126, conversationVisibility
            # (1 = archived) from it.
            archived_column = ('conversationVisibility' if 'conversationVisibility' in present
                               else 'isArchived')
            rows = _select(cur, 'contacts', (
                'identity', 'firstName', 'lastName', 'publicNickName',
                'verificationLevel', 'dateCreated', acquaintance_column, archived_column),
                present=present)
            for row in rows:
                level = row['verificationLevel']
                acquaintance = row[acquaintance_column]
                archived = (row[archived_column] == 1 if archived_column == 'conversationVisibility'
                            else bool(row[archived_column]))
                data_list.append((
                    _epoch_ms_to_utc(row['dateCreated']),
                    row['identity'],
                    _display_name(row),
                    _VERIFICATION_LEVELS.get(level, str(level)),
                    "Yes" if acquaintance else "",
                    "Yes" if archived else "",
                    _profile_picture(container, row['identity'], '.p-'),
                    _profile_picture(container, row['identity'], '.c-'),
                    _profile_picture(container, row['identity'], '.a-'),
                ))
        finally:
            con.close()

    data_list.sort(key=lambda row: (row[0] is None, row[0]))
    logfunc(f"Threema Contacts: {len(data_list)} contact(s) recovered from "
            f"the decrypted database.")
    return data_headers, data_list, _source_paths(stores)


def _display_name(row):
    return (" ".join(p for p in (row.get('firstName'), row.get('lastName')) if p)
            or row.get('publicNickName') or '')


# --- Message bodies ---------------------------------------------------------

def _json_list(body):
    try:
        parts = json.loads(body)
    except (ValueError, TypeError):
        return []
    return parts if isinstance(parts, list) else []


def _part(parts, index, kind):
    """parts[index] if it exists and is of kind; a bool never counts as a
    number, since JSON true/false load as Python bools."""
    if index >= len(parts):
        return None
    value = parts[index]
    if isinstance(value, bool) and kind is not bool:
        return None
    return value if isinstance(value, kind) else None


def _number(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _file_info(body):
    """(file name, MIME type, size, caption, duration) of a type 8 body, by
    the positions FileDataModelSerializer writes. Bodies written before the
    rendering type existed hold the downloaded flag at position 5 and every
    later value one position earlier, which the 5.8.2 reader (FileDataModel.
    java) skipped over; the current reader no longer does."""
    parts = _json_list(body)
    shift = 1 if isinstance(_part(parts, 5, bool), bool) else 0
    metadata = _part(parts, 9 - shift, dict) or {}
    duration = _number(metadata.get('d'))
    return (_part(parts, 4, str) or '', _part(parts, 2, str) or '',
            _part(parts, 3, int), _part(parts, 7 - shift, str) or '',
            round(duration) if duration is not None else None)


def _location_info(body):
    """Latitude/longitude/accuracy/address of a static location message,
    by the fixed [latitude, longitude, accuracy, address, ...] shape every
    location message observed showed; each field is still type-checked."""
    parts = _json_list(body)
    lat, lon = _part(parts, 0, (int, float)), _part(parts, 1, (int, float))
    if lat is None or lon is None:
        return None, None, None, ''
    return lat, lon, _part(parts, 2, (int, float)), _part(parts, 3, str) or ''


def _status_params(body):
    """(status model type, parameters) of a [type, {parameters}] status body.
    A body without the leading type yields (None, parameters)."""
    parts = _json_list(body)
    params = next((p for p in parts if isinstance(p, dict)), {})
    return _part(parts, 0, int), params


_CALL_STATUS = {1: 'Missed', 2: 'Finished', 3: 'Rejected', 4: 'Aborted'}
_GROUP_CALL_STATUS = {1: 'Group call started', 2: 'Group call ended'}
_FORWARD_SECURITY_STATUS = {
    0: 'Static text',
    1: 'Message without forward security',
    2: 'Forward security reset',
    3: 'Forward security established',
    4: 'Forward security established (received)',
    5: 'Forward security messages skipped',
    6: 'Forward security message out of order',
    7: 'Forward security unavailable (downgrade)',
    8: 'Forward security illegal session state',
    9: 'Forward security disabled',
}
_GROUP_STATUS = {
    0: 'Group created', 1: 'Group renamed', 2: 'Group picture updated',
    3: 'Member added', 4: 'Member left', 5: 'Member kicked', 6: 'Notes group',
    7: 'People group', 8: 'First vote', 9: 'Vote modified', 10: 'Vote received',
    11: 'Votes complete', 12: 'Group description changed', 13: 'Group orphaned',
}
_MEDIA_TYPES = {1, 2, 3, 8}


def _decode(mtype, body, caption):
    """The content fields of one message row. 'text' is the original
    'Text / Filename / Address' column (the text, the file name or the
    address); 'message' is what the row shows in a chat, so for a file it is
    the caption and for a call or status row the notice."""
    out = {'content_type': 'Text', 'text': '', 'mime': '', 'size': None,
           'lat': None, 'lon': None, 'accuracy': None, 'call_status': None,
           'call_id': None, 'call_duration': None, 'message': '',
           'media_duration': None}
    caption = caption or ''
    if mtype == 0:
        out['text'] = out['message'] = body or ''
    elif mtype == 1:
        out['content_type'] = 'Image'
        out['message'] = caption
    elif mtype in (2, 3):
        parts = _json_list(body)
        out['content_type'] = 'Video' if mtype == 2 else 'Voice Message'
        out['media_duration'] = _part(parts, 0, int)
        if mtype == 2:
            out['size'] = _part(parts, 4, int)
        out['message'] = caption
    elif mtype == 4:
        out['content_type'] = 'Location'
        out['lat'], out['lon'], out['accuracy'], out['text'] = _location_info(body)
        out['message'] = out['text']
    elif mtype == 8:
        out['content_type'] = 'File'
        filename, out['mime'], out['size'], body_caption, out['media_duration'] = _file_info(body)
        out['text'] = filename
        out['message'] = caption or body_caption
    elif mtype == 9:
        out['content_type'] = 'Call'
        _, params = _status_params(body)
        status = params.get('status')
        # Call Status keeps the stored value; Message carries its name.
        out['call_status'] = status
        out['call_id'] = params.get('callId')
        out['call_duration'] = params.get('duration')
        out['message'] = (f"Call {_CALL_STATUS.get(status, status)}" if status is not None
                          else 'Call')
        if out['call_duration'] is not None:
            out['message'] += f" ({out['call_duration']} s)"
    elif mtype in (11, 12, 13):
        _, params = _status_params(body)
        status = params.get('status')
        names = {11: _GROUP_CALL_STATUS, 12: _FORWARD_SECURITY_STATUS, 13: _GROUP_STATUS}[mtype]
        out['content_type'] = {11: 'Group Call Status', 12: 'Forward Security Status',
                               13: 'Group Status'}[mtype]
        label = names.get(status, f'Status {status}')
        details = [str(params[k]) for k in ('staticText', 'identity', 'newGroupName', 'ballotName')
                   if params.get(k)]
        if params.get('quantity'):
            details.append(str(params['quantity']))
        out['text'] = out['message'] = label + (f": {', '.join(details)}" if details else '')
    else:
        out['content_type'] = f"Unrecognized (type={mtype})"
        out['text'] = out['message'] = body or ''
    return out


def _decrypt_media(path, key):
    """The plaintext of a Threema media file (AES-CBC, 16-byte IV in front,
    PKCS#7 padding), or None if it does not decrypt."""
    try:
        with open(path, 'rb') as f:
            raw = f.read()
    except OSError as ex:
        logfunc(f"Threema: could not read media file {path}: {ex}")
        return None
    if len(raw) < 32 or (len(raw) - 16) % 16:
        return None
    try:
        return unpad(AES.new(key, AES.MODE_CBC, raw[:16]).decrypt(raw[16:]), 16)
    except ValueError:
        return None


def _decrypt_file(path, keys):
    """(plaintext, MIME type) of a Threema user file, trying every key.

    A key whose plaintext has a recognised file type wins. Otherwise the
    first key whose plaintext unpads is taken with MIME type None: the file
    may be of a type the sniffer does not know, or a wrong key may have
    unpadded it by chance, about once in 256 tries. (None, None) when no key
    decrypts it."""
    fallback = None
    for key in keys:
        data = _decrypt_media(path, key)
        if data is None:
            continue
        mime = guess_mime(data)
        if mime:
            return data, mime
        if fallback is None:
            fallback = data
    return fallback, None


def _media_for(uid, container, filename):
    """(media reference or '', Media Status) for one media message."""
    if not uid:
        return '', 'Not on device'
    stem = '.' + re.sub(r'[^A-Za-z0-9]', '', uid)
    found = False
    for name, status in ((stem, 'File'), (stem + '_T', 'Thumbnail only')):
        path = container['media'].get(name)
        if not path:
            continue
        found = True
        data, mime = _decrypt_file(path, _keys(container))
        if data is None:
            logfunc(f"Threema: media file {name} did not decrypt with any key file.")
            continue
        ref = check_in_embedded_media(path, data, filename or name.lstrip('.'))
        if ref:
            return ref, status if mime else f'{status} (type not recognised)'
    return '', 'Decryption failed' if found else 'Not on device'


def _gallery_links(container, rows):
    """{gallery file path: (message stem or None, link text, shared by several)} for the
    container's files in gallery folders. Only content ties a file to a message: it is
    byte identical to one message's decrypted file or thumbnail (copyMediaFileToGallery
    copies either unchanged). A file whose bytes several messages share is reported as
    such and tied to none. A name is never taken as a tie, since anything with access to
    shared storage can write one; an apiMessageId in an untied file's name is only
    reported, with how many messages carry it. rows are message rows with uid and
    apiMessageId, or None when the database was not opened."""
    if not container.get('gallery'):
        return {}
    by_api = {}
    for row in rows or []:
        if row.get('uid') and row.get('apiMessageId'):
            by_api.setdefault(str(row['apiMessageId']).lower(), set()).add(row['uid'])
    hashes = {}
    keys = _keys(container)
    for name, path in sorted(container['media'].items()):
        match = _MEDIA_NAME.match(name)
        data, _ = _decrypt_file(path, keys) if match else (None, None)
        if data is not None:
            hashes.setdefault(hashlib.sha256(data).digest(), set()).add(
                (match.group(1), bool(match.group(2))))
    links = {}
    for name, _label, path in container['gallery']:
        try:
            with open(path, 'rb') as f:
                digest = hashlib.sha256(f.read()).digest()
        except OSError as ex:
            logfunc(f"Threema: could not read gallery file {path}: {ex}")
            digest = None
        found = hashes.get(digest, set())
        found_stems = {stem for stem, _thumb in found}
        api = _GALLERY_API_NAME.match(name)
        if len(found_stems) == 1:
            stem = next(iter(found_stems))
            thumb_only = all(thumb for _stem, thumb in found)
            links[path] = (stem, 'Identical to the message thumbnail' if thumb_only
                           else 'Identical to the message file', False)
        elif found_stems:
            links[path] = (None, f'Identical to the files of {len(found_stems)} messages',
                           True)
        elif api:
            text = f'Name carries apiMessageId {api.group(1)}'
            if rows is not None:
                carriers = len(by_api.get(api.group(1).lower(), ()))
                text += (f', that of {carriers} message' + ('s' if carriers > 1 else '')
                         if carriers else ', that of no message in the database')
            links[path] = (None, text + '; not tied', False)
        else:
            links[path] = (None, '', False)
    return links


def _name_of(identity, own_identity, own, contacts):
    """How an identity is shown: the local account's label for its own
    Threema ID, else the contact's name, else the identity itself."""
    if identity and identity == own_identity:
        return own
    return contacts.get(identity, identity or '')


def _own_account(container):
    """(own Threema ID or '', how the local account is shown)."""
    prefs = container.get('prefs')
    if not prefs:
        return '', 'Local account'
    root = _parse_xml(prefs)
    identity = _xml_value(root, 'identity') or ''
    nickname = _xml_value(root, 'nickname') or ''
    if identity and nickname:
        return identity, f"{nickname} ({identity})"
    return identity, identity or 'Local account'


# MessageState.java: a deprecated thumbs up / thumbs down "sent by the
# recipient" of the message, kept on the message row before reaction tables.
_LEGACY_REACTION_STATES = {'USERACK': '\U0001F44D', 'USERDEC': '\U0001F44E'}


def _reactions(cur, single, group, name_of):
    """{(is group, message row id): ['emoji sender (time)', ...]} from the
    reaction tables: contact_/group_reactions keyed by message id (schema
    version 106 on), contact_/group_emoji_reactions keyed by message uid
    (version 105, which 106 copies into the former)."""
    by_uid = {(False, r['uid']): r['id'] for r in single if r['uid']}
    by_uid.update({(True, r['uid']): r['id'] for r in group if r['uid']})
    created = {(False, r['id']): r['createdAtUtc'] for r in single}
    created.update({(True, r['id']): r['createdAtUtc'] for r in group})
    found = {}
    for is_group, table, legacy in ((False, 'contact_reactions', 'contact_emoji_reactions'),
                                    (True, 'group_reactions', 'group_emoji_reactions')):
        rows = []
        present = _table_columns(cur, table)
        legacy_present = _table_columns(cur, legacy) if not present else set()
        if present:
            rows = [(r['messageId'], r) for r in _select(cur, table, (
                'messageId', 'senderIdentity', 'emojiSequence', 'reactedAt'),
                order_by='reactedAt', present=present)]
        elif legacy_present:
            rows = [(by_uid.get((is_group, r['messageUid'])), r) for r in _select(cur, legacy, (
                'messageUid', 'senderIdentity', 'emojiSequence', 'reactedAt'),
                order_by='reactedAt', present=legacy_present)]
        for message_id, r in rows:
            if message_id is None:
                continue
            when = _epoch_ms_to_utc(r['reactedAt'])
            text = f"{r['emojiSequence'] or ''} {name_of(r['senderIdentity'])}".strip()
            if r['reactedAt'] is not None and r['reactedAt'] == created.get((is_group, message_id)):
                # A converted thumbs up/down takes the message's own time
                # (EmojiReactionsRepository.createEmojiReactionData).
                text += " (no reaction time stored)"
            elif when:
                text += f" ({when:%Y-%m-%d %H:%M:%S} UTC)"
            found.setdefault((is_group, message_id), []).append(text)
    return found


def _legacy_group_reactions(states, name_of):
    """Thumbs up/down per member from a group message's groupMessageStates,
    a JSON object of identity to state."""
    try:
        parsed = json.loads(states) if states else {}
    except (ValueError, TypeError):
        return []
    if not isinstance(parsed, dict):
        return []
    return [f"{_LEGACY_REACTION_STATES[state]} {name_of(identity)}"
            for identity, state in parsed.items() if state in _LEGACY_REACTION_STATES]


def _group_label(group_id, groups):
    name = groups.get(group_id, '')
    return f"Group: {name} (#{group_id})" if name else f"Group #{group_id}"


def _conversation_label(row, contacts, groups):
    """'Name (ID)' for a one-to-one row, 'Group: name (#id)' for a group row."""
    if 'groupId' in row:
        return _group_label(row['groupId'], groups)
    identity = row['identity'] or ''
    name = contacts.get(identity, identity)
    return f"{name} ({identity})" if name and name != identity else identity


_MESSAGE_COLUMNS = (
    'id', 'uid', 'identity', 'outbox', 'type', 'body', 'caption', 'apiMessageId',
    'quotedMessageId', 'state', 'isRead', 'isStatusMessage', 'createdAtUtc',
    'deliveredAtUtc', 'readAtUtc', 'editedAtUtc', 'deletedAtUtc',
)


@artifact_processor
def threema_messages(context):
    # Ordered as check_conversation_column_order requires of an artifact with
    # a conversation view: the time column, the other dates, then direction,
    # sender, text and media, then the remaining columns in their old order.
    data_headers = (
        ("Created", "datetime"), ("Delivered", "datetime"), ("Read At", "datetime"),
        ("Edited", "datetime"), ("Deleted", "datetime"),
        "Direction", "Sender", "Message", ("Media", "media"),
        "Contact", "Content Type",
        "Text / Filename / Address", "MIME Type", "Size (bytes)",
        "Latitude", "Longitude", "Location Accuracy (m)",
        "Call Status", "Call ID", "Call Duration (s)", "State", "Read",
        "Quoted Message",
        "Conversation", "Media Status", "Media Duration (s)", "Reactions", "Gallery Copy",
    )

    files_found = unique_files(context)
    stores = _decrypted_connections(files_found)
    if not stores:
        return data_headers, [], ""

    data_list = []
    for con, container in stores:
        if con is None:
            continue
        try:
            cur = con.cursor()
            contacts = {row['identity']: _display_name(row) or row['identity']
                        for row in _select(cur, 'contacts', (
                            'identity', 'firstName', 'lastName', 'publicNickName'))}
            groups = {row['id']: row['name'] or ''
                      for row in _select(cur, 'm_group', ('id', 'name'))}
            own_identity, own = _own_account(container)
            name_of = functools.partial(_name_of, own_identity=own_identity, own=own,
                                        contacts=contacts)

            single = _select(cur, 'message', _MESSAGE_COLUMNS, order_by='createdAtUtc')
            group = _select(cur, 'm_group_message',
                            _MESSAGE_COLUMNS + ('groupId', 'groupMessageStates'),
                            order_by='createdAtUtc')
            reactions = _reactions(cur, single, group, name_of)

            copies = {}
            for copy_path, (stem, how, _several) in _gallery_links(
                    container, single + group).items():
                if stem:
                    copies.setdefault(stem, []).append(
                        f"{context.get_relative_path(copy_path)} ({how})")

            quotable = {}
            for row in single + group:
                if row['apiMessageId'] and row['type'] == 0 and row['body']:
                    quotable.setdefault(row['apiMessageId'], row['body'])

            for row in single + group:
                is_group = 'groupId' in row
                identity = row['identity'] or ''
                contact_name = contacts.get(identity, identity)
                conversation = _conversation_label(row, contacts, groups)

                if row['isStatusMessage']:
                    direction, sender = 'Status', ''
                elif row['outbox']:
                    direction, sender = 'Sent', own
                else:
                    direction, sender = 'Received', contact_name

                content = _decode(row['type'], row['body'], row['caption'])
                if row['isStatusMessage'] and row['type'] == 0:
                    content['content_type'] = 'Status'

                media, media_status = '', ''
                if row['type'] in _MEDIA_TYPES:
                    media, media_status = _media_for(row['uid'], container, content['text'])

                row_reactions = reactions.get((is_group, row['id']), [])
                if not row_reactions and is_group:
                    row_reactions = _legacy_group_reactions(row['groupMessageStates'], name_of)
                elif not row_reactions and row['state'] in _LEGACY_REACTION_STATES:
                    # The recipient reacted: the contact for a sent message,
                    # the local account for a received one. No time is stored.
                    row_reactions = [f"{_LEGACY_REACTION_STATES[row['state']]} "
                                     f"{own if not row['outbox'] else contact_name}"]

                quoted = row['quotedMessageId']
                data_list.append((
                    _epoch_ms_to_utc(row['createdAtUtc']),
                    _epoch_ms_to_utc(row['deliveredAtUtc']),
                    _epoch_ms_to_utc(row['readAtUtc']),
                    _epoch_ms_to_utc(row['editedAtUtc']),
                    _epoch_ms_to_utc(row['deletedAtUtc']),
                    direction,
                    sender,
                    content['message'],
                    media,
                    contact_name,
                    content['content_type'],
                    content['text'],
                    content['mime'],
                    content['size'],
                    content['lat'],
                    content['lon'],
                    content['accuracy'],
                    content['call_status'],
                    content['call_id'],
                    content['call_duration'],
                    row['state'] or '',
                    "Yes" if row['isRead'] else "",
                    quotable.get(quoted, '') if quoted else '',
                    conversation,
                    media_status,
                    content['media_duration'],
                    '; '.join(row_reactions),
                    '\n'.join(copies.get(re.sub(r'[^A-Za-z0-9]', '', row['uid'] or ''), [])),
                ))
        finally:
            con.close()

    data_list.sort(key=lambda row: (row[0] is None, row[0] or datetime.min.replace(tzinfo=timezone.utc)))
    logfunc(f"Threema Messages: {len(data_list)} message(s) recovered from "
            f"the decrypted database.")
    return data_headers, data_list, _source_paths(stores)


_PICTURE_KINDS = {'.p-': 'Profile picture (from contact)', '.c-': 'Profile picture (set locally)',
                  '.a-': 'Profile picture (Android contact)'}
_GROUP_PICTURE = re.compile(r'^\.(?:gpp|grp-avatar)-(\d+)$')


def _media_owners(cur, container):
    """Lookups from a stored file name to what the database says it belongs to."""
    contacts = {row['identity']: _display_name(row) or row['identity']
                for row in _select(cur, 'contacts', (
                    'identity', 'firstName', 'lastName', 'publicNickName'))}
    groups = {row['id']: row['name'] or '' for row in _select(cur, 'm_group', ('id', 'name'))}
    messages = {}
    rows = []
    columns = ('uid', 'identity', 'type', 'body', 'caption', 'createdAtUtc', 'apiMessageId')
    for table, extra in (('message', ()), ('m_group_message', ('groupId',))):
        for row in _select(cur, table, columns + extra):
            rows.append(row)
            if row['uid']:
                content = _decode(row['type'], row['body'], row['caption'])
                messages[re.sub(r'[^A-Za-z0-9]', '', row['uid'])] = (
                    _epoch_ms_to_utc(row['createdAtUtc']),
                    _conversation_label(row, contacts, groups),
                    content['message'] or content['text'])
    own_identity, own = _own_account(container)
    identities = {identity: f"{name} ({identity})" if name != identity else identity
                  for identity, name in contacts.items()}
    if own_identity:
        identities[own_identity] = f"{own} - local account"
    by_hash = {_profile_picture_name('', i): label for i, label in identities.items()}
    return messages, by_hash, groups, rows


def _describe_media(category, name, owners):
    """(created, kind, belongs to, message) of one stored media file. owners
    is what _media_owners read from the database, or None where no database
    could be opened, in which case nothing is called unreferenced."""
    if owners is None:
        (messages, by_hash, groups), unresolved = ({}, {}, {}), 'Database not opened'
    else:
        (messages, by_hash, groups), unresolved = owners[:3], 'Not referenced by the database'
    if category == 'media':
        match = _MEDIA_NAME.match(name)
        kind = 'Message thumbnail' if match and match.group(2) else 'Message file'
        found = messages.get(match.group(1)) if match else None
        if found:
            return found[0], kind, found[1], found[2]
        return None, kind, unresolved, ''
    if category == 'avatars':
        kind = _PICTURE_KINDS.get(name[:3], 'Profile picture')
        return None, kind, by_hash.get(name[3:], unresolved), ''
    if category == 'groups':
        match = _GROUP_PICTURE.match(name)
        group_id = int(match.group(1)) if match else None
        if group_id is not None and group_id in groups:
            return None, 'Group picture', _group_label(group_id, groups), ''
        return None, 'Group picture', unresolved, ''
    if category == 'other':
        return None, 'Other file', '', ''
    if name == 'wallpaper.jpg':
        return None, 'Default wallpaper', '', ''
    return None, 'Chat wallpaper', '', ''


@artifact_processor
def threema_media(context):
    data_headers = (
        ("Message Created", "datetime"), ("Media", "media"), "Kind", "Belongs To", "Message",
        "Stored File Name", "Storage", "Status", "Gallery Link",
    )

    files_found = unique_files(context)
    stores = _decrypted_connections(files_found, include_without_db=True)
    gallery_files = sum(len(store.container.get('gallery', [])) for store in stores)
    if not stores:
        return data_headers, [], ""

    data_list = []
    skipped = 0
    for con, container in stores:
        owners = None
        if con is not None:
            try:
                owners = _media_owners(con.cursor(), container)
            finally:
                con.close()
        keys = _keys(container)
        for category, name, path, storage in sorted(container['files'],
                                                    key=lambda f: (f[0], f[1], f[3])):
            data, mime = _decrypt_file(path, keys)
            if category == 'other' and data is None:
                # A file the client does not name as a user file is reported
                # only when it decrypts as one.
                skipped += 1
                continue
            if not keys:
                status = 'Not decrypted (no usable master key)'
            elif data is None:
                status = 'Did not decrypt'
            else:
                status = 'Decrypted' if mime else 'Decrypted, type not recognised'
            media = ''
            if data is not None:
                media = check_in_embedded_media(path, data, name.lstrip('.')) or ''
            created, kind, belongs, text = _describe_media(category, name, owners)
            data_list.append((created, media, kind, belongs, text, name,
                              _STORAGE_LABELS[storage], status, ''))
        links = _gallery_links(container, owners[3] if owners else None)
        messages = owners[0] if owners else {}
        for name, label, path in container.get('gallery', []):
            stem, how, several = links.get(path, (None, '', False))
            try:
                with open(path, 'rb') as f:
                    data = f.read()
            except OSError:
                data = None
            media = check_in_embedded_media(path, data, name) or '' if data is not None else ''
            if stem in messages:
                created, belongs, text = messages[stem]
            else:
                created, text = None, ''
                belongs = ('Database not opened' if owners is None else
                           'Not referenced by the database' if stem else
                           'Several messages' if several else
                           'No identical message file' if keys else
                           'Not compared (no usable master key)')
            data_list.append((created, media, 'File in gallery folder', belongs, text, name,
                              f"Shared storage ({label})", 'Not encrypted', how))

    data_list.sort(key=lambda row: (row[0] is None, row[0] or datetime.min.replace(tzinfo=timezone.utc),
                                    row[2], row[5]))
    if skipped:
        logfunc(f"Threema Media: {skipped} other file(s) in the user files directories did not "
                f"decrypt and are not listed.")
    logfunc(f"Threema Media: {len(data_list)} stored media file(s) found, "
            f"{gallery_files} of them in gallery folders.")
    return data_headers, data_list, _source_paths(stores)

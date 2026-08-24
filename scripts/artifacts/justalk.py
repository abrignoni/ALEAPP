__artifacts_v2__ = {
    "justalk_messages": {
        "name": "JusTalk - Messages",
        "description": "Chat messages from the JusTalk Realm store, with the message body, the "
                       "direction, the sender, the media type and the cached media file where it "
                       "is present in the extraction",
        "author": "@AlexisBrignoni, @Newhope81, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "JusTalk",
        "notes": "Messages are read from the class_CallLog table of the per-account Realm store "
                 "(files/<account uid>.realm), not from class_MessageChat, which was present in "
                 "the schema but empty in the sample this artifact was built from. class_CallLog "
                 "holds chat messages and call records in the same table; rows whose type is "
                 "AudioCall or VideoCall are reported by the JusTalk - Call Logs artifact instead.\n"
                 "Direction is taken from the boolean 'incoming' column. The separate 'state' "
                 "column is reported as stored: nothing in the extraction documents its values.\n"
                 "Media is linked without guessing. The message's 'fileUrl' column is a row index "
                 "into the class_ROFileUrl table, and that row's 'md5' column is base64 of the MD5 "
                 "of the media file's contents. Every file in the paths above is hashed and matched "
                 "against it, so a message is tied to a file by content rather than by name, size "
                 "or timestamp proximity. A message with no matching file means no copy of that "
                 "media was found in the extraction; it does not establish that the media never "
                 "existed on the device.\n"
                 "Duration is stored in seconds on voice and video message rows. That was derived "
                 "by dividing the stored byte length by the stored duration across the sampled "
                 "rows, which gave consistent audio and video bitrates; it is an inference from "
                 "the data, not a documented unit.\n"
                 "Validation boundary. This was built from a single private sample holding one "
                 "one-to-one conversation, so the fields are mapped from that sample and the "
                 "counts here are not from a public corpus. The class_ServerGroup and "
                 "class_ROKids* tables were all empty in it, so group chats and JusTalk Kids parental controls are not "
                 "covered. The reply, reaction, sticker, poll and link columns of class_CallLog "
                 "were unpopulated and are not reported. A sample exercising any of those would "
                 "be welcome.",
        "paths": ('*/com.juphoon.justalk/files/*.realm',
                  '*/com.juphoon.justalk/files/imfilecache/*',
                  '*/com.juphoon.justalk/files/image_manager_disk_cache/*',
                  '*/com.juphoon.justalk/files/http410cache/*',
                  '*/com.juphoon.justalk/files/JusTalk/profiles/*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {},
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Chat Partner",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender Name",
                "mediaColumn": "Media",
            }
        },
    },
    "justalk_calls": {
        "name": "JusTalk - Call Logs",
        "description": "Audio and video calls from the JusTalk Realm store, with the direction, "
                       "the duration and the server call identifier",
        "author": "@AlexisBrignoni, @Newhope81, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "JusTalk",
        "notes": "Read from the rows of class_CallLog whose type is AudioCall or VideoCall. "
                 "Direction is taken from the boolean 'incoming' column.\n"
                 "Duration on these rows is reported both as stored and converted from "
                 "milliseconds. Milliseconds is an inference: in the sample, three calls were "
                 "followed by a further message 15.4, 31.6 and 24.0 seconds after the call record, "
                 "each slightly longer than the duration read as milliseconds and not reconcilable "
                 "with the same value read as seconds. Note that this differs from the duration on "
                 "voice and video message rows, which is in seconds. The stored value is kept in "
                 "its own column so the conversion can be checked.\n"
                 "The 'state' and 'reason' columns are reported as stored; nothing in the "
                 "extraction documents their values. A duration of zero is not by itself evidence "
                 "that a call was not answered.",
        "paths": ('*/com.juphoon.justalk/files/*.realm',),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {},
    },
    "justalk_media": {
        "name": "JusTalk - Media",
        "description": "File records from the JusTalk Realm store with the cached copies found in "
                       "the extraction, plus any cached files the store does not account for",
        "author": "@AlexisBrignoni, @Newhope81, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "JusTalk",
        "notes": "Each row is one class_ROFileUrl record. The record's 'md5' column is base64 of "
                 "the MD5 of the file's contents, so cached copies are located by hashing every "
                 "file in the paths above and matching, rather than by file name. The same content "
                 "is often cached in more than one place: files/imfilecache holds the app's own "
                 "copy, files/image_manager_disk_cache and files/http410cache held further copies "
                 "of some items in the sample. All matches are reported.\n"
                 "Cached files that no class_ROFileUrl record accounts for are listed as their own "
                 "rows with an empty File Key so they are not dropped. Thumbnails, avatars and "
                 "sticker assets are expected to appear there. Files in these caches are often "
                 "stored with no extension or a '.0' extension; in the sample they were still "
                 "images, so the extension is reported as found and the content is checked in on "
                 "its own sniffed type.\n"
                 "The class_ROFileUrl table also carries sticker pack assets, which have a "
                 "filePath but no encryptedUrl and are not messages. 'localPath' and "
                 "'thumbnailLocalPath' are the paths the app recorded; in the sample they pointed "
                 "into the app's own cache, not to a user-initiated export to shared storage. They "
                 "are reported as stored and are not resolved against the extraction.",
        "paths": ('*/com.juphoon.justalk/files/*.realm',
                  '*/com.juphoon.justalk/files/imfilecache/*',
                  '*/com.juphoon.justalk/files/image_manager_disk_cache/*',
                  '*/com.juphoon.justalk/files/http410cache/*',
                  '*/com.juphoon.justalk/files/JusTalk/profiles/*'),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {},
    },
    "justalk_contacts": {
        "name": "JusTalk - Contacts",
        "description": "Contacts from the JusTalk Realm store, with the JusTalk ID, the display "
                       "and nickname, the client version reported for that account and the last "
                       "online time",
        "author": "@AlexisBrignoni, @Newhope81, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "JusTalk",
        "notes": "Read from the class_ServerFriend table. The class_Contact table, which holds "
                 "device address book matches, was empty in the sample this artifact was built "
                 "from and is not covered here.\n"
                 "The 'version' column carries a platform-prefixed client version string for the "
                 "other party's account, for example a value beginning 'ios.'. 'loginCountry' is "
                 "reported as stored; in the sample it held a value matching a telephone country "
                 "calling code, but nothing in the extraction documents the format.\n"
                 "relationType and serverRelationType are reported as stored.",
        "paths": ('*/com.juphoon.justalk/files/*.realm',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {},
    },
    "justalk_members": {
        "name": "JusTalk - Members",
        "description": "Server members (contacts/groups) from the JusTalk Realm store",
        "author": "@AlexisBrignoni, @Newhope81, Claude",
        "creation_date": "2026-08-10",
        "last_update_date": "2026-08-10",
        "requirements": "none",
        "category": "JusTalk",
        "notes": "Read from the class_ServerMember table.",
        "paths": ('*/com.juphoon.justalk/files/*.realm',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {},
    },
    "justalk_moments": {
        "name": "JusTalk - Moments",
        "description": "Moments (timeline posts) from the JusTalk Realm store",
        "author": "@AlexisBrignoni, @Newhope81, Claude",
        "creation_date": "2026-08-10",
        "last_update_date": "2026-08-10",
        "requirements": "none",
        "category": "JusTalk",
        "notes": "Read from the class_Moment table.",
        "paths": ('*/com.juphoon.justalk/files/*.realm',),
        "output_types": "standard",
        "artifact_icon": "layout",
        "sample_data": {},
    },
    "justalk_account": {
        "name": "JusTalk - Account",
        "description": "The local JusTalk account identifiers taken from the Realm store file "
                       "name, the app's provisioning file and the Realm schema version",
        "author": "@AlexisBrignoni, @Newhope81, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "JusTalk",
        "notes": "The per-account Realm store is named after the local account's own user id, so "
                 "the file name is reported as the account UID. That reading is corroborated by "
                 "the senderUid on outgoing message rows, which carries the same value.\n"
                 "The cur_prof_user attribute of files/JusTalk/profiles/provisions.xml holds a "
                 "scheme token joined to the account's JusTalk id, for example "
                 "'username)lola6593'. It is reported both as stored and split, because the "
                 "scheme token is not part of the id. The split is derived from the same "
                 "extraction: class_CallLog writes the peer form of that value as a URI reading "
                 "'[username:<id>@justalk.com]' on a row whose class_ServerFriend justalkId "
                 "column holds exactly the <id> part, so the token before the separator is the "
                 "scheme. The separator differs between the two because the value is also used "
                 "as a directory name under files/JusTalk/profiles/. A value not in that shape "
                 "is reported unchanged in both columns.\n"
                 "The JusTalk ID column prefers the justalkId key of the local profile in "
                 "files/mmkv/JusProfileManager<account uid>, which names the value directly, and "
                 "falls back to splitting cur_prof_user when that store is absent. In the sample "
                 "the two agreed, and a bare value in the per-profile provision-v1.xml agreed "
                 "with both.\n"
                 "The remaining account fields come from that same MMKV profile, which holds one "
                 "JSON document under a single key. Field names there are the app's own: "
                 "Basic.NickName, Ue.Email, Basic.Birthday, Phone.Country, loginCountry, "
                 "signUpDate, lastLoginTimeMillis, uuid and loginToken. Birthday is reported as "
                 "the app stored it, a plain date string with no time or zone. signUpDate is in "
                 "seconds and lastLoginTimeMillis in milliseconds, as their names state.\n"
                 "Ue.Facebook, Ue.Google and Ue.Huawei are linked-account slots. They were all "
                 "empty in the sample, so an empty value here means the slot carries no value, "
                 "not that a linked account was removed.\n"
                 "loginToken is a bearer credential for the account, reported in full at the "
                 "examiner's request. It is a JSON Web Token (RFC 7519), so its payload segment "
                 "is base64url and carries the standard 'exp' expiry claim; Token Expiry is that "
                 "claim decoded, and Token Subject is the payload's uid claim as stored. The "
                 "signature is not verified and the token is not tested against any server, so "
                 "these columns describe what the token asserts about itself and not whether it "
                 "is currently valid.\n"
                 "The Realm header reports two top references, which is the store's normal "
                 "committed and uncommitted pair. Both are read and their row counts compared; "
                 "where they differ, content is present in one view and not the other. In the "
                 "sample they matched exactly.\n"
                 "shared_prefs/com.juphoon.justalk_preferences.xml was checked and carries only "
                 "advertising consent framework keys, no account identity, so it is not parsed.\n"
                 "Validation boundary. Built from a single private sample holding one signed-in "
                 "account, so every field here was seen populated exactly once, and the "
                 "linked-account and family fields were never seen populated at all. An MMKV "
                 "store can be written in an AES-encrypted mode, which this reader does not "
                 "decrypt; a store written that way yields no keys, so an empty result is not "
                 "evidence the store was empty.",
        "paths": ('*/com.juphoon.justalk/files/*.realm',
                  '*/com.juphoon.justalk/files/JusTalk/profiles/provisions.xml',
                  '*/com.juphoon.justalk/files/mmkv/*'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {},
    },
    "justalk_app_state": {
        "name": "JusTalk - App State",
        "description": "Key and value pairs from the app's default MMKV store, covering the "
                       "device identifier, the signed-in account id, the push token and the "
                       "install channel, including values that later writes superseded",
        "author": "@AlexisBrignoni, @Newhope81, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "JusTalk",
        "notes": "Read from files/mmkv/mmkv.default with the shared mmkv_parser. Keys and values "
                 "are reported as the app wrote them and are not renamed or interpreted.\n"
                 "MMKV appends rather than edits, so changing a key writes a new entry and leaves "
                 "the previous one in the file. Every entry is reported in file order. The Current "
                 "Value column marks the last entry for a key, which is the one the app reads; "
                 "rows marked otherwise are earlier values still present in the store. In the "
                 "sample this preserved one superseded value, an empty VersionCheckerNewVersion "
                 "written before the current one.\n"
                 "A repeated entry is not by itself evidence the value changed. The app rewrites "
                 "some keys with the value they already held, which is why most repeats here are "
                 "identical.\n"
                 "A zero-length value is how MMKV records a removal, and is shown as an empty "
                 "Value with the type reported as removed. That is distinct from a key holding "
                 "an empty string.\n"
                 "Values are typed by the calling app, not on disk. The reader reports a string "
                 "where the stored bytes are a length-prefixed string and an integer where they "
                 "are a bare scalar, which is the only distinction the bytes support; a value "
                 "shown as an integer may have been written as a boolean.",
        "paths": ('*/com.juphoon.justalk/files/mmkv/*',),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {},
    },
    "justalk_kids_messages": {
        "name": "JusTalk Kids - Messages",
        "description": "Chat messages from the JusTalk Realm store, with the message body, the "
                       "direction, the sender, the media type and the cached media file where it "
                       "is present in the extraction",
        "author": "@AlexisBrignoni, @Newhope81, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "JusTalk Kids",
        "notes": "Messages are read from the class_CallLog table of the per-account Realm store "
                 "(files/<account uid>.realm), not from class_MessageChat, which was present in "
                 "the schema but empty in the sample this artifact was built from. class_CallLog "
                 "holds chat messages and call records in the same table; rows whose type is "
                 "AudioCall or VideoCall are reported by the JusTalk - Call Logs artifact instead.\n"
                 "Direction is taken from the boolean 'incoming' column. The separate 'state' "
                 "column is reported as stored: nothing in the extraction documents its values.\n"
                 "Media is linked without guessing. The message's 'fileUrl' column is a row index "
                 "into the class_ROFileUrl table, and that row's 'md5' column is base64 of the MD5 "
                 "of the media file's contents. Every file in the paths above is hashed and matched "
                 "against it, so a message is tied to a file by content rather than by name, size "
                 "or timestamp proximity. A message with no matching file means no copy of that "
                 "media was found in the extraction; it does not establish that the media never "
                 "existed on the device.\n"
                 "Duration is stored in seconds on voice and video message rows. That was derived "
                 "by dividing the stored byte length by the stored duration across the sampled "
                 "rows, which gave consistent audio and video bitrates; it is an inference from "
                 "the data, not a documented unit.\n"
                 "Validation boundary. This was built from a single private sample holding one "
                 "one-to-one conversation, so the fields are mapped from that sample and the "
                 "counts here are not from a public corpus. The class_ServerGroup and "
                 "class_ROKids* tables were all empty in it, so group chats and JusTalk Kids parental controls are not "
                 "covered. The reply, reaction, sticker, poll and link columns of class_CallLog "
                 "were unpopulated and are not reported. A sample exercising any of those would "
                 "be welcome.",
        "paths": ('*/com.justalk.kids.android/files/*.realm',
                  '*/com.justalk.kids.android/files/imfilecache/*',
                  '*/com.justalk.kids.android/files/image_manager_disk_cache/*',
                  '*/com.justalk.kids.android/files/http410cache/*',
                  '*/com.justalk.kids.android/files/JusTalk/profiles/*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {},
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Chat Partner",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender Name",
                "mediaColumn": "Media",
            }
        },
    },
    "justalk_kids_calls": {
        "name": "JusTalk Kids - Call Logs",
        "description": "Audio and video calls from the JusTalk Realm store, with the direction, "
                       "the duration and the server call identifier",
        "author": "@AlexisBrignoni, @Newhope81, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "JusTalk Kids",
        "notes": "Read from the rows of class_CallLog whose type is AudioCall or VideoCall. "
                 "Direction is taken from the boolean 'incoming' column.\n"
                 "Duration on these rows is reported both as stored and converted from "
                 "milliseconds. Milliseconds is an inference: in the sample, three calls were "
                 "followed by a further message 15.4, 31.6 and 24.0 seconds after the call record, "
                 "each slightly longer than the duration read as milliseconds and not reconcilable "
                 "with the same value read as seconds. Note that this differs from the duration on "
                 "voice and video message rows, which is in seconds. The stored value is kept in "
                 "its own column so the conversion can be checked.\n"
                 "The 'state' and 'reason' columns are reported as stored; nothing in the "
                 "extraction documents their values. A duration of zero is not by itself evidence "
                 "that a call was not answered.",
        "paths": ('*/com.justalk.kids.android/files/*.realm',),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {},
    },
    "justalk_kids_media": {
        "name": "JusTalk Kids - Media",
        "description": "File records from the JusTalk Realm store with the cached copies found in "
                       "the extraction, plus any cached files the store does not account for",
        "author": "@AlexisBrignoni, @Newhope81, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "JusTalk Kids",
        "notes": "Each row is one class_ROFileUrl record. The record's 'md5' column is base64 of "
                 "the MD5 of the file's contents, so cached copies are located by hashing every "
                 "file in the paths above and matching, rather than by file name. The same content "
                 "is often cached in more than one place: files/imfilecache holds the app's own "
                 "copy, files/image_manager_disk_cache and files/http410cache held further copies "
                 "of some items in the sample. All matches are reported.\n"
                 "Cached files that no class_ROFileUrl record accounts for are listed as their own "
                 "rows with an empty File Key so they are not dropped. Thumbnails, avatars and "
                 "sticker assets are expected to appear there. Files in these caches are often "
                 "stored with no extension or a '.0' extension; in the sample they were still "
                 "images, so the extension is reported as found and the content is checked in on "
                 "its own sniffed type.\n"
                 "The class_ROFileUrl table also carries sticker pack assets, which have a "
                 "filePath but no encryptedUrl and are not messages. 'localPath' and "
                 "'thumbnailLocalPath' are the paths the app recorded; in the sample they pointed "
                 "into the app's own cache, not to a user-initiated export to shared storage. They "
                 "are reported as stored and are not resolved against the extraction.",
        "paths": ('*/com.justalk.kids.android/files/*.realm',
                  '*/com.justalk.kids.android/files/imfilecache/*',
                  '*/com.justalk.kids.android/files/image_manager_disk_cache/*',
                  '*/com.justalk.kids.android/files/http410cache/*',
                  '*/com.justalk.kids.android/files/JusTalk/profiles/*'),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {},
    },
    "justalk_kids_contacts": {
        "name": "JusTalk Kids - Contacts",
        "description": "Contacts from the JusTalk Realm store, with the JusTalk ID, the display "
                       "and nickname, the client version reported for that account and the last "
                       "online time",
        "author": "@AlexisBrignoni, @Newhope81, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "JusTalk Kids",
        "notes": "Read from the class_ServerFriend table. The class_Contact table, which holds "
                 "device address book matches, was empty in the sample this artifact was built "
                 "from and is not covered here.\n"
                 "The 'version' column carries a platform-prefixed client version string for the "
                 "other party's account, for example a value beginning 'ios.'. 'loginCountry' is "
                 "reported as stored; in the sample it held a value matching a telephone country "
                 "calling code, but nothing in the extraction documents the format.\n"
                 "relationType and serverRelationType are reported as stored.",
        "paths": ('*/com.justalk.kids.android/files/*.realm',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {},
    },
    "justalk_kids_members": {
        "name": "JusTalk Kids - Members",
        "description": "Server members (contacts/groups) from the JusTalk Realm store",
        "author": "@AlexisBrignoni, @Newhope81, Claude",
        "creation_date": "2026-08-10",
        "last_update_date": "2026-08-10",
        "requirements": "none",
        "category": "JusTalk Kids",
        "notes": "Read from the class_ServerMember table.",
        "paths": ('*/com.justalk.kids.android/files/*.realm',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {},
    },
    "justalk_kids_moments": {
        "name": "JusTalk Kids - Moments",
        "description": "Moments (timeline posts) from the JusTalk Realm store",
        "author": "@AlexisBrignoni, @Newhope81, Claude",
        "creation_date": "2026-08-10",
        "last_update_date": "2026-08-10",
        "requirements": "none",
        "category": "JusTalk Kids",
        "notes": "Read from the class_Moment table.",
        "paths": ('*/com.justalk.kids.android/files/*.realm',),
        "output_types": "standard",
        "artifact_icon": "layout",
        "sample_data": {},
    },
    "justalk_kids_account": {
        "name": "JusTalk Kids - Account",
        "description": "The local JusTalk account identifiers taken from the Realm store file "
                       "name, the app's provisioning file and the Realm schema version",
        "author": "@AlexisBrignoni, @Newhope81, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "JusTalk Kids",
        "notes": "The per-account Realm store is named after the local account's own user id, so "
                 "the file name is reported as the account UID. That reading is corroborated by "
                 "the senderUid on outgoing message rows, which carries the same value.\n"
                 "The cur_prof_user attribute of files/JusTalk/profiles/provisions.xml holds a "
                 "scheme token joined to the account's JusTalk id, for example "
                 "'username)lola6593'. It is reported both as stored and split, because the "
                 "scheme token is not part of the id. The split is derived from the same "
                 "extraction: class_CallLog writes the peer form of that value as a URI reading "
                 "'[username:<id>@justalk.com]' on a row whose class_ServerFriend justalkId "
                 "column holds exactly the <id> part, so the token before the separator is the "
                 "scheme. The separator differs between the two because the value is also used "
                 "as a directory name under files/JusTalk/profiles/. A value not in that shape "
                 "is reported unchanged in both columns.\n"
                 "The JusTalk ID column prefers the justalkId key of the local profile in "
                 "files/mmkv/JusProfileManager<account uid>, which names the value directly, and "
                 "falls back to splitting cur_prof_user when that store is absent. In the sample "
                 "the two agreed, and a bare value in the per-profile provision-v1.xml agreed "
                 "with both.\n"
                 "The remaining account fields come from that same MMKV profile, which holds one "
                 "JSON document under a single key. Field names there are the app's own: "
                 "Basic.NickName, Ue.Email, Basic.Birthday, Phone.Country, loginCountry, "
                 "signUpDate, lastLoginTimeMillis, uuid and loginToken. Birthday is reported as "
                 "the app stored it, a plain date string with no time or zone. signUpDate is in "
                 "seconds and lastLoginTimeMillis in milliseconds, as their names state.\n"
                 "Ue.Facebook, Ue.Google and Ue.Huawei are linked-account slots. They were all "
                 "empty in the sample, so an empty value here means the slot carries no value, "
                 "not that a linked account was removed.\n"
                 "loginToken is a bearer credential for the account, reported in full at the "
                 "examiner's request. It is a JSON Web Token (RFC 7519), so its payload segment "
                 "is base64url and carries the standard 'exp' expiry claim; Token Expiry is that "
                 "claim decoded, and Token Subject is the payload's uid claim as stored. The "
                 "signature is not verified and the token is not tested against any server, so "
                 "these columns describe what the token asserts about itself and not whether it "
                 "is currently valid.\n"
                 "The Realm header reports two top references, which is the store's normal "
                 "committed and uncommitted pair. Both are read and their row counts compared; "
                 "where they differ, content is present in one view and not the other. In the "
                 "sample they matched exactly.\n"
                 "shared_prefs/com.justalk.kids.android_preferences.xml was checked and carries only "
                 "advertising consent framework keys, no account identity, so it is not parsed.\n"
                 "Validation boundary. Built from a single private sample holding one signed-in "
                 "account, so every field here was seen populated exactly once, and the "
                 "linked-account and family fields were never seen populated at all. An MMKV "
                 "store can be written in an AES-encrypted mode, which this reader does not "
                 "decrypt; a store written that way yields no keys, so an empty result is not "
                 "evidence the store was empty.",
        "paths": ('*/com.justalk.kids.android/files/*.realm',
                  '*/com.justalk.kids.android/files/JusTalk/profiles/provisions.xml',
                  '*/com.justalk.kids.android/files/mmkv/*'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {},
    },
    "justalk_kids_app_state": {
        "name": "JusTalk Kids - App State",
        "description": "Key and value pairs from the app's default MMKV store, covering the "
                       "device identifier, the signed-in account id, the push token and the "
                       "install channel, including values that later writes superseded",
        "author": "@AlexisBrignoni, @Newhope81, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "JusTalk Kids",
        "notes": "Read from files/mmkv/mmkv.default with the shared mmkv_parser. Keys and values "
                 "are reported as the app wrote them and are not renamed or interpreted.\n"
                 "MMKV appends rather than edits, so changing a key writes a new entry and leaves "
                 "the previous one in the file. Every entry is reported in file order. The Current "
                 "Value column marks the last entry for a key, which is the one the app reads; "
                 "rows marked otherwise are earlier values still present in the store. In the "
                 "sample this preserved one superseded value, an empty VersionCheckerNewVersion "
                 "written before the current one.\n"
                 "A repeated entry is not by itself evidence the value changed. The app rewrites "
                 "some keys with the value they already held, which is why most repeats here are "
                 "identical.\n"
                 "A zero-length value is how MMKV records a removal, and is shown as an empty "
                 "Value with the type reported as removed. That is distinct from a key holding "
                 "an empty string.\n"
                 "Values are typed by the calling app, not on disk. The reader reports a string "
                 "where the stored bytes are a length-prefixed string and an integer where they "
                 "are a bare scalar, which is the only distinction the bytes support; a value "
                 "shown as an integer may have been written as a boolean.",
        "paths": ('*/com.justalk.kids.android/files/mmkv/*',),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {},
    },
}

import base64
import hashlib
import json
import os
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, check_in_media, convert_unix_ts_to_utc
from scripts.mmkv_parser import MMKVError, decode_value, read_dict, read_entries
from scripts.realm_parser import parse_realm_file, realm_rows

# Rows of class_CallLog carrying these type values are call records rather than chat
# messages, and are reported by justalk_calls instead of justalk_messages.
CALL_TYPES = ('AudioCall', 'VideoCall')

# Files under the paths above that are the store itself or app configuration rather than
# cached media, so they are not hashed and do not appear as unaccounted media.
SKIP_SUFFIXES = ('.realm', '.lock', '.crc', '.log', '.backup-log', '.xml', '.ini')


def _is_justalk_realm(path):
    """The realm glob picks up default.realm and the versioned backup copy as well as the
    account store, so confirm the file carries JusTalk classes before reading it.
    Empty templates (0 rows in key tables) are ignored to prevent returning No Data."""
    try:
        tables = parse_realm_file(path).get('active', {})
    except Exception:  # pylint: disable=broad-exception-caught
        return False
    
    if 'metadata' not in tables:
        return False
        
    for cls in ('class_CallLog', 'class_ROFileUrl', 'class_ServerFriend', 'class_ServerMember', 'class_Moment'):
        if cls in tables and tables[cls].get('row_count', 0) > 0:
            return True
            
    return False


def _account_realms(files_found):
    """Return all valid per-account Realm stores. default.realm and .realm are empty stores
    and .v23.backup.realm copies are pre-upgrade snapshots, so they are passed over."""
    candidates = []
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('.realm'):
            continue
        name = os.path.basename(file_found)
        if name in ('default.realm', '.realm'):
            continue
        candidates.append(file_found)
    live = [path for path in candidates if '.backup.' not in os.path.basename(path)]
    valid_realms = []
    for path in live:
        if _is_justalk_realm(path):
            valid_realms.append(path)
    return valid_realms


def _rows(realm_path, class_name):
    if not realm_path:
        return []
    try:
        return list(realm_rows(realm_path, class_name))
    except Exception:  # pylint: disable=broad-exception-caught
        return []


def _md5_hex(stored):
    """class_ROFileUrl.md5 holds base64 of the raw MD5 digest, so decode it to hex before
    comparing against a hash computed over a file in the extraction."""
    if not stored:
        return ''
    try:
        raw = base64.b64decode(stored, validate=True)
    except Exception:  # pylint: disable=broad-exception-caught
        return ''
    if len(raw) != 16:
        return ''
    return raw.hex()


def _hash_index(files_found):
    """Map the MD5 of each candidate media file's contents to the paths holding it. The
    same content is cached in more than one directory, so a digest maps to a list."""
    index = {}
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith(SKIP_SUFFIXES) or os.path.isdir(file_found):
            continue
        try:
            with open(file_found, 'rb') as handle:
                digest = hashlib.md5(handle.read()).hexdigest()
        except OSError:
            continue
        index.setdefault(digest, []).append(file_found)
    return index



def enforce_extension(filename, magic_bytes=None):
    if not filename: return ""
    ext = os.path.splitext(filename)[1]
    detected_ext = None
    if magic_bytes:
        if magic_bytes.startswith(b'\xff\xd8\xff'): detected_ext = '.jpg'
        elif magic_bytes.startswith(b'\x89PNG'): detected_ext = '.png'
        elif magic_bytes.startswith(b'RIFF') and b'WEBP' in magic_bytes[:16]: detected_ext = '.webp'
        elif magic_bytes.startswith(b'GIF8'): detected_ext = '.gif'
        elif b'ftypheic' in magic_bytes[:16] or b'ftypheix' in magic_bytes[:16] or b'ftypmif1' in magic_bytes[:16]: detected_ext = '.heic'
        elif b'ftypM4A' in magic_bytes[:16]: detected_ext = '.m4a'
        elif b'ftyp' in magic_bytes[:16]: detected_ext = '.mp4'
        elif magic_bytes.startswith(b'RIFF') and b'WAVE' in magic_bytes[:16]: detected_ext = '.wav'
    if detected_ext:
        return detected_ext
    return ext

def _check_in(paths):
    for path in paths:
        try:
            with open(path, 'rb') as f:
                magic_bytes = f.read(16)
        except OSError:
            magic_bytes = None
        ext = enforce_extension(os.path.basename(path), magic_bytes)
        ref = check_in_media(path, os.path.basename(path), force_extension=ext)
        if ref: return ref
    return ''


def _file_record(file_records, link):
    """class_CallLog.fileUrl is a row index into class_ROFileUrl, not a URL."""
    if link is None:
        return {}
    try:
        return file_records[int(link)]
    except (TypeError, ValueError, IndexError):
        return {}


def _int_or_blank(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return ''


def _seconds_from_ms(value):
    value = _int_or_blank(value)
    if value == '' or value == 0:
        return ''
    return round(value / 1000, 3)


def _epoch(value):
    """The MMKV profile stores some epochs as JSON numbers and others as quoted strings,
    so coerce before handing the value to the shared converter."""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    return convert_unix_ts_to_utc(value)


@artifact_processor
def justalk_messages(context):
    files_found = context.get_files_found()
    source_paths = _account_realms(files_found)
    data_list = []

    hash_index = _hash_index(files_found)

    for source_path in source_paths:
        file_records = _rows(source_path, 'class_ROFileUrl')
        for row in sorted(_rows(source_path, 'class_CallLog'), key=lambda r: r.get('timestamp') or 0):
            if row.get('type') in CALL_TYPES:
                continue
            outgoing = not row.get('incoming')
            media = _file_record(file_records, row.get('fileUrl'))
            matches = hash_index.get(_md5_hex(media.get('md5')), []) if media else []
            
            mtype = row.get('type')
            msg_content = row.get('content')
            if mtype in ("Photo", "Video", "Movie", "Voice", "Location") and media:
                msg_content = f"[{mtype}]"
                
            data_list.append((
                convert_unix_ts_to_utc(row.get('timestamp')),
                'Outgoing' if outgoing else 'Incoming',
                row.get('senderName'),
                msg_content,
                _check_in(matches),
                row.get('name'),
                mtype,
                '' if not media else ('Recovered' if matches else 'Not in extraction'),
                media.get('encryptedUrl', ''),
                _int_or_blank(media.get('length')) if media else '',
                media.get('suffix', ''),
                _int_or_blank(media.get('duration')) if media else '',
                media.get('localPath', ''),
                media.get('thumbnailLocalPath', ''),
                row.get('senderUid'),
                row.get('uid'),
                row.get('imdnId'),
                row.get('logId'),
                row.get('state'),
                row.get('readState'),
            ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Direction',
        'Sender Name',
        'Message',
        ('Media', 'media'),
        'Chat Partner',
        'Message Type',
        'Media Recovery',
        'Encrypted URL',
        'Media Size (bytes)',
        'Media Suffix',
        'Media Duration (seconds)',
        'Recorded Local Path',
        'Recorded Thumbnail Path',
        'Sender UID',
        'Partner UID',
        'IMDN ID',
        'Log ID',
        'State (as stored)',
        'Read State (as stored)',
    )
    return data_headers, data_list, source_paths[0] if source_paths else ''


@artifact_processor
def justalk_calls(context):
    source_paths = _account_realms(context.get_files_found())
    data_list = []

    for source_path in source_paths:
        for row in sorted(_rows(source_path, 'class_CallLog'), key=lambda r: r.get('timestamp') or 0):
            if row.get('type') not in CALL_TYPES:
                continue
            data_list.append((
                convert_unix_ts_to_utc(row.get('timestamp')),
                'Outgoing' if not row.get('incoming') else 'Incoming',
                row.get('type'),
                row.get('name'),
                _seconds_from_ms(row.get('duration')),
                _int_or_blank(row.get('duration')),
                row.get('uid'),
                row.get('serverCallId'),
                row.get('logId'),
                row.get('state'),
                row.get('reason'),
            ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Direction',
        'Call Type',
        'Partner Name',
        'Duration (seconds)',
        'Duration (as stored)',
        'Partner UID',
        'Server Call ID',
        'Log ID',
        'State (as stored)',
        'Reason (as stored)',
    )
    return data_headers, data_list, source_paths[0] if source_paths else ''


@artifact_processor
def justalk_media(context):
    files_found = context.get_files_found()
    source_paths = _account_realms(files_found)
    data_list = []

    hash_index = _hash_index(files_found)
    accounted = set()

    for source_path in source_paths:
        file_records = _rows(source_path, 'class_ROFileUrl')
        # A message row points at its file record by index, so build the reverse map to report
        # which message each file belongs to.
        message_by_index = {}
        for row in _rows(source_path, 'class_CallLog'):
            link = row.get('fileUrl')
            if link is not None:
                message_by_index.setdefault(int(link), row)

        for index, media in enumerate(file_records):
            digest = _md5_hex(media.get('md5'))
            matches = hash_index.get(digest, [])
            accounted.update(matches)
            message = message_by_index.get(index, {})
            data_list.append((
                convert_unix_ts_to_utc(message.get('timestamp')) if message else '',
                _check_in(matches),
                media.get('suffix'),
                _int_or_blank(media.get('length')),
                _int_or_blank(media.get('duration')),
                digest,
                media.get('encryptedUrl'),
                media.get('fileKey'),
                media.get('fileName'),
                media.get('fileUrl'),
                media.get('filePath'),
                media.get('localPath'),
                media.get('thumbnailLocalPath'),
                _int_or_blank(media.get('width')),
                _int_or_blank(media.get('height')),
                message.get('type', ''),
                message.get('logId', ''),
                '; '.join(os.path.basename(path) for path in matches),
            ))

    for digest, paths in sorted(hash_index.items()):
        for path in paths:
            if path in accounted:
                continue
            data_list.append((
                '', _check_in([path]), os.path.splitext(path)[1].lstrip('.'),
                os.path.getsize(path) if os.path.exists(path) else '', '',
                digest, '', '', '', '', '', '', '', '', '', '', '',
                os.path.basename(path),
            ))

    data_headers = (
        ('Timestamp', 'datetime'),
        ('Media', 'media'),
        'Suffix',
        'Size (bytes)',
        'Duration (seconds)',
        'Content MD5',
        'Encrypted URL',
        'File Key',
        'File Name',
        'Remote URL',
        'Server File Path',
        'Recorded Local Path',
        'Recorded Thumbnail Path',
        'Width',
        'Height',
        'Message Type',
        'Message Log ID',
        'Cached File Names',
    )
    return data_headers, data_list, source_paths[0] if source_paths else ''


@artifact_processor
def justalk_contacts(context):
    source_paths = _account_realms(context.get_files_found())
    data_list = []

    for source_path in source_paths:
        for row in _rows(source_path, 'class_ServerFriend'):
            data_list.append((
                _epoch(row.get('timestamp')),
                _epoch(row.get('lastOnlineTime')),
                _epoch(row.get('birthday')),
                row.get('justalkId'),
                row.get('name'),
                row.get('nickName'),
                row.get('uid'),
                row.get('phone'),
                row.get('gender'),
                row.get('loginCountry'),
                row.get('version'),
                row.get('packageName'),
                row.get('avatarUrl'),
                row.get('relationType'),
                row.get('serverRelationType'),
                row.get('onlineState'),
                'Yes' if row.get('mute') else 'No',
                'Yes' if row.get('sticky') else 'No',
            ))

    data_headers = (
        ('Timestamp', 'datetime'),
        ('Last Online Time', 'datetime'),
        ('Birthday', 'datetime'),
        'JusTalk ID',
        'Name',
        'Nickname',
        'UID',
        'Phone',
        'Gender',
        'Login Country (as stored)',
        'Client Version',
        'Package Name',
        'Avatar URL',
        'Relation Type (as stored)',
        'Server Relation Type (as stored)',
        'Online State (as stored)',
        'Muted',
        'Pinned',
    )
    return data_headers, data_list, source_paths[0] if source_paths else ''


def _profile_user(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('provisions.xml'):
            continue
        try:
            general = ET.parse(file_found).getroot().find('GENERAL')
        except (ET.ParseError, OSError):
            continue
        if general is not None:
            return general.get('cur_prof_user', ''), file_found
    return '', ''


def _mmkv_path(files_found, basename_prefix, account_uid=''):
    """Return the MMKV store whose file name starts with basename_prefix. The app writes one
    profile store per identity it has held, so prefer the one named for the account uid."""
    candidates = []
    for file_found in files_found:
        file_found = str(file_found)
        parent, name = os.path.split(file_found)
        if os.path.basename(parent) != 'mmkv' or not name.startswith(basename_prefix):
            continue
        if name.endswith('.crc'):
            continue
        candidates.append(file_found)
    preferred = [p for p in candidates if account_uid and os.path.basename(p).endswith(account_uid)]
    for path in preferred + candidates:
        try:
            if read_entries(path):
                return path
        except (MMKVError, OSError):
            continue
    return ''


def _local_profile(files_found, account_uid):
    """The local account's own profile, stored as one JSON document under a single MMKV key."""
    path = _mmkv_path(files_found, 'JusProfileManager', account_uid)
    if not path:
        return {}, ''
    try:
        store = read_dict(path)
    except (MMKVError, OSError):
        return {}, path
    for value in store.values():
        if not isinstance(value, str):
            continue
        try:
            document = json.loads(value)
        except ValueError:
            continue
        if isinstance(document, dict):
            return document, path
    return {}, path


def _jwt_claims(token):
    """Return the payload claims of a JSON Web Token (RFC 7519) without verifying it.

    The signature is not checked and the token is not presented to any server, so this
    reports what the token asserts about itself, nothing more."""
    if not token or not isinstance(token, str):
        return {}
    parts = token.split('.')
    if len(parts) != 3:
        return {}
    payload = parts[1] + '=' * (-len(parts[1]) % 4)
    try:
        claims = json.loads(base64.urlsafe_b64decode(payload))
    except (ValueError, TypeError):
        return {}
    return claims if isinstance(claims, dict) else {}


def _justalk_id(profile_user):
    """cur_prof_user is a scheme token joined to the account's JusTalk id, as in
    'username)lola6593'. The same store writes the peer form of that value as a URI,
    '[username:johnlucas90@justalk.com]', against a class_ServerFriend row whose justalkId
    column reads 'johnlucas90', so the token before the separator is the scheme and the
    part after it is the id. The separator differs because the value is also used as a
    directory name under files/JusTalk/profiles/. Anything not in that shape is returned
    unchanged rather than guessed at."""
    if not profile_user:
        return ''
    scheme, separator, identifier = profile_user.partition(')')
    if separator and scheme == 'username' and identifier:
        return identifier
    return profile_user


@artifact_processor
def justalk_account(context):
    files_found = context.get_files_found()
    source_paths = _account_realms(files_found)
    data_list = []

    profile_user, profile_path = _profile_user(files_found)
    if not source_paths and not profile_user:
        return _account_headers(), data_list, ''

    for source_path in source_paths or ['']:
        counts = {}
        if source_path:
            for section in ('active', 'inactive'):
                total = 0
                for class_name in ('class_CallLog', 'class_ROFileUrl', 'class_ServerFriend',
                                   'class_Conversation'):
                    try:
                        total += len(list(realm_rows(source_path, class_name, section=section)))
                    except Exception:  # pylint: disable=broad-exception-caught
                        pass
                counts[section] = total

        metadata = _rows(source_path, 'metadata')
        account_uid = os.path.basename(source_path)[:-len('.realm')] if source_path else ''

        profile, mmkv_profile_path = _local_profile(files_found, account_uid)
        token = profile.get('loginToken', '')
        claims = _jwt_claims(token)

        data_list.append((
            _epoch(profile.get('lastLoginTimeMillis')),
            _epoch(profile.get('signUpDate')),
            _epoch(claims.get('exp')),
            account_uid,
            profile.get('justalkId') or _justalk_id(profile_user),
            profile.get('Basic.NickName', ''),
            profile.get('Ue.Email', ''),
            profile.get('phone', ''),
            profile.get('Basic.Birthday', ''),
            profile.get('Phone.Country', ''),
            profile.get('loginCountry', ''),
            profile.get('uuid', ''),
            token,
            claims.get('uid', ''),
            profile.get('Ue.Facebook', ''),
            profile.get('Ue.Google', ''),
            profile.get('Ue.Huawei', ''),
            profile.get('familyId', ''),
            profile.get('parentPhone', ''),
            profile.get('consecutiveLoginDays', ''),
            profile.get('blockStrangers', ''),
            profile_user,
            metadata[0].get('version') if metadata else '',
            counts.get('active', ''),
            counts.get('inactive', ''),
            'Yes' if counts and counts.get('active') != counts.get('inactive') else 'No',
            context.get_relative_path(source_path) if source_path else '',
            context.get_relative_path(profile_path) if profile_path else '',
            context.get_relative_path(mmkv_profile_path) if mmkv_profile_path else '',
        ))

    return _account_headers(), data_list, source_paths[0] if source_paths else profile_path


def _account_headers():
    return (
        ('Last Login', 'datetime'),
        ('Sign-Up Date', 'datetime'),
        ('Token Expiry', 'datetime'),
        'Account UID',
        'JusTalk ID',
        'Nickname',
        'Email',
        'Phone',
        'Birthday (as stored)',
        'Phone Country',
        'Login Country (as stored)',
        'Profile UUID',
        'Login Token',
        'Token Subject (as stored)',
        'Linked Facebook',
        'Linked Google',
        'Linked Huawei',
        'Family ID',
        'Parent Phone',
        'Consecutive Login Days',
        'Block Strangers (as stored)',
        'Profile User (as stored)',
        'Realm Schema Version',
        'Rows in Committed View',
        'Rows in Uncommitted View',
        'Views Differ',
        'Realm Store Path',
        'Provisioning File Path',
        'MMKV Profile Path',
    )


@artifact_processor
def justalk_app_state(context):
    files_found = context.get_files_found()
    source_path = _mmkv_path(files_found, 'mmkv.default')
    data_list = []

    if source_path:
        try:
            entries = read_entries(source_path)
        except (MMKVError, OSError):
            entries = []
        # The last entry for a key is the one the app reads; earlier ones are superseded
        # values the append-only store still holds.
        last_index = {key: index for index, (key, _) in enumerate(entries)}
        for index, (key, container) in enumerate(entries):
            value = decode_value(container)
            if value is None:
                value_type = 'removed'
                rendered = ''
            elif isinstance(value, str):
                value_type = 'string'
                rendered = value
            elif isinstance(value, int):
                value_type = 'integer'
                rendered = value
            else:
                value_type = 'bytes'
                rendered = value.hex()
            data_list.append((
                key,
                rendered,
                value_type,
                'Yes' if last_index.get(key) == index else 'No',
                index,
            ))

    data_headers = (
        'Key',
        'Value',
        'Value Type',
        'Current Value',
        'Entry Order',
    )
    return data_headers, data_list, source_path


@artifact_processor
def justalk_members(context):
    source_paths = _account_realms(context.get_files_found())
    data_list = []

    for source_path in source_paths:
        for row in _rows(source_path, 'class_ServerMember'):
            data_list.append((
                row.get('id', ''),
                row.get('uid', ''),
                row.get('name', ''),
                row.get('sortKey', ''),
                row.get('relationType', ''),
                row.get('serverFriend', ''),
            ))

    data_headers = (
        'Member ID',
        'UID',
        'Name',
        'Sort Key',
        'Relation Type (as stored)',
        'Server Friend (as stored)',
    )
    return data_headers, data_list, source_paths[0] if source_paths else ''


@artifact_processor
def justalk_moments(context):
    source_paths = _account_realms(context.get_files_found())
    data_list = []

    for source_path in source_paths:
        for row in sorted(_rows(source_path, 'class_Moment'), key=lambda r: r.get('createTime') or 0):
            data_list.append((
                _epoch(row.get('createTime')),
                _epoch(row.get('serverCreateTime')),
                _epoch(row.get('serverUpdateTime')),
                row.get('momentUuid', ''),
                row.get('uid', ''),
                row.get('name', ''),
                row.get('description', ''),
                row.get('type', ''),
                row.get('status', ''),
                row.get('userStatus', ''),
                row.get('fileList', ''),
                row.get('likeList', ''),
                row.get('commentList', ''),
                row.get('link', ''),
                row.get('isLiked', ''),
            ))

    data_headers = (
        ('Create Time', 'datetime'),
        ('Server Create Time', 'datetime'),
        ('Server Update Time', 'datetime'),
        'Moment UUID',
        'UID',
        'Name',
        'Description',
        'Type',
        'Status (as stored)',
        'User Status (as stored)',
        'File List',
        'Like List',
        'Comment List',
        'Link',
        'Is Liked (as stored)',
    )
    return data_headers, data_list, source_paths[0] if source_paths else ''


@artifact_processor
def justalk_kids_messages(context):
    return justalk_messages.__wrapped__(context)

@artifact_processor
def justalk_kids_calls(context):
    return justalk_calls.__wrapped__(context)

@artifact_processor
def justalk_kids_media(context):
    return justalk_media.__wrapped__(context)

@artifact_processor
def justalk_kids_contacts(context):
    return justalk_contacts.__wrapped__(context)

@artifact_processor
def justalk_kids_account(context):
    return justalk_account.__wrapped__(context)

@artifact_processor
def justalk_kids_app_state(context):
    return justalk_app_state.__wrapped__(context)


@artifact_processor
def justalk_kids_members(context):
    return justalk_members.__wrapped__(context)


@artifact_processor
def justalk_kids_moments(context):
    return justalk_moments.__wrapped__(context)

__artifacts_v2__ = {
    "content_query_files": {
        "name": "Content Query Files",
        "description": "What each saved content query output file of an android_triage or ALEX raw text extraction, "
                       "or of an ALEX PRFS zip, holds: rows, No result found., an access or provider error, an empty "
                       "file, or no file, with the status ALEX wrote beside it in a PRFS zip.",
        "author": "@Maxitelmo, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Logs & Diagnostics",
        "notes": "One row per URI that the Content Query artifacts read, for each output folder found, and one row per "
                 "other output file in the folder. Folders read: the <YYYYMMDD_HH_MM_SS>_contentprovider folder that "
                 "android_triage (RealityNet/android_triage, android_triage.sh, content_provider function, "
                 "https://github.com/RealityNet/android_triage/blob/14edd9358e3cf111bc90fe2bd72a62c5b24e67ae/android_triage.sh#L706-L804) "
                 "writes under the device's ANDROID_ID folder, and the content_provider_<serial> folder that ALEX "
                 "(prosch88/ALEX, alex.py, query_content, "
                 "https://github.com/prosch88/ALEX/blob/9ef34bf02c7f7ff29e1ad1a1db3c7b2ac6e3f048/alex.py#L4280-L4388) "
                 "writes when its content provider output is saved as raw text, with one <key> folder per provider, "
                 "and the extra/content_provider folder of an ALEX PRFS zip (below). "
                 "ALEX's JSON output and the databases it rebuilds from it are not read here. Status says what the "
                 "file holds: rows (with the row count), 'No result found.' (the content command prints it when the "
                 "provider returns no cursor or an empty one), 'access denied (SecurityException)' when the text holds "
                 "the error line 'Error while accessing provider:' followed by a java.lang.SecurityException, "
                 "'provider error' for the same error line followed by any other exception (Detail gives its class "
                 "and message), 'empty file', 'text not recognised' (Detail gives the first line), 'file not "
                 "readable' (the file was found but ALEAPP could not open or read its copy; Detail gives the class "
                 "and system text of the error raised when the copy was opened, and the other files and folders "
                 "are still read; when the copy into the report's data folder failed, Detail can read "
                 "FileNotFoundError and the cause is in the run log), or 'no file'. "
                 "Content.java prints the error line and the stack trace on stderr (lines 530 and 531 at "
                 "https://android.googlesource.com/platform/frameworks/base/+/8d2ed506045d5d6cf25ef7ef77a30da910733657/cmds/content/src/com/android/commands/content/Content.java). "
                 "android_triage redirects stdout only, so a query that fails leaves an empty file there and the "
                 "error text is not in the extraction; an empty file says only that the query printed nothing on "
                 "stdout. android_triage creates the file of every URI it queries, so a URI file missing from an "
                 "android_triage folder was not kept in the extraction, or the run stopped before that query. "
                 "ALEX up to commit 8f27e7a writes no file when the output holds any of 'Error while accessing "
                 "provider', 'Unsupported argument', 'No result found' or 'command not found', matched anywhere in the "
                 "output, including inside a value, and notes the skip in its own log only. From ed3d41eb (2026-11-25, "
                 "https://github.com/prosch88/ALEX/blob/ed3d41ebea64f73f86f4568f29ff6cf5a1a10cf1/alex.py#L4280-L4321) "
                 "it writes the file whenever the output holds a row, so a missing file then means no row was printed "
                 "(No result found. or an error). Either way, for ALEX a missing file is reported as unknown, since no "
                 "rows and an error look the same. From ed3d41eb ALEX's PRFS zip (layout 'ALEX PRFS zip') keeps the "
                 "same <key>/<name>.txt under extra/content_provider/, written for every URI ALEX queries, also when "
                 "the output is empty or an error, unless the run stopped before that query; a file missing there "
                 "is reported as not in the extraction. Beside each file ALEX writes <name>.status.json; Tool Status "
                 "shows its status as written (rows, empty or error) and is blank for the other layouts. ALEX "
                 "sets it with its own row parser: rows when it finds a row, empty when the output is blank or "
                 "exactly 'No result found.', error otherwise. Status still comes from the text, and Detail says "
                 "when ALEX's status does not stand for it (rows for rows; empty for 'No result found.' or an "
                 "empty file; error for access denied, provider error or text not recognised), when the status "
                 "file is missing, cannot be read or holds no usable status (none, only white space, or text that "
                 "cannot be written as UTF-8), and, on a row of its own, when a status file has no text file "
                 "beside it. URI is the one the file name stands for; for a file no artifact reads, it is the URI "
                 "the status file names, and Detail says so; a status file naming another URI than the file name "
                 "is flagged in Detail, and its status is not compared with the text, nor is the status of a "
                 "status file whose URI is not text. The <name>.json ALEX writes "
                 "with JSON output on is not read. A row of a folder "
                 "can say 'not queried by this tool' when the layout has no file for "
                 "that URI (android_triage does not query SMS, MMS or the call log; ALEX does not query "
                 "content://com.android.calendar/events). Rows of a file ending with a provider error after its last "
                 "row say so in Detail. Columns lists the column names that the rows of the file printed, in order. "
                 "Read By names the Content Query artifact that presents the file's rows; 'not read' means none does, "
                 "which says nothing about what the file holds. android_triage's own log (<folder>.txt) and its "
                 "dumpsys of the providers (content_providers_list.txt) are not content query output and are not "
                 "listed. Evidence tier: source-verified (format from the AOSP source above, layouts from the source "
                 "of "
                 "each tool at the commits linked) and tested on synthetic files only.",
        "paths": ('*/*_contentprovider/*.txt', '*/content_provider_*/*.txt', '*/extra/content_provider/*.txt',
                  '*/extra/content_provider/*.status.json'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "file-text",
    },
    "content_query_sms": {
        "name": "SMS (content query)",
        "description": "SMS rows from the saved output of adb shell content query --uri content://sms, as printed, "
                       "with dates read as milliseconds.",
        "author": "@Maxitelmo, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Messaging",
        "notes": "Read from ALEX raw text output only (content_provider_<serial>/sms/sms.txt, or "
                 "extra/content_provider/sms/sms.txt in an ALEX PRFS zip); android_triage does not "
                 "query SMS. ALEX also keeps sms_inbox, sms_sent, sms_draft, sms_outbox, sms_queued and sms_all, which "
                 "are views of the same table; they are not read, so a message is not reported twice. ALEX up to "
                 "commit 8f27e7a (prosch88/ALEX) writes no file when the output holds 'No result found' or another of "
                 "its four error strings anywhere, so with it one such message body leaves no sms.txt at all; from "
                 "ed3d41eb (2026-11-25) it writes the file whenever the output holds a row. Content Query Files "
                 "reports a missing file as unknown; in an ALEX PRFS zip (from ed3d41eb), "
                 "which holds the file of every URI ALEX queries, as not in the extraction. "
                 "Date and Date Sent: the provider contract gives the type INTEGER (long) and no unit "
                 "(Telephony.TextBasedSmsColumns.DATE and DATE_SENT, "
                 "https://developer.android.com/reference/android/provider/Telephony.TextBasedSmsColumns#DATE). They "
                 "are read as milliseconds since 1970-01-01 UTC, the unit AOSP's SmsProvider uses when it sets the "
                 "date itself (System.currentTimeMillis(), line 783 at "
                 "https://android.googlesource.com/platform/packages/providers/TelephonyProvider/+/5fb0368b51edc7e9babaa2febf88e8aa94b86f55/src/com/android/providers/telephony/SmsProvider.java). "
                 "A value of 0, NULL or nothing is blank. Type is the type value as printed and the name of the "
                 "Telephony.TextBasedSmsColumns MESSAGE_TYPE constant with that value (0 ALL, 1 INBOX, 2 SENT, 3 "
                 "DRAFT, "
                 "4 OUTBOX, 5 FAILED, 6 QUEUED; "
                 "https://developer.android.com/reference/android/provider/Telephony.TextBasedSmsColumns#MESSAGE_TYPE_INBOX); "
                 "another value is shown as printed. Address, Body and the other columns are as printed. "
                 "Format: rows are read from the text that the content command prints (AOSP Content.java, lines 664 to "
                 "706 at "
                 "https://android.googlesource.com/platform/frameworks/base/+/8d2ed506045d5d6cf25ef7ef77a30da910733657/cmds/content/src/com/android/commands/content/Content.java): "
                 "'Row: <n> ' and the name=value pairs joined with ', ', with no quoting or escaping. A NULL value "
                 "prints as the text NULL and a BLOB as the text BLOB, so a stored text NULL or BLOB cannot be told "
                 "apart from a real NULL or BLOB. An empty string prints as nothing and is blank here. Values are "
                 "shown "
                 "as printed, line breaks kept. A row is split at ', <next column>=' along the column list that the "
                 "rows of the file agree on; Parse Note flags a row where a value holds ', <name>=' for a name of that "
                 "list (the split may be off there) and a row that could not be split. A value line that is exactly "
                 "'Row: <next row number> <first column>=...' cannot be told apart from a new row. Rows are what the "
                 "provider returned to the shell user when the tool ran; deleted records are not in the output. "
                 "Columns not listed here are not shown (Content Query Files lists the columns of each file), and a "
                 "listed column that a device does not print is blank and named in the log. Source Line is the line "
                 "of the file where the row starts. Evidence tier: source-verified and tested on synthetic files "
                 "only.",
        "paths": ('*/content_provider_*/sms/sms.txt', '*/extra/content_provider/sms/sms.txt'),
        "output_types": "standard",
        "artifact_icon": "message",
        "multiline_columns": ["Body", "Parse Note"],
    },
    "content_query_mms": {
        "name": "MMS (content query)",
        "description": "MMS message rows from the saved output of adb shell content query --uri content://mms, as "
                       "printed, with dates read as seconds.",
        "author": "@Maxitelmo, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Messaging",
        "notes": "Read from ALEX raw text output only (content_provider_<serial>/mms/mms.txt, or "
                 "extra/content_provider/mms/mms.txt in an ALEX PRFS zip); android_triage does not "
                 "query MMS. ALEX's mms_inbox, mms_sent and mms_outbox files are views of the same table and are not "
                 "read. From, To, Cc and Bcc are the address values of the rows of mms_addr.txt in the same folder "
                 "(content://mms/addr) whose msg_id is the message's _id, by type, in file order and joined with "
                 "'; ', as printed (a NULL address shows as the text NULL); an address row whose type is none of "
                 "the four (PduHeaders FROM 137, TO 151, CC 130, BCC 129) is not shown on the message row. MMS "
                 "Addresses (content query) lists every address row with its Source Line. AOSP's MmsProvider does "
                 "not match content://mms/addr (it "
                 "matches content://mms/<id>/addr, line 1211 at "
                 "https://android.googlesource.com/platform/packages/providers/TelephonyProvider/+/f5fa3b6153f98c57fa50c80ade2904005a4987ce/src/com/android/providers/telephony/MmsProvider.java), "
                 "but some device providers answer it with one row per address keyed by msg_id. When ALEX kept no "
                 "mms_addr.txt the four columns are blank and Parse Note says 'addresses unknown' on each row, "
                 "since no rows, an error and a skipped dump look the same. When mms_addr.txt is there but holds "
                 "no FROM, TO, CC or BCC row for a message, Parse Note says so on that row. When mms_addr.txt is not "
                 "a full list of rows (a provider error, rows followed by an error, rows that could not be split, an "
                 "empty or unrecognised file, a file that could not be read, or rows that print no msg_id or type "
                 "column; the cause of a missing column is not established, and ALEX (prosch88/ALEX 9ef34bf0 and "
                 "ed3d41eb) and android_triage (RealityNet/android_triage 14edd935) query without a projection), "
                 "the addresses read from it are "
                 "shown, a message with some says 'addresses may be partial' with the reason, and a message with "
                 "none says 'addresses unknown' with the reason. A message row whose _id is "
                 "empty or the text NULL is not matched and says 'addresses unknown'; address rows whose msg_id is "
                 "empty or NULL are not matched to any message. The report's source list names mms_addr.txt next to "
                 "mms.txt; Source File and Source Line stay those of the message row. The "
                 "parts of each message are in MMS Parts (content query), keyed by its _id. Date and Date Sent: the "
                 "provider contract gives the type INTEGER (long) and no unit (Telephony.BaseMmsColumns.DATE and "
                 "DATE_SENT, https://developer.android.com/reference/android/provider/Telephony.BaseMmsColumns#DATE). "
                 "They are read as seconds since 1970-01-01 UTC, the unit AOSP's MmsProvider uses when it sets the "
                 "date itself (System.currentTimeMillis() / 1000, line 479 of the MmsProvider.java linked above). A "
                 "value of 0, NULL or nothing is blank. Message Box is the msg_box value as printed and the name of "
                 "the "
                 "Telephony.BaseMmsColumns MESSAGE_BOX constant with that value (0 ALL, 1 INBOX, 2 SENT, 3 DRAFTS, "
                 "4 OUTBOX, 5 FAILED; "
                 "https://developer.android.com/reference/android/provider/Telephony.BaseMmsColumns#MESSAGE_BOX_INBOX); "
                 "another value is shown as printed. Subject (sub), Message Type (m_type) and the other columns are as "
                 "printed. ALEX up to commit 8f27e7a (prosch88/ALEX) writes no file when the output holds 'No result "
                 "found' or "
                 "another of its four error strings anywhere, including inside a value; from ed3d41eb (2026-11-25) it "
                 "writes the file whenever the output holds a row. Content Query Files reports a missing file as "
                 "unknown; in an ALEX PRFS zip (from ed3d41eb), "
                 "which holds the file of every URI ALEX queries, as not in the extraction. "
                 "Format: rows are read from the text that the content command prints (AOSP Content.java, lines 664 to "
                 "706 at "
                 "https://android.googlesource.com/platform/frameworks/base/+/8d2ed506045d5d6cf25ef7ef77a30da910733657/cmds/content/src/com/android/commands/content/Content.java): "
                 "'Row: <n> ' and the name=value pairs joined with ', ', with no quoting or escaping. A NULL value "
                 "prints as the text NULL and a BLOB as the text BLOB, so a stored text NULL or BLOB cannot be told "
                 "apart from a real NULL or BLOB. An empty string prints as nothing and is blank here. Values are "
                 "shown "
                 "as printed, line breaks kept. A row is split at ', <next column>=' along the column list that the "
                 "rows of the file agree on; Parse Note flags a row where a value holds ', <name>=' for a name of that "
                 "list (the split may be off there) and a row that could not be split. A value line that is exactly "
                 "'Row: <next row number> <first column>=...' cannot be told apart from a new row. Rows are what the "
                 "provider returned to the shell user when the tool ran; deleted records are not in the output. "
                 "Columns not listed here are not shown (Content Query Files lists the columns of each file), and a "
                 "listed column that a device does not print is blank and named in the log. Source Line is the line "
                 "of the file where the row starts. Evidence tier: source-verified and tested on synthetic files "
                 "only.",
        "paths": ('*/content_provider_*/mms/mms.txt', '*/extra/content_provider/mms/mms.txt',
                  '*/content_provider_*/mms/mms_addr.txt', '*/extra/content_provider/mms/mms_addr.txt'),
        "output_types": "standard",
        "artifact_icon": "message",
        "multiline_columns": ["Subject", "Parse Note"],
    },
    "content_query_mms_addresses": {
        "name": "MMS Addresses (content query)",
        "description": "MMS address rows from the saved output of adb shell content query --uri content://mms/addr, "
                       "as printed, with the PduHeaders name of each address type.",
        "author": "@Maxitelmo, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Messaging",
        "notes": "Read from ALEX raw text output only (content_provider_<serial>/mms/mms_addr.txt, or "
                 "extra/content_provider/mms/mms_addr.txt in an ALEX PRFS zip); android_triage "
        "does "
                 "not query MMS. AOSP's MmsProvider does not match content://mms/addr (it matches "
                 "content://mms/<id>/addr, line 1211 at "
                 "https://android.googlesource.com/platform/packages/providers/TelephonyProvider/+/f5fa3b6153f98c57fa50c80ade2904005a4987ce/src/com/android/providers/telephony/MmsProvider.java), "
                 "but some device providers answer it with one row per address keyed by msg_id, the _id of the "
                 "message in MMS (content query). Where the provider rejects the URI ALEX keeps no file and the "
                 "addresses are unknown; Content Query Files reports that. Address Type is the type value as printed "
                 "and the name of the PduHeaders address field with that value (129 BCC, 130 CC, 137 FROM, 151 TO; "
                 "lines 31, 32, 39 and 55 at "
                 "https://android.googlesource.com/platform/frameworks/base/+/8d2ed506045d5d6cf25ef7ef77a30da910733657/telephony/common/com/google/android/mms/pdu/PduHeaders.java); "
                 "another value is shown as printed. Address, Charset, Contact ID and Subscription ID are as printed. "
                 "MMS Row says whether msg_id is the _id of a row of mms.txt in the same folder: yes, or no when "
                 "mms.txt is a full list of rows (or 'No result found.'). It is blank, with the reason in Parse Note, "
                 "when msg_id is empty or the text NULL, when the folder has no mms.txt, and when mms.txt is not a "
                 "full list (a provider error, rows followed by an error, rows that could not be split, an empty or "
                 "unrecognised file, a file that could not be read, or rows that print no _id column) and holds no "
                 "row with that _id. The report's source list names mms.txt next to "
                 "mms_addr.txt; Source File and Source Line stay those of the address row. The same addresses are "
                 "shown on the message rows of MMS (content query) as From, To, Cc and Bcc. ALEX up to commit "
                 "8f27e7a (prosch88/ALEX) writes no file when the output holds 'No result found' or "
                 "another of its four error strings anywhere, including inside a value; from ed3d41eb (2026-11-25) it "
                 "writes the file whenever the output holds a row. Content Query Files reports a missing file as "
                 "unknown; in an ALEX PRFS zip (from ed3d41eb), "
                 "which holds the file of every URI ALEX queries, as not in the extraction. "
                 "Format: rows are read from the text that the content command prints (AOSP Content.java, lines 664 to "
                 "706 at "
                 "https://android.googlesource.com/platform/frameworks/base/+/8d2ed506045d5d6cf25ef7ef77a30da910733657/cmds/content/src/com/android/commands/content/Content.java): "
                 "'Row: <n> ' and the name=value pairs joined with ', ', with no quoting or escaping. A NULL value "
                 "prints as the text NULL and a BLOB as the text BLOB, so a stored text NULL or BLOB cannot be told "
                 "apart from a real NULL or BLOB. An empty string prints as nothing and is blank here. A row is split "
                 "at ', <next column>=' along the column list that the rows of the file agree on; Parse Note flags a "
                 "row where a value holds ', <name>=' for a name of that list (the split may be off there) and a row "
                 "that could not be split. Columns not listed here are not shown (Content Query Files lists the "
                 "columns of each file), and a listed column that a device does not print is blank and named in the "
                 "log. Source Line is the line of the file where the row starts. Evidence tier: source-verified and "
                 "tested on synthetic files only.",
        "paths": ('*/content_provider_*/mms/mms_addr.txt', '*/extra/content_provider/mms/mms_addr.txt',
                  '*/content_provider_*/mms/mms.txt', '*/extra/content_provider/mms/mms.txt'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "users",
        "multiline_columns": ["Parse Note"],
    },
    "content_query_mms_parts": {
        "name": "MMS Parts (content query)",
        "description": "MMS part rows from the saved output of adb shell content query --uri content://mms/part, as "
                       "printed; the part content (media) is not in this output.",
        "author": "@Maxitelmo, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Messaging",
        "notes": "Read from ALEX raw text output only (content_provider_<serial>/mms/mms_part.txt, or "
                 "extra/content_provider/mms/mms_part.txt in an ALEX PRFS zip); android_triage "
        "does "
                 "not query MMS. A part row gives the part's message (mid, the _id of the row in MMS (content query)), "
                 "position (seq), content type (ct), names (name, fn, cl, cid), character set (chset), the path of the "
                 "part file on the device (_data) and, for a text part, its text. The content of a part file (a "
                 "picture, audio, video or other media) is not in content query output: it is read with a separate "
                 "command such as content read, and neither layout read here saves it, so the media was not collected "
                 "and is not linked. A _data path names where the provider kept the file on the device; the file "
                 "itself is not in these layouts. ALEX up to commit 8f27e7a (prosch88/ALEX) writes no file when the "
                 "output holds 'No result found' or "
                 "another of its four error strings anywhere, including inside a value; from ed3d41eb (2026-11-25) it "
                 "writes the file whenever the output holds a row. Content Query Files reports a missing file as "
                 "unknown; in an ALEX PRFS zip (from ed3d41eb), "
                 "which holds the file of every URI ALEX queries, as not in the extraction. "
                 "Format: rows are read from the text that the content command prints (AOSP Content.java, lines 664 to "
                 "706 at "
                 "https://android.googlesource.com/platform/frameworks/base/+/8d2ed506045d5d6cf25ef7ef77a30da910733657/cmds/content/src/com/android/commands/content/Content.java): "
                 "'Row: <n> ' and the name=value pairs joined with ', ', with no quoting or escaping. A NULL value "
                 "prints as the text NULL and a BLOB as the text BLOB, so a stored text NULL or BLOB cannot be told "
                 "apart from a real NULL or BLOB. An empty string prints as nothing and is blank here. Values are "
                 "shown "
                 "as printed, line breaks kept. A row is split at ', <next column>=' along the column list that the "
                 "rows of the file agree on; Parse Note flags a row where a value holds ', <name>=' for a name of that "
                 "list (the split may be off there) and a row that could not be split. A value line that is exactly "
                 "'Row: <next row number> <first column>=...' cannot be told apart from a new row. Rows are what the "
                 "provider returned to the shell user when the tool ran; deleted records are not in the output. "
                 "Columns not listed here are not shown (Content Query Files lists the columns of each file), and a "
                 "listed column that a device does not print is blank and named in the log. Source Line is the line "
                 "of the file where the row starts. Evidence tier: source-verified and tested on synthetic files "
                 "only.",
        "paths": ('*/content_provider_*/mms/mms_part.txt', '*/extra/content_provider/mms/mms_part.txt'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "paperclip",
        "multiline_columns": ["Text", "Parse Note"],
    },
    "content_query_call_log": {
        "name": "Call Log (content query)",
        "description": "Call rows from the saved output of adb shell content query --uri content://call_log/calls, "
                       "as printed, with the date read as milliseconds and the duration as seconds.",
        "author": "@Maxitelmo, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Calls & Contacts",
        "notes": "Read from ALEX raw text output only (content_provider_<serial>/call_log/call_log_calls.txt, or "
                 "extra/content_provider/call_log/call_log_calls.txt in an ALEX PRFS zip); "
                 "android_triage does not query the call log. Date is read as milliseconds since 1970-01-01 UTC and "
                 "Duration (s) is the duration value as printed, in seconds, per the provider contract "
                 "(CallLog.Calls.DATE, 'in milliseconds since the epoch', and CallLog.Calls.DURATION, 'in seconds', "
                 "https://developer.android.com/reference/android/provider/CallLog.Calls#DATE). A date of 0, NULL or "
                 "nothing is blank. Type is the type value as printed and the name of the CallLog.Calls constant with "
                 "that value (1 INCOMING_TYPE, 2 OUTGOING_TYPE, 3 MISSED_TYPE, 4 VOICEMAIL_TYPE, 5 REJECTED_TYPE, "
                 "6 BLOCKED_TYPE, 7 ANSWERED_EXTERNALLY_TYPE; "
                 "https://developer.android.com/reference/android/provider/CallLog.Calls#INCOMING_TYPE); another value "
                 "is shown as printed. Number, Name and the other columns are as printed; Name is a cached value the "
                 "provider keeps with the call. ALEX up to commit 8f27e7a (prosch88/ALEX) writes no file when the "
                 "output holds 'No result found' or "
                 "another of its four error strings anywhere, including inside a value; from ed3d41eb (2026-11-25) it "
                 "writes the file whenever the output holds a row. Content Query Files reports a missing file as "
                 "unknown; in an ALEX PRFS zip (from ed3d41eb), "
                 "which holds the file of every URI ALEX queries, as not in the extraction. "
                 "Format: rows are read from the text that the content command prints (AOSP Content.java, lines 664 to "
                 "706 at "
                 "https://android.googlesource.com/platform/frameworks/base/+/8d2ed506045d5d6cf25ef7ef77a30da910733657/cmds/content/src/com/android/commands/content/Content.java): "
                 "'Row: <n> ' and the name=value pairs joined with ', ', with no quoting or escaping. A NULL value "
                 "prints as the text NULL and a BLOB as the text BLOB, so a stored text NULL or BLOB cannot be told "
                 "apart from a real NULL or BLOB. An empty string prints as nothing and is blank here. Values are "
                 "shown "
                 "as printed, line breaks kept. A row is split at ', <next column>=' along the column list that the "
                 "rows of the file agree on; Parse Note flags a row where a value holds ', <name>=' for a name of that "
                 "list (the split may be off there) and a row that could not be split. A value line that is exactly "
                 "'Row: <next row number> <first column>=...' cannot be told apart from a new row. Rows are what the "
                 "provider returned to the shell user when the tool ran; deleted records are not in the output. "
                 "Columns not listed here are not shown (Content Query Files lists the columns of each file), and a "
                 "listed column that a device does not print is blank and named in the log. Source Line is the line "
                 "of the file where the row starts. Evidence tier: source-verified and tested on synthetic files "
                 "only.",
        "paths": ('*/content_provider_*/call_log/call_log_calls.txt',
                  '*/extra/content_provider/call_log/call_log_calls.txt'),
        "output_types": "standard",
        "artifact_icon": "phone",
        "multiline_columns": ["Parse Note"],
    },
    "content_query_contacts": {
        "name": "Contacts (content query)",
        "description": "Contact rows from the saved output of adb shell content query --uri "
                       "content://com.android.contacts/contacts, as printed.",
        "author": "@Maxitelmo, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Calls & Contacts",
        "notes": "Read from android_triage (<date>_contentprovider/contacts_contacts.txt) and ALEX raw text output "
                 "(content_provider_<serial>/com.android.contacts/com.android.contacts_contacts.txt, or "
                 "extra/content_provider/com.android.contacts/com.android.contacts_contacts.txt in an ALEX PRFS "
                 "zip). One row per "
                 "aggregated contact the provider returned; the phone numbers are in Contact Phone Numbers (content "
                 "query), keyed by Contact ID. Last Updated is contact_last_updated_timestamp read as milliseconds "
                 "since 1970-01-01 UTC, per the provider contract "
                 "(ContactsContract.ContactsColumns.CONTACT_LAST_UPDATED_TIMESTAMP, 'milliseconds since epoch', "
                 "https://developer.android.com/reference/android/provider/ContactsContract.ContactsColumns#CONTACT_LAST_UPDATED_TIMESTAMP); "
                 "a value of 0, NULL or nothing is blank. Display Name, Has Phone Number, Starred and Lookup Key are "
                 "as printed. ALEX up to commit 8f27e7a (prosch88/ALEX) writes no file when the output holds 'No "
                 "result found' or "
                 "another of its four error strings anywhere, including inside a value; from ed3d41eb (2026-11-25) it "
                 "writes the file whenever the output holds a row. Content Query Files reports a missing file as "
                 "unknown; in an ALEX PRFS zip (from ed3d41eb), "
                 "which holds the file of every URI ALEX queries, as not in the extraction. "
                 "Format: rows are read from the text that the content command prints (AOSP Content.java, lines 664 to "
                 "706 at "
                 "https://android.googlesource.com/platform/frameworks/base/+/8d2ed506045d5d6cf25ef7ef77a30da910733657/cmds/content/src/com/android/commands/content/Content.java): "
                 "'Row: <n> ' and the name=value pairs joined with ', ', with no quoting or escaping. A NULL value "
                 "prints as the text NULL and a BLOB as the text BLOB, so a stored text NULL or BLOB cannot be told "
                 "apart from a real NULL or BLOB. An empty string prints as nothing and is blank here. Values are "
                 "shown "
                 "as printed, line breaks kept. A row is split at ', <next column>=' along the column list that the "
                 "rows of the file agree on; Parse Note flags a row where a value holds ', <name>=' for a name of that "
                 "list (the split may be off there) and a row that could not be split. A value line that is exactly "
                 "'Row: <next row number> <first column>=...' cannot be told apart from a new row. Rows are what the "
                 "provider returned to the shell user when the tool ran; deleted records are not in the output. "
                 "Columns not listed here are not shown (Content Query Files lists the columns of each file), and a "
                 "listed column that a device does not print is blank and named in the log. Source Line is the line "
                 "of the file where the row starts. Source File holds the file each row came from. Evidence tier: "
                 "source-verified and tested on synthetic files only.",
        "paths": ('*/*_contentprovider/contacts_contacts.txt',
                  '*/content_provider_*/com.android.contacts/com.android.contacts_contacts.txt',
                  '*/extra/content_provider/com.android.contacts/com.android.contacts_contacts.txt'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "users",
        "multiline_columns": ["Display Name", "Parse Note"],
    },
    "content_query_contact_phones": {
        "name": "Contact Phone Numbers (content query)",
        "description": "Phone number rows from the saved output of adb shell content query --uri "
                       "content://com.android.contacts/data/phones, as printed.",
        "author": "@Maxitelmo, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Calls & Contacts",
        "notes": "Read from android_triage (<date>_contentprovider/contacts_data_phones.txt) and ALEX raw text output "
                 "(content_provider_<serial>/com.android.contacts/com.android.contacts_data_phones.txt, or "
                 "extra/content_provider/com.android.contacts/com.android.contacts_data_phones.txt in an ALEX PRFS "
                 "zip). One row per "
                 "phone number data row. Number is data1, Phone Type data2, Label data3 and Normalized Number data4, "
                 "as "
                 "printed (ContactsContract.CommonDataKinds.Phone NUMBER, TYPE, LABEL and NORMALIZED_NUMBER, "
                 "https://developer.android.com/reference/android/provider/ContactsContract.CommonDataKinds.Phone); "
                 "Phone Type is not decoded. Account Type and Account Name are the account of the raw contact the "
                 "number belongs to, as printed. Contact Last Updated is contact_last_updated_timestamp read as "
                 "milliseconds since 1970-01-01 UTC, per the provider contract "
                 "(ContactsContract.ContactsColumns.CONTACT_LAST_UPDATED_TIMESTAMP, 'milliseconds since epoch', "
                 "https://developer.android.com/reference/android/provider/ContactsContract.ContactsColumns#CONTACT_LAST_UPDATED_TIMESTAMP); "
                 "it belongs to the aggregated contact, not to the number, and a value of 0, NULL or nothing is blank. "
                 "A value can end with a line break that the provider stores; it is kept. ALEX up to commit 8f27e7a "
                 "(prosch88/ALEX) writes no file when the output holds 'No result found' or "
                 "another of its four error strings anywhere, including inside a value; from ed3d41eb (2026-11-25) it "
                 "writes the file whenever the output holds a row. Content Query Files reports a missing file as "
                 "unknown; in an ALEX PRFS zip (from ed3d41eb), "
                 "which holds the file of every URI ALEX queries, as not in the extraction. "
                 "Format: rows are read from the text that the content command prints (AOSP Content.java, lines 664 to "
                 "706 at "
                 "https://android.googlesource.com/platform/frameworks/base/+/8d2ed506045d5d6cf25ef7ef77a30da910733657/cmds/content/src/com/android/commands/content/Content.java): "
                 "'Row: <n> ' and the name=value pairs joined with ', ', with no quoting or escaping. A NULL value "
                 "prints as the text NULL and a BLOB as the text BLOB, so a stored text NULL or BLOB cannot be told "
                 "apart from a real NULL or BLOB. An empty string prints as nothing and is blank here. Values are "
                 "shown "
                 "as printed, line breaks kept. A row is split at ', <next column>=' along the column list that the "
                 "rows of the file agree on; Parse Note flags a row where a value holds ', <name>=' for a name of that "
                 "list (the split may be off there) and a row that could not be split. A value line that is exactly "
                 "'Row: <next row number> <first column>=...' cannot be told apart from a new row. Rows are what the "
                 "provider returned to the shell user when the tool ran; deleted records are not in the output. "
                 "Columns not listed here are not shown (Content Query Files lists the columns of each file), and a "
                 "listed column that a device does not print is blank and named in the log. Source Line is the line "
                 "of the file where the row starts. Source File holds the file each row came from. Evidence tier: "
                 "source-verified and tested on synthetic files only.",
        "paths": ('*/*_contentprovider/contacts_data_phones.txt',
                  '*/content_provider_*/com.android.contacts/com.android.contacts_data_phones.txt',
                  '*/extra/content_provider/com.android.contacts/com.android.contacts_data_phones.txt'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "users",
        "multiline_columns": ["Display Name", "Parse Note"],
    },
    "content_query_calendar_events": {
        "name": "Calendar Events (content query)",
        "description": "Calendar event rows from the saved output of adb shell content query --uri "
                       "content://com.android.calendar/events, as printed, with start and end read as milliseconds.",
        "author": "@Maxitelmo, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Productivity",
        "notes": "Read from android_triage only (<date>_contentprovider/calendar_events.txt); ALEX does not query "
                 "content://com.android.calendar/events, and its event_entities output is read by Calendar Event "
                 "Entities (content query). Start and End are dtstart and dtend read as milliseconds since 1970-01-01 "
                 "UTC, per the provider contract (CalendarContract.EventsColumns.DTSTART and DTEND, 'UTC millis since "
                 "epoch', https://developer.android.com/reference/android/provider/CalendarContract.EventsColumns#DTSTART); "
                 "a value of 0, NULL or nothing is blank. Per the contract a recurring event is one row whatever the "
                 "number of times it repeats and carries duration (not shown) rather than dtend, and an all-day event "
                 "has eventTimezone UTC and times on a midnight boundary (CalendarContract.Events, "
                 "https://developer.android.com/reference/android/provider/CalendarContract.Events). Time Zone is "
                 "eventTimezone, All Day is allDay, Recurrence Rule is rrule, Deleted is deleted, all as printed. "
                 "Title, Description and Location are as printed. "
                 "Format: rows are read from the text that the content command prints (AOSP Content.java, lines 664 to "
                 "706 at "
                 "https://android.googlesource.com/platform/frameworks/base/+/8d2ed506045d5d6cf25ef7ef77a30da910733657/cmds/content/src/com/android/commands/content/Content.java): "
                 "'Row: <n> ' and the name=value pairs joined with ', ', with no quoting or escaping. A NULL value "
                 "prints as the text NULL and a BLOB as the text BLOB, so a stored text NULL or BLOB cannot be told "
                 "apart from a real NULL or BLOB. An empty string prints as nothing and is blank here. Values are "
                 "shown "
                 "as printed, line breaks kept. A row is split at ', <next column>=' along the column list that the "
                 "rows of the file agree on; Parse Note flags a row where a value holds ', <name>=' for a name of that "
                 "list (the split may be off there) and a row that could not be split. A value line that is exactly "
                 "'Row: <next row number> <first column>=...' cannot be told apart from a new row. Rows are what the "
                 "provider returned to the shell user when the tool ran. Columns not listed here are not shown "
                 "(Content Query Files lists the columns of each file), and a listed column that a device does not "
                 "print is blank and named in the log. Source Line is the line of the file where the row starts. "
                 "Evidence tier: source-verified and tested on synthetic files only.",
        "paths": ('*/*_contentprovider/calendar_events.txt',),
        "output_types": "standard",
        "artifact_icon": "calendar",
        "multiline_columns": ["Title", "Description", "Location", "Parse Note"],
    },
    "content_query_calendar_event_entities": {
        "name": "Calendar Event Entities (content query)",
        "description": "Calendar event rows from the saved output of adb shell content query --uri "
                       "content://com.android.calendar/event_entities, as printed, with start and end read as "
                       "milliseconds.",
        "author": "@Maxitelmo, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Productivity",
        "notes": "Read from android_triage (<date>_contentprovider/calendar_event_entities.txt) and ALEX raw text "
                 "output (content_provider_<serial>/com.android.calendar/com.android.calendar_event_entities.txt, or "
                 "extra/content_provider/com.android.calendar/com.android.calendar_event_entities.txt in an ALEX "
                 "PRFS zip). "
                 "This is a second URI of the same provider as Calendar Events (content query); android_triage "
                 "queries both, so an event can be in both artifacts. Start and End are dtstart and dtend read as "
                 "milliseconds since 1970-01-01 UTC, per the provider contract (CalendarContract.EventsColumns.DTSTART "
                 "and DTEND, 'UTC millis since epoch', "
                 "https://developer.android.com/reference/android/provider/CalendarContract.EventsColumns#DTSTART); a "
                 "value of 0, NULL or nothing is blank, and per the contract a recurring event is one row and carries "
                 "duration rather than dtend (CalendarContract.Events, "
                 "https://developer.android.com/reference/android/provider/CalendarContract.Events). Time Zone is "
                 "eventTimezone, All Day is allDay, Recurrence Rule is rrule, Deleted is deleted, all as printed. "
                 "Title, Description "
                 "and Location are as printed. ALEX up to commit 8f27e7a (prosch88/ALEX) writes no file when the "
                 "output holds 'No result found' or "
                 "another of its four error strings anywhere, including inside a value; from ed3d41eb (2026-11-25) it "
                 "writes the file whenever the output holds a row. Content Query Files reports a missing file as "
                 "unknown; in an ALEX PRFS zip (from ed3d41eb), "
                 "which holds the file of every URI ALEX queries, as not in the extraction. "
                 "Format: rows are read from the text that the content command prints (AOSP Content.java, lines 664 to "
                 "706 at "
                 "https://android.googlesource.com/platform/frameworks/base/+/8d2ed506045d5d6cf25ef7ef77a30da910733657/cmds/content/src/com/android/commands/content/Content.java): "
                 "'Row: <n> ' and the name=value pairs joined with ', ', with no quoting or escaping. A NULL value "
                 "prints as the text NULL and a BLOB as the text BLOB, so a stored text NULL or BLOB cannot be told "
                 "apart from a real NULL or BLOB. An empty string prints as nothing and is blank here. Values are "
                 "shown "
                 "as printed, line breaks kept. A row is split at ', <next column>=' along the column list that the "
                 "rows of the file agree on; Parse Note flags a row where a value holds ', <name>=' for a name of that "
                 "list (the split may be off there) and a row that could not be split. A value line that is exactly "
                 "'Row: <next row number> <first column>=...' cannot be told apart from a new row. Rows are what the "
                 "provider returned to the shell user when the tool ran. Columns not listed here are not shown "
                 "(Content Query Files lists the columns of each file), and a listed column that a device does not "
                 "print is blank and named in the log. Source Line is the line of the file where the row starts. "
                 "Source File holds the file each row came from. Evidence tier: source-verified and tested on "
                 "synthetic files only.",
        "paths": ('*/*_contentprovider/calendar_event_entities.txt',
                  '*/content_provider_*/com.android.calendar/com.android.calendar_event_entities.txt',
                  '*/extra/content_provider/com.android.calendar/com.android.calendar_event_entities.txt'),
        "output_types": "standard",
        "artifact_icon": "calendar",
        "multiline_columns": ["Title", "Description", "Location", "Parse Note"],
    },
    "content_query_calendars": {
        "name": "Calendars (content query)",
        "description": "Calendar rows from the saved output of adb shell content query --uri "
                       "content://com.android.calendar/calendars, as printed.",
        "author": "@Maxitelmo, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Productivity",
        "notes": "Read from android_triage (<date>_contentprovider/calendar_calendars.txt) and ALEX raw text output "
                 "(content_provider_<serial>/com.android.calendar/com.android.calendar_calendars.txt, or "
                 "extra/content_provider/com.android.calendar/com.android.calendar_calendars.txt in an ALEX PRFS "
                 "zip). One row per "
                 "calendar; Calendar ID is the _id that the event rows name in their calendar_id. Account Name, "
                 "Account Type, Display Name (calendar_displayName), Owner Account (ownerAccount), Visible, Sync "
                 "Events "
                 "and Deleted are as printed. ALEX up to commit 8f27e7a (prosch88/ALEX) writes no file when the "
                 "output holds 'No result found' or "
                 "another of its four error strings anywhere, including inside a value; from ed3d41eb (2026-11-25) it "
                 "writes the file whenever the output holds a row. Content Query Files reports a missing file as "
                 "unknown; in an ALEX PRFS zip (from ed3d41eb), "
                 "which holds the file of every URI ALEX queries, as not in the extraction. "
                 "Format: rows are read from the text that the content command prints (AOSP Content.java, lines 664 to "
                 "706 at "
                 "https://android.googlesource.com/platform/frameworks/base/+/8d2ed506045d5d6cf25ef7ef77a30da910733657/cmds/content/src/com/android/commands/content/Content.java): "
                 "'Row: <n> ' and the name=value pairs joined with ', ', with no quoting or escaping. A NULL value "
                 "prints as the text NULL and a BLOB as the text BLOB, so a stored text NULL or BLOB cannot be told "
                 "apart from a real NULL or BLOB. An empty string prints as nothing and is blank here. Values are "
                 "shown "
                 "as printed, line breaks kept. A row is split at ', <next column>=' along the column list that the "
                 "rows of the file agree on; Parse Note flags a row where a value holds ', <name>=' for a name of that "
                 "list (the split may be off there) and a row that could not be split. Columns not listed here are not "
                 "shown (Content Query Files lists the columns of each file), and a listed column that a device does "
                 "not print is blank and named in the log. Source Line is the line of the file where the row starts. "
                 "Source File holds the file each row came from. Evidence tier: source-verified and tested on "
                 "synthetic files only.",
        "paths": ('*/*_contentprovider/calendar_calendars.txt',
                  '*/content_provider_*/com.android.calendar/com.android.calendar_calendars.txt',
                  '*/extra/content_provider/com.android.calendar/com.android.calendar_calendars.txt'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "calendar",
        "multiline_columns": ["Parse Note"],
    },
    "content_query_media_files": {
        "name": "MediaStore Files (content query)",
        "description": "MediaStore file rows from the saved output of adb shell content query --uri "
                       "content://media/external/file, as printed, with dates read per the MediaStore contract.",
        "author": "@Maxitelmo, Claude",
        "creation_date": "2026-11-25",
        "last_update_date": "2026-11-27",
        "requirements": "none",
        "category": "Photos & Media",
        "notes": "Read from android_triage (<date>_contentprovider/media_external_file.txt) and ALEX raw text output "
                 "(content_provider_<serial>/media/media_external_file.txt, or "
                 "extra/content_provider/media/media_external_file.txt in an ALEX PRFS zip). One row per file the "
                 "MediaStore indexed "
                 "on external storage and returned to the shell user; the files themselves are not in this output. "
                 "Date Added and Date Modified are date_added and date_modified read as seconds since 1970-01-01 UTC, "
                 "and Date Taken is datetaken read as milliseconds since 1970-01-01 UTC, per the provider contract "
                 "(MediaStore.MediaColumns.DATE_ADDED and DATE_MODIFIED, 'number of seconds since "
                 "1970-01-01T00:00:00Z', and DATE_TAKEN, 'number of milliseconds since 1970-01-01T00:00:00Z', "
                 "https://developer.android.com/reference/android/provider/MediaStore.MediaColumns#DATE_ADDED); a "
                 "value of 0, NULL or nothing is blank. The contract says date_modified is the indexed "
                 "File.lastModified() and datetaken is taken from the file's metadata (MediaMetadataRetriever or "
                 "EXIF). "
                 "Owner Package is owner_package_name, the package the contract says contributed the item, which can "
                 "be NULL, and whose visibility from Android 14 depends on package visibility. Path (_data), Display "
                 "Name, Relative Path, Volume, MIME Type, Size, Bucket, Trashed (is_trashed) and Pending (is_pending) "
                 "are as printed; MediaStore columns differ between Android versions, so some can be blank. ALEX up "
                 "to commit 8f27e7a (prosch88/ALEX) writes no file when the output holds 'No result found' or "
                 "another of its four error strings anywhere, including inside a value; from ed3d41eb (2026-11-25) it "
                 "writes the file whenever the output holds a row. Content Query Files reports a missing file as "
                 "unknown; in an ALEX PRFS zip (from ed3d41eb), "
                 "which holds the file of every URI ALEX queries, as not in the extraction. "
                 "Format: rows are read from the text that the content command prints (AOSP Content.java, lines 664 to "
                 "706 at "
                 "https://android.googlesource.com/platform/frameworks/base/+/8d2ed506045d5d6cf25ef7ef77a30da910733657/cmds/content/src/com/android/commands/content/Content.java): "
                 "'Row: <n> ' and the name=value pairs joined with ', ', with no quoting or escaping. A NULL value "
                 "prints as the text NULL and a BLOB as the text BLOB, so a stored text NULL or BLOB cannot be told "
                 "apart from a real NULL or BLOB. An empty string prints as nothing and is blank here. Values are "
                 "shown "
                 "as printed. A row is split at ', <next column>=' along the column list that the rows of the file "
                 "agree on; Parse Note flags a row where a value holds ', <name>=' for a name of that list (the split "
                 "may be off there) and a row that could not be split. Columns not listed here are not shown (Content "
                 "Query Files lists the columns of each file), and a listed column that a device does not print is "
                 "blank and named in the log. Source Line is the line of the file where the row starts. Source File "
                 "holds the file each row came from. Evidence tier: source-verified and tested on synthetic files "
                 "only.",
        "paths": ('*/*_contentprovider/media_external_file.txt', '*/content_provider_*/media/media_external_file.txt',
                  '*/extra/content_provider/media/media_external_file.txt'),
        "output_types": "standard",
        "artifact_icon": "photo",
        "multiline_columns": ["Parse Note"],
    },
}

from scripts import content_query_reader as reader
from scripts.ilapfuncs import artifact_processor, logfunc

SMS_TYPES = {'0': 'ALL', '1': 'INBOX', '2': 'SENT', '3': 'DRAFT', '4': 'OUTBOX', '5': 'FAILED', '6': 'QUEUED'}
MMS_BOXES = {'0': 'ALL', '1': 'INBOX', '2': 'SENT', '3': 'DRAFTS', '4': 'OUTBOX', '5': 'FAILED'}
# PduHeaders address field values, as the addr rows print them in their type column.
ADDRESS_TYPES = {'129': 'BCC', '130': 'CC', '137': 'FROM', '151': 'TO'}
ADDRESS_CODES = ('137', '151', '130', '129')
NOTE_ADDRESSES_UNKNOWN = ('addresses unknown: no mms/mms_addr.txt in this folder (ALEX writes none when the query '
                          'printed no row or an error, and up to commit 8f27e7a also when the output holds one of '
                          'its four error strings)')
NOTE_ADDRESSES_ABSENT = ('addresses unknown: no mms/mms_addr.txt in this folder of the extraction (ALEX writes one '
                         'into its PRFS zip for every query it runs)')
NOTE_URI_FROM_STATUS = 'URI as the status file names it'
NOTE_STATUS_NOT_COMPARED = ('the status was not compared with the text: the status file names no URI that can '
                            'be read')
NOTE_NO_ADDRESS_ROWS = 'no FROM, TO, CC or BCC rows for this message in mms_addr.txt'
NOTE_ADDRESSES_INCOMPLETE = ('addresses unknown: no FROM, TO, CC or BCC row for this message was read, and '
                             'mms_addr.txt is incomplete ({reason})')
NOTE_ADDRESSES_PARTIAL = ('addresses may be partial: mms_addr.txt is incomplete ({reason}), so FROM, TO, CC or BCC '
                          'rows for this message may be missing')
NOTE_NO_MMS_KEY = 'addresses unknown: this row has no usable _id (empty or NULL) to match msg_id against'
NOTE_NO_ADDR_KEY = 'MMS row unknown: msg_id is empty or NULL'
NOTE_MMS_ROW_INCOMPLETE = 'MMS row unknown: no MMS row with this _id was read, and mms.txt is incomplete ({reason})'
NOTE_MMS_ROW_NO_FILE = 'MMS row unknown: no mms/mms.txt in this folder'
CALL_TYPES = {'1': 'INCOMING_TYPE', '2': 'OUTGOING_TYPE', '3': 'MISSED_TYPE', '4': 'VOICEMAIL_TYPE',
              '5': 'REJECTED_TYPE', '6': 'BLOCKED_TYPE', '7': 'ANSWERED_EXTERNALLY_TYPE'}

# Columns of each artifact: (header, column name in the dump, how the value is shown).
# 'ms' and 's' are times read as milliseconds or seconds since 1970-01-01 UTC; a dict
# names the contract constant of a value next to the value as printed; None is as printed.
COLUMNS = {
    'sms': (
        ('Date', 'date', 'ms'), ('Date Sent', 'date_sent', 'ms'), ('Type', 'type', SMS_TYPES),
        ('Address', 'address', None), ('Body', 'body', None), ('Read', 'read', None), ('Seen', 'seen', None),
        ('Thread ID', 'thread_id', None), ('Subscription ID', 'sub_id', None), ('Creator', 'creator', None),
        ('Message ID', '_id', None)),
    'mms': (
        ('Date', 'date', 's'), ('Date Sent', 'date_sent', 's'), ('Message Box', 'msg_box', MMS_BOXES),
        ('Subject', 'sub', None), ('Message Type', 'm_type', None), ('Content Type', 'ct_t', None),
        ('Read', 'read', None), ('Seen', 'seen', None), ('Text Only', 'text_only', None),
        ('Thread ID', 'thread_id', None), ('Subscription ID', 'sub_id', None), ('Creator', 'creator', None),
        ('Message ID', '_id', None)),
    'mms_part': (
        ('Message ID', 'mid', None), ('Sequence', 'seq', None), ('Content Type', 'ct', None), ('Name', 'name', None),
        ('File Name', 'fn', None), ('Content Location', 'cl', None), ('Content ID', 'cid', None),
        ('Charset', 'chset', None), ('Text', 'text', None), ('Device Path', '_data', None), ('Part ID', '_id', None)),
    'call_log': (
        ('Date', 'date', 'ms'), ('Type', 'type', CALL_TYPES), ('Number', 'number', None), ('Name', 'name', None),
        ('Duration (s)', 'duration', None), ('Presentation', 'presentation', None),
        ('Phone Account ID', 'subscription_id', None), ('Geocoded Location', 'geocoded_location', None),
        ('Country ISO', 'countryiso', None), ('Call ID', '_id', None)),
    'contacts': (
        ('Last Updated', 'contact_last_updated_timestamp', 'ms'), ('Display Name', 'display_name', None),
        ('Has Phone Number', 'has_phone_number', None), ('Starred', 'starred', None),
        ('Lookup Key', 'lookup', None), ('Contact ID', '_id', None)),
    'contact_phones': (
        ('Contact Last Updated', 'contact_last_updated_timestamp', 'ms'), ('Display Name', 'display_name', None),
        ('Number', 'data1', None), ('Phone Type', 'data2', None), ('Label', 'data3', None),
        ('Normalized Number', 'data4', None), ('Account Type', 'account_type', None),
        ('Account Name', 'account_name', None), ('Contact ID', 'contact_id', None),
        ('Raw Contact ID', 'raw_contact_id', None), ('Data ID', '_id', None)),
    'calendar_events': (
        ('Start', 'dtstart', 'ms'), ('End', 'dtend', 'ms'), ('Time Zone', 'eventTimezone', None),
        ('All Day', 'allDay', None), ('Title', 'title', None), ('Description', 'description', None),
        ('Location', 'eventLocation', None), ('Organizer', 'organizer', None), ('Recurrence Rule', 'rrule', None),
        ('Deleted', 'deleted', None), ('Calendar ID', 'calendar_id', None), ('Event ID', '_id', None)),
    'calendars': (
        ('Display Name', 'calendar_displayName', None), ('Account Name', 'account_name', None),
        ('Account Type', 'account_type', None), ('Owner Account', 'ownerAccount', None),
        ('Visible', 'visible', None), ('Sync Events', 'sync_events', None), ('Deleted', 'deleted', None),
        ('Calendar ID', '_id', None)),
    'media_files': (
        ('Date Added', 'date_added', 's'), ('Date Modified', 'date_modified', 's'), ('Date Taken', 'datetaken', 'ms'),
        ('Path', '_data', None), ('Display Name', '_display_name', None), ('Relative Path', 'relative_path', None),
        ('Volume', 'volume_name', None), ('MIME Type', 'mime_type', None), ('Size', '_size', None),
        ('Owner Package', 'owner_package_name', None), ('Bucket', 'bucket_display_name', None),
        ('Trashed', 'is_trashed', None), ('Pending', 'is_pending', None), ('File ID', '_id', None)),
}
COLUMNS['calendar_event_entities'] = COLUMNS['calendar_events']
COLUMNS['mms_addr'] = (
    ('Message ID', 'msg_id', None), ('Address Type', 'type', ADDRESS_TYPES), ('Address', 'address', None),
    ('Charset', 'charset', None), ('Contact ID', 'contact_id', None), ('Subscription ID', 'sub_id', None),
    ('Address ID', '_id', None))

# Columns taken from another file of the same folder: (position, headers). MMS rows get the
# addresses of their msg_id by type; address rows say whether their msg_id is an MMS row.
JOINED_HEADERS = {'mms': (3, ['From', 'To', 'Cc', 'Bcc']), 'mms_addr': (1, ['MMS Row'])}
# Files an artifact reads only to join, and does not report rows of.
JOINED_FROM = {'mms': ('mms_addr',), 'mms_addr': ('mms',)}

READ_BY = {
    'sms': 'SMS (content query)', 'mms': 'MMS (content query)', 'mms_part': 'MMS Parts (content query)',
    'mms_addr': 'MMS Addresses (content query)',
    'call_log': 'Call Log (content query)', 'contacts': 'Contacts (content query)',
    'contact_phones': 'Contact Phone Numbers (content query)', 'calendar_events': 'Calendar Events (content query)',
    'calendar_event_entities': 'Calendar Event Entities (content query)', 'calendars': 'Calendars (content query)',
    'media_files': 'MediaStore Files (content query)',
}


def _relative(context, path):
    """Path inside the extraction, with '/' separators on every platform."""
    return context.get_relative_path(path).replace('\\', '/').rstrip('/')


def _headers(key, with_source_file):
    headers = []
    for header, _column, shown in COLUMNS[key]:
        if shown in ('ms', 's'):
            headers.append((f'{header} (UTC)', 'datetime'))
        else:
            headers.append(header)
    if key in JOINED_HEADERS:
        position, extra = JOINED_HEADERS[key]
        headers[position:position] = extra
    headers += ['Parse Note', 'Source Line']
    if with_source_file:
        headers.append('Source File')
    return tuple(headers)


def _shown(value, shown, notes):
    if shown in ('ms', 's'):
        moment, note = reader.epoch_to_utc(value, shown)
        if note:
            notes.append(note)
        return moment
    if isinstance(shown, dict) and value in shown:
        return f'{value} ({shown[value]})'
    return value


def _sibling(context, layout, key):
    """The file of URI ``key`` in the same layout folder, from this artifact's files found, or None."""
    for other in context.get_files_found():
        other_layout = reader.layout_of(other)
        uri = reader.uri_of(other_layout[0], other) if other_layout else None
        if other_layout == layout and uri is not None and uri.key == key:
            return other
    return None


def _usable_key(value):
    """True for a join key that can be matched: not empty and not the text NULL."""
    return value.strip() not in ('', 'NULL')


def _incomplete(dump):
    """Why a sibling dump cannot be taken as the full list of its rows, or '' when it can."""
    if dump.status not in (reader.ROWS, reader.NO_RESULT):
        return reader.status_text(dump)
    if dump.detail:
        count = len(dump.records)
        return f'{count} row{"" if count == 1 else "s"}, {dump.detail}'
    unsplit = sum(1 for record in dump.records if not record.pairs)
    if unsplit:
        return f'{unsplit} row(s) not split'
    return ''


def _read_error(error):
    """An OSError as report text, without the path it names (a path on the examiner's machine)."""
    return f'could not be read: {type(error).__name__}' + (f' ({error.strerror})' if error.strerror else '')


def _sibling_dump(context, path, relative, required):
    """(dump, reason) of a sibling file; dump is None when it could not be read. A dump with rows that
    lacks a column of ``required`` cannot say that a key is absent from it, so it gets a reason too."""
    try:
        dump = reader.read_file(path, context.get_seeker())
    except OSError as error:
        logfunc(f'Content query {relative}: {_relative(context, path)} {_read_error(error)}')
        return None, _read_error(error)
    reason = _incomplete(dump)
    missing = [column for column in required if dump.records and column not in dump.columns]
    if missing:
        reason = '; '.join(filter(None, [reason, f'it prints no {" or ".join(missing)} column']))
    return dump, reason


def _joined(context, key, layout, relative):
    """(function of a row's Values and its note list giving the extra values, sibling path), or (None, None)."""
    if key == 'mms':
        addr_path = _sibling(context, layout, 'mms_addr')
        if addr_path is None:
            logfunc(f'Content query {relative}: no mms_addr.txt in this folder, From, To, Cc and Bcc are unknown')

            def unknown(_values, notes):
                notes.append(NOTE_ADDRESSES_ABSENT if layout[0] == reader.ALEX_PRFS else NOTE_ADDRESSES_UNKNOWN)
                return ['', '', '', '']
            return unknown, None
        dump, reason = _sibling_dump(context, addr_path, relative, ('msg_id', 'type'))
        addresses = {}
        for record in (dump.records if dump else []):
            values = reader.Values(record)
            if _usable_key(values['msg_id']):
                addresses.setdefault(values['msg_id'], {}).setdefault(values['type'], []).append(values['address'])
        logfunc(f'Content query {relative}: addresses from {_relative(context, addr_path)}'
                + (f', which is incomplete ({reason})' if reason else ''))

        def found(values, notes):
            if not _usable_key(values['_id']):
                notes.append(NOTE_NO_MMS_KEY)
                return ['', '', '', '']
            by_type = addresses.get(values['_id'], {})
            shown = ['; '.join(by_type.get(code, [])) for code in ADDRESS_CODES]
            if not any(code in by_type for code in ADDRESS_CODES):
                notes.append(NOTE_ADDRESSES_INCOMPLETE.format(reason=reason) if reason else NOTE_NO_ADDRESS_ROWS)
            elif reason:
                notes.append(NOTE_ADDRESSES_PARTIAL.format(reason=reason))
            return shown
        return found, addr_path
    if key == 'mms_addr':
        mms_path = _sibling(context, layout, 'mms')
        if mms_path is None:
            logfunc(f'Content query {relative}: no mms.txt in this folder to match msg_id against')

            def no_mms(_values, notes):
                notes.append(NOTE_MMS_ROW_NO_FILE)
                return ['']
            return no_mms, None
        dump, reason = _sibling_dump(context, mms_path, relative, ('_id',))
        ids = {reader.Values(record)['_id'] for record in (dump.records if dump else [])}
        ids = {value for value in ids if _usable_key(value)}

        def match(values, notes):
            if not _usable_key(values['msg_id']):
                notes.append(NOTE_NO_ADDR_KEY)
                return ['']
            if values['msg_id'] in ids:
                return ['yes']
            if reason:
                notes.append(NOTE_MMS_ROW_INCOMPLETE.format(reason=reason))
                return ['']
            return ['no']
        return match, mms_path
    return None, None


def _read(context, key, with_source_file=True):
    rows, sources = [], []
    run = context.get_seeker()
    for path in sorted(context.get_files_found()):
        layout = reader.layout_of(path)
        relative = _relative(context, path)
        uri = reader.uri_of(layout[0], path) if layout else None
        if uri is not None and uri.key in JOINED_FROM.get(key, ()):
            continue
        if uri is None or uri.key != key:
            logfunc(f'Content query: {relative} is not in a known layout folder, not read')
            continue
        sources.append(path)
        try:
            dump = reader.read_file(path, run)
        except OSError as error:
            logfunc(f'Content query {layout[0]} {relative}: {_read_error(error)}; its rows are not reported')
            continue
        joined, sibling = _joined(context, key, layout, relative)
        if sibling is not None and sibling not in sources:
            sources.append(sibling)
        logfunc(f'Content query {layout[0]} {relative}: {reader.status_text(dump)}')
        for warning in dump.warnings:
            logfunc(f'Content query {relative}: {warning}')
        if dump.status == reader.ROWS:
            absent = [column for _header, column, _shown_as in COLUMNS[key] if column not in dump.columns]
            if absent:
                logfunc(f'Content query {relative}: columns not printed in this file, left blank: {", ".join(absent)}')
        if key == 'mms_part' and dump.records:
            logfunc(f'Content query {relative}: part content (media) is not in content query output and was not '
                    f'collected by this layout; part rows are listed without it')
        for record in dump.records:
            values = reader.Values(record)
            notes = [record.note] if record.note else []
            row = [_shown(values[column], shown, notes) for _header, column, shown in COLUMNS[key]]
            if joined is not None:
                position = JOINED_HEADERS[key][0]
                row[position:position] = joined(values, notes)
            row += ['; '.join(notes), record.line]
            if with_source_file:
                row.append(relative)
            rows.append(tuple(row))
    return _headers(key, with_source_file), rows, '\n'.join(sources)


@artifact_processor
def content_query_sms(context):
    return _read(context, 'sms')


@artifact_processor
def content_query_mms(context):
    return _read(context, 'mms')


@artifact_processor
def content_query_mms_addresses(context):
    return _read(context, 'mms_addr')


@artifact_processor
def content_query_mms_parts(context):
    return _read(context, 'mms_part')


@artifact_processor
def content_query_call_log(context):
    return _read(context, 'call_log')


@artifact_processor
def content_query_contacts(context):
    return _read(context, 'contacts')


@artifact_processor
def content_query_contact_phones(context):
    return _read(context, 'contact_phones')


@artifact_processor
def content_query_calendar_events(context):
    return _read(context, 'calendar_events')


@artifact_processor
def content_query_calendar_event_entities(context):
    return _read(context, 'calendar_event_entities')


@artifact_processor
def content_query_calendars(context):
    return _read(context, 'calendars')


@artifact_processor
def content_query_media_files(context):
    return _read(context, 'media_files')


@artifact_processor
def content_query_files(context):
    headers = ('Layout', 'Folder', 'URI', 'File', 'Status', 'Tool Status', ('Rows', 'number'), 'Detail', 'Columns',
               'Read By')
    # Status files are kept per output folder, as status_file_of names it, so a PRFS folder found
    # inside another one keeps its own.
    folders, statuses_by_folder = {}, {}
    for path in context.get_files_found():
        layout = reader.layout_of(path)
        if layout is not None:
            folders.setdefault(layout, []).append(path)
            continue
        status_file = reader.status_file_of(path)
        if status_file is not None:
            layout_name, folder, output = status_file
            folders.setdefault((layout_name, folder), [])
            statuses_by_folder.setdefault((layout_name, folder), {})[_relative(context, output)] = path
    rows, sources = [], []
    for (layout, folder), paths in sorted(folders.items()):
        statuses = statuses_by_folder.get((layout, folder), {})
        by_name = {}
        for path in paths:
            uri = reader.uri_of(layout, path)
            by_name[uri.key if uri else path] = path
        folder_relative = _relative(context, folder)
        for uri in reader.URIS:
            name = reader.layout_file(layout, uri)
            if name is None:
                rows.append((layout, folder_relative, uri.uri, '', 'not queried by this tool', '', '', '', '',
                             READ_BY[uri.key]))
                continue
            path = by_name.pop(uri.key, None)
            if path is None:
                status_path = statuses.pop(f'{folder_relative}/{name}', None)
                if status_path is not None:
                    rows.append(_status_only_row(layout, folder_relative, uri.uri, name, status_path,
                                                 READ_BY[uri.key]))
                    sources.append(status_path)
                    continue
                rows.append((layout, folder_relative, uri.uri, name, reader.NO_FILE, '', '',
                             reader.missing_file_detail(layout), '', READ_BY[uri.key]))
                continue
            rows.append(_file_row(context, layout, folder_relative, uri.uri, path, READ_BY[uri.key], statuses,
                                  sources))
            sources.append(path)
        for path in sorted(by_name.values()):
            rows.append(_file_row(context, layout, folder_relative, '', path, 'not read', statuses, sources))
            sources.append(path)
        prefix = folder_relative + '/'
        for output in sorted(statuses):
            status_path = statuses.pop(output)
            name = output[len(prefix):] if output.startswith(prefix) else output
            rows.append(_status_only_row(layout, folder_relative, '', name, status_path, 'not read'))
            sources.append(status_path)
    return headers, rows, '\n'.join(sources)


def _tool_status(layout, relative, statuses, sources):
    """(ALEX's status, the URI it names, problem) from the .status.json beside a PRFS zip file; all '' for
    the other layouts."""
    if layout != reader.ALEX_PRFS:
        return '', '', ''
    status_path = statuses.pop(relative, None)
    if status_path is None:
        return '', '', f'no {reader.STATUS_SUFFIX} beside this file'
    sources.append(status_path)
    return reader.read_tool_status(status_path)


def _shown_uri(uri, tool_uri, notes):
    """The URI of a row: the one its file name gives, or the one its status file names when the name
    gives none (noted). A status file naming another URI than the file name gives is noted too."""
    if not uri:
        if tool_uri:
            notes.append(NOTE_URI_FROM_STATUS)
        return tool_uri or ''
    if tool_uri and tool_uri != uri:
        notes.append(f'the status file names {tool_uri}, not the URI of this file name')
    return uri


def _status_only_row(layout, folder_relative, uri, name, status_path, read_by):
    """The row of a .status.json whose .txt is not in this extraction."""
    tool_status, tool_uri, problem = reader.read_tool_status(status_path)
    notes = [f'the {reader.STATUS_SUFFIX} of this file is in this extraction but the file is not']
    uri = _shown_uri(uri, tool_uri, notes)
    detail = '; '.join(filter(None, notes + [problem]))
    return (layout, folder_relative, uri, name, reader.NO_FILE, tool_status, '', detail, '', read_by)


def _file_row(context, layout, folder_relative, uri, path, read_by, statuses, sources):
    relative = _relative(context, path)
    name = relative[len(folder_relative) + 1:] if relative.startswith(folder_relative + '/') else relative
    tool_status, tool_uri, problem = _tool_status(layout, relative, statuses, sources)
    # A status file naming another URI than the file name describes another query, and one whose URI
    # cannot be read cannot be tied to this query: its status is shown as written, but not compared with
    # this file's text.
    same_query = tool_uri is not None and not (uri and tool_uri and tool_uri != uri)
    uri_notes = []
    uri = _shown_uri(uri, tool_uri, uri_notes)
    try:
        dump = reader.read_file(path, context.get_seeker())
    except OSError as error:
        logfunc(f'Content query {layout} {relative}: {_read_error(error)}')
        detail = '; '.join(filter(None, [_read_error(error)] + uri_notes + [problem]))
        return (layout, folder_relative, uri, name, reader.UNREADABLE, tool_status, '', detail, '', read_by)
    notes = ([dump.detail] if dump.detail else []) + dump.warnings + uri_notes + ([problem] if problem else [])
    if tool_uri is None and tool_status:
        notes.append(NOTE_STATUS_NOT_COMPARED)
    if same_query and reader.tool_status_disagrees(tool_status, dump.status):
        notes.append(f'ALEX wrote status {tool_status} for this file, which its own row parser sets; the text '
                     f'reads as {dump.status}')
        logfunc(f'Content query {layout} {relative}: ALEX status {tool_status}, text read as {dump.status}')
    count = len(dump.records) if dump.status == reader.ROWS else ''
    return (layout, folder_relative, uri, name, dump.status, tool_status, count, '; '.join(notes),
            ', '.join(dump.columns), read_by)

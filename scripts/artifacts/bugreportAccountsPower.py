__artifacts_v2__ = {
    "bugreport_accounts": {
        "name": "Bug Report - Accounts",
        "description": "The Accounts list of each Android user in the account service dump of an Android bug report "
                      "text, with the account name and type as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Accounts, Sync and Backup",
        "notes": "One row per Account {name=..., type=...} line under the Accounts: heading of each Android user "
                 "in the account service dump (DUMP OF SERVICE account). User, User Name and User Flags (as "
                 "stored) come from the User UserInfo{id:name:flags}: line above the list; the flags are the "
                 "hexadecimal text after the last colon, shown as stored and not decoded. Account Name is the text "
                 "after name= and Account Type the text after type=, as printed. A name can be an address, a user "
                 "name, an app label or a number, and the dump does not say which. A row says that the account "
                 "manager listed that account for that user when the dump ran; it does not say who the account "
                 "belongs to, whether it is signed in or whether it was used. The Accounts: N number printed for a "
                 "user was compared with the rows read; a difference is logged (none in the five real reports). "
                 "The Huawei report prints a placeholder of nine X characters as the name of every account and a "
                 "name made of invisible direction marks as the user name; both are shown as printed. The account "
                 "event dump lines (description= and date= entries) are not read.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 11, 28, 5, 11 and "
                 "27 rows, each equal to a count of Account { lines in the raw account section and to the printed "
                 "Accounts: N of the user. The Motorola report lists two users (0 with 26 rows and 11 with 1); "
                 "User held one value, 0, on all rows of the other four reports, and User Name and User Flags (as "
                 "stored) each held one value on all rows of each of those four reports. Account Name held one "
                 "value, the placeholder, on all rows of the Huawei report. Not examined: Android 11, 12 and 14 and "
                 "vendors other than the four seen."
                 "\nOn the corpus none of s20fe_a13, samsungs20_a13, sharon_a14 and userb2_a13 gave a row; why was not examined.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_account_history": {
        "name": "Bug Report - Account History",
        "description": "The Accounts History table of each Android user in the account service dump of an Android bug "
                      "report text, with the time, action, account id and uid as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Accounts, Sync and Backup",
        "notes": "One row per line of the table printed under the AccountId, Action_Type, timestamp, UID, "
                 "TableName, Key heading and the Accounts History heading of each Android user. Account ID, "
                 "Action, UID, Table and Key are the printed values: Action is the name the dump prints (the real "
                 "reports printed action_account_add, action_account_remove, action_called_account_add, "
                 "action_called_account_remove, action_set_password, action_clear_password and "
                 "action_authenticator_remove), Account ID is -1 on rows that name no account id (8, 3, 31, 0 and "
                 "9 rows in the five real reports; all of them start with action_called_), and Key is the row key "
                 "of the table, which was not in ascending order in 3 of the 5 reports, so the rows are kept in "
                 "the order printed. Time As Printed is the timestamp text, a device wall-clock time. Time (UTC) "
                 "converts the printed time with the zone shown in Bug Report - Device Facts, and is empty where "
                 "the report records no zone, where the text is not a time or where it is before 2009. All five "
                 "real reports record the same UTC+0 zone without daylight saving, so the conversion was the "
                 "identity on every real row; other zones and daylight saving were tested on constructed text "
                 "only. A row says that the account manager recorded that action at that time; it does not say who "
                 "or what caused it, and the table is the platform's own limited history, so an account or action "
                 "that is not listed says nothing about what happened. The rows are not sorted by time.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 25, 64, 38, 64 "
                 "and 66 rows, each equal to a count of the history lines in the raw text. Table held one value, "
                 "accounts, on all rows of every report, and User held one value, 0, on all rows of the four "
                 "reports with one user. The Motorola report lists 2 rows for user 11. Not examined: Android 11, 12 "
                 "and 14 and vendors other than the four seen."
                 "\nOn the corpus none of s20fe_a13, samsungs20_a13, sharon_a14 and userb2_a13 gave a row; why was not examined.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "history",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_account_authenticators": {
        "name": "Bug Report - Account Authenticators",
        "description": "The RegisteredServicesCache entries of each Android user in the account service dump of an "
                      "Android bug report text, with the account type, component and uid as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Accounts, Sync and Backup",
        "notes": "One row per ServiceInfo: AuthenticatorDescription line under the RegisteredServicesCache heading "
                 "of each Android user. Account Type is the text after type=, Component the ComponentInfo{...} "
                 "text (package and class), UID the number after uid and Last Update Time (as printed) the text "
                 "after lastUpdateTime. The list is the account types that installed apps register with the "
                 "account manager; it is not the list of accounts on the device (see Bug Report - Accounts), and a "
                 "row does not say that any account of that type exists. Last Update Time (as printed) held -1 on "
                 "all rows of the Samsung A-series report, a number on the Samsung S-series rows and was empty on "
                 "all rows of the Huawei, Transsion-brand and Motorola reports, whose builds print no such text; "
                 "the numbers are shown as printed and are not converted.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 20, 37, 15, 14 "
                 "and 46 rows, each equal to a count of ServiceInfo: AuthenticatorDescription lines in the raw "
                 "text. User held one value, 0, on all rows of the four reports with one user. Not examined: "
                 "Android 11, 12 and 14 and vendors other than the four seen."
                 "\nOn the corpus the run gave s20fe_a13 11 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "key",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 11 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_account_visibility": {
        "name": "Bug Report - Account Visibility",
        "description": "The Account visibility lists of each Android user in the account service dump of an Android bug "
                      "report text, with the account, the package and the number printed after it.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Accounts, Sync and Backup",
        "notes": "One row per package line under an account name in the Account visibility: list of each Android "
                 "user. Account is the line above the package lines, Package the text before the last comma and "
                 "Visibility (as stored) the number after it, which is not decoded here. A row says that the "
                 "account manager printed that number for that account and package; it does not say what the "
                 "number allows or whether the package used the account. An account with no package lines has no "
                 "rows.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 31, 75, 14, 9 and "
                 "62 rows, each equal to a count of the package lines in the raw text. Visibility held one value, "
                 "2, on all rows of the Samsung A-series, Huawei and Transsion-brand reports; the Samsung S-series "
                 "and Motorola reports also print 1 (3 and 1 rows). Account held one value on all rows of the "
                 "Huawei and Transsion-brand reports. User held one value, 0, on all rows of the four reports with "
                 "one user. Not examined: Android 11, 12 and 14 and vendors other than the four seen."
                 "\nOn the corpus none of s20fe_a13, samsungs20_a13, sharon_a14 and userb2_a13 gave a row; why was not examined.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "eye",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_sync_adapter_status": {
        "name": "Bug Report - Sync Adapter Status",
        "description": "The Sync Status tables of the content service dump of an Android bug report text, with one row "
                      "for each account and sync authority and the counts and last sync times as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Accounts, Sync and Backup",
        "notes": "One row per authority line of the table printed under each Account <name> u<user> <type> heading "
                 "in the Sync Status part of the content service dump (DUMP OF SERVICE content). A block headed "
                 "with a trailing (locked) is read as well and the text is shown in Account State (as printed). "
                 "Syncable and Enabled are the printed values. The Count columns are the numbers of the Total line "
                 "under the printed column names Loc, Poll, Per, Feed, User, Othr, Tot, Fail and Can; the names "
                 "are kept as printed and the dump does not define them here. Time (as printed) is the Time column "
                 "of the Total line. The last sync cells are printed in the Last Sync column over several lines: a "
                 "source and SUCCESS or FAILURE, then a time, and for a failure a message. They are read in that "
                 "order into Last Success Source, Last Success Time As Printed, Last Failure Source, Last Failure "
                 "Time As Printed and Last Failure Message. The Today and Yestr lines and the Backoff text are not "
                 "listed beyond the Backoff cell of the Total line. Time (UTC) converts the printed time with the "
                 "zone shown in Bug Report - Device Facts, and is empty where the report records no zone, where "
                 "the text is not a time or where it is before 2009. All five real reports record the same UTC+0 "
                 "zone without daylight saving, so the conversion was the identity on every real row; other zones "
                 "and daylight saving were tested on constructed text only. A row says what the sync manager kept "
                 "for that account and authority; it does not say what was synchronized.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 47, 67, 18, 24 "
                 "and 47 rows, each equal to a count of the Total lines of the tables in the raw text. Count Poll "
                 "held 0 on all rows of every report, Last Failure Source, Last Failure Time As Printed and Last "
                 "Failure Message were empty on all rows of the reports other than the Samsung S-series and "
                 "Motorola ones, and Backoff was empty on all rows of every report. Account State (as printed) "
                 "held a text on 11 rows of the Motorola report (the locked block of user 11) and was empty on all "
                 "rows of the other reports. User held one value, 0, on all rows of the four reports other than "
                 "the Motorola one, and Account held one value, the placeholder, on all rows of the Huawei report. "
                 "Rows of an authority that never synced have empty last sync cells (6, 7, 0, 3 and 2 rows). Not "
                 "examined: Android 11, 12 and 14 and vendors other than the four seen."
                 "\nOn the corpus none of s20fe_a13, samsungs20_a13, sharon_a14 and userb2_a13 gave a row; why was not examined.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "refresh-cw",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_sync_recent_history": {
        "name": "Bug Report - Sync Recent History",
        "description": "The Recent Sync History list of the content service dump of an Android bug report text, with the "
                      "time, source, duration, account, authority, reason and extras as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Accounts, Sync and Backup",
        "notes": "One row per #N: line of the Recent Sync History list in the content service dump, in the order "
                 "printed (newest first in the real reports). Time As Printed is the date and time text; Source, "
                 "Duration (s as printed), Account, Account Type, User, Authority and Reason are read from the "
                 "rest of the line. Extra Field (as printed) is the text that the dump prints between the duration "
                 "and the account; it held a whole number, a minutes and seconds text, an hours, minutes and "
                 "seconds text or nothing, and the dump has no column name for it, so it is not interpreted. "
                 "Message is the mesg= line under an entry and Extras the Bundle[...] text of the entry with the "
                 "same number in the Recent Sync History Extras list. Row As Printed holds the line as printed "
                 "(cut at 600 characters) so that a line read in a different shape stays visible. The Huawei "
                 "report prints one placeholder for the account and no account type or user, so those cells are "
                 "empty. Time (UTC) converts the printed time with the zone shown in Bug Report - Device Facts, "
                 "and is empty where the report records no zone, where the text is not a time or where it is "
                 "before 2009. All five real reports record the same UTC+0 zone without daylight saving, so the "
                 "conversion was the identity on every real row; other zones and daylight saving were tested on "
                 "constructed text only. A row says that the sync manager recorded that sync; it does not say what "
                 "was synchronized, and the list is limited to what the device kept.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 39, 100, 3, 23 "
                 "and 61 rows, each equal to a count of the #N: lines of the list in the raw text. User held one "
                 "value, 0, on all rows of the Samsung and Transsion-brand reports (the Motorola report also lists "
                 "user 11, and the Huawei report prints no user). In the Huawei report User, Account Type and "
                 "Message were empty on all rows and Account held one value, the placeholder. Not examined: "
                 "Android 11, 12 and 14, vendors other than the four seen, and an account or authority name that "
                 "contains two adjacent spaces, which the columns would read apart."
                 "\nOn the corpus none of s20fe_a13, samsungs20_a13, sharon_a14 and userb2_a13 gave a row; why was not examined.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "refresh-cw",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_sync_adapter_last_syncs": {
        "name": "Bug Report - Sync Adapter Last Syncs",
        "description": "The Last syncs lists of the Per Adapter History part of the content service dump of an Android "
                      "bug report text, with the time, result, source, reason and extras as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Accounts, Sync and Backup",
        "notes": "One row per dated line under a Last syncs: heading of an account, type and authority in the Per "
                 "Adapter History part of the content service dump. Result is the word after the time (for example "
                 "success, canceled or io-error, as printed), Source, Elapsed (as printed), Reason, Exemption and "
                 "Extras are the printed Source=, Elapsed=, Reason=, Exemption= and Extras= values; Exemption is "
                 "empty where the line prints none. The Per source last syncs lines and the lines that print N/A "
                 "are not listed. Time (UTC) converts the printed time with the zone shown in Bug Report - Device "
                 "Facts, and is empty where the report records no zone, where the text is not a time or where it "
                 "is before 2009. All five real reports record the same UTC+0 zone without daylight saving, so the "
                 "conversion was the identity on every real row; other zones and daylight saving were tested on "
                 "constructed text only. A row says that the sync manager kept that entry for that account and "
                 "authority; the number of entries kept for an adapter is the platform's, so an entry that is not "
                 "listed says nothing about whether a sync happened.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 304, 476, 147, "
                 "201 and 387 rows, each equal to a count of the dated Source= lines in the raw text. Exemption "
                 "was empty on 236, 356, 107, 161 and 283 rows. User held one value, 0, on all rows of the four "
                 "reports other than the Motorola one, which also lists user 11. Account held one value, the "
                 "placeholder, on all rows of the Huawei report. Not examined: Android 11, 12 and 14 and vendors other "
                 "than the four seen."
                 "\nOn the corpus none of s20fe_a13, samsungs20_a13, sharon_a14 and userb2_a13 gave a row; why was not examined.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "history",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_sync_jobs": {
        "name": "Bug Report - Sync Jobs",
        "description": "The Pending Syncs, Periodic Syncs and Active Syncs lists of the content service dump of an "
                      "Android bug report text, with one row for each JobId line.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Accounts, Sync and Backup",
        "notes": "One row per JobId= line under the Active Syncs:, Pending Syncs: and Periodic Syncs: headings of "
                 "the content service dump; List is that heading. Account, Account Type, User, Authority and "
                 "Source are read from the line (two shapes were seen: account/type uN [authority] and, on Android "
                 "10, account/ uN (type uN [authority]), and Details (as printed) holds the rest of the line, for "
                 "example ExpectedIn=, Reason=, Owner={...} and the extras in square brackets. The Owner text and "
                 "the other details are shown as printed and are not decoded. A row says that the sync manager "
                 "held that job when the dump ran, not that the sync ran. Active Syncs held no lines in the real "
                 "reports.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 40, 68, 18, 22 "
                 "and 48 rows, each equal to a count of the JobId= lines in the raw text; no line was left without "
                 "an account. List held one value, Periodic, on all rows of the Huawei report, and Source held one "
                 "value, PERIODIC, on all rows of the Samsung S-series and Huawei reports. User held one value, 0, "
                 "on all rows of four reports. Account held one value, the placeholder, on all rows of the Huawei "
                 "report. Not examined: Android 11, 12 and 14 and vendors other than the four seen."
                 "\nOn the corpus none of s20fe_a13, samsungs20_a13, sharon_a14 and userb2_a13 gave a row; why was not examined.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "list",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_sync_state": {
        "name": "Bug Report - Sync State",
        "description": "The state lines, the list counts and the sync statistics of the content service dump of an "
                      "Android bug report text, as name and value pairs.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Accounts, Sync and Backup",
        "notes": "One row per Name: value line before the Active Syncs heading (for example Data connected, Auto "
                 "sync, Clock valid, Accounts, Now, Uptime and Time spent syncing), one row for each of the Active "
                 "Syncs, Pending Syncs and Periodic Syncs counts, and one row for each line of the Sync Statistics "
                 "list (Today, Day-1 to Day-6 and Week-1 to Week-3 as printed, with the Success and Failure text). "
                 "Value is the text as printed. Time (UTC) is set on the Now row only, from the date and time in "
                 "its parentheses; the other rows hold device counters or lasting times. Time (UTC) converts the "
                 "printed time with the zone shown in Bug Report - Device Facts, and is empty where the report "
                 "records no zone, where the text is not a time or where it is before 2009. All five real reports "
                 "record the same UTC+0 zone without daylight saving, so the conversion was the identity on every "
                 "real row; other zones and daylight saving were tested on constructed text only. The values are a "
                 "snapshot taken when the dump ran. The Service host process, Threads in use and Client PIDs lines "
                 "are not listed.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 23, 23, 25, 25 "
                 "and 23 rows. The rows were read, but they were not counted a second time. Not examined: Android "
                 "11, 12 and 14 and vendors other than the four seen."
                 "\nOn the corpus the run gave s20fe_a13 13 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "info",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 13 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_backup_state": {
        "name": "Bug Report - Backup State",
        "description": "The state lines of the backup service dump of an Android bug report text, as name and value "
                      "pairs.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Accounts, Sync and Backup",
        "notes": "One row per Name: value line at the start of a line in the backup service dump outside the "
                 "lists, and one row for a line that has no colon (Name is Statement and Value the sentence, for "
                 "example the Backup Manager enabled, Auto-restore and Framework scheduling lines). The Last "
                 "backup pass started line is split into its value (the number before (now =) and a row named now "
                 "(in the Last backup pass started line) that holds the number after now =; next scheduled is the "
                 "number on the line below. Time (UTC) is set on those three rows when the printed number reads as "
                 "epoch milliseconds between 2009 and 2100 (0 gets none). The meaning of the numbers and of "
                 "Current (a hexadecimal token) is not decoded here. The Pending key/value backup and Full backup "
                 "queue counts are rows here and their entries are rows of Bug Report - Backup Queues. The dump is "
                 "a snapshot taken when it ran. The Service host process, Threads in use and Client PIDs lines are "
                 "not listed.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 18, 18, 15, 15 "
                 "and 18 rows. The rows were read, but they were not counted a second time. Value was empty on 1 "
                 "row of the Samsung and Motorola reports (the Agent timeouts heading). Not examined: Android 11, "
                 "12 and 14 and vendors other than the four seen."
                 "\nOn the corpus the run gave s20fe_a13 15 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cloud",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 15 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_backup_transports": {
        "name": "Bug Report - Backup Transports",
        "description": "The Transport whitelist and Available transports lists of the backup service dump of an Android "
                      "bug report text, with the destination and intent as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Accounts, Sync and Backup",
        "notes": "One row per line of the Transport whitelist: list (List is Whitelist) and per transport of the "
                 "Available transports: list (List is Available). Transport is the component text as printed. "
                 "Marked With * (current) is yes where the dump puts an asterisk before the transport. Destination "
                 "and Intent are the destination: and intent: lines under an available transport, and are empty on "
                 "whitelist rows; a destination can be an account name, as printed. A row says what the backup "
                 "manager listed when the dump ran; it does not say that a backup was made.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 10, 10, 6, 6 and "
                 "11 rows, each equal to a count of the whitelist lines and the transport lines in the raw text. "
                 "Every report marked one transport with an asterisk. Not examined: Android 11, 12 and 14 and vendors "
                 "other than the four seen."
                 "\nOn the corpus the run gave s20fe_a13 7 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cloud",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 7 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_backup_package_state": {
        "name": "Bug Report - Backup Package State",
        "description": "The package state lines printed under the current transport in the backup service dump of an "
                      "Android bug report text, with the state bytes as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Accounts, Sync and Backup",
        "notes": "One row per line of the form package - N state bytes under the transport marked with an asterisk "
                 "in the Available transports list. Transport is that transport and State Bytes (as printed) the "
                 "number before state bytes. @pm@ and other non-package names are listed as printed. A row says "
                 "that the transport reported that size for that name when the dump ran; it does not say what the "
                 "state holds or when it was written. The Huawei report prints no such lines, so it has no rows, "
                 "which says nothing about the device.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on four of the five real bug reports (Samsung A-series and S-series "
                 "on Android 16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 32, "
                 "31, 0, 26 and 53 rows, each equal to a count of the state bytes lines in the raw text. Transport "
                 "held one value on all rows of every report that has rows. Not examined: Android 11, 12 and 14 and "
                 "vendors other than the four seen."
                 "\nOn the corpus none of s20fe_a13, samsungs20_a13, sharon_a14 and userb2_a13 gave a row; why was not examined.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cloud",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_backup_participants": {
        "name": "Bug Report - Backup Participants",
        "description": "The Participants list of the backup service dump of an Android bug report text, with the uid and "
                      "package as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Accounts, Sync and Backup",
        "notes": "One row per package line under a uid: line of the Participants: list. UID is the number after "
                 "uid: and Package the name. A row says that the backup manager listed that package among its "
                 "participants when the dump ran; it does not say that data of the package was backed up (see Bug "
                 "Report - Backup Queues and Bug Report - Backup Package State).\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 28, 35, 23, 26 "
                 "and 45 rows, each equal to a count of the package lines in the raw text. Not examined: Android "
                 "11, 12 and 14 and vendors other than the four seen."
                 "\nOn the corpus the run gave s20fe_a13 20 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cloud",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 20 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_backup_queues": {
        "name": "Bug Report - Backup Queues",
        "description": "The Pending key/value backup and Full backup queue lists of the backup service dump of an "
                      "Android bug report text, with the package and the number printed before it.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Accounts, Sync and Backup",
        "notes": "One row per BackupRequest{pkg=...} line under Pending key/value backup (Number Before Package is "
                 "empty) and per N : package line under Full backup queue (the number is shown as printed). Time "
                 "(UTC) is set when that number reads as epoch milliseconds between 2009 and 2100; 0 is shown as "
                 "printed and gets no time. What the number records is not stated in the dump, so a time here is "
                 "the number read as a time and nothing more. A row says what the backup manager held in its queue "
                 "when the dump ran; it does not say that a backup happened or failed.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 183, 202, 68, 143 "
                 "and 271 rows, each equal to a count of the two kinds of line in the raw text. Time (UTC) was "
                 "empty on 31, 175, 25, 31 and 52 rows (the pending entries and the entries printed with 0). Not "
                 "examined: Android 11, 12 and 14 and vendors other than the four seen."
                 "\nOn the corpus the run gave s20fe_a13 132 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cloud",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 132 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_users": {
        "name": "Bug Report - Users",
        "description": "The UserInfo records of the user service dump of an Android bug report text, with the type, "
                      "flags, state and the times as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Accounts, Sync and Backup",
        "notes": "One row per UserInfo{id:name:flags} line of the Users: list in the user service dump (DUMP OF "
                 "SERVICE user). User ID, Name and UserInfo Flags (hex as printed) come from that line, Serial No, "
                 "Is Primary and Parent ID from the key=value words after it. Type, Flags Line (as printed), "
                 "State, Has Profile Owner and the Restrictions lists are the lines under the record, as printed "
                 "(none is printed as none). Created, Last Logged In, Start Time, Unlock Time and Last Entered "
                 "Foreground are printed by the dump as a time before the dump (for example +6h14m45s255ms ago) or "
                 "<unknown>; they are shown as printed and not converted, because the dump does not print the "
                 "moment the user service ran, and a time converted with the report time would be a guess. A row "
                 "says what the user manager held when the dump ran. The Android 10 builds print no Type, Flags or "
                 "Last entered foreground lines, so those cells are empty. The Samsung reports have no user "
                 "service section.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on three of the five real bug reports (Samsung A-series and S-series "
                 "on Android 16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 0, 0, "
                 "1, 1 and 2 rows (the Motorola report lists a full user and a profile user), each equal to a "
                 "count of the UserInfo{ lines in the raw text. Has Profile Owner held one value, false, on the "
                 "Motorola rows. Is Primary, Parent ID, Type, Flags Line (as printed) and Last Entered Foreground "
                 "(as printed, relative) were empty on the one row of each Android 10 report. Restrictions and "
                 "Effective Restrictions held the same text on every row of every report (none, or the same two "
                 "restrictions), and User ID and Serial No were equal on every row. Not examined: Android 11, 12 "
                 "and 14, other vendors and devices with more than two users."
                 "\nOn the corpus the run gave s20fe_a13 1 row; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "users",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 1 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_user_manager_facts": {
        "name": "Bug Report - User Manager Facts",
        "description": "The lines of the user service dump of an Android bug report text that are outside the UserInfo "
                      "records, as name and value pairs.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Accounts, Sync and Backup",
        "notes": "One row per Name: value line at the start of the user service dump or after the Users: list (for "
                 "example Current user, Device owner id, Device managed, Started users state, Max users and "
                 "Supports switchable users) and one row for the Guest restrictions list, whose lines are joined "
                 "with a comma. Value is the text as printed and is not decoded (Started users state is a map of "
                 "user ids to numbers). A row says what the user manager printed when the dump ran.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on three of the five real bug reports (Samsung A-series and S-series "
                 "on Android 16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 0, 0, "
                 "7, 7 and 31 rows. The rows were read, but they were not counted a second time. Not examined: "
                 "Android 11, 12 and 14 and vendors other than the four seen."
                 "\nOn the corpus the run gave s20fe_a13 23 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "users",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 23 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_battery_history": {
        "name": "Bug Report - Battery History",
        "description": "The Battery History records of the batterystats service dump of an Android bug report text, with "
                      "the time, battery level, state bits and the changes as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Battery and Power",
        "notes": "One row per record of the Battery History list in the batterystats service dump (DUMP OF SERVICE "
                 "batterystats), in the order printed. Level (%) is the three digit number after the time, State "
                 "Bits (hex as printed) the hexadecimal number after it (not decoded) and Changes (as printed) the "
                 "rest of the record: words such as +screen or -running, key=value pairs such as volt=3781 and "
                 "events such as top=u0a425:\"<package>\", +wake_lock=1001:\"<tag>\" or +job=...; the dump prints what "
                 "changed since the previous record, so the first record after a reset is the long one, and a "
                 "record with no changes text is empty in Changes. Marker is Reset, Clock, Shutdown, Start or "
                 "Overflow for the records whose text starts with RESET:TIME:, TIME:, SHUTDOWN, START or "
                 "*OVERFLOW* (these carry no level and no state bits). A row says that the platform recorded that "
                 "change at that time; it does not say what a person did.\n"
                 "Two layouts were seen. The Android 16 reports (Format: 2) print the date and time of every "
                 "record (Time As Printed, month and day without a year; the year is the latest one that does not "
                 "put the record after the report time, as for Bug Report - Settings Changes). The Android 10 and "
                 "15 reports print an offset from the first record (for example +1d04h32m55s844ms); there Time "
                 "(UTC) is the wall time of the latest RESET:TIME: or TIME: record at or before the record (shown "
                 "in Clock Record Used (as printed)) plus the offset difference to that record, converted with the "
                 "zone shown in Bug Report - Device Facts. Time (UTC) converts the printed time with the zone "
                 "shown in Bug Report - Device Facts, and is empty where the report records no zone, where the "
                 "text is not a time or where it is before 2009. All five real reports record the same UTC+0 zone "
                 "without daylight saving, so the conversion was the identity on every real row; other zones and "
                 "daylight saving were tested on constructed text only. Records can run backward where the clock "
                 "was set: the largest backward step in the real reports was 410.3 seconds (Motorola) and under 9 "
                 "seconds in the others. Not read: the Stats: and Details: lines and the per uid time lines that "
                 "follow a record, and a wrapped line that starts at column 0. Rows are limited to 500,000 per "
                 "report.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 98,779, 32,540, "
                 "11,367, 17,095 and 87,219 rows, each equal to a count of the record lines between the Battery "
                 "History heading and the Per-PID Stats heading in the raw text. In each of the five reports the "
                 "level of the last record equals the level printed in the battery service dump (see Bug Report - "
                 "Battery Service State), and the last record falls 50 to 118 seconds after the report time "
                 "printed in the banner. Clock Record Used (as printed) was empty on all rows of the two Android "
                 "16 reports. Marker held Reset on 1 row of every report, Clock on 31, 10, 4, 7 and 28 rows, Start "
                 "on 1, 0, 1, 1 and 1, and Shutdown on 0, 0, 1, 1 and 0. Not examined: Android 11, 12 and 14 and "
                 "vendors other than the four seen."
                 "\nOn the corpus the run gave s20fe_a13 1,281 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "battery",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 1,281 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_battery_daily_summary": {
        "name": "Bug Report - Battery Daily Summary",
        "description": "The Daily stats periods of the batterystats service dump of an Android bug report text, with the "
                      "start and end, the number of discharge and charge steps and the step totals as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Battery and Power",
        "notes": "One row per Daily from <start> to <end>: period of the Daily stats part of the batterystats "
                 "service dump, and one row for the period that is still open (Period is Current; its start is the "
                 "Current start time and it has no end). Period Start and Period End are printed as "
                 "year-month-day-hour-minute-second; the UTC columns convert them with the zone shown in Bug "
                 "Report - Device Facts and are empty for a time before 2009 (one end of the Transsion-brand "
                 "report is printed as 1970-01-01) or where the report records no zone. Discharge Steps and Charge "
                 "Steps count the #N: lines under the step durations headings of the period. Totals (as printed) "
                 "joins the Discharge ... time: and Charge ... time: lines of the period, which carry the "
                 "platform's own step totals; the names of those lines differ between reports and are shown as "
                 "printed. Package Changes counts the lines of the period in Bug Report - Battery Package Changes. "
                 "The step lines themselves are not listed. A period is a span of the device clock between two "
                 "points the platform chose; it is not a calendar day.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 11 rows in each "
                 "report (10 Daily periods and the Current period), equal to a count of the Daily from lines plus "
                 "the current period in the raw text. Period End was empty on the Current row of every report. Not "
                 "examined: Android 11, 12 and 14 and vendors other than the four seen."
                 "\nOn the corpus the run gave s20fe_a13 1 row; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "battery-charging",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 1 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_battery_package_changes": {
        "name": "Bug Report - Battery Package Changes",
        "description": "The Package changes lines of the Daily stats periods in the batterystats service dump of an "
                      "Android bug report text, with the change, package and version as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Battery and Power",
        "notes": "One row per line under a Package changes: heading of a Daily from period. Change is the first "
                 "word (the real reports printed Update only), Package the second and Version Code the number "
                 "after vers=. The period start and end are those of the Daily from block; the dump does not print "
                 "the time of the change, so the UTC columns are the period boundaries, not the time of the change "
                 "(see Bug Report - Battery Daily Summary for how they are converted). The same line is printed "
                 "several times in a row for one package in the real reports and the rows are kept as printed "
                 "(183, 132, 16, 12 and 509 rows repeat another row of the same period). A row says that the "
                 "platform recorded that package change in that period; it does not say who made it. A package "
                 "that is not listed says nothing about whether it changed.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 240, 176, 31, 24 "
                 "and 733 rows, each equal to a count of the Update lines in the raw text. Change held one value, "
                 "Update, on all rows of every report; Install and Uninstall style words were not seen and are "
                 "read as printed. Period End was empty on 20 rows of the Samsung S-series report and 14 of the "
                 "Transsion-brand report. Not examined: Android 11, 12 and 14 and vendors other than the four seen."
                 "\nOn the corpus none of s20fe_a13, samsungs20_a13, sharon_a14 and userb2_a13 gave a row; why was not examined.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "package",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_battery_power_use": {
        "name": "Bug Report - Battery Power Use",
        "description": "The Estimated power use (mAh) block of the batterystats service dump of an Android bug report "
                      "text, with one row for each item and uid line and the figures as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Battery and Power",
        "notes": "One row per item line (Capacity, Global items, Screen, Idle and similar) and per UID or Uid line "
                 "in the Estimated power use (mAh): block. Kind is Item or UID, Name the text before the colon (a "
                 "uid label such as u0a425 or 1000 for a UID row) and Total (as printed) the first number after "
                 "it, which the block heading gives in mAh. Detail (as printed) holds the rest of the line and the "
                 "lines under it, joined with a bar: the fg, bg, fgs and cached figures, the component=figure "
                 "(duration) lists and, on the Android 10 layout, the ( cpu= wake= ... ) lists and the smearing "
                 "text. Context (as printed) is the heading line of its own (for example on battery, screen on) "
                 "that the Samsung reports print above items; it is empty elsewhere. The three layouts (Android "
                 "10, 15 and 16) print different words, so the figures are not unified. The figures are estimates "
                 "that the device computed from its own power profile; they are not measurements made here, and a "
                 "row says what the device printed. The block also holds sub-lists whose lines repeat item names "
                 "under a context heading. Not read: Per-app mobile ms per packet, wakeup reasons and the other "
                 "lists of the dump.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 322, 241, 127, "
                 "107 and 242 rows, of which the UID rows (269, 209, 119, 100 and 232) are each equal to a count "
                 "of the UID or Uid lines of the block in the raw text; the Item rows and the Detail text were "
                 "read but not counted a second time. Context (as printed) was empty on all rows of the Huawei, "
                 "Transsion-brand and Motorola reports. Not examined: Android 11, 12 and 14 and vendors other than the "
                 "four seen."
                 "\nOn the corpus the run gave s20fe_a13 380 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "battery",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 380 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_battery_wake_locks": {
        "name": "Bug Report - Battery Wake Locks",
        "description": "The Wake lock lines of each uid block and the kernel wake lock list in the Statistics since last "
                      "charge part of the batterystats service dump of an Android bug report text, with the usage text "
                      "as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Battery and Power",
        "notes": "One row per Wake lock line inside a uid block (Kind is UID; UID is the label of the block such "
                 "as u0a425 or 1000) and per Kernel Wake lock line of the All kernel wake locks list (Kind is "
                 "Kernel; UID is empty). Wake Lock is the name before the usage text and Usage (as printed) the "
                 "text after it, for example 14ms partial (4 times) max=8 actual=27 or 55m 24s 16ms (1254 times) "
                 "realtime; the words, times and counts are as printed and are not unified, and a line that prints "
                 "a name only has an empty Usage (as printed). Packages In UID Block lists the names of the Apk "
                 "lines printed in the same uid block (empty where there are none; a uid shared by several "
                 "packages lists them all); it names the packages the dump printed there and does not say which "
                 "one held the lock. The usage is cumulative over the statistics period the dump covers "
                 "(Statistics since last charge), not a list of events. Not read: the All partial wake locks list, "
                 "which repeats the uid block lines with the uid in front, the wakeup reasons, the job lines and "
                 "the other lines of a uid block.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 740, 634, 833, "
                 "436 and 897 rows, each equal to a count of the indented Wake lock lines plus the Kernel Wake "
                 "lock lines in the raw text. UID rows were 692, 583, 723, 394 and 828 and Kernel rows 48, 51, "
                 "110, 42 and 69. Usage (as printed) was empty on 251, 320, 551, 252 and 461 rows. Not examined: "
                 "Android 11, 12 and 14 and vendors other than the four seen."
                 "\nOn the corpus the run gave s20fe_a13 315 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "battery",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 315 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_battery_service_state": {
        "name": "Bug Report - Battery Service State",
        "description": "The Current Battery Service state lines of the battery service dump of an Android bug report "
                      "text, as name and value pairs.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Battery and Power",
        "notes": "One row per name: value line of the battery service dump (DUMP OF SERVICE battery), for example "
                 "status, health, present, level, scale, voltage, temperature, technology and the charge counter, "
                 "plus the vendor lines the dump adds. Value is the text as printed; status, health and the other "
                 "codes are numbers that are not decoded here, and units are not added. The values are a snapshot "
                 "taken when the dump ran and are not a history (see Bug Report - Battery History). The Service "
                 "host process, Threads in use and Client PIDs lines are not listed, and a line without a value is "
                 "not listed.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 72, 80, 14, 13 "
                 "and 39 rows, each equal to a count of the name: value lines in the raw text. The level row "
                 "equals the level of the last Battery History record in each report. Not examined: Android 11, 12 "
                 "and 14 and vendors other than the four seen."
                 "\nOn the corpus the run gave s20fe_a13 43 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "battery",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 43 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_thermal_state": {
        "name": "Bug Report - Thermal Service State",
        "description": "The status lines, temperatures, cooling devices and thresholds of the thermalservice dump of an "
                      "Android bug report text, as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Battery and Power",
        "notes": "One row per status line (Kind is Status; Group is the heading above a tab indented line, for "
                 "example ThermalEventListeners), per Temperature{...} line (Kind is Temperature; Name, Type (as "
                 "stored), Value (as printed) and Status (as stored) are the mName=, mType=, mValue= and mStatus= "
                 "values; Group is the heading of the list: cached temperatures or temperatures read from the "
                 "HAL), per CoolingDevice{...} line (Kind is Cooling Device) and per TemperatureThreshold{...} "
                 "line (Kind is Threshold; Detail (as printed) holds the threshold lists). The type and status "
                 "numbers are not decoded and no unit is added to the values. The figures are a snapshot taken "
                 "when the dump ran. The thermalservice section is not in the two Samsung reports.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on three of the five real bug reports (Samsung A-series and S-series "
                 "on Android 16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 0, 0, "
                 "24, 13 and 36 rows, each equal to a count of the item lines (14, 3 and 25) and of the status "
                 "lines (10, 10 and 11) in the raw text. Detail (as printed) was empty on all rows of the Huawei "
                 "and Transsion-brand reports, which print no thresholds. Not examined: Android 11, 12 and 14 and other "
                 "vendors."
                 "\nOn the corpus the run gave s20fe_a13 20 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "thermometer",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 20 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_power_state": {
        "name": "Bug Report - Power Manager State",
        "description": "The Power Manager State and Settings and Configuration lines and the timeouts of the power "
                      "service dump of an Android bug report text, as name and value pairs.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Battery and Power",
        "notes": "One row per key=value or key: value line in the Power Manager State: and Settings and "
                 "Configuration: blocks of the power service dump (DUMP OF SERVICE power; Block says which), and "
                 "per Name: N ms timeout line below them (Block is Timeouts). A line under a sub-heading such as "
                 "Settings power_manager_constants: has the heading in front of its Name. Value is the text as "
                 "printed, including relative times such as (315377 ms ago) and device idle lists. The values are "
                 "a snapshot taken when the dump ran. Not read: the UID states, the looper state, the battery "
                 "saver blocks and the other parts of the dump.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 115, 109, 82, 81 "
                 "and 103 rows. The rows were read, but they were not counted a second time. Not examined: Android "
                 "11, 12 and 14 and vendors other than the four seen."
                 "\nOn the corpus the run gave s20fe_a13 212 rows, sharon_a14 111 rows and userb2_a13 174 rows (87 from a partial text, 87 from a partial text); samsungs20_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "power",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 212 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 111 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 174 rows",
        }
    },
    "bugreport_power_wake_locks": {
        "name": "Bug Report - Power Wake Locks",
        "description": "The Wake Locks list of the power service dump of an Android bug report text, with the level, "
                      "tag, time held and uid as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Battery and Power",
        "notes": "One row per line under Wake Locks: size=N in the power service dump. Level is the wake lock "
                 "level word (for example PARTIAL_WAKE_LOCK), Tag the quoted text, Flags the words between the tag "
                 "and ACQ= and after the time before the parenthesis, and Held (as printed, relative) the ACQ= "
                 "text, which the dump prints as a time before the dump (for example -936ms) and which is not "
                 "converted. UID and PID are read from uid= and pid=, and Details (as printed) holds the rest of "
                 "the line. A row says that the power manager listed that wake lock when the dump ran; it does not "
                 "say what the holder did. The Motorola report prints size=0 and has no rows.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on four of the five real bug reports (Samsung A-series and S-series "
                 "on Android 16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 2, 3, "
                 "1, 4 and 0 rows, each equal to a count of the lines under the heading in the raw text. Level "
                 "held one value, PARTIAL_WAKE_LOCK, on all rows of the Samsung and Transsion-brand reports; Flags "
                 "held one value, LONG, on all rows of the Samsung S-series report and was empty on all rows of "
                 "the Samsung A-series one. Not examined: Android 11, 12 and 14 and other vendors."
                 "\nOn the corpus the run gave s20fe_a13 8 rows and userb2_a13 3 rows (1 from a partial text, 2 from a partial text); samsungs20_a13 and sharon_a14 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "power",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 8 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 3 rows",
        }
    },
    "bugreport_power_events": {
        "name": "Bug Report - Power Events",
        "description": "The WakeUp History and WakeLock Release History lists of the power service dump of an Android "
                      "bug report text, with the time, uid, reason and package as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Battery and Power",
        "notes": "One row per numbered line of the WakeUp History and WakeLock Release History lists printed under "
                 "PowerHistorian in the power service dump; History says which and Entry is the number in "
                 "brackets. A WakeUp row has UID, Display ID (as printed), State (ON or OFF as printed), Reason, "
                 "Foreground Package and Caller (the text of the last columns, empty where the line prints none). "
                 "A WakeLock Release row has UID (from uid=), Held For (as printed), Lock Level, Tag and Details "
                 "(as printed). Time As Printed is the month, day and time without a year; the year is the latest "
                 "one that does not put the entry after the report time, as for Bug Report - Settings Changes, and "
                 "the time is converted with the zone shown in Bug Report - Device Facts (empty where the report "
                 "has no zone). A row says that the power manager recorded that entry; the lists are the "
                 "platform's limited history, so an entry that is not listed says nothing about what happened. The "
                 "Samsung reports print these lists; the Huawei, Transsion-brand and Motorola reports do not, and "
                 "the Motorola report prints a Wake Lock Log of another shape that is not read.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on two of the five real bug reports (Samsung A-series and S-series "
                 "on Android 16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15) (the "
                 "two Samsung reports): 14 and 141 rows (12 and 100 WakeUp rows, 2 and 41 WakeLock Release rows), "
                 "each equal to a count of the numbered lines of the two lists in the raw text. All five real "
                 "reports are in a UTC+0 zone without daylight saving, so the conversion was the identity; other "
                 "zones were tested on constructed text only. Not examined: other Android versions and vendors."
                 "\nOn the corpus the run gave s20fe_a13 8 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "power",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 8 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_device_idle_state": {
        "name": "Bug Report - Device Idle State",
        "description": "The settings and state lines of the deviceidle service dump of an Android bug report text, as "
                      "name and value pairs.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Battery and Power",
        "notes": "One row per key=value line under the Settings: heading of the deviceidle service dump (Block is "
                 "Settings) and per key=value pair of the state lines at the end of the dump (Block is State, for "
                 "example mState, mLightState, mScreenOn, mCharging and mNextLightIdleDelay). Value is the text as "
                 "printed, with relative times such as +15m0s0ms. The values are a snapshot taken when the dump "
                 "ran. Not read: the allowlist lines (Whitelist ... apps and app ids) and the Idling history "
                 "lines, which are rows of Bug Report - Device Idle History.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 59, 58, 48, 48 "
                 "and 59 rows. The rows were read, but they were not counted a second time. Not examined: Android "
                 "11, 12 and 14 and vendors other than the four seen."
                 "\nOn the corpus the run gave s20fe_a13 54 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "moon",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 54 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_device_idle_history": {
        "name": "Bug Report - Device Idle History",
        "description": "The Idling history list of the deviceidle service dump of an Android bug report text, with the "
                      "state, the time before the dump and the reason as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Battery and Power",
        "notes": "One row per line of the Idling history: list, in the order printed (newest first in the real "
                 "reports). State is the word before the colon (for example light-idle, deep-idle or normal), Time "
                 "Ago (as printed) the time before the dump (for example -7h28m15s23ms) and Reason the text in "
                 "parentheses (for example unlocked or screen), empty where none is printed. The time is not "
                 "converted: the dump does not print the moment the deviceidle service ran, and a time converted "
                 "with the report time would be a guess. A row says that the service recorded that state change. "
                 "The list is the platform's limited history. The Transsion-brand report prints none, so it has no "
                 "rows, which says nothing about the device.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on four of the five real bug reports (Samsung A-series and S-series "
                 "on Android 16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 4, 88, "
                 "5, 0 and 38 rows, each equal to a count of the list lines in the raw text. Reason was empty on "
                 "3, 50, 2 and 25 rows. Not examined: Android 11, 12 and 14 and vendors other than the four seen."
                 "\nOn the corpus the run gave s20fe_a13 2 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "moon",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 2 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_process_stats": {
        "name": "Bug Report - Process Stats",
        "description": "The process lines of the committed periods and of the Process summary parts of the procstats "
                      "service dump of an Android bug report text, with the state share and the figures as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Processes and Memory",
        "notes": "One row per state line (TOTAL, Persistent, Top, Imp Fg, Service and the other labels, as "
                 "printed) under a * process / uid / vversion: line in a COMMITTED STATS FROM period and in the "
                 "Process summary: part of the CURRENT STATS and AGGREGATED OVER LAST 24 HOURS periods; Period is "
                 "that heading. Process, UID and Version are the printed values (a uid such as u0a385 or 1000 and "
                 "the version number without the v). Share Of Time (as printed) is the percentage and Measures (as "
                 "printed) the text in parentheses (three groups of minimum, average and maximum figures and the "
                 "sample count; which group is which is not stated in the dump, so it is not split here). Period "
                 "Start As Printed is the date in the COMMITTED STATS FROM heading; it is empty for the other "
                 "periods (Period Start (UTC) was filled on 740, 916, 450, 501 and 1,065 of the rows), and the UTC "
                 "column converts it with the zone shown in Bug Report - Device Facts. A row says what the "
                 "statistics service kept for that process in that period. Not read: the Per-Package Stats and "
                 "Per-UID Stats parts (they repeat processes under packages and uids), the run time, memory usage "
                 "and PSS collection parts, and the checkin form of the dump.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 3,249, 3,127, "
                 "2,211, 1,919 and 2,757 rows, each equal to a second count of the state lines of those parts in "
                 "the raw text (a separate pass over the section). Each report printed five periods: two COMMITTED "
                 "STATS FROM periods, CURRENT STATS and AGGREGATED OVER LAST 24 HOURS and LAST 3 HOURS. Not "
                 "examined: Android 11, 12 and 14 and vendors other than the four seen."
                 "\nOn the corpus the run gave s20fe_a13 3,330 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cpu",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 3,330 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_process_threads": {
        "name": "Bug Report - Process Threads",
        "description": "The threads listed by ps in the PROCESSES AND THREADS section of an Android bug report text, "
                      "with the pid, tid, user, security label and command as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Processes and Memory",
        "notes": "One row per thread line of the PROCESSES AND THREADS (ps -A -T -Z -O "
                 "pri,nice,rtprio,sched,pcy,time) command section. The columns are the printed ones: PID, TID, "
                 "PPID, User, Command (CMD, which can contain spaces), Label (the security context), State (S), "
                 "VSZ and RSS (shown as printed, not converted), WCHAN, ADDR, PRI, NI, RTPRIO, SCH, PCY and the "
                 "CPU time text. The section is a snapshot of the threads that existed when the command ran; it "
                 "says nothing about threads that had ended. A line with fewer columns than the header is not "
                 "listed (counted in the log). Command was empty on 62, 58, 83, 44 and 28 rows and ADDR held one "
                 "value, 0, on all rows of every report; WCHAN held one value, 0, on all rows of the Huawei and "
                 "Transsion-brand reports.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 4,402, 11,754, "
                 "5,103, 2,801 and 5,137 rows, each equal to the number of lines of the section after the header "
                 "line. Rows are limited to 500,000 per report. Not examined: Android 11, 12 and 14 and vendors other "
                 "than the four seen."
                 "\nOn the corpus the run gave s20fe_a13 11,859 rows (3,799 from the dumpState text, 4,086 from an automatically generated dump, 3,974 from an automatically generated dump), samsungs20_a13 5,738 rows and sharon_a14 3,213 rows; userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cpu",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 11,859 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 5,738 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 3,213 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_memory_by_process": {
        "name": "Bug Report - Memory By Process",
        "description": "The Total PSS by process and Total RSS by process lists of the meminfo service dump of an "
                      "Android bug report text, with the kilobytes, process and pid as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Processes and Memory",
        "notes": "One row per line of the Total PSS by process: and Total RSS by process: lists in the meminfo "
                 "service dump (List is PSS or RSS). Kilobytes is the number before K:, Process the name, PID the "
                 "number after pid and Note the text after a slash in the parentheses (for example activities). "
                 "User (as printed) is the number of a (user N) text and In Swap (KB) the number of the (N K in "
                 "swap) text that the PSS lists print. The lists are a snapshot of the processes that existed when "
                 "the dump ran. The By OOM adjustment and By category lists are not read. The meminfo service dump "
                 "is cut by the device time limit in two of the five real reports (the Samsung S-series report at "
                 "60000 ms and the Transsion-brand report at 30000 ms): a cut dump is logged once and its rows may "
                 "be partial; the Samsung S-series report still holds both lists, and the Transsion-brand report "
                 "holds neither. The Huawei report holds the PSS list only (List held one value, PSS, on all its "
                 "rows), and User (as printed) was empty on all rows of the Samsung and Huawei reports. No rows in "
                 "a report says nothing about the device.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on four of the five real bug reports (Samsung A-series and S-series "
                 "on Android 16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15) (the "
                 "lists are absent from the Transsion-brand report): 342, 712, 200, 0 and 416 rows, each equal to "
                 "a count of the list lines in the raw text. Not examined: Android 11, 12 and 14 and other vendors."
                 "\nOn the corpus the run gave s20fe_a13 440 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cpu",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 440 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_memory_process_detail": {
        "name": "Bug Report - Memory Process Detail",
        "description": "The ** MEMINFO in pid blocks of the meminfo service dump of an Android bug report text, with the "
                      "totals of the heap table and the App Summary figures as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Processes and Memory",
        "notes": "One row per ** MEMINFO in pid N [name] ** block of the meminfo service dump. The figures "
                 "(kilobytes) are the TOTAL row of the heap table (Pss Total, Private Dirty, Shared Dirty, SwapPss "
                 "Dirty, Rss Total, Heap Size, Heap Alloc and Heap Free, read by their printed column names), the "
                 "Native Heap and Dalvik Heap Pss Total, the App Summary rows (Java Heap, Native Heap, Code, "
                 "Stack, Graphics, Private Other and System; the Pss figure, which is the first number of a row) "
                 "and the Views and Activities numbers of the Objects part. A figure that the block does not print "
                 "is empty (the Android 10 builds print no Rss Total). A block with no TOTAL row and no App "
                 "Summary is not listed (1 block of the Huawei report). The blocks are a snapshot of the processes "
                 "that the dump reached; the dump is cut by the device time limit in the Samsung S-series report "
                 "(60000 ms) and the Transsion-brand report (30000 ms), logged once, and the blocks after the cut "
                 "are missing, so a process that has no row says nothing about the device. Not read: the Dalvik "
                 "Details, SQL and DATABASES parts.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 55, 204, 68, 43 "
                 "and 91 rows, equal to the counts of MEMINFO in pid blocks (55, 204, 69, 43 and 91) except for "
                 "the one block of the Huawei report that prints no table. The Pss Total of the TOTAL row equaled "
                 "the total printed in the App Summary in every block that prints both (55, 204, 68, 43 and 91 "
                 "blocks, counted separately from the reader). Rss Total (KB) was empty on all rows of the Huawei "
                 "and Transsion-brand reports. Not examined: Android 11, 12 and 14 and vendors other than the four "
                 "seen."
                 "\nOn the corpus the run gave s20fe_a13 77 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cpu",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 77 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_memory_summary": {
        "name": "Bug Report - Memory Summary",
        "description": "The uptime lines and the Total RAM, Free RAM, Used RAM, Lost RAM and related lines of the "
                      "meminfo service dump of an Android bug report text, as name and value pairs.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Processes and Memory",
        "notes": "One row per line that starts with Uptime and Realtime (two rows, the numbers as printed), Total "
                 "RAM, Free RAM, Used RAM, Lost RAM, ZRAM, Tuning, DMA-BUF, DMA-BUF Heaps, DMA-BUF Heaps pool, GPU "
                 "or Kernel CMA in the meminfo service dump. Value is the text after the colon as printed, with "
                 "its kilobytes and parentheses. The totals are printed after the per process lists, so a meminfo "
                 "dump cut by the device time limit does not hold them (the Transsion-brand report has the uptime "
                 "rows only; the Samsung S-series report, also cut, holds them). The values are a snapshot taken "
                 "when the dump ran.\n"
                 "A report that has no such section gives no rows, and a section that the device cut at its time "
                 "limit is logged once and the rows from it may be partial; no rows says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android "
                 "16, Huawei and a Transsion-brand phone on Android 10, Motorola on Android 15): 15, 14, 8, 2 and "
                 "12 rows. The rows were read, but they were not counted a second time. Value held one value on "
                 "both rows of the Transsion-brand report (the uptime and realtime numbers were equal). Not "
                 "examined: Android 11, 12 and 14 and vendors other than the four seen."
                 "\nOn the corpus the run gave s20fe_a13 11 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cpu",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 11 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
}

from datetime import timedelta

from scripts import dumpstate_accountspower as ap
from scripts import dumpstate_reader
from scripts.ilapfuncs import artifact_processor, logfunc

REPORT_GLOBS = ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip')


def _reports(context):
    """The bug report texts among the staged files, as (Source File label, Report) pairs."""
    return dumpstate_reader.load_reports(context.get_files_found(), context.get_relative_path, logfunc)


def _source_path(context, reports):
    """The staged files that were read; the matched files when none was a bug report."""
    paths = [report.source.path for _label, report in reports] or sorted(str(path) for path in context.get_files_found())
    return '\n'.join(dict.fromkeys(str(path) for path in paths))


def _log_cuts(label, report, service, lines):
    """Say so when the platform cut a dump of ``service`` that holds the rows (or when it cut one and there are no rows)."""
    cut = [section for section in report.sections if section.kind == 'service' and section.name == service and section.timeout_ms]
    if lines:
        cut = [section for section in cut if any(section.line < number < section.end_line for number in lines)]
    if cut:
        dumpstate_reader.say_once(logfunc, f'Bug report {label}: the {service} service dump was cut by a {cut[0].timeout_ms} ms '
                                           f'timeout, the rows from it may be partial')


def _log_empty_section(label, report, kind, name):
    """Say once that a section the artifact reads was not found, so that no rows is not read as nothing happened."""
    if not any(section.kind == kind and section.name == name for section in report.sections):
        dumpstate_reader.say_once(logfunc, f'Bug report {label}: no {name} section was found in this report')


def _wall_utc(report, text):
    """UTC datetime for a device wall-clock text without a zone, or None (no zone in the report, not a time, before 2009)."""
    moment = dumpstate_reader.parse_wall_time(text)
    if moment is None or moment.year < 2009:
        return None
    return report.clock.to_utc(text)


def _dash_utc(report, text):
    return _wall_utc(report, ap.dash_time(text))


def _epoch_ms_utc(text):
    value = str(text).strip()
    if dumpstate_reader.is_digits(value) and dumpstate_reader.plausible_epoch_ms(int(value)):
        return dumpstate_reader.epoch_ms_to_utc(int(value))
    return None


UNREAD = {'account_history': 'account_history_unread', 'sync_last': 'sync_last_unread', 'ps': 'ps_unread',
          'memory_processes': 'meminfo_blocks_unread', 'memory_entries': 'memory_entry_unread', 'procstats': 'procstats_unread',
          'power_events': 'power_event_unread', 'power_wake_locks': 'power_wake_lock_unread', 'backup_queues': 'backup_queue_unread',
          'thermal': 'thermal_unread', 'sync_status': 'sync_account_heading_unread'}


def _log_unread(label, report, table, service):
    """Say once how many lines of the part were not in the shape the reader expects (they are not listed)."""
    count = ap.tables(report).counts.get(UNREAD.get(table, ''), 0)
    if count:
        dumpstate_reader.say_once(logfunc, f'Bug report {label}: {count} line(s) or block(s) of the {service} part were not in the '
                                           f'expected shape and are not listed ({table})')


def _each(context, table, service, kind='service'):
    """Yield ``(label, report, row)`` for every row of ``table``; logs a cut dump, a missing section and lines not read."""
    reports = _reports(context)
    out = []
    for label, report in reports:
        rows = ap.rows(report, table)
        _log_empty_section(label, report, kind, service)
        _log_unread(label, report, table, service)
        if kind == 'service':
            _log_cuts(label, report, service, [row.line for row in rows])
        out.extend((label, report, row) for row in rows)
    return reports, out


@artifact_processor
def bugreport_accounts(context):
    headers = ('User', 'User Name', 'User Flags (as stored)', 'Account Name', 'Account Type', 'Source Line', 'Source File')
    reports, items = _each(context, 'accounts', 'account')
    rows = [(r.user, r.user_name, r.user_flags, r.name, r.account_type, r.line, label) for label, _report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_account_history(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'User', 'Account ID', 'Action', 'UID', 'Table', 'Key',
               'Source Line', 'Source File')
    reports, items = _each(context, 'account_history', 'account')
    rows = [(_wall_utc(report, r.time_text), r.time_text, r.user, r.account_id, r.action, r.uid, r.table, r.key, r.line, label)
            for label, report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_account_authenticators(context):
    headers = ('User', 'Account Type', 'Component', 'UID', 'Last Update Time (as printed)', 'Source Line', 'Source File')
    reports, items = _each(context, 'authenticators', 'account')
    rows = [(r.user, r.account_type, r.component, r.uid, r.updated, r.line, label) for label, _report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_account_visibility(context):
    headers = ('User', 'Account', 'Package', 'Visibility (as stored)', 'Source Line', 'Source File')
    reports, items = _each(context, 'account_visibility', 'account')
    rows = [(r.user, r.account, r.package, r.value, r.line, label) for label, _report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_sync_adapter_status(context):
    headers = (('Last Success (UTC)', 'datetime'), ('Last Failure (UTC)', 'datetime'), 'User', 'Account', 'Account Type',
               'Account State (as printed)', 'Authority', 'Syncable', 'Enabled', 'Count Loc', 'Count Poll', 'Count Per', 'Count Feed', 'Count User',
               'Count Othr', 'Count Tot', 'Count Fail', 'Count Can', 'Time (as printed)', 'Last Success Source',
               'Last Success Time As Printed', 'Last Failure Source', 'Last Failure Time As Printed', 'Last Failure Message',
               'Backoff', 'Source Line', 'Source File')
    reports, items = _each(context, 'sync_status', 'content')
    rows = [(_wall_utc(report, r.success_time), _wall_utc(report, r.failure_time), r.user, r.account, r.account_type, r.account_state,
             r.authority, r.syncable, r.enabled, r.loc, r.poll, r.per, r.feed, r.user_req, r.othr, r.total, r.fail, r.cancel, r.time,
             r.success_source, r.success_time, r.failure_source, r.failure_time, r.failure_message, r.backoff, r.line, label)
            for label, report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_sync_recent_history(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Source', 'Duration (s as printed)', 'Extra Field (as printed)',
               'User', 'Account', 'Account Type', 'Authority', 'Reason', 'Message', 'Extras', 'Entry', 'Row As Printed',
               'Source Line', 'Source File')
    reports, items = _each(context, 'sync_history', 'content')
    rows = [(_wall_utc(report, r.time_text), r.time_text, r.source, r.duration, r.extra, r.user, r.account, r.account_type,
             r.authority, r.reason, r.message, r.extras, r.index, r.text, r.line, label) for label, report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_sync_adapter_last_syncs(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Result', 'Source', 'Elapsed (as printed)', 'Reason', 'Exemption',
               'Extras', 'User', 'Account', 'Account Type', 'Authority', 'Source Line', 'Source File')
    reports, items = _each(context, 'sync_last', 'content')
    rows = [(_wall_utc(report, r.time_text), r.time_text, r.result, r.source, r.elapsed, r.reason, r.exemption, r.extras, r.user,
             r.account, r.account_type, r.authority, r.line, label) for label, report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_sync_jobs(context):
    headers = ('List', 'Job ID', 'User', 'Account', 'Account Type', 'Authority', 'Source', 'Details (as printed)',
               'Source Line', 'Source File')
    reports, items = _each(context, 'sync_jobs', 'content')
    rows = [(r.kind, r.job_id, r.user, r.account, r.account_type, r.authority, r.source, r.details, r.line, label)
            for label, _report, r in items]
    return headers, rows, _source_path(context, reports)


def _paren_time(value):
    return value.partition('(')[2].partition(')')[0]


@artifact_processor
def bugreport_sync_state(context):
    headers = ('Name', 'Value', ('Time (UTC)', 'datetime'), 'Source Line', 'Source File')
    reports, items = _each(context, 'sync_facts', 'content')
    rows = [(r.name, r.value, _wall_utc(report, _paren_time(r.value)) if r.name == 'Now' else None, r.line, label)
            for label, report, r in items]
    return headers, rows, _source_path(context, reports)


BACKUP_TIME_FACTS = ('next scheduled', 'now (in the Last backup pass started line)', 'Last backup pass started')


@artifact_processor
def bugreport_backup_state(context):
    headers = ('Name', 'Value', ('Time (UTC)', 'datetime'), 'Source Line', 'Source File')
    reports, items = _each(context, 'backup_facts', 'backup')
    rows = [(r.name, r.value, _epoch_ms_utc(r.value) if r.name in BACKUP_TIME_FACTS else None, r.line, label)
            for label, _report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_backup_transports(context):
    headers = ('List', 'Transport', 'Marked With * (current)', 'Destination', 'Intent', 'Source Line', 'Source File')
    reports, items = _each(context, 'backup_transports', 'backup')
    rows = [(r.kind, r.name, 'yes' if r.current else '', r.destination, r.intent, r.line, label) for label, _report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_backup_package_state(context):
    headers = ('Transport', 'Package', 'State Bytes (as printed)', 'Source Line', 'Source File')
    reports, items = _each(context, 'backup_package_state', 'backup')
    rows = [(r.transport, r.package, r.state_bytes, r.line, label) for label, _report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_backup_participants(context):
    headers = ('UID', 'Package', 'Source Line', 'Source File')
    reports, items = _each(context, 'backup_participants', 'backup')
    rows = [(r.uid, r.package, r.line, label) for label, _report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_backup_queues(context):
    headers = ('Queue', 'Package', 'Number Before Package (as printed)', ('Time (UTC)', 'datetime'), 'Source Line', 'Source File')
    reports, items = _each(context, 'backup_queues', 'backup')
    rows = [(r.queue, r.package, r.value, _epoch_ms_utc(r.value), r.line, label) for label, _report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_users(context):
    headers = ('User ID', 'Name', 'UserInfo Flags (hex as printed)', 'Serial No', 'Is Primary', 'Parent ID', 'Type', 'Flags Line (as printed)',
               'State', 'Created (as printed, relative)', 'Last Logged In (as printed, relative)', 'Start Time (as printed, relative)',
               'Unlock Time (as printed, relative)', 'Last Entered Foreground (as printed, relative)', 'Has Profile Owner',
               'Restrictions', 'Effective Restrictions', 'Source Line', 'Source File')
    reports, items = _each(context, 'users', 'user')
    rows = [(r.user_id, r.name, r.flags_hex, r.serial, r.primary, r.parent, r.user_type, r.flags, r.state, r.created,
             r.last_logged_in, r.start_time, r.unlock_time, r.last_foreground, r.profile_owner, r.restrictions,
             r.effective_restrictions, r.line, label) for label, _report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_user_manager_facts(context):
    headers = ('Name', 'Value', 'Source Line', 'Source File')
    reports, items = _each(context, 'user_facts', 'user')
    rows = [(r.name, r.value, r.line, label) for label, _report, r in items]
    return headers, rows, _source_path(context, reports)


def _history_time(report, event):
    """UTC datetime of a battery history record, or None."""
    if event.form == 'F2':
        return report.setting_change_time(event.time_text)[1]
    if not event.anchor or event.delta_ms is None:
        return None
    anchor = _wall_utc(report, event.anchor)
    return anchor + timedelta(milliseconds=event.delta_ms) if anchor is not None else None


@artifact_processor
def bugreport_battery_history(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Clock Record Used (as printed)', 'Level (%)', 'State Bits (hex as printed)',
               'Marker', 'Changes (as printed)', 'Source Line', 'Source File')
    reports, items = _each(context, 'battery_history', 'batterystats')
    rows = [(_history_time(report, r), r.time_text, r.anchor if r.form == 'F1' else '', r.level, r.state, r.marker, r.changes, r.line, label)
            for label, report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_battery_daily_summary(context):
    headers = (('Period Start (UTC)', 'datetime'), ('Period End (UTC)', 'datetime'), 'Period', 'Period Start As Printed',
               'Period End As Printed', 'Discharge Steps', 'Charge Steps', 'Totals (as printed)', 'Package Changes',
               'Source Line', 'Source File')
    reports, items = _each(context, 'battery_daily', 'batterystats')
    rows = [(_dash_utc(report, r.start), _dash_utc(report, r.end), r.kind, r.start, r.end, r.discharge_steps, r.charge_steps,
             r.totals, r.package_changes, r.line, label) for label, report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_battery_package_changes(context):
    headers = (('Period Start (UTC)', 'datetime'), ('Period End (UTC)', 'datetime'), 'Period Start As Printed', 'Period End As Printed',
               'Change', 'Package', 'Version Code', 'Source Line', 'Source File')
    reports, items = _each(context, 'battery_packages', 'batterystats')
    rows = [(_dash_utc(report, r.period_start), _dash_utc(report, r.period_end), r.period_start, r.period_end, r.change, r.package,
             r.version, r.line, label) for label, report, r in items]
    return headers, rows, _source_path(context, reports)


def _uid_packages(report, uid):
    return ', '.join(ap.tables(report).uid_packages.get(uid, []))


@artifact_processor
def bugreport_battery_power_use(context):
    headers = ('Kind', 'Name', 'Context (as printed)', 'Total (as printed)', 'Detail (as printed)', 'Source Line', 'Source File')
    reports, items = _each(context, 'battery_power', 'batterystats')
    rows = [(r.kind, r.name, r.context, r.total, r.detail, r.line, label) for label, _report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_battery_wake_locks(context):
    headers = ('Kind', 'UID', 'Packages In UID Block', 'Wake Lock', 'Usage (as printed)', 'Source Line', 'Source File')
    reports, items = _each(context, 'battery_wake_locks', 'batterystats')
    rows = [(r.kind, r.uid, _uid_packages(report, r.uid), r.name, r.usage, r.line, label) for label, report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_battery_service_state(context):
    headers = ('Name', 'Value', 'Source Line', 'Source File')
    reports, items = _each(context, 'battery_facts', 'battery')
    rows = [(r.name, r.value, r.line, label) for label, _report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_thermal_state(context):
    headers = ('Group', 'Kind', 'Name', 'Type (as stored)', 'Value (as printed)', 'Status (as stored)', 'Detail (as printed)',
               'Source Line', 'Source File')
    reports, items = _each(context, 'thermal', 'thermalservice')
    rows = [(r.group, r.kind, r.name, r.item_type, r.value, r.status, r.detail, r.line, label) for label, _report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_power_state(context):
    headers = ('Block', 'Name', 'Value', 'Source Line', 'Source File')
    reports, items = _each(context, 'power_facts', 'power')
    rows = [(r.block, r.name, r.value, r.line, label) for label, _report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_power_wake_locks(context):
    headers = ('Level', 'Tag', 'Flags', 'Held (as printed, relative)', 'UID', 'PID', 'Details (as printed)', 'Source Line', 'Source File')
    reports, items = _each(context, 'power_wake_locks', 'power')
    rows = [(r.level, r.tag, r.flags, r.held, r.uid, r.pid, r.details, r.line, label) for label, _report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_power_events(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'History', 'Entry', 'UID', 'Display ID (as printed)', 'State', 'Reason',
               'Foreground Package', 'Caller', 'Held For (as printed)', 'Lock Level', 'Tag', 'Details (as printed)',
               'Source Line', 'Source File')
    reports, items = _each(context, 'power_events', 'power')
    rows = [(report.setting_change_time(r.time_text)[1], r.time_text, r.kind, r.index, r.uid, r.display, r.state, r.reason,
             r.foreground, r.caller, r.held, r.level, r.tag, r.details, r.line, label) for label, report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_device_idle_state(context):
    headers = ('Block', 'Name', 'Value', 'Source Line', 'Source File')
    reports, items = _each(context, 'idle_facts', 'deviceidle')
    rows = [(r.block, r.name, r.value, r.line, label) for label, _report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_device_idle_history(context):
    headers = ('Position', 'State', 'Time Ago (as printed)', 'Reason', 'Source Line', 'Source File')
    reports, items = _each(context, 'idle_history', 'deviceidle')
    rows = [(r.position, r.state, r.ago, r.reason, r.line, label) for label, _report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_process_stats(context):
    headers = ('Period', 'Process', 'UID', 'Version', 'State', 'Share Of Time (as printed)', 'Measures (as printed)',
               ('Period Start (UTC)', 'datetime'), 'Period Start As Printed', 'Source Line', 'Source File')
    reports, items = _each(context, 'procstats', 'procstats')
    rows = [(r.period, r.process, r.uid, r.version, r.state, r.share, r.measures, _dash_utc(report, r.period_start), r.period_start,
             r.line, label) for label, report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_process_threads(context):
    headers = ('PID', 'TID', 'PPID', 'User', 'Command', 'Label', 'State', 'VSZ (as printed)', 'RSS (as printed)', 'WCHAN', 'ADDR',
               'PRI', 'NI', 'RTPRIO', 'SCH', 'PCY', 'CPU Time (as printed)', 'Source Line', 'Source File')
    reports, items = _each(context, 'ps', 'PROCESSES AND THREADS', kind='command')
    rows = [(r.pid, r.tid, r.ppid, r.user, r.command, r.label, r.state, r.vsz, r.rss, r.wchan, r.addr, r.pri, r.nice, r.rtprio,
             r.sched, r.policy, r.cpu_time, r.line, label) for label, _report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_memory_by_process(context):
    headers = ('List', 'Kilobytes', 'Process', 'PID', 'Note', 'User (as printed)', 'In Swap (KB)', 'Source Line', 'Source File')
    reports, items = _each(context, 'memory_entries', 'meminfo')
    rows = [(r.basis, r.kilobytes, r.process, r.pid, r.note, r.user, r.swap_kilobytes, r.line, label) for label, _report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_memory_process_detail(context):
    headers = ('PID', 'Process', 'Pss Total (KB)', 'Private Dirty (KB)', 'Shared Dirty (KB)', 'SwapPss Dirty (KB)', 'Rss Total (KB)',
               'Heap Size (KB)', 'Heap Alloc (KB)', 'Heap Free (KB)', 'Native Heap Pss (KB)', 'Dalvik Heap Pss (KB)',
               'Summary Java Heap (KB)', 'Summary Native Heap (KB)', 'Summary Code (KB)', 'Summary Stack (KB)',
               'Summary Graphics (KB)', 'Summary Private Other (KB)', 'Summary System (KB)', 'Views', 'Activities',
               'Source Line', 'Source File')
    reports, items = _each(context, 'memory_processes', 'meminfo')
    rows = [(r.pid, r.process, r.pss_total, r.private_dirty, r.shared_dirty, r.swap_pss, r.rss_total, r.heap_size, r.heap_alloc,
             r.heap_free, r.native_heap_pss, r.dalvik_heap_pss, r.java_heap, r.native_heap, r.code, r.stack, r.graphics,
             r.private_other, r.system, r.views, r.activities, r.line, label) for label, _report, r in items]
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_memory_summary(context):
    headers = ('Name', 'Value', 'Source Line', 'Source File')
    reports, items = _each(context, 'memory_facts', 'meminfo')
    rows = [(r.name, r.value, r.line, label) for label, _report, r in items]
    return headers, rows, _source_path(context, reports)

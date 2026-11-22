__artifacts_v2__ = {
    "whatsapp_business_quick_replies": {
        "name": "WhatsApp Business - Quick Replies",
        "description": "Saved quick replies in WhatsApp Business: shortcut, text and linked lists.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-21",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "WhatsApp Business",
        "notes": "Read from com.whatsapp.w4b/databases/msgstore.db: one row per quick_replies row. "
                 "Shortcut is title and Reply Text is content. Field meanings come from the decompiled "
                 "WhatsApp Business app (versionName 2.26.45.80). Tested on a lab test account capture "
                 "of WhatsApp Business 2.26.45.80 that is not in the corpus, against values entered in "
                 "the app. The app adds one example reply of its own, so a row does not establish that "
                 "the user wrote it (a copy taken before the tester added a reply already held 1 of "
                 "the 2 tested rows). Linked Lists reads associated_label_ids, which the app writes as "
                 "comma-separated ids, and shows the labels row name with that _id, or the id itself "
                 "when none matches. That the ids are labels row ids is not established and the column "
                 "was not exercised. Attachments counts quick_reply_attachments rows and held 0. Times "
                 "Used sums usage_count over the quick_reply_usage rows still present. The app deletes "
                 "usage rows older than 7 days, so this is not a lifetime count. Last Used is the "
                 "latest usage_date still present, which the app writes as a yyyyMMdd day in the "
                 "phone's time zone at the time of use, and is shown as that local date. One known use "
                 "gave 1 and the expected day.",
        "paths": ('*/com.whatsapp.w4b/databases/msgstore.db*', '*/com.whatsapp.w4b/databases/wa.db*',
                  '*/com.whatsapp.w4b/databases/smb.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "zap",
    },
    "whatsapp_business_chat_lists": {
        "name": "WhatsApp Business - Chat Lists",
        "description": "Chats recorded in lists (labels) in WhatsApp Business.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-21",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "WhatsApp Business",
        "notes": "Read from com.whatsapp.w4b/databases/msgstore.db: one row per labeled_jid row, "
                 "joined to labels for the list name and to the jid table for the chat. Chat Name "
                 "comes from wa_contacts in the wa.db beside it. It is display_name, or wa_name when "
                 "that is empty, and is blank when wa_contacts has no row with the same id. Field "
                 "meanings come from the decompiled WhatsApp Business app (versionName 2.26.45.80). "
                 "Tested on a lab test account capture of WhatsApp Business 2.26.45.80 that is not in "
                 "the corpus, against values entered in the app. A chat placed in 2 lists gave 2 rows. "
                 "Lists with no chats are not reported. On the tested account 3 of the 5 lists were "
                 "made by the app and held no chats. The table has no time, so a row does not show "
                 "when the chat was added.",
        "paths": ('*/com.whatsapp.w4b/databases/msgstore.db*', '*/com.whatsapp.w4b/databases/wa.db*',
                  '*/com.whatsapp.w4b/databases/smb.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "tag",
    },
    "whatsapp_business_customer_notes": {
        "name": "WhatsApp Business - Customer Notes",
        "description": "Notes the WhatsApp Business account saved about a chat.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-21",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "WhatsApp Business",
        "notes": "Read from com.whatsapp.w4b/databases/smb.db: one row per wa_notes row. Created and "
                 "Modified are created_at and modified_at read as Unix milliseconds. The app keeps one "
                 "note per chat and overwrites its text on an edit. An edit was not exercised: Created "
                 "and Modified were equal on the tested row. Chat is chat_jid. Chat Name comes from "
                 "wa_contacts in the wa.db beside it. It is display_name, or wa_name when that is "
                 "empty, and is blank when wa_contacts has no row with the same id. Field meanings "
                 "come from the decompiled WhatsApp Business app (versionName 2.26.45.80). Tested on a "
                 "lab test account capture of WhatsApp Business 2.26.45.80 that is not in the corpus, "
                 "against values entered in the app. One known note was read back. note_type and "
                 "account_jid are not reported: note_type held 0 and account_jid was NULL on the "
                 "tested row.",
        "paths": ('*/com.whatsapp.w4b/databases/msgstore.db*', '*/com.whatsapp.w4b/databases/wa.db*',
                  '*/com.whatsapp.w4b/databases/smb.db*'),
        "output_types": "standard",
        "artifact_icon": "file-text",
    },
    "whatsapp_business_automated_messages": {
        "name": "WhatsApp Business - Automated Messages",
        "description": "Greeting and away message settings in WhatsApp Business.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-21",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "WhatsApp Business",
        "notes": "Read from the greeting_* and away_* keys of the props table in "
                 "com.whatsapp.w4b/databases/msgstore.db, one row each for Greeting and Away. Field "
                 "meanings come from the decompiled WhatsApp Business app (versionName 2.26.45.80). "
                 "Tested on a lab test account capture of WhatsApp Business 2.26.45.80 that is not in "
                 "the corpus, against values entered in the app. Setting is on or off from greeting_on "
                 "for Greeting. For Away it is away_state. always_on (1), custom (2) and "
                 "non_business_hours (3) are the names the app's away settings screen gives these "
                 "values. off (0) is this module's label: the app treats 0 as away not enabled. "
                 "Recipients is the distribution value named everyone (0), non_contacts (1), allowlist "
                 "(2) or blocklist (3). Setting or Recipients is blank when its key is not stored, and "
                 "the app reads a missing key as 0. On three of the four tested captures "
                 "away_distribution was not stored. Schedule Start and End are away_start_time and "
                 "away_end_time read as Unix milliseconds. The app writes them when a custom schedule "
                 "is saved. No capture was taken after the schedule was changed away from custom, so "
                 "whether they remain is not established. Read them with Setting. Allow List and Block "
                 "List are the stored account lists. Exercised: on, off, always_on, custom, allowlist, "
                 "and everyone as a stored value for Greeting only. non_business_hours, non_contacts, "
                 "blocklist and the Greeting lists were not. A setting does not establish that a "
                 "message was sent: two incoming messages received while Away was always_on got no "
                 "away reply. The app checks further conditions before it sends one. The away_messages "
                 "table, which the app uses to record who was already sent the away reply, held no "
                 "rows on the tested captures and is not read.",
        "paths": ('*/com.whatsapp.w4b/databases/msgstore.db*', '*/com.whatsapp.w4b/databases/wa.db*',
                  '*/com.whatsapp.w4b/databases/smb.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "message-circle",
    },
    "whatsapp_business_profiles": {
        "name": "WhatsApp Business - Business Profiles",
        "description": "Business profiles WhatsApp Business stored in wa.db.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-21",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "WhatsApp Business",
        "notes": "Read from com.whatsapp.w4b/databases/wa.db: one row per wa_biz_profiles row. "
                 "Business Name is verified_name from wa_vnames for the same account. Categories and "
                 "Websites come from their child tables. Columns carry the table's own column names. "
                 "Business Name was matched to the known name on one row. Tested on a lab test account "
                 "capture of WhatsApp Business 2.26.45.80 that is not in the corpus, against values "
                 "entered in the app. On the tested file the only row was the device's own business, "
                 "with its known name and category. A profile can belong to another business. The "
                 "table has no column that marks the device's own account, so compare Account with the "
                 "device's own number. Description, Email, Address, Latitude, Longitude, Websites and "
                 "Hours Note were empty on the tested row and were not exercised. The test account had "
                 "a business hours setting, and it was not found in hours_note or "
                 "wa_biz_profiles_hours, which held no rows and is not read. Time Zone is time_zone, "
                 "which the app reads with the business hours. A stored 0, 0 coordinate pair is shown "
                 "blank. Other profile fields are not reported.",
        "paths": ('*/com.whatsapp.w4b/databases/msgstore.db*', '*/com.whatsapp.w4b/databases/wa.db*',
                  '*/com.whatsapp.w4b/databases/smb.db*'),
        "output_types": ["html", "tsv", "lava", "kml"],
        "artifact_icon": "briefcase",
    },
}

import os
import re
import sqlite3
from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import android_user, unique_files
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

# AwaySettingsActivity names 1 to 3. 'off' is this module's label for 0, which the app treats as not enabled.
_AWAY_STATES = {0: 'off', 1: 'always_on', 2: 'custom', 3: 'non_business_hours'}
_RECIPIENTS = {0: 'everyone', 1: 'non_contacts', 2: 'allowlist', 3: 'blocklist'}


def _time(value):
    if not isinstance(value, int) or value <= 0:
        return ''
    try:
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _local_day(value):
    """A yyyyMMdd integer as YYYY-MM-DD, the phone's local date."""
    digits = str(value or '')
    return f'{digits[:4]}-{digits[4:6]}-{digits[6:8]}' if re.fullmatch(r'\d{8}', digits) else digits


def _tables(db):
    return {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def _columns(db, table):
    return {row[1] for row in db.execute(f'PRAGMA table_info("{table}")')}


def _stores(context, name):
    for file_found in unique_files(context):
        path = str(file_found)
        if os.path.basename(path) == name:
            yield path


def _contacts(folder):
    """{jid: name} from the wa.db in the same databases folder."""
    path = os.path.join(folder, 'wa.db')
    if not os.path.isfile(path):
        return {}
    db = open_sqlite_db_readonly(path)
    if db is None:
        return {}
    names = {}
    try:
        if 'wa_contacts' in _tables(db) and {'jid', 'display_name', 'wa_name'} <= _columns(db, 'wa_contacts'):
            for jid, display, push in db.execute('SELECT jid, display_name, wa_name FROM wa_contacts'):
                if jid and (display or push):
                    names.setdefault(jid, display or push)
    except sqlite3.Error as error:
        logfunc(f'WhatsApp Business Tools: could not read contacts: {error}')
    finally:
        db.close()
    return names


def _int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _named(names, value):
    number = _int(value)
    if number is None:
        return ''
    return f'{names[number]} ({number})' if number in names else f'Unknown ({number})'


@artifact_processor
def whatsapp_business_quick_replies(context):
    data_headers = ('Shortcut', 'Reply Text', 'Linked Lists', 'Attachments', 'Times Used (kept rows)',
                    'Last Used (local date)', 'Android User')
    data_list, sources = [], []
    for path in _stores(context, 'msgstore.db'):
        db = open_sqlite_db_readonly(path)
        if db is None:
            continue
        sources.append(path)
        user = android_user(context.get_relative_path(path))
        try:
            tables = _tables(db)
            if 'quick_replies' not in tables:
                continue
            labels = dict(db.execute('SELECT _id, label_name FROM labels')) if 'labels' in tables else {}
            attachments, usage = {}, {}
            if 'quick_reply_attachments' in tables:
                for reply, count in db.execute('SELECT quick_reply_id, count(*) FROM quick_reply_attachments '
                                               'GROUP BY quick_reply_id'):
                    attachments[str(reply)] = count
            if 'quick_reply_usage' in tables:
                # quick_reply_id is TEXT in this table while quick_replies._id is an integer.
                for reply, total, last in db.execute('SELECT quick_reply_id, sum(usage_count), max(usage_date) '
                                                     'FROM quick_reply_usage GROUP BY quick_reply_id'):
                    usage[str(reply)] = (total, last)
            records = db.execute('SELECT _id, title, content, associated_label_ids FROM quick_replies '
                                 'ORDER BY _id').fetchall()
        except sqlite3.Error as error:
            logfunc(f'WhatsApp Business Tools: could not read quick replies: {error}')
            continue
        finally:
            db.close()
        for row_id, title, content, label_ids in records:
            linked = [labels.get(_int(part), part) for part in str(label_ids or '').replace(',', ' ').split()]
            total, last = usage.get(str(row_id), ('', ''))
            data_list.append((title or '', content or '', ', '.join(linked), attachments.get(str(row_id), 0),
                              total, _local_day(last), user))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def whatsapp_business_chat_lists(context):
    data_headers = ('List', 'Chat', 'Chat Name', 'Android User')
    data_list, sources = [], []
    for path in _stores(context, 'msgstore.db'):
        db = open_sqlite_db_readonly(path)
        if db is None:
            continue
        sources.append(path)
        user = android_user(context.get_relative_path(path))
        names = _contacts(os.path.dirname(path))
        try:
            if not {'labels', 'labeled_jid', 'jid'} <= _tables(db):
                continue
            records = db.execute('SELECT l.label_name, j.raw_string FROM labeled_jid x '
                                 'JOIN labels l ON l._id = x.label_id '
                                 'LEFT JOIN jid j ON j._id = x.jid_row_id '
                                 'ORDER BY l.sort_id, l._id, x._id').fetchall()
        except sqlite3.Error as error:
            logfunc(f'WhatsApp Business Tools: could not read lists: {error}')
            continue
        finally:
            db.close()
        for label, jid in records:
            data_list.append((label or '', jid or '', names.get(jid, ''), user))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def whatsapp_business_customer_notes(context):
    data_headers = (('Created', 'datetime'), ('Modified', 'datetime'), 'Chat', 'Chat Name', 'Note',
                    'Android User')
    data_list, sources = [], []
    for path in _stores(context, 'smb.db'):
        db = open_sqlite_db_readonly(path)
        if db is None:
            continue
        sources.append(path)
        user = android_user(context.get_relative_path(path))
        names = _contacts(os.path.dirname(path))
        try:
            if 'wa_notes' not in _tables(db):
                continue
            records = db.execute('SELECT created_at, modified_at, chat_jid, note_content FROM wa_notes '
                                 'ORDER BY created_at').fetchall()
        except sqlite3.Error as error:
            logfunc(f'WhatsApp Business Tools: could not read notes: {error}')
            continue
        finally:
            db.close()
        for created, modified, jid, note in records:
            data_list.append((_time(created), _time(modified), jid or '', names.get(jid, ''), note or '', user))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def whatsapp_business_automated_messages(context):
    data_headers = ('Message Type', 'Setting', 'Message', ('Schedule Start', 'datetime'),
                    ('Schedule End', 'datetime'), 'Recipients', 'Allow List', 'Block List',
                    'Android User')
    data_list, sources = [], []
    for path in _stores(context, 'msgstore.db'):
        db = open_sqlite_db_readonly(path)
        if db is None:
            continue
        sources.append(path)
        user = android_user(context.get_relative_path(path))
        try:
            if 'props' not in _tables(db):
                continue
            props = dict(db.execute("SELECT key, value FROM props WHERE key LIKE 'greeting_%' "
                                    "OR key LIKE 'away_%'"))
        except sqlite3.Error as error:
            logfunc(f'WhatsApp Business Tools: could not read settings: {error}')
            continue
        finally:
            db.close()
        if 'greeting_on' in props or 'greeting_message' in props:
            enabled = props.get('greeting_on')
            setting = 'on' if enabled == 'true' else 'off' if enabled == 'false' else str(enabled or '')
            data_list.append(('Greeting', setting, props.get('greeting_message') or '', '', '',
                              _named(_RECIPIENTS, props.get('greeting_distribution')),
                              props.get('greeting_white_list') or '', props.get('greeting_black_list') or '',
                              user))
        if 'away_state' in props or 'away_message' in props:
            data_list.append(('Away', _named(_AWAY_STATES, props.get('away_state')),
                              props.get('away_message') or '', _time(_int(props.get('away_start_time'))),
                              _time(_int(props.get('away_end_time'))),
                              _named(_RECIPIENTS, props.get('away_distribution')),
                              props.get('away_white_list') or '', props.get('away_black_list') or '', user))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def whatsapp_business_profiles(context):
    data_headers = ('Account', 'Business Name', 'Categories', 'Description', 'Email', 'Address',
                    ('Latitude', 'latitude'), ('Longitude', 'longitude'), 'Websites', 'Hours Note',
                    'Time Zone', 'Android User')
    data_list, sources = [], []
    for path in _stores(context, 'wa.db'):
        db = open_sqlite_db_readonly(path)
        if db is None:
            continue
        sources.append(path)
        user = android_user(context.get_relative_path(path))
        try:
            tables = _tables(db)
            if 'wa_biz_profiles' not in tables:
                continue
            verified, categories, websites = {}, {}, {}
            if 'wa_vnames' in tables:
                verified = dict(db.execute('SELECT jid, verified_name FROM wa_vnames'))
            if 'wa_biz_profiles_categories' in tables:
                for profile, name in db.execute('SELECT wa_biz_profile_id, category_name FROM wa_biz_profiles_categories'):
                    categories.setdefault(profile, []).append(name or '')
            if 'wa_biz_profiles_websites' in tables:
                for profile, site in db.execute('SELECT wa_biz_profile_id, websites FROM wa_biz_profiles_websites'):
                    websites.setdefault(profile, []).append(site or '')
            records = db.execute('SELECT _id, jid, business_description, email, address, latitude, longitude, '
                                 'hours_note, time_zone FROM wa_biz_profiles ORDER BY _id').fetchall()
        except sqlite3.Error as error:
            logfunc(f'WhatsApp Business Tools: could not read profiles: {error}')
            continue
        finally:
            db.close()
        for row_id, jid, about, email, address, latitude, longitude, hours, zone in records:
            has_point = latitude not in (None, 0, 0.0) or longitude not in (None, 0, 0.0)
            data_list.append((jid or '', verified.get(jid) or '', ', '.join(categories.get(row_id, [])),
                              about or '', email or '', address or '', latitude if has_point else '',
                              longitude if has_point else '', ', '.join(websites.get(row_id, [])), hours or '',
                              zone or '', user))
    return data_headers, data_list, '\n'.join(sources)

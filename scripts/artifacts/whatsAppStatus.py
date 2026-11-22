__artifacts_v2__ = {
    "whatsapp_status_updates": {
        "name": "WhatsApp - Status Updates",
        "description": "Rows of the status table in WhatsApp's status.db: status updates the account posted "
                       "and status updates it received.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-21",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "Read from com.whatsapp/databases/status.db with its write-ahead log, one row per row "
                 "of the status table. Field meanings come from the decompiled WhatsApp Business app "
                 "(versionName 2.26.45.80). A status table is also present in com.whatsapp on the six "
                 "tested images. Its columns vary with the app version: 21 on the two Samsung images, "
                 "20 on three images and 16 on kevin_pocox7_a15, which has no received_timestamp "
                 "column and no status_thumbnail table. The names for Type (class X.EZF) and State "
                 "(class X.1t6, which jadx shows as EnumC42181t6) come from that Business app build "
                 "and are applied to both apps. Direction is Sent when sender_user_jid is status_me, "
                 "the value the app stores as sender for the account's own statuses. Every other value "
                 "is shown as Received. The app also treats a row whose sender is the account's own "
                 "identifier as its own. The module does not test for that, and no tested row had it. "
                 "Sender is blank on Sent rows. Sender Name comes from wa_contacts in the wa.db beside "
                 "it (display_name, then wa_name) and is blank when no contact matches. No tested row "
                 "had a matching contact, so a filled Sender Name was not exercised. Status Time, "
                 "Server Receipt Time and Received Time are timestamp, server_receipt_timestamp and "
                 "received_timestamp read as Unix milliseconds. A stored 0 or negative value, which "
                 "the app uses for no value, is shown blank. Server Receipt Time was -1 on the tested "
                 "Received rows, and Received Time was 0 on the tested Sent row. Type and State are "
                 "named from the app's status type and state enums, and a value outside them is shown "
                 "as Unknown. Text is text_data. Thumbnail is the image stored in "
                 "status_thumbnail.thumbnail, a JPEG on the 3 tested rows. When a status has more than "
                 "one thumbnail row, one is shown. The full media file is not linked: file_path was "
                 "empty on the tested media rows. Mime Type and Duration (as stored) come from "
                 "media_content. Archived is is_archived. Android User comes from the store's path. "
                 "Not reported from the status table: sort_id, uuid, status_info_row_id, secret, "
                 "content_proto, fp_proto, origin, flags, audience_type, stanza_xml, batch_state and "
                 "server_sts. View Count and Reaction Count are view_count and reaction_count from "
                 "status_interactions, blank when the status has no row there (kevin_pocox7_a15 has no "
                 "such table). The app's database triggers add 1 to view_count when a receipt gets a "
                 "seen_timestamp, and add or subtract 1 from reaction_count when a type 1 row is added "
                 "to or deleted from status_add_on. No trigger lowers view_count. On the WhatsApp "
                 "Business lab capture, View Count was 1 and Reaction Count was 0 on the one tested "
                 "Sent status, which had 1 known view. The 3 tested com.whatsapp rows had no "
                 "status_interactions row, so both columns were blank on them. A View Count above 1 "
                 "and a nonzero Reaction Count were not exercised. Other tables are not read. Among "
                 "them: status_add_on (one row per reaction, poll vote, question answer or sticker "
                 "interaction, by the app's add-on type enum) held no rows on any tested store, so its "
                 "fields could not be checked. status_interactions_totals, a second table of "
                 "interaction totals, held no rows on any tested store. status_receipt_device holds "
                 "per-device receipt records, and Status Viewers reports the per-user receipts. "
                 "status_text holds styling and link preview fields. It had 1 row across the tested "
                 "stores, on the lab capture, and its url and page_title were empty. status_info holds "
                 "per-chat counters that summarize these rows. The table holds only what the app still "
                 "keeps, so a missing status does not establish that none was posted or received. "
                 "Tested rows: the same 3 received VIDEO statuses, state RECEIVED, all from one "
                 "sender, on samsung_a166u_a16_known_20261116 and samsung_a166u_a16_known_20261117 "
                 "(com.whatsapp), and 1 sent TEXT status, state SENT, on a lab test account capture of "
                 "WhatsApp Business 2.26.45.80 that is not in the corpus. Both apps are read by the "
                 "same code. Other types and states, an archived row, and the older 16-column table "
                 "with rows were not exercised. On the other tested images in sample_data the table "
                 "held no rows.",
        "paths": ('*/com.whatsapp/databases/status.db*', '*/com.whatsapp/databases/wa.db*'),
        "output_types": "standard",
        "artifact_icon": "circle",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | 3 rows",
            "samsung_a166u_a16_known_20261117": "Android 16 | 3 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "dragna_pixel9a_a16": "Android 16 | 0 rows",
        },
    },
    "whatsapp_status_viewers": {
        "name": "WhatsApp - Status Viewers",
        "description": "Receipts WhatsApp stored for status updates: who received or viewed each one.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-21",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "Read from com.whatsapp/databases/status.db with its write-ahead log, one row per "
                 "status_seen_receipt row joined to its status. A receipt whose status row is no "
                 "longer in the table is not reported. Field meanings come from the decompiled "
                 "WhatsApp Business app (versionName 2.26.45.80). Viewed Time is seen_timestamp, which "
                 "the app writes for receipt type 13. Received Time is received_timestamp, which it "
                 "writes for the other receipt types the store accepts (5, 8, 15, 17, 18). What each "
                 "type number means was not established. Both are read as Unix milliseconds, and "
                 "Viewed Time is blank when the column is empty. Status Time is when the status was "
                 "posted. Viewer is receipt_user_jid. Viewer Name comes from wa_contacts in the wa.db "
                 "beside it and is blank when no contact has that identifier. The tested viewer was "
                 "stored as a lid identifier with no wa_contacts match, so a filled Viewer Name was "
                 "not exercised. A row records a receipt the app stored. No row does not establish "
                 "that nobody viewed a status. Tested on a lab test account capture of WhatsApp "
                 "Business 2.26.45.80 that is not in the corpus: a known view from a second test phone "
                 "gave 1 row with both times, and a capture taken before the view gave the same row "
                 "with Viewed Time blank. The six tested com.whatsapp images "
                 "(samsung_a166u_a16_known_20261116, samsung_a166u_a16_known_20261117, "
                 "hc_pixel8pro_a16, hc_pixel8pro_a17, kevin_pocox7_a15, dragna_pixel9a_a16) held no "
                 "receipt rows.",
        "paths": ('*/com.whatsapp/databases/status.db*', '*/com.whatsapp/databases/wa.db*'),
        "output_types": "standard",
        "artifact_icon": "eye",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | 0 rows",
            "samsung_a166u_a16_known_20261117": "Android 16 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "dragna_pixel9a_a16": "Android 16 | 0 rows",
        },
    },
    "whatsapp_business_status_updates": {
        "name": "WhatsApp Business - Status Updates",
        "description": "Rows of the status table in WhatsApp Business's status.db: status updates the "
                       "account posted and status updates it received.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-21",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "WhatsApp Business",
        "notes": "Read from com.whatsapp.w4b/databases/status.db with its write-ahead log, one row per "
                 "row of the status table. Field meanings come from the decompiled WhatsApp Business "
                 "app (versionName 2.26.45.80). A status table is also present in com.whatsapp on the "
                 "six tested images. Its columns vary with the app version: 21 on the two Samsung "
                 "images, 20 on three images and 16 on kevin_pocox7_a15, which has no "
                 "received_timestamp column and no status_thumbnail table. The names for Type (class "
                 "X.EZF) and State (class X.1t6, which jadx shows as EnumC42181t6) come from that "
                 "Business app build and are applied to both apps. Direction is Sent when "
                 "sender_user_jid is status_me, the value the app stores as sender for the account's "
                 "own statuses. Every other value is shown as Received. The app also treats a row "
                 "whose sender is the account's own identifier as its own. The module does not test "
                 "for that, and no tested row had it. Sender is blank on Sent rows. Sender Name comes "
                 "from wa_contacts in the wa.db beside it (display_name, then wa_name) and is blank "
                 "when no contact matches. No tested row had a matching contact, so a filled Sender "
                 "Name was not exercised. Status Time, Server Receipt Time and Received Time are "
                 "timestamp, server_receipt_timestamp and received_timestamp read as Unix "
                 "milliseconds. A stored 0 or negative value, which the app uses for no value, is "
                 "shown blank. Server Receipt Time was -1 on the tested Received rows, and Received "
                 "Time was 0 on the tested Sent row. Type and State are named from the app's status "
                 "type and state enums, and a value outside them is shown as Unknown. Text is "
                 "text_data. Thumbnail is the image stored in status_thumbnail.thumbnail, a JPEG on "
                 "the 3 tested rows. When a status has more than one thumbnail row, one is shown. The "
                 "full media file is not linked: file_path was empty on the tested media rows. Mime "
                 "Type and Duration (as stored) come from media_content. Archived is is_archived. "
                 "Android User comes from the store's path. Not reported from the status table: "
                 "sort_id, uuid, status_info_row_id, secret, content_proto, fp_proto, origin, flags, "
                 "audience_type, stanza_xml, batch_state and server_sts. View Count and Reaction Count "
                 "are view_count and reaction_count from status_interactions, blank when the status "
                 "has no row there (kevin_pocox7_a15 has no such table). The app's database triggers "
                 "add 1 to view_count when a receipt gets a seen_timestamp, and add or subtract 1 from "
                 "reaction_count when a type 1 row is added to or deleted from status_add_on. No "
                 "trigger lowers view_count. View Count was 1 and Reaction Count was 0 on the one "
                 "tested Sent status, which had 1 known view. The 3 tested com.whatsapp Received rows "
                 "had no status_interactions row, so both columns were blank on them. A View Count "
                 "above 1 and a nonzero Reaction Count were not exercised. Other tables are not read. "
                 "Among them: status_add_on (one row per reaction, poll vote, question answer or "
                 "sticker interaction, by the app's add-on type enum) held no rows on any tested "
                 "store, so its fields could not be checked. status_interactions_totals, a second "
                 "table of interaction totals, held no rows on any tested store. status_receipt_device "
                 "holds per-device receipt records, and Status Viewers reports the per-user receipts. "
                 "status_text holds styling and link preview fields. It had 1 row across the tested "
                 "stores, on the lab capture, and its url and page_title were empty. status_info holds "
                 "per-chat counters that summarize these rows. The table holds only what the app still "
                 "keeps, so a missing status does not establish that none was posted or received. "
                 "Tested rows: the same 3 received VIDEO statuses, state RECEIVED, all from one "
                 "sender, on samsung_a166u_a16_known_20261116 and samsung_a166u_a16_known_20261117 "
                 "(com.whatsapp), and 1 sent TEXT status, state SENT, on a lab test account capture of "
                 "WhatsApp Business 2.26.45.80 that is not in the corpus. Both apps are read by the "
                 "same code. Other types and states, an archived row, and the older 16-column table "
                 "with rows were not exercised. None of the six tested corpus images holds a "
                 "com.whatsapp.w4b status.db.",
        "paths": ('*/com.whatsapp.w4b/databases/status.db*', '*/com.whatsapp.w4b/databases/wa.db*'),
        "output_types": "standard",
        "artifact_icon": "circle",
    },
    "whatsapp_business_status_viewers": {
        "name": "WhatsApp Business - Status Viewers",
        "description": "Receipts WhatsApp Business stored for status updates: who received or viewed each "
                       "one.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-21",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "WhatsApp Business",
        "notes": "Read from com.whatsapp.w4b/databases/status.db with its write-ahead log, one row per "
                 "status_seen_receipt row joined to its status. A receipt whose status row is no "
                 "longer in the table is not reported. Field meanings come from the decompiled "
                 "WhatsApp Business app (versionName 2.26.45.80). Viewed Time is seen_timestamp, which "
                 "the app writes for receipt type 13. Received Time is received_timestamp, which it "
                 "writes for the other receipt types the store accepts (5, 8, 15, 17, 18). What each "
                 "type number means was not established. Both are read as Unix milliseconds, and "
                 "Viewed Time is blank when the column is empty. Status Time is when the status was "
                 "posted. Viewer is receipt_user_jid. Viewer Name comes from wa_contacts in the wa.db "
                 "beside it and is blank when no contact has that identifier. The tested viewer was "
                 "stored as a lid identifier with no wa_contacts match, so a filled Viewer Name was "
                 "not exercised. A row records a receipt the app stored. No row does not establish "
                 "that nobody viewed a status. Tested on a lab test account capture of WhatsApp "
                 "Business 2.26.45.80 that is not in the corpus: a known view from a second test phone "
                 "gave 1 row with both times, and a capture taken before the view gave the same row "
                 "with Viewed Time blank. The six tested com.whatsapp images "
                 "(samsung_a166u_a16_known_20261116, samsung_a166u_a16_known_20261117, "
                 "hc_pixel8pro_a16, hc_pixel8pro_a17, kevin_pocox7_a15, dragna_pixel9a_a16) held no "
                 "receipt rows.",
        "paths": ('*/com.whatsapp.w4b/databases/status.db*', '*/com.whatsapp.w4b/databases/wa.db*'),
        "output_types": "standard",
        "artifact_icon": "eye",
    },
}

import os
import sqlite3
from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import android_user, unique_files
from scripts.ilapfuncs import artifact_processor, check_in_embedded_media, logfunc, \
    open_sqlite_db_readonly

_OWN_STATUS = 'status_me'
# The app's status type and state enums, by stored value
_TYPES = {1: 'FUTURE', 2: 'PLACEHOLDER', 3: 'TEXT', 4: 'IMAGE', 5: 'VIDEO', 6: 'GIF', 7: 'VOICE',
          8: 'REVOKED', 9: 'QUIZ'}
_STATES = {0: 'PREPARING', 1: 'SENDING', 2: 'FAILED_TO_SEND', 3: 'SENT', 4: 'RECEIVED',
           5: 'VIEWING', 6: 'VIEWED', 7: 'PERMANENTLY_FAILED_TO_SEND'}


def _time(value):
    if not isinstance(value, int) or value <= 0:
        return ''
    try:
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _enum(names, value):
    if value is None:
        return ''
    name = names.get(value)
    return f'{name} ({value})' if name else f'Unknown ({value})'


def _tables(db):
    return {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def _columns(db, table):
    return {row[1] for row in db.execute(f'PRAGMA table_info("{table}")')}


def _contacts(status_path):
    """{jid: name} from the wa.db beside status.db."""
    path = os.path.join(os.path.dirname(status_path), 'wa.db')
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
        logfunc(f'WhatsApp Status: could not read contacts: {error}')
    finally:
        db.close()
    return names


def _stores(context):
    for file_found in unique_files(context):
        path = str(file_found)
        if os.path.basename(path) == 'status.db':
            yield path


def _sender(jid, names):
    if jid == _OWN_STATUS:
        return 'Sent', '', ''
    return 'Received', jid or '', names.get(jid, '')


def _updates(context):
    headers = (('Status Time', 'datetime'), ('Server Receipt Time', 'datetime'),
               ('Received Time', 'datetime'), 'Direction', 'Sender', 'Sender Name', 'Type', 'State',
               'Text', ('Thumbnail', 'media'), 'Mime Type', 'Duration (as stored)', 'Archived',
               'View Count', 'Reaction Count', 'Android User')
    rows, sources = [], []
    for path in _stores(context):
        db = open_sqlite_db_readonly(path)
        if db is None:
            continue
        sources.append(path)
        user = android_user(context.get_relative_path(path))
        names = _contacts(path)
        try:
            tables = _tables(db)
            if 'status' not in tables:
                continue
            columns = _columns(db, 'status')
            received = 'received_timestamp' if 'received_timestamp' in columns else 'NULL'
            archived = 'is_archived' if 'is_archived' in columns else 'NULL'
            thumbs, media, interactions = {}, {}, {}
            if 'status_interactions' in tables:
                for row_id, views, reactions in db.execute(
                        'SELECT status_row_id, view_count, reaction_count FROM status_interactions'):
                    interactions[row_id] = (views, reactions)
            if 'status_thumbnail' in tables:
                for row_id, blob in db.execute('SELECT status_row_id, thumbnail FROM status_thumbnail'):
                    if blob:
                        thumbs.setdefault(row_id, blob)
            if {'status_media_link', 'media_content'} <= tables:
                for row_id, mime, duration in db.execute(
                        'SELECT l.status_row_id, m.mime_type, m.media_duration FROM status_media_link l '
                        'JOIN media_content m ON m.row_id = l.media_content_row_id'):
                    media.setdefault(row_id, (mime or '', duration if duration is not None else ''))
            records = db.execute(
                f'SELECT row_id, timestamp, server_receipt_timestamp, {received}, sender_user_jid, '
                f'type, state, text_data, {archived} FROM status ORDER BY timestamp').fetchall()
        except sqlite3.Error as error:
            logfunc(f'WhatsApp Status: could not read status: {error}')
            continue
        finally:
            db.close()
        for row_id, stamp, server, got, jid, kind, state, text, is_archived in records:
            direction, sender, name = _sender(jid, names)
            blob = thumbs.get(row_id)
            item = check_in_embedded_media(path, blob) if blob else ''
            mime, duration = media.get(row_id, ('', ''))
            views, reactions = interactions.get(row_id, ('', ''))
            rows.append((_time(stamp), _time(server), _time(got), direction, sender, name,
                         _enum(_TYPES, kind), _enum(_STATES, state), text or '', item or '', mime,
                         duration, '' if is_archived is None else ('Yes' if is_archived else 'No'),
                         views, reactions, user))
    return headers, rows, '\n'.join(sources)


def _viewers(context):
    headers = (('Received Time', 'datetime'), ('Viewed Time', 'datetime'),
               ('Status Time', 'datetime'), 'Viewer', 'Viewer Name', 'Status Type', 'Status Text',
               'Android User')
    rows, sources = [], []
    for path in _stores(context):
        db = open_sqlite_db_readonly(path)
        if db is None:
            continue
        sources.append(path)
        user = android_user(context.get_relative_path(path))
        names = _contacts(path)
        try:
            if not {'status', 'status_seen_receipt'} <= _tables(db):
                continue
            records = db.execute(
                'SELECT s.timestamp, r.received_timestamp, r.seen_timestamp, r.receipt_user_jid, '
                's.type, s.text_data FROM status_seen_receipt r '
                'JOIN status s ON s.row_id = r.status_row_id ORDER BY r.received_timestamp').fetchall()
        except sqlite3.Error as error:
            logfunc(f'WhatsApp Status: could not read receipts: {error}')
            continue
        finally:
            db.close()
        for stamp, got, seen, jid, kind, text in records:
            rows.append((_time(got), _time(seen), _time(stamp), jid or '', names.get(jid, ''),
                          _enum(_TYPES, kind), text or '', user))
    return headers, rows, '\n'.join(sources)


@artifact_processor
def whatsapp_status_updates(context):
    return _updates(context)


@artifact_processor
def whatsapp_status_viewers(context):
    return _viewers(context)


@artifact_processor
def whatsapp_business_status_updates(context):
    return _updates(context)


@artifact_processor
def whatsapp_business_status_viewers(context):
    return _viewers(context)

"""WhatsApp add-on artifacts: reactions, edits, revoked messages, polls,
per-recipient receipts and system events from msgstore.db.

The map of which msgstore.db tables hold these records was informed by
WAInsight by Akhil Dara (https://github.com/akhil-dara/WAInsight, MIT
license). The queries here were written against the schemas of the tested
images and verified on them; see each artifact's sample_data.
"""

__artifacts_v2__ = {
    "get_whatsapp_reactions": {
        "name": "WhatsApp - Message Reactions",
        "description": "WhatsApp emoji reactions to messages (msgstore.db message_add_on_reaction)",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "Each row is one entry in the message_add_on_reaction table joined to its "
                 "message_add_on record and the message it reacted to. In every tested image the "
                 "add-on record's message_add_on_type was 56 for all reaction rows; the value is "
                 "also reported as stored. In tested one-to-one chats the add-on's "
                 "sender_jid_row_id held -1 (55 of 55 rows), so the Sender columns resolve only "
                 "in group chats; in a one-to-one chat the Chat JID column identifies the other "
                 "party and the Direction column identifies which side reacted. "
                 "Source-table map informed by WAInsight (github.com/akhil-dara/WAInsight, MIT).",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*'),
        "output_types": "standard",
        "artifact_icon": "thumbs-up",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 1 row",
            "hc_pixel8pro_a17": "Android 17 | com.whatsapp 2.26.29.73 | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 15 rows",
            "pixel3_a11": "Android 11 | com.whatsapp 2.20.198.15 | 0 rows",
            "pixel3_a12": "Android 12 | com.whatsapp 2.21.20.20 | 0 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 1 row",
            "russell_a14": "Android 14 | com.whatsapp 2.24.16.76 | 17 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 4 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 0 rows",
            "sharon_a13": "Android 13 | com.whatsapp 2.23.12.78 | 470 rows",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 600 rows",
        },
    },
    "get_whatsapp_message_edits": {
        "name": "WhatsApp - Message Edit History",
        "description": "WhatsApp messages recorded as edited (msgstore.db message_edit_info)",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "message_edit_info records the row id of an edited message, the key id the "
                 "message was originally sent under, and edit timestamps. It does not carry the "
                 "pre-edit text, and the message table stores a single text_data value per row, "
                 "so the Message column shows the text as currently stored, not the original. "
                 "Source-table map informed by WAInsight (github.com/akhil-dara/WAInsight, MIT).",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*'),
        "output_types": "standard",
        "artifact_icon": "edit",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | com.whatsapp 2.26.29.73 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 191 rows",
            "pixel3_a11": "Android 11 | com.whatsapp 2.20.198.15 | 0 rows",
            "pixel3_a12": "Android 12 | com.whatsapp 2.21.20.20 | 0 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 0 rows",
            "russell_a14": "Android 14 | com.whatsapp 2.24.16.76 | 11 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 0 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 19 rows",
            "sharon_a13": "Android 13 | com.whatsapp 2.23.12.78 | 12 rows",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 29 rows",
        },
    },
    "get_whatsapp_revoked_messages": {
        "name": "WhatsApp - Revoked Messages",
        "description": "WhatsApp message rows referenced by msgstore.db's message_revoked table",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "Rows in message_revoked joined to the message row they reference. Across all "
                 "tested images (283 rows) text_data on the referenced row was empty, so no "
                 "message body is available here; the surviving fields are the timestamps, "
                 "direction, parties and key id. Observed message_type values were 15 and 64 "
                 "(reported as stored; no lookup table for them exists in the database). Older "
                 "databases in the tested set (Android 11/12 era) lack the revoke_timestamp and "
                 "admin_jid_row_id columns; those columns are reported empty there. "
                 "Source-table map informed by WAInsight (github.com/akhil-dara/WAInsight, MIT).",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*'),
        "output_types": "standard",
        "artifact_icon": "trash-2",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 1 row",
            "hc_pixel8pro_a17": "Android 17 | com.whatsapp 2.26.29.73 | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 204 rows",
            "pixel3_a11": "Android 11 | com.whatsapp 2.20.198.15 | 0 rows",
            "pixel3_a12": "Android 12 | com.whatsapp 2.21.20.20 | 0 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 0 rows",
            "russell_a14": "Android 14 | com.whatsapp 2.24.16.76 | 53 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 0 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 6 rows",
            "sharon_a13": "Android 13 | com.whatsapp 2.23.12.78 | 8 rows",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 10 rows",
        },
    },
    "get_whatsapp_polls": {
        "name": "WhatsApp - Polls",
        "description": "WhatsApp poll questions and options with stored vote totals (msgstore.db)",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "One row per poll option, joined to the poll's message row; the question is the "
                 "message row's text_data. Vote Total is the integer stored in "
                 "message_poll_option.vote_total, as stored. The per-voter tables "
                 "(message_add_on_poll_vote and its options table) were present but empty in "
                 "every tested image, so per-voter votes are not parsed; a corpus exercising "
                 "them would allow that to be added. "
                 "Source-table map informed by WAInsight (github.com/akhil-dara/WAInsight, MIT).",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*'),
        "output_types": "standard",
        "artifact_icon": "chart-bar",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | com.whatsapp 2.26.29.73 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 827 rows",
            "pixel3_a11": "Android 11 | com.whatsapp 2.20.198.15 | 0 rows",
            "pixel3_a12": "Android 12 | com.whatsapp 2.21.20.20 | 0 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 0 rows",
            "russell_a14": "Android 14 | com.whatsapp 2.24.16.76 | 64 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 0 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 4 rows",
            "sharon_a13": "Android 13 | com.whatsapp 2.23.12.78 | 0 rows",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 0 rows",
        },
    },
    "get_whatsapp_message_receipts": {
        "name": "WhatsApp - Message Receipts Per Recipient",
        "description": "WhatsApp per-recipient delivery, read and played receipts (msgstore.db receipt_user)",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "One row per recipient per message from the receipt_user table. The three "
                 "timestamp columns carry the table's own column names (receipt_timestamp, "
                 "read_timestamp, played_timestamp); the database does not document their exact "
                 "semantics and this artifact does not assert them. Receipt rows whose message "
                 "row no longer exists are kept, with the message fields empty (112 of 206 rows "
                 "on one tested image). "
                 "Source-table map informed by WAInsight (github.com/akhil-dara/WAInsight, MIT).",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*'),
        "output_types": "standard",
        "artifact_icon": "user-check",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 14 rows",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 4 rows",
            "hc_pixel8pro_a17": "Android 17 | com.whatsapp 2.26.29.73 | 4 rows",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 77 rows",
            "pixel3_a11": "Android 11 | com.whatsapp 2.20.198.15 | 5 rows",
            "pixel3_a12": "Android 12 | com.whatsapp 2.21.20.20 | 13 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 11 rows",
            "russell_a14": "Android 14 | com.whatsapp 2.24.16.76 | 158 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 33 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 0 rows",
            "sharon_a13": "Android 13 | com.whatsapp 2.23.12.78 | 156 rows",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 206 rows",
        },
    },
    "get_whatsapp_system_events": {
        "name": "WhatsApp - System Events",
        "description": "WhatsApp system messages: group and chat state changes (msgstore.db message_system)",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-14",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "Rows in message_system joined to the message row and to the companion tables "
                 "that hold decoded details where present: affected participants "
                 "(message_system_chat_participant), old and new number "
                 "(message_system_number_change), and prior value "
                 "(message_system_value_change.old_data). action_type is an integer with no "
                 "lookup table in the database and is reported as stored. "
                 "Source-table map informed by WAInsight (github.com/akhil-dara/WAInsight, MIT).",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/wa.db*'),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 10 rows",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 41 rows",
            "hc_pixel8pro_a17": "Android 17 | com.whatsapp 2.26.29.73 | 41 rows",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 28 rows",
            "pixel3_a11": "Android 11 | com.whatsapp 2.20.198.15 | 0 rows",
            "pixel3_a12": "Android 12 | com.whatsapp 2.21.20.20 | 0 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 165 rows",
            "russell_a14": "Android 14 | com.whatsapp 2.24.16.76 | 194 rows",
            "russell_pixel6a_a13": "Android 13 | com.whatsapp vc 231278007 | 1 row",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 12 rows",
            "sharon_a13": "Android 13 | com.whatsapp 2.23.12.78 | 504 rows",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 773 rows",
        },
    },
}

import sqlite3

from scripts.ilapfuncs import (artifact_processor, attach_sqlite_db_readonly,
                               convert_unix_ts_to_utc, null_absent_columns,
                               open_sqlite_db_readonly)

_DIRECTION_CASE = "CASE m.from_me WHEN 1 THEN 'Outgoing' WHEN 0 THEN 'Incoming' END"


def _find(files_found, suffix):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith(('-wal', '-shm', '-journal')):
            continue
        if file_found.endswith(suffix):
            return file_found
    return ''


def _open_msgstore(files_found):
    """Open msgstore.db read-only, attaching wa.db as wadb when present.

    Returns (db, cursor, msgstore_path, wa_attached).
    """
    msg = _find(files_found, 'msgstore.db')
    if not msg:
        return None, None, '', False
    db = open_sqlite_db_readonly(msg)
    if not db:
        return None, None, '', False
    cursor = db.cursor()
    wa_attached = False
    wa = _find(files_found, 'wa.db')
    if wa:
        try:
            cursor.execute(attach_sqlite_db_readonly(wa, 'wadb'))
            wa_attached = True
        except sqlite3.Error:
            pass
    return db, cursor, msg, wa_attached


def _table_exists(cursor, name):
    try:
        cursor.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,))
        return cursor.fetchone() is not None
    except sqlite3.Error:
        return False


def _name_join(wa_attached, jid_alias, out_alias):
    """LEFT JOIN wa.db's contact names onto a jid alias, or a NULL column."""
    if wa_attached:
        return (f'LEFT JOIN wadb.wa_contacts {out_alias} '
                f'ON {out_alias}.jid = {jid_alias}.raw_string',
                f'{out_alias}.wa_name')
    return '', 'NULL'


def _run(cursor, msg_path, sql):
    """Run a query with absent-column tolerance; missing tables return []."""
    sql = null_absent_columns(msg_path, sql)
    try:
        cursor.execute(sql)
        return cursor.fetchall()
    except sqlite3.Error:
        return []


def _ts(value):
    if not value:
        return ''
    return convert_unix_ts_to_utc(value)


@artifact_processor
def get_whatsapp_reactions(context):
    files_found = context.get_files_found()
    db, cursor, source, wa_attached = _open_msgstore(files_found)
    data_list = []
    if db:
        if _table_exists(cursor, 'message_add_on_reaction'):
            join, name_col = _name_join(wa_attached, 'sj', 'wc')
            rows = _run(cursor, source, f'''
            SELECT mao.timestamp, r.sender_timestamp, r.reaction,
                   CASE mao.from_me WHEN 1 THEN 'Outgoing' WHEN 0 THEN 'Incoming' END,
                   sj.raw_string, {name_col},
                   cj.raw_string, ch.subject,
                   pm.text_data, pm.message_type, mao.message_add_on_type, mao.key_id
            FROM message_add_on_reaction r
            JOIN message_add_on mao ON mao._id = r.message_add_on_row_id
            LEFT JOIN message pm ON pm._id = mao.parent_message_row_id
            LEFT JOIN jid sj ON sj._id = mao.sender_jid_row_id
            {join}
            LEFT JOIN chat ch ON ch._id = mao.chat_row_id
            LEFT JOIN jid cj ON cj._id = ch.jid_row_id
            ORDER BY mao.timestamp
            ''')
            for row in rows:
                data_list.append((_ts(row[0]), _ts(row[1]), row[2], row[3], row[4],
                                  row[5], row[6], row[7], row[8], row[9], row[10],
                                  row[11]))
        db.close()

    data_headers = (('Reaction Timestamp', 'datetime'), ('Sender Timestamp', 'datetime'),
                    'Reaction', 'Direction', 'Sender JID', 'Sender WA Name', 'Chat JID',
                    'Chat Name', 'Reacted-To Message', 'Reacted-To Message Type (as stored)',
                    'Add-On Type (as stored)', 'Key ID')
    return data_headers, data_list, source


@artifact_processor
def get_whatsapp_message_edits(context):
    files_found = context.get_files_found()
    db, cursor, source, wa_attached = _open_msgstore(files_found)
    data_list = []
    if db:
        if _table_exists(cursor, 'message_edit_info'):
            join, name_col = _name_join(wa_attached, 'sj', 'wc')
            rows = _run(cursor, source, f'''
            SELECT e.edited_timestamp, e.sender_timestamp, m.timestamp, m.text_data,
                   {_DIRECTION_CASE},
                   sj.raw_string, {name_col},
                   cj.raw_string, ch.subject, e.original_key_id, m.key_id
            FROM message_edit_info e
            JOIN message m ON m._id = e.message_row_id
            LEFT JOIN jid sj ON sj._id = m.sender_jid_row_id
            {join}
            LEFT JOIN chat ch ON ch._id = m.chat_row_id
            LEFT JOIN jid cj ON cj._id = ch.jid_row_id
            ORDER BY e.edited_timestamp
            ''')
            for row in rows:
                data_list.append((_ts(row[0]), _ts(row[1]), _ts(row[2]), row[3], row[4],
                                  row[5], row[6], row[7], row[8], row[9], row[10]))
        db.close()

    data_headers = (('Last Edit Timestamp', 'datetime'), ('Sender Timestamp', 'datetime'),
                    ('Message Timestamp', 'datetime'), 'Message (as currently stored)',
                    'Direction', 'Sender JID', 'Sender WA Name', 'Chat JID', 'Chat Name',
                    'Original Key ID', 'Current Key ID')
    return data_headers, data_list, source


@artifact_processor
def get_whatsapp_revoked_messages(context):
    files_found = context.get_files_found()
    db, cursor, source, wa_attached = _open_msgstore(files_found)
    data_list = []
    if db:
        if _table_exists(cursor, 'message_revoked'):
            join, name_col = _name_join(wa_attached, 'sj', 'wc')
            rows = _run(cursor, source, f'''
            SELECT r.revoke_timestamp, m.timestamp, m.received_timestamp,
                   {_DIRECTION_CASE},
                   sj.raw_string, {name_col},
                   aj.raw_string, cj.raw_string, ch.subject,
                   m.message_type, r.revoked_key_id
            FROM message_revoked r
            JOIN message m ON m._id = r.message_row_id
            LEFT JOIN jid sj ON sj._id = m.sender_jid_row_id
            {join}
            LEFT JOIN jid aj ON aj._id = r.admin_jid_row_id
            LEFT JOIN chat ch ON ch._id = m.chat_row_id
            LEFT JOIN jid cj ON cj._id = ch.jid_row_id
            ORDER BY m.timestamp
            ''')
            for row in rows:
                data_list.append((_ts(row[0]), _ts(row[1]), _ts(row[2]), row[3], row[4],
                                  row[5], row[6], row[7], row[8], row[9], row[10]))
        db.close()

    data_headers = (('Revoke Timestamp', 'datetime'), ('Message Timestamp', 'datetime'),
                    ('Received Timestamp', 'datetime'), 'Direction', 'Sender JID',
                    'Sender WA Name', 'Admin JID', 'Chat JID', 'Chat Name',
                    'Message Type (as stored)', 'Revoked Key ID')
    return data_headers, data_list, source


@artifact_processor
def get_whatsapp_polls(context):
    files_found = context.get_files_found()
    db, cursor, source, wa_attached = _open_msgstore(files_found)
    data_list = []
    if db:
        if _table_exists(cursor, 'message_poll'):
            join, name_col = _name_join(wa_attached, 'sj', 'wc')
            rows = _run(cursor, source, f'''
            SELECT m.timestamp, m.text_data, o.option_name, o.vote_total,
                   p.selectable_options_count,
                   {_DIRECTION_CASE},
                   sj.raw_string, {name_col},
                   cj.raw_string, ch.subject, m.key_id
            FROM message_poll p
            JOIN message m ON m._id = p.message_row_id
            LEFT JOIN message_poll_option o ON o.message_row_id = p.message_row_id
            LEFT JOIN jid sj ON sj._id = m.sender_jid_row_id
            {join}
            LEFT JOIN chat ch ON ch._id = m.chat_row_id
            LEFT JOIN jid cj ON cj._id = ch.jid_row_id
            ORDER BY m.timestamp, o._id
            ''')
            for row in rows:
                data_list.append((_ts(row[0]), row[1], row[2], row[3], row[4], row[5],
                                  row[6], row[7], row[8], row[9], row[10]))
        db.close()

    data_headers = (('Poll Timestamp', 'datetime'), 'Question', 'Option',
                    'Vote Total (as stored)', 'Selectable Options Count', 'Direction',
                    'Sender JID', 'Sender WA Name', 'Chat JID', 'Chat Name', 'Key ID')
    return data_headers, data_list, source


@artifact_processor
def get_whatsapp_message_receipts(context):
    files_found = context.get_files_found()
    db, cursor, source, wa_attached = _open_msgstore(files_found)
    data_list = []
    if db:
        if _table_exists(cursor, 'receipt_user'):
            join, name_col = _name_join(wa_attached, 'rj', 'wc')
            rows = _run(cursor, source, f'''
            SELECT r.receipt_timestamp, r.read_timestamp, r.played_timestamp,
                   m.timestamp, rj.raw_string, {name_col},
                   cj.raw_string, ch.subject, m.text_data, m.message_type, m.key_id
            FROM receipt_user r
            LEFT JOIN message m ON m._id = r.message_row_id
            LEFT JOIN jid rj ON rj._id = r.receipt_user_jid_row_id
            {join}
            LEFT JOIN chat ch ON ch._id = m.chat_row_id
            LEFT JOIN jid cj ON cj._id = ch.jid_row_id
            ORDER BY r.receipt_timestamp
            ''')
            for row in rows:
                data_list.append((_ts(row[0]), _ts(row[1]), _ts(row[2]), _ts(row[3]),
                                  row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10]))
        db.close()

    data_headers = (('Receipt Timestamp', 'datetime'), ('Read Timestamp', 'datetime'),
                    ('Played Timestamp', 'datetime'), ('Message Timestamp', 'datetime'),
                    'Recipient JID', 'Recipient WA Name', 'Chat JID', 'Chat Name',
                    'Message', 'Message Type (as stored)', 'Key ID')
    return data_headers, data_list, source


@artifact_processor
def get_whatsapp_system_events(context):
    files_found = context.get_files_found()
    db, cursor, source, _wa_attached = _open_msgstore(files_found)
    data_list = []
    if db:
        if _table_exists(cursor, 'message_system'):
            # Companion tables vary by release; compose each join only when
            # its table exists so one absent table cannot zero the artifact.
            if _table_exists(cursor, 'message_system_chat_participant'):
                participants = ('''(SELECT group_concat(pj.raw_string, ', ')
                      FROM message_system_chat_participant p
                      LEFT JOIN jid pj ON pj._id = p.user_jid_row_id
                     WHERE p.message_row_id = s.message_row_id)''')
            else:
                participants = 'NULL'
            if _table_exists(cursor, 'message_system_number_change'):
                number_cols = 'oj.raw_string, nj.raw_string'
                number_join = ('''
            LEFT JOIN message_system_number_change n ON n.message_row_id = s.message_row_id
            LEFT JOIN jid oj ON oj._id = n.old_jid_row_id
            LEFT JOIN jid nj ON nj._id = n.new_jid_row_id''')
            else:
                number_cols = 'NULL, NULL'
                number_join = ''
            if _table_exists(cursor, 'message_system_value_change'):
                value_col = 'v.old_data'
                value_join = ('\n            LEFT JOIN message_system_value_change v'
                              ' ON v.message_row_id = s.message_row_id')
            else:
                value_col = 'NULL'
                value_join = ''
            if _table_exists(cursor, 'message_system_group'):
                group_col = 'g.is_me_joined'
                group_join = ('\n            LEFT JOIN message_system_group g'
                              ' ON g.message_row_id = s.message_row_id')
            else:
                group_col = 'NULL'
                group_join = ''
            rows = _run(cursor, source, f'''
            SELECT m.timestamp, s.action_type, cj.raw_string, ch.subject, m.text_data,
                   {participants},
                   {number_cols}, {value_col}, {group_col}
            FROM message_system s
            JOIN message m ON m._id = s.message_row_id
            LEFT JOIN chat ch ON ch._id = m.chat_row_id
            LEFT JOIN jid cj ON cj._id = ch.jid_row_id{number_join}{value_join}{group_join}
            ORDER BY m.timestamp
            ''')
            for row in rows:
                data_list.append((_ts(row[0]), row[1], row[2], row[3], row[4], row[5],
                                  row[6], row[7], row[8], row[9]))
        db.close()

    data_headers = (('Event Timestamp', 'datetime'), 'Action Type (as stored)', 'Chat JID',
                    'Chat Name', 'Text', 'Affected Participants', 'Old JID', 'New JID',
                    'Prior Value', 'Is Me Joined (as stored)')
    return data_headers, data_list, source

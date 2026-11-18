__artifacts_v2__ = {
    "snapchat_turn_events": {
        "name": "Snapchat - Conversation Turn Events",
        "description": "Per Snapchat conversation, the message sent, message received, view "
                       "sent and view received events the app's recents ranking kept in "
                       "turn_db, with their times and when the last two turns began. On "
                       "dragna_pixel9a_a16 they name conversations the arroyo.db artifacts do"
                       " not report.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Snapchat",
        "notes": "Read from the Turn and TurnEvent tables of "
                 "com.snapchat.android/files/valdi_cache/sqlite/<account>/turn_db, with its "
                 "write-ahead log when one is beside it. Sources are the app's own script "
                 "modules in the APK installed on dragna_pixel9a_a16 (Snapchat versionCode "
                 "319422; assets/turn_db.valdimodule and assets/recents_ranking.valdimodule, "
                 "zstd-compressed, read after decompression); other app versions were not "
                 "read, and three of the four tested stores were written by other versions. "
                 "turn_db/src/sqlgen/TurnDb holds the schema and TurnQueries the queries; "
                 "recents_ranking/src/TurnEventHandler and TurnRepository write them. That "
                 "version derives at most one event from each committed message of the "
                 "content types it counts (snap, chat, bot_response, "
                 "my_ai_spectacles_bot_response), and does not store every one: a message "
                 "with no read time or no recorded viewer gives MessageSend when the "
                 "signed-in user sent it and MessageReceive otherwise, at the message's "
                 "createdAt; a read message gives ViewReceive when the signed-in user sent it"
                 " and another member viewed it, or ViewSend when the signed-in user viewed "
                 "it, at the message's readAt, and a read message that fits neither case "
                 "gives no event. 'Event Time' is that time (TurnEvent.updatedAt, Unix "
                 "milliseconds, shown in UTC). It is the first event of that type stored in "
                 "the current turn: later events of the same type in the same turn are not "
                 "stored, and each conversation keeps one event per type for its current turn"
                 " (UNIQUE(type, turnId)). When a new event type ends the current turn under "
                 "the module's rules (for example a MessageReceive after a MessageSend), or "
                 "when the conversation has no events yet, the app stores the event's time as"
                 " 'Turn Began' (Turn.lastUpdatedAt), keeps the earlier one as 'Previous Turn"
                 " Began' (secondToLastUpdatedAt) when it is earlier than the new event, and "
                 "starts the turn's events again; otherwise it adds the event to the current "
                 "turn only if the turn holds no event of that type, whatever its time, so an"
                 " event can be earlier than 'Turn Began' (1 row each on dragna_pixel9a_a16 "
                 "and samsungs20_a13). 'Previous Turn Began' is blank in stores whose Turn "
                 "table predates that column (hc_pixel8pro_a16 and samsungs20_a13), and where"
                 " the column is empty (every row of hc_pixel8pro_a17, 40 of 44 on "
                 "dragna_pixel9a_a16): the app leaves it empty when there is no earlier turn "
                 "or when the earlier turn's time is not earlier than the new event. "
                 "'Conversation ID' is the Snapchat conversation id, the same id the Snapchat"
                 " - Conversations (arroyo.db) artifact shows. 'Account' is the name of the "
                 "folder that holds the store; on dragna_pixel9a_a16 it equals the sender id "
                 "of the outgoing messages in Snapchat - Messages (arroyo.db), and it held "
                 "one value on every row of each image. The tables name no sender or text. On"
                 " dragna_pixel9a_a16 the 44 events name 43 conversations, 35 of which are "
                 "not among the conversations Snapchat - Conversations (arroyo.db) reports, "
                 "live or recovered. The 35 MessageReceive events in those conversations "
                 "match no message in Snapchat - Messages (arroyo.db); the other 5 each match"
                 " a reported message of the same conversation within 1 second of its "
                 "creation time. On that image the turn events record a received message in "
                 "35 conversations for which those two artifacts report nothing; why "
                 "arroyo.db holds no rows for them was not established.",
        "paths": ('*/com.snapchat.android/files/valdi_cache/sqlite/*/turn_db*',),
        "output_types": "standard",
        "artifact_icon": "repeat",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | com.snapchat.android versionCode 319422 | 44 rows",
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android | 3 rows",
            "hc_pixel8pro_a17": "Android 17 | com.snapchat.android | 13 rows",
            "samsungs20_a13": "Android 13 | com.snapchat.android | 5 rows",
        },
    },
}

import os
import re
from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records

_ACCOUNT = re.compile(r'/valdi_cache/sqlite/([^/]+)/turn_db$')
# secondToLastUpdatedAt is added by a later schema step (ALTER TABLE in the app's turn_db
# module), so older stores lack it.
_QUERY = '''
    SELECT TurnEvent.updatedAt, TurnEvent.type, Turn.conversationId, Turn.lastUpdatedAt,
           {previous}
    FROM TurnEvent JOIN Turn ON Turn._id = TurnEvent.turnId
    ORDER BY TurnEvent.updatedAt DESC
'''


def _utc_ms(value):
    if not isinstance(value, int) or value <= 0:
        return ''
    try:
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


@artifact_processor
def snapchat_turn_events(context):
    data_headers = (
        ('Event Time', 'datetime'), ('Turn Began', 'datetime'),
        ('Previous Turn Began', 'datetime'), 'Event Type', 'Conversation ID', 'Account')
    data_list, sources = [], []
    for file_found in unique_files(context):
        path = str(file_found)
        if os.path.basename(path) != 'turn_db':
            continue
        sources.append(path)
        match = _ACCOUNT.search(str(context.get_relative_path(path)).replace('\\', '/'))
        account = match.group(1) if match else ''
        columns = {row[1] for row in get_sqlite_db_records(path, 'PRAGMA table_info(Turn)')}
        previous_column = ('Turn.secondToLastUpdatedAt' if 'secondToLastUpdatedAt' in columns
                           else 'NULL')
        query = _QUERY.format(previous=previous_column)
        for updated, kind, conversation, last, previous in get_sqlite_db_records(path, query):
            data_list.append((
                _utc_ms(updated), _utc_ms(last), _utc_ms(previous), kind or '',
                conversation or '', account,
            ))
    return data_headers, data_list, '\n'.join(sources)

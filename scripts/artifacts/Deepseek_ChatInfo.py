from datetime import datetime, timezone

from scripts.ilapfuncs import (
    artifact_processor,
    open_sqlite_db_readonly
)

__artifacts_v2__ = {
    "deepseek_chat_info": {
        "name": "Deepseek Chat Info",
        "description": "Deepseek chat sessions from the chat_session_list table, with each session's updated_at value",
        "author": "RicardoBentoSantos, @AlexisBrignoni, Codex",
        "creation_date": "2026-05-24",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "DeepSeek",
        "notes": (
            "Timestamp is updated_at read as Unix seconds and shown in UTC. The unit and what "
            "updated_at marks are this parser's reading and have not been checked against a source or data: no "
            "registered corpus holds this database (20 zip listings and 24 tar indexes checked "
            "on 2026-10-04). The updated_at (as stored) column shows the value the database "
            "holds, unchanged. Timestamp is blank when updated_at is empty, zero, or cannot be "
            "read as Unix seconds."
        ),
        "paths": ('*/data/com.deepseek.chat/databases/deepseek_chat_*.db*'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "message-circle"
    }
}


@artifact_processor
def deepseek_chat_info(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = ""

    query = """
    SELECT
        id,
        title,
        updated_at
    FROM
        chat_session_list
    """

    data_headers = (
        ('Timestamp', 'datetime'),
        'Chat ID',
        'Title',
        'updated_at (as stored)'
    )

    for source_path in files_found:

        db = open_sqlite_db_readonly(source_path)

        if db is None:
            continue

        try:

            cursor = db.cursor()
            cursor.execute(query)

            all_rows = cursor.fetchall()

            for row in all_rows:

                chat_id, title, updated_at = row

                lava_timestamp = None
                updated_at_stored = '' if updated_at is None else str(updated_at)

                if updated_at:

                    try:

                        ts = float(updated_at)

                        datetime.fromtimestamp(ts, tz=timezone.utc)

                        lava_timestamp = ts

                    except Exception:  # pylint: disable=broad-exception-caught

                        lava_timestamp = None

                data_list.append((
                    lava_timestamp,
                    chat_id,
                    title,
                    updated_at_stored
                ))

        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error processing {source_path}: {e}")

        finally:
            db.close()

    return data_headers, data_list, source_path
from datetime import datetime, timezone

from scripts.ilapfuncs import (
    artifact_processor,
    open_sqlite_db_readonly
)

__artifacts_v2__ = {
    "deepseek_chat_info": {
        "name": "Deepseek Chat Info",
        "description": "List of Deepseek chat sessions and last updated timestamps",
        "author": "RicardoBentoSantos",
        "creation_date": "2026-05-24",
        "last_update_date": "2026-05-24",
        "requirements": "none",
        "category": "DeepSeek",
        "notes": "",
        "paths": ('*/data/com.deepseek.chat/databases/deepseek_chat_*.db'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "message-circle"
    }
}


@artifact_processor
def deepseek_chat_info(files_found, report_folder, seeker, wrap_text):

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
        'Last Updated (UTC)'
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
                updated_at_utc = ""

                if updated_at:

                    try:

                        ts = float(updated_at)

                        lava_timestamp = ts

                        updated_at_utc = datetime.fromtimestamp(
                            ts,
                            tz=timezone.utc
                        ).strftime('%Y-%m-%d %H:%M:%S')

                    except Exception:

                        updated_at_utc = str(updated_at)

                data_list.append((
                    lava_timestamp,
                    chat_id,
                    title,
                    updated_at_utc
                ))

        except Exception as e:
            print(f"Error processing {source_path}: {e}")

        finally:
            db.close()

    return data_headers, data_list, source_path
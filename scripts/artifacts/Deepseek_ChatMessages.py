import json
import math
#import markdown

from datetime import datetime, timezone

from scripts.ilapfuncs import (
    artifact_processor,
    open_sqlite_db_readonly
)

__artifacts_v2__ = {
    "deepseek_chat_messages": {
        "name": "Deepseek Chat Messages",
        "description": "Deepseek chat messages from the chat_session_messages tables: role, inserted_at (read as Unix seconds) and the text of the REQUEST and RESPONSE fragments. Other fragment types are left out. When the fragments value cannot be parsed, the whole value is reported as stored.",
        "author": "RicardoBentoSantos",
        "creation_date": "2026-05-24",
        "last_update_date": "2026-11-22",
        "requirements": "",
        "category": "DeepSeek",
        "notes": "inserted_at is read as Unix seconds. The unit was not checked against the app's code or a real database. A value that cannot be converted is shown as stored.",
        "paths": ('*/data/com.deepseek.chat/databases/deepseek_chat_*.db*'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "message",
        "multiline_columns": ["Message Content"]
    }
}


def _sort_time(value):
    """A sort key for inserted_at. A value that is not a finite number sorts first."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0
    return number if math.isfinite(number) else 0


def extract_content_from_fragments(fragments):

    if not fragments:
        return ""

    try:

        data = json.loads(fragments)

        contents = []

        for item in data:

            if item.get("type") in ["REQUEST", "RESPONSE"]:
                contents.append(item.get("content", ""))

        full_text = "\n\n".join(contents)
        
        #HTML conversion removed because LAVA will support markdown.
        #HTML escape not allowed do to possible avenue for injection attacks
        # '''' 
        # full_text = html.unescape(full_text)

        # rendered_html = markdown.markdown(
            # full_text,
            # extensions=[
                # "extra",
                # "nl2br",
                # "sane_lists"
            # ]
        # )
        # '''

        return full_text

    except Exception:  # pylint: disable=broad-exception-caught
        return (str(fragments))


@artifact_processor
def deepseek_chat_messages(context):
    files_found = context.get_files_found()

    data_headers = (
        ('Timestamp', 'datetime'),
        'Chat Table',
        'Inserted At (UTC)',
        'Role',
        'Message Content'
    )

    data_list = []

    source_path = ""

    for source_path in files_found:

        db = open_sqlite_db_readonly(source_path)

        if db is None:
            continue

        try:

            cursor = db.cursor()

            cursor.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                AND name LIKE 'chat_session_messages_%'
            """)

            tables = cursor.fetchall()

            if not tables:
                continue

            for (table_name,) in tables:

                try:

                    cursor.execute(f'''
                        SELECT
                            role,
                            inserted_at,
                            fragments
                        FROM "{table_name}"
                    ''')

                    rows = cursor.fetchall()

                    if not rows:
                        continue

                    rows = sorted(
                        rows,
                        key=lambda x: _sort_time(x[1])
                    )

                    for role, inserted_at, fragments in rows:

                        lava_timestamp = None
                        inserted_at_utc = ""

                        if inserted_at:

                            try:

                                ts = float(inserted_at)

                                inserted_at_utc = datetime.fromtimestamp(
                                    ts,
                                    tz=timezone.utc
                                ).strftime('%Y-%m-%d %H:%M:%S')

                                lava_timestamp = ts

                            except Exception:  # pylint: disable=broad-exception-caught

                                inserted_at_utc = str(inserted_at)

                        content = extract_content_from_fragments(
                            fragments
                        )
                        
                        # '''
                        # chat_html = f
                        # <div class="chat-message">
                            # <div class="chat-content">
                                # {content}
                            # </div>
                        # </div>
                        # '''

                        data_list.append((
                            lava_timestamp,
                            table_name,
                            inserted_at_utc,
                            role,
                            content
                        ))

                except Exception as e:  # pylint: disable=broad-exception-caught
                    print(f"Error processing table {table_name}: {e}")

        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error processing database {source_path}: {e}")

        finally:
            db.close()

    return data_headers, data_list, source_path
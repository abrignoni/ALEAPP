from scripts.ilapfuncs import (
    artifact_processor,
    open_sqlite_db_readonly
)

__artifacts_v2__ = {
    "deepseek_user_info": {
        "name": "Deepseek User Info",
        "description": "Deepseek account information including token, email and phone number",
        "author": "RicardoBentoSantos",
        "creation_date": "2026-05-24",
        "last_update_date": "2026-05-24",
        "requirements": "none",
        "category": "DeepSeek",
        "notes": "",
        "paths": ('*/data/com.deepseek.chat/databases/deepseek_chat.db'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "user"
    }
}


@artifact_processor
def deepseek_user_info(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = ""

    query = """
    SELECT
        id,
        token,
        email,
        mobile_number
    FROM
        app_user_info
    """

    data_headers = ('User ID', 'Token', 'Email', 'Mobile Number')

    for source_path in files_found:

        db = open_sqlite_db_readonly(source_path)

        if db is None:
            continue

        try:
            cursor = db.cursor()
            cursor.execute(query)

            all_rows = cursor.fetchall()

            for row in all_rows:

                user_id, token, email, mobile_number = row

                if not mobile_number or str(mobile_number).strip() == "":
                    mobile_number = "Not Found"

                data_list.append((
                    user_id,
                    token,
                    email,
                    mobile_number
                ))

        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error processing {source_path}: {e}")

        finally:
            db.close()

    return data_headers, data_list, source_path
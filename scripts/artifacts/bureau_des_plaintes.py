__artifacts_v2__ = {
    "bureauDesPlaintes": {
        "name": "Bureau_des_Plaintes",
        "description": "Parses complaint records stored in the Bureau des Plaintes database.",
        "author": "@ThibaultCart",
        "creation_date": "2026-11-12",
        "last_update_date": "2026-11-12",
        "requirements": "none",
        "category": "Bureau des Plaintes",
        "paths": (
            "*/com.scotch.singlecelie30ansdage/databases/BureauDesPlaintes*",
        ),
        "output_types": "standard",
        "artifact_icon": "report",
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, convert_unix_ts_to_utc


@artifact_processor
def bureauDesPlaintes(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "BureauDesPlaintes")

    query = """
        SELECT
            p.id,
            p.plainte,
            o.outil,
            p.horodatage
        FROM Plaintes p
        LEFT JOIN Outils o ON o.id = p.outil_id
    """

    data_list = []
    db_records = get_sqlite_db_records(source_path, query)
    for record in db_records:
        data_list.append((
            record[0],
            record[1],
            record[2],
            convert_unix_ts_to_utc(record[3]),
        ))

    data_headers = (
        "Complaint ID",
        "Complaint",
        "Tool",
        ("Date", "datetime"),
    )
    return data_headers, data_list, source_path

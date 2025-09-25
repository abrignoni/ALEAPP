__artifacts_v2__ = {
    "swissmeteo_plz": {
        "name": "Swissmeteo",
        "description": "parse the interaction with meteo of particular places",
        "author": "jerome.arn@vd.ch",
        "creation_date": "2025-09-25",
        "last_update_date": "2025-09-25",
        "requirements": "none",
        "category": "Meteo",
        "notes": "",
        "paths": ('*/data/ch.admin.meteoswiss/databases/favorites_prediction_db.sqlite', '*data/ch.admin.meteoswiss/files/db/localdata.sqlite'),
        "output_types": "standard",
        "artifact_icon": "flag"
    }
}


from scripts.ilapfuncs import artifact_processor, get_file_path, \
    get_sqlite_db_records, logfunc, tsv, timeline, open_sqlite_db_readonly
from scripts.artifact_report import ArtifactHtmlReport

@artifact_processor
def swissmeteo_plz(files_found, report_folder, seeker, wrap_text):
    source_path = get_file_path(files_found, "favorites_prediction_db.sqlite")
    data_list = []

    for file_found in files_found:
        file_found = str(file_found)

    if files_found[0].endswith('favorites_prediction_db.sqlite'):
        query = '''
        SELECT 
            datetime(timestamp/1000, 'unixepoch', 'localtime') AS created_date,
            plz
        FROM plz_interaction
        ORDER BY created_date DESC
        '''

        data_headers = ('Consulted timestamp', 'Post code', "Location name", "Altitude", "Map link")
        db_records = get_sqlite_db_records(files_found[0], query)

        local_data = []
        if files_found[1].endswith('localdata.sqlite'):
            db = open_sqlite_db_readonly(files_found[1])
            cursor = db.cursor()

        for record in db_records:
            local_data = get_location_infos(cursor, record[1])
            if len(local_data) > 0:
                print(local_data[0])
                link = lv03_to_osm(local_data[0][1], local_data[0][2])
                data_list.append((record[0], record[1][:4], local_data[0][4], local_data[0][3], link))
            else:
                data_list.append(record + ('', '', ''))

        return data_headers, data_list, source_path

    else:
        logfunc('No Swissmeteo')

def lv03_to_osm(E, N): 
    x, y = (E-600000)/1e6, (N-200000)/1e6; 
    lat = 16.9023892+3.238272*y-0.270978*x**2-0.002528*y**2-0.0447*x**2*y-0.0140*y**3; 
    lon = 2.6779094+4.728982*x+0.791484*x*y+0.1306*x*y**2-0.0436*x**3; 
    lat, lon = lat*100/36, lon*100/36; 
    return f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}&zoom=18"

def get_location_infos(cursor, NPA):
    query = '''
    SELECT 
        plz_pk,
        x,
        y,
        altitude,
        primary_name
    FROM plz
    WHERE plz_pk = ?
    '''

    cursor.execute(query, (NPA,))
    local_data = cursor.fetchall()
    return local_data
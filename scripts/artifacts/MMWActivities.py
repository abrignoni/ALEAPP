# Get Information related to the activities of the user from the Map My Walk app
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-03-25
# Version: 1.0
# Requirements: Python 3.7 or higher, folium
import datetime
import json
import os
import sqlite3

import folium
import xlsxwriter

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, get_raw_fields, check_raw_fields, check_internet_connection


def get_map_activities(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Map My Walk Activities")
    use_network = check_internet_connection()
    if use_network:
        conn = sqlite3.connect('coordinates.db')
        c = conn.cursor()
        c.execute(
            '''CREATE TABLE IF NOT EXISTS raw_fields (id INTEGER PRIMARY KEY AUTOINCREMENT, stored_time TIMESTAMP DATETIME DEFAULT 
            CURRENT_TIMESTAMP, latitude text, longitude text, road text, city text, postcode text, country text)''')
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)

    # Get information from the table device_sync_audit
    cursor = db.cursor()
    cursor.execute('''
        Select localId
        from timeSeries
        group by localId
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries} entries in timeSeries table")
        report = ArtifactHtmlReport('Activities')
        report.start_artifact_report(report_folder, 'Map-My-Walk Activities')
        report.add_script()
        data_headers = ('ID', 'Start Time', 'End Time', 'Distance(KM)', 'Speed', 'Duration(m)', 'Coordinates KML', 'Coordinates Excel', 'Button')
        data_list = []
        activity_date = ''
        activity_json = []
        html_map = []
        for row in all_rows:
            id = row[0]
            coordinates = []
            coordinatesE = []
            speed = []
            i = 0
            cursor.execute(f'''
                            Select timestamp, distance, speed, latitude, longitude, timeOffset
                            from timeSeries
                            where localId = '{id}'
                        ''')
            positions = cursor.fetchall()
            usageentries_p = len(positions)
            if usageentries_p > 0:
                for row_p in positions:
                    if row_p[0]:
                        if i == 0:
                            startTime = datetime.datetime.utcfromtimestamp(row_p[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                            startOffset = row_p[5]
                        # last point
                        if i == usageentries_p - 1:
                            endTime = datetime.datetime.utcfromtimestamp(row_p[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                            endOffset = row_p[5]
                        time_now = datetime.datetime.utcfromtimestamp(row_p[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                        i += 1
                    if row_p[1]:
                        distance = row_p[1]
                    if row_p[2]:
                        speed.append(row_p[2])
                    if row_p[3] and row_p[4]:
                        coordinates.append((row_p[3], row_p[4]))
                        coordinatesE.append([row_p[3], row_p[4], time_now])
                # mean speed
                if len(speed) > 0:
                    speed = sum(speed) / len(speed)
                    speed = round(speed, 2)
                time = endOffset - startOffset
                # convert ms to min
                time = time / 60000
                time = round(time, 2)
                # convert m to km
                distance = distance / 1000
                distance = round(distance, 2)
                place_lat = []
                place_lon = []

                m = folium.Map(location=[coordinates[0][0], coordinates[0][1]], zoom_start=10, max_zoom=19)

                for coordinate in coordinates:
                    # if points are to close, skip
                    if len(place_lat) > 0 and abs(place_lat[-1] - coordinate[0]) < 0.0001 and abs(
                            place_lon[-1] - coordinate[1]) < 0.0001:
                        continue
                    else:
                        place_lat.append(coordinate[0])
                        place_lon.append(coordinate[1])

                points = []
                for i in range(len(place_lat)):
                    points.append([place_lat[i], place_lon[i]])

                # Add points to map
                for index, lat in enumerate(place_lat):
                    # Start point
                    if index == 0:
                        folium.Marker([lat, place_lon[index]],
                                      popup=(('Start Location\nActivity ID \n' + str(row[0])).format(index)),
                                      icon=folium.Icon(color='blue', icon='flag', prefix='fa')).add_to(m)
                    # last point
                    elif index == len(place_lat) - 1:
                        folium.Marker([lat, place_lon[index]],
                                      popup=(('End Location\nActivity ID \n' + str(row[0])).format(index)),
                                      icon=folium.Icon(color='red', icon='flag', prefix='fa')).add_to(m)
                    # middle points

                if use_network:
                    # Create an excel file with the coordinates
                    if os.name == 'nt':
                        f = open(report_folder + "\\" + str(row[0]) + ".xlsx", "w")
                        workbook = xlsxwriter.Workbook(report_folder + "\\" + str(row[0]) + ".xlsx")
                    else:
                        f = open(report_folder + "/" + str(row[0]) + ".xlsx", "w")
                        workbook = xlsxwriter.Workbook(report_folder + "/" + str(row[0]) + ".xlsx")
                    worksheet = workbook.add_worksheet()
                    rowE = 0
                    col = 0
                    worksheet.write(rowE, col, "Timestamp")
                    worksheet.write(rowE, col + 1, "Latitude")
                    worksheet.write(rowE, col + 2, "Longitude")
                    worksheet.write(rowE, col + 3, "Road")
                    worksheet.write(rowE, col + 4, "City")
                    worksheet.write(rowE, col + 5, "Postcode")
                    worksheet.write(rowE, col + 6, "Country")
                    rowE += 1

                    for coordinate in coordinatesE:
                        # coordinate = str(coordinate)
                        # round to 5 decimal cases
                        lat = round(coordinate[0], 3)
                        lon = round(coordinate[1], 3)
                        worksheet.write(rowE, col, coordinate[2])
                        worksheet.write(rowE, col + 1, lat)
                        worksheet.write(rowE, col + 2, lon)
                        location = check_raw_fields(lat, lon, c)
                        if location is None:
                            logfunc('Getting coordinates data from API might take some time')
                            location = get_raw_fields(lat, lon, c, conn)
                            for key, value in location.items():
                                if key == "road":
                                    worksheet.write(rowE, col + 3, value)
                                elif key == "city":
                                    worksheet.write(rowE, col + 4, value)
                                elif key == "postcode":
                                    worksheet.write(rowE, col + 5, value)
                                elif key == "country":
                                    worksheet.write(rowE, col + 6, value)
                        else:
                            logfunc('Getting coordinate data from database')
                            worksheet.write(rowE, col + 3, location[4])
                            worksheet.write(rowE, col + 4, location[5])
                            worksheet.write(rowE, col + 5, location[6])
                            worksheet.write(rowE, col + 6, location[7])
                        rowE += 1
                    workbook.close()
                # Create polyline
                folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(m)
                # Save the map to an HTML file
                title = 'Map-My-Walk_Polyline_Map_' + str(id)
                if os.name == 'nt':
                    m.save(report_folder + '\\' + title + '.html')
                else:
                    m.save(report_folder + '/' + title + '.html')
                html_map.append('<iframe id="' + str(
                    id) + '" src="Map-My-Walk/' + title + '.html" width="100%" height="500" class="map" hidden></iframe>')
                # save coords to a kml file
                kml = """
                                                    <?xml version="1.0" encoding="UTF-8"?>
                                                    <kml xmlns="http://www.opengis.net/kml/2.2">
                                                    <Document>
                                                    <name>Coordinates</name>
                                                    <description>Coordinates</description>
                                                    <Style id="yellowLineGreenPoly">
                                                        <LineStyle>
                                                            <color>7f00ffff</color>
                                                            <width>4</width>
                                                        </LineStyle>
                                                        <PolyStyle>
                                                            <color>7f00ff00</color>
                                                        </PolyStyle>
                                                    </Style>
                                                    <Placemark>
                                                        <name>Absolute Extruded</name>
                                                        <description>Transparent green wall with yellow outlines</description>
                                                        <styleUrl>#yellowLineGreenPoly</styleUrl>
                                                        <LineString>
                                                            <extrude>1</extrude>
                                                            <tessellate>1</tessellate>
                                                            <altitudeMode>clampedToGround</altitudeMode>
                                                            <coordinates>
                                                            """
                for i in range(len(place_lat)):
                    kml += str(place_lon[i]) + ',' + str(place_lat[i]) + ',0 '
                kml = kml[:-1]
                kml += """
                                                            </coordinates>
                                                        </LineString>
                                                    </Placemark>
                                                    </Document>
                                                    </kml>
                                                    """
                # remove the first space
                kml = kml[1:]
                # remove last line
                kml = kml[:-1]
                # remove extra indentation
                kml = kml.replace("    ", "")
                if os.name == 'nt':
                    with open(report_folder + '\\' + str(row[0]) + '.kml', 'w') as f:
                        f.write(kml)
                        f.close()
                else:
                    with open(report_folder + '/' + str(row[0]) + '.kml', 'w') as f:
                        f.write(kml)
                        f.close()
                map = True
            # extract date from startTimeGMT
            current_date = startTime.split(' ')[0]
            if current_date != activity_date:
                activity_json.append({
                    'date': current_date,
                    'total': 1,
                })
                activity_date = current_date
            else:
                # Change the total of the last element of the list
                activity_json[-1]['total'] += 1

            if use_network:
                data_list.append((row[0], startTime, endTime, distance, speed, time, '<a href=Map-My-Walk/'+str(row[0])+'.kml class="badge badge-light" target="_blank">'+str(row[0])+'.kml</a>', '<a href=Map-My-Walk/'+str(row[0])+'.xlsx class="badge badge-light" target="_blank">'+str(row[0])+'.xlsx</a>', '<button type="button" class="btn btn-light btn-sm" onclick="openMap(\''+str(id)+'\')">Show Map</button>'))
            else:
                data_list.append((row[0], startTime, endTime, distance, speed, time, '<a href=Map-My-Walk/'+str(row[0])+'.kml class="badge badge-light" target="_blank">'+str(row[0])+'.kml</a>', 'N/A', '<button type="button" class="btn btn-light btn-sm" onclick="openMap(\''+str(id)+'\')">Show Map</button>'))


        # Filter by date
        report.add_heat_map(json.dumps(activity_json))
        table_id = "MapWalkActivities"
        report.filter_by_date(table_id, 1)
        report.write_artifact_data_table(data_headers, data_list, file_found, table_id=table_id, html_escape=False)
        # Add the map to the report
        report.add_section_heading('Map My Walk Polyline Map')
        for htmlMap in html_map:
            report.add_map(htmlMap)
        report.end_artifact_report()

        tsvname = f'Map - Activities'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Map - Activities'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Map My Walk Activities data available')

    if use_network:
        conn.close()
    db.close()


__artifacts__ = {
    "MapWalkActivities": (
        "Map-My-Walk",
        ('*com.mapmywalk.android2/databases/workout.db*'),
        get_map_activities)
}

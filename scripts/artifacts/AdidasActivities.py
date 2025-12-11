# Get Information relative to the user activities that are present in the database (db) from the Adidas Running app, the activities are stored the table (session)
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-03-24
# Version: 1.0
# Requirements: Python 3.7 or higher, json, polyline, folium
import json
import os
import sqlite3

import folium
import polyline
import xlsxwriter

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, check_raw_fields, get_raw_fields, check_internet_connection


def get_adidas_activities(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Adidas Activities")
    use_network = check_internet_connection()
    if use_network:
        conn = sqlite3.connect('coordinates.db')
        c = conn.cursor()
        c.execute(
            '''CREATE TABLE IF NOT EXISTS raw_fields (id INTEGER PRIMARY KEY AUTOINCREMENT, stored_time TIMESTAMP DATETIME DEFAULT 
            CURRENT_TIMESTAMP, latitude text, longitude text, road text, city text, postcode text, country text)''')
    files_found = [x for x in files_found if not x.endswith('-journal')]
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)

    cursor = db.cursor()
    cursor.execute('''
    Select sampleId, userId, distance, datetime("startTime"/1000, 'unixepoch'), datetime("endTime"/1000, 'unixepoch'), runtime, maxSpeed, calories, temperature, note, maxPulse, avgPulse, maxElevation, minElevation, humidity, encodedTrace, firstLatitude, firstLongitude
    from session;
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries} Adidas Activities")
        report = ArtifactHtmlReport('Activities')
        report.start_artifact_report(report_folder, 'Adidas Activities')
        report.add_script()
        data_headers = ('Sample ID', 'User ID', 'Distance', 'Start Time', 'End Time', 'Run Time', 'Max Speed', 'Calories', 'Temperature', 'Note', 'Max Pulse', 'Avg Pulse', 'Max Elevation', 'Min Elevation', 'Humidity', 'Coordinates KML', 'Coordinates Excel', 'Button')
        data_list = []
        activity_date = ''
        activity_json = []
        html_map = []
        for row in all_rows:
            sampleId = row[0]
            userId = row[1]
            distance = row[2]
            startTime = row[3]
            endTime = row[4]
            runtime = row[5]
            # convert ms to minutes
            runtime = runtime / 60000
            maxSpeed = row[6]
            if maxSpeed:
                maxSpeed = round(maxSpeed, 2)
            calories = row[7]
            temperature = row[8]
            if temperature == -300:
                temperature = 'N/A'
            note = row[9]
            maxPulse = row[10]
            avgPulse = row[11]
            maxElevation = row[12]
            if maxElevation == -32768:
                maxElevation = 'N/A'
            minElevation = row[13]
            if minElevation == 32767:
                minElevation = 'N/A'
            humidity = row[14]
            if humidity == -1:
                humidity = 'N/A'
            poly = row[15]
            if poly:
                # logfunc(f"Polyline: {poly}")
                try:
                    coordinates = polyline.decode(poly)
                except:
                    logfunc(f"Polyline: {poly} could not be decoded")
                    poly = None
                    break
                place_lat = []
                place_lon = []
                if use_network:
                    if os.name == 'nt':
                        f = open(report_folder + "\\" + str(row[0]) + ".xlsx", "w")
                        workbook = xlsxwriter.Workbook(report_folder + "\\" + str(row[0]) + ".xlsx")
                    else:
                        f = open(report_folder + "/" + str(row[0]) + ".xlsx", "w")
                        workbook = xlsxwriter.Workbook(report_folder + "/" + str(row[0]) + ".xlsx")
                    worksheet = workbook.add_worksheet()
                    rowE = 0
                    col = 0
                    worksheet.write(rowE, col, "Latitude")
                    worksheet.write(rowE, col + 1, "Longitude")
                    worksheet.write(rowE, col + 2, "Road")
                    worksheet.write(rowE, col + 3, "City")
                    worksheet.write(rowE, col + 4, "Postcode")
                    worksheet.write(rowE, col + 5, "Country")
                    rowE += 1
                    for coordinate in coordinates:
                        coordinate = str(coordinate)
                        # remove the parenthesis
                        coordinate = coordinate.replace("(", "")
                        coordinate = coordinate.replace(")", "")
                        coordinate = coordinate.split(",")
                        lat = float(coordinate[0])
                        lon = float(coordinate[1])
                        lat = round(lat, 3)
                        lon = round(lon, 3)
                        worksheet.write(rowE, col, lat)
                        worksheet.write(rowE, col + 1, lon)
                        location = check_raw_fields(lat, lon, c)
                        if location is None:
                            logfunc('Getting coordinates data from API might take some time')
                            location = get_raw_fields(lat, lon, c, conn)
                            for key, value in location.items():
                                if key == "road":
                                    worksheet.write(rowE, col + 2, value)
                                elif key == "city":
                                    worksheet.write(rowE, col + 3, value)
                                elif key == "postcode":
                                    worksheet.write(rowE, col + 4, value)
                                elif key == "country":
                                    worksheet.write(rowE, col + 5, value)
                        else:
                            logfunc('Getting coordinate data from database')
                            worksheet.write(rowE, col + 2, location[4])
                            worksheet.write(rowE, col + 3, location[5])
                            worksheet.write(rowE, col + 4, location[6])
                            worksheet.write(rowE, col + 5, location[7])
                        rowE += 1
                    workbook.close()

                m = folium.Map(location=[row[16], row[17]], zoom_start=10, max_zoom=19)

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

                # Create polyline
                folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(m)
                # Save the map to an HTML file
                title = 'Adidas_Polyline_Map_' + str(sampleId)
                if os.name == 'nt':
                    m.save(report_folder + '\\' + title + '.html')
                else:
                    m.save(report_folder + '/' + title + '.html')
                html_map.append('<iframe id="' + str(
                    sampleId) + '" src="Adidas-Running/' + title + '.html" width="100%" height="500" class="map" hidden></iframe>')
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
            if poly:
                if use_network:
                    data_list.append((sampleId, userId, distance, startTime, endTime, runtime, maxSpeed, calories, temperature, note, maxPulse, avgPulse, maxElevation, minElevation, humidity, '<a href=Adidas-Running/'+str(row[0])+'.kml class="badge badge-light" target="_blank">'+str(row[0])+'.kml</a>', '<a href=Adidas-Running/'+str(row[0])+'.xlsx class="badge badge-light" target="_blank">'+str(row[0])+'.xlsx</a>', '<button type="button" class="btn btn-light btn-sm" onclick="openMap(\''+str(sampleId)+'\')">Show Map</button>'))
                else:
                    data_list.append((sampleId, userId, distance, startTime, endTime, runtime, maxSpeed, calories, temperature, note, maxPulse, avgPulse, maxElevation, minElevation, humidity, '<a href=Adidas-Running/'+str(row[0])+'.kml class="badge badge-light" target="_blank">'+str(row[0])+'.kml</a>', 'N/A', '<button type="button" class="btn btn-light btn-sm" onclick="openMap(\''+str(sampleId)+'\')">Show Map</button>'))
            else:
                data_list.append((sampleId, userId, distance, startTime, endTime, runtime, maxSpeed, calories, temperature, note, maxPulse, avgPulse, maxElevation, minElevation, humidity, 'N/A', 'N/A', 'N/A'))
        # Added feature to allow the user to sort the data by the selected collumns and with the ID of the table
        tableID = 'adidas_activities'
        report.add_heat_map(json.dumps(activity_json))
        report.filter_by_date(tableID, 3)

        report.write_artifact_data_table(data_headers, data_list, file_found, table_id=tableID, html_escape=False)
        # Add the map to the report
        report.add_section_heading('Adidas Polyline Map')
        for htmlMap in html_map:
            report.add_map(htmlMap)
        report.end_artifact_report()

        tsvname = f'Adidas - Activities'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Adidas - Activities'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Adidas Activities data available')

    if use_network:
        conn.close()
    db.close()


__artifacts__ = {
    "AdidasActivities": (
        "Adidas-Running",
        ('*/com.runtastic.android/databases/db*'),
        get_adidas_activities)
}
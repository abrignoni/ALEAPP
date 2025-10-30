# Get GPS data from the table 'activity_polyline' and activity_details
# The script uses polyline to decode the GPS data and folium to plot the GPS data on a map
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-03-18
# Version: 1.0
# Requirements: Python 3.7 or higher, folium and polyline, datetime
import datetime
import os
import sqlite3

import folium
import polyline
import xlsxwriter

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, check_raw_fields, get_raw_fields, check_internet_connection


def get_nike_polyline(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Nike Polyline")
    use_network = check_internet_connection()
    if use_network:
        conn = sqlite3.connect('coordinates.db')
        c = conn.cursor()
        c.execute(
            '''CREATE TABLE IF NOT EXISTS raw_fields (id INTEGER PRIMARY KEY AUTOINCREMENT, stored_time TIMESTAMP DATETIME DEFAULT 
            CURRENT_TIMESTAMP, latitude text, longitude text, road text, city text, postcode text, country text)''')

    #Generate title for map file
    title = 'Nike_Polyline_Map_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)

    # Get the GPS data from the table 'activity_polyline' for the activities in the table 'activity_details'
    cursor = db.cursor()
    cursor.execute('''
        SELECT 
        activity.as2_sa_id, 
        activity.as2_sa_start_utc_ms,
        activity.as2_sa_end_utc_ms,
        activity.as2_sa_active_duration_ms,
        ap.as2_p_encoded_polyline
        from activity 
        left join activity_polyline ap on activity.as2_sa_id = ap.as2_p_activity_id
        where ap.as2_p_encoded_polyline is not null
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f'Found {usageentries} activity_polyline entries')
        report = ArtifactHtmlReport('Nike - Activity Route')
        report.start_artifact_report(report_folder, 'Nike - Activity Route')
        report.add_script()
        data_headers = ('Activity ID', 'Start Time UTC', 'End Time UTC', 'Duration', 'Coordinates KML', 'Coordinates Excel', 'Button')
        data_list = []
        html_map = []
        for row in all_rows:
            activity_id = row[0]
            place_lat = []
            place_lon = []
            start_time_utc = row[1]
            # convert ms to date
            start_time_utc = datetime.datetime.utcfromtimestamp(start_time_utc / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
            end_time_utc = row[2]
            # convert ms to date
            end_time_utc = datetime.datetime.utcfromtimestamp(end_time_utc / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
            duration = row[3]
            # convert ms to minutes
            duration = duration / 60000
            # round to 2 decimals
            duration = round(duration, 2)

            #convert polyline to lat/long
            coordinates = polyline.decode(row[4])
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

            m = folium.Map(location=[coordinates[0][0], coordinates[0][1]], zoom_start=10, max_zoom=19)

            for coordinate in coordinates:
                #if points are to close, skip
                if len(place_lat) > 0 and abs(place_lat[-1] - coordinate[0]) < 0.0001 and abs(place_lon[-1] - coordinate[1]) < 0.0001:
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
                    folium.Marker([lat, place_lon[index]],popup=(('Start Location\nActivity ID \n' + str(row[0])).format(index)),icon=folium.Icon(color='blue', icon='flag', prefix='fa')).add_to(m)
                # last point
                elif index == len(place_lat) - 1:
                    folium.Marker([lat, place_lon[index]],popup=(('End Location\nActivity ID \n' + str(row[0])).format(index)),icon=folium.Icon(color='red', icon='flag', prefix='fa')).add_to(m)
                # middle points


            # Create polyline
            folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(m)
            # Save the map to an HTML file
            title = 'Nike_Polyline_Map_' + str(activity_id)
            if os.name == 'nt':
                m.save(report_folder + '\\' + title + '.html')
            else:
                m.save(report_folder + '/' + title + '.html')
            html_map.append('<iframe id="' + str(activity_id) + '" src="Nike-Run/' + title + '.html" width="100%" height="500" class="map" hidden></iframe>')
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
            # Store the map in the report
            if use_network:
                data_list.append((activity_id, start_time_utc, end_time_utc, duration, '<a href=Nike-Run/'+str(activity_id)+'.kml class="badge badge-light" target="_blank">'+str(row[0])+'.kml</a>', '<a href=Nike-Run/'+str(activity_id)+'.xlsx class="badge badge-light" target="_blank">'+str(row[0])+'.xlsx</a>', '<button type="button" class="btn btn-light btn-sm" onclick="openMap(\''+str(activity_id)+'\')">Show Map</button>'))
            else:
                data_list.append((activity_id, start_time_utc, end_time_utc, duration, '<a href=Nike-Run/'+str(activity_id)+'.kml class="badge badge-light" target="_blank">'+str(row[0])+'.kml</a>', 'N/A', '<button type="button" class="btn btn-light btn-sm" onclick="openMap(\''+str(activity_id)+'\')">Show Map</button>'))


        # Added feature to allow the user to sort the data by the selected collumns and with the ID of the table
        table_id = 'Nike_Polyline'
        report.filter_by_date(table_id, 1)

        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False, table_id='Nilke_Polyline')

        # Add the map to the report
        report.add_section_heading('Nike Polyline Map')
        for htmlMap in html_map:
            report.add_map(htmlMap)
        report.end_artifact_report()

        tsvname = f'Nike - Polyline'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Nike - Polyline'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Nike Polyline data available')

    if use_network:
        conn.close()
    db.close()


__artifacts__ = {
    "NikePolyline": (
        "Nike-Run",
        ('*/com.nike.plusgps/databases/com.nike.nrc.room*'),
        get_nike_polyline)
}

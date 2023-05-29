# Get GPS coordinates from Strava FIT files stored in the public folder: /Android/data/com.strava/files/activities
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-03-24
# Version: 1.0
# Requirements: Python 3.7 or higher, folium and polyline, fitdecode, datetime
from datetime import datetime
import warnings
import os
import sqlite3

import folium
import fitdecode
import xlsxwriter

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, check_raw_fields, get_raw_fields, check_internet_connection


def suppress_fitdecode_warnings(message, category, filename, lineno, file=None, line=None):
    if category == UserWarning and 'fitdecode' in message.args[0]:
        return
    else:
        return message, category, filename, lineno, file, line


# Set the filter function as the default warning filter
warnings.showwarning = suppress_fitdecode_warnings


def get_gps(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Strava FIT Files")
    use_network = check_internet_connection()
    if use_network:
        conn = sqlite3.connect('coordinates.db')
        c = conn.cursor()
        c.execute(
            '''CREATE TABLE IF NOT EXISTS raw_fields (id INTEGER PRIMARY KEY AUTOINCREMENT, stored_time TIMESTAMP DATETIME DEFAULT 
            CURRENT_TIMESTAMP, latitude text, longitude text, road text, city text, postcode text, country text)''')
    report = ArtifactHtmlReport('Strava')
    report.start_artifact_report(report_folder, 'Strava')
    report.add_script()
    # report.filter_by_date('GarminActAPI', 1, 1)
    data_headers = (
    'Activity Type', 'Start Time', 'End Time', 'Total Time (minutes)', 'Total Distance (km)', 'Coordinates KML', 'Coordinates Excel', 'Button')
    data_list = []
    html_map = []
    act = 1
    files_found = [x for x in files_found if x.endswith('fit')]
    # file = str(files_found[0])
    for file in files_found:
        file = str(file)
        logfunc("Processing file: " + file)
        coordinates = []
        coordinatesE = []
        # Decode FIT file
        with fitdecode.FitReader(file) as fit:
            logfunc("Found Strava FIT file")
            for frame in fit:
                if frame.frame_type == fitdecode.FIT_FRAME_DATAMESG:
                    if frame.name == 'record':
                        # Check if the record message contains the position_lat
                        # and position_long fields.
                        if frame.has_field('position_lat') and frame.has_field('position_long'):
                            lat = frame.get_value('position_lat')
                            lon = frame.get_value('position_long')
                            timestamp = frame.get_value('timestamp')
                            timestamp = timestamp.timestamp()
                            # convert from UNIX timestamp to UTC
                            timestamp = datetime.utcfromtimestamp(timestamp)
                            timestamp = str(timestamp)
                            # convert from semicircles to degrees
                            lat = lat * (180.0 / 2 ** 31)
                            lon = lon * (180.0 / 2 ** 31)
                            # round to 5 decimal places
                            lat = round(lat, 5)
                            lon = round(lon, 5)
                            coordinates.append([lat, lon])
                            coordinatesE.append([lat, lon, timestamp])
                    elif frame.name == 'session':
                        if frame.has_field('total_elapsed_time'):
                            total_elapsed_time = frame.get_value('total_elapsed_time')
                            # convert to minutes
                            total_elapsed_time_m = total_elapsed_time / 60
                            total_elapsed_time_m = int(total_elapsed_time_m)
                        if frame.has_field('start_time'):
                            start_time = frame.get_value('start_time')
                            # convert from FIT timestamp to UNIX timestamp
                            start_time_u = start_time.timestamp()
                            # add seconds to the UNIX timestamp
                            end_time = start_time_u + total_elapsed_time
                            # convert from UNIX timestamp to UTC
                            start_time = datetime.utcfromtimestamp(start_time_u)
                            end_time = datetime.utcfromtimestamp(end_time)
                        if frame.has_field('sport'):
                            sport = frame.get_value('sport')
                        if frame.has_field('total_distance'):
                            total_distance = frame.get_value('total_distance')
                            # convert from m to km
                            total_distance = total_distance / 1000
                            total_distance = round(total_distance, 2)
        # Generate HTML file with the map and the route using Folium
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
                    folium.Marker([lat, place_lon[index]], popup=('Start Location\n'.format(index)),
                                  icon=folium.Icon(color='blue', icon='flag', prefix='fa')).add_to(m)
                # last point
                elif index == len(place_lat) - 1:
                    folium.Marker([lat, place_lon[index]], popup=(('End Location\n').format(index)),
                                  icon=folium.Icon(color='red', icon='flag', prefix='fa')).add_to(m)
                # middle points

        if use_network:
            # Create an excel file with the coordinates
            if os.name == 'nt':
                f = open(report_folder + "\\" + str(act) + ".xlsx", "w")
                workbook = xlsxwriter.Workbook(report_folder + "\\" + str(act) + ".xlsx")
            else:
                f = open(report_folder + "/" + str(act) + ".xlsx", "w")
                workbook = xlsxwriter.Workbook(report_folder + "/" + str(act) + ".xlsx")
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
        title = 'Strava_Activity_' + str(act)
        if os.name == 'nt':
            m.save(report_folder + '\\' + title + '.html')
        else:
            m.save(report_folder + '/' + title + '.html')
        html_map.append('<iframe id="' + str(
            act) + '" src="Strava/' + title + '.html" width="100%" height="500" class="map" hidden></iframe>')
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
        for coordinate in coordinates:
            kml += str(coordinate[1]) + "," + str(coordinate[0]) + ",0 \n"
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
            with open(report_folder + '\\' + str(act) + '.kml', 'w') as f:
                f.write(kml)
                f.close()
        else:
            with open(report_folder + '/' + str(act) + '.kml', 'w') as f:
                f.write(kml)
                f.close()
        if use_network:
            data_list.append((sport, start_time, end_time, total_elapsed_time_m, total_distance, '<a href=Strava/' + str(
                act) + '.kml class="badge badge-light" target="_blank">' + str(act) + '.kml</a>', '<a href=Strava/' + str(
                act) + '.xlsx class="badge badge-light" target="_blank">' + str(act) + '.xlsx</a>',
                              '<button type="button" class="btn btn-light btn-sm" onclick="openMap(\'' + str(
                                  act) + '\')">Show Map</button>'))
        else:
            data_list.append(
                (sport, start_time, end_time, total_elapsed_time_m, total_distance, '<a href=Strava/' + str(
                    act) + '.kml class="badge badge-light" target="_blank">' + str(act) + '.kml</a>',
                 'N/A',
                 '<button type="button" class="btn btn-light btn-sm" onclick="openMap(\'' + str(
                     act) + '\')">Show Map</button>'))
        act += 1

    report.filter_by_date('Strava', 1)
    report.write_artifact_data_table(data_headers, data_list, file, html_escape=False, table_id='Strava')
    # Add the map to the report
    report.add_section_heading('Strava')
    for htmlMap in html_map:
        report.add_map(htmlMap)
    report.end_artifact_report()

    tsvname = f'Strava Log'
    tsv(report_folder, data_headers, data_list, tsvname)

    if use_network:
        conn.close()

__artifacts__ = {
    "Strava": (
        "Strava",
        ('*/com.strava/files*'),
        get_gps)
}

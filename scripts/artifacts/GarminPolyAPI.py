# Get GPS coordinates from Garmin API related to activities
# Requires to have extracted the information from the Garmin API using the script in the url: https://github.com/labcif/Garmin-Connect-API-Extractor
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-02-24
# Version: 1.0
# Requirements: Python 3.7 or higher, json and datetime
import datetime
import json
import os
import sqlite3

import folium
import xlsxwriter

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, check_raw_fields, get_raw_fields, check_internet_connection


def get_poly_api(files_found, report_folder, seeker, wrap_text):

    logfunc("Processing data for Polyline API")
    use_network = check_internet_connection()
    if use_network:
        conn = sqlite3.connect('coordinates.db')
        c = conn.cursor()
        c.execute(
            '''CREATE TABLE IF NOT EXISTS raw_fields (id INTEGER PRIMARY KEY AUTOINCREMENT, stored_time TIMESTAMP DATETIME DEFAULT 
            CURRENT_TIMESTAMP, latitude text, longitude text, road text, city text, postcode text, country text)''')

    report = ArtifactHtmlReport('Polyline API')
    report.start_artifact_report(report_folder, 'Polyline API')
    report.add_script()
    # report.filter_by_date('GarminActAPI', 1, 1)
    data_headers = ('Activity ID', 'Start Time', 'End Time', 'Start Coordinates', 'End Coordinates', 'Coordinates KML', 'Coordiantes Excel', 'Button')
    data_list = []
    html_map = []
    #file = str(files_found[0])
    for file in files_found:
        file = str(file)
        logfunc("Processing file: " + file)
        #Open JSON file
        with open(file, "r") as f:
            data = json.load(f)

        if len(data) > 0:

            logfunc("Found Garmin Presistent file")
            # Get Activity ID

            activity_id = data['activityId']
            # Get polyline array
            polyline = data['geoPolylineDTO']['polyline']
            place_lat = []
            place_lon = []
            coordinates = []
            i = 0
            for geo in polyline:
                if i == 0:
                    # convert unix timestamp to datetime
                    start_time = datetime.datetime.utcfromtimestamp(geo['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    start = '[' + str(geo['lat']) + ', ' + str(geo['lon']) + ']'
                    place_lat.append(geo['lat'])
                    place_lon.append(geo['lon'])
                    m = folium.Map(location=[geo['lat'], geo['lon']], zoom_start=10, max_zoom=19)
                    i += 1
                # last point
                elif i == len(polyline) - 1:
                    # convert unix timestamp to datetime
                    end_time = datetime.datetime.utcfromtimestamp(geo['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    end = '[' + str(geo['lat']) + ', ' + str(geo['lon']) + ']'
                    place_lat.append(geo['lat'])
                    place_lon.append(geo['lon'])
                    i += 1
                else:
                    if len(place_lat) > 0 and abs(place_lat[-1] - geo['lat']) < 0.0002 and abs(
                            place_lon[-1] - geo['lat']) < 0.0002:
                        continue
                    else:
                        place_lat.append(geo['lat'])
                        place_lon.append(geo['lon'])
                    i += 1
                time = datetime.datetime.utcfromtimestamp(geo['time'] / 1000).strftime('%Y-%m-%d')
                coordinates.append([geo['lat'], geo['lon'], time])

            points = []
            for i in range(len(place_lat)):
                points.append([place_lat[i], place_lon[i]])

            for index, lat in enumerate(place_lat):
                # Start point
                if index == 0:
                    folium.Marker([lat, place_lon[index]],
                                    popup=(('Start Location\nActivity ID \n' + str(activity_id)).format(index)),
                                    icon=folium.Icon(color='blue', icon='flag', prefix='fa')).add_to(m)
                # last point
                elif index == len(place_lat) - 1:
                    folium.Marker([lat, place_lon[index]],
                                    popup=(('End Location\nActivity ID \n' + str(activity_id)).format(index)),
                                    icon=folium.Icon(color='red', icon='flag', prefix='fa')).add_to(m)

            if use_network:
                # Create an excel file with the coordinates
                if os.name == 'nt':
                    f = open(report_folder + "\\" + str(activity_id) + ".xlsx", "w")
                    workbook = xlsxwriter.Workbook(report_folder + "\\" + str(activity_id) + ".xlsx")
                else:
                    f = open(report_folder + "/" + str(activity_id) + ".xlsx", "w")
                    workbook = xlsxwriter.Workbook(report_folder + "/" + str(activity_id) + ".xlsx")
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
                for coordinate in coordinates:
                    lat = float(coordinate[0])
                    lon = float(coordinate[1])
                    lat = round(lat, 3)
                    lon = round(lon, 3)
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
            title = 'Garmin_Polyline_Map_' + str(activity_id)
            if os.name == 'nt':
                m.save(report_folder + '\\' + title + '.html')
            else:
                m.save(report_folder + '/' + title + '.html')
            html_map.append('<iframe id="' + str(activity_id) + '" src="Garmin-API/' + title + '.html" width="100%" height="500" class="map" hidden></iframe>')
            #save coords to a kml file
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
                with open(report_folder + '\\' + str(activity_id) + '.kml', 'w') as f:
                    f.write(kml)
                    f.close()
            else:
                with open(report_folder + '/' + str(activity_id) + '.kml', 'w') as f:
                    f.write(kml)
                    f.close()
            if use_network:
                data_list.append((activity_id, start_time, end_time, start, end, '<a href=Garmin-API/'+str(activity_id)+'.kml class="badge badge-light" target="_blank">'+str(activity_id)+'.kml</a>', '<a href=Garmin-API/'+str(activity_id)+'.xlsx class="badge badge-light" target="_blank">'+str(activity_id)+'.xlsx</a>', '<button type="button" class="btn btn-light btn-sm" onclick="openMap(\''+str(activity_id)+'\')">Show Map</button>'))
            else:
                data_list.append((activity_id, start_time, end_time, start, end, str(activity_id)+'.kml', 'N/A', '<button type="button" class="btn btn-light btn-sm" onclick="openMap(\''+str(activity_id)+'\')">Show Map</button>'))

    report.filter_by_date('GarminPolyAPI', 1)
    report.write_artifact_data_table(data_headers, data_list, file, html_escape=False, table_id='GarminPolyAPI')
    # Add the map to the report
    report.add_section_heading('Garmin Polyline Map')
    for htmlMap in html_map:
        report.add_map(htmlMap)
    report.end_artifact_report()

    tsvname = f'Garmin Log'
    tsv(report_folder, data_headers, data_list, tsvname)

    if use_network:
        conn.close()


__artifacts__ = {
    "GarminPolyAPI": (
        "Garmin-API",
        ('*/garmin.api/activity_details*'),
        get_poly_api)
}

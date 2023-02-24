# Get GPS coordinates from Garmin API related to activities
# Requires to have extracted the information from the Garmin API using the script in the url: https://github.com/labcif/Garmin-Connect-API-Extractor
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-02-24
# Version: 1.0
# Requirements: Python 3.7 or higher, json and datetime
import datetime
import json
import os

import folium

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv


def get_poly_api(files_found, report_folder, seeker, wrap_text):

    logfunc("Processing data for Polyline API")
    report = ArtifactHtmlReport('Polyline API')
    report.start_artifact_report(report_folder, 'Polyline API')
    report.add_script()
    # report.filter_by_date('GarminActAPI', 1, 1)
    data_headers = ('Activity ID', 'Start Time', 'End Time', 'Start Coordinates', 'End Coordinates', 'Coordinates', 'Button')
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
            coords = ""
            i = 0
            for geo in polyline:
                if i == 0:
                    # convert unix timestamp to datetime
                    start_time = datetime.datetime.fromtimestamp(geo['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    start = '[' + str(geo['lat']) + ', ' + str(geo['lon']) + ']'
                    place_lat.append(geo['lat'])
                    place_lon.append(geo['lon'])
                    coords += '[' + str(place_lat) + ', ' + str(place_lon) + ']'
                    m = folium.Map(location=[geo['lat'], geo['lon']], zoom_start=10, max_zoom=19)
                    i += 1
                # last point
                elif i == len(polyline) - 1:
                    # convert unix timestamp to datetime
                    end_time = datetime.datetime.fromtimestamp(geo['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    end = '[' + str(geo['lat']) + ', ' + str(geo['lon']) + ']'
                    place_lat.append(geo['lat'])
                    place_lon.append(geo['lon'])
                    coords += ', [' + str(place_lat) + ', ' + str(place_lon) + ']'
                    i += 1
                else:
                    if len(place_lat) > 0 and abs(place_lat[-1] - geo['lat']) < 0.0002 and abs(
                            place_lon[-1] - geo['lat']) < 0.0002:
                        continue
                    else:
                        place_lat.append(geo['lat'])
                        place_lon.append(geo['lon'])
                    coords += ', [' + str(place_lat) + ', ' + str(place_lon) + ']'
                    i += 1

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
            data_list.append((activity_id, start_time, end_time, start, end, '<a href=Garmin-API/'+str(activity_id)+'.kml class="badge badge-light" target="_blank">'+str(activity_id)+'.kml</a>', '<button type="button" class="btn btn-light btn-sm" onclick="openMap(\''+str(activity_id)+'\')">Show Map</button>'))

    report.filter_by_date('GarminPolyAPI', 1)
    report.write_artifact_data_table(data_headers, data_list, file, html_escape=False, table_id='GarminPolyAPI')
    # Add the map to the report
    report.add_section_heading('Garmin Polyline Map')
    for htmlMap in html_map:
        report.add_map(htmlMap)
    report.end_artifact_report()

    tsvname = f'Garmin Log'
    tsv(report_folder, data_headers, data_list, tsvname)


__artifacts__ = {
    "GarminPolyAPI": (
        "Garmin-API",
        ('*/garmin.api/activity_details*'),
        get_poly_api)
}

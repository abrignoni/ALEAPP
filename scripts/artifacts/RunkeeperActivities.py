# Get Information related to the activities of the user from the Runkeeper app database
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-03-25
# Version: 1.0
# Requirements: Python 3.7 or higher, folium
import json
import os

import folium

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_run_activities(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Runkeeper Activities")
    files_found = [x for x in files_found if not x.endswith('-journal')]
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)

    # Get information from the table device_sync_audit
    cursor = db.cursor()
    cursor.execute('''
        Select _id, datetime("start_date"/1000,'unixepoch'), datetime("device_sync_time"/1000,'unixepoch'), distance, elapsed_time, activity_type, calories, heart_rate, totalClimb, uuid, nickname
        from trips
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries} entries in completed_exercises")
        report = ArtifactHtmlReport('Activities')
        report.start_artifact_report(report_folder, 'Runkeeper Activities')
        report.add_script()
        data_headers = ('ID', 'Start Time', 'End Time', 'Distance', 'Duration', 'Activity Type', 'Calories', 'Heart Rate', 'Total Climb', 'UUID', 'Nickname', 'Coordinates', 'Button')
        data_list = []
        activity_date = ''
        activity_json = []
        html_map = []
        for row in all_rows:
            id = row[0]
            map = False
            coordinates = []
            cursor.execute(f'''
                            Select latitude, longitude
                            from points
                            where trip_id = '{id}'
                        ''')
            positions = cursor.fetchall()
            usageentries_p = len(positions)
            if usageentries_p > 0:
                for row_p in positions:
                    coordinates.append((row_p[0], row_p[1]))
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

                # Create polyline
                folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(m)
                # Save the map to an HTML file
                title = 'Runkeeper_Polyline_Map_' + str(id)
                if os.name == 'nt':
                    m.save(report_folder + '\\' + title + '.html')
                else:
                    m.save(report_folder + '/' + title + '.html')
                html_map.append('<iframe id="' + str(
                    id) + '" src="Runkeeper/' + title + '.html" width="100%" height="500" class="map" hidden></iframe>')
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
            startTime = row[1]
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

            if map:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], '<a href=Runkeeper/'+str(row[0])+'.kml class="badge badge-light" target="_blank">'+str(row[0])+'.kml</a>', '<button type="button" class="btn btn-light btn-sm" onclick="openMap(\''+str(id)+'\')">Show Map</button>'))
            else:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], 'N/A', 'N/A'))

        # Filter by date
        report.add_heat_map(json.dumps(activity_json))
        table_id = "RunkeeperActivities"
        report.filter_by_date(table_id, 1)
        report.write_artifact_data_table(data_headers, data_list, file_found, table_id=table_id, html_escape=False)
        # Add the map to the report
        report.add_section_heading('Runkeeper Polyline Map')
        for htmlMap in html_map:
            report.add_map(htmlMap)
        report.end_artifact_report()

        tsvname = f'Runkeeper - Activities'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Runkeeper - Activities'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Runkeeper Activities data available')

    db.close()


__artifacts__ = {
    "RunkeeperActivities": (
        "Runkeeper",
        ('*com.fitnesskeeper.runkeeper.pro/databases/RunKeeper.sqlite*'),
        get_run_activities)
}

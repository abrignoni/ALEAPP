__artifacts_v2__ = {
    "organicmaps_bookmarks": {
        "name": "Organic Maps - Bookmarks",
        "description": "Parses the saved place bookmarks of the Organic Maps Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Organic Maps",
        "notes": "One row per point bookmark in the KML files under files/bookmarks. Organic Maps "
                 "stores each bookmark category as its own KML document, so the Category column is the "
                 "document name, which is also the file name without the extension. Each row carries "
                 "the bookmark's name, its Latitude, Longitude and altitude taken from the KML Point "
                 "(KML stores coordinates in longitude, latitude, altitude order, and they are split "
                 "back out here), a Timestamp, and any description the user added. The Timestamp is the "
                 "KML TimeStamp/when value, an ISO 8601 time ending in Z, so it is UTC and is reported "
                 "as stored; on the tested device 14:42 UTC matched the device's 10:42 local clock. A "
                 "bookmark records that the user saved that location on this device. The client can "
                 "also keep a compiled binary copy of the same bookmarks with a .kmb extension; that is "
                 "not parsed here because the .kml is the editable source the client writes. Recorded "
                 "GPS tracks are in the same KML files as line geometry and are reported by the Tracks "
                 "artifact, not here. The app's settings.ini in the same container holds the storage "
                 "path, the last used bookmark category and an assisted GPS timestamp, and is not "
                 "parsed.",
        "paths": ('*/app.organicmaps*/files/bookmarks/*.kml',),
        "output_types": "all",
        "artifact_icon": "map-pin"
    },
    "organicmaps_tracks": {
        "name": "Organic Maps - Tracks",
        "description": "Parses the recorded GPS tracks of the Organic Maps Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Organic Maps",
        "notes": "One row per recorded track in the KML files under files/bookmarks. A track is a "
                 "Placemark whose geometry is a line rather than a single point, stored either as a "
                 "LineString or as a gx:Track. Each row gives the track's name, its category (the KML "
                 "document name), the number of points, and the first and last coordinates so the "
                 "extent is visible; the Latitude and Longitude columns hold the first point so the row "
                 "maps. A gx:Track can also carry a when time per point, and the first and last of "
                 "those are reported as the start and end times when present, as stored. This was "
                 "empty on the tested device, so the line and gx:Track parsing is code-present and "
                 "exercised against no rows here. The full point list is not enumerated one row per "
                 "point; the KML itself in files/bookmarks holds every point for an examiner who needs "
                 "the whole line.",
        "paths": ('*/app.organicmaps*/files/bookmarks/*.kml',),
        "output_types": "all",
        "artifact_icon": "route"
    }
}

import os
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.artifacts.storagePathViews import unique_files

KML_NS = {'k': 'http://www.opengis.net/kml/2.2',
          'gx': 'http://www.google.com/kml/ext/2.2'}


def _text(element, path):
    found = element.find(path, KML_NS)
    if found is None or found.text is None:
        return ''
    return found.text.strip()


def _category(document, file_found):
    name = _text(document, 'k:name')
    if name:
        return name
    return os.path.splitext(os.path.basename(file_found))[0]


def _split_coordinate(triple):
    """A single KML 'lon,lat,alt' coordinate as (lat, lon, alt) strings."""
    parts = [p for p in triple.strip().split(',') if p != '']
    if len(parts) < 2:
        return '', '', ''
    lon, lat = parts[0], parts[1]
    alt = parts[2] if len(parts) > 2 else ''
    return lat, lon, alt


def _kml_documents(context):
    """(ElementTree document element, file path) for every bookmarks KML that parses."""
    for file_found in unique_files(context):
        file_found = str(file_found).replace('\\', '/')
        if os.path.isdir(file_found) or not file_found.endswith('.kml'):
            continue
        try:
            tree = ET.parse(file_found)
        except ET.ParseError as error:
            logfunc(f'Organic Maps: could not parse {file_found}: {error}')
            continue
        document = tree.getroot().find('k:Document', KML_NS)
        if document is None:
            continue
        yield document, file_found


@artifact_processor
def organicmaps_bookmarks(context):
    data_list = []
    sources = []
    for document, file_found in _kml_documents(context):
        category = _category(document, file_found)
        read_any = False
        for placemark in document.findall('k:Placemark', KML_NS):
            point = placemark.find('k:Point/k:coordinates', KML_NS)
            if point is None or not (point.text and point.text.strip()):
                continue
            lat, lon, alt = _split_coordinate(point.text)
            data_list.append((
                _text(placemark, 'k:TimeStamp/k:when'),
                _text(placemark, 'k:name'),
                category,
                lat, lon, alt,
                _text(placemark, 'k:description'),
                context.get_relative_path(file_found),
            ))
            read_any = True
        if read_any and file_found not in sources:
            sources.append(file_found)

    data_headers = (
        'Timestamp', 'Name', 'Category', 'Latitude', 'Longitude', 'Altitude',
        'Description', 'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)


def _line_points(placemark):
    """[(lat, lon, alt), ...] and [when, ...] for a track placemark, or ([], [])."""
    coords = placemark.find('k:LineString/k:coordinates', KML_NS)
    if coords is not None and coords.text:
        points = [_split_coordinate(c) for c in coords.text.split() if c.strip()]
        return points, []
    track = placemark.find('gx:Track', KML_NS)
    if track is not None:
        points = []
        whens = []
        for element in track:
            tag = element.tag.split('}')[-1]
            if tag == 'coord' and element.text:
                parts = element.text.split()
                if len(parts) >= 2:
                    alt = parts[2] if len(parts) > 2 else ''
                    points.append((parts[1], parts[0], alt))
            elif tag == 'when' and element.text:
                whens.append(element.text.strip())
        return points, whens
    return [], []


@artifact_processor
def organicmaps_tracks(context):
    data_list = []
    sources = []
    for document, file_found in _kml_documents(context):
        category = _category(document, file_found)
        read_any = False
        for placemark in document.findall('k:Placemark', KML_NS):
            points, whens = _line_points(placemark)
            if not points:
                continue
            first = points[0]
            last = points[-1]
            data_list.append((
                whens[0] if whens else '',
                whens[-1] if whens else '',
                _text(placemark, 'k:name'),
                category,
                len(points),
                first[0], first[1],
                last[0], last[1],
                context.get_relative_path(file_found),
            ))
            read_any = True
        if read_any and file_found not in sources:
            sources.append(file_found)

    data_headers = (
        'Start Time', 'End Time', 'Name', 'Category', 'Point Count',
        'Latitude', 'Longitude', 'End Latitude', 'End Longitude', 'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)

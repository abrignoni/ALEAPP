# common standard imports
import codecs
import csv
from datetime import *
import json
import os
import re
import shutil
import sqlite3
import sys
from functools import lru_cache
from pathlib import Path

# common third party imports
import pytz
import simplekml
from bs4 import BeautifulSoup
from scripts.filetype import guess_mime

# LEAPP version unique imports
from geopy.geocoders import Nominatim


os.path.basename = lru_cache(maxsize=None)(os.path.basename)

class OutputParameters:
    '''Defines the parameters that are common for '''
    # static parameters
    nl = '\n'
    screen_output_file_path = ''

    def __init__(self, output_folder):
        now = datetime.now()
        currenttime = str(now.strftime('%Y-%m-%d_%A_%H%M%S'))
        self.report_folder_base = os.path.join(output_folder,
                                               'ALEAPP_Reports_' + currenttime)  # aleapp , aleappGUI, ileap_artifacts, report.py
        self.temp_folder = os.path.join(self.report_folder_base, 'temp')
        OutputParameters.screen_output_file_path = os.path.join(self.report_folder_base, 'Script Logs',
                                                                'Screen Output.html')
        OutputParameters.screen_output_file_path_devinfo = os.path.join(self.report_folder_base, 'Script Logs',
                                                                        'DeviceInfo.html')

        os.makedirs(os.path.join(self.report_folder_base, 'Script Logs'))
        os.makedirs(self.temp_folder)
        
def convert_local_to_utc(local_timestamp_str):
    # Parse the timestamp string with timezone offset, ex. 2023-10-27 18:18:29-0400
    local_timestamp = datetime.strptime(local_timestamp_str, "%Y-%m-%d %H:%M:%S%z")
    
    # Convert to UTC timestamp
    utc_timestamp = local_timestamp.astimezone(timezone.utc)
    
    # Return the UTC timestamp
    return utc_timestamp

def convert_time_obj_to_utc(ts):
    timestamp = ts.replace(tzinfo=timezone.utc)
    return timestamp

def convert_utc_human_to_timezone(utc_time, time_offset): 
    #fetch the timezone information
    timezone = pytz.timezone(time_offset)
    
    #convert utc to timezone
    timezone_time = utc_time.astimezone(timezone)
    
    #return the converted value
    return timezone_time

def timestampsconv(webkittime):
    unix_timestamp = webkittime + 978307200
    finaltime = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
    return(finaltime)

def convert_ts_human_to_utc(ts): #This is for timestamp in human form
    if '.' in ts:
        ts = ts.split('.')[0]
        
    dt = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S') #Make it a datetime object
    timestamp = dt.replace(tzinfo=timezone.utc) #Make it UTC
    return timestamp

def convert_ts_int_to_utc(ts): #This int timestamp to human format & utc
    timestamp = datetime.fromtimestamp(ts, tz=timezone.utc)
    return timestamp

def utf8_in_extended_ascii(input_string, *, raise_on_unexpected=False):
    """Returns a tuple of bool (whether mis-encoded utf-8 is present) and str (the converted string)"""
    output = []  # individual characters, join at the end
    is_in_multibyte = False  # True if we're currently inside a utf-8 multibyte character
    multibytes_expected = 0
    multibyte_buffer = []
    mis_encoded_utf8_present = False
    
    def handle_bad_data(index, character):
        if not raise_on_unexpected: # not raising, so we dump the buffer into output and append this character
            output.extend(multibyte_buffer)
            multibyte_buffer.clear()
            output.append(character)
            nonlocal is_in_multibyte
            is_in_multibyte = False
            nonlocal multibytes_expected
            multibytes_expected = 0
        else:
            raise ValueError(f"Expected multibyte continuation at index: {index}")
            
    for idx, c in enumerate(input_string):
        code_point = ord(c)
        if code_point <= 0x7f or code_point > 0xf4:  # ASCII Range data or higher than you get for mis-encoded utf-8:
            if not is_in_multibyte:
                output.append(c)  # not in a multibyte, valid ascii-range data, so we append
            else:
                handle_bad_data(idx, c)
        else:  # potentially utf-8
            if (code_point & 0xc0) == 0x80:  # continuation byte
                if is_in_multibyte:
                    multibyte_buffer.append(c)
                else:
                    handle_bad_data(idx, c)
            else:  # start-byte
                if not is_in_multibyte:
                    assert multibytes_expected == 0
                    assert len(multibyte_buffer) == 0
                    while (code_point & 0x80) != 0:
                        multibytes_expected += 1
                        code_point <<= 1
                    multibyte_buffer.append(c)
                    is_in_multibyte = True
                else:
                    handle_bad_data(idx, c)
                    
        if is_in_multibyte and len(multibyte_buffer) == multibytes_expected:  # output utf-8 character if complete
            utf_8_character = bytes(ord(x) for x in multibyte_buffer).decode("utf-8")
            output.append(utf_8_character)
            multibyte_buffer.clear()
            is_in_multibyte = False
            multibytes_expected = 0
            mis_encoded_utf8_present = True
        
    if multibyte_buffer:  # if we have left-over data
        handle_bad_data(len(input_string), "")
    
    return mis_encoded_utf8_present, "".join(output)

def is_platform_linux():
    '''Returns True if running on Linux'''
    return sys.platform == 'linux'

def is_platform_macos():
    '''Returns True if running on macOS'''
    return sys.platform == 'darwin'

def is_platform_windows():
    '''Returns True if running on Windows'''
    return sys.platform == 'win32'

def sanitize_file_path(filename, replacement_char='_'):
    r'''
    Removes illegal characters (for windows) from the string passed. Does not replace \ or /
    '''
    return re.sub(r'[*?:"<>|\'\r\n]', replacement_char, filename)

def sanitize_file_name(filename, replacement_char='_'):
    '''
    Removes illegal characters (for windows) from the string passed.
    '''
    return re.sub(r'[\\/*?:"<>|\'\r\n]', replacement_char, filename)

def get_next_unused_name(path):
    '''Checks if path exists, if it does, finds an unused name by appending -xx
       where xx=00-99. Return value is new path.
       If it is a file like abc.txt, then abc-01.txt will be the next
    '''
    folder, basename = os.path.split(path)
    ext = None
    if basename.find('.') > 0:
        basename, ext = os.path.splitext(basename)
    num = 1
    new_name = basename
    if ext != None:
        new_name += f"{ext}"
    while os.path.exists(os.path.join(folder, new_name)):
        new_name = basename + "-{:02}".format(num)
        if ext != None:
            new_name += f"{ext}"
        num += 1
    return os.path.join(folder, new_name)

def open_sqlite_db_readonly(path):
    '''Opens an sqlite db in read-only mode, so original db (and -wal/journal are intact)'''
    if is_platform_windows():
        if path.startswith('\\\\?\\UNC\\'): # UNC long path
            path = "%5C%5C%3F%5C" + path[4:]
        elif path.startswith('\\\\?\\'):    # normal long path
            path = "%5C%5C%3F%5C" + path[4:]
        elif path.startswith('\\\\'):       # UNC path
            path = "%5C%5C%3F%5C\\UNC" + path[1:]
        else:                               # normal path
            path = "%5C%5C%3F%5C" + path
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def does_column_exist_in_db(db, table_name, col_name):
    '''Checks if a specific col exists'''
    col_name = col_name.lower()
    try:
        db.row_factory = sqlite3.Row # For fetching columns by name
        query = f"pragma table_info('{table_name}');"
        cursor = db.cursor()
        cursor.execute(query)
        all_rows = cursor.fetchall()
        for row in all_rows:
            if row['name'].lower() == col_name:
                return True
    except sqlite3.Error as ex:
        logfunc(f"Query error, query={query} Error={str(ex)}")
        pass
    return False

def does_table_exist(db, table_name):
    '''Checks if a table with specified name exists in an sqlite db'''
    try:
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        cursor = db.execute(query)
        for row in cursor:
            return True
    except sqlite3.Error as ex:
        logfunc(f"Query error, query={query} Error={str(ex)}")
    return False


class GuiWindow:
    '''This only exists to hold window handle if script is run from GUI'''
    window_handle = None  # static variable

    @staticmethod
    def SetProgressBar(n, total):
        if GuiWindow.window_handle:
            progress_bar = GuiWindow.window_handle.nametowidget('!progressbar')
            progress_bar.config(value=n)


def logfunc(message=""):
    def redirect_logs(string):
        log_text.insert('end', string)
        log_text.see('end')
        log_text.update()

    if GuiWindow.window_handle:
        log_text = GuiWindow.window_handle.nametowidget('logs_frame.log_text')
        sys.stdout.write = redirect_logs

    with open(OutputParameters.screen_output_file_path, 'a', encoding='utf8') as a:
        print(message)
        a.write(message + '<br>' + OutputParameters.nl)


def logdevinfo(message=""):
    with open(OutputParameters.screen_output_file_path_devinfo, 'a', encoding='utf8') as b:
        b.write(message + '<br>' + OutputParameters.nl)


""" def deviceinfoin(ordes, kas, vas, sources): # unused function
    sources = str(sources)
    db = sqlite3.connect(reportfolderbase+'Device Info/di.db')
    cursor = db.cursor()
    datainsert = (ordes, kas, vas, sources,)
    cursor.execute('INSERT INTO devinf (ord, ka, va, source)  VALUES(?,?,?,?)', datainsert)
    db.commit() """


def html2csv(reportfolderbase):
    # List of items that take too long to convert or that shouldn't be converted
    itemstoignore = ['index.html',
                     'Distribution Keys.html',
                     'StrucMetadata.html',
                     'StrucMetadataCombined.html']

    if os.path.isdir(os.path.join(reportfolderbase, '_CSV Exports')):
        pass
    else:
        os.makedirs(os.path.join(reportfolderbase, '_CSV Exports'))
    for root, _, files in sorted(os.walk(reportfolderbase)):
        for file in files:
            if file.endswith(".html"):
                fullpath = (os.path.join(root, file))
                if file in itemstoignore:
                    pass
                else:
                    data = open(fullpath, 'r', encoding='utf8')
                    soup = BeautifulSoup(data, 'html.parser')
                    tables = soup.find_all("table")
                    data.close()

                    for table in tables:
                        output_rows = []
                        for table_row in table.findAll('tr'):
                            columns = table_row.findAll('td')
                            output_row = [column.text for column in columns]
                            output_rows.append(output_row)

                        file = (os.path.splitext(file)[0])
                        with codecs.open(os.path.join(reportfolderbase, '_CSV Exports', file + '.csv'), 'a',
                                         'utf-8-sig') as csvfile:
                            writer = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_ALL)
                            writer.writerows(output_rows)


def tsv(report_folder, data_headers, data_list, tsvname, source_file=None):
    report_folder = report_folder.rstrip('/')
    report_folder = report_folder.rstrip('\\')
    report_folder_base, tail = os.path.split(report_folder)
    tsv_report_folder = os.path.join(report_folder_base, '_TSV Exports')

    if os.path.isdir(tsv_report_folder):
        pass
    else:
        os.makedirs(tsv_report_folder)

    if os.path.exists(os.path.join(tsv_report_folder, tsvname + '.tsv')):
        with codecs.open(os.path.join(tsv_report_folder, tsvname + '.tsv'), 'a', 'utf-8-sig') as tsvfile:
            tsv_writer = csv.writer(tsvfile, delimiter='\t')
            for i in data_list:
                if source_file == None:
                    tsv_writer.writerow(i)
                else:
                    row_data = list(i)
                    row_data.append(source_file)
                    tsv_writer.writerow(tuple(row_data))
    else:
        with codecs.open(os.path.join(tsv_report_folder, tsvname + '.tsv'), 'a', 'utf-8-sig') as tsvfile:
            tsv_writer = csv.writer(tsvfile, delimiter='\t')
            if source_file == None:
                tsv_writer.writerow(data_headers)
                for i in data_list:
                    tsv_writer.writerow(i)
            else:
                data_hdr = list(data_headers)
                data_hdr.append("source file")
                tsv_writer.writerow(tuple(data_hdr))
                for i in data_list:
                    row_data = list(i)
                    row_data.append(source_file)
                    tsv_writer.writerow(tuple(row_data))


def timeline(report_folder, tlactivity, data_list, data_headers):
    report_folder = report_folder.rstrip('/')
    report_folder = report_folder.rstrip('\\')
    report_folder_base, tail = os.path.split(report_folder)
    tl_report_folder = os.path.join(report_folder_base, '_Timeline')

    if os.path.isdir(tl_report_folder):
        tldb = os.path.join(tl_report_folder, 'tl.db')
        db = sqlite3.connect(tldb)
        cursor = db.cursor()
        cursor.execute('''PRAGMA synchronous = EXTRA''')
        cursor.execute('''PRAGMA journal_mode = WAL''')
        db.commit()
    else:
        os.makedirs(tl_report_folder)
        # create database
        tldb = os.path.join(tl_report_folder, 'tl.db')
        db = sqlite3.connect(tldb, isolation_level = 'exclusive')
        cursor = db.cursor()
        cursor.execute(
            """
            CREATE TABLE data(key TEXT, activity TEXT, datalist TEXT)
            """
        )
        db.commit()

    for entry in data_list:
        entry = [str(field) for field in entry]
        
        data_dict = dict(zip(data_headers, entry))

        data_str = json.dumps(data_dict)
        cursor.executemany(
            "INSERT INTO data VALUES(?,?,?)", [(str(entry[0]), tlactivity, data_str)])

    db.commit()
    db.close()


def media_to_html(media_path, files_found, report_folder):
    """
    Show selected media files in the HTML report with proper relative pathing.

    Provide the media file unique path or identifier, search for it in the list of paths for the artifact.
    Place the responsive files in the folder for the artifact and generate realative paths for them in the report.

    :param str media_path: Can be a path or a string that is unique to selected to be shown image.
    :param list files_found: Paths that are a result of the regex executed when the artifact script is called.
    :param str report_folder: Folder within the report stucture that is automatically named as the artifact.
    :return: The relative path to the file in the report folder with proper HTML tags applied.
    :rtype: str
    """

    def media_path_filter(name):
        return media_path in name

    def relative_paths(source, splitter):
        splitted_a = source.split(splitter)
        for x in splitted_a:
            if 'LEAPP_Reports_' in x:
                report_folder = x

        splitted_b = source.split(report_folder)
        return '.' + splitted_b[1]

    platform = is_platform_windows()
    if platform:
        media_path = media_path.replace('/', '\\')
        splitter = '\\'
    else:
        splitter = '/'

    thumb = media_path
    for match in filter(media_path_filter, files_found):
        filename = os.path.basename(match)
        if filename.startswith('~') or filename.startswith('._'):
            continue

        dirs = os.path.dirname(report_folder)
        dirs = os.path.dirname(dirs)
        env_path = os.path.join(dirs, 'temp')
        if env_path in match:
            source = match
            source = relative_paths(source, splitter)
        else:
            path = os.path.dirname(match)
            dirname = os.path.basename(path)
            filename = Path(match)
            filename = filename.name
            locationfiles = Path(report_folder).joinpath(dirname)
            Path(f'{locationfiles}').mkdir(parents=True, exist_ok=True)
            shutil.copy2(match, locationfiles)
            source = Path(locationfiles, filename)
            source = relative_paths(str(source), splitter)

        mimetype = guess_mime(match)
        if mimetype == None:
            mimetype = ''

        if 'video' in mimetype:
            thumb = f'<video width="320" height="240" controls="controls"><source src="{source}" type="video/mp4" preload="none">Your browser does not support the video tag.</video>'
        elif 'image' in mimetype:
            thumb = f'<a href="{source}" target="_blank"><img src="{source}"width="300"></img></a>'
        elif 'audio' in mimetype:
            thumb = f'<audio controls><source src="{source}" type="audio/ogg"><source src="{source}" type="audio/mpeg">Your browser does not support the audio element.</audio>'
        else:
            thumb = f'<a href="{source}" target="_blank"> Link to {filename} file</>'
    return thumb


def kmlgen(report_folder, kmlactivity, data_list, data_headers):
    report_folder = report_folder.rstrip('/')
    report_folder = report_folder.rstrip('\\')
    report_folder_base, _ = os.path.split(report_folder)
    kml_report_folder = os.path.join(report_folder_base, '_KML Exports')

    if os.path.isdir(kml_report_folder):
        latlongdb = os.path.join(kml_report_folder, '_latlong.db')
        db = sqlite3.connect(latlongdb)
        cursor = db.cursor()
        cursor.execute('''PRAGMA synchronous = EXTRA''')
        cursor.execute('''PRAGMA journal_mode = WAL''')
        db.commit()
    else:
        os.makedirs(kml_report_folder)
        latlongdb = os.path.join(kml_report_folder, '_latlong.db')
        db = sqlite3.connect(latlongdb)
        cursor = db.cursor()
        cursor.execute(
            """
        CREATE TABLE data(key TEXT, latitude TEXT, longitude TEXT, activity TEXT)
        """
        )
        db.commit()

    kml = simplekml.Kml(open=1)

    for idx in range(len(data_list)):
        modifiedDict = dict(zip(data_headers, data_list[idx]))
        times = modifiedDict['Timestamp']
        lon = modifiedDict['Longitude']
        lat = modifiedDict['Latitude']
        if lat:
            pnt = kml.newpoint()
            pnt.name = times
            pnt.description = f"Timestamp: {times} - {kmlactivity}"
            pnt.coords = [(lon, lat)]
            cursor.execute("INSERT INTO data VALUES(?,?,?,?)", (times, lat, lon, kmlactivity))

    db.commit()
    db.close()
    kml.save(os.path.join(kml_report_folder, f'{kmlactivity}.kml'))


def abxread(in_path,
            multi_root):  # multi_root should be False under most circumstances. File with no root tags set the multi_root argument to True.

    """
    Copyright 2021-2022, CCL Forensics
    Permission is hereby granted, free of charge, to any person obtaining a copy of
    this software and associated documentation files (the "Software"), to deal in
    the Software without restriction, including without limitation the rights to
    use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
    of the Software, and to permit persons to whom the Software is furnished to do
    so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
    """

    import base64
    import enum
    import struct
    import typing
    import xml.etree.ElementTree as etree

    __version__ = "0.2.0"
    __description__ = "Python module to convert Android ABX binary XML files"
    __contact__ = "Alex Caithness"

    # See: base/core/java/com/android/internal/util/BinaryXmlSerializer.java

    class AbxDecodeError(Exception):
        pass

    class XmlType(enum.IntEnum):
        # These first constants are from: libcore/xml/src/main/java/org/xmlpull/v1/XmlPullParser.java
        # most of them are unused, but here for completeness
        START_DOCUMENT = 0
        END_DOCUMENT = 1
        START_TAG = 2
        END_TAG = 3
        TEXT = 4
        CDSECT = 5
        ENTITY_REF = 6
        IGNORABLE_WHITESPACE = 7
        PROCESSING_INSTRUCTION = 8
        COMMENT = 9
        DOCDECL = 10

        ATTRIBUTE = 15

    class DataType(enum.IntEnum):
        TYPE_NULL = 1 << 4
        TYPE_STRING = 2 << 4
        TYPE_STRING_INTERNED = 3 << 4
        TYPE_BYTES_HEX = 4 << 4
        TYPE_BYTES_BASE64 = 5 << 4
        TYPE_INT = 6 << 4
        TYPE_INT_HEX = 7 << 4
        TYPE_LONG = 8 << 4
        TYPE_LONG_HEX = 9 << 4
        TYPE_FLOAT = 10 << 4
        TYPE_DOUBLE = 11 << 4
        TYPE_BOOLEAN_TRUE = 12 << 4
        TYPE_BOOLEAN_FALSE = 13 << 4

    class AbxReader:
        MAGIC = b"ABX\x00"

        def _read_raw(self, length):
            buff = self._stream.read(length)
            if len(buff) < length:
                raise ValueError(f"couldn't read enough data at offset: {self._stream.tell() - len(buff)}")
            return buff

        def _read_byte(self):
            buff = self._read_raw(1)
            return buff[0]

        def _read_short(self):
            buff = self._read_raw(2)
            return struct.unpack(">h", buff)[0]

        def _read_int(self):
            buff = self._read_raw(4)
            return struct.unpack(">i", buff)[0]

        def _read_long(self):
            buff = self._read_raw(8)
            return struct.unpack(">q", buff)[0]

        def _read_float(self):
            buff = self._read_raw(4)
            return struct.unpack(">f", buff)[0]

        def _read_double(self):
            buff = self._read_raw(8)
            return struct.unpack(">d", buff)[0]

        def _read_string_raw(self):
            length = self._read_short()
            if length < 0:
                raise ValueError(f"Negative string length at offset {self._stream.tell() - 2}")
            buff = self._read_raw(length)
            return buff.decode("utf-8")

        def _read_interned_string(self):
            reference = self._read_short()
            if reference == -1:
                value = self._read_string_raw()
                self._interned_strings.append(value)
            else:
                value = self._interned_strings[reference]
            return value

        def __init__(self, stream: typing.BinaryIO):
            self._interned_strings = []
            self._stream = stream

        def read(self, *, is_multi_root=False):
            """
            Read the ABX file
            :param is_multi_root: some xml files on Android contain multiple root elements making reading them using a
            document model problematic. For these files, set is_multi_root to True and the output ElementTree will wrap
            the elements in a single "root" element.
            :return: ElementTree representation of the data.
            """
            magic = self._read_raw(len(AbxReader.MAGIC))
            if magic != AbxReader.MAGIC:
                raise ValueError(f"Invalid magic. Expected {AbxReader.MAGIC.hex()}; got: {magic.hex()}")

            # document_opened = False
            document_opened = True
            root_closed = False
            root = None
            element_stack = []  # because ElementTree doesn't support parents we maintain a stack
            if is_multi_root:
                root = etree.Element("root")
                element_stack.append(root)

            while True:
                # Read the token. This gives us the XML data type and the raw data type.
                token_raw = self._stream.read(1)
                if not token_raw:
                    break
                token = token_raw[0]

                data_start_offset = self._stream.tell()

                # The lower nibble gives us the XML type. This is mostly defined in XmlPullParser.java, other than
                # ATTRIBUTE which is from BinaryXmlSerializer
                xml_type = token & 0x0f
                if xml_type == XmlType.START_DOCUMENT:
                    # Since Android 13, START_DOCUMENT can essentially be considered no-op as it's implied by the reader to
                    # always be present (regardless of whether it is).
                    if token & 0xf0 != DataType.TYPE_NULL:
                        raise AbxDecodeError(
                            f"START_DOCUMENT with an invalid data type at offset {data_start_offset - 1}")
                    # if document_opened:
                    # if not root_closed:
                    #     raise AbxDecodeError(f"Unexpected START_DOCUMENT at offset {data_start_offset - 1}")
                    document_opened = True

                elif xml_type == XmlType.END_DOCUMENT:
                    if token & 0xf0 != DataType.TYPE_NULL:
                        raise AbxDecodeError(
                            f"END_DOCUMENT with an invalid data type at offset {data_start_offset - 1}")
                    if not (len(element_stack) == 0 or (len(element_stack) == 1 and is_multi_root)):
                        raise AbxDecodeError(f"END_DOCUMENT with unclosed elements at offset {data_start_offset - 1}")
                    if not document_opened:
                        raise AbxDecodeError(f"END_DOCUMENT before document started at offset {data_start_offset - 1}")
                    break

                elif xml_type == XmlType.START_TAG:
                    if token & 0xf0 != DataType.TYPE_STRING_INTERNED:
                        raise AbxDecodeError(f"START_TAG with an invalid data type at offset {data_start_offset - 1}")
                    if not document_opened:
                        raise AbxDecodeError(f"START_TAG before document started at offset {data_start_offset - 1}")
                    if root_closed:
                        raise AbxDecodeError(
                            f"START_TAG after root was closed started at offset {data_start_offset - 1}")

                    tag_name = self._read_interned_string()
                    if len(element_stack) == 0:
                        element = etree.Element(tag_name)
                        element_stack.append(element)
                        root = element
                    else:
                        element = etree.SubElement(element_stack[-1], tag_name)
                        element_stack.append(element)

                elif xml_type == XmlType.END_TAG:
                    if token & 0xf0 != DataType.TYPE_STRING_INTERNED:
                        raise AbxDecodeError(f"END_TAG with an invalid data type at offset {data_start_offset}")
                    if len(element_stack) == 0 or (is_multi_root and len(element_stack) == 1):
                        raise AbxDecodeError(f"END_TAG without any elements left at offset {data_start_offset}")

                    tag_name = self._read_interned_string()
                    if element_stack[-1].tag != tag_name:
                        raise AbxDecodeError(
                            f"Unexpected END_TAG name at {data_start_offset}. "
                            f"Expected: {element_stack[-1].tag}; got: {tag_name}")

                    last = element_stack.pop()
                    if len(element_stack) == 0:
                        root_closed = True
                        root = last
                elif xml_type == XmlType.TEXT:
                    value = self._read_string_raw()
                    if len(element_stack[-1]):
                        if len(value.strip()) == 0:  # layout whitespace can be safely discarded
                            continue
                        raise NotImplementedError("Can't deal with elements with mixed text and element contents")

                    if element_stack[-1].text is None:
                        element_stack[-1].text = value
                    else:
                        element_stack[-1].text += value
                elif xml_type == XmlType.ATTRIBUTE:
                    if len(element_stack) == 0 or (is_multi_root and len(element_stack) == 1):
                        raise AbxDecodeError(f"ATTRIBUTE without any elements left at offset {data_start_offset}")

                    attribute_name = self._read_interned_string()

                    if attribute_name in element_stack[-1].attrib:
                        raise AbxDecodeError(f"ATTRIBUTE name already in target element at offset {data_start_offset}")

                    data_type = token & 0xf0

                    if data_type == DataType.TYPE_NULL:
                        value = None  # remember to output xml as "null"
                    elif data_type == DataType.TYPE_BOOLEAN_TRUE:
                        # value = True  # remember to output xml as "true"
                        value = "true"
                    elif data_type == DataType.TYPE_BOOLEAN_FALSE:
                        # value = False  # remember to output xml as "false"
                        value = "false"
                    elif data_type == DataType.TYPE_INT:
                        value = self._read_int()
                    elif data_type == DataType.TYPE_INT_HEX:
                        value = f"{self._read_int():x}"  # don't do this conversion in dict
                    elif data_type == DataType.TYPE_LONG:
                        value = self._read_long()
                    elif data_type == DataType.TYPE_LONG_HEX:
                        value = f"{self._read_long():x}"  # don't do this conversion in dict
                    elif data_type == DataType.TYPE_FLOAT:
                        value = self._read_float()
                    elif data_type == DataType.TYPE_DOUBLE:
                        value = self._read_double()
                    elif data_type == DataType.TYPE_STRING:
                        value = self._read_string_raw()
                    elif data_type == DataType.TYPE_STRING_INTERNED:
                        value = self._read_interned_string()
                    elif data_type == DataType.TYPE_BYTES_HEX:
                        length = self._read_short()  # is this safe?
                        value = self._read_raw(length)
                        value = value.hex()  # skip this step for dict
                    elif data_type == DataType.TYPE_BYTES_BASE64:
                        length = self._read_short()  # is this safe?
                        value = self._read_raw(length)
                        value = base64.encodebytes(value).decode().strip()
                    else:
                        raise AbxDecodeError(f"Unexpected attribute datatype at offset: {data_start_offset}")

                    element_stack[-1].attrib[attribute_name] = str(value)
                else:
                    raise NotImplementedError(f"unexpected XML type: {xml_type}")

            if not (root_closed or (is_multi_root and len(element_stack) == 1 and element_stack[0] is root)):
                raise AbxDecodeError("Elements still in the stack when completing the document")

            if root is None:
                raise AbxDecodeError("Document was never assigned a root element")

            tree = etree.ElementTree(root)

            return tree

    with open(in_path, "rb") as f:
        reader = AbxReader(f)
        doc = reader.read(is_multi_root=multi_root)
        # print(etree.tostring(doc.getroot()).decode())
    return doc


def checkabx(in_path):
    MAGIC = b"ABX\x00"
    with open(in_path, "rb") as f:
        magic = f.read(4)

    if magic != MAGIC:
        return (False)
    else:
        return (True)


def get_raw_fields(latitude, longitude, c, conn):
    geolocator = Nominatim(user_agent="address-retrieval")
    location = geolocator.reverse(f"{latitude}, {longitude}")
    if location:
        raw_data = location.raw
        # check if raw_data["address"]["road"] exists
        not_present = False
        if "road" in raw_data["address"]:
            road = raw_data["address"]["road"]
        elif "hamlet" in raw_data["address"]:
            road = raw_data["address"]["hamlet"]
        else:
            road = 'Not Present'
            not_present = True

        if "city" in raw_data["address"]:
            city = raw_data["address"]["city"]
        elif "town" in raw_data["address"]:
            city = raw_data["address"]["town"]
        else:
            city = 'Not present'
            not_present = True
        if not not_present:
            store_raw_fields(latitude, longitude, road, city,
                             raw_data["address"]["postcode"], raw_data["address"]["country"], c, conn)
        # create a dict
        obtained_data = {"road": road, "city": city, "postcode": raw_data["address"]["postcode"],
                         "country": raw_data["address"]["country"]}
        return obtained_data
    else:
        print("Location not found.")


def store_raw_fields(latitude_value, longitude_value, road_value, city_value, postcode_value, country_value, c, conn):
    # Check if the entry is already present
    c.execute('''SELECT * FROM raw_fields WHERE latitude=? AND longitude=?''', (latitude_value, longitude_value))
    if c.fetchone() is None:
        # Insert a row of data
        c.execute('''INSERT INTO raw_fields (latitude, longitude, road, city, postcode, country) 
                      VALUES (?, ?, ?, ?, ?, ?)''',
                  (latitude_value, longitude_value, road_value, city_value, postcode_value, country_value))

        # Save (commit) the changes
        conn.commit()

# Function to check if the raw fields are already present in the database and return them if present or return None
def check_raw_fields(latitude, longitude, c):
    # Check if the entry is already present
    c.execute('''SELECT * FROM raw_fields WHERE latitude=? AND longitude=?''', (latitude, longitude))
    data = c.fetchone()
    # convert to dict
    return data

#Function to check if the user as internet connection to do the geocoding features
def check_internet_connection():
    try:
        geolocator = Nominatim(user_agent="check_internet_connection")
        location = geolocator.reverse("39.7495, 8.8077")  # Leiria coordinates
        logfunc("Internet connection is available.")
        return True
    except:
        logfunc("Internet connection is not available.")
        return False
    
    
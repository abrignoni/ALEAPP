import codecs
import csv
import datetime
import os
import pathlib
import re
import sqlite3
import sys
import simplekml
import magic
import shutil
from pathlib import Path

from bs4 import BeautifulSoup
from functools import lru_cache

os.path.basename = lru_cache(maxsize=None)(os.path.basename)

class OutputParameters:
    '''Defines the parameters that are common for '''
    # static parameters
    nl = '\n'
    screen_output_file_path = ''
    
    def __init__(self, output_folder):
        now = datetime.datetime.now()
        currenttime = str(now.strftime('%Y-%m-%d_%A_%H%M%S'))
        self.report_folder_base = os.path.join(output_folder, 'ALEAPP_Reports_' + currenttime) # aleapp , aleappGUI, ileap_artifacts, report.py
        self.temp_folder = os.path.join(self.report_folder_base, 'temp')
        OutputParameters.screen_output_file_path = os.path.join(self.report_folder_base, 'Script Logs', 'Screen Output.html')
        OutputParameters.screen_output_file_path_devinfo = os.path.join(self.report_folder_base, 'Script Logs', 'DeviceInfo.html')
        
        os.makedirs(os.path.join(self.report_folder_base, 'Script Logs'))
        os.makedirs(self.temp_folder)

def is_platform_windows():
    '''Returns True if running on Windows'''
    return os.name == 'nt'

def sanitize_file_path(filename, replacement_char='_'):
    '''
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
    return sqlite3.connect (f"file:{path}?mode=ro", uri=True)

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
        print(f"Query error, query={query} Error={str(ex)}")
        pass
    return False

def does_table_exist(db, table_name):
    '''Checks if a table with specified name exists in an sqlite db'''
    try:
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        cursor = db.execute(query)
        for row in cursor:
            return True
    except sqlite3Error as ex:
        logfunc(f"Query error, query={query} Error={str(ex)}")
    return False

class GuiWindow:
    '''This only exists to hold window handle if script is run from GUI'''
    window_handle = None # static variable 
    progress_bar_total = 0
    progress_bar_handle = None

    @staticmethod
    def SetProgressBar(n):
        if GuiWindow.progress_bar_handle:
            GuiWindow.progress_bar_handle.UpdateBar(n)

def logfunc(message=""):
    with open(OutputParameters.screen_output_file_path, 'a', encoding='utf8') as a:
        print(message)
        a.write(message + '<br>' + OutputParameters.nl)

    if GuiWindow.window_handle:
        GuiWindow.window_handle.refresh()
        
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
    #List of items that take too long to convert or that shouldn't be converted
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
                    soup = BeautifulSoup(data,'html.parser')
                    tables = soup.find_all("table")
                    data.close()

                    for table in tables:
                        output_rows = []
                        for table_row in table.findAll('tr'):

                            columns = table_row.findAll('td')
                            output_row = [column.text for column in columns]
                            output_rows.append(output_row)
        
                        file = (os.path.splitext(file)[0])
                        with codecs.open(os.path.join(reportfolderbase, '_CSV Exports',  file +'.csv'), 'a', 'utf-8-sig') as csvfile:
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

    if os.path.exists(os.path.join(tsv_report_folder, tsvname +'.tsv')):
        with codecs.open(os.path.join(tsv_report_folder, tsvname +'.tsv'), 'a', 'utf-8-sig') as tsvfile:
            tsv_writer = csv.writer(tsvfile, delimiter='\t')
            for i in data_list:
                if source_file == None:
                    tsv_writer.writerow(i)
                else:
                    row_data = list(i)
                    row_data.append(source_file)
                    tsv_writer.writerow(tuple(row_data))
    else:    
        with codecs.open(os.path.join(tsv_report_folder, tsvname +'.tsv'), 'a', 'utf-8-sig') as tsvfile:
            tsv_writer = csv.writer(tsvfile, delimiter='\t')
            if source_file ==  None:
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
    report_folder_base, _ = os.path.split(report_folder)
    tl_report_folder = os.path.join(report_folder_base, '_Timeline')

    tldb = os.path.join(tl_report_folder, 'tl.db')
    if os.path.isdir(tl_report_folder):    
        db = sqlite3.connect(tldb)
        cursor = db.cursor()
        cursor.execute('''PRAGMA synchronous = EXTRA''')
        cursor.execute('''PRAGMA journal_mode = WAL''')
    else:
        os.makedirs(tl_report_folder)
        #create database
        db = sqlite3.connect(tldb, isolation_level = 'exclusive')
        cursor = db.cursor()
        cursor.execute(
        """
        CREATE TABLE data(key TEXT, activity TEXT, datalist TEXT)
        """
            )
        db.commit()
    
    for idx in range(len(data_list)):    
        modifiedList = list(map(lambda x, y: x + ': ' +  str(y), data_headers, data_list[idx]))
        cursor.executemany("INSERT INTO data VALUES(?,?,?)", [(str(data_list[idx][0]), tlactivity, str(modifiedList))])
        
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
        return '.'+ splitted_b[1]
    
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
            
        mimetype = magic.from_file(match, mime = True)
        
        if 'video' in mimetype:
            thumb = f'<video width="320" height="240" controls="controls"><source src="{source}" type="video/mp4">Your browser does not support the video tag.</video>'
        elif 'image' in mimetype:
            thumb = f'<img src="{source}"width="300"></img>'
        elif 'audio' in mimetype:
            thumb = f'<audio controls><source src="{source}" type="audio/ogg"><source src="{source}" type="audio/mpeg">Your browser does not support the audio element.</audio>'
        else:
            thumb = f'<a href="{source}"> Link to {mimetype} </>'
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
    
def abxread(in_path, multi_root): #multi_root should be False under most circumstances. File with no root tags set the multi_root argument to True.
    
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
    
    
    __version__ = "0.1.0"
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
                
            document_opened = False
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
                    if token & 0xf0 != DataType.TYPE_NULL:
                        raise AbxDecodeError(
                            f"START_DOCUMENT with an invalid data type at offset {data_start_offset} - 1")
                    if document_opened:
                        raise AbxDecodeError(f"Unexpected START_DOCUMENT at offset {data_start_offset}")
                    document_opened = True
                    
                elif xml_type == XmlType.END_DOCUMENT:
                    if token & 0xf0 != DataType.TYPE_NULL:
                        raise AbxDecodeError(f"END_DOCUMENT with an invalid data type at offset {data_start_offset}")
                    if not (len(element_stack) == 0 or (len(element_stack) == 1 and is_multi_root)):
                        raise AbxDecodeError(f"END_DOCUMENT with unclosed elements at offset {data_start_offset}")
                    if not document_opened:
                        raise AbxDecodeError(f"END_DOCUMENT before document started at offset {data_start_offset}")
                    break
                
                elif xml_type == XmlType.START_TAG:
                    if token & 0xf0 != DataType.TYPE_STRING_INTERNED:
                        raise AbxDecodeError(f"START_TAG with an invalid data type at offset {data_start_offset}")
                    if not document_opened:
                        raise AbxDecodeError(f"START_TAG before document started at offset {data_start_offset}")
                    if root_closed:
                        raise AbxDecodeError(f"START_TAG after root was closed started at offset {data_start_offset}")
                        
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
                        value = True  # remember to output xml as "true"
                    elif data_type == DataType.TYPE_BOOLEAN_FALSE:
                        value = False  # remember to output xml as "false"
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
        #print(etree.tostring(doc.getroot()).decode())
    return doc

def checkabx(in_path):
    MAGIC = b"ABX\x00"
    with open(in_path, "rb") as f:
        magic = f.read(4)
        
    if magic != MAGIC:
        return(False)
    else:
        return(True)
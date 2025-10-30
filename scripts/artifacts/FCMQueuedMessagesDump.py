"""
Copyright 2022, CCL Forensics

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

import pathlib
import typing
import json
import base64
import blackboxprotobuf
import gzip

from scripts.ccl.ccl_android_fcm_queued_messages import FcmIterator
from scripts.artifact_report import ArtifactHtmlReport
import scripts.ilapfuncs


__version__ = "1.1"
__description__ = """Creates a summary report of all records from the fcm_queued_messages.ldb leveldb in 
com.google.android.gms"""
__contact__ = "Alex Caithness (research [at] cclsolutionsgroup.com)"


class SupportsContains(typing.Protocol):
    def __contains__(self, item) -> bool:
        ...


def get_fcm_dump(files_found, report_folder, seeker, wrap_text):
    # we only need the input data dirs not every matching file
    in_dirs = set(pathlib.Path(x).parent for x in files_found)
    package_tables = {}
    for in_db_dir in in_dirs:
        with FcmIterator(in_db_dir) as iterator:
            for record in iterator:
                if record.package not in package_tables:
                    package_tables[record.package] = []

                for k, v in record.key_values.items():
                    package_tables[record.package].append([
                        record.timestamp,
                        pathlib.Path(record.originating_file).name,
                        record.key,
                        k,
                        v
                    ])

        if not package_tables:
            scripts.ilapfuncs.logfunc("No FCM Notifications Found")

        for package, rows in package_tables.items():
            try:
                report = ArtifactHtmlReport(f"Firebase Cloud Messaging Queued Messages Dump: {package}")
                report_name = f"FCM-Dump-{package}"
                scripts.ilapfuncs.logfunc(report_name)
                report.start_artifact_report(report_folder, report_name)
                report.add_script()
                data_headers = ["Timestamp", "Originating File", "Record ID", "Key", "Value"]
                source_files = " ".join(str(x) for x in in_dirs)

                report.write_artifact_data_table(data_headers, rows, source_files)
                report.end_artifact_report()

                scripts.ilapfuncs.tsv(report_folder, data_headers, rows, report_name, source_files)
                scripts.ilapfuncs.timeline(report_folder, report_name, rows, data_headers)
                
                if package == 'com.verizon.messaging.vzmsgs':
                    process_fcm_dump_com_verizon_messaging_vzmsgs(report_folder, package, rows, source_files)
                
                if package == 'com.zhiliaoapp.musically':
                    process_fcm_dump_com_zhiliaoapp_musically(report_folder, package, rows, source_files)
                
                if package == 'com.instagram.android':
                    process_fcm_dump_com_instagram_android(report_folder, package, rows, source_files)
                
                if package == 'com.google.android.googlequicksearchbox':
                    process_fcm_dump_com_google_android_googlequicksearchbox(report_folder, package, rows, source_files)

            except Exception as e:
                scripts.ilapfuncs.logfunc(f"Error while processing FCM data for package: {package}")

def process_fcm_dump_com_verizon_messaging_vzmsgs(report_folder, package, rows, source_files):
    data_list_clean = []
    for data in rows:
        fecha = data[0]
        origfile = data[1]
        llave = data[3]
        datos = data[4]
        
        
        if llave == 'message':
            try:
                base64_string  = datos
                base64_bytes = base64_string.encode("ascii")
                sample_string_bytes = base64.b64decode(base64_bytes)
                sample_string = sample_string_bytes.decode("ascii")
                data_list_clean.append((fecha, origfile, llave, sample_string))
            except:
                data_list_clean.append((fecha, origfile, llave, datos))
        else:
            data_list_clean.append((fecha, origfile, llave, datos))
            
    if data_list_clean:
        report = ArtifactHtmlReport(f"Firebase Cloud Messaging Queued Messages Clean: {package}")
        report_name = f"FCM-Clean-Dump-{package}"
        report.start_artifact_report(report_folder, report_name)
        report.add_script()
        data_headers = ["Timestamp","Originating File", "Key", "Value"]
        
        report.write_artifact_data_table(data_headers, data_list_clean, source_files)
        report.end_artifact_report()
        
        scripts.ilapfuncs.tsv(report_folder, data_headers, data_list_clean, report_name, source_files)
        scripts.ilapfuncs.timeline(report_folder, report_name, data_list_clean, data_headers)

def process_fcm_dump_com_zhiliaoapp_musically(report_folder, package, rows, source_files):
    data_list_clean = []
    for data in rows:
        fecha = data[0]
        origfile = data[1]
        llave = data[3]
        datos = data[4]
        if llave == 'payload':
            try:
                datos = json.loads(datos)
            except:
                scripts.ilapfuncs.logfunc('Error reading json data')
            if (type(datos)) is dict:
                data_list_clean.append((fecha, origfile, datos['text'], datos['title']))
            
    if data_list_clean:
        report = ArtifactHtmlReport(f"Firebase Cloud Messaging Queued Messages Clean: {package}")
        report_name = f"FCM-Clean-Dump-{package}"
        report.start_artifact_report(report_folder, report_name)
        report.add_script()
        data_headers = ["Timestamp","Originating File", "Data", "Title"]
        
        report.write_artifact_data_table(data_headers, data_list_clean, source_files)
        report.end_artifact_report()
        
        scripts.ilapfuncs.tsv(report_folder, data_headers, data_list_clean, report_name, source_files)
        scripts.ilapfuncs.timeline(report_folder, report_name, data_list_clean, data_headers)

def process_fcm_dump_com_instagram_android(report_folder, package, rows, source_files):
    data_list_clean = []
    for data in rows:
        fecha = data[0]
        origfile = data[1]
        datos = data[4]
        try:
            datos = json.loads(datos)
        except:
            pass
        if (type(datos)) is dict:
            if 'collapse_key' in datos:
                data_list_clean.append((fecha, origfile, datos['collapse_key'], datos['m'], datos['s'], datos['u']))
            elif 'c' in datos:
                data_list_clean.append((fecha, origfile, datos['c'], datos['m'], datos['s'], datos['u']))
            
    if data_list_clean:
        report = ArtifactHtmlReport(f"Firebase Cloud Messaging Queued Messages Clean: {package}")
        report_name = f"FCM-Clean-Dump-{package}"
        report.start_artifact_report(report_folder, report_name)
        report.add_script()
        data_headers = ["Timestamp","Originating File", "Data", "M", "S", "U"]
        
        report.write_artifact_data_table(data_headers, data_list_clean, source_files)
        report.end_artifact_report()
        
        scripts.ilapfuncs.tsv(report_folder, data_headers, data_list_clean, report_name, source_files)
        scripts.ilapfuncs.timeline(report_folder, report_name, data_list_clean, data_headers)

def process_fcm_dump_com_google_android_googlequicksearchbox(report_folder, package, rows, source_files):
    data_list_clean = []
    for data in rows:
        fecha = data[0]
        origfile = data[1]
        llave = data[3]
        datos = data[4]
    
        if llave == 'casp':
            datos = base64.b64decode(datos)
            
            values, actual_types = blackboxprotobuf.decode_message(datos)
            
            values = (values['3'])
            try:
                smartspacecheck = values['3'].decode()
            except:
                smartspacecheck = values['3']
            
            if 'Smartspace' in smartspacecheck:
                values = values['14']['2']['13']['2']
                
                values = gzip.decompress(values)
                
                values, actual_types = blackboxprotobuf.decode_message(values)
                url = values['2']['14'].decode()
                lat = url.split('?')[1].split('lat=')[1].split('&')[0]
                lon = url.split('?')[1].split('lat=')[1].split('&')[1].split('lon=')[1]
                data_list_clean.append((fecha,lat,lon,url,origfile))
            
            tomorrow = values.get('12',None)
            if tomorrow is not None:
                tomorrow = values['12']['1']
                
                if isinstance(tomorrow, bytes):
                    tomorrow = tomorrow.decode()
            
                    if 'Tomorrow' in tomorrow:
                        try:
                            values = (values['14']['2']['20'])
                            values = gzip.decompress(values)
                            
                            typess = {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}, '2': {'type': 'int', 'name': ''}, '3': {'type': 'fixed64', 'name': ''}}, 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'fixed32', 'name': ''}, '3': {'type': 'fixed32', 'name': ''}}, 'name': ''}, '3': {'type': 'int', 'name': ''}, '4': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}, '2': {'type': 'int', 'name': ''}, '3': {'type': 'fixed64', 'name': ''}}, 'name': ''}, '2': {'type': 'message', 'message_typedef': {}, 'name': ''}, '6': {'type': 'int', 'name': ''}}, 'name': ''}, '5': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'bytes', 'name': ''}}, 'name': ''}, '6': {'type': 'message', 'message_typedef': {'3': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'fixed32', 'name': ''}, '3': {'type': 'fixed32', 'name': ''}}, 'name': ''}, '4': {'type': 'int', 'name': ''}}, 'name': ''}, '7': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '7': {'type': 'int', 'name': ''}, '8': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '7': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'double', 'name': ''}, '2': {'type': 'double', 'name': ''}, '3': {'type': 'bytes', 'name': ''}}, 'name': ''}, '3': {'type': 'bytes', 'name': ''}, '8': {'type': 'bytes', 'name': ''}, '11': {'type': 'bytes', 'name': ''}}, 'name': ''}}, 'name': ''}, '12': {'type': 'bytes', 'name': ''}, '15': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}, '16': {'type': 'int', 'name': ''}, '17': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}, '20': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '8': {'type': 'message', 'message_typedef': {'5': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '3': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'fixed64', 'name': ''}, '2': {'type': 'fixed64', 'name': ''}, '3': {'type': 'bytes', 'name': ''}}, 'name': ''}, '3': {'type': 'bytes', 'name': ''}, '8': {'type': 'bytes', 'name': ''}, '11': {'type': 'bytes', 'name': ''}}, 'name': ''}}, 'name': ''}, '3': {'type': 'int', 'name': ''}, '6': {'type': 'int', 'name': ''}, '10': {'type': 'message', 'message_typedef': {}, 'name': ''}, '11': {'type': 'message', 'message_typedef': {'5': {'type': 'message', 'message_typedef': {'2': {'type': 'int', 'name': ''}, '13': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'fixed32', 'name': ''}, '3': {'type': 'fixed32', 'name': ''}}, 'name': ''}}, 'name': ''}, '15': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '14': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}, '3': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}, '2': {'type': 'bytes', 'name': ''}, '3': {'type': 'bytes', 'name': ''}, '4': {'type': 'message', 'message_typedef': {'5': {'type': 'message', 'message_typedef': {'2': {'type': 'int', 'name': ''}, '13': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'fixed32', 'name': ''}, '3': {'type': 'fixed32', 'name': ''}}, 'name': ''}}, 'name': ''}, '15': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '5': {'type': 'message', 'message_typedef': {'5': {'type': 'message', 'message_typedef': {'2': {'type': 'int', 'name': ''}, '13': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'fixed32', 'name': ''}, '3': {'type': 'fixed32', 'name': ''}}, 'name': ''}}, 'name': ''}, '15': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '6': {'type': 'message', 'message_typedef': {'5': {'type': 'message', 'message_typedef': {'2': {'type': 'int', 'name': ''}, '13': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'fixed32', 'name': ''}, '3': {'type': 'fixed32', 'name': ''}}, 'name': ''}}, 'name': ''}, '15': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '7': {'type': 'message', 'message_typedef': {'5': {'type': 'message', 'message_typedef': {'2': {'type': 'int', 'name': ''}, '13': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'fixed32', 'name': ''}, '3': {'type': 'fixed32', 'name': ''}}, 'name': ''}}, 'name': ''}, '15': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '8': {'type': 'message', 'message_typedef': {'5': {'type': 'message', 'message_typedef': {'2': {'type': 'int', 'name': ''}, '13': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'fixed32', 'name': ''}, '3': {'type': 'fixed32', 'name': ''}}, 'name': ''}}, 'name': ''}, '15': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '9': {'type': 'message', 'message_typedef': {'5': {'type': 'message', 'message_typedef': {'2': {'type': 'int', 'name': ''}, '13': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'fixed32', 'name': ''}, '3': {'type': 'fixed32', 'name': ''}}, 'name': ''}}, 'name': ''}, '15': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '10': {'type': 'message', 'message_typedef': {'5': {'type': 'message', 'message_typedef': {'2': {'type': 'int', 'name': ''}, '13': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'fixed32', 'name': ''}, '3': {'type': 'fixed32', 'name': ''}}, 'name': ''}}, 'name': ''}, '15': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '18': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}
                            
                            values, typess = blackboxprotobuf.decode_message(values, typess)
                            
                            lat = values['1']['7']['1']['8']['7']['2']['1']
                            lon = values['1']['7']['1']['8']['7']['2']['2']
                            city = values['1']['7']['1']['8']['7']['2']['3'].decode()
                            data_list_clean.append((fecha,lat,lon,city,origfile))
                        except:
                            pass

    if data_list_clean:
        report = ArtifactHtmlReport(f"Firebase Cloud Messaging Queued Messages Geolocation: {package}")
        report_name = f"FCM-Clean-Dump-Geolocation-{package}"
        report.start_artifact_report(report_folder, report_name)
        report.add_script()
        data_headers = ["Timestamp", "Latitude", "Longitude", "URL or Location","Originating File"]
        
        report.write_artifact_data_table(data_headers, data_list_clean, source_files)
        report.end_artifact_report()
        
        scripts.ilapfuncs.tsv(report_folder, data_headers, data_list_clean, report_name, source_files)
        scripts.ilapfuncs.timeline(report_folder, report_name, data_list_clean, data_headers)
        scripts.ilapfuncs.kmlgen(report_folder, report_name, data_list_clean, data_headers)

__artifacts__ = {
        "FCM_Dump": (
                "Firebase Cloud Messaging",
                ('*/fcm_queued_messages.ldb/*'),
                get_fcm_dump)
}

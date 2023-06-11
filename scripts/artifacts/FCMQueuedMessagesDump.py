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

from scripts.ccl_android_fcm_queued_messages import FcmIterator
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
            report = ArtifactHtmlReport(f"Firebase Cloud Messaging Queued Messages Dump: {package}")
            report_name = f"FCM-Dump-{package}"
            report.start_artifact_report(report_folder, report_name)
            report.add_script()
            data_headers = ["Timestamp", "Originating File", "Record ID", "Key", "Value"]
            source_files = " ".join(str(x) for x in in_dirs)

            report.write_artifact_data_table(data_headers, rows, source_files)
            report.end_artifact_report()

            scripts.ilapfuncs.tsv(report_folder, data_headers, rows, report_name, source_files)
            scripts.ilapfuncs.timeline(report_folder, report_name, rows, data_headers)
            
            if package == 'com.zhiliaoapp.musically':
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
                            logfunc('Error reading json data')
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
            
            if package == 'com.instagram.android':
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
                        data_list_clean.append((fecha, origfile, datos['collapse_key'], datos['m'], datos['s'], datos['u']))
                        
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
            
            if package == 'com.google.android.googlequicksearchbox':
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
                        smartspacecheck = values['3'].decode()
                        
                        if 'Smartspace' in smartspacecheck:
                            values = values['14']['2']['13']['2']
                            
                            values = gzip.decompress(values)
                            
                            values, actual_types = blackboxprotobuf.decode_message(values)
                            url = values['2']['14'].decode()
                            lat = url.split('?')[1].split('lat=')[1].split('&')[0]
                            lon = url.split('?')[1].split('lat=')[1].split('&')[1].split('lon=')[1]
                            data_list_clean.append((fecha,lat,lon,url,origfile))
                
                if data_list_clean:
                    report = ArtifactHtmlReport(f"Firebase Cloud Messaging Queued Messages Geolocation: {package}")
                    report_name = f"FCM-Clean-Dump-Geolocation-{package}"
                    report.start_artifact_report(report_folder, report_name)
                    report.add_script()
                    data_headers = ["Timestamp", "Latitude", "Longitude", "URL","Originating File"]
                    
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
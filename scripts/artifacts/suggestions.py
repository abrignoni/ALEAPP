import os
import datetime
import xml.etree.ElementTree as ET
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def get_suggestions(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('suggestions.xml'):
            continue # Skip all other files
        
        data_list = []
        tree = ET.parse(file_found)
        root = tree.getroot()
        
        for elem in root:
            item = elem.attrib
            if item['name'] == 'com.android.settings.suggested.category.DEFERRED_SETUP_setup_time':
                timestamp = (datetime.datetime.utcfromtimestamp(int(item['value'])/1000).strftime('%Y-%m-%d %H:%M:%S'))
                data_list.append((timestamp, item['name']))
            if item['name'] == 'com.android.settings/com.android.settings.biometrics.fingerprint.FingerprintEnrollSuggestionActivity_setup_time':
                timestamp = (datetime.datetime.utcfromtimestamp(int(item['value'])/1000).strftime('%Y-%m-%d %H:%M:%S'))
                data_list.append((timestamp, item['name']))
            if item['name'] == 'com.google.android.setupwizard/com.google.android.setupwizard.deferred.DeferredSettingsSuggestionActivity_setup_time':
                timestamp = (datetime.datetime.utcfromtimestamp(int(item['value'])/1000).strftime('%Y-%m-%d %H:%M:%S'))
                data_list.append((timestamp, item['name']))
        
        if data_list:
            report = ArtifactHtmlReport('Suggestions.xml')
            report.start_artifact_report(report_folder, 'Suggestions.xml')
            report.add_script()
            data_headers = ('Timestamp','Name')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Suggestions XML data'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Suggestions XML data'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Suggestions XML data available')

__artifacts__ = {
        "suggestions": (
                "Wipe & Setup",
                ('*/com.google.android.settings.intelligence/shared_prefs/suggestions.xml'),
                get_suggestions)
}
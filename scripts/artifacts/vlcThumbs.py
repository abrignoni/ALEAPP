import os
import shutil

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import timeline, tsv, is_platform_windows, open_sqlite_db_readonly, media_to_html


def get_vlcThumbs(files_found, report_folder, seeker, wrap_text):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        
        data_file_real_path = file_found
        shutil.copy2(data_file_real_path, report_folder)
        data_file_name = os.path.basename(data_file_real_path)
        thumb = f'<img src="{report_folder}/{data_file_name}"></img>'
        
        data_list.append((data_file_name, thumb))
    
    path_to_files = os.path.dirname(data_file_real_path)
    
    description = 'VLC Thumbnails'
    report = ArtifactHtmlReport('VLC Thumbnails')
    report.start_artifact_report(report_folder, 'VLC Thumbnails', description)
    report.add_script()
    data_headers = ('Filename', 'Thumbnail' )
    report.write_artifact_data_table(data_headers, data_list, path_to_files, html_escape=False)
    report.end_artifact_report()
    
    tsvname = 'VLC Thumbnails'
    tsv(report_folder, data_headers, data_list, tsvname)
    
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('vlc_media.db'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            datetime(last_played_date, 'unixepoch' ),
            datetime(insertion_date, 'unixepoch' ),
            id_media,
            filename,
            play_count,
            is_favorite
            FROM media
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            
            if usageentries > 0:
                for row in all_rows:
                    
                    thumb = media_to_html(f'medialib/{row[2]}.jpg', files_found, report_folder)
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],thumb))
                
                report = ArtifactHtmlReport('VLC Thumbnail Data')
                report.start_artifact_report(report_folder, 'VLC Thumbnail Data')
                report.add_script()
                data_headers = ('Last Played', 'Insertion Date','ID Media', 'Filename', 'Play Count', 'Is favorite', 'Thumbnail') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                report.write_artifact_data_table(data_headers, data_list, path_to_files, html_no_escape=['Thumbnail'])
                report.end_artifact_report()
                
                tsvname = f'VLC Thumbnail Data'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'VLC Thumbnail Data'
                timeline(report_folder, tlactivity, data_list, data_headers)
    
__artifacts__ = {
        "VLC Thumbs": (
                "VLC",
                ('*/org.videolan.vlc/files/medialib/*.jpg', '*/org.videolan.vlc/app_db/vlc_media.db*'),
                get_vlcThumbs)
}

        
        
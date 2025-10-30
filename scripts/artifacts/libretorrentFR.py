import sqlite3
import textwrap
import bencoding
from datetime import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, kmlgen

def get_libretorrentFR(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_name = str(file_found)
        if file_found.endswith('libretorrent.db'):
            break # Skip all other files
    
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    * from FastResume
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        
        for row in all_rows:
            pass
            torrentihash = row[0]
            encoded_data = row[1]
            decodedDict = bencoding.bdecode(encoded_data)
            
            torrentihas = torrentname = spath = iname = tdown = tup = aggf = agg = ''
            for key,value in decodedDict.items():
                #print(key,value)
                if key == b'info':
                    for ikey, ivalue in value.items():
                        if ikey == b'piece length':
                            pass
                        if ikey == b'name':
                            torrentname = (ivalue.decode())
                        if ikey == b'files':
                            for files in ivalue:
                                for iikey, iivalue in files.items():
                                    if iikey == b'length':
                                        lenghtf = (iivalue)
                                    if iikey == b'path':
                                        pathf = (iivalue[0].decode())
                                aggf = aggf + f'Lenght: {lenghtf} Path: {pathf} <br>'
                elif key == b'trackers':
                    pass
                elif key == b'pieces':
                    pass
                elif key == b'peers':
                    pass
                elif key == b'banned_peers':
                    pass
                elif key == b'banned_peers6':
                    pass
                elif key == b'peers6':
                    pass
                elif key == b'mapped_files':
                    pass
                elif key == b'piece_priority':
                    pass
                elif key == b'file_priority':
                    pass
                elif key == b'info-hash':
                    pass #need to use bencode tools to reverse engineer the number
                elif key == b'info-hash2':
                    pass
                elif key == b'save_path':
                    spath = value.decode()
                elif key == b'name':
                    iname = value.decode()
                elif key == b'total_downloaded':
                    tdown = value
                elif key == b'total_uploaded':
                    tup = value
                else:
                    if (isinstance(value, int)):
                        value = value
                    elif (isinstance(value, list)):
                        value = str(value)
                    else:
                        value = value.decode()
                    agg = agg + f'{key.decode()}: {value} <br>'
                    
            data_list.append((torrentihash,torrentname,spath,iname,tdown,tup,aggf,agg))
        
        report = ArtifactHtmlReport('Libre Torrent - Fast Resume')
        report.start_artifact_report(report_folder, 'Libre Torrent - Fast Resume')
        report.add_script()
        data_headers = ('Torrent InfoHash','Torrent Name','Save Path','Name','Total Downloaded','Total Uploaded','Length - Path','Key - Value')
        report.write_artifact_data_table(data_headers, data_list, file_found,html_escape=False)
        report.end_artifact_report()
        
        tsvname = f'Libre Torrent - Fast Resume'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('No Libre Torrents Fast Resume data available')
        
    db.close()

__artifacts__ = {
        "LibretorrentFR": (
                "Libre Torrent",
                ('*/data/com.houseoflife.bitlord/databases/libretorrent.db*','*/libretorrent.db*'),
                get_libretorrentFR)
}

import codecs
import csv
import datetime
import os
import pathlib
import sqlite3
import sys

from bs4 import BeautifulSoup

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

        os.makedirs(os.path.join(self.report_folder_base, 'Script Logs'))
        os.makedirs(self.temp_folder)

def is_platform_windows():
    '''Returns True if running on Windows'''
    return os.name == 'nt'

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
    for root, dirs, files in sorted(os.walk(reportfolderbase)):
        for file in files:
            if file.endswith(".html"):
                fullpath = (os.path.join(root, file))
                head, tail = os.path.split(fullpath)
                if file in itemstoignore:
                    pass
                else:
                    data = open(fullpath, 'r', encoding='utf8')
                    soup=BeautifulSoup(data,'html.parser')
                    tables = soup.find_all("table")
                    data.close()
                    output_final_rows=[]

                    for table in tables:
                        output_rows = []
                        for table_row in table.findAll('tr'):

                            columns = table_row.findAll('td')
                            output_row = []
                            for column in columns:
                                    output_row.append(column.text)
                            output_rows.append(output_row)
        
                        file = (os.path.splitext(file)[0])
                        with codecs.open(os.path.join(reportfolderbase, '_CSV Exports',  file +'.csv'), 'a', 'utf-8-sig') as csvfile:
                            writer = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_ALL)
                            writer.writerows(output_rows)

def tsv(report_folder, data_headers, data_list, tsvname):
    report_folder = report_folder.rstrip('/')
    report_folder = report_folder.rstrip('\\')
    report_folder_base, tail = os.path.split(report_folder)
    tsv_report_folder = os.path.join(report_folder_base, '_TSV Exports')
    
    if os.path.isdir(tsv_report_folder):
        pass
    else:
        os.makedirs(tsv_report_folder)
    
    with codecs.open(os.path.join(tsv_report_folder + '/' + tsvname +'.tsv'), 'a', 'utf-8-sig') as tsvfile:
        tsv_writer = csv.writer(tsvfile, delimiter='\t')
        tsv_writer.writerow(data_headers)
        for i in data_list:
            tsv_writer.writerow(i)

def timeline(report_folder, tlactivity, data_list):
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
    else:
        os.makedirs(tl_report_folder)
        #create database
        tldb = os.path.join(tl_report_folder, 'tl.db')
        db = sqlite3.connect(tldb, isolation_level = 'exclusive')
        cursor = db.cursor()
        cursor.execute(
        """
        CREATE TABLE data(key TEXT, activity TEXT, datalist TEXT)
        """
            )
        db.commit()
    
    for i in data_list:
        #datainsert = (str(i[0]), tlactivity, str(i),)
        cursor.executemany("INSERT INTO data VALUES(?,?,?)", [(str(i[0]), tlactivity, str(i))])
    db.commit()
    db.close()
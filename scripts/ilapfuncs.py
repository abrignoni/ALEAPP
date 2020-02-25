import csv
import datetime
import os
import pathlib
import sys

from bs4 import BeautifulSoup

nl = '\n' 
now = datetime.datetime.now()
currenttime = str(now.strftime('%Y-%m-%d_%A_%H%M%S'))
reportfolderbase = './ALEAPP_Reports_' + currenttime + '/'
base = '/ALEAPP_Reports_' + currenttime + '/'
temp = reportfolderbase + 'temp/'

def is_platform_windows():
    '''Returns True if running on Windows'''
    return os.name == 'nt'

def logfunc(message=""):
    if pathlib.Path(reportfolderbase+'Script Logs/Screen Output.html').is_file():
        with open(reportfolderbase+'Script Logs/Screen Output.html', 'a', encoding='utf8') as a:
            print(message)
            a.write(message+'<br>')
    else:
        with open(reportfolderbase+'Script Logs/Screen Output.html', 'a', encoding='utf8') as a:
            print(message)
            a.write(message+'<br>')
    
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
                    
    if os.path.isdir(reportfolderbase+'_CSV Exports/'):
        pass
    else:
        os.makedirs(reportfolderbase+'_CSV Exports/')
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
                        with codecs.open(reportfolderbase+'_CSV Exports/'+file+'.csv', 'a', 'utf-8-sig') as csvfile:
                            writer = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_ALL)
                            writer.writerows(output_rows)

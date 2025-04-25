# Kijiji Local Recent Searches
# Author:  Terry Chabot (Krypterry)
# Version: 1.0.0
# Kijiji App Version Tested: v17.5.0b172 (2022-05-06)
# Requirements:  None
#
#   Description:
#   Obtains search terms entered by the local user, potentially including GPS location.
#
#   Additional Info:
#       Kijiji.ca is a Canadian online classified advertising website and part of eBay Classifieds Group, with over 16 million unique visitors per month.
#
#       Kijiji, May 2022 <https://help.kijiji.ca/helpdesk/basics/what-is-kijiji>
#       Wikipedia - The Free Encyclopedia, May 2022, <https://en.wikipedia.org/wiki/Kijiji>
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, open_sqlite_db_readonly, does_table_exist_in_db

recent_searches_query = \
'''
    SELECT 
        datetime([time]/1000, 'UNIXEPOCH') [DateSearched],
        keyword,
        thumbnail,
        address,
        latitude,
        longitude,
        distance,
        ad_type,
        price_type,
        CASE min_price
            WHEN -1 THEN ''
            ELSE min_price
        END min_price,
        CASE max_price
            WHEN -1 THEN ''
            ELSE max_price
        END max_price
    FROM recent_searches
    ORDER BY TIME ASC;
'''

def get_kijijiRecentSearches(files_found, report_folder, seeker, wrap_text):
    file_found = str(files_found[0])
    logfunc(f'Database file {file_found} is being interrogated...')
    db = open_sqlite_db_readonly(file_found)
    db.row_factory = sqlite3.Row # For fetching columns by name
    tabCheck = does_table_exist_in_db(file_found, 'recent_searches')
    if tabCheck == False:
        logfunc('The recent_searches table was not found in the database!')
        return False

    cursor = db.cursor()
    cursor.execute(recent_searches_query)
    all_rows = cursor.fetchall()
    if len(all_rows) > 0:
        report = ArtifactHtmlReport('Kijiji Recent Searches')
        report.start_artifact_report(report_folder, 'Kijiji Recent Searches')
        report.add_script()

        data_headers = ('Date', 'Search Keyword', 'Thumbnail', 'Address', 'Latitude', 'Longitude', 'Search Distance', 'Ad Type', 'Price Type', 'Min Price', 'Max Price')
        data_list = []
        for row in all_rows:
            data_list.append((row['DateSearched'], row['keyword'], row['thumbnail'], row['address'], 
                              row['latitude'], row['longitude'], row['distance'], row['ad_type'], 
                              row['price_type'], row['min_price'], row['max_price']))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Kijiji Recent Searches'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No Kijiji Recent Search data was found.')

    db.close()

__artifacts__ = {
    "kijijiRecentSearches": (
        "Kijiji Recent Searches",
        ('*/com.ebay.kijiji.ca/databases/searches.*'),
        get_kijijiRecentSearches)
}
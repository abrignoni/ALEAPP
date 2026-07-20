# pylint: disable=W0718
__artifacts_v2__ = {
    "get_chrome": {
        "name": "Web History",
        "description": "Parses Web History from Chromium based browsers",
        "author": "",
        "creation_date": "2020-03-19",
        "last_update_date": "2020-03-19",
        "requirements": "none",
        "category": "Chromium",
        "notes": "",
        "paths": ('*/app_chrome/Default/History*', '*/app_sbrowser/Default/History*', '*/app_opera/History*', '*/app_webview/Default/History*'),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "anne_a15": "Android 15 | com.android.chrome vc 733915533, com.sec.android.app.sbrowser vc 1280509502 | 94 rows",
            "galaxys10_a10": "Android 10 | com.android.chrome vc 438910534 | 191 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.chrome vc 782711433, com.brave.browser vc 429117204, com.sec.android.app.sbrowser vc 1300067502 | 20 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.chrome vc 733920733 | 46 rows",
            "pixel7a_a14": "Android 14 | 76 rows",
            "samsunga53_a14": "Android 14 | com.android.chrome vc 744417133, com.sec.android.app.sbrowser vc 1290059502 | 132 rows",
            "samsungs20_a13": "Android 13 | com.android.chrome vc 749919233, com.brave.browser vc 428414124, com.microsoft.emmx vc 365012523 | 65 rows",
            "sharon_a14": "Android 14 | com.android.chrome vc 653310333, com.sec.android.app.sbrowser vc 1260103502 | 137 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.chrome vc 573513033, com.brave.browser vc 415212624 | 118 rows",
            "userb2_a13": "Android 13 | com.android.chrome vc 677808133 | 62 rows",
        },
    },
    "get_chromeWebVisits": {
        "name": "Web Visits",
        "description": "Parses Web Visits from Chromium based browsers",
        "author": "",
        "creation_date": "2020-03-19",
        "last_update_date": "2020-03-19",
        "requirements": "none",
        "category": "Chromium",
        "notes": "",
        "paths": ('*/app_chrome/Default/History*', '*/app_sbrowser/Default/History*', '*/app_opera/History*', '*/app_webview/Default/History*'),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "anne_a15": "Android 15 | com.android.chrome vc 733915533, com.sec.android.app.sbrowser vc 1280509502 | 127 rows",
            "galaxys10_a10": "Android 10 | com.android.chrome vc 438910534 | 291 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.chrome vc 782711433, com.brave.browser vc 429117204, com.sec.android.app.sbrowser vc 1300067502 | 39 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.chrome vc 733920733 | 71 rows",
            "pixel7a_a14": "Android 14 | 89 rows",
            "samsunga53_a14": "Android 14 | com.android.chrome vc 744417133, com.sec.android.app.sbrowser vc 1290059502 | 174 rows",
            "samsungs20_a13": "Android 13 | com.android.chrome vc 749919233, com.brave.browser vc 428414124, com.microsoft.emmx vc 365012523 | 86 rows",
            "sharon_a14": "Android 14 | com.android.chrome vc 653310333, com.sec.android.app.sbrowser vc 1260103502 | 198 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.chrome vc 573513033, com.brave.browser vc 415212624 | 207 rows",
            "userb2_a13": "Android 13 | com.android.chrome vc 677808133 | 76 rows",
        },
    },
    "get_chromeSearchTerms": {
        "name": "Search Terms",
        "description": "Parses Search Terms from Chromium based browsers",
        "author": "",
        "creation_date": "2020-03-19",
        "last_update_date": "2020-03-19",
        "requirements": "none",
        "category": "Chromium",
        "notes": "",
        "paths": ('*/app_chrome/Default/History*', '*/app_sbrowser/Default/History*', '*/app_opera/History*', '*/app_webview/Default/History*'),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "anne_a15": "Android 15 | com.android.chrome vc 733915533, com.sec.android.app.sbrowser vc 1280509502 | 44 rows",
            "galaxys10_a10": "Android 10 | com.android.chrome vc 438910534 | 20 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.chrome vc 782711433, com.brave.browser vc 429117204, com.sec.android.app.sbrowser vc 1300067502 | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.android.chrome vc 733920733 | 3 rows",
            "pixel7a_a14": "Android 14 | 7 rows",
            "samsunga53_a14": "Android 14 | com.android.chrome vc 744417133, com.sec.android.app.sbrowser vc 1290059502 | 39 rows",
            "samsungs20_a13": "Android 13 | com.android.chrome vc 749919233, com.brave.browser vc 428414124, com.microsoft.emmx vc 365012523 | 18 rows",
            "sharon_a14": "Android 14 | com.android.chrome vc 653310333, com.sec.android.app.sbrowser vc 1260103502 | 18 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.chrome vc 573513033, com.brave.browser vc 415212624 | 37 rows",
            "userb2_a13": "Android 13 | com.android.chrome vc 677808133 | 16 rows",
        },
    },
    "get_chromeDownloads": {
        "name": "Downloads",
        "description": "Parses Downloads from Chromium based browsers",
        "author": "",
        "creation_date": "2020-03-19",
        "last_update_date": "2020-03-19",
        "requirements": "none",
        "category": "Chromium",
        "notes": "",
        "paths": ('*/app_chrome/Default/History*', '*/app_sbrowser/Default/History*', '*/app_opera/History*', '*/app_webview/Default/History*'),
        "output_types": "standard",
        "artifact_icon": "download",
        "sample_data": {
            "anne_a15": "Android 15 | com.android.chrome vc 733915533, com.sec.android.app.sbrowser vc 1280509502 | 0 rows",
            "galaxys10_a10": "Android 10 | com.android.chrome vc 438910534 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.chrome vc 782711433, com.brave.browser vc 429117204, com.sec.android.app.sbrowser vc 1300067502 | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.android.chrome vc 733920733 | 0 rows",
            "pixel7a_a14": "Android 14 | 4 rows",
            "samsunga53_a14": "Android 14 | com.android.chrome vc 744417133, com.sec.android.app.sbrowser vc 1290059502 | 0 rows",
            "samsungs20_a13": "Android 13 | com.android.chrome vc 749919233, com.brave.browser vc 428414124, com.microsoft.emmx vc 365012523 | 2 rows",
            "sharon_a14": "Android 14 | com.android.chrome vc 653310333, com.sec.android.app.sbrowser vc 1260103502 | 108 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.chrome vc 573513033, com.brave.browser vc 415212624 | 1 row",
            "userb2_a13": "Android 13 | com.android.chrome vc 677808133 | 2 rows",
        },
    },
    "get_chromeKeywordSearchTerms": {
        "name": "Keyword Search Terms",
        "description": "Parses Keyword Search Terms from Chromium based browsers",
        "author": "",
        "creation_date": "2020-03-19",
        "last_update_date": "2020-03-19",
        "requirements": "none",
        "category": "Chromium",
        "notes": "",
        "paths": ('*/app_chrome/Default/History*', '*/app_sbrowser/Default/History*', '*/app_opera/History*', '*/app_webview/Default/History*'),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "anne_a15": "Android 15 | com.android.chrome vc 733915533, com.sec.android.app.sbrowser vc 1280509502 | 88 rows",
            "galaxys10_a10": "Android 10 | com.android.chrome vc 438910534 | 15 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.chrome vc 782711433, com.brave.browser vc 429117204, com.sec.android.app.sbrowser vc 1300067502 | 4 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.chrome vc 733920733 | 3 rows",
            "pixel7a_a14": "Android 14 | 7 rows",
            "samsunga53_a14": "Android 14 | com.android.chrome vc 744417133, com.sec.android.app.sbrowser vc 1290059502 | 48 rows",
            "samsungs20_a13": "Android 13 | com.android.chrome vc 749919233, com.brave.browser vc 428414124, com.microsoft.emmx vc 365012523 | 18 rows",
            "sharon_a14": "Android 14 | com.android.chrome vc 653310333, com.sec.android.app.sbrowser vc 1260103502 | 23 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.chrome vc 573513033, com.brave.browser vc 415212624 | 44 rows",
            "userb2_a13": "Android 13 | com.android.chrome vc 677808133 | 16 rows",
        },
    }
}

import datetime
import os
import re
import urllib.parse

from scripts.ilapfuncs import logfunc, open_sqlite_db_readonly, does_column_exist_in_db, artifact_processor


def get_browser_name(file_name):

    if 'brave' in file_name.lower():
        return 'Brave'
    elif 'microsoft' in file_name.lower():
        return 'Edge'
    elif 'opera' in file_name.lower():
        return 'Opera'
    elif 'android.chrome' in file_name.lower():
        return 'Chrome'
    elif 'app_webview' in file_name:
        try:
            result = re.search('.*/(.*)/app_webview/Default.*', file_name)
            return result.group(1)
        except Exception:
            return 'Unknown'
    else:
        return 'Unknown'


def _webkit_to_utc(value):
    '''Chromium/WebKit timestamp = microseconds since 1601-01-01 UTC'''
    if value in (None, 0, ''):
        return ''
    return datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(microseconds=int(value))


def _history_files(files_found):
    '''Yield (file_found, browser_name) for the real History DBs, skipping journals/mirrors.'''
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'History':  # skip -journal and other files
            continue
        if file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue  # Skip mirror, it should be duplicate data
        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'
        yield file_found, browser_name


@artifact_processor
def get_chrome(context):
    files_found = context.get_files_found()
    all_data = []
    data_headers = ['Last Visit Time', 'URL', 'Title', 'Visit Count', 'Typed Count', 'ID', 'Hidden']
    lava_data_headers = data_headers.copy()
    lava_data_headers[0] = (lava_data_headers[0], 'datetime')
    all_data_headers = lava_data_headers + ['Browser Name']
    report_file = 'Unknown'

    for file_found, browser_name in _history_files(files_found):
        report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT last_visit_time, url, title, visit_count, typed_count, id,
        CASE hidden WHEN 0 THEN '' WHEN 1 THEN 'Yes' END as Hidden
        FROM urls
        ''')
        rows = cursor.fetchall()
        db.close()

        data_list = [(_webkit_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6]) for r in rows]
        if data_list:
            all_data.extend([row + (browser_name,) for row in data_list])
        else:
            logfunc(f'No {browser_name} - Web History data available')

    return all_data_headers, all_data, report_file


@artifact_processor
def get_chromeWebVisits(context):
    files_found = context.get_files_found()
    all_data = []
    data_headers = ['Visit Timestamp', 'URL', 'Title', 'Duration', 'Transition Type', 'Qualifier(s)', 'From Visit URL']
    lava_data_headers = data_headers.copy()
    lava_data_headers[0] = (lava_data_headers[0], 'datetime')
    all_data_headers = lava_data_headers + ['Browser Name']
    report_file = 'Unknown'

    for file_found, browser_name in _history_files(files_found):
        report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        visits.visit_time,
        urls.url,
        urls.title,
        CASE visits.visit_duration
            WHEN 0 THEN ''
            ELSE strftime('%H:%M:%f', visits.visit_duration / 1000000.000,'unixepoch')
        END as Duration,
        CASE visits.transition & 0xff
            WHEN 0 THEN 'LINK'
            WHEN 1 THEN 'TYPED'
            WHEN 2 THEN 'AUTO_BOOKMARK'
            WHEN 3 THEN 'AUTO_SUBFRAME'
            WHEN 4 THEN 'MANUAL_SUBFRAME'
            WHEN 5 THEN 'GENERATED'
            WHEN 6 THEN 'START_PAGE'
            WHEN 7 THEN 'FORM_SUBMIT'
            WHEN 8 THEN 'RELOAD'
            WHEN 9 THEN 'KEYWORD'
            WHEN 10 THEN 'KEYWORD_GENERATED'
            ELSE NULL
        END AS CoreTransitionType,
        trim((CASE WHEN visits.transition & 0x00800000 THEN 'BLOCKED, ' ELSE '' END ||
        CASE WHEN visits.transition & 0x01000000 THEN 'FORWARD_BACK, ' ELSE '' END ||
        CASE WHEN visits.transition & 0x02000000 THEN 'FROM_ADDRESS_BAR, ' ELSE '' END ||
        CASE WHEN visits.transition & 0x04000000 THEN 'HOME_PAGE, ' ELSE '' END ||
        CASE WHEN visits.transition & 0x08000000 THEN 'FROM_API, ' ELSE '' END ||
        CASE WHEN visits.transition & 0x10000000 THEN 'CHAIN_START, ' ELSE '' END ||
        CASE WHEN visits.transition & 0x20000000 THEN 'CHAIN_END, ' ELSE '' END ||
        CASE WHEN visits.transition & 0x40000000 THEN 'CLIENT_REDIRECT, ' ELSE '' END ||
        CASE WHEN visits.transition & 0x80000000 THEN 'SERVER_REDIRECT, ' ELSE '' END ||
        CASE WHEN visits.transition & 0xC0000000 THEN 'IS_REDIRECT_MASK, ' ELSE '' END),', ')
        AS Qualifiers,
        Query2.url AS FromURL
        FROM visits
        LEFT JOIN urls ON visits.url = urls.id
        LEFT JOIN (SELECT urls.url,urls.title,visits.visit_time,visits.id FROM visits LEFT JOIN urls ON visits.url = urls.id) Query2 ON visits.from_visit = Query2.id
        ''')
        rows = cursor.fetchall()
        db.close()

        data_list = [(_webkit_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6]) for r in rows]
        if data_list:
            all_data.extend([row + (browser_name,) for row in data_list])
        else:
            logfunc(f'No {browser_name} - Web Visits data available')

    return all_data_headers, all_data, report_file


@artifact_processor
def get_chromeSearchTerms(context):
    files_found = context.get_files_found()
    all_data = []
    data_headers = ['Last Visit Time', 'Search Term', 'URL', 'Title', 'Visit Count']
    lava_data_headers = data_headers.copy()
    lava_data_headers[0] = (lava_data_headers[0], 'datetime')
    all_data_headers = lava_data_headers + ['Browser Name']
    report_file = 'Unknown'

    for file_found, browser_name in _history_files(files_found):
        report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT url, title, visit_count, last_visit_time
        FROM urls
        WHERE url like '%search?q=%'
        ''')
        rows = cursor.fetchall()
        db.close()

        data_list = []
        for r in rows:
            search = r[0].split('search?q=')[1].split('&')[0]
            search = urllib.parse.unquote(search).replace('+', ' ')
            data_list.append((_webkit_to_utc(r[3]), search, r[0], r[1], r[2]))

        if data_list:
            all_data.extend([row + (browser_name,) for row in data_list])
        else:
            logfunc(f'No {browser_name} - Search Terms data available')

    return all_data_headers, all_data, report_file


@artifact_processor
def get_chromeDownloads(context):
    files_found = context.get_files_found()
    all_data = []
    data_headers = ['Start Time', 'End Time', 'Last Access Time', 'URL', 'Target Path', 'State',
                    'Danger Type', 'Interrupt Reason', 'Opened?', 'Received Bytes', 'Total Bytes']
    lava_data_headers = data_headers.copy()
    for i in (0, 1, 2):
        lava_data_headers[i] = (lava_data_headers[i], 'datetime')
    all_data_headers = lava_data_headers + ['Browser Name']
    report_file = 'Unknown'

    for file_found, browser_name in _history_files(files_found):
        report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found
        # older chrome db (32) lacks last_access_time; pre-v65 lacks tab_url
        last_access_sel = 'last_access_time' if does_column_exist_in_db(file_found, 'downloads', 'last_access_time') else "'' as last_access_time"
        tab_url_sel = 'tab_url' if does_column_exist_in_db(file_found, 'downloads', 'tab_url') else "'' as tab_url"

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute(f'''
        SELECT
        start_time,
        end_time,
        {last_access_sel},
        {tab_url_sel},
        target_path,
        CASE state
            WHEN "0" THEN "In Progress"
            WHEN "1" THEN "Complete"
            WHEN "2" THEN "Canceled"
            WHEN "3" THEN "Interrupted"
            WHEN "4" THEN "Interrupted"
        END,
        CASE danger_type
            WHEN "0" THEN ""
            WHEN "1" THEN "Dangerous"
            WHEN "2" THEN "Dangerous URL"
            WHEN "3" THEN "Dangerous Content"
            WHEN "4" THEN "Content May Be Malicious"
            WHEN "5" THEN "Uncommon Content"
            WHEN "6" THEN "Dangerous But User Validated"
            WHEN "7" THEN "Dangerous Host"
            WHEN "8" THEN "Potentially Unwanted"
            WHEN "9" THEN "Allowlisted by Policy"
            WHEN "10" THEN "Pending Scan"
            WHEN "11" THEN "Blocked - Password Protected"
            WHEN "12" THEN "Blocked - Too Large"
            WHEN "13" THEN "Warning - Sensitive Content"
            WHEN "14" THEN "Blocked - Sensitive Content"
            WHEN "15" THEN "Safe - Deep Scanned"
            WHEN "16" THEN "Dangerous, But User Opened"
            WHEN "17" THEN "Prompt For Scanning"
            WHEN "18" THEN "Blocked - Unsupported Type"
            WHEN "19" THEN "Dangerous - Account Compromise"
            WHEN "20" THEN "Deep Scan Failed"
            WHEN "21" THEN "Encrypted - Prompt User for Password for Local Scanning"
            WHEN "22" THEN "Encrypted - Pending Detailed Verdict after Local Scanning"
            WHEN "23" THEN "Blocked - Scan Failed"
        END,
        CASE interrupt_reason
            WHEN "0" THEN ""
            WHEN "1" THEN "File Error"
            WHEN "2" THEN "Access Denied"
            WHEN "3" THEN "Disk Full"
            WHEN "5" THEN "Path Too Long"
            WHEN "6" THEN "File Too Large"
            WHEN "7" THEN "Virus"
            WHEN "10" THEN "Temporary Problem"
            WHEN "11" THEN "Blocked"
            WHEN "12" THEN "Security Check Failed"
            WHEN "13" THEN "Resume Error"
            WHEN "14" THEN "File Hash Mismatch"
            WHEN "15" THEN "File Same as Source"
            WHEN "20" THEN "Network Error"
            WHEN "21" THEN "Operation Timed Out"
            WHEN "22" THEN "Connection Lost"
            WHEN "23" THEN "Server Down"
            WHEN "30" THEN "Server Error"
            WHEN "31" THEN "Range Request Error"
            WHEN "32" THEN "Server Precondition Error"
            WHEN "33" THEN "Unable To Get File"
            WHEN "34" THEN "Server Unauthorized"
            WHEN "35" THEN "Server Certificate Problem"
            WHEN "36" THEN "Server Access Forbidden"
            WHEN "37" THEN "Server Unreachable"
            WHEN "38" THEN "Content Lenght Mismatch"
            WHEN "39" THEN "Cross Origin Redirect"
            WHEN "40" THEN "Canceled"
            WHEN "41" THEN "Browser Shutdown"
            WHEN "50" THEN "Browser Crashed"
        END,
        CASE opened WHEN 0 THEN '' WHEN 1 THEN 'Yes' END,
        received_bytes,
        total_bytes
        FROM downloads
        ''')
        rows = cursor.fetchall()
        db.close()

        data_list = []
        for r in rows:
            data_list.append((_webkit_to_utc(r[0]), _webkit_to_utc(r[1]), _webkit_to_utc(r[2]),
                              r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10]))

        if data_list:
            all_data.extend([row + (browser_name,) for row in data_list])
        else:
            logfunc(f'No {browser_name} - Downloads data available')

    return all_data_headers, all_data, report_file


@artifact_processor
def get_chromeKeywordSearchTerms(context):
    files_found = context.get_files_found()
    all_data = []
    data_headers = ['Last Visit Time', 'Term', 'URL']
    lava_data_headers = data_headers.copy()
    lava_data_headers[0] = (lava_data_headers[0], 'datetime')
    all_data_headers = lava_data_headers + ['Browser Name']
    report_file = 'Unknown'

    for file_found, browser_name in _history_files(files_found):
        report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT url_id, term, id, url, last_visit_time
        FROM keyword_search_terms, urls
        WHERE url_id = id
        ''')
        rows = cursor.fetchall()
        db.close()

        data_list = [(_webkit_to_utc(r[4]), r[1], r[3]) for r in rows]
        if data_list:
            all_data.extend([row + (browser_name,) for row in data_list])
        else:
            logfunc(f'No {browser_name} - Keyword Search Terms data available')

    return all_data_headers, all_data, report_file

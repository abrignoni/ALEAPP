from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly

def get_swellbeing(files_found, report_folder, seeker, wrap_text):

    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('dwbCommon.db'):
            continue # Skip all other files
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(usageEvents.timeStamp/1000, "UNIXEPOCH") as timestamps,
        usageEvents.eventId,
        foundPackages.name, 
        usageEvents.eventType,
        CASE
        when usageEvents.eventType=1 THEN 'ACTIVITY_RESUMED'
        when usageEvents.eventType=2 THEN 'ACTIVITY_PAUSED'
        when usageEvents.eventType=5 THEN 'CONFIGURATION_CHANGE'
        when usageEvents.eventType=7 THEN 'USER_INTERACTION'
        when usageEvents.eventType=10 THEN 'NOTIFICATION PANEL'
        when usageEvents.eventType=11 THEN 'STANDBY_BUCKET_CHANGED'
        when usageEvents.eventType=12 THEN 'NOTIFICATION'
        when usageEvents.eventType=15 THEN 'SCREEN_INTERACTIVE (Screen on for full user interaction)'
        when usageEvents.eventType=16 THEN 'SCREEN_NON_INTERACTIVE (Screen on in Non-interactive state or completely turned off)'
        when usageEvents.eventType=17 THEN 'KEYGUARD_SHOWN || POSSIBLE DEVICE LOCK'
        when usageEvents.eventType=18 THEN 'KEYGUARD_HIDDEN || DEVICE UNLOCK'
        when usageEvents.eventType=19 THEN 'FOREGROUND_SERVICE START'
        when usageEvents.eventType=20 THEN 'FOREGROUND_SERVICE_STOP'
        when usageEvents.eventType=23 THEN 'ACTIVITY_STOPPED'
        when usageEvents.eventType=26 THEN 'DEVICE_SHUTDOWN'
        when usageEvents.eventType=27 THEN 'DEVICE_STARTUP'
        when usageEvents.eventType=28 THEN 'USER_UNLOCKED'
        else usageEvents.eventType
        END as eventTypeDescription
        FROM usageEvents
        INNER JOIN foundPackages ON usageEvents.pkgId=foundPackages.pkgId
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0: 
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], file_found))
        db.close()
        
    if data_list:
        report = ArtifactHtmlReport('Samsung Digital Wellbeing - Events')
        report.start_artifact_report(report_folder, 'Samsung Digital Wellbeing - Events')
        report.add_script()
        data_headers = ('Timestamp','Event ID','Package Name','Event Type','Event Type Description','Source File')
        
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Samsung Digital Wellbeing - Events'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Samsung Digital Wellbeing - Events'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Samsung Digital Wellbeing - Events data available')

__artifacts__ = {
        "swellbeing": (
                "Digital Wellbeing",
                ('*/com.samsung.android.forest/databases/dwbCommon.db*'),
                get_swellbeing)
}

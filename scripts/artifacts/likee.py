import os
import sys
import re
import itertools
import unicodedata
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import (
    logfunc,
    tsv,
    timeline,
    is_platform_windows,
    open_sqlite_db_readonly,
)
from pathlib import Path


def remove_control_chars(s):
    all_chars = (chr(i) for i in range(sys.maxunicode))
    categories = {"Cc"}
    control_chars = "".join(
        c for c in all_chars if unicodedata.category(c) in categories
    )
    control_chars = "".join(
        map(chr, itertools.chain(range(0x00, 0x20), range(0x7F, 0xA0)))
    )
    control_char_re = re.compile("[%s]" % re.escape(control_chars))
    return control_char_re.sub("", s)


def get_likee(files_found, report_folder, seeker, wrap_text):
    src_likee_location = ""
    data_list = []

    for file_found in files_found:
        file_name = str(file_found)
        journalName = os.path.basename(file_found)
        outputpath = os.path.join(report_folder, journalName + ".txt")
        level2, level1 = os.path.split(outputpath)
        level2 = os.path.split(level2)[1]
        final = level2 + "/" + level1
        if file_name.endswith("_location.kv"):
            src_likee_location = str(file_found)
            src_likee_location = file_found.replace(seeker.data_folder, "")
            with open(outputpath, "w") as w:
                f = open(file_found, "r", errors="ignore")
                Lines = f.readlines()
                for line in Lines:
                    if "address" in line:
                        line_encode = line.encode("utf-8", errors="ignore")
                        line_decode = line_encode.decode()
                        dstring1 = (line_decode[: line.find("address", 0, 6)]).replace(
                            "\uFFFD" "\u2660", " "
                        )
                        loc_out = remove_control_chars(dstring1)
                        w.write(loc_out)

        out = (
            f'<a href="{final}" style = "color:blue" target="_blank">{journalName}</a>'
        )
        data_list.append((out, file_found))

        report = ArtifactHtmlReport("Likee User Location")
        report.start_artifact_report(report_folder, "Likee User Location")
        report.add_script()
        data_headers = ["Artifact", "Location"]
        report.write_artifact_data_table(
            data_headers, data_list, file_found, html_escape=False
        )
        report.end_artifact_report()


def get_likee_db(files_found, report_folder, seeker, wrap_text):

    src_likee_pub = ""
    src_likee_msg = ""
    likee_pub_db = ""
    likee_msg_db = ""
    db1_data_list = []
    db2_data_list = []

    for file_found in files_found:
        file_name = str(file_found)
        ustring = "like_pub.db"
        if ustring in file_name:
            likee_pub_db = str(file_found)
            src_likee_pub = file_found.replace(seeker.data_folder, "")

        mstring = "message_u"
        if mstring in file_name:
            likee_msg_db = str(file_found)
            src_likee_msg = file_found.replace(seeker.data_folder, "")
            db2_data_list.append(str(file_found))

    db = open_sqlite_db_readonly(likee_pub_db)
    cursor = db.cursor()
    try:
        cursor.execute(
            """
                    SELECT
                        UI.history_user_name,UI.history_user_bigo_id,UI.history_user_uid
                    FROM user_search_history as UI
                        """
        )

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)

    except:
        usageentries = 0

    if usageentries > 0:
        report = ArtifactHtmlReport("Likee Users")
        report.start_artifact_report(report_folder, "Likee Users")
        report.add_script()
        db1_data_headers = ("Users", "Username", "User ID")
        db1_data_list = []
        for row in all_rows:
            db1_data_list.append((row[0], row[1], row[2]))

        report.write_artifact_data_table(
            db1_data_headers, db1_data_list, src_likee_pub, html_escape=False
        )
        report.end_artifact_report()

        tsvname = f"Likee User Info"
        tsv(report_folder, db1_data_headers, db1_data_list, tsvname, src_likee_pub)

    else:
        logfunc("No user info found")

    db.close()

    for likee_msg_db in db2_data_list:
        db = open_sqlite_db_readonly(likee_msg_db)
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                SELECT
                    messages.uid,messages.content,
                    datetime(messages.time/1000, 'unixepoch')
                FROM messages
                """
            )
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)

        except:
            usageentries = 0

        if usageentries > 0:
            report = ArtifactHtmlReport("Likee Messages")
            report.start_artifact_report(report_folder, "Likee Messages")
            report.add_script()
            db2_data_headers = ("User ID", "Message Content", "Timestamp")
            db2_data_list = []
            for row in all_rows:
                db2_data_list.append((row[0], row[1], row[2]))

            report.write_artifact_data_table(
                db2_data_headers, db2_data_list, src_likee_msg, html_escape=False
            )
            report.end_artifact_report()

            tsvname = f"Likee Messages"
            tsv(report_folder, db2_data_headers, db2_data_list, tsvname, src_likee_msg)

        else:
            logfunc("No Message data found" + (str(file_found)))

        db.close()


__artifacts__ = {
    "likee_location": ("LIKEE", ("*/video.like/files/*/*location.kv"), get_likee),
    "likee_databases": ("LIKEE", ("*/video.like/databases/*.db"), get_likee_db),
}


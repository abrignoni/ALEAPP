import xmltodict
from hashlib import md5
import base64
import binascii

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows 
from scripts.parse3 import ParseProto

def get_vaulty_info(files_found, report_folder, seeker, wrap_text):

    title = "Vaulty - Info"

    # Prefs File
    file_found = str(files_found[0])

    data_headers = ('Key', 'Value')
    data_list = []
    
    with open(file_found, "r") as file:
        xml = file.read()
    prefs = xmltodict.parse(xml)

    
    # PIN
    for item in prefs["map"]["string"]:
        if item.get("@name", None) == "password_hash":
            password_hash = item.get("#text", None)

    if password_hash:
        md5_hash_binary = base64.decodestring(password_hash.encode())
        md5_hash = binascii.hexlify(md5_hash_binary).decode()

        data_list.append(["Password MD5", md5_hash])

        def brute_force(target):
            four_digit_pins = list(map(lambda x: f"{x:04}", range(0, 10000)))
            six_digit_pins = list(map(lambda x: f"{x:06}", range(0, 1000000)))
            pins = four_digit_pins + six_digit_pins

            for index, item in enumerate(pins):
                pin = item.encode()
                guess = md5(pin).hexdigest()
                if guess == target:
                    return pins[index]
            else:
                return "Brute Force was Unsuccessful - this is not the password"

        password = brute_force(md5_hash)
        data_list.append(["Password", password])

    # Security question
    for item in prefs["map"]["string"]:
        if item.get("@name", None) == "security_question":
            question = item.get("#text", None)
            data_list.append(["Security Question", question])
        
    # Security Answer
    for item in prefs["map"]["string"]:
        if item.get("@name", None) == "security_answer_hash":
            answer = item.get("#text", None)
            answer = base64.decodestring(answer.encode())
            answer = binascii.hexlify(answer).decode()
            data_list.append(["Security Answer MD5", answer])

    # Store
    for item in prefs["map"]["string"]:
        if item.get("@name", None) == "location":
            location = item.get("#text", None)
            data_list.append(["Location", location])

    # Drive
    for item in prefs["map"]["string"]:
        if item.get("@name", None) == "drive_account_name":
            drive = item.get("#text", None)
            data_list.append(["Drive Account", drive])


    # Reporting
    report = ArtifactHtmlReport(title)
    report.start_artifact_report(report_folder, title)
    report.add_script()
    report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
    report.end_artifact_report()
    
    tsv(report_folder, data_headers, data_list, title)

__artifacts__ = {
    "vaulty_info": (
        "Vaulty",
        ('*/com.theronrogers.vaultyfree/shared_prefs/com.theronrogers.vaultyfree_preferences.xml'),
        get_vaulty_info)
}
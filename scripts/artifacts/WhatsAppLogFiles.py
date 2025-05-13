import os
import gzip
import re
import sqlite3
from collections import defaultdict

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, open_sqlite_db_readonly


def normalize_jid(jid):
    """
    Normalize WhatsApp JIDs by removing ':X' before the '@' symbol.

    Args:
        jid (str): The JID to normalize.

    Returns:
        str: The normalized JID.
    """
    return re.sub(r':\d+@', '@', jid)


class WAIndex:
    """
    Index for fast lookup of JIDs based on the last 4 digits of the phone number.
    Maps suffixes (last 4 digits) to sets of JIDs for efficient searching.
    """

    def __init__(self):
        self.index = defaultdict(set)  # Dictionary mapping suffixes to sets of JIDs

    def add(self, jid):
        """
        Add a JID to the index based on the last 4 digits of the phone number.

        Args:
            jid (str): The JID to add to the index.
        """
        if not isinstance(jid, str) or '@' not in jid:
            logfunc(f"Invalid JID format: {jid}")
            return
        jid = normalize_jid(jid)
        phone_number = jid.split('@')[0]
        suf = phone_number[-4:]  # Extract the last 4 digits
        self.index[suf].add(jid)  # Add JID to the set for this suffix
        #logfunc(f"Loaded into index: {jid}")

    def search_by_sufix(self, jid_input):
        """
        Search for JIDs by the last 4 digits and return only the numbers before '@'.

        Args:
            jid_input (str): The JID to search for.

        Returns:
            str: A string of matching phone numbers (before '@') joined by ' or ', or a message if no matches are found.
        """
        if '@' not in jid_input:
            return f"Invalid JID format: {jid_input}"
        suf = jid_input.split('@')[0][-4:]  # Extract the last 4 digits of the input JID
        results = self.index.get(suf, set())  # Get all JIDs with matching suffix
        if not results:
            return f"No matches found for suffix: {jid_input.split('@')[0]}"
        return " or ".join(sorted(jid.split('@')[0] for jid in results))

    def print_index(self):
        """
        Print all indexed suffixes and their associated JIDs for debugging.
        """
        for suf, jids in self.index.items():
            logfunc(f"Suffix: {suf}")
            for jid in sorted(jids):
                logfunc(f"   {jid}")


def load_contacts(cursor):
    """
    Load contacts from the WhatsApp database into the WAIndex for lookup.

    Args:
        cursor (sqlite3.Cursor): Database cursor to execute queries.

    Returns:
        WAIndex: An index containing the loaded JIDs.
    """
    index = WAIndex()
    cursor.execute('SELECT jid FROM wa_contacts')  # Query to fetch JIDs
    for (jid,) in cursor.fetchall():
        index.add(jid)  # Add each JID to the index
    return index


class WAToken:
    """
    Token representation for WhatsApp log events with associated metadata.
    """

    def __init__(self, token, description):
        self.token = token
        self.description = description


class WALogLine:
    """
    Representation of a parsed WhatsApp log line with extracted metadata.
    """

    def __init__(self, wa_token, line, file_name):
        self.line = line
        self.wa_token = wa_token
        self.file_name = file_name
        self.timestamp = self.get_timestamp(line)

    def process_line(self, line, file_name, index):
        """
        Process a log line to extract contact information and metadata.

        Args:
            line (str): The log line to process.
            file_name (str): The name of the file being processed.
            index (WAIndex): The index of JIDs for lookup.

        Returns:
            list: A list containing the processed data (timestamp, token, description, line, file name, probable contact).
        """
        self.file_name = file_name

        # Regular expression to extract WhatsApp JIDs from the log line
        pattern = r'\b\d{4,}(?::\d+)?@s\.whatsapp\.net\b'
        matches = re.findall(pattern, line)
        cellphone_result = ""

        if matches:
            # Normalize all JIDs and extract unique phone numbers (before '@')
            unique_numbers = set()
            for match in matches:
                normalized_jid = normalize_jid(
                    match)  # Normalize JID (e.g., 1234:0@s.whatsapp.net -> 1234@s.whatsapp.net)
                phone_number = normalized_jid.split('@')[0]  # Extract the phone number part
                unique_numbers.add(phone_number)  # Add to set to ensure uniqueness

            # Search for matches in the index for each unique phone number
            cellphones = []
            for phone_number in unique_numbers:
                # Create a JID for searching (e.g., 1234@s.whatsapp.net)
                jid_to_search = f"{phone_number}@s.whatsapp.net"
                result = index.search_by_sufix(jid_to_search)
                if "No matches found" not in result:  # Only include valid matches
                    cellphones.append(result)

            cellphone_result = ",".join(cellphones) if cellphones else ""

        # Update token description for enter/exit conversation events
        if self.wa_token.token == enter_exit_conversation_token.token:
            if "false" in line:
                self.wa_token.description = "Exit conversation"
            elif "true" in line:
                self.wa_token.description = "Enter conversation"

        #logfunc(f"Cellphone: {cellphone_result}")

        # Return the processed data as a list for reporting
        return [
            self.timestamp,
            self.wa_token.token,
            self.wa_token.description,
            line,
            file_name,
            cellphone_result
        ]

    def get_timestamp(self, line):
        """
        Extract the timestamp from the log line using a regex pattern.

        Args:
            line (str): The log line to parse.

        Returns:
            str: The extracted timestamp or "N/A" if not found.
        """
        date_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line)
        return date_match.group() if date_match else "N/A"


# Define a specific token for entering/exiting conversations
enter_exit_conversation_token = WAToken("conversation/window-focus-changed", "")


def get_WhatsAppLogFiles(files_found, report_folder, seeker, wrap_text):
    """
    Process WhatsApp log files, extract relevant events, and generate forensic reports.

    Args:
        files_found (list): List of file paths to process.
        report_folder (str): Directory to store the generated reports.
        seeker (object): Object for accessing file system (from forensic framework).
        wrap_text (bool): Whether to wrap text in the report.

    Returns:
        None
    """
    # List of tokens to identify specific events in the logs
    lst_of_tokens = [
        WAToken("WriterThread/write/send-encrypted Key", "Sent message"),
        WAToken("ConnectionThreadRequestsImpl/message", "Received message"),
        enter_exit_conversation_token,
        WAToken("HandleMeComposing/sendComposing", "Owner typing"),
        WAToken("messagenotification/postChildNotification", "Message received notification"),
        WAToken("msgstore/deletemsgs/mark", "Selected message deletion"),
        WAToken("CoreMessageStore/deletemsgs/batches", "Batch message deletion"),
        WAToken("ConnectionThreadRequestsImpl/compose/composing", "Party typing")
    ]

    # Create a dictionary for faster token lookups
    token_dict = {token.token: token for token in lst_of_tokens}
    token_ignore_line = "status@broadcast"  # Ignore lines containing this token
    data_list = []  # List to store processed log data for reporting

    # Locate the WhatsApp wa.db file and load contacts
    index = None
    for file_found in files_found:
        logfunc(f"List of files tested: {file_found}")
        file_name = str(file_found)
        if file_name.endswith('wa.db'):
            try:
                with open_sqlite_db_readonly(file_name) as db:
                    cursor = db.cursor()
                    index = load_contacts(cursor)  # Load contacts into the index
                    if not index.index:
                        logfunc('No WhatsApp - Contacts found')
                    #else:
                        #logfunc("Index loaded:")
                        #index.print_index()
            except sqlite3.Error as e:
                logfunc(f"Error accessing database {file_name}: {str(e)}")
                continue

    if index is None:
        logfunc("No WhatsApp database (wa.db) found. Proceeding without contact index.")
        index = WAIndex()  # Create an empty index to avoid errors

    # Process each log file
    logfunc(f"Number of files found: {len(files_found)}")

    for file_found in files_found:
        file_path_complete = str(file_found)
        file_name = os.path.basename(file_path_complete)

        logfunc(f"Processing file: {file_path_complete}")

        try:
            # Process both .gz (compressed) and .log (uncompressed) files line by line
            if file_path_complete.endswith('.gz'):
                with gzip.open(file_path_complete, 'rt', encoding='utf-8', errors='replace') as file:
                    for line in file:
                        line = line.strip()
                        for token_key in token_dict:
                            if token_key in line and token_ignore_line not in line:
                                wa_log_line = WALogLine(token_dict[token_key], line, file_name)
                                data_list.append(wa_log_line.process_line(line, file_name, index))
            elif file_path_complete.endswith('.log'):
                with open(file_path_complete, 'r', encoding='utf-8', errors='replace') as file:
                    for line in file:
                        line = line.strip()
                        for token_key in token_dict:
                            if token_key in line and token_ignore_line not in line:
                                wa_log_line = WALogLine(token_dict[token_key], line, file_name)
                                data_list.append(wa_log_line.process_line(line, file_name, index))
        except UnicodeDecodeError as e:
            logfunc(f"Encoding error in file {file_path_complete}: {str(e)}")
            continue
        except gzip.BadGzipFile as e:
            logfunc(f"Invalid gzip file {file_path_complete}: {str(e)}")
            continue
        except Exception as e:
            logfunc(f"Error processing file {file_path_complete}: {str(e)}")
            continue

    # Generate reports if data was extracted
    if data_list:
        report = ArtifactHtmlReport('WhatsApp Logs Analysis')
        report.start_artifact_report(report_folder, 'WhatsApp Logs')
        report.add_script()
        data_headers = ('Timestamp', 'Token', 'Description', 'Full line', 'Source File', 'Probable Contact')
        report.write_artifact_data_table(data_headers, data_list, report_folder)
        report.end_artifact_report()

        tsvname = 'WhatsApp Logs - Detailed'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No relevant data found in the analyzed logs. No report was generated.')


# Artifact definition for integration with a forensic framework
__artifacts__ = {
    "WhatsApp Log Files": (
        "WhatsApp Log Files",
        ('*/data/com.whatsapp/files/Logs/*', '*/data/com.whatsapp/databases/*.db'),
        get_WhatsAppLogFiles)
}
__artifacts_v2__ = {
    "get_WhatsAppLogFiles": {
        "name": "WhatsApp Log Files",
        "description": "Key events extracted from the WhatsApp application logs: message send "
                       "and receive markers, conversation focus changes, typing indicators, "
                       "notifications and message deletions",
        "author": "Mateus Polastro",
        "creation_date": "2025-05-13",
        "last_update_date": "2026-08-10",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "Each row is a log line matching one of eight event tokens; the token-to-event "
                 "mapping comes from the author's research on WhatsApp logs and the full line is "
                 "reported beside it so the reading can be checked. Lines mentioning "
                 "status@broadcast are skipped by design.\n"
                 "The logs redact phone numbers, so a JID in a line may carry only trailing "
                 "digits. The Possible Full Numbers column lists every wa.db contact whose number "
                 "ends in the same last four digits; that is a candidate list, not an "
                 "identification, and more than one candidate is shown joined with 'or'. An "
                 "empty value means no wa.db contact shares the suffix.\n"
                 "The log declares its own timezone: each logfile header line carries a "
                 "tz=+/-HHMM offset, and timestamps are converted to UTC using the most recent "
                 "declared offset. A line seen before any header keeps its timestamp as "
                 "written.",
        "paths": (
            "*/com.whatsapp/files/Logs/*",
            "*/com.whatsapp/databases/wa.db",
        ),
        "output_types": "standard",
        "artifact_icon": "message-square",
        "sample_data": {
            "anne_a15": "20 rows",
            "hc_pixel8pro_a16": "0 rows",
            "hc_pixel8pro_a17": "0 rows",
            "kevin_pocox7_a15": "34 rows",
            "pixel7a_a14": "34 rows",
            "russell_pixel6a_a13": "24 rows",
            "samsungs20_a13": "1 row",
            "sharon_a14": "0 rows",
        },
    }
}

import os
import gzip
import re
import sqlite3
from collections import defaultdict

from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


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

    This function is intentionally "best-effort" because WhatsApp DB schemas vary
    across versions/devices. The goal here is simply to collect JIDs so we can
    later suggest probable contacts by suffix matching (see WAIndex.search_by_sufix).

    Args:
        cursor (sqlite3.Cursor): Database cursor to execute queries.

    Returns:
        WAIndex: An index containing the loaded JIDs.
    """
    index = WAIndex()

    # Helper: add jids from a (table, column) pair if it exists
    def _try_add_from(table: str, col: str):
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            cols = {row[1] for row in cursor.fetchall()}  # (cid, name, type, ...)
            if col not in cols:
                return

            # Pull distinct values; filter to WhatsApp JIDs when possible.
            try:
                cursor.execute(
                    f"SELECT DISTINCT {col} FROM {table} "
                    f"WHERE {col} LIKE '%@s.whatsapp.net' OR {col} LIKE '%@g.us'"
                )
            except sqlite3.Error:
                cursor.execute(f"SELECT DISTINCT {col} FROM {table}")

            for (jid,) in cursor.fetchall():
                if jid:
                    index.add(str(jid))
        except sqlite3.Error:
            # Ignore and keep trying other candidates
            return

    # Common/historical WhatsApp tables that may contain JIDs
    candidates = [
        ("wa_contacts", "jid"),
        ("wa_vnames", "jid"),
        ("wa_contacts", "jid_raw_string"),
        ("contacts", "jid"),
        ("vnames", "jid"),
    ]

    for table, col in candidates:
        _try_add_from(table, col)

    # Fallback: if nothing found, scan for any table containing a 'jid' column.
    # (Avoids hard-failing on unexpected schema changes.)
    if not index.index:
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [t[0] for t in cursor.fetchall() if t and t[0]]
            for table in tables:
                _try_add_from(table, "jid")
        except sqlite3.Error:
            pass

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
        if not date_match:
            return ''
        try:
            return datetime.strptime(date_match.group(), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return date_match.group()


# Each logfile header declares the timezone its timestamps are written in,
# e.g. "==== logfile level=3 tz=+0200 ====".
TZ_HEADER_RE = re.compile(r'==== logfile .*?tz=([+-])(\d{2})(\d{2})')


def _tz_from_header(line):
    m = TZ_HEADER_RE.search(line)
    if not m:
        return None
    sign = 1 if m.group(1) == '+' else -1
    return timezone(sign * timedelta(hours=int(m.group(2)), minutes=int(m.group(3))))


# Define a specific token for entering/exiting conversations
enter_exit_conversation_token = WAToken("conversation/window-focus-changed", "")

@artifact_processor
def get_WhatsAppLogFiles(context):
    files_found = [str(f) for f in context.get_files_found()]
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
        file_name = str(file_found)
        if file_name.endswith('wa.db'):
            try:
                with open_sqlite_db_readonly(file_name) as db:
                    cursor = db.cursor()
                    index = load_contacts(cursor)  # Load contacts into the index
                    if not index.index:
                        logfunc('No WhatsApp contacts found in wa.db; the candidate column stays empty')
            except sqlite3.Error as e:
                logfunc(f"Error accessing database {file_name}: {str(e)}")
                continue

    if index is None:
        logfunc("No WhatsApp database (wa.db) found. Proceeding without contact index.")
        index = WAIndex()  # Create an empty index to avoid errors

    for file_found in files_found:
        file_path_complete = str(file_found)
        file_name = os.path.basename(file_path_complete)

        try:
            # Process both .gz (compressed) and .log (uncompressed) files line by line
            if file_path_complete.endswith('.gz'):
                opener = gzip.open(file_path_complete, 'rt', encoding='utf-8', errors='replace')
            elif file_path_complete.endswith('.log'):
                opener = open(file_path_complete, 'r', encoding='utf-8', errors='replace')
            else:
                continue
            current_tz = None
            with opener as file:
                for line in file:
                    line = line.strip()
                    header_tz = _tz_from_header(line)
                    if header_tz is not None:
                        current_tz = header_tz
                        continue
                    for token_key in token_dict:
                        if token_key in line and token_ignore_line not in line:
                            wa_log_line = WALogLine(token_dict[token_key], line, file_name)
                            row = wa_log_line.process_line(line, file_name, index)
                            if isinstance(row[0], datetime) and current_tz is not None:
                                row[0] = row[0].replace(tzinfo=current_tz).astimezone(timezone.utc)
                            data_list.append(row)
        except UnicodeDecodeError as e:
            logfunc(f"Encoding error in file {file_path_complete}: {str(e)}")
            continue
        except gzip.BadGzipFile as e:
            logfunc(f"Invalid gzip file {file_path_complete}: {str(e)}")
            continue
        except OSError as e:
            logfunc(f"Error processing file {file_path_complete}: {str(e)}")
            continue

    source_path = next((p for p in files_found if p.lower().endswith(('.log', '.gz'))),
                       files_found[0] if files_found else '')

    data_headers = (
        ('Timestamp', 'datetime'),
        'Token',
        'Description',
        'Full Line',
        'Source File',
        'Possible Full Numbers (last-4 match)',
    )
    return data_headers, data_list, source_path

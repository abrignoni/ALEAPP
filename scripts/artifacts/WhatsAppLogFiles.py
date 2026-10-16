__artifacts_v2__ = {
    "get_WhatsAppLogFiles": {
        "name": "WhatsApp Log Files",
        "description": "Log lines from the WhatsApp application logs that contain one of "
                       "eight tokens, each shown with the label this parser assigns to that "
                       "token",
        "author": "Mateus Polastro, @AlexisBrignoni, Codex",
        "creation_date": "2025-05-13",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "Each row is a log line containing one of eight tokens; a line containing two "
                 "tokens gives two rows. The Description shown for a token is this parser's "
                 "label: the token-to-event mapping is not vendor-documented, and the Full Line "
                 "column is reported beside it so the reading can be checked. For the "
                 "conversation/window-focus-changed token the Description is set from the last "
                 "word of the line: Exit conversation when it is false, Enter conversation when "
                 "it is true, and blank for any other word. On anne_a15, kevin_pocox7_a15, "
                 "pixel7a_a14 and russell_pixel6a_a13 all 80 such lines ended in true (40) or "
                 "false (40). Lines mentioning status@broadcast are skipped by design.\nThe "
                 "Possible Full Numbers column lists every JID read from wa.db (user and group "
                 "JIDs found in the wa_contacts, wa_vnames, contacts and vnames tables, or in "
                 "any table with a jid column when those yield none) whose part before the @ "
                 "ends in the same four characters as the digits before @s.whatsapp.net in the "
                 "line. A log is matched only with the wa.db under the same com.whatsapp "
                 "directory; each tested image held one wa.db, so the case of more than one was "
                 "checked on a constructed input only. That is a candidate list, not an "
                 "identification, and more than one candidate is shown joined with 'or'. An "
                 "empty value means the line held no JID of the form digits@s.whatsapp.net, or "
                 "no JID read from that wa.db shares the suffix, or no wa.db was readable in "
                 "that directory.\nThe log declares its own timezone: each logfile header line "
                 "carries a tz=+/-HHMM offset, and timestamps are converted to UTC using the "
                 "most recent offset declared in the same file. A line seen before any header "
                 "in its file has no declared offset: its Timestamp is left blank and the "
                 "reading as written stays at the start of Full Line. On the five tested images "
                 "with rows (anne_a15, kevin_pocox7_a15, pixel7a_a14, russell_pixel6a_a13, "
                 "samsungs20_a13) every log file began with a header and no row was blank.",
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

        # The focus line ends with the word true or false. The label is decided per
        # line from that last word, so one line's label cannot carry over to another.
        description = self.wa_token.description
        if self.wa_token.token == enter_exit_conversation_token.token:
            words = line.split()
            last_word = words[-1] if words else ''
            if last_word == "false":
                description = "Exit conversation"
            elif last_word == "true":
                description = "Enter conversation"
            else:
                description = ""

        #logfunc(f"Cellphone: {cellphone_result}")

        # Return the processed data as a list for reporting
        return [
            '',  # filled by the caller once the file's declared offset is known
            self.wa_token.token,
            description,
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
            datetime: The reading as written, with no zone, or None if none parses.
        """
        date_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line)
        if not date_match:
            return None
        try:
            return datetime.strptime(date_match.group(), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return None


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


def _container_of(path):
    """The part of a path up to its com.whatsapp folder, so a log is only matched
    with the wa.db of the same app data directory."""
    path = str(path).replace('\\', '/')
    marker = '/com.whatsapp/'
    pos = path.rfind(marker)
    return path[:pos + len(marker)] if pos >= 0 else ''


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

    # Locate each WhatsApp wa.db file and load its contacts, one index per
    # com.whatsapp directory
    indexes = {}
    for file_found in files_found:
        file_name = str(file_found)
        if file_name.endswith('wa.db'):
            try:
                with open_sqlite_db_readonly(file_name) as db:
                    cursor = db.cursor()
                    wa_index = load_contacts(cursor)  # Load contacts into the index
                    if not wa_index.index:
                        logfunc('No WhatsApp contacts found in wa.db; the candidate column stays empty')
                    indexes[_container_of(file_name)] = wa_index
            except sqlite3.Error as e:
                logfunc(f"Error accessing database {file_name}: {str(e)}")
                continue

    if not indexes:
        logfunc("No WhatsApp database (wa.db) found. Proceeding without contact index.")
    empty_index = WAIndex()  # Used for a log whose directory has no readable wa.db
    no_offset_rows = 0

    for file_found in files_found:
        file_path_complete = str(file_found)
        file_name = os.path.basename(file_path_complete)
        index = indexes.get(_container_of(file_path_complete), empty_index)

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
                            stamp = wa_log_line.timestamp
                            if stamp is not None and current_tz is not None:
                                row[0] = stamp.replace(tzinfo=current_tz).astimezone(timezone.utc)
                            elif stamp is not None:
                                # No offset declared yet: the reading has no zone, so
                                # no instant is reported. It stays in Full Line.
                                no_offset_rows += 1
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

    if no_offset_rows:
        logfunc(f'{no_offset_rows} WhatsApp log line(s) came before any tz header; '
                'their Timestamp is left blank')

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

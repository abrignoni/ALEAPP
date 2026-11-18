"""Samsung Quick Share (com.samsung.android.app.sharelive) transfers and link shares.

Quick Share keeps its sharing state in databases/linkShare.db, a Room database. Nearby
transfers to and from other devices sit in shares, devices, transfer_request,
transfer_file and request_accept; shares made as a link sit in box and content.
"""

__artifacts_v2__ = {
    "get_samsung_quick_share_transfers": {
        "name": "Samsung Quick Share - Transfers",
        "description": (
            "Parses nearby Quick Share transfers from linkShare.db: one row per file per "
            "peer device listed in a share (outgoing) and one row per incoming request, "
            "with the peer device name, the file name, size and type, the file counts, the "
            "PIN shown for the transfer and the stored status values."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Samsung Quick Share",
        "notes": (
            "Read from com.samsung.android.app.sharelive/databases/linkShare.db with its "
            "-wal. Outgoing rows come from the devices table (one row per peer device "
            "listed in a share), joined to shares on share_id for Share Created, to "
            "transfer_internet on request_id for Transfer Started, and to transfer_file on "
            "the device's transfer_request_id for the file. transfer_file held six rows on "
            "the known data, three per sent file; the artifact reports the one the device "
            "row points to. Shares of more than one file were not exercised. Incoming rows "
            "come from request_accept. "
            "Known data (samsung_a166u_a16_known_20261117, a Galaxy A16 sharing with a "
            "second test phone, actions and times logged during the session): one image and "
            "one text file sent, one text file received and one declined. Every logged "
            "transfer appears. The file names, PINs and peer device name match the log. The "
            "log gives a size for three of the four files and those match (the image to the "
            "nearest KB). "
            "Outgoing: the two sent files have Files Sent 1 of Files Total 1. A third "
            "outgoing row, whose share was created 11 seconds before the text file's share, "
            "lists the same peer; the log records no separate action for it and what "
            "produced it is not established. It has every count 0, no file and Accept "
            "Result (as stored) -1. "
            "Transfer Started is transfer_internet.created_at, Share Created is "
            "shares.create_time and Peer Updated is devices.update_time, all milliseconds "
            "since the Unix epoch converted to UTC and cut to the whole second. On the "
            "known data Transfer Started was within 2 seconds of the logged start of each "
            "send; Share Created and Peer Updated were 53 to 88 seconds earlier than the "
            "logged moment the send finished, and which event those two record is not "
            "established. Transfer Started is blank where no transfer_internet row has the "
            "device's request_id (the row with nothing sent). "
            "Incoming: request_accept.create_time held 0 on both known-data rows, so the "
            "time columns are blank there. The received file had receive_status 4 and "
            "accept_result 0; the declined one receive_status 10 and accept_result 1. "
            "Outcome shows Received or Declined for exactly those two combinations and is "
            "blank for any other, which keeps the stored values in Status (as stored) and "
            "Accept Result (as stored). Each label rests on one logged transfer; a transfer "
            "accepted and then failed or cancelled was not exercised. On an incoming row "
            "Files Sent or Downloaded is download_file_count, which held 0 on both rows, "
            "the received one included, so on the known data it did not count the saved "
            "file. "
            "On an incoming row File Name is represent_file_name, or file_name where that "
            "is empty; File Size is total_file_size, or total_bytes where that is absent or "
            "NULL (total_bytes held 0 on both known-data rows, so on a version without "
            "total_file_size the value is not established as the file's size); Peer Device "
            "Name is device_name, or sender_name where that is empty (equal on both "
            "known-data rows). request_accept columns differ between app versions "
            "(cookbook_a11 and samsunga53_a14 have no sender_name or total_file_size, "
            "sharon_a14 no sender_name); a missing one is read as blank. "
            "receiving_file held no rows and request_accept.provider_uri and parent_folder "
            "were NULL, so the artifact reports no saved path; on the known data the "
            "received file was in Download/Quick Share. request_accept.custom_data (a blob) "
            "is not decoded. "
            "Status (as stored) is devices.share_status on outgoing rows (4 on both sent "
            "files, 0 on the row with nothing sent) and request_accept.receive_status on "
            "incoming rows. Outgoing values are not decoded. Share or Request ID is "
            "devices.share_id on outgoing rows and the request_accept row id, prefixed with "
            "the table name, on incoming rows. "
            "sqlite_sequence shows devices reached id 4 while three rows remain, so at "
            "least one devices row was removed; the artifact reports the rows present at "
            "extraction. "
            "Left out: shares rows that list no peer device (the known data holds 8, three "
            "of them from before the session; two, with secure_mode 1, were created within "
            "a second after each sent share; what creates the others is not established), "
            "sending_request (a request id and connection type), optional_meta (media type, "
            "width, height and cloud flags for a sent file), enhanced_share_items and "
            "enhanced_share_content (a sender package name and one item with its own file "
            "name and size; their purpose is not established), and the peer IP addresses, "
            "keys and hashes in devices and request_accept. cached_devices, "
            "recent_recipient and app_usage_stats held no rows on every registered image "
            "that holds linkShare.db (sharon_a13 has no cached_devices or recent_recipient "
            "table). "
            "None of the seven other registered images that hold linkShare.db has a row in "
            "devices or request_accept. On samsung_a166u_a16_known_20261117 Peer Device "
            "Name held one value and Android User held 0 on all five rows (one peer phone; "
            "linkShare.db exists only in user 0's container, and the Secure Folder user's "
            "container holds none), and Files Failed and Files Cancelled were identical on "
            "every row: 0 on each outgoing row and blank on each incoming row, where "
            "request_accept has no such counts."
        ),
        "paths": ("*/com.samsung.android.app.sharelive/databases/linkShare.db*",),
        "output_types": "standard",
        "artifact_icon": "share-2",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.samsung.android.app.sharelive | 5 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.app.sharelive | devices and request_accept empty | 0 rows",
            "anne_a15": "Android 15 | com.samsung.android.app.sharelive | devices and request_accept empty | 0 rows",
            "cookbook_a11": "Android 11 | com.samsung.android.app.sharelive | devices and request_accept empty | 0 rows",
            "falken_a326u_a13": "Android 13 | com.samsung.android.app.sharelive | devices and request_accept empty | 0 rows",
            "samsunga53_a14": "Android 14 | com.samsung.android.app.sharelive | devices and request_accept empty | 0 rows",
            "sharon_a14": "Android 14 | com.samsung.android.app.sharelive | devices and request_accept empty | 0 rows",
            "sharon_a13": "Android 13 | com.samsung.android.app.sharelive | older linkShare.db with no devices or request_accept table | 0 rows",
            "adams_ss135dl_a13": "Android 13 | no linkShare.db | 0 rows",
            "galaxys10_a10": "Android 10 | no linkShare.db | 0 rows",
            "s20fe_a13": "Android 13 | no linkShare.db | 0 rows",
            "samsungs20_a13": "Android 13 | no linkShare.db | 0 rows",
        },
    },
    "get_samsung_quick_share_link_shares": {
        "name": "Samsung Quick Share - Link Shares",
        "description": (
            "Parses Quick Share link shares recorded in the box and content tables of "
            "linkShare.db: one row per file, with the link creation and expiry times, the "
            "link URL and the file name, type, size, dimensions and stored hash."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Samsung Quick Share",
        "notes": (
            "Read from the box (one row per link) and content (one row per file, box_id "
            "points to box.id) tables of "
            "com.samsung.android.app.sharelive/databases/linkShare.db. Whether a box row "
            "can also record a link received from someone else is not established. "
            "Created and Expires are box.create_time and box.expire_time, milliseconds "
            "since the Unix epoch converted to UTC. The decoded values fall before the "
            "extraction date; no logged link share was available to check them against. "
            "Link URL is box.url as stored. Hash (as stored) is content.hash; on sharon_a13 "
            "it held 64 hexadecimal characters and equalled content.cloud_hash, and which "
            "algorithm produced it is not established. Status (as stored) and Type (as "
            "stored) are box.status and box.type, not decoded. "
            "Exercised on one link share of one JPEG image, present on sharon_a13 (an older "
            "linkShare.db without the nearby-transfer tables) and with the same values on "
            "sharon_a14, a later image of the same CTF persona's phone. On every other "
            "registered image that holds linkShare.db the box table is empty. The artifact "
            "does not establish whether the link still worked at extraction time; "
            "box.status is not decoded. transfer_info (current and total counts, a status "
            "and an error code per box) is not reported. Files received through a link are "
            "not exercised."
        ),
        "paths": ("*/com.samsung.android.app.sharelive/databases/linkShare.db*",),
        "output_types": "standard",
        "artifact_icon": "link",
        "sample_data": {
            "sharon_a13": "Android 13 | com.samsung.android.app.sharelive | 1 row",
            "sharon_a14": "Android 14 | com.samsung.android.app.sharelive | 1 row",
            "samsung_a166u_a16_known_20261117": "Android 16 | com.samsung.android.app.sharelive | box empty | 0 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.app.sharelive | box empty | 0 rows",
            "anne_a15": "Android 15 | com.samsung.android.app.sharelive | box empty | 0 rows",
            "cookbook_a11": "Android 11 | com.samsung.android.app.sharelive | box empty | 0 rows",
            "falken_a326u_a13": "Android 13 | com.samsung.android.app.sharelive | box empty | 0 rows",
            "samsunga53_a14": "Android 14 | com.samsung.android.app.sharelive | box empty | 0 rows",
            "adams_ss135dl_a13": "Android 13 | no linkShare.db | 0 rows",
            "galaxys10_a10": "Android 10 | no linkShare.db | 0 rows",
            "s20fe_a13": "Android 13 | no linkShare.db | 0 rows",
            "samsungs20_a13": "Android 13 | no linkShare.db | 0 rows",
        },
    },
}

import re

from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    does_table_exist_in_db,
    get_sqlite_db_records,
    is_sqlite_sidecar,
)

PACKAGE = "com.samsung.android.app.sharelive"
_USER_RE = re.compile(r"/(?:user|user_de|data_mirror/data_(?:ce|de)/[^/]+)/(\d+)/")


def _container(path):
    """(android user, storage area) of the sharelive container a path sits in, or None."""
    norm = str(path).replace("\\", "/")
    idx = norm.find(f"/{PACKAGE}/")
    if idx < 0:
        return None
    head = norm[:idx + 1]
    area = "de" if ("/user_de/" in head or "/data_mirror/data_de/" in head) else "ce"
    match = None
    for match in _USER_RE.finditer(head):
        pass
    if match and head.endswith(f"/{match.group(1)}/"):
        return int(match.group(1)), area
    if head.rstrip("/").rsplit("/", 1)[-1] == "data":
        # /data/data/<pkg>, and layouts such as userdata/data/<pkg> that keep user 0 there
        return 0, area
    return None


def _databases(files_found):
    for path in files_found:
        path = str(path)
        if is_sqlite_sidecar(path) or not path.endswith("linkShare.db"):
            continue
        container = _container(path)
        if container is None:
            continue
        yield path, container


def _ms(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ""
    return convert_unix_ts_to_utc(value) if value > 0 else ""


def _has_columns(path, table, columns):
    rows = get_sqlite_db_records(path, f"PRAGMA table_info({table})")
    present = {row[1] for row in rows}
    return all(column in present for column in columns)


OUTGOING_QUERY = """
SELECT {started}, shares.create_time, devices.update_time, devices.device_name,
       transfer_file.file_name,
       transfer_file.file_size, transfer_file.mime_type, devices.file_sent_count,
       devices.file_total_count, devices.file_failed_count, devices.file_cancelled_count,
       devices.share_status, devices.accept_result, devices.pin_code, transfer_file.uri,
       devices.share_id, devices.id
FROM devices
LEFT JOIN shares ON shares.id = devices.share_id
{internet_join}LEFT JOIN transfer_file ON transfer_file.transfer_request_id = devices.transfer_request_id
                        AND devices.transfer_request_id > 0
ORDER BY shares.create_time, devices.id, transfer_file.id
"""

INCOMING_COLUMNS = (
    "create_time", "device_name", "sender_name", "represent_file_name", "file_name",
    "total_file_size", "total_bytes", "total_file_count", "download_file_count",
    "receive_status", "accept_result", "pin_code", "id",
)


def _incoming_query(path):
    """request_accept columns vary by app version; a missing one is read as NULL."""
    present = {row[1] for row in get_sqlite_db_records(path, "PRAGMA table_info(request_accept)")}
    select = ", ".join(column if column in present else f"NULL AS {column}"
                       for column in INCOMING_COLUMNS)
    return f"SELECT {select} FROM request_accept ORDER BY create_time, id"


@artifact_processor
def get_samsung_quick_share_transfers(context):
    data_list = []
    source_paths = []
    seen = set()
    for path, container in _databases(context.get_files_found()):
        source_paths.append(path)
        if does_table_exist_in_db(path, "devices") and _has_columns(
                path, "devices", ("transfer_request_id", "pin_code", "update_time")):
            has_internet = does_table_exist_in_db(path, "transfer_internet") and \
                _has_columns(path, "transfer_internet", ("request_id", "created_at")) and \
                _has_columns(path, "devices", ("request_id",))
            query = OUTGOING_QUERY.format(
                started="ti.created_at" if has_internet else "NULL",
                internet_join=("LEFT JOIN transfer_internet ti ON ti.request_id = devices.request_id\n"
                               if has_internet else ""))
            for row in get_sqlite_db_records(path, query):
                (started, created, updated, peer, file_name, size, mime, sent, total, failed, cancelled,
                 status, accept_result, pin, uri, share_id, device_pk) = row
                key = (container, "out", share_id, device_pk, file_name, uri)
                if key in seen:
                    continue
                seen.add(key)
                data_list.append((
                    _ms(started), _ms(created), _ms(updated), "Outgoing", peer or "", file_name or "",
                    size if size is not None else "", mime or "", sent, total, failed, cancelled,
                    "", status, accept_result, pin or "", uri or "", share_id, container[0],
                ))
        if does_table_exist_in_db(path, "request_accept") and _has_columns(
                path, "request_accept", ("receive_status", "accept_result", "id")):
            for row in get_sqlite_db_records(path, _incoming_query(path)):
                (created, device_name, sender_name, represent_name, plain_name, size,
                 total_bytes, total, downloaded, receive_status, accept_result, pin,
                 request_pk) = row
                file_name = represent_name or plain_name
                if size is None:
                    size = total_bytes
                key = (container, "in", request_pk, file_name, pin)
                if key in seen:
                    continue
                seen.add(key)
                if receive_status == 4 and accept_result == 0:
                    outcome = "Received"
                elif receive_status == 10 and accept_result == 1:
                    outcome = "Declined"
                else:
                    outcome = ""
                data_list.append((
                    "", _ms(created), "", "Incoming", device_name or sender_name or "",
                    file_name or "", size if size is not None else "", "", downloaded, total,
                    "", "", outcome, receive_status, accept_result, pin or "", "",
                    f"request_accept {request_pk}", container[0],
                ))

    data_headers = (
        ("Transfer Started", "datetime"),
        ("Share Created", "datetime"),
        ("Peer Updated", "datetime"),
        "Direction",
        "Peer Device Name",
        "File Name",
        ("File Size (bytes)", "number"),
        "MIME Type",
        ("Files Sent or Downloaded", "number"),
        ("Files Total", "number"),
        ("Files Failed", "number"),
        ("Files Cancelled", "number"),
        "Outcome",
        "Status (as stored)",
        "Accept Result (as stored)",
        "PIN",
        "Source URI",
        "Share or Request ID",
        "Android User",
    )
    return data_headers, data_list, "\n".join(sorted(set(source_paths)))


LINK_QUERY = """
SELECT box.create_time, box.expire_time, content.file_name, content.mime_type,
       content.file_size, content.width, content.height, box.url, content.hash, box.status,
       box.type, box.content_cnt, box.id, content.id
FROM box
LEFT JOIN content ON content.box_id = box.id
ORDER BY box.create_time, box.id, content.id
"""


@artifact_processor
def get_samsung_quick_share_link_shares(context):
    data_list = []
    source_paths = []
    seen = set()
    for path, container in _databases(context.get_files_found()):
        source_paths.append(path)
        if not (does_table_exist_in_db(path, "box") and does_table_exist_in_db(path, "content")):
            continue
        for row in get_sqlite_db_records(path, LINK_QUERY):
            (created, expires, file_name, mime, size, width, height, url, file_hash, status,
             box_type, content_count, box_pk, content_pk) = row
            key = (container, box_pk, content_pk, created, url)
            if key in seen:
                continue
            seen.add(key)
            data_list.append((
                _ms(created), _ms(expires), file_name or "", mime or "",
                size if size is not None else "", width, height, url or "", file_hash or "",
                content_count, status, box_type, box_pk, container[0],
            ))

    data_headers = (
        ("Created", "datetime"),
        ("Expires", "datetime"),
        "File Name",
        "MIME Type",
        ("File Size (bytes)", "number"),
        "Width",
        "Height",
        "Link URL",
        ("Hash (as stored)", "hash"),
        "Files in Link",
        "Status (as stored)",
        "Type (as stored)",
        "Box ID",
        "Android User",
    )
    return data_headers, data_list, "\n".join(sorted(set(source_paths)))

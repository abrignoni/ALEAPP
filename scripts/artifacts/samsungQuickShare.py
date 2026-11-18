"""Samsung Quick Share (com.samsung.android.app.sharelive) transfers and link shares.

Quick Share keeps its sharing state in databases/linkShare.db, a Room database. Nearby
transfers to and from other devices sit in shares, devices, transfer_request,
transfer_file and request_accept; shares made as a link sit in box and content.
"""

__artifacts_v2__ = {
    "get_samsung_quick_share_transfers": {
        "name": "Samsung Quick Share - Transfers",
        "description": (
            "Parses nearby Quick Share transfers from linkShare.db: one row per peer device a "
            "share was addressed to (outgoing) and one row per incoming request (received or "
            "declined), with the peer device name, the file name, size and type, the file "
            "counts, the PIN shown for the transfer and the stored status values."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Samsung Quick Share",
        "notes": (
            "Read from com.samsung.android.app.sharelive/databases/linkShare.db with its -wal. "
            "Outgoing rows come from the devices table (one row per peer device listed in a "
            "share), joined to shares on share_id for Share Created and to transfer_file on the "
            "device's transfer_request_id for the file. Incoming rows come from request_accept. "
            "Known data (samsung_a166u_a16_known_20261117, a Galaxy A16 sharing with a second "
            "test phone, actions and times logged during the session): one image and one text "
            "file sent, one text file received and one declined. Every logged transfer appears, "
            "and the file names, sizes, PINs and peer device name match the log. "
            "Outgoing: the two sent files have Files Sent 1 of Files Total 1. A third outgoing "
            "row, for a share sheet opened with the same peer listed and nothing sent, has every "
            "count 0, no file and Accept Result (as stored) -1. "
            "Share Created is shares.create_time and Peer Updated is devices.update_time, both "
            "milliseconds since the Unix epoch converted to UTC. On the known data both were "
            "53 to 88 seconds earlier than the logged moment the send finished; which event "
            "each records is not established. "
            "Incoming: request_accept stores no time on the known data (create_time NULL on "
            "both rows), so Share Created and Peer Updated are blank there. The received file "
            "had receive_status 4 and accept_result 0; the declined one receive_status 10 and "
            "accept_result 1. Outcome shows Received or Declined for exactly those two "
            "combinations and is blank for any other, which keeps the stored values in Status "
            "(as stored) and Accept Result (as stored). On an incoming row Files Sent or "
            "Downloaded is download_file_count, which held 0 on both rows, the received one "
            "included, so it is not a count of files saved. File Name on an incoming row is "
            "represent_file_name, or file_name where that is empty, and File Size is "
            "total_file_size, or total_bytes where the column is absent. request_accept "
            "columns differ between app versions (cookbook_a11 and samsunga53_a14 have no "
            "sender_name or total_file_size, sharon_a14 no sender_name); a missing one is read "
            "as blank. receiving_file held no rows, so the saved path of the received "
            "file is not in this database; on the known data it was in Download/Quick Share. "
            "Status (as stored) is devices.share_status on outgoing rows (4 on both sent "
            "files, 0 on the share with nothing sent). No other status values are decoded. "
            "Left out: shares rows that list no peer device (each send on the known data also "
            "made share rows with no device, two of them with secure_mode 1), transfer_internet "
            "and sending_request (request ids and a creation time, no file or peer), "
            "optional_meta and enhanced_share_items and enhanced_share_content (the sending "
            "app's preview metadata), and the peer IP addresses, keys and hashes in devices "
            "and request_accept. cached_devices, recent_recipient and app_usage_stats were "
            "empty on every registered image that holds linkShare.db. "
            "No registered image other than the known data holds a row in devices or "
            "request_accept. On samsung_a166u_a16_known_20261117 Peer Device Name held one "
            "value and Android User held 0 on all five rows (one peer phone, one Android user), "
            "and Files Failed and Files Cancelled were identical on every row: 0 on each "
            "outgoing row and blank on each incoming row, where request_accept has no such "
            "counts."
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
            "Parses Quick Share shares made as a link from linkShare.db: one row per file in a "
            "link share, with the link creation and expiry times, the link URL and the file "
            "name, type, size, dimensions and stored hash."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Samsung Quick Share",
        "notes": (
            "Read from the box (one row per link) and content (one row per file, box_id points "
            "to box.id) tables of com.samsung.android.app.sharelive/databases/linkShare.db. "
            "Created and Expires are box.create_time and box.expire_time, milliseconds since "
            "the Unix epoch converted to UTC. Link URL is box.url as stored. Hash (as stored) is "
            "content.hash; on sharon_a13 it held 64 hexadecimal characters and equalled "
            "content.cloud_hash, and which algorithm produced it is not established. Status (as "
            "stored) and Type (as stored) are box.status and box.type, not decoded. "
            "Exercised on one link share of one JPEG image, present on sharon_a13 (an older "
            "linkShare.db without the nearby-transfer tables) and with the same values on "
            "sharon_a14, a later image of the same owner. On every other registered image that "
            "holds linkShare.db the box table is empty. Whether the link "
            "still worked at extraction time is not recorded. transfer_info (upload progress "
            "per box) is not reported. Files received through a link are not exercised."
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
    if head.endswith("/data/data/"):
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
SELECT shares.create_time, devices.update_time, devices.device_name, transfer_file.file_name,
       transfer_file.file_size, transfer_file.mime_type, devices.file_sent_count,
       devices.file_total_count, devices.file_failed_count, devices.file_cancelled_count,
       devices.share_status, devices.accept_result, devices.pin_code, transfer_file.uri,
       devices.share_id, devices.id
FROM devices
LEFT JOIN shares ON shares.id = devices.share_id
LEFT JOIN transfer_file ON transfer_file.transfer_request_id = devices.transfer_request_id
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
            for row in get_sqlite_db_records(path, OUTGOING_QUERY):
                (created, updated, peer, file_name, size, mime, sent, total, failed, cancelled,
                 status, accept_result, pin, uri, share_id, device_pk) = row
                key = (container, "out", share_id, device_pk, file_name, uri)
                if key in seen:
                    continue
                seen.add(key)
                data_list.append((
                    _ms(created), _ms(updated), "Outgoing", peer or "", file_name or "",
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
                    _ms(created), "", "Incoming", device_name or sender_name or "",
                    file_name or "", size if size is not None else "", "", downloaded, total,
                    "", "", outcome, receive_status, accept_result, pin or "", "",
                    f"request_accept {request_pk}", container[0],
                ))

    data_headers = (
        ("Share Created", "datetime"),
        ("Peer Updated", "datetime"),
        "Direction",
        "Peer Device Name",
        "File Name",
        "File Size (bytes)",
        "MIME Type",
        "Files Sent or Downloaded",
        "Files Total",
        "Files Failed",
        "Files Cancelled",
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
        "File Size (bytes)",
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

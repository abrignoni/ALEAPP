__artifacts_v2__ = {
    "cff_searched_places": {
        "name": "SBB Mobile - Searched places",
        "description": "List of places searched in the past with last time used",
        "author": "jerome.arn@vd.ch",
        "creation_date": "2026-03-26",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Travel",
        "notes": (
            "Timestamps are rendered in UTC. The Type names for the stored 'a', 'p', 'c' "
            "and 's' values were established through testing; any other value is shown as "
            "stored."
        ),
        "paths": ('*/data/ch.sbb.mobile.*/databases/SbbMobile.db*'),
        "output_types": "standard",
        "html_columns": ['location of places (link)'],
        "artifact_icon": "search",
        "sample_data": {
            "galaxys10_a10": "Android 10 | ch.sbb.mobile.android.b2c vc 111004052 | 0 rows",
        }
    },
    "cff_search_history": {
        "name": "SBB Mobile - Search History",
        "description": "Search history records stored by the application",
        "author": "jerome.arn@vd.ch",
        "creation_date": "2026-03-26",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Travel",
        "notes": (
            "Timestamps are rendered in UTC. The Departure (type) and Destination (type) "
            "names for the stored 'a', 'p', 'c' and 's' values were established through "
            "testing; any other value is shown as stored. Result Coordinates are the "
            "latitude and longitude stored on the search row, which describe a place in the "
            "itinerary and not the location of the device when the search was made."
        ),
        "paths": ('*/data/ch.sbb.mobile.*/databases/SbbMobile.db*'),
        "output_types": "standard",
        "html_columns": ['Result Coordinates (link)'],
        "artifact_icon": "search",
        "sample_data": {
            "galaxys10_a10": "Android 10 | ch.sbb.mobile.android.b2c vc 111004052 | 4 rows",
        }
    },
    "cff_travel_cards": {
        "name": "SBB Mobile - Travel Cards",
        "description": "Information about public transportation pass linked to application",
        "author": "jerome.arn@vd.ch",
        "creation_date": "2026-03-26",
        "last_update_date": "2026-03-26",
        "requirements": "none",
        "category": "Travel",
        "notes": "",
        "paths": ('*/data/ch.sbb.mobile.*/databases/SbbMobile.db*'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "galaxys10_a10": "Android 10 | ch.sbb.mobile.android.b2c vc 111004052 | 0 rows",
        }
    },
    "cff_purchased_tickets": {
        "name": "SBB Mobile - Ticket Purchased recently",
        "description": "List of purchased tickets recorded in the PurchasedTickets table",
        "author": "jerome.arn@vd.ch",
        "creation_date": "2026-03-26",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Travel",
        "notes": (
            "Refund State shows the stored refundState value; a value of 'COMPLETE' is "
            "reported as 'Refunded' and every other value is shown as stored, because the "
            "meaning of the other states is not established."
        ),
        "paths": ('*/data/ch.sbb.mobile.*/databases/SbbMobile.db*'),
        "output_types": "standard",
        "artifact_icon": "star",
        "sample_data": {
            "galaxys10_a10": "Android 10 | ch.sbb.mobile.android.b2c vc 111004052 | 0 rows",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, \
    get_sqlite_db_records, logfunc, null_absent_columns
from scripts.html_safe import esc


@artifact_processor
def cff_purchased_tickets(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "SbbMobile.db")

    if source_path:
        query = '''
            SELECT
                validFrom,
                validUntil,
                traveler,
                CASE
                    WHEN refundState == "COMPLETE" THEN "Refunded"
                    ELSE refundState
                END AS refundState,
                paymentMethodType,
                displayInfo_ticketType,
                displayInfo_titleLine_firstSegment,
                displayInfo_titleLine_lastSegment
            FROM
                PurchasedTickets
        '''

        data_headers = ("Valid from", "Valid until", "Traveler", "Refund State",
                        "Payment method", "Ticket description", "Ticket departure", "Ticket destination")
        db_records = list(get_sqlite_db_records(source_path, null_absent_columns(source_path, query)))

        return data_headers, db_records, source_path
    else:
        logfunc('No Data')


@artifact_processor
def cff_searched_places(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "SbbMobile.db")
    data_list = []

    if source_path:
        query = '''
            SELECT
                datetime(timestamp/1000, 'unixepoch'),
                title,
                CASE
                    WHEN favorite THEN "True"
                    ELSE "False"
                END AS favorite,
                CASE
                    WHEN type == "a" THEN "Address"
                    WHEN type == "p" THEN "POI"
                    WHEN type == "c" THEN "Coordinate"
                    WHEN type == "s" THEN "Station"
                    ELSE type
                END AS type,
                latitude,
                longitude
            FROM
                SearchedPlaces
        '''

        data_headers = (("Searched timestamp (UTC)", "datetime"), "Title", "Is favorite", "Type",
                        "location of places (link)")
        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        data_list = [
            record[:4] + (coordinate_to_osm(record[4], record[5]),)
            for record in db_records]

        return data_headers, data_list, source_path
    else:
        logfunc('No Data')


@artifact_processor
def cff_search_history(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "SbbMobile.db")
    data_list = []

    if source_path:
        query = '''
                SELECT
                datetime(timestamp/1000, 'unixepoch'),
                departure,
                CASE
                    WHEN departureType == "a" THEN "Address"
                    WHEN departureType == "p" THEN "POI"
                    WHEN departureType == "c" THEN "Coordinate"
                    WHEN departureType == "s" THEN "Station"
                    ELSE departureType
                END AS departureType,
                target,
                CASE
                    WHEN targetType == "a" THEN "Address"
                    WHEN targetType == "p" THEN "POI"
                    WHEN targetType == "c" THEN "Coordinate"
                    WHEN targetType == "s" THEN "Station"
                    ELSE targetType
                END AS targetType,
                latitude,
                longitude
            FROM
                SearchHistory
        '''

        data_headers = (("Search timestamp (UTC)", "datetime"), "Departure", "Departure (type)", "Destination",
                        "Destination (type)", "Result Coordinates (link)")
        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        data_list = [
            record[:5] + ((coordinate_to_osm(record[5], record[6]),) if record[5] and record[6] else ("",))
            for record in db_records
        ]

        return data_headers, data_list, source_path
    else:
        logfunc('No Data')


@artifact_processor
def cff_travel_cards(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "SbbMobile.db")
    data_list = []

    if source_path:
        query = '''
            SELECT
                name,
                type,
                contract_id,
                valid_from,
                valid_to,
                contract_state
            FROM
                SwissPassTravelCards
        '''

        data_headers = ("Name", "Type", "Contract ID", "Valid From", "Valid To", "Contract state")
        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        data_list = [record[:6] for record in db_records]
        return data_headers, data_list, source_path
    else:
        logfunc('No Data')


def coordinate_to_osm(lat, lon):
    return f"https://www.openstreetmap.org/?mlat={esc(lat)}&mlon={esc(lon)}&zoom=15"

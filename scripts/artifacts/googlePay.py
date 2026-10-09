# pylint: disable=W0613
"""Parses Google Pay payment history and related party information.

The parser reads conversation cards stored in Google Pay's SQLite database and
decodes protobuf fields used for payment transactions, UPI parties and
transaction metadata. It also supports the older PaisaUserDatabase.db
directory used by some Google Pay versions.
"""

__artifacts_v2__ = {
    "get_googlePay_transactions": {
        "name": "Google Pay Transactions",
        "description": "Parses Google Pay UPI payments from its conversation cards (data.db): date, sent or "
                       "received, amount, status, the counterparty's name and UPI ID, the UPI reference and the "
                       "device owner's UPI ID and account.",
        "author": "@prcharan592",
        "creation_date": "2026-09-28",
        "last_update_date": "2026-09-28",
        "requirements": "none",
        "category": "Google Pay",
        "notes": "Owner is the device's Google Pay user: the payer of a sent payment and the payee of a received "
                 "one. Counterparty Name at Bank is the name the UPI ID is registered to, which can differ from "
                 "the name Google Pay showed.",
        "paths": ('*/com.google.android.apps.nbu.paisa.user/files/.mfca/sessions/*/conversation/data.db*',),
        "output_types": "standard",
        "artifact_icon": "credit-card",
    },
    "get_googlePay_upi_ids": {
        "name": "Google Pay UPI IDs",
        "description": "Parses every UPI ID Google Pay's conversation cards (data.db) name - the people and "
                       "merchants the owner paid, was paid by or talked to, and the owner's own - with the name "
                       "shown, the name at the bank, the masked phone and how many cards and payments name it.",
        "author": "@prcharan592",
        "creation_date": "2026-09-29",
        "last_update_date": "2026-09-29",
        "requirements": "none",
        "category": "Google Pay",
        "notes": "Device Owner is Yes for a UPI ID the owner paid from or was paid into. First and Last Seen are "
                 "the times of the first and last card that names it, not of a payment.",
        "paths": ('*/com.google.android.apps.nbu.paisa.user/files/.mfca/sessions/*/conversation/data.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "get_googlePay_people": {
        "name": "Google Pay People",
        "description": "Parses the people and merchants in an older Google Pay's directory (PaisaUserDatabase.db): "
                       "name, UPI IDs and the names on their accounts, mobile number, linked bank account, and "
                       "the last message in the conversation with them.",
        "author": "@prcharan592",
        "creation_date": "2026-09-29",
        "last_update_date": "2026-09-29",
        "requirements": "none",
        "category": "Google Pay",
        "notes": "A person's name is the one on their Google Pay profile, not a name the owner saved. Names at "
                 "Bank are the names the UPI IDs are registered to.",
        "paths": ('*/com.google.android.apps.nbu.paisa.user/files/accounts/*/PaisaUserDatabase.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
    },
}

import datetime
import os
import re
import shutil
import sqlite3
import tempfile

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

#: The state codes, each named by what the card shows beside it on the live cases.
STATES = {
    10: 'Completed',  # the completed-payment mark
    # Shown like a completed payment and never with a failure message. 15 on
    8: 'Completed',
    9: 'Failed',      # the red cross, "Payment failed. Insufficient bank balance.", "Invalid UPI PIN"
    6: 'Failed',
    14: 'Declined',   # a request turned down or left to lapse
    2: 'Pending',     # "action required": a request not yet answered
}
#: Which way the money went, from the device owner's side (payment field 13).
DIRECTIONS = {1: 'Received', 2: 'Sent'}

_CARD = 2
_PAYMENT, _BILL_PAYMENT = 50, 54
#: In a payment: the transaction, the note, the transaction as last updated,
#: the UPI leg, and the direction.
_TXN, _NOTE, _LATEST, _UPI, _DIRECTION = 1, 2, 6, 7, 13
#: In a transaction.
_ID, _TIME_MS, _AMOUNT, _STATE, _OTHER_END, _PROBLEM = 1, 2, 3, 5, 9, 14
#: In the UPI leg: the reference number, then payer and payee, each an account
#: at field 10000 holding its UPI ID, masked account number, name, bank and app.
_REFERENCE, _PAYER, _PAYEE, _ACCOUNT = 1, 4, 5, 10000
_VPA, _ACCOUNT_NO, _HOLDER, _BANK, _APP = 1, 2, 4, 6, 8
#: The line the card shows: "To <name>", "From <name>", "Self transfer", "<merchant> requested money from you".
_HEADLINE = (75, 1, 1, 2)
#: Who posted the card (2.6) and the conversation's other end (2.81): a person's profile at .8 - name 1,
#: masked phone 3, UPI instrument 5.1 (UPI ID 1, name at the bank 3) - or a merchant at 2.81.10, its name
#: A request turns both round (_owner_from_poster).
_SENDER, _PEER = (_CARD, 6, 8), (_CARD, 81, 8)
_MERCHANT = (_CARD, 81, 10)
#: A profile outside the card body that some cards carry (an extension field).
_EXTRA_PROFILE = (364499449, 3, 8)


def _varint(buf, at):
    """(value, next offset) of the varint at ``at``; raises ValueError when it runs off the end."""
    value, shift = 0, 0
    while True:
        if at >= len(buf) or shift > 63:
            raise ValueError("truncated varint")
        byte = buf[at]
        value |= (byte & 0x7F) << shift
        at += 1
        if not byte & 0x80:
            return value, at
        shift += 7


def message(buf):
    """{field number: [values]} of one protobuf message, or None when ``buf`` is not a whole one.

    Varints and fixed-width fields come back as ints, length-delimited fields as
    bytes. Whether those bytes are text or a nested message is decided by what
    the field is known to hold, never guessed from the bytes: a short string
    such as a biller's name also parses as a valid message.
    """
    if isinstance(buf, dict):
        return buf
    if not isinstance(buf, (bytes, bytearray, memoryview)):
        return None
    buf, at, out = bytes(buf), 0, {}
    try:
        while at < len(buf):
            key, at = _varint(buf, at)
            field, wire = key >> 3, key & 7
            if field == 0:
                return None
            if wire == 0:
                value, at = _varint(buf, at)
            elif wire in (1, 5):
                width = 8 if wire == 1 else 4
                value, at = int.from_bytes(buf[at:at + width], 'little'), at + width
            elif wire == 2:
                size, at = _varint(buf, at)
                value, at = buf[at:at + size], at + size
            else:
                return None
            if at > len(buf):
                return None
            out.setdefault(field, []).append(value)
    except ValueError:
        return None
    return out


def _sub(msg, *path):
    """The message at ``path`` (the first at each level), parsed; {} when any step is missing."""
    msg = message(msg) or {}
    for field in path:
        values = msg.get(field)
        msg = (message(values[0]) or {}) if values else {}
    return msg


def _value(msg, *path):
    values = _sub(msg, *path[:-1]).get(path[-1])
    return values[0] if values else None


def _int(msg, *path):
    value = _value(msg, *path)
    return value if isinstance(value, int) else None


def _text(msg, *path):
    value = _value(msg, *path)
    if not isinstance(value, bytes):
        return ''
    try:
        return value.decode('utf-8').strip()
    except UnicodeDecodeError:
        return ''


def _money(amount):
    """(amount, currency) of a google.type.Money: units plus nanos, to the paisa."""
    if not amount:
        return '', ''
    units, nanos = _int(amount, 2) or 0, _int(amount, 3) or 0
    if units >= 1 << 63:
        units -= 1 << 64      # int64 on the wire
    if nanos >= 1 << 63:
        nanos -= 1 << 64      # int32, sign-extended to ten bytes
    return round(units + nanos / 1e9, 2), _text(amount, 1)


def _utc(ms):
    try:
        if ms is None:
            return ''
        return datetime.datetime.fromtimestamp(int(ms) / 1000, datetime.timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _committed_rows(path, query):
    """The rows of ``query`` as the app last committed them.

    A read-only connection cannot roll back a hot journal - one left by a write
    the app was part-way through when the phone was imaged - and then refuses
    to read at all ("attempt to write a readonly database"). One phone's
    data.db came with a 251,464-byte data.db-journal. The database and its
    journal are copied aside and opened there, which rolls the unfinished write
    back: the state the app itself would read on its next start.
    """
    db = open_sqlite_db_readonly(path)
    if db is None:
        return []
    try:
        return db.execute(query).fetchall()
    except sqlite3.OperationalError as exc:
        journal = path + '-journal'
        if 'readonly' not in str(exc).lower() or not os.path.exists(journal):
            raise
    finally:
        db.close()
    with tempfile.TemporaryDirectory() as scratch:
        copy = os.path.join(scratch, os.path.basename(path))
        shutil.copyfile(path, copy)
        shutil.copyfile(journal, copy + '-journal')
        db = sqlite3.connect(copy)
        try:
            return db.execute(query).fetchall()
        finally:
            db.close()


def _tables(path):
    return {name for (name,) in _committed_rows(path, "SELECT name FROM sqlite_master WHERE type='table'")}


def _payment(card):
    """(transaction, UPI leg, direction code, note) of a payment or bill card, or None for any other card."""
    body = _sub(card, _CARD)
    if _PAYMENT in body:
        payment = _sub(body, _PAYMENT)
        txn = _sub(payment, _LATEST, _TXN) or _sub(payment, _TXN)
        return txn, _sub(payment, _UPI, 2), _int(payment, _DIRECTION), _text(payment, _NOTE, 1)
    if _BILL_PAYMENT in body:
        # A bill or a recharge: always paid out.
        return _sub(body, _BILL_PAYMENT, 1, 2, 1), _sub(body, _BILL_PAYMENT, 2, 1, 2), 2, ''
    return None


def _leg_owner(blob):
    """Returns the device owner's UPI ID identified from a payment card."""
    found = _payment(blob)
    if found is None:
        return ''
    _txn, leg, direction_code, _note = found
    side = {'Sent': _PAYER, 'Received': _PAYEE}.get(DIRECTIONS.get(direction_code, ''))
    return _text(leg, side, _ACCOUNT, _VPA) if side else ''


def _leg_owners(cards):
    """Every owner's UPI ID the UPI legs of these (card_id, blob, ...) rows name, lower-cased."""
    return {v.lower() for v in (_leg_owner(row[1]) for row in cards) if v}


def _other_ends(blob, txn, leg, direction):
    """Every UPI ID the card gives the payment's other end - its profile, its side of the UPI leg - and the
    conversation's other end (a person at 2.81.8, a merchant at 2.81.10), lower-cased."""
    vpas = {_text(i, 1) for path in ((txn, _OTHER_END, 8, 5, 1), (blob, *_PEER, 5, 1)) for i in _every(*path)}
    vpas |= set(map(_as_text, _every(blob, *_MERCHANT, 5, 1)))
    side = {'Sent': _PAYEE, 'Received': _PAYER}.get(direction)
    if side:
        vpas.add(_text(leg, side, _ACCOUNT, _VPA))
    return {v.lower() for v in vpas if v}


def _owner_from_poster(blob, txn, leg, direction, leg_owners):
    """The card poster's UPI ID (2.6.8) when the poster is the device owner, else ''.

    """
    poster = _text(blob, *_SENDER, 5, 1, 1)
    if not poster or poster.lower() in _other_ends(blob, txn, leg, direction):
        return ''
    if direction == 'Sent':
        return '' if 'requested' in _text(blob, _CARD, *_HEADLINE).lower() else poster
    return poster if direction == 'Received' and poster.lower() in leg_owners else ''


def _row(card_id, blob, created_ms, leg_owners=frozenset()):
    found = _payment(blob)
    if found is None:
        return None
    txn, leg, direction_code, note = found
    amount, currency = _money(_sub(txn, _AMOUNT))
    if amount == '':
        return None
    direction = DIRECTIONS.get(direction_code, '')
    payer, payee = _sub(leg, _PAYER, _ACCOUNT), _sub(leg, _PAYEE, _ACCOUNT)
    owner, other = {'Sent': (payer, payee), 'Received': (payee, payer)}.get(direction, ({}, {}))

    # The other end as Google Pay shows it: a person with their UPI ID, or a merchant.
    person = _sub(txn, _OTHER_END, 8)
    instrument = _sub(person, 5, 1)
    name = _text(person, 1) or _text(txn, _OTHER_END, 10, 1) or _text(other, _HOLDER)
    merchant_vpa = _text(blob, *_MERCHANT, 5, 1) if name and _text(blob, *_MERCHANT, 1) == name else ''
    owner_vpa = _text(owner, _VPA) or _owner_from_poster(blob, txn, leg, direction, leg_owners)
    state = _int(txn, _STATE, 1)
    problem = re.sub(r'<[^>]+>', '', _text(txn, _PROBLEM, 3, 7)).strip() or _text(txn, _PROBLEM, 3, 5)
    txn_id = _int(txn, _ID)
    reference = _text(leg, _REFERENCE)
    row = (
        _utc(_int(txn, _TIME_MS) or created_ms), direction, amount, currency,
        STATES.get(state, f'Unknown ({state})' if state is not None else ''),
        name, _text(instrument, 1) or _text(other, _VPA) or merchant_vpa,
        _text(instrument, 3) or _text(other, _HOLDER),
        _text(instrument, 5) or _text(other, _APP), _text(other, _ACCOUNT_NO), _text(other, _BANK),
        _text(blob, _CARD, *_HEADLINE), note, problem, reference,
        owner_vpa, _text(owner, _ACCOUNT_NO), _text(owner, _BANK),
        state if state is not None else '', str(txn_id) if txn_id is not None else '', card_id,
    )
    # Which of two cards for one payment to keep: the one with the reference
    # number, then the one in the payment's own conversation rather than its
    # ":original_peer" copy.
    rank = (bool(reference), not str(card_id).endswith(':original_peer'))
    return row, txn_id, rank


@artifact_processor
def get_googlePay_transactions(context):
    files_found = context.get_files_found()
    by_payment = {}
    sources = []
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.basename(file_found) != 'data.db':
            continue  # -journal, -wal, -shm
        if 'conversation_card' not in _tables(file_found):
            continue
        sources.append(file_found)
        rows = _committed_rows(file_found, '''
            SELECT card_id, paisa_conversation_card, card_creation_timestamp
            FROM conversation_card
            ORDER BY card_creation_timestamp
        ''')
        owners = _leg_owners(rows)
        for card_id, blob, created_ms in rows:
            got = _row(card_id, blob, created_ms, owners)
            if got is None:
                continue
            row, txn_id, rank = got
            key = (file_found, txn_id if txn_id is not None else card_id)
            if key not in by_payment or rank > by_payment[key][1]:
                by_payment[key] = (row, rank)

    data_headers = (
        ('Transaction Date', 'datetime'), 'Direction', 'Amount', 'Currency', 'Status',
        'Counterparty', 'Counterparty UPI ID', 'Counterparty Name at Bank', 'Counterparty UPI App',
        'Counterparty Account', 'Counterparty Bank', 'Description', 'Note', 'Failure Reason', 'UPI Reference',
        'Owner UPI ID', 'Owner Account', 'Owner Bank', 'Status Code', 'Transaction ID', 'Card ID',
    )
    return data_headers, [row for row, _rank in by_payment.values()], '\n'.join(sources)


def _masked_phone(profile):
    """"+91 ******1234" from a profile's masked phone (field 3: country code, masked number)."""
    number = _text(profile, 3, 2)
    code = _text(profile, 3, 1)
    return f'+{code} {number}' if number and code else number


def _every(msg, *path):
    """Every value at ``path``, through repeated fields: a person can hold several UPI instruments."""
    level = [msg]
    for field in path:
        level = [v for m in level for v in (message(m) or {}).get(field, [])]
    return level


def _as_text(value):
    try:
        return value.decode('utf-8').strip() if isinstance(value, bytes) else ''
    except UnicodeDecodeError:
        return ''


def _parties(blob):
    """(UPI ID, name shown, name at the bank, masked phone, kind) of each party a card names.

    The card's poster, the conversation's other end (a person or a merchant), a profile in the extension
    field, the payment's other end and both ends of its UPI leg - each UPI instrument of each. Only a UPI
    ID the card holds as a whole field is read, never one inside a line of text.
    """
    out = []
    people = [p for path in (_SENDER, _PEER, _EXTRA_PROFILE) for p in _every(blob, *path)]
    found = _payment(blob)
    if found is not None:
        people += _every(found[0], _OTHER_END, 8)
    for profile in people:
        name, phone = _text(profile, 1), _masked_phone(profile)
        for instrument in _every(profile, 5, 1):
            vpa = _text(instrument, 1)
            if vpa:
                out.append((vpa, name, _text(instrument, 3), phone, 'Person'))
    for shop in _every(blob, *_MERCHANT):
        for vpa in map(_as_text, _every(shop, 5, 1)):
            if vpa:
                out.append((vpa, _text(shop, 1), '', '', 'Merchant'))
    if found is not None:
        for side in (_PAYER, _PAYEE):
            account = _sub(found[1], side, _ACCOUNT)
            if _text(account, _VPA):
                out.append((_text(account, _VPA), '', _text(account, _HOLDER), '', ''))
    return out


def _owners(blob, leg_owners=frozenset()):
    """Returns UPI IDs identified as belonging to the device owner."""
    found = _payment(blob)
    if found is None:
        return set()
    txn, leg, direction_code, _note = found
    owned = {_leg_owner(blob), _owner_from_poster(blob, txn, leg, DIRECTIONS.get(direction_code, ''), leg_owners)}
    return {v.lower() for v in owned if v}


@artifact_processor
def get_googlePay_upi_ids(context):
    files_found = context.get_files_found()
    """One row per UPI ID the conversation cards name.

    The payments list holds only the UPI IDs a payment names. On copies of four phones' databases the
    """
    data_list = []
    sources = []
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.basename(file_found) != 'data.db':
            continue  # -journal, -wal, -shm
        if 'conversation_card' not in _tables(file_found):
            continue
        seen, owners = {}, set()
        cards = _committed_rows(file_found, '''
                SELECT card_id, paisa_conversation_card, card_creation_timestamp
                FROM conversation_card ORDER BY card_creation_timestamp''')
        leg_owners = _leg_owners(cards)
        for card_id, blob, created_ms in cards:
            found = _payment(blob)
            txn_id = _int(found[0], _ID) if found is not None else None
            owners |= _owners(blob, leg_owners)
            for vpa, name, bank_name, phone, kind in _parties(blob):
                entry = seen.setdefault(vpa.lower(), {
                    'vpa': vpa, 'names': {}, 'bank_names': {}, 'phones': {}, 'kinds': set(), 'cards': set(),
                    'payments': set(),
                    'first': created_ms if isinstance(created_ms, int) and created_ms > 0 else None,
                    'last': created_ms if isinstance(created_ms, int) and created_ms > 0 else None})
                for key, value in (('names', name), ('bank_names', bank_name), ('phones', phone)):
                    if value:
                        entry[key][value] = entry[key].get(value, 0) + 1
                if kind:
                    entry['kinds'].add(kind)
                entry['cards'].add(card_id)
                if txn_id is not None:
                    entry['payments'].add(txn_id)
                if isinstance(created_ms, int) and created_ms > 0:
                    if entry['first'] is None:
                        entry['first'] = created_ms
                    else:
                        entry['first'] = min(entry['first'], created_ms)
                    if entry['last'] is None:
                        entry['last'] = created_ms
                    else:
                        entry['last'] = max(entry['last'], created_ms)

        def most(counts):
            return max(counts.items(), key=lambda kv: (kv[1], kv[0]))[0] if counts else ''
        rows = [(
            _utc(e['last']), e['vpa'], most(e['names']), most(e['bank_names']), most(e['phones']),
            'Merchant' if 'Merchant' in e['kinds'] else 'Person' if e['kinds'] else '',
            'Yes' if key in owners else '', len(e['cards']), len(e['payments']), _utc(e['first']),
        ) for key, e in seen.items()]
        if rows:
            sources.append(file_found)
        data_list.extend(sorted(rows, key=lambda r: str(r[0]), reverse=True))

    data_headers = (
        ('Last Seen', 'datetime'), 'UPI ID', 'Name', 'Name at Bank', 'Masked Phone', 'Kind', 'Device Owner',
        'Cards', 'Payments', ('First Seen', 'datetime'),
    )
    return data_headers, data_list, '\n'.join(sources)


def _columns(db, table):
    return {row[1] for row in db.execute(f'PRAGMA table_info("{table}")')}


def _select(db, table, wanted, alias):
    """``alias.column`` for each wanted column the table has, NULL for one it lacks: an older or newer
    Google Pay that drops or renames a column loses that column, not the table."""
    have = _columns(db, table)
    return ', '.join(f'{alias}.{c}' if c in have else 'NULL' for c in wanted)


def _stamp(value, scale):
    try:
        return _utc(int(value) * scale) if value else ''
    except (TypeError, ValueError):
        return ''


def _number(code, national):
    national = str(national).strip() if national not in (None, '') else ''
    return f'+{code} {national}' if national and code not in (None, '') else national


#: The directory's tables, and the columns read from each.
_ACTORS = ('actor_id', 'actor_is_blocked')
_USERS = ('user_actor_id', 'user_name', 'user_masked_phone_number_country_code',
          'user_masked_phone_number_national_number', 'user_email', 'user_phone_number_country_code',
          'user_phone_number_national_number', 'user_creation_time_seconds')
_MERCHANTS = ('merchant_actor_id', 'merchant_name', 'merchant_official_name', 'merchant_website',
              'merchant_contact_page_url', 'merchant_contact_email_address', 'merchant_phone_number_country_code',
              'merchant_phone_number_national_number')
_INSTRUMENTS = ('actor_id', 'vpa', 'name_on_account')
_BANK_ACCOUNTS = ('account_owner_actor_id', 'ifsc_code', 'masked_account_number', 'bank_name')
_CONVERSATIONS = ('peer_actor_id', 'last_message_creation_timestamp')


def _directory(db):
    """Builds a normalized directory of people, merchants and payment accounts."""
    tables = {name for (name,) in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}

    def rows(table, wanted):
        if table not in tables:
            return []
        try:
            return db.execute(f'SELECT {_select(db, table, wanted, "t")} FROM "{table}" t').fetchall()
        except sqlite3.Error as exc:
            try:
                logfunc(f'Google Pay People: {table} not read: {exc}')
            except OSError:       # the log writes to the last run's report folder: never why the rest is lost
                print(f'Google Pay People: {table} not read: {exc}')
            return []

    actors = {}

    def actor(actor_id):
        return actors.setdefault(actor_id, {
            'kind': '', 'name': '', 'official': '', 'mobile': '', 'masked': '', 'email': '', 'web': '',
            'joined': '', 'blocked': None, 'vpas': [], 'bank_names': [], 'bank': '', 'last': 0, 'chats': 0})
    for actor_id, blocked in rows('ACTOR_TABLE', _ACTORS):
        actor(actor_id)['blocked'] = blocked
    for actor_id, name, masked_cc, masked, email, cc, national, joined in rows('USER_TABLE', _USERS):
        actor(actor_id).update({'kind': 'Person', 'name': _s(name), 'masked': _number(masked_cc, masked),
                                'mobile': _number(cc, national), 'email': _s(email), 'joined': _stamp(joined, 1000)})
    for actor_id, name, official, web, page, email, cc, national in rows('MERCHAT_TABLE', _MERCHANTS):
        actor(actor_id).update({'kind': 'Merchant', 'name': _s(name), 'official': _s(official),
                                'web': _s(web) or _s(page), 'email': _s(email), 'mobile': _number(cc, national)})
    for actor_id, vpa, holder in sorted(rows('INSTRUMENT_TABLE', _INSTRUMENTS), key=lambda r: (str(r[0]), str(r[1]))):
        a = actor(actor_id)
        for key, value in (('vpas', _s(vpa)), ('bank_names', _s(holder))):
            if value and value not in a[key]:
                a[key].append(value)
    for actor_id, ifsc, number, bank in rows('BANK_ACCOUNT_TABLE', _BANK_ACCOUNTS):
        actor(actor_id)['bank'] = ' '.join(x for x in (_s(bank), _s(number) and f'...{_s(number)}',
                                                         _s(ifsc) and f'({_s(ifsc)})') if x)
    for actor_id, last in rows('CONVERSATION_INFO_TABLE', _CONVERSATIONS):
        if actor_id:
            a = actor(actor_id)
            a['chats'] += 1
            if isinstance(last, int):
                a['last'] = max(a['last'], last)
    actors.pop(None, None)
    return actors


@artifact_processor
def get_googlePay_people(context):
    files_found = context.get_files_found()
    """One row per person or merchant in PaisaUserDatabase.db, the directory an older Google Pay kept.

    """
    data_list = []
    sources = []
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.basename(file_found) != 'PaisaUserDatabase.db':
            continue  # -wal, -shm, -journal
        db = open_sqlite_db_readonly(file_found)
        if db is None:
            continue
        try:
            actors = _directory(db)
        finally:
            db.close()
        rows = [(
            _stamp(a['last'], 1), a['kind'], a['name'], a['official'], ', '.join(a['vpas']),
            ', '.join(a['bank_names']), a['mobile'], a['masked'], a['bank'], a['email'], a['web'], a['joined'],
            {0: 'No', 1: 'Yes'}.get(a['blocked'], ''), a['chats'], actor_id,
        ) for actor_id, a in actors.items()]
        if rows:
            sources.append(file_found)
        data_list.extend(sorted(rows, key=lambda r: str(r[0]), reverse=True))

    data_headers = (
        ('Last Message', 'datetime'), 'Kind', 'Name', 'Official Name', 'UPI IDs', 'Names at Bank',
        'Mobile Number', 'Masked Mobile', 'Bank Account', 'Email', 'Website', ('Joined Google Pay', 'datetime'),
        'Blocked', 'Conversations', 'Actor ID',
    )
    return data_headers, data_list, '\n'.join(sources)


def _s(value):
    return str(value).strip() if value not in (None, '') else ''

"""Actual SQLite/protobuf fixtures for neutral legacy-store record evidence."""
import base64
import pathlib
import sqlite3
from scripts import blackboxprotobuf

MISSING = object()
PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGMQ0bABAADMAHm9FcOvAAAAAElFTkSuQmCC')


def wire(code=5, group=False, incoming=True, media=False):
    value = {'1':b'media-message' if media else b'message', '2':1700000000000,
             '3':b'local', '4':{'1':b'other'}, '6':0, '10':b'MMS image' if media else b'body'}
    types = {'1':{'name':'','type':'bytes'},'2':{'name':'','type':'int'},'3':{'name':'','type':'bytes'},
             '4':{'name':'','type':'message','message_typedef':{'1':{'name':'','type':'bytes'}}},
             '6':{'name':'','type':'int'},'10':{'name':'','type':'bytes'}}
    if code is not MISSING:
        value['13']=code;types['13']={'name':'','type':'int'}
    if group:
        value['15']={'1':b'group body','4':[{'1':b'peer-one'},{'1':b'peer-two'}]}
        types['15']={'name':'','type':'message','message_typedef':{'1':{'name':'','type':'bytes'},
                    '4':{'name':'','type':'message','message_typedef':{'1':{'name':'','type':'bytes'}}},
                    '5':{'name':'','type':'bytes'}}}
        if incoming:value['15']['5']=b'peer-one'
    return bytes(blackboxprotobuf.encode_message(value,types))


def rows_for(kind):
    if kind=='SAFE':
        return [(wire(5,media=True),'t-in'),(wire(6),'t-out'),(wire(group=True),'g-in'),
                (wire(group=True,incoming=False),'g-out'),(wire(0),'x-call'),(wire(3),''),
                (wire(99),'t-unknown'),(wire(0),'x-call'),(wire(MISSING),'x-missing')]
    if kind=='BOUNDARIES':
        return [(wire(5),'t-first'),(wire(0),None),(wire(0),7),(wire(0),b'id-bytes'),
                (wire(MISSING),'t-missing'),(b'\xff','x-corrupt'),(None,'x-null-blob'),
                ('stored text','x-text-blob'),(wire(0),'t-unknown'),(wire(6),'t-last')]
    if kind=='NEW_ONLY':
        return [(b'\xff','t-corrupt'),(b'\x0f','t-badwire'),(b'\r\x01','t-shortfixed'),
                (wire(5),'t-healthy'),(wire(0),'x-later')]
    raise ValueError(kind)


def make_database(root, kind='SAFE', prefix='data/data', account='1'):
    path=pathlib.Path(root)/prefix/'com.google.android.apps.googlevoice/files/accounts'/account/'LegacyMsgDbInstance.db'
    path.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(path);db.execute('CREATE TABLE message_t(message_blob,conversation_id)')
    rows=rows_for(kind);db.executemany('INSERT INTO message_t VALUES(?,?)',rows);db.commit();db.close()
    if kind=='SAFE':
        media=pathlib.Path(root)/prefix/'com.google.android.apps.googlevoice/cache/Photo MMS images/media-message-14.png'
        media.parent.mkdir(parents=True,exist_ok=True);media.write_bytes(PNG)
    return path,rows

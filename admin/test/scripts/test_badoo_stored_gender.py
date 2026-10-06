"""Stored gender codes keep SQLite values instead of unsupported interpretations."""
from pathlib import Path
import sqlite3
import tempfile
import unittest
from scripts.artifacts.BadooChat import get_badoo_chat
from admin.test.scripts.test_history_doclist_all_sources import Context

VALUES=[None,0,1,2,-1,99,'','0','custom',2]


def create_badoo_fixture(root, empty=False):
    path=Path(root)/'data/data/com.badoo.mobile/databases/ChatComDatabase'
    path.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(path)
    db.execute('CREATE TABLE conversation_info(user_id,gender,user_name,user_image_url,age,user_photos,work,education,encrypted_user_id)')
    for index,value in enumerate([] if empty else VALUES):
        if index==9:
            index=3  # A repeated source record must survive without deduplication.
        db.execute('INSERT INTO conversation_info VALUES(?,?,?,?,?,?,?,?,?)',
                   (index,value,'name '+str(index),'https://example.invalid/image',20,
                    '[{"url":"https://example.invalid/photo"}]' if index%2 else 'invalid',
                    'work','education','encrypted '+str(index)))
    db.commit()
    db.close()
    return str(path)


class TestBadooStoredGender(unittest.TestCase):
    def test_stored_values_types_and_repeated_codes(self):
        with tempfile.TemporaryDirectory() as root:
            path=create_badoo_fixture(root)
            headers,rows,_=get_badoo_chat.__wrapped__(Context(root,[path]))
            with sqlite3.connect(path) as db:
                source=db.execute('SELECT user_id,gender,user_name,user_image_url,age,user_photos,work,education,encrypted_user_id FROM conversation_info').fetchall()
            self.assertEqual(headers[1],'Gender (as stored)')
            self.assertEqual([row[1] for row in rows],VALUES)
            self.assertEqual([type(row[1]) for row in rows],[type(v) for v in VALUES])
            self.assertEqual(len(rows),10)
            self.assertEqual(rows[-1],rows[3])
            for row,stored in zip(rows,source):
                self.assertEqual(row[:5],stored[:5])
                self.assertEqual(row[6:],stored[6:])
                self.assertEqual(row[5],'' if stored[5]=='invalid' else 'https://example.invalid/photo')

    def test_empty_table_remains_empty(self):
        with tempfile.TemporaryDirectory() as root:
            path=create_badoo_fixture(root,empty=True)
            self.assertEqual(get_badoo_chat.__wrapped__(Context(root,[path]))[1],[])

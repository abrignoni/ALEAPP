"""Raw code transparency preserves interpreted rows and independent evidence sources."""
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
from scripts.artifacts import AIChatbotNovaHistory as nova
from admin.test.scripts.test_history_doclist_all_sources import Context

CODES=[None,0,1,2,-1,99,'custom']
FUNCTIONS=[nova.nova_chatbot_history_detail,nova.nova_chatbot_documents,nova.nova_chatbot_images]


def create_nova_codes_fixture(root):
    root=Path(root)
    paths=[]
    for prefix in ['data/data','data/user/10']:
        path=root/prefix/'com.scaleup.chatai/databases/chat-ai.db'
        path.parent.mkdir(parents=True,exist_ok=True)
        db=sqlite3.connect(path)
        db.execute('CREATE TABLE History(id,UUID,title,chatBotModel,assistantId,softDeleted)')
        db.execute('CREATE TABLE HistoryDetail(id,UUID,historyID,type,text,token,reasoningContent,createdAt,lastModifiedAt,syncState,syncRetryCount)')
        db.execute('CREATE TABLE HistoryDetailDocument(id,historyDetailID,url,name,type,size,mimeType)')
        db.execute('CREATE TABLE HistoryDetailImage(id,historyDetailID,url,prompt,state,mimeType,styleId,pipeline)')
        db.execute('CREATE TABLE HistoryDetailLink(historyDetailID,url)')
        db.execute('INSERT INTO History VALUES(1,?,?,?,?,?)',('conversation',prefix,0,0,0))
        for index,code in enumerate(CODES):
            db.execute('INSERT INTO HistoryDetail VALUES(?,?,?,?,?,?,?,?,?,?,?)',(index,'message'+str(index),1,code,'text <é>',0,'reasoning',1700000000000+index,1700000010000+index,0,0))
            db.execute('INSERT INTO HistoryDetailDocument VALUES(?,?,?,?,?,?,?)',(index,index,'https://example.invalid/<é>:x','file',code,0,'text/plain'))
            db.execute('INSERT INTO HistoryDetailImage VALUES(?,?,?,?,?,?,?,?)',(index,index,'https://example.invalid/<é>:x','prompt',code,'image/png',0,'pipeline'))
        # Related records without a source message retain the existing INNER JOIN exclusion.
        db.execute('INSERT INTO HistoryDetailDocument VALUES(99,999,?,?,?,?,?)',('url','orphan',1,0,'text/plain'))
        db.commit();db.close();paths.append(str(path))
    alias=root/'data/user/0/com.scaleup.chatai/databases/chat-ai.db'
    alias.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(paths[0],alias);paths.append(str(alias))
    return paths


class TestNovaRawCodes(unittest.TestCase):
    def test_raw_values_preserve_labels_source_and_timestamp_mapping(self):
        with tempfile.TemporaryDirectory() as root:
            files=create_nova_codes_fixture(root)
            for function in FUNCTIONS:
                with self.subTest(artifact=function.__name__):
                    headers,data,_=function.__wrapped__(Context(root,files))
                    names=[x[0] if isinstance(x,tuple) else x for x in headers]
                    rows=[dict(zip(names,row)) for row in data]
                    self.assertEqual(len(rows),14)
                    self.assertEqual(len({row['Source File'] for row in rows}),2)
                    self.assertIn('Timestamp',names[0])
                    code_key='Role Code (as stored)' if function==nova.nova_chatbot_history_detail else 'Submitted By Code (as stored)'
                    label_key='Role' if function==nova.nova_chatbot_history_detail else 'Submitted By'
                    for row in rows:
                        ident=row['Msg ID']
                        self.assertEqual(row[code_key],CODES[ident])
                        self.assertEqual(type(row[code_key]),type(CODES[ident]))
                        self.assertEqual(row[label_key],nova.get_role(CODES[ident]))
                        self.assertTrue((Path(root)/row['Source File']).is_file())
                        if function==nova.nova_chatbot_history_detail:
                            self.assertEqual(row['Token (as stored)'],0)
                            self.assertLess(row['Message Timestamp'],row['Last Modified At'])
                        else:
                            key='Source Type Code (as stored)' if function==nova.nova_chatbot_documents else 'State Code (as stored)'
                            self.assertEqual(row[key],CODES[ident])
                            self.assertEqual(row['URL (as stored)'],'https://example.invalid/<é>:x')

    def test_missing_inputs_remain_empty(self):
        for function in FUNCTIONS:
            self.assertEqual(function.__wrapped__(Context('.',[]))[1],[])

"""Actual DiskLru JSON/media pairs preserve candidate occurrences conservatively."""
import copy
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import bereal as parser


class Context:
    def __init__(self,root,files):self.root,self.files=root,list(map(str,files))
    def get_files_found(self):return self.files
    def get_relative_path(self,path):return str(pathlib.Path(path).relative_to(self.root))


def pair(folder,key,url,document=None,color=None):
    folder.mkdir(parents=True,exist_ok=True)
    (folder/(key+'.0')).write_text(url+'\nGET\nHTTP/1.1 200 OK\n')
    body=folder/(key+'.1')
    if color is not None:Image.new('RGB',(2,2),color).save(body,format='PNG')
    else:body.write_text(json.dumps(document))
    return body


def make_fixture(root):
    folder=root/'data/data/com.bereal.ft/cache/network'
    other=root/'data/user/10/com.bereal.ft/cache/network'
    a={'id':'A','username':'a','isMe':True,'profilePicture':'https://images.test/unique'}
    b={'id':'B','username':'b','isMe':True,'profilePicture':'https://images.test/ambiguous'}
    pair(folder,'profiles','https://api.test/users/me',{'profiles':[a,b,copy.deepcopy(a)]})
    pair(folder,'unique','https://images.test/unique',color=(1,2,3))
    pair(folder,'ambiguous-a','https://images.test/ambiguous',color=(4,5,6))
    pair(folder,'ambiguous-b','https://images.test/ambiguous',color=(7,8,9))
    pair(other,'cross-root','https://images.test/unique',color=(10,11,12))
    pair(folder,'negative','https://api.test/media?x=/me#myprofile',{'username':'excluded'})
    pair(folder,'query','https://api.test/data?x=/me#myprofile',{'username':'excluded-query'})
    pair(folder,'json-path','https://api.test/data',{'myprofile':{'username':'path','profilePicture':'https://images.test/unique'},'myprofileSuffix':{'username':'excluded-path'}})
    plain=root/'data/data/com.bereal.ft/files/plain.json';plain.parent.mkdir(parents=True,exist_ok=True)
    plain.write_text(json.dumps({'profiles':[{'username':'plain','isMe':True,'profilePicture':'https://images.test/unique'},{'username':'low'}]}))
    prefs=root/'data/data/com.bereal.ft/shared_prefs/account.xml';prefs.parent.mkdir(parents=True,exist_ok=True);prefs.write_text('<map><string name="username">low</string></map>')
    return sorted(p for p in root.rglob('*') if p.is_file())


class BeRealProfileCandidatesTest(unittest.TestCase):
    def test_occurrences_exact_markers_and_conservative_media(self):
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder);files=make_fixture(root);before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
            with patch.object(parser,'check_in_media',side_effect=lambda path,**kwargs:'checked:'+str(path)) as media:
                headers,rows,sources=parser.bereal_device_user.__wrapped__(Context(root,files))
            self.assertEqual(len(rows),6)
            self.assertEqual([r[1] for r in rows[:3]],['a','b','a'])
            self.assertEqual([r[7] for r in rows],['High']*3+['Medium']*2+['Low'])
            self.assertEqual([r[9] for r in rows[:3]],[2,3,4])
            self.assertEqual([r[8] for r in rows[:3]],['profiles[0]','profiles[1]','profiles[2]'])
            self.assertEqual(rows[0][10:12],(2,1));self.assertTrue(rows[0][4])
            self.assertEqual(rows[1][10:12],(2,2));self.assertEqual(rows[1][4],'');self.assertIn('Ambiguous',rows[1][12])
            plain=next(r for r in rows if r[1]=='plain');self.assertEqual(plain[4],'');self.assertIn('Unknown',plain[12])
            self.assertTrue(all(i['same_cache_parent'] is None for i in json.loads(plain[13])))
            self.assertEqual(media.call_count,3)
            self.assertTrue(all('authenticated' not in call.kwargs['name'] for call in media.call_args_list))
            self.assertEqual(headers[-1],'Source File');self.assertTrue(all(not pathlib.Path(r[-1]).is_absolute() for r in rows))
            with patch.object(parser,'check_in_media',return_value='same'):
                _,reverse,_=parser.bereal_device_user.__wrapped__(Context(root,list(reversed(files))))
            self.assertEqual(sorted((r[1],r[8],r[9],r[13]) for r in rows),sorted((r[1],r[8],r[9],r[13]) for r in reverse))
            self.assertEqual(before,{p:hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
            self.assertIn('profiles.1',sources)

    def test_single_plain_source_and_unmatched_basename(self):
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder);files=make_fixture(root);plain=next(p for p in files if p.name=='plain.json')
            with patch.object(parser,'check_in_media') as media:
                headers,rows,_=parser.bereal_device_user.__wrapped__(Context(root,[plain]))
            self.assertEqual(len(rows),1);self.assertNotIn('Source File',headers);self.assertEqual(rows[0][10],0);media.assert_not_called()

    def test_exact_url_and_both_parent_proofs_required(self):
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder);cache=root/'data/data/com.bereal.ft/cache/network'
            image=pair(cache,'unique','https://images.test/unique',color=(1,2,3))
            body=pair(cache,'profile','https://api.test/me',{'username':'candidate','profilePicture':'https://missing.test/unique'})
            files=sorted(cache.iterdir())
            with patch.object(parser,'check_in_media') as media:
                _,rows,_=parser.bereal_device_user.__wrapped__(Context(root,files))
            self.assertEqual(rows[0][10:12],(0,0));media.assert_not_called()
            body.write_text(json.dumps({'username':'candidate','profilePicture':'https://images.test/unique'}))
            ctx=Context(root,files)
            original=ctx.get_relative_path
            ctx.get_relative_path=lambda path: 'other-root/cache/network/unique.1' if pathlib.Path(path)==image else original(path)
            with patch.object(parser,'check_in_media') as media:
                _,rows,_=parser.bereal_device_user.__wrapped__(ctx)
            self.assertEqual(rows[0][10:12],(1,0));self.assertEqual(rows[0][4],'');media.assert_not_called()

if __name__=='__main__':
    unittest.main()

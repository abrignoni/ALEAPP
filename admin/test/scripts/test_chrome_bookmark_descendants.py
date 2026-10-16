"""JSON child occurrences retain descendants, duplicates and their raw context."""
import copy
import datetime
import json
import pathlib
import shutil
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts.chromeBookmarks import get_chromeBookmarks  # pylint: disable=wrong-import-position

STAMP = '13344473600123456'


def write_json(root, data, prefix='data/data/com.android.chrome/app_chrome/Default'):
    path = pathlib.Path(root) / prefix / 'Bookmarks'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    return path


def context(root, paths):
    return SimpleNamespace(get_files_found=lambda:list(map(str,paths)),
                           get_relative_path=lambda p:str(pathlib.Path(p).relative_to(root)))


def make_tree():
    leaf = {'date_added': STAMP, 'url': 'https://repeat.test/', 'name': 'Repeated', 'type': 'url', 'id': '42'}
    inner = {'children': [copy.deepcopy(leaf)], 'date_added': STAMP, 'name': '', 'type': 'folder', 'id': 'B'}
    folder = {'children': [copy.deepcopy(leaf),inner], 'date_added': '0', 'name': 'A/雪', 'type': 'folder', 'id': 0}
    empty = {'children': [], 'date_added': STAMP, 'name': 'Empty', 'type': 'folder'}
    return {'roots': {
        'bookmark_bar': {'children':[leaf,folder,empty,copy.deepcopy(leaf)], 'name':'Root', 'id':'r0'},
        'other': {'children':[copy.deepcopy(leaf)], 'name':'Other', 'id':'r1'},
        'synced': {'children':[], 'name':'Synced', 'id':'r2'}},
        'metadata': {'unrelated': {'children':[leaf], 'name':'Do not report'}}}


def make_malformed_tree():
    dates = [None,'','bad',['bad'],{'bad':1},10**80,-10**80,0,-1,1.9,True]
    children = [{'date_added':value,'name':'N'+str(i),'id':i,'type':'url','url':'https://invalid.test/'}
                for i,value in enumerate(dates)]
    children[5]['id'] = 10**81
    children += [None,7,'scalar',{'name':'<b>name</b>','date_added':STAMP,'children':{'not':'list'},'type':'folder'},
                 {'name':'Missingdate','type':'url','id':-10**81}]
    return {'roots': {'bad-root': None, 'good': {'name':'R','id':10**82,'children':children},
                      'bad-children': {'name':'Bad','children':'not-list'}}}


class ChromeBookmarkDescendantsTest(unittest.TestCase):
    def parse(self, root, paths):
        with patch('scripts.artifacts.chromeBookmarks.logfunc') as log:
            result = get_chromeBookmarks.__wrapped__(context(root,paths))
        return (*result,log)

    def test_preorder_duplicates_folder_rows_and_lossless_ancestry(self):
        with tempfile.TemporaryDirectory() as root:
            path = write_json(root,make_tree())
            headers, rows, source, log = self.parse(root,[path])
            self.assertEqual(len(rows),8)
            self.assertEqual(headers[:2],[('Added Date','datetime'),'Added Date (as stored)'])
            self.assertEqual(len(headers),11)
            self.assertEqual([r[3] for r in rows],['Repeated','A/雪','Repeated','','Repeated','Empty','Repeated','Repeated'])
            self.assertEqual([r[4] for r in rows],['Root','Root','A/雪','A/雪','','Root','Root','Other'])
            self.assertEqual([json.loads(r[7]) for r in rows],
                             [['Root'],['Root'],['Root','A/雪'],['Root','A/雪'],
                              ['Root','A/雪',''],['Root'],['Root'],['Other']])
            self.assertEqual([r[8] for r in rows],['42',0,'42','B','42',None,'42','42'])
            self.assertEqual([r[9] for r in rows],['r0','r0',0,0,'B','r0','r0','r1'])
            self.assertEqual([r[10] for r in rows],['bookmark_bar']*7+['other'])
            self.assertEqual(rows[0],rows[6])
            self.assertEqual(sum(r[2]=='https://repeat.test/' for r in rows),5)
            self.assertEqual(rows[1][0],datetime.datetime(1601,1,1,tzinfo=datetime.timezone.utc))
            self.assertEqual(source,str(path))
            self.assertEqual(log.call_count,0)

    def test_root_property_order_cannot_change_parent_or_drop_children(self):
        with tempfile.TemporaryDirectory() as root:
            tree = make_tree()
            for key,node in tree['roots'].items():
                tree['roots'][key] = {'name':node['name'],'id':node['id'],'children':node['children']}
            _, rows, _, _ = self.parse(root,[write_json(root,tree)])
            self.assertEqual(len(rows),8)
            self.assertEqual(rows[0][4],'Root')
            self.assertEqual(rows[-1][4],'Other')

    def test_invalid_dates_retain_native_raw_values_and_accepted_conversion(self):
        with tempfile.TemporaryDirectory() as root:
            tree = make_malformed_tree()
            _, rows, _, log = self.parse(root,[write_json(root,tree)])
            self.assertEqual(len(rows),13)
            dates = [None,'','bad',['bad'],{'bad':1},10**80,-10**80,0,-1,1.9,True]
            for row,raw in zip(rows,dates):
                expected = str(raw) if isinstance(raw,int) and abs(raw)>=2**63 else raw
                self.assertEqual((type(row[1]),row[1]),(type(expected),expected))
            self.assertTrue(all(row[0]=='' for row in rows[:7]))
            for row,raw in zip(rows[7:11],dates[7:]):
                self.assertEqual(row[0],datetime.datetime(1601,1,1,tzinfo=datetime.timezone.utc)+
                                 datetime.timedelta(microseconds=int(raw)))
            self.assertEqual(rows[-2][3],'<b>name</b>')
            self.assertEqual(rows[-1][1],'')
            self.assertEqual(rows[5][8],str(10**81))
            self.assertEqual(rows[-1][8],str(-10**81))
            self.assertTrue(all(row[9]==str(10**82) for row in rows))
            self.assertEqual(sum('invalid date_added' in c.args[0] for c in log.call_args_list),8)
            self.assertEqual(sum('non-object child' in c.args[0] for c in log.call_args_list),3)
            self.assertEqual(sum('non-list children' in c.args[0] for c in log.call_args_list),2)
            self.assertTrue(all(len(c.args[0])<500 for c in log.call_args_list))

    def test_malformed_root_objects_do_not_abort_other_files(self):
        with tempfile.TemporaryDirectory() as root:
            good = write_json(root,make_tree())
            paths = [write_json(root,data,'data/data/p'+str(i)+'.test/app_chrome/Default')
                     for i,data in enumerate([[],None,{'roots':[]},{'roots':None},{}])]
            _, rows, source, log = self.parse(root,paths+[good])
            self.assertEqual(len(rows),8)
            self.assertEqual(source,str(good))
            self.assertEqual(sum('unsupported roots object' in c.args[0] for c in log.call_args_list),5)

    def test_failed_empty_and_alias_inputs_do_not_create_false_source_column(self):
        with tempfile.TemporaryDirectory() as root:
            good = write_json(root,make_tree())
            alias = pathlib.Path(root)/'data/user/0/com.android.chrome/app_chrome/Default/Bookmarks'
            alias.parent.mkdir(parents=True); shutil.copy2(good,alias)
            bad = write_json(root,{},'data/data/bad.test/app_chrome/Default'); bad.write_text('{',encoding='utf-8')
            invalid_utf8 = write_json(root,{},'data/data/utf8.test/app_chrome/Default'); invalid_utf8.write_bytes(b'\xff')
            missing = pathlib.Path(root)/'data/data/missing.test/app_chrome/Default/Bookmarks'
            backup = good.with_name('Bookmarks.bak'); shutil.copy2(good,backup)
            empty = write_json(root,{'roots':{}},'data/data/empty.test/app_chrome/Default')
            headers, rows, source, log = self.parse(root,[bad,invalid_utf8,missing,alias,good,backup,empty])
            self.assertEqual(len(rows),8)
            self.assertNotIn('Source File',headers)
            self.assertEqual(source,str(good))
            self.assertEqual(sum('unavailable JSON' in c.args[0] for c in log.call_args_list),3)

    def test_independent_contributors_repeat_rows_and_keep_source_encounter_order(self):
        with tempfile.TemporaryDirectory() as root:
            first = write_json(root,make_tree(),'data/user/10/com.android.chrome/app_chrome/Default')
            second = write_json(root,make_tree())
            headers, rows, sources, _ = self.parse(root,[first,second])
            self.assertEqual(len(rows),16)
            self.assertEqual(headers[-1],'Source File')
            self.assertEqual([r[:-1] for r in rows[:8]],[r[:-1] for r in rows[8:]])
            self.assertEqual([r[-1] for r in rows[:8]],[str(first.relative_to(root))]*8)
            self.assertEqual(sources.splitlines(),list(map(str,[first,second])))

    def test_moderate_deep_children_are_walked_without_recursive_helper(self):
        with tempfile.TemporaryDirectory() as root:
            node = {'name':'leaf','date_added':'0','type':'url'}
            for index in range(120):
                node = {'name':str(index),'date_added':'0','type':'folder','children':[node]}
            tree = {'roots':{'bar':{'name':'Root','children':[node]}}}
            _, rows, _, _ = self.parse(root,[write_json(root,tree)])
            self.assertEqual(len(rows),121)
            self.assertEqual(rows[-1][3],'leaf')
            self.assertEqual(len(json.loads(rows[-1][7])),121)

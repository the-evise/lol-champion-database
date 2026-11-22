import json,pathlib,subprocess,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class WebBuildTests(unittest.TestCase):
 def test_catalog_and_lazy_records_match_database(self):
  with tempfile.TemporaryDirectory() as temp:
   result=subprocess.run([sys.executable,str(ROOT/'scripts/build_web.py'),'--output',temp],capture_output=True,text=True,check=True)
   out=pathlib.Path(temp);catalog=json.loads((out/'data/catalog.json').read_text());records=json.loads((ROOT/'data/champions.json').read_text())
   self.assertEqual({c['id'] for c in catalog['champions']},{c['id'] for c in records})
   self.assertLess((out/'data/catalog.json').stat().st_size,100000)
   for c in catalog['champions']:
    full=json.loads((out/'data/champions'/(c['id']+'.json')).read_text());self.assertEqual(c['positions'],full['gameplay']['positions']['client']);self.assertEqual(c['region'],full['lore']['region'])
    self.assertEqual(c['story_count'],sum(r['type']=='story' for r in full['lore']['resources']))
    for key in ['portrait','hero']:
     self.assertTrue(c[key].startswith('https://ddragon.leagueoflegends.com/') or (out/c[key]).is_file())
   for name in ['index.html','app.js','styles.css','favicon.svg']:self.assertTrue((out/name).exists())
if __name__=='__main__':unittest.main()

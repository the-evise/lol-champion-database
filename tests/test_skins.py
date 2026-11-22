import json,pathlib,sqlite3,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build import build_sqlite
from validate_skins import validate
class SkinCatalogTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.skins=json.loads((ROOT/'data/skins.json').read_text());cls.byid={s['id']:s for s in cls.skins};cls.lines={s['id']:s for s in json.loads((ROOT/'data/skinlines.json').read_text())};cls.worlds={s['id']:s for s in json.loads((ROOT/'data/skin_universes.json').read_text())}
 def test_catalog_integrity(self):self.assertEqual(validate(),[])
 def test_requested_result_identities(self):
  coven=self.byid['skin:25026'];pentakill=self.byid['skin:30004']
  self.assertEqual(coven['matching']['result_label'],'Coven Morgana');self.assertEqual(pentakill['matching']['result_label'],'Pentakill Karthus')
  self.assertIn(92,coven['skinline_ids']);self.assertIn('universe:eclipse',coven['universe_ids']);self.assertIn('universe:riot-records',pentakill['universe_ids'])
  self.assertTrue(coven['matching']['label_eligible']);self.assertTrue(pentakill['matching']['label_eligible'])
 def test_quest_tiers_do_not_disappear(self):
  self.assertEqual(self.byid['skin:103086']['variant_of'],'skin:103085');self.assertEqual(self.byid['skin:147002']['variant_of'],'skin:147001')
  self.assertEqual(self.byid['skin:147003']['kind'],'quest_tier')
 def test_chromas_not_independent_personalities(self):
  chromas={c['id'] for s in self.skins for c in s['chromas']}
  self.assertNotIn('skin:25027',self.byid);self.assertIn(25027,chromas)
  self.assertTrue(all(not c['separate_personality_result'] for s in self.skins for c in s['chromas']))
 def test_unreleased_and_removed_are_catalogued_but_ineligible(self):
  excluded=[s for s in self.skins if s['availability'] in ['Upcoming','Canceled','Removed'] or s['kind']=='historical']
  self.assertTrue(excluded);self.assertTrue(all(not s['matching']['label_eligible'] for s in excluded))
  without_id=[s for s in self.skins if s['riot_skin_id'] is None];self.assertTrue(without_id);self.assertTrue(all(s['id'].startswith('wiki:') for s in without_id))
 def test_unresolved_wiki_variants_not_fabricated(self):
  self.assertIsNone(self.byid['skin:103089']['variant_of']);self.assertEqual(self.byid['skin:103089']['variant_reference_wiki']['skin_id'],'skin:103087')
 def test_lore_scope_is_explicit(self):
  self.assertTrue(self.byid['skin:25026']['lore']['summary_reviewed'])
  self.assertTrue(all(not s['lore']['raw_prose_redistributed'] and not s['analysis']['inherit_base_personality_automatically'] for s in self.skins))
  self.assertTrue(all(s['lore']['source_id'] and (s['lore']['json_pointer'] or s['lore']['wiki_locator']) for s in self.skins if s['lore']['available']))
 def test_sqlite_skin_joins(self):
  champions=json.loads((ROOT/'data/champions.json').read_text());sources=json.loads((ROOT/'data/sources.json').read_text())['sources']
  with tempfile.TemporaryDirectory() as temp:
   p=pathlib.Path(temp)/'db.sqlite';build_sqlite(p,champions,sources);con=sqlite3.connect(p)
   self.assertEqual(con.execute('SELECT COUNT(*) FROM skins').fetchone()[0],len(self.skins));self.assertEqual(con.execute('PRAGMA foreign_key_check').fetchall(),[])
   self.assertEqual(con.execute("SELECT result_label FROM result_identity_catalog WHERE result_key='skin:25026'").fetchone()[0],'Coven Morgana')
   self.assertEqual(con.execute('SELECT COUNT(*) FROM skin_chromas').fetchone()[0],sum(len(s['chromas']) for s in self.skins));con.close()
if __name__=='__main__':unittest.main()

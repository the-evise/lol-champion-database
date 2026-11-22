import json,pathlib,sys,tempfile,unittest,sqlite3
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from lua_table import parse
from build import build_sqlite
class ParserTests(unittest.TestCase):
 def test_safe_numeric_expression(self):
  self.assertEqual(parse('return {["x"] = { ["hp"] = 84+1000/17, ["offset"] = -0.1, ["ok"]=true }}')['x']['hp'],84+1000/17)
 def test_order_and_escapes(self):
  self.assertEqual(parse('return {"A", "B", "C"}'),['A','B','C'])
 def test_rejects_code(self):
  with self.assertRaises((ValueError,AssertionError,SyntaxError)):parse('return {x = os.execute("anything")}')
class DatabaseTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.rows=json.loads((ROOT/'data/champions.json').read_text());cls.sources=json.loads((ROOT/'data/sources.json').read_text())['sources'];cls.byid={c['id']:c for c in cls.rows}
 def test_zero_capability_is_not_negative(self):
  absent=[(c,k) for c in self.rows for k in ['control','utility'] if c['gameplay']['ratings'][k]==0]
  self.assertTrue(absent)
  for c,k in absent:self.assertEqual(c['analysis']['gameplay_features'][k],0)
 def test_external_character_not_promoted_to_playable(self):
  self.assertNotIn('Norra',self.byid)
  norra=[r for r in self.byid['Yuumi']['lore']['related_champions'] if r['name']=='Norra'];self.assertEqual(norra[0]['id'],None)
 def test_no_claimed_story_review_or_validated_quiz(self):
  self.assertTrue(all(not c['coverage']['linked_story_editorial_review'] and not c['analysis']['personality_quiz_ready'] for c in self.rows))
 def test_sqlite_rebuild_and_relations(self):
  with tempfile.TemporaryDirectory() as temp:
   path=pathlib.Path(temp)/'db.sqlite';build_sqlite(path,self.rows,self.sources);build_sqlite(path,self.rows,self.sources)
   con=sqlite3.connect(path)
   self.assertEqual(con.execute('SELECT COUNT(*) FROM champions').fetchone()[0],len(self.rows))
   self.assertEqual(con.execute('SELECT COUNT(*) FROM abilities').fetchone()[0],5*len(self.rows))
   self.assertEqual(con.execute("SELECT COUNT(DISTINCT role) FROM role_candidates").fetchone()[0],5)
   self.assertEqual(con.execute('PRAGMA foreign_key_check').fetchall(),[]);con.close()
if __name__=='__main__':unittest.main()

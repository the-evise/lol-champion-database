#!/usr/bin/env python3
"""Validate shipped content and cross-file consistency; no network required."""
import collections,csv,json,pathlib,sqlite3,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
records=json.loads((ROOT/'data/champions.json').read_text());report=json.loads((ROOT/'data/coverage.json').read_text());sources=json.loads((ROOT/'data/sources.json').read_text())['sources'];source_ids={s['id'] for s in sources}
errors=[]
def check(ok,message):
 if not ok:errors.append(message)
ids=[c['id'] for c in records];check(len(ids)==len(set(ids)),'Duplicate champion IDs');check(len(records)==report['champion_count'],'Coverage count differs');check(len({c['riot_id'] for c in records})==len(records),'Duplicate Riot IDs')
role_counts=collections.Counter()
for c in records:
 id=c['id'];g=c['gameplay'];l=c['lore'];a=c['analysis']
 check(json.loads((ROOT/f'data/champions/{id}.json').read_text())==c,f'{id}: individual/aggregate mismatch')
 check((ROOT/f'docs/champions/{id}.md').exists(),f'{id}: missing dossier')
 for key in ['lore','gameplay_api','gameplay_wiki']:check(c['provenance'][key] in source_ids,f'{id}: unresolved source {key}')
 check(bool(l['summary']),f'{id}: missing authored summary')
 check(c['coverage']['short_bio_editorial_review'],f'{id}: editorial source changed or unreviewed')
 check(len(g['abilities'])==5,f'{id}: incomplete ability slots')
 for k,v in g['ratings'].items():check(type(v) is int and (0<=v<=100 if k=='style' else 1<=v<=3 if k=='difficulty' else 0<=v<=3),f'{id}: invalid rating {k}: {v}')
 for k,v in a['gameplay_features'].items():check(v is None or 0<=v<=1,f'{id}: invalid normalized feature {k}')
 check(a['personality_scores'] is None and a['personality_quiz_ready'] is False,f'{id}: unvalidated scores presented as ready')
 for t in a['candidate_themes']:check(t['evidence_source_id'] in source_ids and t['status']=='tentative_interpretation',f'{id}: theme lacks interpretation marker or provenance')
 for p in g['positions']['client']:
  check(p in ['top','jungle','mid','bottom','support'],f'{id}: unknown position {p}');role_counts[p]+=1
 for r in l['related_champions']:check(r['id'] in ids or r['id'] is None,f'{id}: invalid related ID')
 for r in l['resources']:check(r['url'].startswith('https://'),f'{id}: non-HTTPS resource')
for role in ['top','jungle','mid','bottom','support']:check(role_counts[role]>=3,f'{role}: fewer than three candidates')
check(not report['gaps'],'Source or editorial gaps present')
check(len(list(csv.DictReader((ROOT/'data/champions.csv').open())))==len(records),'CSV count differs')
db=ROOT/'build/champions.sqlite'
if db.exists():
 con=sqlite3.connect(db);check(con.execute('PRAGMA integrity_check').fetchone()[0]=='ok','SQLite integrity check failed');check(con.execute('SELECT COUNT(*) FROM champions').fetchone()[0]==len(records),'SQLite count differs');check(not con.execute('PRAGMA foreign_key_check').fetchall(),'SQLite foreign key failure');con.close()
if errors:print('\n'.join(errors));sys.exit(1)
print(f'PASS: {len(records)} champions; JSON/CSV/dossiers/sources/ratings/roles consistent. Role pools: {dict(role_counts)}')

#!/usr/bin/env python3
"""Filter the database without imposing a quiz or recommendation score."""
import argparse,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--champion');p.add_argument('--role',choices=['top','jungle','mid','bottom','support']);p.add_argument('--theme');p.add_argument('--search');p.add_argument('--max-difficulty',type=int,choices=[1,2,3]);p.add_argument('--json',action='store_true');a=p.parse_args()
rows=json.loads((ROOT/'data/champions.json').read_text(encoding='utf-8'))
if a.champion:rows=[c for c in rows if a.champion.casefold() in (c['id'].casefold(),c['name'].casefold())]
if a.role:rows=[c for c in rows if a.role in c['gameplay']['positions']['client']]
if a.theme:rows=[c for c in rows if a.theme in [t['theme'] for t in c['analysis']['candidate_themes']]]
if a.search:rows=[c for c in rows if a.search.casefold() in json.dumps({'name':c['name'],'lore':c['lore']['summary'],'motivation':c['analysis']['central_motivation']},ensure_ascii=False).casefold()]
if a.max_difficulty:rows=[c for c in rows if c['gameplay']['ratings']['difficulty'] is not None and c['gameplay']['ratings']['difficulty']<=a.max_difficulty]
if a.json:print(json.dumps(rows,ensure_ascii=False,indent=2))
else:
 for c in rows:print(f'{c["name"]:18} {", ".join(c["gameplay"]["positions"]["client"]):20} {c["lore"]["summary"]}')
 print(f'\n{len(rows)} matches. These are filtered candidates, not ranked recommendations.')

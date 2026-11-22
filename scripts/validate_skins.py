#!/usr/bin/env python3
"""Check completeness, relationships, source references, and candidate boundaries."""
import collections,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def validate(root=ROOT):
 d=root/'data';skins=json.loads((d/'skins.json').read_text());report=json.loads((d/'skin_coverage.json').read_text());champions=json.loads((d/'champions.json').read_text());cid={c['id'] for c in champions};ids={s['id'] for s in skins};lines={l['id']:l for l in json.loads((d/'skinlines.json').read_text())};worlds={w['id']:w for w in json.loads((d/'skin_universes.json').read_text())};sources={s['id'] for s in json.loads((d/'skin_sources.json').read_text())['sources']};errors=[];rules=json.loads((d/'skin_vibe_rules.json').read_text())
 def check(ok,m):
  if not ok:errors.append(m)
 check(len(ids)==len(skins),'Duplicate result keys');check(len(skins)==report['total_entries'],'Coverage count differs');check({s['champion_id'] for s in skins}==cid,'Some champions missing cosmetics');check(sum(s['is_base'] for s in skins)==len(champions),'Expected one base appearance per champion')
 riotids=[s['riot_skin_id'] for s in skins if s['riot_skin_id'] is not None];check(len(riotids)==len(set(riotids)),'Duplicate Riot skin IDs');chromas=[]
 for s in skins:
  vibe=s.get('vibe',{});tags=vibe.get('tags',[])
  check(len(tags)==2 and len(set(tags))==2,s['id']+': expected exactly two distinct vibe tags')
  check(all(t in rules['vocabulary'] for t in tags),s['id']+': unknown vibe tag')
  check(vibe.get('scope')=='aesthetic_impression' and vibe.get('lore_based') is False and vibe.get('personality_claim') is False,s['id']+': unsupported tag interpretation')
  key=s['id'];check(s['champion_id'] in cid,key+': unknown champion');check(s['variant_of'] is None or s['variant_of'] in ids,key+': missing variant parent');check(all(l in lines for l in s['skinline_ids']),key+': unknown skinline');check(all(u in worlds for u in s['universe_ids']),key+': unknown universe')
  check(all(i in sources for i in s['provenance']['source_ids']),key+': unknown source');check(not s['lore']['source_id'] or s['lore']['source_id'] in sources,key+': missing lore source')
  check(s['analysis']['personality_scores'] is None and not s['analysis']['inherit_base_personality_automatically'],key+': unsupported automatic personality')
  if s['matching']['label_eligible']:check(s['inventory_scope'] in ['client_inventory','quest_tier'] and s['availability'] not in ['Upcoming','Canceled','Removed'],key+': ineligible catalog entry marked as released')
  for c in s['chromas']:check(c['parent_skin_id']==key and not c['separate_personality_result'],key+': invalid chroma parent');chromas.append(c['id'])
  if s['lore']['summary']:check(s['lore']['summary_reviewed'],key+': stale editorial review')
 check(len(chromas)==len(set(chromas)),'Duplicate chromas');check(not(set(chromas)&set(riotids)),'Chroma presented as a skin identity')
 for c in cid:check(json.loads((d/'skins'/(c+'.json')).read_text())['skins']==[s for s in skins if s['champion_id']==c],c+': per-champion data differs')
 for line in lines.values():check(set(line['skin_ids'])=={s['id'] for s in skins if line['id'] in s['skinline_ids']},line['name']+': inconsistent skinline membership')
 for w in worlds.values():check(set(w['skin_ids'])=={s['id'] for s in skins if w['id'] in s['universe_ids']},w['name']+': inconsistent universe membership')
 check(not report['unresolved_global_skins'],'Unresolved source skins');check(not report['unknown_skinline_ids'],'Unresolved source skinlines');check(not report['chroma_parent_conflicts'],'Chroma parent conflicts')
 return errors
if __name__=='__main__':
 errors=validate()
 if errors:print('\n'.join(errors));sys.exit(1)
 print('PASS: every champion covered; skins, chromas, memberships, source links, and candidate boundaries are consistent.')

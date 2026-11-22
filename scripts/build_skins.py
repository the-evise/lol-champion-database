#!/usr/bin/env python3
"""Build a complete, source-linked PC cosmetics catalog without copying source prose."""
import argparse,collections,csv,datetime,hashlib,html,json,pathlib,re,sys,unicodedata
from urllib.parse import quote
from lua_table import parse
ROOT=pathlib.Path(__file__).resolve().parents[1];DATA=ROOT/'data';CACHE=ROOT/'.cache/skins'
AS_OF='2026-11-22'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,v,compact=False):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=None if compact else 2,separators=(',',':') if compact else None)+'\n',encoding='utf-8')
def norm(s):return ''.join(c.lower() for c in unicodedata.normalize('NFKD',s) if c.isalnum())
def slug(s):return re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()).strip('-') or 'unnamed'
def plain(s):return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',s or ''))).strip()
def sha(s):return hashlib.sha256(s.encode()).hexdigest()
def wiki_payload(path):
 page=next(iter(read(path)['query']['pages'].values()));rev=page['revisions'][0];return page['title'],rev,rev['slots']['main']['*']
def source(id,path,url,kind,**extra):return {'id':id,'url':url,'kind':kind,'retrieved_at':datetime.datetime.fromtimestamp(path.stat().st_mtime,datetime.timezone.utc).isoformat(),'payload_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),**extra}
def asset_url(path,patch):
 prefix='/lol-game-data/assets/'
 if not path or not path.lower().startswith(prefix):return None
 return f'https://raw.communitydragon.org/{patch}/plugins/rcp-be-lol-game-data/global/default/'+path[len(prefix):].lower()
def main():
 global AS_OF
 parser=argparse.ArgumentParser();parser.add_argument('--as-of',default=AS_OF,help='Snapshot date for release eligibility (YYYY-MM-DD)');args=parser.parse_args();AS_OF=datetime.date.fromisoformat(args.as_of).isoformat()
 champions=read(DATA/'champions.json');patch=champions[0]['snapshot_version'].rsplit('.',1)[0];base=f'https://raw.communitydragon.org/{patch}/plugins/rcp-be-lol-game-data/global/default/v1/'
 clients={c['id']:read(CACHE/'client'/(c['id']+'.json')) for c in champions}
 global_skins=read(CACHE/'skins.json');line_input=read(CACHE/'skinlines.json');universe_input=read(CACHE/'universes.json')
 wiki_title,wiki_rev,wiki_text=wiki_payload(CACHE/'wiki_skins.json');wiki=parse(wiki_text)
 group_title,group_rev,group_text=wiki_payload(CACHE/'wiki_universe_groups.json');groups=parse(group_text)
 editorial=read(DATA/'skin_editorial.json');pin_path=DATA/'skin_editorial_hashes.json';pins=read(pin_path) if pin_path.exists() else {}
 sources=[source('skins:cdragon',CACHE/'skins.json',base+'skins.json','communitydragon_client_data',patch=patch),source('skinlines:cdragon',CACHE/'skinlines.json',base+'skinlines.json','communitydragon_client_data',patch=patch),source('universes:cdragon',CACHE/'universes.json',base+'universes.json','communitydragon_client_data',patch=patch)]
 for id,path,title,rev in [('skins:wiki',CACHE/'wiki_skins.json',wiki_title,wiki_rev),('universes:wiki',CACHE/'wiki_universe_groups.json',group_title,group_rev)]:
  url='https://wiki.leagueoflegends.com/en-us/'+quote(title,safe=':/')
  sources.append(source(id,path,url,'league_wiki',revision_id=rev['revid'],revision_timestamp=rev['timestamp'],permalink=f'https://wiki.leagueoflegends.com/en-us/index.php?title={quote(title)}&oldid={rev["revid"]}',history_url=url+'?action=history',license={'name':'CC BY-SA 3.0','url':'https://creativecommons.org/licenses/by-sa/3.0/'}))
 wiki_by_champion={v['id']:(name,v) for name,v in wiki.items()};wiki_by_id={};wiki_null=[]
 for champion in champions:
  name,data=wiki_by_champion[champion['riot_id']]
  for short,v in data['skins'].items():
   info=(champion,short,v)
   if type(v['id']) is int:wiki_by_id[champion['riot_id']*1000+v['id']]=info
   else:wiki_null.append(info)
 members={};tier_parent={};tier_locators={}
 for champion in champions:
  cid=champion['id'];client=clients[cid];url=base+f'champions/{champion["riot_id"]}.json';p=CACHE/'client'/(cid+'.json')
  sources.append(source('skins:client:'+cid,p,url,'communitydragon_client_data',patch=patch))
  for i,s in enumerate(client['skins']):
   members[s['id']]=(champion,s,f'/skins/{i}','client_inventory')
   for ti,t in enumerate((s.get('questSkinInfo') or {}).get('tiers',[])):
    if t['id']!=s['id']:
     merged={**s,**t,'isBase':False,'chromas':[],'questSkinInfo':None};members[t['id']]=(champion,merged,f'/skins/{i}/questSkinInfo/tiers/{ti}','quest_tier');tier_parent[t['id']]=s['id']
 # Global-only classic entries have no current champion inventory membership. Resolve
 # ownership by an explicit classic namespace rule, verified against all current IDs.
 # The final three digits identify the historic model; the middle digits are champion ID.
 unresolved_global=[]
 for key,s in global_skins.items():
  sid=int(key)
  if sid in members:continue
  match=next((c for c in champions if sid//1000==60000+c['riot_id']),None)
  if match and s['name'].startswith('Classic ') and norm(re.sub(r'^Classic (?:[0-9]{4} )?','',s['name'].strip()))==norm(match['name']):members[sid]=(match,s,'/'+key,'classic_archive')
  else:unresolved_global.append({'skin_id':sid,'name':s['name']})
 for sid,(c,short,w) in wiki_by_id.items():
  if sid not in members:
   members[sid]=(c,{'id':sid,'name':w.get('formatname') or f'{short} {c["name"]}','isBase':w['id']==0},None,'wiki_only')
 worlds={};lines={};line_worlds=collections.defaultdict(set);wiki_set_worlds=collections.defaultdict(set)
 def world(name):
  key='universe:'+slug(name)
  if key not in worlds:worlds[key]={'id':key,'name':name,'client_universe_ids':[],'source_ids':[],'skin_ids':[],'description_available':False}
  return worlds[key]
 for u in universe_input:
  if not u['name']:continue
  w=world(u['name']);w['client_universe_ids'].append(u['id']);w['source_ids'].append('universes:cdragon');w['description_available']=bool(u.get('description'));w['description_lookup']={'source_id':'universes:cdragon','json_pointer':f'/{universe_input.index(u)}/description','sha256':sha(plain(u.get('description')))}
  for lid in u.get('skinSets',[]):line_worlds[lid].add(w['id'])
 for name,sets in groups.items():
  w=world(name);w['source_ids'].append('universes:wiki');w['wiki_sets']=sets
  for s in sets:wiki_set_worlds[s].add(w['id'])
 for i,l in enumerate(line_input):
  if not l['name']:continue
  lines[l['id']]={'id':l['id'],'name':l['name'],'universe_ids':sorted(line_worlds[l['id']]),'skin_ids':[],'source_id':'skinlines:cdragon','description_available':bool(l.get('description')),'description_lookup':{'source_id':'skinlines:cdragon','json_pointer':f'/{i}/description','sha256':sha(plain(l.get('description')))}}
 skins=[];chroma_seen={};unknown_lines=set();conflicts=[]
 def make(c,s,short,w,origin,pointer):
  cid=c['id'];sid=s.get('id');key=f'skin:{sid}' if sid is not None else f'wiki:{cid}:{slug(short)}';is_base=s.get('isBase',False);glob=global_skins.get(str(sid),{})
  lid_values=sorted({x['id'] for x in (s.get('skinLines') or glob.get('skinLines') or [])})
  for lid in lid_values:
   if lid not in lines:unknown_lines.add(lid)
  sets=w.get('set',[]) if isinstance(w.get('set'),list) else []
  world_ids=sorted({u for lid in lid_values for u in line_worlds[lid]}|{u for st in sets for u in wiki_set_worlds[st]})
  wi_lore=plain(w.get('lore'));client_lore=plain(s.get('description'));description=client_lore or wi_lore
  lore_source='skins:client:'+cid if client_lore and origin in ['client_inventory','quest_tier'] else 'skins:cdragon' if client_lore else 'skins:wiki' if wi_lore else None
  lore_pointer=(pointer+'/description') if client_lore and pointer and origin in ['client_inventory','quest_tier'] else f'/{sid}/description' if client_lore else None
  release=w.get('release');release=release if release and re.fullmatch(r'\d{4}-\d{2}-\d{2}',release) else None
  availability=w.get('availability') or ('Historical archive' if origin=='classic_archive' else 'Unlisted')
  excluded=availability in ['Upcoming','Canceled','Removed'] or (release and release>AS_OF) or origin=='classic_archive'
  eligible=not excluded and origin in ['client_inventory','quest_tier']
  parent=tier_parent.get(sid)
  if parent is None and type(w.get('variant')) is int:parent=c['riot_id']*1000+w['variant']
  parent_key=f'skin:{parent}' if parent is not None else None
  rarity=s.get('rarity') or glob.get('rarity');rarity=rarity[1:] if rarity and rarity.startswith('k') else rarity
  if rarity=='NoRarity':rarity='Standard'
  art=s if s.get('splashPath') else glob
  assets={key:asset_url(art.get(field),patch) for key,field in [('splash','splashPath'),('uncentered_splash','uncenteredSplashPath'),('tile','tilePath'),('loading','loadScreenPath')]}
  if not assets['splash'] and sid is not None and 0<=sid-c['riot_id']*1000<1000:
   assets['splash']=f'https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{cid}_{sid-c["riot_id"]*1000}.jpg'
  if not assets['tile']:assets['tile']=assets['splash']
  added=editorial.get(str(sid));reviewed=False
  if added and description:
   if str(sid) not in pins:pins[str(sid)]=sha(description)
   reviewed=pins[str(sid)]==sha(description)
  source_ids=['skins:wiki'] if w else []
  if origin in ['client_inventory','quest_tier']:source_ids.append('skins:client:'+cid)
  if glob:source_ids.append('skins:cdragon')
  chromas=[]
  for x in s.get('chromas',glob.get('chromas',[])) or []:
   if x['id']==sid:continue
   chr={'id':x['id'],'parent_skin_id':key,'name':x.get('name'),'colors':x.get('colors') or [],'tile_url':asset_url(x.get('chromaPath') or x.get('tilePath'),patch),'kind':'chroma','separate_personality_result':False}
   chromas.append(chr)
   if x['id'] in chroma_seen and chroma_seen[x['id']]!=key:conflicts.append({'chroma_id':x['id'],'parents':[chroma_seen[x['id']],key]})
   chroma_seen[x['id']]=key
  record={'schema_version':'1.0.0','id':key,'riot_skin_id':sid,'champion_id':cid,'champion_riot_id':c['riot_id'],'champion_name':c['name'],'name':s.get('name') or w.get('formatname') or f'{short} {c["name"]}','is_base':is_base,'kind':'base' if is_base else 'quest_tier' if origin=='quest_tier' else 'historical' if origin=='classic_archive' else 'skin','inventory_scope':origin,'skin_num':sid-c['riot_id']*1000 if sid is not None and origin!='classic_archive' else None,'content_id':s.get('contentId') or glob.get('contentId'),'rarity':rarity,'availability':availability,'release_date':release,'retired_date':w.get('retired'),'legacy_client':s.get('isLegacy',glob.get('isLegacy')),'cost_wiki':w.get('cost'),'loot_eligible_wiki':w.get('looteligible'),'skinline_ids':lid_values,'wiki_sets':sets,'universe_ids':world_ids,'variant_of':parent_key,'forms_wiki':w.get('forms',[]),'chromas':chromas,'artwork':assets,'lore':{'available':bool(description),'summary':added['summary'] if added else None,'summary_kind':'original_paraphrase' if added else None,'summary_reviewed':reviewed,'biography_sha256':sha(description) if description else None,'biography_word_count':len(description.split()),'source_id':lore_source,'json_pointer':lore_pointer,'wiki_locator':{'champion':c['name'],'skin':short,'field':'lore'} if wi_lore else None,'wiki_url':f'https://wiki.leagueoflegends.com/en-us/{quote(c["name"].replace(" ","_"))}/LoL/Cosmetics','raw_prose_redistributed':False},'analysis':{'candidate_themes':added['themes'] if added else [],'status':'editorial_interpretation_unvalidated' if added else 'not_annotated','personality_scores':None,'inherit_base_personality_automatically':False},'matching':{'result_key':key,'result_label':s.get('name') or f'{short} {c["name"]}','label_eligible':eligible,'narrative_family_id':parent_key or key,'champion_profile_ref':f'data/champions/{cid}.json','gameplay_profile_ref':f'data/champions/{cid}.json','personalization_status':'unscored','evidence_scope':'skin_biography' if added else 'catalog_metadata_only'},'provenance':{'source_ids':sorted(set(source_ids)),'snapshot_patch':patch,'wiki_revision_id':wiki_rev['revid'],'as_of':AS_OF}}
  return record
 for sid,(c,s,pointer,origin) in members.items():
  _,short,w=wiki_by_id.get(sid,(None,s['name'],{}));r=make(c,s,short,w,origin,pointer);skins.append(r)
 for c,short,w in wiki_null:
  skins.append(make(c,{'id':None,'name':w.get('formatname') or f'{short} {c["name"]}','isBase':False},short,w,'wiki_only',None))
 known_keys={s['id'] for s in skins};unresolved_variants=[]
 for record in skins:
  if record['variant_of'] and record['variant_of'] not in known_keys:
   unresolved_variants.append({'skin_id':record['id'],'wiki_parent_reference':record['variant_of']})
   record['variant_reference_wiki']={'skin_id':record['variant_of'],'resolution':'not_in_snapshot'}
   record['variant_of']=None;record['matching']['narrative_family_id']=record['id']
 skins.sort(key=lambda s:(s['champion_name'].casefold(),not s['is_base'],s['name'].casefold()))
 by_champ=collections.defaultdict(list)
 for s in skins:
  by_champ[s['champion_id']].append(s)
  for lid in s['skinline_ids']:
   if lid in lines:lines[lid]['skin_ids'].append(s['id'])
  for uid in s['universe_ids']:worlds[uid]['skin_ids'].append(s['id'])
 for w in worlds.values():w['source_ids']=sorted(set(w['source_ids']))
 write(DATA/'skins.json',skins,compact=True)
 for cid,entries in by_champ.items():write(DATA/'skins'/(cid+'.json'),{'champion_id':cid,'skins':entries})
 write(DATA/'skinlines.json',sorted(lines.values(),key=lambda l:l['name'].casefold()));write(DATA/'skin_universes.json',sorted(worlds.values(),key=lambda u:u['name'].casefold()));write(DATA/'skin_editorial_hashes.json',pins)
 write(DATA/'skin_sources.json',{'snapshot_patch':patch,'sources':sources})
 report={'as_of':AS_OF,'snapshot_patch':patch,'champions_expected':len(champions),'champions_with_skins':len(by_champ),'total_entries':len(skins),'base_appearances':sum(s['is_base'] for s in skins),'non_base_entries':sum(not s['is_base'] for s in skins),'released_skin_result_labels':sum(s['matching']['label_eligible'] and not s['is_base'] for s in skins),'quest_tiers':sum(s['kind']=='quest_tier' for s in skins),'historical_archives':sum(s['kind']=='historical' for s in skins),'wiki_only_without_riot_id':sum(s['riot_skin_id'] is None for s in skins),'chromas':len(chroma_seen),'skins_with_lore':sum(s['lore']['available'] and not s['is_base'] for s in skins),'skin_biographies_summarized':sum(s['lore']['summary_reviewed'] for s in skins),'skinlines_with_members':sum(bool(l['skin_ids']) for l in lines.values()),'universes_with_members':sum(bool(u['skin_ids']) for u in worlds.values()),'unresolved_global_skins':unresolved_global,'unresolved_variant_references':unresolved_variants,'unknown_skinline_ids':sorted(unknown_lines),'chroma_parent_conflicts':conflicts,'personality_model_validated':False,'scope':'PC League of Legends. Chromas are separate cosmetic options. Wild Rift-exclusive catalogs are not included.'}
 dd_files=[ROOT/'.cache/ddragon'/(c['id']+'.json') for c in champions]
 if all(p.exists() for p in dd_files):
  dd_ids={int(entry['id']) for p in dd_files for entry in next(iter(read(p)['data'].values()))['skins']}
  skin_riot_ids={s['riot_skin_id'] for s in skins if s['riot_skin_id'] is not None};chroma_ids=set(chroma_seen)
  report['data_dragon_reconciliation']={'appearance_entries':len(dd_ids),'resolved_as_skins':len(dd_ids&skin_riot_ids),'resolved_as_chromas':len(dd_ids&chroma_ids),'unresolved_ids':sorted(dd_ids-skin_riot_ids-chroma_ids)}
 else:report['data_dragon_reconciliation']=None
 write(DATA/'skin_coverage.json',report)
 with (DATA/'skins.csv').open('w',encoding='utf-8',newline='') as f:
  out=csv.writer(f);out.writerow(['id','riot_skin_id','champion_id','name','is_base','kind','rarity','availability','release_date','skinlines','wiki_sets','universes','variant_of','chroma_count','lore_available','result_label_eligible'])
  for s in skins:out.writerow([s['id'],s['riot_skin_id'],s['champion_id'],s['name'],s['is_base'],s['kind'],s['rarity'],s['availability'],s['release_date'],'|'.join(lines[i]['name'] for i in s['skinline_ids'] if i in lines),'|'.join(s['wiki_sets']),'|'.join(worlds[i]['name'] for i in s['universe_ids']),s['variant_of'],len(s['chromas']),s['lore']['available'],s['matching']['label_eligible']])
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()

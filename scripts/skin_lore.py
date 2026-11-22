#!/usr/bin/env python3
"""Resolve original skin biographies on demand for local research (not redistributed)."""
import argparse,json,pathlib,urllib.request,urllib.parse,sys
from build_skins import plain,sha,wiki_payload
from lua_table import parse
ROOT=pathlib.Path(__file__).resolve().parents[1]
def pointer(data,path):
 for segment in path.strip('/').split('/'):
  segment=segment.replace('~1','/').replace('~0','~');data=data[int(segment)] if isinstance(data,list) else data[segment]
 return data
def main():
 p=argparse.ArgumentParser();p.add_argument('--skin',help='Exact result key, Riot skin ID, or exact full skin name');p.add_argument('--all',action='store_true',help='Resolve all available biographies');p.add_argument('--output',help='Optional local JSON output, e.g. .cache/skin-lore.json');a=p.parse_args()
 records=json.loads((ROOT/'data/skins.json').read_text());sources={s['id']:s for s in json.loads((ROOT/'data/skin_sources.json').read_text())['sources']};cache={};warnings=[]
 if a.all:selected=[s for s in records if s['lore']['available']]
 elif a.skin:
  selected=[s for s in records if a.skin.casefold() in [s['id'].casefold(),str(s['riot_skin_id']).casefold(),s['name'].casefold()]]
  if len(selected)!=1:raise SystemExit(f'Expected one exact match; found {len(selected)}.')
 else:raise SystemExit('Choose --skin or --all.')
 def payload(id):
  if id in cache:return cache[id]
  source=sources[id];folder=ROOT/'.cache/skins';file=folder/('client/'+id.rsplit(':',1)[1]+'.json') if id.startswith('skins:client:') else folder/('wiki_skins.json' if id=='skins:wiki' else 'skins.json')
  if file.exists():raw=file.read_bytes()
  else:
   u=source['url']
   if id=='skins:wiki':u='https://wiki.leagueoflegends.com/en-us/api.php?action=query&format=json&prop=revisions&rvprop=ids%7Ctimestamp%7Ccontent&rvslots=main&titles=Module%3ASkinData%2Fdata&rvstartid='+str(source['revision_id'])+'&rvendid='+str(source['revision_id'])
   raw=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'LoLChampionResearch/0.2 (source-linked research)'}),timeout=40).read();file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(raw)
  data=json.loads(raw)
  if id=='skins:wiki':data=parse(next(iter(data['query']['pages'].values()))['revisions'][0]['slots']['main']['*'])
  cache[id]=data;return data
 out=[]
 for skin in selected:
  lore=skin['lore'];id=lore['source_id']
  if not id:continue
  data=payload(id)
  if lore['json_pointer']:text=plain(pointer(data,lore['json_pointer']))
  else:
   loc=lore['wiki_locator'];text=plain(data[loc['champion']]['skins'][loc['skin']]['lore'])
  matches=sha(text)==lore['biography_sha256']
  if not matches:warnings.append(skin['id'])
  out.append({'id':skin['id'],'name':skin['name'],'source_id':id,'biography':text,'matches_snapshot':matches})
 result={'skins':out,'changed_biography_ids':warnings}
 text=json.dumps(result,ensure_ascii=False,indent=2)
 if a.output:
  path=pathlib.Path(a.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8');print(f'Wrote {len(out)} source biographies; {len(warnings)} differ from the snapshot.')
 else:print(text)
if __name__=='__main__':main()

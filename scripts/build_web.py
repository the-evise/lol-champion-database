#!/usr/bin/env python3
"""Build a dependency-free visual browser from the committed database."""
import argparse,concurrent.futures,json,pathlib,shutil,urllib.request,io,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
REGIONS={'bandle-city':'Bandle City','bilgewater':'Bilgewater','demacia':'Demacia','freljord':'Freljord','ionia':'Ionia','ixtal':'Ixtal','mount-targon':'Targon','noxus':'Noxus','piltover':'Piltover','shadow-isles':'Shadow Isles','shurima':'Shurima','unaffiliated':'Across Runeterra','void':'The Void','zaun':'Zaun'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--download-art',action='store_true',help='Cache official splash art as optimized WebP (requires Pillow)');p.add_argument('--output',default=str(ROOT/'dist'));a=p.parse_args()
 records=json.loads((ROOT/'data/champions.json').read_text());cache=ROOT/'.cache/art';cache.mkdir(parents=True,exist_ok=True);failures=[]
 if a.download_art:
  from PIL import Image,ImageOps
  def download(c):
   id=c['id'];card=cache/(id+'-card.webp');hero=cache/(id+'-hero.webp')
   if card.exists() and hero.exists():return
   url=f'https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{id}_0.jpg'
   for attempt in range(3):
    try:
     with urllib.request.urlopen(url,timeout=30) as r:im=Image.open(io.BytesIO(r.read())).convert('RGB')
     # The right half of most Riot splashes contains the character.
     ImageOps.fit(im,(420,470),centering=(0.64,0.45)).save(card,'WEBP',quality=78)
     im.thumbnail((1500,900));im.save(hero,'WEBP',quality=80);return
    except Exception as e:
     if attempt==2:failures.append({'id':id,'error':str(e)})
     else:time.sleep(1+attempt)
  with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(download,records))
 out=pathlib.Path(a.output);out.mkdir(parents=True,exist_ok=True)
 for p in (ROOT/'web').iterdir():
  if p.is_file():shutil.copy2(p,out/p.name)
 if not (cache/'Kindred-hero.webp').exists():
  css=out/'styles.css';css.write_text(css.read_text().replace('assets/champions/Kindred-hero.webp','https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Kindred_0.jpg'))
 (out/'data/champions').mkdir(parents=True,exist_ok=True);(out/'assets/champions').mkdir(parents=True,exist_ok=True)
 catalog=[]
 for c in records:
  id=c['id'];local=all((cache/(id+'-'+kind+'.webp')).exists() for kind in ['card','hero'])
  if local:
   for kind in ['card','hero']:shutil.copy2(cache/(id+'-'+kind+'.webp'),out/'assets/champions'/(id+'-'+kind+'.webp'))
  remote=f'https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{id}_0.jpg'
  catalog.append({'id':id,'name':c['name'],'title':c['title'],'region':c['lore']['region'],'region_name':REGIONS.get(c['lore']['region'],'Unknown'),'positions':c['gameplay']['positions']['client'],'classes':c['gameplay']['classes_data_dragon'],'subclasses':c['gameplay']['subclasses_wiki'],'difficulty':c['gameplay']['ratings']['difficulty'],'themes':[t['theme'] for t in c['analysis']['candidate_themes']],'story_count':sum(r['type']=='story' for r in c['lore']['resources']),'portrait':f'assets/champions/{id}-card.webp' if local else remote,'hero':f'assets/champions/{id}-hero.webp' if local else remote})
  (out/'data/champions'/(id+'.json')).write_text(json.dumps(c,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 (out/'data/catalog.json').write_text(json.dumps({'champions':catalog,'regions':REGIONS,'coverage':json.loads((ROOT/'data/coverage.json').read_text())},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 if (ROOT/'data/skins.json').exists():
  skins=json.loads((ROOT/'data/skins.json').read_text());lines=json.loads((ROOT/'data/skinlines.json').read_text());worlds=json.loads((ROOT/'data/skin_universes.json').read_text())
  skin_catalog={'coverage':json.loads((ROOT/'data/skin_coverage.json').read_text()),'lines':[{'id':l['id'],'name':l['name'],'count':len(l['skin_ids'])} for l in lines],'worlds':[{'id':w['id'],'name':w['name'],'count':len(w['skin_ids'])} for w in worlds],'skins':[{'id':s['id'],'c':s['champion_id'],'n':s['name'],'r':s['rarity'],'l':s['skinline_ids'],'u':s['universe_ids'],'a':s['artwork']['tile'],'eligible':s['matching']['label_eligible'],'availability':s['availability'],'kind':s['kind'],'chromas':len(s['chromas']),'sets':s['wiki_sets'],'v':s['vibe']['tags']} for s in skins if not s['is_base']]}
  (out/'data/skin-catalog.json').write_text(json.dumps(skin_catalog,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
  (out/'data/skins').mkdir(parents=True,exist_ok=True)
  for p in (ROOT/'data/skins').glob('*.json'):(out/'data/skins'/p.name).write_text(json.dumps(json.loads(p.read_text()),ensure_ascii=False,separators=(',',':')),encoding='utf-8')
  # One small, local hero keeps the skin landing page stable; cards load on demand.
  skin_art=cache.parent/'skin-hero.webp'
  (out/'assets/skins').mkdir(parents=True,exist_ok=True)
  if skin_art.exists():shutil.copy2(skin_art,out/'assets/skins/coven-morgana.webp')
  else:
   css=out/'styles.css';css.write_text(css.read_text().replace('assets/skins/coven-morgana.webp','https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Morgana_26.jpg'))
 print(json.dumps({'champions':len(catalog),'local_art':sum('assets/' in c['portrait'] for c in catalog),'art_failures':failures,'catalog_bytes':(out/'data/catalog.json').stat().st_size,'output':str(out)}))
if __name__=='__main__':main()

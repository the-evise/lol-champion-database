#!/usr/bin/env python3
"""Refresh pinned PC skin metadata from client files and Wiki; cache originals locally."""
import argparse,concurrent.futures,datetime,json,pathlib,urllib.parse
from refresh_sources import fetch
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--patch',help='CommunityDragon patch; defaults to champion snapshot major.minor');a=p.parse_args()
 records=json.loads((ROOT/'data/champions.json').read_text());patch=a.patch or records[0]['snapshot_version'].rsplit('.',1)[0];cache=ROOT/'.cache/skins';cache.mkdir(parents=True,exist_ok=True)
 base=f'https://raw.communitydragon.org/{patch}/plugins/rcp-be-lol-game-data/global/default/v1/'
 jobs=[(base+name+'.json',cache/(name+'.json')) for name in ['skins','skinlines','universes']]
 for title,name in [('Module:SkinData/data','wiki_skins.json'),('Module:SkinData/universes','wiki_universe_groups.json')]:
  u='https://wiki.leagueoflegends.com/en-us/api.php?action=query&format=json&prop=revisions&rvprop=ids%7Ctimestamp%7Ccontent&rvslots=main&titles='+urllib.parse.quote(title);jobs.append((u,cache/name))
 for c in records:jobs.append((base+f'champions/{c["riot_id"]}.json',cache/'client'/(c['id']+'.json')))
 failures=[]
 def job(item):
  u,path=item
  try:fetch(u,path)
  except Exception as e:
   # A failed request must never silently reuse a previous payload.
   failures.append({'url':u,'file':str(path.relative_to(ROOT)),'error':str(e)})
   if path.exists():path.unlink()
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(job,jobs))
 (cache/'failures.json').write_text(json.dumps(failures,indent=2))
 if failures:raise SystemExit(f'{len(failures)} requests failed. Inspect .cache/skins/failures.json before building.')
 if patch!=records[0]['snapshot_version'].rsplit('.',1)[0]:raise SystemExit('Downloaded patch differs from champion snapshot. Update champion snapshot before building the combined database.')
 print(f'Fetched {len(jobs)} sources at {patch}. Run python scripts/build_skins.py, then python scripts/build.py --sqlite-only.')
if __name__=='__main__':main()

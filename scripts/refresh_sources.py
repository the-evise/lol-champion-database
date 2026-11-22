#!/usr/bin/env python3
"""Refresh public sources. No Riot key, credentials, or third-party Python packages."""
import argparse, concurrent.futures, json, pathlib, time, urllib.request, unicodedata
ROOT=pathlib.Path(__file__).resolve().parents[1]
UA={'User-Agent':'LoLChampionResearch/0.1 (source-linked personal research)'}
def normalized(s): return ''.join(c.lower() for c in unicodedata.normalize('NFKD',s) if c.isalnum())
def fetch(url,path):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=45) as r: data=json.load(r)
            path.parent.mkdir(parents=True,exist_ok=True)
            tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8');tmp.replace(path)
            return data
        except Exception:
            if attempt==2:raise
            time.sleep(attempt+1)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--version',help='Pin an available Data Dragon version; otherwise use latest');args=parser.parse_args()
    cache=ROOT/'.cache';cache.mkdir(exist_ok=True)
    versions=fetch('https://ddragon.leagueoflegends.com/api/versions.json',cache/'versions.json')
    version=args.version or versions[0]
    roster=fetch(f'https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json',cache/'roster.json')
    index=fetch('https://universe-meeps.leagueoflegends.com/v1/en_us/champion-browse/index.json',cache/'universe_index.json')
    wiki='https://wiki.leagueoflegends.com/en-us/api.php?action=query&format=json&titles=Module:ChampionData/data&prop=revisions&rvprop=ids%7Ctimestamp%7Ccontent&rvslots=main'
    fetch(wiki,cache/'wiki.json')
    fetch('https://wiki.leagueoflegends.com/en-us/api.php?action=query&format=json&meta=siteinfo&siprop=rightsinfo',cache/'wiki_rights.json')
    lookup={normalized(c['name']):c for c in index['champions']}
    failures=[]
    def champion(c):
        slug=lookup.get(normalized(c['name']),{}).get('slug',normalized(c['name']))
        for kind,url in [('universe',f'https://universe-meeps.leagueoflegends.com/v1/en_us/champions/{slug}/index.json'),('ddragon',f'https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion/{c["id"]}.json')]:
            try:fetch(url,cache/kind/(c['id']+'.json'))
            except Exception as e:
                # Never reuse an old successful file as if this fetch succeeded.
                failures.append({'champion':c['id'],'source':kind,'error':str(e)})
                p=cache/kind/(c['id']+'.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'error':str(e),'url':url}))
        print(c['id'],flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(champion,roster['data'].values()))
    (cache/'failures.json').write_text(json.dumps(failures,indent=2))
    if failures:raise SystemExit(f'{len(failures)} source requests failed; inspect .cache/failures.json. Build will report gaps.')
    print(f'Fetched {len(roster["data"])} champions at {version}. Next: python scripts/build.py')
if __name__=='__main__':main()

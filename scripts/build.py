#!/usr/bin/env python3
"""Produce portable JSON/CSV/Markdown and SQLite from cached sources + editorial work."""
import argparse, collections, csv, datetime, hashlib, html, json, pathlib, re, sqlite3, sys
from urllib.parse import quote
from lua_table import parse
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=ROOT/'data';CACHE=ROOT/'.cache'
POSITIONS={'Top':'top','Jungle':'jungle','Middle':'mid','Bottom':'bottom','Support':'support'}
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def plain(s):return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',s or ''))).strip()
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def stamp(p):return datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat()
def array(v):return v if isinstance(v,list) else []
def source(id,kind,url,path,**more):
    return {'id':id,'kind':kind,'url':url,'retrieved_at':stamp(path),'payload_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),**more}
def normalize(s):return ''.join(c.lower() for c in s if c.isalnum())
def build_sqlite(path,records,sources):
    path.parent.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(path)
    con.executescript((ROOT/'schema.sql').read_text())
    con.executescript((ROOT/'skin_schema.sql').read_text())
    with con:
        for table in ['skin_chromas','skin_line_memberships','skin_universe_memberships','skins','skin_lines','skin_universes','champion_roles','champion_themes','related_champions','champion_resources','abilities','sources','champions']:con.execute('DELETE FROM '+table)
        for c in records:
            g=c['gameplay'];l=c['lore'];a=c['analysis'];r=g['ratings']
            con.execute('INSERT INTO champions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(c['id'],c['riot_id'],c['name'],c['title'],l['region'],l['summary'],a['central_motivation'],g['range_type'],r.get('difficulty'),r.get('damage'),r.get('toughness'),r.get('control'),r.get('mobility'),r.get('utility'),json.dumps(c,ensure_ascii=False)))
            for role in g['positions']['client']:con.execute('INSERT INTO champion_roles VALUES (?,?,?)',(c['id'],role,'client'))
            for role in g['positions']['external']:con.execute('INSERT INTO champion_roles VALUES (?,?,?)',(c['id'],role,'external'))
            for t in a['candidate_themes']:con.execute('INSERT INTO champion_themes VALUES (?,?,?)',(c['id'],t['theme'],t['evidence']))
            for t in l['related_champions']:con.execute('INSERT INTO related_champions VALUES (?,?,?,?)',(c['id'],t['id'],t['name'],'universe_curated_relation'))
            for t in l['resources']:con.execute('INSERT INTO champion_resources VALUES (?,?,?,?,?)',(c['id'],t['type'],t['title'],t['url'],t['review_status']))
            for t in g['abilities']:con.execute('INSERT INTO abilities VALUES (?,?,?,?)',(c['id'],t['slot'],t['name'],json.dumps(t,ensure_ascii=False)))
        for s in sources:con.execute('INSERT INTO sources VALUES (?,?,?,?)',(s['id'],s['kind'],s['url'],json.dumps(s,ensure_ascii=False)))
        if (DATA/'skins.json').exists():
            for line in load(DATA/'skinlines.json'):con.execute('INSERT INTO skin_lines VALUES (?,?,?)',(line['id'],line['name'],json.dumps(line,ensure_ascii=False)))
            for universe in load(DATA/'skin_universes.json'):con.execute('INSERT INTO skin_universes VALUES (?,?,?)',(universe['id'],universe['name'],json.dumps(universe,ensure_ascii=False)))
            for s in load(DATA/'skins.json'):
                con.execute('INSERT INTO skins VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',(s['id'],s['riot_skin_id'],s['champion_id'],s['name'],s['is_base'],s['kind'],s['rarity'],s['availability'],s['release_date'],s['variant_of'],s['lore']['available'],s['matching']['label_eligible'],json.dumps(s,ensure_ascii=False)))
                for lid in s['skinline_ids']:con.execute('INSERT INTO skin_line_memberships VALUES (?,?)',(s['id'],lid))
                for uid in s['universe_ids']:con.execute('INSERT INTO skin_universe_memberships VALUES (?,?)',(s['id'],uid))
                for ch in s['chromas']:con.execute('INSERT INTO skin_chromas VALUES (?,?,?,?)',(ch['id'],s['id'],ch['name'],json.dumps(ch,ensure_ascii=False)))
            for source in load(DATA/'skin_sources.json')['sources']:con.execute('INSERT INTO sources VALUES (?,?,?,?)',(source['id'],source['kind'],source['url'],json.dumps(source,ensure_ascii=False)))
    con.execute('VACUUM');con.close()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--sqlite-only',action='store_true');args=parser.parse_args()
    if args.sqlite_only:
        records=load(DATA/'champions.json');sources=load(DATA/'sources.json')['sources'];build_sqlite(ROOT/'build/champions.sqlite',records,sources);print(f'Built SQLite for {len(records)} champions');return
    roster=load(CACHE/'roster.json');version=roster['version'];index=load(CACHE/'universe_index.json')
    wp=next(iter(load(CACHE/'wiki.json')['query']['pages'].values()));rev=wp['revisions'][0];wiki=parse(rev['slots']['main']['*'])
    byid={str(v['id']):v for v in wiki.values()};names={normalize(v['name']):v['id'] for v in roster['data'].values()}
    editorial={r['id']:r for r in csv.DictReader((DATA/'editorial.tsv').open(encoding='utf-8'),delimiter='\t')}
    pinned_path=DATA/'editorial_source_hashes.json';pins=load(pinned_path) if pinned_path.exists() else {}
    sources=[source('roster','riot_data_dragon',f'https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json',CACHE/'roster.json',version=version),source('universe_index','riot_universe','https://universe-meeps.leagueoflegends.com/v1/en_us/champion-browse/index.json',CACHE/'universe_index.json'),source('wiki_champion_data','league_wiki','https://wiki.leagueoflegends.com/en-us/Module:ChampionData/data',CACHE/'wiki.json',revision_id=rev['revid'],revision_timestamp=rev['timestamp'],permalink=f'https://wiki.leagueoflegends.com/en-us/index.php?title=Module:ChampionData/data&oldid={rev["revid"]}',history_url='https://wiki.leagueoflegends.com/en-us/Module:ChampionData/data?action=history',license=load(CACHE/'wiki_rights.json')['query']['rightsinfo'])]
    records=[];gaps=[]
    for id,b in roster['data'].items():
        up=CACHE/'universe'/(id+'.json');dp=CACHE/'ddragon'/(id+'.json')
        ud=load(up) if up.exists() else {};dd=load(dp) if dp.exists() else {};uc=ud.get('champion',{});d=dd.get('data',{}).get(id,{});w=byid.get(b['key'],{})
        slug=uc.get('slug',normalize(b['name']));short=plain(uc.get('biography',{}).get('short'));full=plain(uc.get('biography',{}).get('full'));short_hash=digest(short)
        ed=editorial.get(id);reviewed=False
        if ed and short:
            if id not in pins:pins[id]=short_hash
            reviewed=pins[id]==short_hash
        if not uc:gaps.append({'id':id,'field':'universe','reason':ud.get('error','missing')})
        if not d:gaps.append({'id':id,'field':'game_data','reason':dd.get('error','missing')})
        if not w:gaps.append({'id':id,'field':'wiki','reason':'missing'})
        if not ed:gaps.append({'id':id,'field':'editorial','reason':'new champion requires authored summary'})
        if ed and not reviewed:gaps.append({'id':id,'field':'editorial_review','reason':'source missing or changed; review required'})
        universe_id='universe:'+id;game_id='ddragon:'+id
        if up.exists():sources.append(source(universe_id,'riot_universe',f'https://universe-meeps.leagueoflegends.com/v1/en_us/champions/{slug}/index.json',up,short_biography_sha256=short_hash,full_biography_sha256=digest(full),full_biography_word_count=len(full.split())))
        if dp.exists():sources.append(source(game_id,'riot_data_dragon',f'https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion/{id}.json',dp,version=version))
        related=[]
        for c in ud.get('related-champions',[]):
            rid=names.get(normalize(c['name']));related.append({'id':rid,'name':c['name'],'url':'https://universe.leagueoflegends.com'+c['url'],'relationship_type':'curated_related_link','specific_relationship':None})
        resources=[]
        for m in ud.get('modules',[]):
            kind=m.get('type');url=m.get('url') or m.get('uri')
            if kind not in ['story-preview','featured-video'] or not url:continue
            if url.startswith('/'):url='https://universe.leagueoflegends.com'+url
            resources.append({'type':'story' if kind=='story-preview' else 'video','title':plain(m.get('title','')),'url':url,'story_slug':m.get('story-slug'),'published_at':m.get('release-date'),'minutes_to_read':m.get('minutes-to-read'),'review_status':'catalogued_not_read','continuity_status':'not_adjudicated'})
        abilities=[]
        if d:
            abilities.append({'slot':'P','name':d.get('passive',{}).get('name'),'source_id':game_id})
            for slot,a in zip(['Q','W','E','R'],d.get('spells',[])):
                abilities.append({'slot':slot,'name':a['name'],'cooldown_by_rank':a.get('cooldown'),'cost_by_rank':a.get('cost'),'range_by_rank':a.get('range'),'source_id':game_id,'data_caveat':'Static API values may omit conditional changes or special cases.'})
        ratings={k:w.get(k) for k in ['difficulty','damage','toughness','control','mobility','utility','style']}
        notes=['Summary is an original paraphrase of the retrieved Universe short biography; full biography and linked stories are not editorially reviewed.','Universe links may include historical or alternate-continuity material; continuity has not been adjudicated.']
        if id=='JarvanIV':notes.append('Source describes Jarvan as prince/heir. Reconcile royal status against later narrative sources before displaying a current-status claim.')
        if id=='Rammus':notes.append('Origin theories in the source are presented as speculation; do not turn them into confirmed facts.')
        if id=='Amumu':notes.append('The source explicitly treats the origin as uncertain folklore.')
        if id=='Shaco':notes.append('The summary follows the current retrieved biography; do not infer that every origin detail has independent confirmation.')
        summary=ed['summary'] if ed else None
        themes=[{'theme':t,'evidence':summary,'evidence_source_id':universe_id,'status':'tentative_interpretation'} for t in ed['candidate_themes'].split(';')] if ed else []
        c={'schema_version':'1.0.0','id':id,'riot_id':int(b['key']),'name':b['name'],'title':b['title'],'snapshot_version':version,
           'lore':{'universe_slug':slug,'biography_url':f'https://universe.leagueoflegends.com/en_US/story/champion/{slug}/','champion_url':f'https://universe.leagueoflegends.com/en_US/champion/{slug}/','summary':summary,'summary_kind':'original_paraphrase','summary_evidence_scope':'universe_short_biography','region':uc.get('associated-faction-slug') or None,'species_as_listed':[x['name'] for x in uc.get('races',[])],'related_champions':related,'resources':resources,'notes':notes,'source_id':universe_id},
           'gameplay':{'classes_data_dragon':d.get('tags',b.get('tags',[])),'subclasses_wiki':array(w.get('role')),'client_tags_wiki':array(w.get('client_tags')),'positions':{'client':[POSITIONS[x] for x in array(w.get('client_positions')) if x in POSITIONS],'external':[POSITIONS[x] for x in array(w.get('external_positions')) if x in POSITIONS],'source_id':'wiki_champion_data','caveat':'Client labels and secondary external labels; neither is a current role win-rate estimate.'},'range_type':w.get('rangetype'),'resource':d.get('partype'),'release_date_wiki':w.get('date'),'last_changed_patch_wiki':w.get('changes'),'ratings':ratings,'ratings_source_id':'wiki_champion_data','adaptive_damage_type_wiki':w.get('adaptivetype'),'base_stats_data_dragon':d.get('stats',{}),'abilities':abilities,'source_id':game_id},
           'analysis':{'status':'exploratory_not_quiz_validated','central_motivation':ed['motivation'] if ed else None,'candidate_themes':themes,'personality_scores':None,'personality_quiz_ready':False,'gameplay_features':{**{k:((v-1)/2 if k=='difficulty' else v/3) if isinstance(v,(int,float)) else None for k,v in ratings.items() if k!='style'},'ability_vs_attack_style':ratings['style']/100 if isinstance(ratings['style'],(int,float)) else None},'feature_method':'Source rating normalization only: difficulty: (rating-1)/2; capabilities: rating/3; style/100. Not measured performance or personality.'},
           'provenance':{'lore':universe_id,'gameplay_api':game_id,'gameplay_wiki':'wiki_champion_data','editorial':'data/editorial.tsv','field_exceptions':['candidate themes and motivation are interpretations, not Riot labels','specific relationship types and unlisted species are unknown']},
           'coverage':{'universe_available':bool(uc),'full_biography_available':bool(full),'short_bio_editorial_review':reviewed,'full_biography_editorial_review':False,'linked_story_editorial_review':False,'wiki_available':bool(w),'game_data_available':bool(d),'continuity_reconciled':False}}
        records.append(c);write(DATA/'champions'/(id+'.json'),c)
    records.sort(key=lambda c:c['name'].casefold())
    expected={c['id'] for c in records}
    for p in (DATA/'champions').glob('*.json'):
        if p.stem not in expected:p.unlink()
    write(pinned_path,pins);write(DATA/'champions.json',records)
    write(DATA/'sources.json',{'snapshot_version':version,'sources':sources})
    playable={normalize(c['name']) for c in records}
    report={'snapshot_version':version,'champion_count':len(records),'coverage_counts':{k:sum(c['coverage'][k] for c in records) for k in records[0]['coverage']},'story_links':sum(sum(r['type']=='story' for r in c['lore']['resources']) for c in records),'unique_story_urls':len({r['url'] for c in records for r in c['lore']['resources'] if r['type']=='story'}),'universe_entries_outside_playable_roster':[{'name':c['name'],'slug':c['slug']} for c in index['champions'] if normalize(c['name']) not in playable],'wiki_forms_outside_roster':[n for n,v in wiki.items() if str(v['id']) not in {str(c['riot_id']) for c in records}],'gaps':gaps,'deep_research_complete':False}
    write(DATA/'coverage.json',report)
    csvfields=['id','name','region','positions_client','positions_external','subclasses','range_type','difficulty','damage','toughness','control','mobility','utility','style','candidate_themes','motivation','summary']
    with (DATA/'champions.csv').open('w',newline='',encoding='utf-8') as f:
        out=csv.DictWriter(f,fieldnames=csvfields);out.writeheader()
        for c in records:
            g=c['gameplay'];out.writerow({'id':c['id'],'name':c['name'],'region':c['lore']['region'],'positions_client':'|'.join(g['positions']['client']),'positions_external':'|'.join(g['positions']['external']),'subclasses':'|'.join(g['subclasses_wiki']),'range_type':g['range_type'],**g['ratings'],'candidate_themes':'|'.join(t['theme'] for t in c['analysis']['candidate_themes']),'motivation':c['analysis']['central_motivation'],'summary':c['lore']['summary']})
    dossiers=ROOT/'docs/champions';dossiers.mkdir(parents=True,exist_ok=True)
    for c in records:
        g=c['gameplay'];l=c['lore'];a=c['analysis']
        text=f'# {c["name"]} — {c["title"]}\n\n{l["summary"] or "Editorial summary pending."}\n\n'
        text+='## Lore and interpretation\n\n'
        text+=f'- Region in Universe: {l["region"] or "Unknown"}\n- Motivation (interpretation): {a["central_motivation"]}\n- Candidate themes (unvalidated): '+', '.join(t['theme'] for t in a['candidate_themes'])+'\n\n'
        text+=f'[Champion profile]({l["champion_url"]}) · [Full original biography]({l["biography_url"]}) · [Wiki](https://wiki.leagueoflegends.com/en-us/{quote(c["name"].replace(" ","_"))}) · [JSON record](../../data/champions/{c["id"]}.json)\n\n'
        text+='## Gameplay snapshot\n\n| Field | Value |\n|---|---|\n'
        for k,v in [('Client positions',', '.join(g['positions']['client'])),('External positions',', '.join(g['positions']['external'])),('Wiki subclasses',', '.join(g['subclasses_wiki'])),('Range type',g['range_type']),('Resource',g['resource']),*g['ratings'].items()]:text+=f'| {k} | {v} |\n'
        text+='\nDifficulty uses 1–3; capability ratings use 0–3 (0 means absent); style uses 0–100. These are coarse source labels, not win-rate statistics.\n\n'
        text+='## Linked stories and media\n\n'
        text+='\n'.join(f'- [{r["title"]}]({r["url"]}) ({r["type"]}; catalogued, not read)' for r in l['resources']) or 'No linked resource in the retrieved profile.'
        text+='\n\n## Research status\n\n'+'\n'.join('- '+n for n in l['notes'])+'\n\nSee [source manifest](../../data/sources.json) for retrieval timestamps, hashes, and Wiki revision.\n'
        (dossiers/(c['id']+'.md')).write_text(text,encoding='utf-8')
    (ROOT/'docs/INDEX.md').write_text('# Champion index\n\n'+''.join(f'- [{c["name"]}](champions/{c["id"]}.md)\n' for c in records),encoding='utf-8')
    build_sqlite(ROOT/'build/champions.sqlite',records,sources)
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()

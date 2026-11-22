"""Conservative aesthetic labels. No lore, personality, price, or rarity inference."""
import json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
def load_rules():return json.loads((ROOT/'data/skin_vibe_rules.json').read_text(encoding='utf-8'))
def assign_vibes(skin,rules):
 name=skin['name'].casefold().strip();key=skin['id']
 if skin['is_base']:pair=rules['base_tags'];kind='base_presentation';rule='base'
 elif key in rules['skin_overrides']:pair=rules['skin_overrides'][key];kind='individual_editorial';rule='skin:'+key
 else:
  hit=next((r for r in rules['name_rules'] if re.search(r['pattern'],name)),None)
  if hit:pair=hit['tags'];kind='name_theme';rule=hit['id']
  else:
   lines=[str(i) for i in skin['skinline_ids'] if str(i) in rules['skinlines']]
   lines.sort(key=lambda i:(int(i) in rules['broad_line_ids'],int(i)))
   if lines:pair=rules['skinlines'][lines[0]]['tags'];kind='skin_line_theme';rule='line:'+lines[0]
   else:
    alias=next((rules['wiki_set_aliases'][n] for n in skin['wiki_sets'] if n in rules['wiki_set_aliases']),None)
    if alias:pair=rules['skinlines'][str(alias)]['tags'];kind='wiki_set_theme';rule='line:'+str(alias)
    else:pair=rules['fallback_tags'];kind='generic_fallback';rule='fallback'
 if len(pair)!=2 or len(set(pair))!=2 or any(t not in rules['vocabulary'] for t in pair):raise ValueError(f'Invalid aesthetic pair for {key}: {pair}')
 return {'tags':list(pair),'scope':'aesthetic_impression','basis':kind,'rule_id':rule,'rules_ref':'data/skin_vibe_rules.json','method_version':rules['version'],'lore_based':False,'personality_claim':False,'individual_artwork_reviewed':False}

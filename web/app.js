'use strict';
const $ = (s, root = document) => root.querySelector(s);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const REPOSITORY = 'https://github.com/the-evise/lol-champion-database';
const roleNames = {top:'Top',jungle:'Jungle',mid:'Mid',bottom:'Bottom',support:'Support'};
const difficultyNames = {1:'Easy',2:'Moderate',3:'Hard'};
const icons = {
 all:'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c-5 5-5 13 0 18 5-5 5-13 0-18Z"/>',
 top:'<path d="M3 3h18L6 18H3V3Zm3 3v7L13 6H6ZM9 21h12V9"/>',
 jungle:'<path d="M12 21C4 17 3 11 4 4l5 6L8 2l5 7 3-6 1 9 4-3c-1 6-4 10-9 12Z"/>',
 mid:'<path d="M3 3h12M3 3v12M21 21H9m12 0V9M4 20 20 4m-2-1h3v3M3 18v3h3"/>',
 bottom:'<path d="M21 21H3L18 6h3v15Zm-3-3v-7l-7 7h7ZM15 3H3v12"/>',
 support:'<path d="m12 3 3 5 6 1-4 5 1 7-6-3-6 3 1-7-4-5 6-1 3-5Z"/>',
 demacia:'<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3ZM8 9l4 3 4-3M12 6v11"/>',
 freljord:'<path d="M12 2v20M3 7l18 10M3 17 21 7M8 4l4 4 4-4M8 20l4-4 4 4M3 11l5-1-1-5m14 8-5 1 1 5"/>',
 ionia:'<path d="M12 21C4 17 3 9 5 3c5 1 8 5 7 10 0-5 4-8 9-8-1 7-4 12-9 16ZM7 9l5 12M17 10l-5 11"/>',
 noxus:'<path d="m12 2 7 8-3 10-4-3-4 3-3-10 7-8ZM12 7v10M8 11l4 2 4-2"/>',
 shurima:'<circle cx="12" cy="12" r="4"/><path d="M12 1v4m0 14v4M1 12h4m14 0h4M4 4l3 3m10 10 3 3M4 20l3-3M17 7l3-3"/>',
 'mount-targon':'<path d="m2 21 7-13 4 7 3-11 6 17H2ZM12 2v4M10 4h4"/>',
 piltover:'<path d="m12 2 3 4 5 1-1 5 1 5-5 1-3 4-3-4-5-1 1-5-1-5 5-1 3-4Z"/><circle cx="12" cy="12" r="4"/>',
 zaun:'<path d="M9 3h6M10 3v7L4 20h16l-6-10V3M8 15h8"/><circle cx="12" cy="17" r="1"/>',
 bilgewater:'<path d="M12 3v17M8 7l4-4 4 4M3 13c0 7 6 8 9 8s9-1 9-8M3 13l-1 4m1-4 4 1m14-1 1 4m-1-4-4 1"/>',
 'shadow-isles':'<path d="M6 20c-4-6-1-15 6-18 7 3 10 12 6 18l-3-2-3 4-3-4-3 2Z"/><path d="m8 11 2 2m6-2-2 2M12 16v1"/>',
 void:'<path d="m12 2 9 6v8l-9 6-9-6V8l9-6Zm0 5 5 5-5 5-5-5 5-5Z"/>',
 ixtal:'<path d="m12 2 10 10-10 10L2 12 12 2Zm0 5 5 5-5 5-5-5 5-5ZM2 12h5m10 0h5M12 2v5m0 10v5"/>',
 'bandle-city':'<path d="M12 21V10m0 5C3 15 1 9 3 5c6 0 10 3 9 10Zm0-3c0-7 5-9 9-8 0 5-3 9-9 8Z"/>',
 book:'<path d="M12 5C8 2 4 3 2 4v15c4-2 7-1 10 1 3-2 6-3 10-1V4c-3-1-7-2-10 1Zm0 0v15"/>',
};
function icon(key) { return `<svg viewBox="0 0 24 24" aria-hidden="true">${icons[key] || icons.all}</svg>`; }
function difficulty(value) {return `<span class="difficulty" aria-label="${esc(difficultyNames[value] || 'Unknown')} difficulty">${[1,2,3].map(i=>`<i class="${i<=value?'on':''}"></i>`).join('')}</span>`;}
function external(url, text, className='') {return `<a class="${className}" href="${esc(url)}" target="_blank" rel="noopener noreferrer">${text}</a>`;}
function safeDate(value) {if (!value) return null;const d=new Date(value);return Number.isFinite(d.getTime())?d:null;}
let catalog=[], regions={}, coverage={}, byId=new Map(), filterState={q:'',position:'',class:'',difficulty:'',region:'',sort:'name'}, selected=null, browseScroll=0, renderGeneration=0;
const detailCache=new Map();
function readState() {
 const p=new URLSearchParams(location.search);
 for(const k of Object.keys(filterState)) filterState[k]=p.get(k)||(k==='sort'?'name':'');
 const match=location.hash.match(/^#champion\/([^/]+)$/);try{selected=match?decodeURIComponent(match[1]):null;}catch{selected='invalid-link';}
 if(filterState.position&&!roleNames[filterState.position])filterState.position='';
 if(filterState.region&&!regions[filterState.region])filterState.region='';
 if(!['','1','2','3'].includes(filterState.difficulty))filterState.difficulty='';
 if(!['name','stories','difficulty'].includes(filterState.sort))filterState.sort='name';
}
function updateUrl(push=false) {
 const url=new URL(location.href);url.search='';
 for(const [k,v] of Object.entries(filterState)) if(v&&!(k==='sort'&&v==='name'))url.searchParams.set(k,v);
 url.hash=selected?`champion/${encodeURIComponent(selected)}`:'';
 history[push?'pushState':'replaceState']({browseScroll},'',url);
}
function filtered(ignoreRegion=false) {
 const query=filterState.q.trim().toLocaleLowerCase();
 return catalog.filter(c=>(!query||[c.name,c.title,...c.themes,c.region_name].join(' ').toLocaleLowerCase().includes(query))&&(!filterState.position||c.positions.includes(filterState.position))&&(!filterState.class||c.classes.includes(filterState.class)||c.subclasses.includes(filterState.class))&&(!filterState.difficulty||c.difficulty===Number(filterState.difficulty))&&(ignoreRegion||!filterState.region||c.region===filterState.region));
}
function renderRegions() {
 const counts={};for(const c of filtered(true))counts[c.region]=(counts[c.region]||0)+1;
 const total=Object.values(counts).reduce((a,b)=>a+b,0);
 $('#region-list').innerHTML=`<button class="region-button ${!filterState.region?'active':''}" data-region="" aria-pressed="${!filterState.region}">${icon('all')}<span>All Runeterra</span><span class="region-count">${total}</span></button><div class="region-divider"></div>`+Object.entries(regions).sort((a,b)=>a[1].localeCompare(b[1])).map(([id,name])=>`<button class="region-button ${filterState.region===id?'active':''}" data-region="${esc(id)}" aria-pressed="${filterState.region===id}">${icon(id)}<span>${esc(name)}</span><span class="region-count">${counts[id]||0}</span></button>`).join('');
}
function syncControls() {
 $('#search').value=filterState.q;$('#class-filter').value=filterState.class;$('#difficulty-filter').value=filterState.difficulty;$('#sort-filter').value=filterState.sort;$('#region-filter-mobile').value=filterState.region;
 $('#position-filters').innerHTML=[['','All'],...Object.entries(roleNames)].map(([id,name])=>`<button class="position-button ${filterState.position===id?'active':''}" data-position="${id}" aria-pressed="${filterState.position===id}">${id?icon(id):icon('all')}${name}</button>`).join('');
}
function renderGrid() {
 const rows=filtered();
 rows.sort((a,b)=>filterState.sort==='stories'?b.story_count-a.story_count||a.name.localeCompare(b.name):filterState.sort==='difficulty'?a.difficulty-b.difficulty||a.name.localeCompare(b.name):a.name.localeCompare(b.name));
 $('#result-count').textContent=`${rows.length} ${rows.length===1?'champion':'champions'}`;
 $('#collection-title').textContent=filterState.region?regions[filterState.region]||'Explore Runeterra':'Choose your legend';
 $('#collection-eyebrow').textContent=filterState.region?'STORIES SHAPED BY A PLACE':'THE COMPLETE COLLECTION';
 $('#active-filters').innerHTML=Object.entries(filterState).filter(([k,v])=>v&&k!=='sort').map(([k,v])=>`<button class="filter-chip" data-clear="${k}" aria-label="Remove ${esc(k)} filter">${esc(k==='position'?roleNames[v]:k==='difficulty'?difficultyNames[v]:k==='region'?regions[v]:v)}<span aria-hidden="true">×</span></button>`).join('');
 $('#champion-grid').innerHTML=rows.length?rows.map(c=>`<button class="champion-card" data-champion="${esc(c.id)}" aria-label="Explore ${esc(c.name)}, ${esc(c.title)}"><div class="card-image"><img src="${esc(c.portrait)}" alt="" loading="lazy" decoding="async" width="420" height="470"><span class="card-region">${esc(c.region_name)}</span><div class="card-positions">${c.positions.slice(0,2).map(p=>`<span title="${roleNames[p]}">${icon(p)}</span>`).join('')}</div></div><div class="card-info"><h3 class="card-name">${esc(c.name)}</h3><p class="card-title">${esc(c.title)}</p><div class="card-bottom"><span class="card-class">${esc(c.subclasses.join(' / ')||c.classes.join(' / '))}</span>${difficulty(c.difficulty)}</div></div></button>`).join(''):`<div class="empty-state"><h3>No legends found here.</h3><p>Try a different search or give your filters a little more room.</p><button class="button" data-reset>Clear all filters</button></div>`;
 $('#champion-grid').setAttribute('aria-busy','false');renderRegions();
}
function setFilter(key,value) {filterState[key]=value;updateUrl();syncControls();renderGrid();}
function titleCase(s){return String(s||'').replace(/-/g,' ').replace(/\b\w/g,c=>c.toUpperCase());}
function timelineMarkup(c) {
 const stories=c.lore.resources.filter(r=>r.type==='story');
 const dated=stories.filter(r=>safeDate(r.published_at)).sort((a,b)=>safeDate(a.published_at)-safeDate(b.published_at)||a.title.localeCompare(b.title));
 const undated=stories.filter(r=>!safeDate(r.published_at));
 const entries=[...dated,...undated];
 const videos=c.lore.resources.filter(r=>r.type==='video');
 return `<section class="detail-section story-section"><div class="section-heading"><h2 class="section-title">Follow the story</h2><span class="section-pill">${stories.length} ${stories.length===1?'linked story':'linked stories'}</span></div><p class="timeline-intro">Start with the biography, then explore the linked stories. ${dated.length?'The reading path below follows <strong>publication order</strong>, not a verified in-world timeline.':'No reliable story dates are available for this profile.'}</p><a class="flow-start" href="${esc(c.lore.biography_url)}" target="_blank" rel="noopener noreferrer">${icon('book')}<div><strong>Begin with ${esc(c.name)}’s biography</strong><p>The full origin and background, on League Universe.</p></div></a>${entries.length?`<div class="timeline">${entries.map(r=>{const d=safeDate(r.published_at);return `<article class="timeline-entry"><div class="timeline-date">${d?`${d.toLocaleDateString('en',{month:'short',timeZone:'UTC'})}<strong>${d.getUTCFullYear()}</strong>`:'Date<br>unlisted'}</div><a class="timeline-story" href="${esc(r.url)}" target="_blank" rel="noopener noreferrer"><span class="resource-label">LEAGUE UNIVERSE · SHORT STORY</span><h3>${esc(r.title)}</h3><p>${r.minutes_to_read?`${esc(r.minutes_to_read)} min read · `:''}${d?d.toLocaleDateString('en',{day:'numeric',month:'long',year:'numeric',timeZone:'UTC'}):'Publication date not provided'} · Read original</p></a></article>`;}).join('')}</div>`:'<p class="muted">This profile does not currently link any additional short stories. The biography is the starting point.</p>'}${videos.length?`<div class="media-resources">${videos.map(r=>external(r.url,`${icon('book')} ${esc(r.title)}`)).join('')}</div><p class="editorial-note">Other media linked by Universe. Shared continuity is not assumed.</p>`:''}<p class="editorial-note">Stories are catalogued from this champion’s Universe page. Publication dates do not establish event chronology; the list may not include every appearance.</p></section>`;
}
function relatedMarkup(c) {
 const related=c.lore.related_champions;
 return `<section class="detail-section related-section"><div class="section-heading"><h2 class="section-title">Connected legends</h2><span class="section-pill">${related.length} related ${related.length===1?'character':'characters'}</span></div><p class="editorial-note">Characters linked by League Universe. A connection does not necessarily mean ally or enemy.</p>${related.length?`<div class="related-grid">${related.map(r=>{const other=byId.get(r.id);return other?`<button class="related-card" data-champion="${esc(other.id)}"><img src="${esc(other.portrait)}" alt="" loading="lazy" width="51" height="58"><div><strong>${esc(other.name)}</strong><span>${esc(other.region_name)}</span></div></button>`:external(r.url,`<div><strong>${esc(r.name)}</strong><span>Universe character</span></div>`,'related-card');}).join('')}</div>`:'<p class="muted">No related characters listed in the retrieved profile.</p>'}</section>`;
}
function formatNumbers(arr) {return Array.isArray(arr)?[...new Set(arr)].map(n=>Number.isInteger(n)?n:Math.round(n*100)/100).join(' / '):'Not listed';}
function abilityMarkup(c) {
 return `<section class="detail-section ability-section"><div class="section-heading"><h2 class="section-title">The champion’s toolkit</h2><span class="section-pill">${esc(c.snapshot_version)}</span></div><div class="abilities">${c.gameplay.abilities.map(a=>`<article class="ability"><span class="ability-slot">${esc(a.slot)}</span><h3>${esc(a.name||'Unlisted')}</h3>${a.slot==='P'?'':`<p><span>Cooldown: ${esc(formatNumbers(a.cooldown_by_rank))}s</span><span>Cost: ${esc(formatNumbers(a.cost_by_rank))}</span></p>`}</article>`).join('')}</div><p class="editorial-note">Static values by rank, grouped when identical. Costs use this champion’s resource. Conditional effects and ability descriptions need ability-specific verification.</p></section>`;
}
function renderDetail(c) {
 const meta=byId.get(c.id), g=c.gameplay, l=c.lore, a=c.analysis, ratings=g.ratings;
 const ratingLabels={damage:'Damage',toughness:'Toughness',control:'Crowd control',mobility:'Mobility',utility:'Utility'};
 const facts=[['Region',esc(meta.region_name)],['Position',g.positions.client.map(p=>`${icon(p)} ${roleNames[p]}`).join(' · ')||'Unlisted'],['Class',esc(g.subclasses_wiki.join(' / ')||g.classes_data_dragon.join(' / '))],['Difficulty',`${difficultyNames[ratings.difficulty]||'Unknown'} ${difficulty(ratings.difficulty)}`],['Range & resource',esc([g.range_type,g.resource].filter(Boolean).join(' · '))]];
 const statLabels={hp:'Health',mp:'Resource pool',attackdamage:'Attack damage',armor:'Armor',spellblock:'Magic resistance',movespeed:'Move speed',attackrange:'Attack range',attackspeed:'Attack speed'};
 $('#detail-view').innerHTML=`<div class="detail-breadcrumb"><button data-close>All champions</button><span class="separator">/</span><a href="#" data-region-link="${esc(l.region||'')}">${esc(meta.region_name)}</a><span class="separator">/</span><span>${esc(c.name)}</span></div><section class="detail-hero" aria-labelledby="champion-title"><img src="${esc(meta.hero)}" alt="${esc(c.name)} official champion artwork" width="1500" height="900" fetchpriority="high"><div class="detail-hero-copy"><p class="eyebrow">${icon(l.region||'all')} ${esc(meta.region_name.toUpperCase())}</p><h1 id="champion-title" tabindex="-1">${esc(c.name)}</h1><p class="detail-subtitle">${esc(c.title)}</p><div class="hero-tags">${g.classes_data_dragon.map(t=>`<span>${esc(t)}</span>`).join('')}${l.species_as_listed.map(t=>`<span>${esc(t)}</span>`).join('')}</div></div></section><div class="detail-body"><div class="identity-strip">${facts.map(([label,v])=>`<div class="identity-item"><span class="meta-label">${label}</span><span class="identity-value">${v}</span></div>`).join('')}</div><div class="detail-layout"><div class="detail-main"><section class="lore-overview"><h2 class="section-title">Behind the legend</h2><p class="story-summary">${esc(l.summary||'A story summary has not yet been added.')}</p>${a.central_motivation?`<div class="motivation"><p class="eyebrow">WHAT DRIVES ${esc(c.name.toUpperCase())}</p><p>${esc(a.central_motivation)}</p></div>`:''}<div class="theme-tags">${a.candidate_themes.map(t=>`<span class="theme-tag">${esc(titleCase(t.theme))}</span>`).join('')}</div><p class="editorial-note">Motivation and themes are editorial interpretations of the short biography.</p><div class="source-actions">${external(l.biography_url,'Read full biography','button gold')}${external(`https://wiki.leagueoflegends.com/en-us/${encodeURIComponent(c.name.replace(/ /g,'_'))}`,'Gameplay wiki','button ghost')}</div></section>${abilityMarkup(c)}${timelineMarkup(c)}<section class="detail-section skin-section"><div class="section-heading"><h2 class="section-title">Their other lives</h2><a class="section-pill" href="skins.html?champion=${encodeURIComponent(c.id)}">Browse all skins</a></div><p class="editorial-note">Meet this champion in other worlds. Each skin keeps its own identity and lore.</p><div class="profile-skins" id="profile-skins" aria-busy="true"><p class="editorial-note">Opening the skin collection…</p></div></section>${relatedMarkup(c)}<section class="detail-section source-section"><h2 class="section-title">A living compendium</h2><p class="editorial-note">This overview summarizes the short Universe biography. Full biographies and linked stories are available at their sources; they have not yet been fully annotated. Gameplay is a versioned snapshot, not a live assessment of champion strength.</p><details class="data-details"><summary>Source notes & base statistics</summary><ul>${l.notes.map(n=>`<li>${esc(n)}</li>`).join('')}<li>Species: ${esc(l.species_as_listed.join(', ')||'Not explicitly listed by Universe.')}</li><li>Secondary position labels: ${esc(g.positions.external.map(p=>roleNames[p]).join(', ')||'Unlisted')}. These are not current role statistics.</li><li>${external(`${REPOSITORY}/blob/main/data/champions/${encodeURIComponent(c.id)}.json`,'View complete champion data')} · ${external(`${REPOSITORY}/blob/main/data/sources.json`,'Source history and fingerprints')}</li></ul><dl class="base-stats">${Object.entries(statLabels).filter(([k])=>g.base_stats_data_dragon[k]!=null).map(([k,label])=>`<div><dt>${label}</dt><dd>${esc(g.base_stats_data_dragon[k])}</dd></div>`).join('')}</dl></details></section></div><aside class="quick-panel" aria-label="Gameplay profile"><p class="eyebrow">AT A GLANCE</p><h2>How they play</h2>${Object.entries(ratingLabels).map(([key,label])=>`<div class="rating-row"><span>${label}</span><div class="rating-track" role="meter" aria-label="${label}" aria-valuenow="${ratings[key]??0}" aria-valuemin="0" aria-valuemax="3"><span style="width:${((ratings[key]??0)/3)*100}%"></span></div><strong>${ratings[key]??'–'}</strong></div>`).join('')}<div class="damage-style"><p><span>Basic attacks</span><span>Abilities</span></p><div class="rating-track" role="meter" aria-label="Ability orientation" aria-valuenow="${ratings.style??0}" aria-valuemin="0" aria-valuemax="100"><span style="width:${ratings.style??0}%"></span></div><p class="style-note">${ratings.style>=70?'Leans toward ability use.':ratings.style<=30?'Leans toward basic attacks.':'Combines attacks and abilities.'}</p></div><div class="theme-tags">${g.client_tags_wiki.map(t=>`<span class="theme-tag">${esc(t)}</span>`).join('')}</div><p class="style-note">Capability ratings: 0–3. Coarse gameplay labels from the Wiki, not a performance ranking.</p></aside></div></div>`;
 loadProfileSkins(c.id);
 document.title=`${c.name} — Runeterra Atlas`;
 $('#champion-title').focus({preventScroll:true});
}
async function loadProfileSkins(id) {
 try {
  const r=await fetch(`data/skins/${encodeURIComponent(id)}.json`);if(!r.ok)throw new Error('No skin data');const data=await r.json();if(selected!==id)return;
  const skins=data.skins.filter(s=>!s.is_base&&s.matching.label_eligible).slice(0,6);const target=$('#profile-skins');if(!target)return;
  target.innerHTML=skins.length?skins.map(s=>`<a class="skin-card" href="skins.html?champion=${encodeURIComponent(id)}#${encodeURIComponent(s.id)}"><div class="skin-card-art"><img src="${esc(s.artwork.tile||byId.get(id).portrait)}" alt="" loading="lazy" width="420" height="300"></div><div class="skin-card-copy"><h3>${esc(s.name)}</h3><p>${esc(s.wiki_sets.join(' · ')||s.rarity||'Alternate appearance')}</p></div></a>`).join(''):'<p class="editorial-note">No alternate skins are listed in this snapshot.</p>';target.setAttribute('aria-busy','false');
 }catch(e){const target=$('#profile-skins');if(target&&selected===id){target.innerHTML='<p class="editorial-note">Open the skin gallery to explore alternate appearances.</p>';target.setAttribute('aria-busy','false');}}
}
async function route() {
 const generation=++renderGeneration;
 if (!selected) {
  $('#browse-view').hidden=false;$('#detail-view').hidden=true;document.title='Runeterra Atlas — Champion Compendium';syncControls();renderGrid();return;
 }
 $('#browse-view').hidden=true;$('#detail-view').hidden=false;
 if(!byId.has(selected)) {$('#detail-view').innerHTML='<div class="state-error"><h1>That legend isn’t in the atlas.</h1><p>The champion link may be incomplete.</p><button class="button" data-close>Browse all champions</button></div>';return;}
 $('#detail-view').innerHTML='<div class="detail-loading" role="status">Opening this champion’s story…</div>';
 try {
  let c=detailCache.get(selected);
  if(!c) {const response=await fetch(`data/champions/${encodeURIComponent(selected)}.json`);if(!response.ok)throw new Error('Champion data unavailable');c=await response.json();detailCache.set(c.id,c);}
  if(generation!==renderGeneration)return;
  renderDetail(c);
 } catch(e) {
  if(generation!==renderGeneration)return;
  $('#detail-view').innerHTML=`<div class="state-error"><h1>This page couldn’t be loaded.</h1><p>Please try again or return to the gallery.</p><button class="button" data-retry>Try again</button> <button class="button ghost" data-close>All champions</button></div>`;
 }
}
function openChampion(id) {if(!selected)browseScroll=window.scrollY;selected=id;updateUrl(true);window.scrollTo({top:0,behavior:'instant'});route();}
function closeChampion() {const closingId=selected;selected=null;updateUrl(true);route();requestAnimationFrame(()=>{window.scrollTo({top:browseScroll,behavior:'instant'});const button=$(`[data-champion="${CSS.escape(closingId||'')}"]`);if(button)button.focus({preventScroll:true});});}
function resetFilters() {filterState={q:'',position:'',class:'',difficulty:'',region:'',sort:'name'};updateUrl();syncControls();renderGrid();}
document.addEventListener('click', e=>{
 const champ=e.target.closest('[data-champion]');if(champ){openChampion(champ.dataset.champion);return;}
 if(e.target.closest('[data-close]')){closeChampion();return;}
 if(e.target.closest('[data-retry]')){route();return;}
 const region=e.target.closest('[data-region]');if(region){setFilter('region',region.dataset.region);return;}
 const position=e.target.closest('[data-position]');if(position){setFilter('position',position.dataset.position);return;}
 const clear=e.target.closest('[data-clear]');if(clear){setFilter(clear.dataset.clear,'');return;}
 if(e.target.closest('[data-reset]')){resetFilters();return;}
 const regionLink=e.target.closest('[data-region-link]');if(regionLink){e.preventDefault();selected=null;filterState.region=regionLink.dataset.regionLink;updateUrl(true);route();window.scrollTo({top:0,behavior:'instant'});}
});
let searchTimer;
$('#search').addEventListener('input',e=>{clearTimeout(searchTimer);const value=e.target.value;searchTimer=setTimeout(()=>{filterState.q=value;updateUrl();renderGrid();},100);});
for(const [selector,key] of [['#class-filter','class'],['#difficulty-filter','difficulty'],['#sort-filter','sort'],['#region-filter-mobile','region']])$(selector).addEventListener('change',e=>setFilter(key,e.target.value));
$('#regions-nav').addEventListener('click',()=>{if(selected){selected=null;updateUrl(true);route();}const target=window.innerWidth<=900?$('#region-filter-mobile'):$('#region-list');target.scrollIntoView({behavior:'smooth',block:'center'});if(target.tagName==='SELECT')target.focus();else $('button',target)?.focus();});
$('#champion-nav').addEventListener('click',e=>{e.preventDefault();if(selected)closeChampion();else window.scrollTo({top:0,behavior:'smooth'});});
$('.footer-brand').addEventListener('click',e=>{e.preventDefault();if(selected)closeChampion();window.scrollTo({top:0,behavior:'smooth'});});
$('.brand').addEventListener('click',e=>{e.preventDefault();selected=null;resetFilters();updateUrl(true);route();window.scrollTo({top:0,behavior:'smooth'});});
window.addEventListener('popstate',()=>{readState();route();if(!selected)requestAnimationFrame(()=>window.scrollTo({top:history.state?.browseScroll||browseScroll,behavior:'instant'}));else window.scrollTo({top:0,behavior:'instant'});});
document.addEventListener('keydown',e=>{if(e.key==='/'&&!['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)&&!selected){e.preventDefault();$('#search').focus();}if(e.key==='Escape'&&selected)closeChampion();});
document.addEventListener('error',e=>{if(e.target.tagName==='IMG')e.target.classList.add('error-art');},true);
async function init(){
 try {
  const response=await fetch('data/catalog.json');if(!response.ok)throw new Error('Catalog unavailable');const data=await response.json();catalog=data.champions;regions=data.regions;coverage=data.coverage;byId=new Map(catalog.map(c=>[c.id,c]));
  $('#total-champions').textContent=catalog.length;$('#total-regions').textContent=Object.keys(regions).length;$('#total-stories').textContent=coverage.unique_story_urls;
  const classes=[...new Set(catalog.flatMap(c=>[...c.classes,...c.subclasses]))].sort();$('#class-filter').innerHTML='<option value="">All classes</option>'+classes.map(c=>`<option value="${esc(c)}">${esc(c)}</option>`).join('');
  $('#region-filter-mobile').innerHTML='<option value="">All Runeterra</option>'+Object.entries(regions).sort((a,b)=>a[1].localeCompare(b[1])).map(([id,name])=>`<option value="${esc(id)}">${esc(name)}</option>`).join('');
  readState();await route();
 }catch(e){$('#champion-grid').innerHTML='<div class="empty-state"><h3>The atlas couldn’t be opened.</h3><p>Please refresh the page to try loading the champion catalog again.</p><button class="button" data-reload>Reload atlas</button></div>';$('#result-count').textContent='Catalog unavailable';$('#champion-grid').setAttribute('aria-busy','false');$('[data-reload]').addEventListener('click',()=>location.reload());}
}
init();

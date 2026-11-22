# Attribution and reuse

## Riot Games

Champion names, fictional settings, lore, game content, and associated intellectual property belong to Riot Games and their respective owners.

Sources:

- League Universe: https://universe.leagueoflegends.com/
- Universe public content payloads: per-champion URLs in `data/sources.json`.
- Data Dragon: https://developer.riotgames.com/docs/lol#data-dragon

The visual browser displays official Riot champion splash artwork. The optional art build fetches it from Data Dragon, crops/resizes it, and converts it to WebP for display; these changes do not confer ownership or relicense the artwork. Artwork remains Riot Games content.

Lore entries here are concise original paraphrases and interpretations, with links to original full prose. This project does not redistribute the complete stories or artwork and does not claim ownership of Riot's intellectual property. No code or data license here grants rights to Riot's underlying IP.

## League of Legends Wiki contributors

Gameplay taxonomy, client attributes and positions, ratings, and related Wiki-derived fields are adapted from **Module:ChampionData/data**, by the League of Legends Wiki contributors.

- Source: https://wiki.leagueoflegends.com/en-us/Module:ChampionData/data
- Authors and edits: https://wiki.leagueoflegends.com/en-us/Module:ChampionData/data?action=history
- Initial revision: **4095247**, timestamp **2026-11-17T22:50:10Z**; the manifest is authoritative after subsequent refreshes.
- Initial revision permalink: https://wiki.leagueoflegends.com/en-us/index.php?title=Module:ChampionData/data&oldid=4095247
- License reported by the site's rightsinfo API: **Creative Commons Attribution-ShareAlike 3.0**: https://creativecommons.org/licenses/by-sa/3.0/

Changes: parsed the data-only Lua table, selected fields, joined to Riot IDs, renamed and normalized position keys, computed normalized rating features, and embedded attributed results in JSON/CSV/SQL-compatible records. Wiki-derived adaptations are distributed under CC BY-SA 3.0. This applies to adaptations of the licensed material; it does not relicense Riot's underlying IP.

## Original project work

Original scripts are provided under the MIT license in `LICENSE`. Original editorial additions are shared under CC BY-SA 3.0 to accompany the attributed database, subject to underlying third-party rights. Source data is not covered by the MIT code license.

This project is not endorsed by Riot Games. See the disclaimer in README.md.

## Skin catalog additions

Cosmetic names, artwork, biography source content, and client metadata remain Riot Games material. CommunityDragon distributes unpacked client data; this catalog uses its pinned **16.23** client payloads. Individual champion payloads establish inventory membership; bulk `skins.json`, `skinlines.json`, and `universes.json` supply IDs, appearance assets, chromas, and thematic relationships. Exact URLs and hashes are in `data/skin_sources.json`. CommunityDragon documentation: https://www.communitydragon.org/docs/assets

Additional Wiki-derived fields come from `Module:SkinData/data` and `Module:SkinData/universes`, by the League of Legends Wiki contributors, under the site's CC BY-SA 3.0 terms. The source manifest includes the exact revisions, permalinks, and contributor-history URLs. Changes include parsing data-only Lua, selecting metadata, combining client and Wiki sources, distinguishing cosmetics from chromas and quest tiers, and resolving memberships. These adaptations remain CC BY-SA 3.0, subject to Riot's underlying rights.

The catalog redistributes source references and hashes rather than the complete original skin biographies. Fifteen initial summaries are original paraphrases with source review pins. The local biography resolver retrieves originals for research on demand; its cache is excluded from git and the hosted UI.

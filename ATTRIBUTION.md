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

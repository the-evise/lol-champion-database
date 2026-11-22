# League of Legends champion research database

A source-linked database for two future products: **character/personality matching** and **playstyle recommendations by position**. The quiz and its scoring are deliberately left open.

The initial snapshot contains **all 173 playable champions in Riot Data Dragon 16.23.1**, retrieved on **22 November 2026**. Universe and Wiki information is joined by stable Riot champion ID, with explicit handling for display names and non-playable characters.

## Visual browser

[Open Runeterra Atlas](https://runeterra-atlas.h-zarepour01.chatgpt.site) to browse champion artwork, combine region/position/class/difficulty filters, and open unified champion profiles. Profiles include a biography overview, gameplay ratings, ability data, connected characters, and a publication-ordered story reading path. Publication order is explicitly separate from in-world chronology.

The browser uses plain HTML/CSS/JavaScript, a 62 KB catalog, lazy-loaded WebP art, and individual champion records loaded on demand. Its source is in `web/`. To build locally:

```bash
python scripts/build_web.py
python -m http.server 8000 --directory dist
```

For locally optimized artwork, install Pillow and run `python scripts/build_web.py --download-art`. Without that optional step, the browser uses official Riot CDN artwork. No JavaScript dependencies are required.

## Skins and alternate identities

The database also includes **2,026 non-base cosmetic entries** for all 173 champions, with **1,971 released skin labels** suitable for a future result library, **226 skin lines**, **131 world/setting groups**, and **7,205 chromas tracked separately**. Browse [Alternate Lives](https://runeterra-atlas.h-zarepour01.chatgpt.site/skins.html), read [the skin data guide](docs/SKINS.md), or open the [coverage report](data/skin_coverage.json).

Every skin now has **exactly two simple aesthetic vibe tags**, such as **mysterious + elegant** for Coven Morgana and **bold + rebellious** for Pentakill Karthus. They are theme impressions, separate from lore and personality claims, and appear in the browser, JSON, CSV, and SQLite exports. The skin search accepts vibe words. Source biographies remain separate references; alternate skins do not automatically inherit original-world personality.

## Start here

- [Browse every champion](docs/INDEX.md)
- [All champion records: JSON](data/champions.json)
- [Spreadsheet-friendly CSV](data/champions.csv)
- [Coverage report](data/coverage.json)
- [Source manifest and retrieval hashes](data/sources.json)
- [Data dictionary](docs/DATA_DICTIONARY.md)
- [Research boundaries and next research passes](docs/RESEARCH.md)

Example dossiers: [Ahri](docs/champions/Ahri.md), [Jhin](docs/champions/Jhin.md), [Braum](docs/champions/Braum.md), [Locke](docs/champions/Locke.md).

## What is included

| Layer | Coverage | Contents |
|---|---:|---|
| Champion roster | 173/173 | Stable ID, name, title, snapshot version |
| Universe short-biography summaries | 173/173 | Original concise paraphrase, region, species when explicitly listed |
| Original full-biography access | 173/173 | Links to Riot's original biographies; availability and source fingerprint |
| Linked story catalog | 260 links / 200 unique stories | Titles, links, publication metadata when present |
| Related champions | All retrieved curated links | Related-page links, without invented ally/enemy labels |
| Gameplay | 173/173 | Classes, subclasses, positions, resource, range type, ratings, base statistics, ability names and static numeric arrays |
| Exploratory character analysis | 173/173 | Motivation and three candidate themes, labeled as interpretations |
| Source tracking | Every record | URLs, retrieval timestamps, hashes, Wiki revision and license |

**This is a complete roster-level foundation, not a completed deep reading of every story.** Summaries currently use the short Universe biographies. Full biographies and associated stories are linked and catalogued; their deeper events, relationships, and narrative developments have not been editorially analyzed. `data/coverage.json` exposes this explicitly. Full original prose and artwork are not redistributed in this repository.

## Use the data

No API key or Python dependencies are required. Python 3.10+ is recommended.

```bash
# Search and filter the committed JSON.
python scripts/explore.py --champion Ahri --json
python scripts/explore.py --theme protection
python scripts/explore.py --role support --max-difficulty 1
python scripts/explore.py --search betrayal

# Build a local SQL database from committed records; no network needed.
python scripts/build.py --sqlite-only
python scripts/validate.py
```

`build/champions.sqlite` includes relational tables for champions, positions, themes, related links, resources, abilities, and sources. The full JSON record is also retained per champion. The generated database is ignored by git; committed JSON is the portable source of truth.

```python
import sqlite3
con = sqlite3.connect('build/champions.sqlite')
print(con.execute('''
    SELECT name, difficulty, control, utility
    FROM role_candidates
    WHERE role = 'support' AND difficulty = 1
    ORDER BY name
''').fetchall())
```

```javascript
// For a Node.js application or analysis script:
import { readFile } from 'node:fs/promises';
const champions = JSON.parse(await readFile('data/champions.json', 'utf8'));
const junglers = champions.filter(c => c.gameplay.positions.client.includes('jungle'));
```

The position keys are `top`, `jungle`, `mid`, `bottom`, and `support`. `bottom` is a lane position, not a synonym for the marksman class. There are at least three candidates for each position, but **no recommendation ranking or validated personality score exists yet**.

## Refresh sources

```bash
python scripts/refresh_sources.py --version 16.23.1
python scripts/build.py
python scripts/validate.py
```

Omit `--version` to discover the latest published Data Dragon version. Downloaded source payloads stay in ignored `.cache/`. The pipeline uses four workers, bounded retries, and a non-executing parser for Wiki Lua data.

Refreshing does not rewrite authored summaries. If a short biography changes, the summary loses its reviewed status and validation fails until it is reviewed. New champions appear with explicit editorial gaps. After reviewing a revised short biography, update its editorial entry and deliberately replace its hash in `data/editorial_source_hashes.json` with the new hash from `data/sources.json`; do not reset hashes without review.

Source data can disagree or lag a patch. API spell arrays are not authoritative simulations of every conditional interaction. Wiki client positions and externally sourced positions are retained separately and are not live role statistics. Adaptive damage type is not a measured damage breakdown. See [the data dictionary](docs/DATA_DICTIONARY.md).

## Attribution

Sources are Riot's **League Universe**, Riot's **Data Dragon**, and the **League of Legends Wiki**. Wiki-derived data is attributed with revision/history links and its reported **CC BY-SA 3.0** license. Source IP remains with its respective owners. See [ATTRIBUTION.md](ATTRIBUTION.md).

League of Legends Champion Research Database is not endorsed by Riot Games and does not reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games and all associated properties are trademarks or registered trademarks of Riot Games, Inc.

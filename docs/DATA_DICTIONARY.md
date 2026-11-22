# Data dictionary

Each `data/champions/<DataDragonID>.json` is identical to its entry in the aggregate array. Names can change; use `riot_id` for joins and `id` for paths.

| Field | Meaning and source |
|---|---|
| `id` | Riot Data Dragon API key, e.g. `MonkeyKing` for Wukong |
| `riot_id` | Numeric Riot champion ID |
| `snapshot_version` | Data Dragon version, not an assertion that every other source matches that patch |
| `lore.summary` | Original paraphrase of the retrieved Universe short biography |
| `lore.region` | Universe's associated faction slug; `unaffiliated` is a supplied label, `null` is missing |
| `lore.species_as_listed` | Explicit Universe race entries; an empty list means unlisted, not human |
| `lore.related_champions` | Universe's curated related links. These do not establish friendship, kinship, or rivalry |
| `lore.resources` | Linked stories and videos from the champion page, including metadata when available |
| `lore.notes` | Evidence scope, continuity limits, and known research questions |
| `gameplay.classes_data_dragon` | Broad labels such as Mage, Fighter, or Support |
| `gameplay.subclasses_wiki` | Wiki taxonomy such as Burst, Warden, or Juggernaut |
| `gameplay.client_tags_wiki` | Client attributes recorded by the Wiki, e.g. Mobile or Crowd Control |
| `gameplay.positions.client` | Client-assigned positions recorded by the Wiki |
| `gameplay.positions.external` | Wiki's secondary external position labels; method and recency are not assumed |
| `gameplay.range_type` | Wiki melee/ranged label; some transforming champions have additional contextual behavior |
| `gameplay.resource` | Data Dragon resource label |
| `gameplay.ratings` | Coarse Wiki-recorded ratings, not measurements of current win rate or mastery ceiling |
| `gameplay.adaptive_damage_type_wiki` | Adaptive stat preference. Do not interpret as the champion's actual damage composition |
| `gameplay.base_stats_data_dragon` | Base values and per-level parameters as supplied by the static API |
| `gameplay.abilities` | Passive and Q/W/E/R names, plus spell cooldown/cost/range arrays where supplied |
| `analysis.central_motivation` | Editorial interpretation supported by the source-linked summary |
| `analysis.candidate_themes` | Tentative thematic labels with paraphrased evidence and source ID; not psychometric facts |
| `analysis.personality_scores` | `null`; no invented personality vector |
| `analysis.gameplay_features` | Deterministic normalization of source ratings, with no extra gameplay judgments |
| `coverage` | Source availability and separate editorial-review flags |
| `provenance` | Source IDs and explicit interpretation exceptions |

## Rating scales

| Rating | Raw range | Normalized feature |
|---|---|---|
| Difficulty | 1–3 | `(raw - 1) / 2` |
| Damage, toughness, control, mobility, utility | 0–3 | `raw / 3` |
| Style | 0–100 | `raw / 100` |

A capability value of zero is retained as zero. Missing values remain `null`. Style describes an attack-versus-ability orientation; it is not a literal measured percentage of damage. Do not average difficulty with capabilities as if high difficulty were a universal benefit.

Wiki source documentation: [champion ratings](https://wiki.leagueoflegends.com/en-us/List_of_champions/Ratings).

`last_changed_patch_wiki` is the Wiki entry's recorded change marker; it does not certify that every field was checked against that patch. Spell range arrays can contain sentinel or special-case values, and costs may refer to different resources. Exact combat simulation needs ability-specific verification.

## Sources and continuity

`data/sources.json` records one source per champion per source system, plus the roster, Universe index, and Wiki bulk revision. The Wiki source includes the license returned by its own siteinfo API, revision timestamp, revision permalink, and author-history link.

A source fingerprint detects changed input; it does not prove that the source is narratively current. Universe content is recorded as retrieved. Cinematics, older biographies, and other media are not automatically assumed to share one reconciled continuity.

Related entries can point to non-playable characters. Yuumi's link to Norra has a null playable champion ID; the name and source URL are retained. `explore-champions` discovery suggestions are intentionally excluded from relationships. Alternate gameplay forms are excluded from the playable champion count.

## Editing

Edit summaries and candidate themes in `data/editorial.tsv`; do not hand-edit generated records. This TSV is the editorial input, not an evidence-free scoring model. Run `build.py` and `validate.py` after changes. Source review hashes are intentionally separate from source refreshes.

# Skins and alternate identities

[Browse the skin gallery](https://runeterra-atlas.h-zarepour01.chatgpt.site/skins.html).

The PC snapshot is dated **22 November 2026**, using client patch **16.23** and the recorded Wiki revisions. It covers all **173 champions**.

| Catalog layer | Count | Meaning |
|---|---:|---|
| Base appearances | 173 | Original champion identities |
| Non-base catalog entries | 2,026 | Released skins, quest tiers, historical archives, announced/canceled/removed records |
| Released skin result labels | 1,971 | Current champion inventory entries and explicit quest tiers, excluding known unreleased/removed items |
| Chromas | 7,205 | Separate color choices associated with a parent skin |
| Skin lines with members | 226 | Source-provided thematic collections |
| Worlds/settings with members | 131 | Client and Wiki thematic groupings; not every group is a single story continuity |
| Non-base biographies available | 1,873 | Original prose available through recorded source locators |
| Biographies summarized and initially annotated | 15 | Coven and Pentakill examples; thematic interpretations remain unvalidated |

The full catalog has **2,199 entries including the 173 base appearances**. Availability labels and prices are source snapshots, not live store quotes. Legacy or limited availability does not prevent a character from being a valid quiz identity.

## Files

- `data/skins.json`: complete aggregate records.
- `data/skins/<ChampionID>.json`: the same records grouped by champion.
- `data/skins.csv`: spreadsheet-friendly catalog.
- `data/skinlines.json`: line IDs, names, membership, and source description locators.
- `data/skin_universes.json`: worlds/settings and memberships.
- `data/skin_sources.json`: source URLs, hashes, timestamps, Wiki revisions, and licenses.
- `data/skin_coverage.json`: coverage, exclusions, reconciliation, and unresolved references.
- `data/skin_editorial.json`: original summaries and exploratory themes.
- `data/skin_editorial_hashes.json`: review pins for those summaries.
- `schema/skin.schema.json`: record contract.

Each skin has its own stable `matching.result_key`, exact display label, parent champion, line/world memberships, image URLs, rarity, release metadata, variant relationships, chromas, and evidence scope. Base champion records remain separate.

## Identities and variants

- `skin:25026` is **Coven Morgana**, in the **Coven** line and **Eclipse** world.
- `skin:30004` is **Pentakill Karthus**, in **Pentakill** and **Riot Records**.
- `skin:103086` is **Immortalized Legend Ahri**, an explicit tier of `skin:103085`.
- Seraphine's K/DA ALL OUT forms are retained as explicit quest tiers.
- Morgana's Ruby Coven chroma belongs to Coven Morgana; it is not another independent character story.

IDs are read from source records. Eight historical/canceled records without a Riot skin ID retain a `wiki:<champion>:<name>` key and a null Riot ID. No numeric ID is invented.

Forty-one Classic archive entries occur in the bulk client catalog but not the current individual champion inventories. Ownership is checked using the catalog's classic namespace and exact champion-name agreement. They are preserved with `kind: historical` and excluded from default released-result candidates.

Two Wiki variant references point to IDs absent from this snapshot. They remain in `variant_reference_wiki` with `resolution: not_in_snapshot`; a canonical `variant_of` relationship is not fabricated. See the coverage report.

Data Dragon includes many chromas in its `skins` arrays. Every one of the existing snapshot's **9,287 appearance entries** is resolved as a skin or a chroma. These are not 9,287 independent personalities.

## Biography access

The repository does not duplicate the complete source prose. Every available biography has a source reference, JSON pointer or Wiki locator, fingerprint, and word count. All **2,046 available biographies including bases** were resolved against their stored fingerprint during this build, with no mismatches.

Resolve a biography directly for local research:

```bash
python scripts/skin_lore.py --skin "Coven Morgana"
python scripts/skin_lore.py --skin skin:30004
python scripts/skin_lore.py --all --output .cache/skin-lore.json
```

The helper reuses local source caches and retrieves missing sources when necessary. Changed biography hashes are reported. Its full-prose output is a local research cache and should not be committed or bundled into the public browser. The browser links to the original source instead.

Only 15 skin biographies have editorial summaries in this initial pass. The remaining records explicitly say they are not annotated. Original-world personality is not automatically assigned to an alternate-world character.

## SQL

```bash
python scripts/build.py --sqlite-only
```

The generated database includes `skins`, `skin_lines`, `skin_universes`, `skin_line_memberships`, `skin_universe_memberships`, `skin_chromas`, and `result_identity_catalog`.

```sql
SELECT r.result_key, r.result_label, r.champion_name
FROM result_identity_catalog r
JOIN skin_line_memberships m ON m.skin_id = r.result_key
JOIN skin_lines l ON l.id = m.line_id
WHERE l.name = 'Coven';
```

`result_identity_catalog` gives valid labels, not a finished personality ranking. Skin-aware results can use champion similarity plus separately evidenced skin-character or world preferences. Aesthetic preference is distinct from moral character. The larger result library increases variety; identical answers may still legitimately lead to the same result.

## Refresh and review

```bash
# Keep the champion snapshot and client skin patch aligned.
python scripts/refresh_skins.py --patch 16.23
python scripts/build_skins.py --as-of 2026-11-22
python scripts/build.py --sqlite-only
python scripts/validate_skins.py
python scripts/build_web.py
```

After a source change, reviewed summaries lose their reviewed status if their biography fingerprint changes. Update the editorial text and review hash only after checking the revised biography. Refreshing the metadata does not produce new personality scores.

The scope is **PC League of Legends**, including its retained archival records. Wild Rift-exclusive and other game-specific cosmetics are not claimed as covered.

## Champion catalogs

| Champion | Non-base entries | Released labels |
|---|---:|---:|
| [Aatrox](../data/skins/Aatrox.json) | 12 | 12 |
| [Ahri](../data/skins/Ahri.json) | 23 | 22 |
| [Akali](../data/skins/Akali.json) | 25 | 23 |
| [Akshan](../data/skins/Akshan.json) | 4 | 4 |
| [Alistar](../data/skins/Alistar.json) | 18 | 16 |
| [Ambessa](../data/skins/Ambessa.json) | 2 | 2 |
| [Amumu](../data/skins/Amumu.json) | 15 | 14 |
| [Anivia](../data/skins/Anivia.json) | 13 | 13 |
| [Annie](../data/skins/Annie.json) | 20 | 19 |
| [Aphelios](../data/skins/Aphelios.json) | 7 | 7 |
| [Ashe](../data/skins/Ashe.json) | 20 | 20 |
| [Aurelion Sol](../data/skins/AurelionSol.json) | 6 | 6 |
| [Aurora](../data/skins/Aurora.json) | 3 | 3 |
| [Azir](../data/skins/Azir.json) | 7 | 7 |
| [Bard](../data/skins/Bard.json) | 8 | 8 |
| [Bel'Veth](../data/skins/Belveth.json) | 4 | 4 |
| [Blitzcrank](../data/skins/Blitzcrank.json) | 19 | 18 |
| [Brand](../data/skins/Brand.json) | 13 | 13 |
| [Braum](../data/skins/Braum.json) | 9 | 9 |
| [Briar](../data/skins/Briar.json) | 3 | 3 |
| [Caitlyn](../data/skins/Caitlyn.json) | 20 | 20 |
| [Camille](../data/skins/Camille.json) | 8 | 8 |
| [Cassiopeia](../data/skins/Cassiopeia.json) | 9 | 9 |
| [Cho'Gath](../data/skins/Chogath.json) | 11 | 11 |
| [Corki](../data/skins/Corki.json) | 11 | 11 |
| [Darius](../data/skins/Darius.json) | 15 | 15 |
| [Diana](../data/skins/Diana.json) | 16 | 16 |
| [Dr. Mundo](../data/skins/DrMundo.json) | 12 | 11 |
| [Draven](../data/skins/Draven.json) | 14 | 14 |
| [Ekko](../data/skins/Ekko.json) | 13 | 13 |
| [Elise](../data/skins/Elise.json) | 9 | 9 |
| [Evelynn](../data/skins/Evelynn.json) | 18 | 18 |
| [Ezreal](../data/skins/Ezreal.json) | 23 | 22 |
| [Fiddlesticks](../data/skins/Fiddlesticks.json) | 13 | 12 |
| [Fiora](../data/skins/Fiora.json) | 17 | 16 |
| [Fizz](../data/skins/Fizz.json) | 13 | 13 |
| [Galio](../data/skins/Galio.json) | 12 | 11 |
| [Gangplank](../data/skins/Gangplank.json) | 13 | 12 |
| [Garen](../data/skins/Garen.json) | 18 | 16 |
| [Gnar](../data/skins/Gnar.json) | 10 | 10 |
| [Gragas](../data/skins/Gragas.json) | 14 | 14 |
| [Graves](../data/skins/Graves.json) | 13 | 13 |
| [Gwen](../data/skins/Gwen.json) | 6 | 6 |
| [Hecarim](../data/skins/Hecarim.json) | 12 | 12 |
| [Heimerdinger](../data/skins/Heimerdinger.json) | 10 | 9 |
| [Hwei](../data/skins/Hwei.json) | 3 | 3 |
| [Illaoi](../data/skins/Illaoi.json) | 6 | 6 |
| [Irelia](../data/skins/Irelia.json) | 17 | 16 |
| [Ivern](../data/skins/Ivern.json) | 6 | 6 |
| [Janna](../data/skins/Janna.json) | 17 | 17 |
| [Jarvan IV](../data/skins/JarvanIV.json) | 15 | 15 |
| [Jax](../data/skins/Jax.json) | 18 | 17 |
| [Jayce](../data/skins/Jayce.json) | 12 | 12 |
| [Jhin](../data/skins/Jhin.json) | 13 | 13 |
| [Jinx](../data/skins/Jinx.json) | 15 | 15 |
| [K'Sante](../data/skins/KSante.json) | 4 | 4 |
| [Kai'Sa](../data/skins/Kaisa.json) | 16 | 16 |
| [Kalista](../data/skins/Kalista.json) | 6 | 6 |
| [Karma](../data/skins/Karma.json) | 17 | 15 |
| [Karthus](../data/skins/Karthus.json) | 11 | 10 |
| [Kassadin](../data/skins/Kassadin.json) | 10 | 9 |
| [Katarina](../data/skins/Katarina.json) | 20 | 19 |
| [Kayle](../data/skins/Kayle.json) | 20 | 18 |
| [Kayn](../data/skins/Kayn.json) | 8 | 8 |
| [Kennen](../data/skins/Kennen.json) | 10 | 10 |
| [Kha'Zix](../data/skins/Khazix.json) | 8 | 8 |
| [Kindred](../data/skins/Kindred.json) | 9 | 9 |
| [Kled](../data/skins/Kled.json) | 4 | 4 |
| [Kog'Maw](../data/skins/KogMaw.json) | 16 | 15 |
| [LeBlanc](../data/skins/Leblanc.json) | 14 | 14 |
| [Lee Sin](../data/skins/LeeSin.json) | 20 | 19 |
| [Leona](../data/skins/Leona.json) | 18 | 18 |
| [Lillia](../data/skins/Lillia.json) | 6 | 6 |
| [Lissandra](../data/skins/Lissandra.json) | 9 | 9 |
| [Locke](../data/skins/Locke.json) | 1 | 1 |
| [Lucian](../data/skins/Lucian.json) | 14 | 14 |
| [Lulu](../data/skins/Lulu.json) | 14 | 14 |
| [Lux](../data/skins/Lux.json) | 22 | 22 |
| [Malphite](../data/skins/Malphite.json) | 14 | 14 |
| [Malzahar](../data/skins/Malzahar.json) | 13 | 13 |
| [Maokai](../data/skins/Maokai.json) | 11 | 11 |
| [Master Yi](../data/skins/MasterYi.json) | 19 | 18 |
| [Mel](../data/skins/Mel.json) | 3 | 3 |
| [Milio](../data/skins/Milio.json) | 3 | 3 |
| [Miss Fortune](../data/skins/MissFortune.json) | 24 | 23 |
| [Mordekaiser](../data/skins/Mordekaiser.json) | 14 | 13 |
| [Morgana](../data/skins/Morgana.json) | 18 | 17 |
| [Naafiri](../data/skins/Naafiri.json) | 4 | 4 |
| [Nami](../data/skins/Nami.json) | 15 | 14 |
| [Nasus](../data/skins/Nasus.json) | 14 | 13 |
| [Nautilus](../data/skins/Nautilus.json) | 11 | 11 |
| [Neeko](../data/skins/Neeko.json) | 10 | 10 |
| [Nidalee](../data/skins/Nidalee.json) | 17 | 16 |
| [Nilah](../data/skins/Nilah.json) | 3 | 3 |
| [Nocturne](../data/skins/Nocturne.json) | 10 | 10 |
| [Nunu & Willump](../data/skins/Nunu.json) | 13 | 12 |
| [Olaf](../data/skins/Olaf.json) | 11 | 11 |
| [Orianna](../data/skins/Orianna.json) | 13 | 13 |
| [Ornn](../data/skins/Ornn.json) | 5 | 5 |
| [Pantheon](../data/skins/Pantheon.json) | 14 | 13 |
| [Poppy](../data/skins/Poppy.json) | 14 | 13 |
| [Pyke](../data/skins/Pyke.json) | 12 | 12 |
| [Qiyana](../data/skins/Qiyana.json) | 10 | 10 |
| [Quinn](../data/skins/Quinn.json) | 7 | 7 |
| [Rakan](../data/skins/Rakan.json) | 12 | 12 |
| [Rammus](../data/skins/Rammus.json) | 12 | 12 |
| [Rek'Sai](../data/skins/RekSai.json) | 5 | 5 |
| [Rell](../data/skins/Rell.json) | 4 | 4 |
| [Renata Glasc](../data/skins/Renata.json) | 5 | 5 |
| [Renekton](../data/skins/Renekton.json) | 15 | 15 |
| [Rengar](../data/skins/Rengar.json) | 9 | 9 |
| [Riven](../data/skins/Riven.json) | 18 | 17 |
| [Rumble](../data/skins/Rumble.json) | 6 | 6 |
| [Ryze](../data/skins/Ryze.json) | 15 | 14 |
| [Samira](../data/skins/Samira.json) | 6 | 6 |
| [Sejuani](../data/skins/Sejuani.json) | 13 | 13 |
| [Senna](../data/skins/Senna.json) | 12 | 12 |
| [Seraphine](../data/skins/Seraphine.json) | 13 | 13 |
| [Sett](../data/skins/Sett.json) | 11 | 11 |
| [Shaco](../data/skins/Shaco.json) | 16 | 16 |
| [Shen](../data/skins/Shen.json) | 14 | 13 |
| [Shyvana](../data/skins/Shyvana.json) | 9 | 8 |
| [Singed](../data/skins/Singed.json) | 12 | 12 |
| [Sion](../data/skins/Sion.json) | 12 | 11 |
| [Sivir](../data/skins/Sivir.json) | 20 | 19 |
| [Skarner](../data/skins/Skarner.json) | 7 | 6 |
| [Smolder](../data/skins/Smolder.json) | 2 | 2 |
| [Sona](../data/skins/Sona.json) | 17 | 17 |
| [Soraka](../data/skins/Soraka.json) | 19 | 18 |
| [Swain](../data/skins/Swain.json) | 10 | 10 |
| [Sylas](../data/skins/Sylas.json) | 9 | 9 |
| [Syndra](../data/skins/Syndra.json) | 13 | 13 |
| [Tahm Kench](../data/skins/TahmKench.json) | 7 | 7 |
| [Taliyah](../data/skins/Taliyah.json) | 6 | 6 |
| [Talon](../data/skins/Talon.json) | 12 | 12 |
| [Taric](../data/skins/Taric.json) | 8 | 7 |
| [Teemo](../data/skins/Teemo.json) | 16 | 15 |
| [Thresh](../data/skins/Thresh.json) | 16 | 16 |
| [Tristana](../data/skins/Tristana.json) | 19 | 18 |
| [Trundle](../data/skins/Trundle.json) | 8 | 8 |
| [Tryndamere](../data/skins/Tryndamere.json) | 13 | 13 |
| [Twisted Fate](../data/skins/TwistedFate.json) | 17 | 16 |
| [Twitch](../data/skins/Twitch.json) | 15 | 14 |
| [Udyr](../data/skins/Udyr.json) | 6 | 6 |
| [Urgot](../data/skins/Urgot.json) | 8 | 8 |
| [Varus](../data/skins/Varus.json) | 15 | 15 |
| [Vayne](../data/skins/Vayne.json) | 19 | 19 |
| [Veigar](../data/skins/Veigar.json) | 16 | 16 |
| [Vel'Koz](../data/skins/Velkoz.json) | 7 | 7 |
| [Vex](../data/skins/Vex.json) | 4 | 4 |
| [Vi](../data/skins/Vi.json) | 13 | 13 |
| [Viego](../data/skins/Viego.json) | 7 | 7 |
| [Viktor](../data/skins/Viktor.json) | 8 | 8 |
| [Vladimir](../data/skins/Vladimir.json) | 14 | 14 |
| [Volibear](../data/skins/Volibear.json) | 11 | 10 |
| [Warwick](../data/skins/Warwick.json) | 17 | 16 |
| [Wukong](../data/skins/MonkeyKing.json) | 9 | 9 |
| [Xayah](../data/skins/Xayah.json) | 12 | 12 |
| [Xerath](../data/skins/Xerath.json) | 9 | 9 |
| [Xin Zhao](../data/skins/XinZhao.json) | 13 | 12 |
| [Yasuo](../data/skins/Yasuo.json) | 19 | 19 |
| [Yone](../data/skins/Yone.json) | 12 | 12 |
| [Yorick](../data/skins/Yorick.json) | 10 | 9 |
| [Yunara](../data/skins/Yunara.json) | 2 | 2 |
| [Yuumi](../data/skins/Yuumi.json) | 10 | 10 |
| [Zaahen](../data/skins/Zaahen.json) | 1 | 1 |
| [Zac](../data/skins/Zac.json) | 7 | 7 |
| [Zed](../data/skins/Zed.json) | 14 | 14 |
| [Zeri](../data/skins/Zeri.json) | 6 | 6 |
| [Ziggs](../data/skins/Ziggs.json) | 12 | 12 |
| [Zilean](../data/skins/Zilean.json) | 8 | 8 |
| [Zoe](../data/skins/Zoe.json) | 10 | 10 |
| [Zyra](../data/skins/Zyra.json) | 12 | 12 |

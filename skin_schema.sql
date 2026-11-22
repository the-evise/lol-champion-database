CREATE TABLE IF NOT EXISTS skin_lines (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL, record_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS skin_universes (
 id TEXT PRIMARY KEY, name TEXT NOT NULL, record_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS skins (
 id TEXT PRIMARY KEY, riot_skin_id INTEGER UNIQUE, champion_id TEXT NOT NULL REFERENCES champions(id),
 name TEXT NOT NULL, is_base INTEGER NOT NULL, kind TEXT NOT NULL, rarity TEXT,
 availability TEXT, release_date TEXT, variant_of TEXT REFERENCES skins(id) DEFERRABLE INITIALLY DEFERRED,
 lore_available INTEGER NOT NULL, result_label_eligible INTEGER NOT NULL, record_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS skin_line_memberships (
 skin_id TEXT REFERENCES skins(id), line_id INTEGER REFERENCES skin_lines(id),
 PRIMARY KEY(skin_id,line_id)
);
CREATE TABLE IF NOT EXISTS skin_universe_memberships (
 skin_id TEXT REFERENCES skins(id), universe_id TEXT REFERENCES skin_universes(id),
 PRIMARY KEY(skin_id,universe_id)
);
CREATE TABLE IF NOT EXISTS skin_chromas (
 id INTEGER PRIMARY KEY, parent_skin_id TEXT NOT NULL REFERENCES skins(id),
 name TEXT, record_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS skins_by_champion ON skins(champion_id);
CREATE INDEX IF NOT EXISTS skin_line_lookup ON skin_line_memberships(line_id);
CREATE INDEX IF NOT EXISTS skin_universe_lookup ON skin_universe_memberships(universe_id);
CREATE VIEW IF NOT EXISTS result_identity_catalog AS
 SELECT s.id AS result_key,s.name AS result_label,c.id AS champion_id,c.name AS champion_name,
 s.is_base,s.kind,s.rarity,s.variant_of,s.lore_available
 FROM skins s JOIN champions c ON s.champion_id=c.id
 WHERE s.result_label_eligible=1;

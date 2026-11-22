PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS champions (
 id TEXT PRIMARY KEY, riot_id INTEGER UNIQUE NOT NULL, name TEXT NOT NULL, title TEXT,
 region TEXT, summary TEXT, motivation TEXT, range_type TEXT,
 difficulty INTEGER, damage INTEGER, toughness INTEGER, control INTEGER,
 mobility INTEGER, utility INTEGER, record_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS champion_roles (
 champion_id TEXT REFERENCES champions(id), role TEXT, source_kind TEXT,
 PRIMARY KEY(champion_id,role,source_kind)
);
CREATE TABLE IF NOT EXISTS champion_themes (
 champion_id TEXT REFERENCES champions(id), theme TEXT, evidence TEXT,
 PRIMARY KEY(champion_id,theme)
);
CREATE TABLE IF NOT EXISTS related_champions (
 champion_id TEXT REFERENCES champions(id), related_id TEXT, related_name TEXT, relation_kind TEXT,
 PRIMARY KEY(champion_id,related_name)
);
CREATE TABLE IF NOT EXISTS champion_resources (
 champion_id TEXT REFERENCES champions(id), type TEXT, title TEXT, url TEXT, review_status TEXT
);
CREATE TABLE IF NOT EXISTS abilities (
 champion_id TEXT REFERENCES champions(id), slot TEXT, name TEXT, record_json TEXT,
 PRIMARY KEY(champion_id,slot)
);
CREATE TABLE IF NOT EXISTS sources (id TEXT PRIMARY KEY, kind TEXT, url TEXT, record_json TEXT);
CREATE INDEX IF NOT EXISTS roles_lookup ON champion_roles(role,source_kind);
CREATE INDEX IF NOT EXISTS themes_lookup ON champion_themes(theme);
CREATE VIEW IF NOT EXISTS role_candidates AS
 SELECT c.id,c.name,r.role,c.difficulty,c.damage,c.toughness,c.control,c.mobility,c.utility
 FROM champions c JOIN champion_roles r ON c.id=r.champion_id WHERE r.source_kind='client';

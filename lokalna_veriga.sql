CREATE TABLE zaposleni (
    emso INTEGER PRIMARY KEY,
    ime TEXT NOT NULL,
    priimek TEXT NOT NULL,
    geslo TEXT
);

CREATE TABLE lokacija (
    id INTEGER PRIMARY KEY,
    ime TEXT NOT NULL,
    vodja INTEGER NOT NULL REFERENCES zaposleni(emso) 
);

CREATE TABLE soba (
    id INTEGER PRIMARY KEY,
    velikost INTEGER NOT NULL,
    cena INTEGER NOT NULL,
    lokacija INTEGER NOT NULL REFERENCES lokacija(id),
    ureja INTEGER NOT NULL REFERENCES zaposleni(emso)
);

CREATE TABLE zajtrk (
    id INTEGER PRIMARY KEY,
    ime TEXT NOT NULL,
    cena INTEGER NOT NULL,
    pripravlja INTEGER NOT NULL REFERENCES zaposleni(emso) 
);

CREATE TABLE rezervacija (
    id INTEGER PRIMARY KEY,
    rezervirana_soba INTEGER NOT NULL REFERENCES soba(id),
    pricetek_bivanja DATE NOT NULL CHECK (datum >= now()),
    stevilo_nocitev INTEGER NOT NULL CHECK (stevilo_nocitev > 0),
    vkljucuje INTEGER REFERENCES zajtrk(id),
    geslo TEXT NOT NULL
);

GRANT ALL ON DATABASE sem2022_tiak TO brinar WITH GRANT OPTION;
GRANT ALL ON DATABASE sem2022_tiak TO tinkarac WITH GRANT OPTION;
GRANT ALL ON SCHEMA public TO brinar WITH GRANT OPTION;
GRANT ALL ON SCHEMA public TO tinkarac WITH GRANT OPTION;

GRANT ALL ON ALL TABLES IN SCHEMA public TO brinar WITH GRANT OPTION;
GRANT ALL ON ALL TABLES IN SCHEMA public TO tinkarac WITH GRANT OPTION;
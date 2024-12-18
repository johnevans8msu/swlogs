CREATE TABLE IF NOT EXISTS swlogs.overall (
    id     int generated always as identity primary key,
    date   DATE,
    bytes  bigint,
    hits   bigint
);

create index on swlogs.overall (date);

CREATE TABLE IF NOT EXISTS swlogs.bots (
    id        int generated always as identity primary key,
    ua        TEXT,
    hits      INTEGER,
    error_pct REAL,
    c429      INTEGER,
    robots    boolean,
    xmlui     boolean,
    sitemaps  boolean,
    item_pct  REAL,
    date      DATE
);

CREATE TABLE IF NOT EXISTS swlogs.ip32 (
    ip        cidr,
    hits      INTEGER,
    error_pct REAL,
    date      DATE
);

CREATE TABLE IF NOT EXISTS swlogs.ip24 (
    ip        cidr,
    hits      INTEGER,
    error_pct REAL,
    date      DATE
);

CREATE TABLE IF NOT EXISTS swlogs.ip16 (
    ip        cidr,
    hits      INTEGER,
    error_pct REAL,
    date      DATE
);

CREATE TABLE IF NOT EXISTS swlogs.staging (
    ip        cidr,
    timestamp timestamp with time zone,
    status    INTEGER,
    useragent text,
    url       text,
    bytes     INTEGER
);


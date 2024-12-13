-- Must update pg_hba.conf, add this line
-- 
-- local   jevans          jevans                                    scram-sha-256
--
\c jevans

drop schema if exists swlogs cascade;
create schema if not exists swlogs authorization jevans;

alter database jevans set search_path to swlogs, public;

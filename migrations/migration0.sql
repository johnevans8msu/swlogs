-- Must update pg_hba.conf, add this line
-- 
-- local   jevans          jevans                                    scram-sha-256
--
create role jevans login;
create database jevans owner jevans;

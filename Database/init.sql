CREATE USER compress_user WITH PASSWORD '$$53eer3&777R';
\connect compress_database;
CREATE SCHEMA compress_schema;
GRANT CREATE ON SCHEMA compress_schema TO compress_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA compress_schema TO compress_user;

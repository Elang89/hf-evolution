 ALTER SYSTEM SET wal_level = logical;
 ALTER SYSTEM SET max_replication_slots = 4;
 ALTER SYSTEM SET max_connections = 500;

 CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
 CREATE TABLE authors (
    id UUID NOT NULL,
    author_name VARCHAR(128),
    author_email VARCHAR (128), 
    CONSTRAINT pkey_author PRIMARY KEY(id)
 )
 WITH (
    OIDS=FALSE
 );

 CREATE TABLE hf_repositories (
    id UUID NOT NULL,
    repository_name VARCHAR (256) NOT NULL,
    repository_type SMALLINT NOT NULL, 
    CONSTRAINT pkey_hf_repositories PRIMARY KEY(id)
 )
 WITH (
    OIDS=FALSE
 );


 CREATE TABLE hf_commits (
    id UUID NOT NULL,
    commit_hash VARCHAR(128) NOT NULL,
    commit_message TEXT,
    author_timestamp TIMESTAMP NOT NULL, 
    commit_timestamp TIMESTAMP NOT NULL,
    insertions INTEGER,
    deletions INTEGER,
    total_lines_modified INTEGER,
    total_files_modified INTEGER,
    dmm_unit_size NUMERIC,
    dmm_unit_complexity NUMERIC,
    dmm_unit_interfacing NUMERIC,
    CONSTRAINT pkey_commit PRIMARY KEY(id)
 )
 WITH (
    OIDS=FALSE
 );
 

 CREATE TABLE file_changes (
    id UUID NOT NULL,
    filename VARCHAR(128) NOT NULL,
    change_type SMALLINT, 
    diff TEXT,
    added_lines INTEGER,
    deleted_lines INTEGER,
    nloc INTEGER,
    cyclomatic_complexity NUMERIC,
    token_count INTEGER, 
    CONSTRAINT pkey_file_change PRIMARY KEY(id)
 )
 WITH (
    OIDS=FALSE
 );


 CREATE TABLE events (
    id UUID NOT NULL,
    repository_id UUID NOT NULL,
    commit_id UUID NOT NULL, 
    author_id UUID NOT NULL,
    file_change_id UUID NOT NULL,
    CONSTRAINT pkey_event PRIMARY KEY (id),
    CONSTRAINT  fkey_hf_repository FOREIGN KEY (repository_id) REFERENCES hf_repositories(id),
    CONSTRAINT  fkey_hf_commit FOREIGN KEY (commit_id) REFERENCES hf_commits(id),
    CONSTRAINT  fkey_author FOREIGN KEY (author_id) REFERENCES authors(id),
    CONSTRAINT  fkey_file_change FOREIGN KEY  (file_change_id) REFERENCES file_changes(id) 
 ) WITH (
    OIDS=FALSE
 );


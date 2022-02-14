 ALTER SYSTEM SET wal_level = logical;
 ALTER SYSTEM SET max_replication_slots = 3;
 ALTER SYSTEM SET max_connections = 500;

 CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
 CREATE TABLE authors (
    id UUID NOT NULL,
    author_name VARCHAR(32) UNIQUE NOT NULL,
    author_email VARCHAR (32), 
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    CONSTRAINT pkey_author PRIMARY KEY(id)
 )
 WITH (
    OIDS=FALSE
 );

 CREATE TABLE artifacts (
    id UUID NOT NULL,
    artifact_name VARCHAR (64) UNIQUE NOT NULL,
    artifact_type SMALLINT NOT NULL, 
    created_at TIMESTAMP  NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    CONSTRAINT pkey_artifacts PRIMARY KEY(id)
 )
 WITH (
    OIDS=FALSE
 );


 CREATE TABLE artifact_commits (
    id UUID NOT NULL,
    author_id UUID NOT NULL,
    artifact_id UUID NOT NULL,
    commit_hash VARCHAR(40) UNIQUE NOT NULL,
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
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    CONSTRAINT pkey_artifact_commit PRIMARY KEY(id),
    CONSTRAINT fkey_author  FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE,
    CONSTRAINT fkey_artifact FOREIGN KEY (artifact_id) REFERENCES artifacts(id) ON DELETE CASCADE
 )
 WITH (
    OIDS=FALSE
 );
 
 CREATE TABLE artifact_files (
    id UUID NOT NULL,
    artifact_id UUID NOT NULL,
    artifact_commit_id UUID NOT NULL, 
    artifact_file_name VARCHAR(40) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP, 
    CONSTRAINT pkey_artifact_file PRIMARY KEY(id),
    CONSTRAINT fkey_artifact FOREIGN  KEY (artifact_id) REFERENCES artifacts(id) ON DELETE CASCADE,
    CONSTRAINT fkey_artifact_commit FOREIGN  KEY (artifact_commit_id) REFERENCES artifact_commits(id) ON DELETE CASCADE
 )
 WITH (
    OIDS=FALSE
 );

 CREATE TABLE artifact_file_changes (
    id UUID NOT NULL,
    artifact_file_id UUID NOT NULL,
    artifact_commit_id UUID NOT NULL, 
    diff TEXT,
    added_lines INTEGER,
    deleted_lines INTEGER,
    lines_of_code INTEGER,
    cyclomatic_complexity NUMERIC, 
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP, 
    CONSTRAINT pkey_artifact_file_change PRIMARY KEY(id),
    CONSTRAINT fkey_artifact_file FOREIGN  KEY (artifact_file_id) REFERENCES artifact_files(id) ON DELETE CASCADE,
    CONSTRAINT fkey_artifact_commit FOREIGN  KEY (artifact_commit_id) REFERENCES artifact_commits(id) ON DELETE CASCADE
 )
 WITH (
    OIDS=FALSE
 );
 

 CREATE TABLE issues (
    id UUID NOT NULL,
    artifact_id UUID NOT NULL, 
    issue_title VARCHAR(100) UNIQUE NOT NULL,
    issue_description TEXT,
    issue_timestamp TIMESTAMP NOT NULL,
    issue_comment_num INTEGER,
    issue_assignees INTEGER,
    issue_closing_date TIMESTAMP,
    issue_number INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    CONSTRAINT pkey_issue PRIMARY KEY (id),
    CONSTRAINT fkey_artifact FOREIGN  KEY (artifact_id) REFERENCES artifacts(id) ON DELETE CASCADE
 )
 WITH (
    OIDS=FALSE
 );

 CREATE TABLE issue_comments (
    id UUID NOT NULL,
    issue_id UUID NOT NULL,
    issue_comment_body TEXT,
    issue_comment_timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    CONSTRAINT pkey_issue_comment PRIMARY KEY (id),
    CONSTRAINT fkey_issue FOREIGN KEY (issue_id) REFERENCES issues(id) ON DELETE CASCADE
 )
 WITH (
    OIDS=FALSE
 );
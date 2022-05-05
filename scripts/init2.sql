 CREATE TABLE github_repositories (
    id UUID NOT NULL,
    repository_name VARCHAR(32),
    repository_type INTEGER,
    CONSTRAINT pkey_github_repository PRIMARY KEY (id)
 );

 CREATE TABLE issues (
    id UUID NOT NULL,
    github_repository_id UUID NOT NULL, 
    issue_title TEXT NOT NULL,
    issue_description TEXT,
    issue_timestamp TIMESTAMP NOT NULL,
    issue_comment_num INTEGER,
    issue_state VARCHAR(10) NOT NULL,
    issue_locked BOOLEAN NOT NULL,
    issue_lock_reason VARCHAR (30),
    issue_assignees INTEGER,
    issue_closing_date TIMESTAMP,
    issue_number INTEGER,
    CONSTRAINT pkey_issue PRIMARY KEY (id),
    CONSTRAINT fkey_github_repository FOREIGN KEY (github_repository_id) REFERENCES github_repositories(id) ON DELETE CASCADE
 )
 WITH (
    OIDS=FALSE
 );

 CREATE TABLE issue_comments (
    id UUID NOT NULL,
    issue_id UUID NOT NULL,
    issue_comment_body TEXT,
    issue_comment_length INTEGER,
    issue_comment_timestamp TIMESTAMP NOT NULL,
    CONSTRAINT pkey_issue_comment PRIMARY KEY (id),
    CONSTRAINT fkey_issue FOREIGN KEY (issue_id) REFERENCES issues(id) ON DELETE CASCADE
 )
 WITH (
    OIDS=FALSE
 );

 CREATE TABLE workflow_runs (
    id UUID NOT NULL,
    github_repository_id UUID NOT NULL,
    run_number INTEGER NOT NULL,
    event VARCHAR(10) NOT NULL,
    run_timestamp TIMESTAMP NOT NULL,
    duration_ms INTEGER, 
    status VARCHAR(10) NOT NULL,
    conclusion VARCHAR(10),
    CONSTRAINT pkey_workflow_run PRIMARY KEY (id),
    CONSTRAINT fkey_github_repository FOREIGN KEY (github_repository_id) REFERENCES github_repositories(id) ON DELETE CASCADE
 )
 WITH (
     OIDS=FALSE    
 );
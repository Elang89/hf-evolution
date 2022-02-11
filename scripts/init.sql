 CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


 CREATE TABLE authors (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    author_name VARCHAR(32) UNIQUE NOT NULL,
    author_fake_name VARCHAR(32) UNIQUE NOT NULL,
    author_email VARCHAR (32), 
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    CONSTRAINT pkey_author PRIMARY KEY(id)
 )
 WITH (
    OIDS=FALSE
 );

 CREATE TABLE datasets (
    id UUID NOT NULL DEFAULT  uuid_generate_v4(),
    dataset_name VARCHAR (64) UNIQUE NOT NULL,
    created_at TIMESTAMP  NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    CONSTRAINT pkey_dataset PRIMARY KEY(id)
 )
 WITH (
    OIDS=FALSE
 );

 CREATE TABLE models (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    model_name VARCHAR(64) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    CONSTRAINT pkey_model PRIMARY KEY(id)
 )
 WITH (
    OIDS=FALSE
 );

 CREATE TABLE products (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    product_name VARCHAR(64) UNIQUE NOT NULL,
    created_at TIMESTAMP  NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    CONSTRAINT pkey_product PRIMARY KEY(id)
 ) 
 WITH (
    OIDS=FALSE
 );


 CREATE TABLE dataset_commits (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    author_id UUID NOT NULL,
    dataset_id UUID NOT NULL,
    commit_hash VARCHAR(40) UNIQUE NOT NULL,
    commit_message TEXT,
    commit_timestamp TIMESTAMP NOT NULL, 
    insertions INTEGER,
    deletions INTEGER,
    total_lines_modified INTEGER,
    total_files_modified INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    CONSTRAINT pkey_dataset_commit PRIMARY KEY(id),
    CONSTRAINT fkey_author  FOREIGN KEY (author_id) REFERENCES authors(id),
    CONSTRAINT fkey_dataset FOREIGN KEY (dataset_id) REFERENCES datasets(id)
 )
 WITH (
    OIDS=FALSE
 );
 
 CREATE TABLE dataset_files (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    dataset_id UUID NOT NULL,
    dataset_commit_id UUID NOT NULL, 
    dataset_file_name VARCHAR(40) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP, 
    CONSTRAINT pkey_dataset_file PRIMARY KEY(id),
    CONSTRAINT fkey_dataset FOREIGN  KEY (dataset_id) REFERENCES datasets(id),
    CONSTRAINT fkey_dataset_commit FOREIGN  KEY (dataset_commit_id) REFERENCES dataset_commits(id)
 )
 WITH (
    OIDS=FALSE
 );

 CREATE TABLE dataset_file_changes (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    dataset_file_id UUID NOT NULL,
    diff TEXT,
    added_lines INTEGER,
    deleted_lines INTEGER,
    lines_of_code INTEGER,
    complexity NUMERIC, 
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP, 
    CONSTRAINT pkey_dataset_file_change PRIMARY KEY(id),
    CONSTRAINT fkey_dataset_file FOREIGN  KEY (dataset_file_id) REFERENCES dataset_files(id)
 )
 WITH (
    OIDS=FALSE
 );
 
 CREATE TABLE model_commits (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    author_id UUID NOT NULL,
    model_id UUID NOT NULL,
    commit_hash VARCHAR(40) UNIQUE NOT NULL,
    commit_message TEXT,
    commit_timestamp TIMESTAMP NOT NULL,
    insertions INTEGER,
    deletions INTEGER,
    total_lines_modified INTEGER,
    total_files_modified INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    CONSTRAINT pkey_model_commit PRIMARY KEY (id),
    CONSTRAINT fkey_author FOREIGN KEY (author_id) REFERENCES authors(id),
    CONSTRAINT fkey_model FOREIGN KEY (model_id) REFERENCES models(id)
 )
 WITH (
    OIDS=FALSE
 );
CREATE TABLE model_files (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    model_id UUID NOT NULL,
    model_commit_id UUID NOT NULL, 
    model_file_name VARCHAR(40) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP, 
    CONSTRAINT pkey_model_file PRIMARY KEY(id),
    CONSTRAINT fkey_model FOREIGN  KEY (model_id) REFERENCES  models(id),
    CONSTRAINT fkey_model_commit FOREIGN  KEY (model_commit_id) REFERENCES model_commits(id)
 )
 WITH (
    OIDS=FALSE
 );

  CREATE TABLE model_file_changes (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    model_file_id UUID NOT NULL,
    diff TEXT,
    added_lines INTEGER,
    deleted_lines INTEGER,
    lines_of_code INTEGER,
    complexity NUMERIC, 
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP, 
    CONSTRAINT pkey_model_file_change PRIMARY KEY(id),
    CONSTRAINT fkey_model_file FOREIGN  KEY (model_file_id) REFERENCES model_files(id)
 )
 WITH (
    OIDS=FALSE
 );

 CREATE TABLE product_commits (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    author_id UUID NOT NULL,
    product_id UUID NOT NULL,
    commit_hash VARCHAR(40) UNIQUE NOT NULL,
    commit_message TEXT,
    commit_timestamp TIMESTAMP NOT NULL,
    insertions INTEGER,
    deletions INTEGER,
    total_lines_modified INTEGER,
    total_files_modified INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    CONSTRAINT pkey_product_commit PRIMARY KEY (id),
    CONSTRAINT fkey_author FOREIGN KEY (author_id) REFERENCES authors(id),
    CONSTRAINT fkey_product FOREIGN KEY (product_id) REFERENCES products(id)
 )
 WITH (
     OIDS=FALSE
 );

   CREATE TABLE product_files (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL,
    product_commit_id UUID NOT NULL, 
    product_file_name VARCHAR(40) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP, 
    CONSTRAINT pkey_product_file PRIMARY KEY(id),
    CONSTRAINT fkey_product FOREIGN  KEY (product_id) REFERENCES products(id),
    CONSTRAINT fkey_product_commit FOREIGN  KEY (product_commit_id) REFERENCES product_commits(id)
 )
 WITH (
    OIDS=FALSE
 );

  CREATE TABLE product_file_changes (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    product_file_id UUID NOT NULL,
    diff TEXT,
    added_lines INTEGER,
    deleted_lines INTEGER,
    lines_of_code INTEGER,
    complexity NUMERIC, 
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP, 
    CONSTRAINT pkey_product_file_change PRIMARY KEY(id),
    CONSTRAINT fkey_product_file FOREIGN  KEY (product_file_id) REFERENCES product_files(id)
 )
 WITH (
    OIDS=FALSE
 );

 CREATE TABLE issues (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL, 
    issue_title VARCHAR(100) UNIQUE NOT NULL,
    issue_description TEXT,
    issue_timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    CONSTRAINT pkey_issue PRIMARY KEY (id),
    CONSTRAINT fkey_product FOREIGN  KEY (product_id) REFERENCES products(id)
 )
 WITH (
    OIDS=FALSE
 );

 CREATE TABLE issue_comments (
    id UUID NOT NULL DEFAULT uuid_generate_v4(),
    issue_id UUID NOT NULL,
    issue_comment_body TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    CONSTRAINT pkey_issue_comment PRIMARY KEY (id),
    CONSTRAINT fkey_issue FOREIGN KEY (issue_id) REFERENCES issues(id)
 )
 WITH (
    OIDS=FALSE
 );
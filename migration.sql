BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 74de74a58414

CREATE TABLE documents (
    name VARCHAR(255) NOT NULL, 
    description VARCHAR(500), 
    category VARCHAR(255) NOT NULL, 
    size INTEGER NOT NULL, 
    id UUID DEFAULT gen_random_uuid() NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (name)
);

INSERT INTO alembic_version (version_num) VALUES ('74de74a58414') RETURNING alembic_version.version_num;

COMMIT;


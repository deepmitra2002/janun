CREATE EXTENSION IF NOT EXISTS vector;


CREATE TABLE admin_users (
	id VARCHAR(36) NOT NULL, 
	username VARCHAR(120) NOT NULL, 
	password_hash TEXT NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (username)
)

;


CREATE TABLE feedback (
	id VARCHAR(36) NOT NULL, 
	message TEXT NOT NULL, 
	service_slug VARCHAR(120), 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
)

;


CREATE TABLE service_categories (
	slug VARCHAR(80) NOT NULL, 
	name_en VARCHAR(160) NOT NULL, 
	name_bn VARCHAR(160) NOT NULL, 
	icon VARCHAR(40) NOT NULL, 
	PRIMARY KEY (slug)
)

;


CREATE TABLE admin_sessions (
	token_hash VARCHAR(64) NOT NULL, 
	admin_id VARCHAR(36) NOT NULL, 
	expires_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (token_hash), 
	FOREIGN KEY(admin_id) REFERENCES admin_users (id)
)

;


CREATE TABLE audit_logs (
	id VARCHAR(36) NOT NULL, 
	admin_id VARCHAR(36) NOT NULL, 
	action VARCHAR(100) NOT NULL, 
	target VARCHAR(100) NOT NULL, 
	note TEXT NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(admin_id) REFERENCES admin_users (id)
)

;


CREATE TABLE services (
	id VARCHAR(36) NOT NULL, 
	slug VARCHAR(120) NOT NULL, 
	name_en VARCHAR(200) NOT NULL, 
	name_bn VARCHAR(200) NOT NULL, 
	category VARCHAR(80) NOT NULL, 
	description_en TEXT NOT NULL, 
	description_bn TEXT NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	official_url TEXT NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(category) REFERENCES service_categories (slug)
)

;

CREATE UNIQUE INDEX ix_services_slug ON services (slug);

CREATE INDEX ix_services_status ON services (status);


CREATE TABLE sources (
	id VARCHAR(36) NOT NULL, 
	service_id VARCHAR(36) NOT NULL, 
	url TEXT NOT NULL, 
	title VARCHAR(300) NOT NULL, 
	agency VARCHAR(200) NOT NULL, 
	current_version VARCHAR(36), 
	PRIMARY KEY (id), 
	FOREIGN KEY(service_id) REFERENCES services (id)
)

;

CREATE INDEX ix_sources_service_id ON sources (service_id);


CREATE TABLE source_versions (
	id VARCHAR(36) NOT NULL, 
	source_id VARCHAR(36) NOT NULL, 
	content TEXT NOT NULL, 
	content_hash VARCHAR(64) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	claims JSON NOT NULL, 
	retrieved_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	verified_at TIMESTAMP WITH TIME ZONE, 
	review_due TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(source_id) REFERENCES sources (id)
)

;

CREATE INDEX ix_source_versions_status ON source_versions (status);

CREATE INDEX ix_source_versions_source_id ON source_versions (source_id);


CREATE TABLE knowledge_chunks (
	id VARCHAR(36) NOT NULL, 
	version_id VARCHAR(36) NOT NULL, 
	text TEXT NOT NULL, 
	ordinal INTEGER NOT NULL, 
	embedding VECTOR(1536), 
	embedding_model VARCHAR(150), 
	PRIMARY KEY (id), 
	FOREIGN KEY(version_id) REFERENCES source_versions (id)
)

;

CREATE INDEX ix_knowledge_chunks_version_id ON knowledge_chunks (version_id);

CREATE INDEX ix_chunks_fts ON knowledge_chunks USING gin (to_tsvector('simple', text));
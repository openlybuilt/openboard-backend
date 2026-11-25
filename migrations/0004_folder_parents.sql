ALTER TABLE folders ADD COLUMN parent_id TEXT;
CREATE INDEX folders_owner_parent ON folders(owner_id, parent_id);

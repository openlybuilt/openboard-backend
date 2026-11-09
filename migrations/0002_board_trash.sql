ALTER TABLE boards ADD COLUMN deleted_at INTEGER;
CREATE INDEX boards_deleted_at ON boards(deleted_at);

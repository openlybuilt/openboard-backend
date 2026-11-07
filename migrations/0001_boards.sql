CREATE TABLE boards (
  owner_id TEXT NOT NULL,
  id TEXT NOT NULL,
  body TEXT NOT NULL,
  updated_at INTEGER NOT NULL,
  PRIMARY KEY (owner_id, id)
);
CREATE INDEX boards_owner_updated ON boards(owner_id, updated_at DESC);

-- +goose Up
CREATE TABLE bots (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT NOT NULL UNIQUE,
    interval_seconds INTEGER NOT NULL DEFAULT 60,
    kuma_url TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1
);

-- +goose Down
DROP TABLE bots;
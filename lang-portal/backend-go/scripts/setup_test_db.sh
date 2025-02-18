#!/bin/bash

# Create test database directory
mkdir -p config/database

# Remove existing test database
rm -f config/database/test.db

# Initialize test database
sqlite3 config/database/test.db <<EOF
-- Create tables with AUTOINCREMENT starting from 1
CREATE TABLE groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at DATETIME NOT NULL
);

CREATE TABLE words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    japanese TEXT NOT NULL,
    romaji TEXT NOT NULL,
    english TEXT NOT NULL,
    created_at DATETIME NOT NULL
);

-- ... other tables ...
EOF

# Make the script executable
chmod +x scripts/setup_test_db.sh 
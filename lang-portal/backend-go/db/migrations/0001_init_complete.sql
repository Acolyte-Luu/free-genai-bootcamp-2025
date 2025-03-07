PRAGMA foreign_keys = OFF;

-- Drop tables if they exist (for clean install)
DROP TABLE IF EXISTS word_review_items;
DROP TABLE IF EXISTS study_sessions;
DROP TABLE IF EXISTS study_activities;
DROP TABLE IF EXISTS word_groups;
DROP TABLE IF EXISTS words_groups; -- In case the old name still exists
DROP TABLE IF EXISTS words;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS schema_migrations;

-- Create words table with parts column included
CREATE TABLE words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    japanese TEXT NOT NULL,
    romaji TEXT NOT NULL,
    english TEXT NOT NULL,
    parts TEXT NULL, -- Parts column included from start
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create groups table
CREATE TABLE groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create the join table with the correct name (word_groups)
CREATE TABLE word_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (word_id) REFERENCES words(id),
    FOREIGN KEY (group_id) REFERENCES groups(id)
);

-- Create the properly structured study_activities table
CREATE TABLE study_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    thumbnail_url TEXT NULL,
    description TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create study_sessions table
CREATE TABLE study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    study_activity_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups(id),
    FOREIGN KEY (study_activity_id) REFERENCES study_activities(id)
);

-- Create word_review_items table
CREATE TABLE word_review_items (
    word_id INTEGER NOT NULL,
    study_session_id INTEGER NOT NULL,
    correct BOOLEAN NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (word_id, study_session_id),
    FOREIGN KEY (word_id) REFERENCES words(id),
    FOREIGN KEY (study_session_id) REFERENCES study_sessions(id)
);

-- Create migrations tracking table
CREATE TABLE schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default study activities
INSERT INTO study_activities (id, name, thumbnail_url, description) VALUES 
(1, 'Flashcards', '/images/flashcards.png', 'Practice vocabulary with flashcards'),
(2, 'Writing Practice', '/images/writing.png', 'Practice writing Japanese characters'),
(3, 'Reading Exercise', '/images/reading.png', 'Improve reading comprehension'),
(4, 'Listening Practice', '/images/listening.png', 'Enhance listening skills with audio exercises'),
(5, 'Speaking Drill', '/images/speaking.png', 'Practice pronunciation and speaking');

-- Mark all migrations as applied
INSERT INTO schema_migrations (version) VALUES 
('0001_init'),
('0002_add_parts_to_words'),
('0003_fix_study_activities'),
('0004_fix_table_naming'),
('0005_add_study_activities_seed_data');

PRAGMA foreign_keys = ON; 
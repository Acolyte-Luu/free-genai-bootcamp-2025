import sqlite3
from typing import List, Dict, Any

def create_tables():
    """Create the necessary tables in the SQLite database."""
    conn = sqlite3.connect('song_vocabulary.db')
    cursor = conn.cursor()
    
    # Create songs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        artist TEXT,
        lyrics TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create vocabulary table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vocabulary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        song_id INTEGER,
        word TEXT NOT NULL,
        translation TEXT NOT NULL,
        example TEXT NOT NULL,
        FOREIGN KEY (song_id) REFERENCES songs (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def save_song_and_vocabulary(title, artist, lyrics, vocabulary):
    """Save a song and its vocabulary to the database."""
    
    # Connect to the database
    conn = sqlite3.connect('song_vocabulary.db')
    cursor = conn.cursor()
    
    # Insert the song
    cursor.execute('''
        INSERT INTO songs (title, artist, lyrics)
        VALUES (?, ?, ?)
    ''', (title, artist, lyrics))
    
    # Get the song id
    song_id = cursor.lastrowid
    
    # Insert the vocabulary items
    for item in vocabulary:
        # Map our vocabulary structure to database fields
        word = item.get('kanji', '')
        translation = item.get('english', '')
        # Use romaji as example if available, or create a simple example
        example = f"Example with {word}" if 'example' not in item else item['example']
        
        cursor.execute('''
            INSERT INTO vocabulary (song_id, word, translation, example)
            VALUES (?, ?, ?, ?)
        ''', (song_id, word, translation, example))
    
    # Commit the changes
    conn.commit()
    conn.close()
    
    return song_id

if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully") 
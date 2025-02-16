package database

import (
	"database/sql"
	"log"
	"path/filepath"
	"sync"

	_ "github.com/mattn/go-sqlite3"
)

var (
	db   *sql.DB
	once sync.Once
)

// GetDB returns a singleton database connection
func GetDB() *sql.DB {
	once.Do(func() {
		var err error
		dbPath := filepath.Join(".", "words.db")
		db, err = sql.Open("sqlite3", dbPath)
		if err != nil {
			log.Fatalf("Failed to open database: %v", err)
		}

		// Test the connection
		if err = db.Ping(); err != nil {
			log.Fatalf("Failed to ping database: %v", err)
		}

		log.Println("Database connection established")
	})

	return db
}

// Close closes the database connection
func Close() error {
	if db != nil {
		return db.Close()
	}
	return nil
}

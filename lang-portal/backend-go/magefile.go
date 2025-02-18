//go:build mage

package main

import (
	"database/sql"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/lang-portal/backend-go/internal/database/seed"
	"github.com/magefile/mage/sh"
	_ "github.com/mattn/go-sqlite3"
)

const dbPath = "words.db"

// InitDB initializes the SQLite database
func InitDB() error {
	fmt.Println("Initializing database...")

	if _, err := os.Stat(dbPath); err == nil {
		fmt.Println("Database already exists")
		return nil
	}

	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		return fmt.Errorf("failed to open database: %v", err)
	}
	defer db.Close()

	fmt.Println("Database initialized successfully")
	return nil
}

// Migrate runs all pending migrations
func Migrate() error {
	fmt.Println("Running migrations...")

	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		return fmt.Errorf("failed to open database: %v", err)
	}
	defer db.Close()

	// Create migrations table if it doesn't exist
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS migrations (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT NOT NULL,
			applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)
	`)
	if err != nil {
		return fmt.Errorf("failed to create migrations table: %v", err)
	}

	// Get list of migration files
	files, err := filepath.Glob("db/migrations/*.sql")
	if err != nil {
		return fmt.Errorf("failed to read migration files: %v", err)
	}
	sort.Strings(files)

	// Apply each migration
	for _, file := range files {
		name := filepath.Base(file)
		var exists bool
		err = db.QueryRow("SELECT EXISTS(SELECT 1 FROM migrations WHERE name = ?)", name).Scan(&exists)
		if err != nil {
			return fmt.Errorf("failed to check migration status: %v", err)
		}

		if exists {
			fmt.Printf("Skipping migration %s (already applied)\n", name)
			continue
		}

		content, err := os.ReadFile(file)
		if err != nil {
			return fmt.Errorf("failed to read migration file %s: %v", name, err)
		}

		tx, err := db.Begin()
		if err != nil {
			return fmt.Errorf("failed to start transaction: %v", err)
		}

		// Split the content into individual statements
		statements := strings.Split(string(content), ";")
		for _, stmt := range statements {
			stmt = strings.TrimSpace(stmt)
			if stmt == "" {
				continue
			}

			if _, err := tx.Exec(stmt); err != nil {
				tx.Rollback()
				return fmt.Errorf("failed to execute migration %s: %v", name, err)
			}
		}

		if _, err := tx.Exec("INSERT INTO migrations (name) VALUES (?)", name); err != nil {
			tx.Rollback()
			return fmt.Errorf("failed to record migration %s: %v", name, err)
		}

		if err := tx.Commit(); err != nil {
			return fmt.Errorf("failed to commit migration %s: %v", name, err)
		}

		fmt.Printf("Applied migration %s\n", name)
	}

	fmt.Println("Migrations completed successfully")
	return nil
}

// Seed loads seed data into the database
func Seed() error {
	fmt.Println("Loading seed data...")

	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		return fmt.Errorf("failed to open database: %v", err)
	}
	defer db.Close()

	seedData, err := seed.LoadSeedData("db/seeds")
	if err != nil {
		return fmt.Errorf("failed to load seed data: %v", err)
	}

	seeder := seed.NewSeeder(db)
	if err := seeder.Seed(seedData); err != nil {
		return fmt.Errorf("failed to seed database: %v", err)
	}

	fmt.Println("Seed data loaded successfully")
	return nil
}

// runMigrations applies migrations to the given database
func runMigrations(db *sql.DB) error {
	// Create migrations table
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS migrations (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT NOT NULL,
			applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)
	`)
	if err != nil {
		return fmt.Errorf("failed to create migrations table: %v", err)
	}

	// Get list of migration files
	files, err := filepath.Glob("db/migrations/*.sql")
	if err != nil {
		return fmt.Errorf("failed to read migration files: %v", err)
	}
	sort.Strings(files)

	// Apply each migration
	for _, file := range files {
		name := filepath.Base(file)
		var exists bool
		err = db.QueryRow("SELECT EXISTS(SELECT 1 FROM migrations WHERE name = ?)", name).Scan(&exists)
		if err != nil {
			return fmt.Errorf("failed to check migration status: %v", err)
		}

		if exists {
			fmt.Printf("Skipping migration %s (already applied)\n", name)
			continue
		}

		content, err := os.ReadFile(file)
		if err != nil {
			return fmt.Errorf("failed to read migration file %s: %v", name, err)
		}

		// Execute migration
		if _, err := db.Exec(string(content)); err != nil {
			return fmt.Errorf("failed to execute migration %s: %v", name, err)
		}

		// Record migration
		if _, err := db.Exec("INSERT INTO migrations (name) VALUES (?)", name); err != nil {
			return fmt.Errorf("failed to record migration %s: %v", name, err)
		}

		fmt.Printf("Applied migration %s\n", name)
	}

	return nil
}

// SetupTestDB creates and initializes the test database
func SetupTestDB() error {
	fmt.Println("Setting up test database...")

	// Create directory
	if err := os.MkdirAll("config/database", 0755); err != nil {
		return err
	}

	// Remove existing test db
	if err := os.Remove("config/database/test.db"); err != nil && !os.IsNotExist(err) {
		return err
	}

	// Initialize test database
	db, err := sql.Open("sqlite3", "config/database/test.db")
	if err != nil {
		return err
	}
	defer db.Close()

	// Run schema creation
	if err := runMigrations(db); err != nil {
		return err
	}

	return nil
}

// ResetTestDB resets the test database to a clean state
func ResetTestDB() error {
	return SetupTestDB()
}

// Test runs tests with the test database
func Test() error {
	if err := ResetTestDB(); err != nil {
		return err
	}

	os.Setenv("GO_ENV", "test")
	return sh.Run("go", "test", "./...")
}

package main

import (
	"database/sql"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/lang-portal/backend-go/internal/api/routes"
	"github.com/lang-portal/backend-go/internal/config"
	"github.com/lang-portal/backend-go/internal/database/seed"
	"github.com/lang-portal/backend-go/internal/services"
	_ "github.com/mattn/go-sqlite3"
)

// runMigrations handles database migrations
func runMigrations(db *sql.DB) error {
	log.Println("Checking for database migrations...")

	// First, create migrations table if it doesn't exist
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS schema_migrations (
			version TEXT PRIMARY KEY,
			applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
	`)
	if err != nil {
		return err
	}

	// Get all applied migrations
	rows, err := db.Query("SELECT version FROM schema_migrations")
	if err != nil {
		return err
	}
	defer rows.Close()

	appliedMigrations := make(map[string]bool)
	for rows.Next() {
		var version string
		if err := rows.Scan(&version); err != nil {
			return err
		}
		appliedMigrations[version] = true
	}

	// Get all migration files
	migrationsDir := "db/migrations"
	files, err := ioutil.ReadDir(migrationsDir)
	if err != nil {
		return err
	}

	// Sort migration files to ensure order
	var migrationFiles []string
	for _, file := range files {
		if !file.IsDir() && strings.HasSuffix(file.Name(), ".sql") {
			migrationFiles = append(migrationFiles, file.Name())
		}
	}
	sort.Strings(migrationFiles)

	// Apply pending migrations
	for _, filename := range migrationFiles {
		version := strings.TrimSuffix(filename, ".sql")

		// Skip if already applied
		if appliedMigrations[version] {
			log.Printf("Migration %s already applied", version)
			continue
		}

		// Read migration file
		migrationPath := filepath.Join(migrationsDir, filename)
		migrationSQL, err := ioutil.ReadFile(migrationPath)
		if err != nil {
			return err
		}

		log.Printf("Applying migration: %s", filename)

		// Begin transaction for this migration
		tx, err := db.Begin()
		if err != nil {
			return err
		}

		// Execute each statement in the migration
		for _, statement := range strings.Split(string(migrationSQL), ";") {
			statement = strings.TrimSpace(statement)
			if statement == "" {
				continue
			}

			if _, err := tx.Exec(statement); err != nil {
				tx.Rollback()
				return err
			}
		}

		// Record that this migration was applied
		_, err = tx.Exec("INSERT INTO schema_migrations (version) VALUES (?)", version)
		if err != nil {
			tx.Rollback()
			return err
		}

		// Commit transaction
		if err := tx.Commit(); err != nil {
			return err
		}

		log.Printf("Successfully applied migration: %s", filename)
	}

	log.Println("Database migrations are up-to-date")
	return nil
}

// initializeDatabase handles initial database setup using consolidated migration
func initializeDatabase(db *sql.DB) error {
	// Check if database is already initialized
	var tableCount int
	err := db.QueryRow("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").Scan(&tableCount)
	if err != nil {
		return err
	}

	// If database already has tables, assume it's initialized
	if tableCount > 0 {
		log.Println("Database already initialized")
		return nil
	}

	// Database is empty, run the complete initialization
	log.Println("Initializing new database...")
	migrationSQL, err := ioutil.ReadFile("db/migrations/0001_init_complete.sql")
	if err != nil {
		return fmt.Errorf("failed to read migration file: %v", err)
	}

	// Execute the migration script
	_, err = db.Exec(string(migrationSQL))
	if err != nil {
		return fmt.Errorf("failed to initialize database: %v", err)
	}

	log.Println("Database initialized successfully")
	return nil
}

// Add this function to verify all required tables exist
func verifyDatabaseTables(db *sql.DB) error {
	requiredTables := []string{
		"words", "groups", "word_groups", "study_activities",
		"study_sessions", "word_review_items", "schema_migrations",
	}

	log.Println("Verifying database tables...")

	for _, table := range requiredTables {
		var count int
		err := db.QueryRow(fmt.Sprintf("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='%s'", table)).Scan(&count)
		if err != nil {
			return fmt.Errorf("error checking for table %s: %v", table, err)
		}

		if count == 0 {
			return fmt.Errorf("required table %s does not exist", table)
		}

		log.Printf("Table %s exists", table)
	}

	log.Println("All required tables verified successfully")
	return nil
}

func main() {
	// Set Gin to Release mode
	gin.SetMode(gin.ReleaseMode)

	dbPath := config.GetDBPath()
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Verify database connection
	if err := db.Ping(); err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	// Initialize or migrate the database
	if os.Getenv("GO_ENV") == "test" {
		// For tests, always recreate the database completely
		log.Println("Test mode: Forcing complete database rebuild")

		// Delete the test database file if it exists
		os.Remove(dbPath)

		// Reconnect to the database (which will create a new empty file)
		db.Close()
		db, err = sql.Open("sqlite3", dbPath)
		if err != nil {
			log.Fatalf("Failed to reconnect to database: %v", err)
		}

		// Initialize with the complete schema
		if err := initializeDatabase(db); err != nil {
			log.Fatalf("Failed to initialize test database: %v", err)
		}

		// Verify all tables exist
		if err := verifyDatabaseTables(db); err != nil {
			log.Fatalf("Database verification failed: %v", err)
		}
	} else {
		// For normal operation, try initialization or fall back to migrations
		if err := initializeDatabase(db); err != nil {
			if err := runMigrations(db); err != nil {
				log.Fatalf("Failed to run migrations: %v", err)
			}
		}
	}

	// After running migrations, seed the database with initial data
	if os.Getenv("GO_ENV") != "test" {
		log.Println("Checking for seed data...")
		if err := seed.LoadSeedData(db, "db/seeds"); err != nil {
			log.Printf("Warning: Failed to load seed data: %v", err)
		}
	}

	// Setup router with database
	router := routes.SetupRouter(db)

	// Add CORS middleware
	router.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://localhost:8081"},
		AllowMethods:     []string{"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
	}))

	// Create services
	llmService := services.NewLLMService()

	// Register routes
	router.POST("/generate-vocabulary", func(c *gin.Context) {
		var req struct {
			Theme string `json:"theme"`
		}
		if err := c.BindJSON(&req); err != nil {
			c.JSON(400, gin.H{"error": err.Error()})
			return
		}

		vocab, err := llmService.GenerateVocabulary(req.Theme)
		if err != nil {
			c.JSON(500, gin.H{"error": err.Error()})
			return
		}

		c.JSON(200, vocab)
	})

	// Start server
	log.Println("Starting server on :8080")
	if err := router.Run(":8080"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

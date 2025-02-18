package main

import (
	"database/sql"
	"log"

	"github.com/gin-gonic/gin"
	"github.com/lang-portal/backend-go/internal/api/routes"
	"github.com/lang-portal/backend-go/internal/config"
	_ "github.com/mattn/go-sqlite3"
)

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

	// Setup router with database
	router := routes.SetupRouter(db)

	// Start server
	log.Println("Starting server on :8080")
	if err := router.Run(":8080"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

package main

import (
	"log"

	"github.com/gin-gonic/gin"
	"github.com/lang-portal/backend-go/internal/api/routes"
	"github.com/lang-portal/backend-go/internal/database"
)

func main() {
	// Set Gin to Release mode
	gin.SetMode(gin.ReleaseMode)

	// Initialize database connection
	db := database.GetDB()
	defer database.Close()

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

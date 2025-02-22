package main

import (
	"database/sql"
	"log"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/lang-portal/backend-go/internal/api/routes"
	"github.com/lang-portal/backend-go/internal/config"
	"github.com/lang-portal/backend-go/internal/services"
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

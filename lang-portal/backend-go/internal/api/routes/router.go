package routes

import (
	"database/sql"

	"github.com/gin-gonic/gin"
	"github.com/lang-portal/backend-go/internal/api/handlers"
	"github.com/lang-portal/backend-go/internal/database/repository"
	"github.com/lang-portal/backend-go/internal/middleware"
	"github.com/lang-portal/backend-go/internal/services"
)

// SetupRouter initializes all routes for the application
func SetupRouter(db *sql.DB) *gin.Engine {
	router := gin.Default()

	// Add middleware
	router.Use(middleware.LoggerMiddleware())
	router.Use(middleware.ErrorHandler())

	// Add CORS middleware
	router.Use(middleware.CORSMiddleware())

	// Initialize repositories
	wordRepo := repository.NewWordRepository(db)
	groupRepo := repository.NewGroupRepository(db)
	studyRepo := repository.NewStudyRepository(db)
	dashRepo := repository.NewDashboardRepository(db)

	// Initialize services
	studyService := services.NewStudyService(studyRepo, wordRepo, groupRepo)

	// Initialize handlers
	wordHandler := handlers.NewWordHandler(wordRepo)
	groupHandler := handlers.NewGroupHandler(groupRepo)
	studyHandler := handlers.NewStudyHandler(studyRepo, studyService)
	dashboardHandler := handlers.NewDashboardHandler(dashRepo)

	// API routes group
	api := router.Group("/api")
	{
		// Words routes
		api.GET("/words", wordHandler.GetWords)
		api.GET("/words/:id", wordHandler.GetWord)

		// Groups routes
		api.GET("/groups", groupHandler.GetGroups)
		api.GET("/groups/:id", groupHandler.GetGroup)
		api.GET("/groups/:id/words", groupHandler.GetGroupWords)
		api.GET("/groups/:id/words/raw", groupHandler.GetGroupWordsRaw)
		api.POST("/groups", groupHandler.CreateGroup)
		api.POST("/groups/:id/words", groupHandler.CreateGroupWords)
		api.GET("/groups/:id/study_sessions", groupHandler.GetGroupStudySessions)

		// Study activities routes
		api.GET("/study_activities", studyHandler.GetStudyActivities)
		api.POST("/study_activities", studyHandler.CreateStudyActivity)
		api.POST("/study_activities/sessions", studyHandler.CreateStudySession)
		api.GET("/study_activities/:id", studyHandler.GetStudyActivity)
		api.GET("/study_activities/:id/sessions", studyHandler.GetActivitySessions)
		api.GET("/study_activities/:id/launch", studyHandler.GetActivityLaunchData)

		// Study sessions routes
		api.GET("/study_sessions", studyHandler.GetStudySessions)
		api.GET("/study_sessions/:id", studyHandler.GetStudySession)
		api.POST("/study_sessions/:id/words/:word_id/review", studyHandler.ReviewWord)
		api.GET("/study_sessions/:id/words", studyHandler.GetSessionWords)

		// Dashboard routes
		dashboard := api.Group("/dashboard")
		{
			dashboard.GET("/last_study_session", dashboardHandler.GetLastStudySession)
			dashboard.GET("/study_progress", dashboardHandler.GetStudyProgress)
			dashboard.GET("/quick_stats", dashboardHandler.GetQuickStats)
		}

		// Reset routes
		api.POST("/reset_history", dashboardHandler.ResetHistory)
		api.POST("/full_reset", dashboardHandler.FullReset)

		// Ollama routes
		api.POST("/generate-vocabulary", func(c *gin.Context) {
			var req struct {
				Theme string `json:"theme"`
			}

			if err := c.BindJSON(&req); err != nil {
				c.JSON(400, gin.H{"error": "Invalid request"})
				return
			}

			llm := services.NewLLMService()
			vocab, err := llm.GenerateVocabulary(req.Theme)
			if err != nil {
				c.JSON(500, gin.H{"error": err.Error()})
				return
			}

			c.JSON(200, vocab)
		})
	}

	return router
}

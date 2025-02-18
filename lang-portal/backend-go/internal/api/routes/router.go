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
		api.POST("/groups", groupHandler.CreateGroup)
		api.POST("/groups/:id/words", groupHandler.CreateGroupWords)

		// Study sessions routes
		api.GET("/study_sessions", studyHandler.GetStudySessions)
		api.GET("/study_sessions/:id", studyHandler.GetStudySession)
		api.POST("/study_activities", studyHandler.CreateStudySession)
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
	}

	return router
}

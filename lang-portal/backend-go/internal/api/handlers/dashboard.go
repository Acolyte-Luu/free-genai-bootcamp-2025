package handlers

import (
	"fmt"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/lang-portal/backend-go/internal/database/repository"
)

type DashboardHandler struct {
	dashRepo *repository.DashboardRepository
}

func NewDashboardHandler(dashRepo *repository.DashboardRepository) *DashboardHandler {
	return &DashboardHandler{dashRepo: dashRepo}
}

// GetLastStudySession godoc
func (h *DashboardHandler) GetLastStudySession(c *gin.Context) {
	session, err := h.dashRepo.GetLastStudySession()
	if err != nil {
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   fmt.Sprintf("Failed to fetch last study session: %v", err),
		})
		return
	}

	// If no session exists, return empty session structure
	if session == nil {
		c.JSON(http.StatusOK, Response{
			Success: true,
			Data: map[string]interface{}{
				"id":                0,
				"group_id":          0,
				"group_name":        "",
				"study_activity_id": 0,
				"created_at":        time.Now(),
				"correct_count":     0,
				"total_words":       0,
			},
		})
		return
	}

	c.JSON(http.StatusOK, Response{
		Success: true,
		Data:    session,
	})
}

// GetStudyProgress godoc
func (h *DashboardHandler) GetStudyProgress(c *gin.Context) {
	progress, err := h.dashRepo.GetStudyProgress()
	if err != nil {
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   fmt.Sprintf("Failed to fetch study progress: %v", err),
		})
		return
	}

	c.JSON(http.StatusOK, Response{
		Success: true,
		Data:    progress,
	})
}

// GetQuickStats godoc
func (h *DashboardHandler) GetQuickStats(c *gin.Context) {
	stats, err := h.dashRepo.GetQuickStats()
	if err != nil {
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   fmt.Sprintf("Failed to fetch quick stats: %v", err),
		})
		return
	}

	c.JSON(http.StatusOK, Response{
		Success: true,
		Data:    stats,
	})
}

// ResetHistory godoc
func (h *DashboardHandler) ResetHistory(c *gin.Context) {
	if err := h.dashRepo.ResetHistory(); err != nil {
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   fmt.Sprintf("Failed to reset study history: %v", err),
		})
		return
	}

	c.JSON(http.StatusOK, Response{
		Success: true,
		Message: "Study history has been reset successfully",
	})
}

// FullReset godoc
func (h *DashboardHandler) FullReset(c *gin.Context) {
	if err := h.dashRepo.FullReset(); err != nil {
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   fmt.Sprintf("Failed to reset application data: %v", err),
		})
		return
	}

	c.JSON(http.StatusOK, Response{
		Success: true,
		Message: "Application data has been reset successfully",
		Data:    []interface{}{},
	})
}

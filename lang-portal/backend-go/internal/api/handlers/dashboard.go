package handlers

import (
	"net/http"

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
			Error:   "Failed to fetch last study session",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"data": session,
	})
}

// GetStudyProgress godoc
func (h *DashboardHandler) GetStudyProgress(c *gin.Context) {
	progress, err := h.dashRepo.GetStudyProgress()
	if err != nil {
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   "Failed to fetch study progress",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"data": progress,
	})
}

// GetQuickStats godoc
func (h *DashboardHandler) GetQuickStats(c *gin.Context) {
	stats, err := h.dashRepo.GetQuickStats()
	if err != nil {
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   "Failed to fetch quick stats",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"data": stats,
	})
}

// ResetHistory godoc
func (h *DashboardHandler) ResetHistory(c *gin.Context) {
	if err := h.dashRepo.ResetHistory(); err != nil {
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   "Failed to reset study history",
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
			Error:   "Failed to reset application data",
		})
		return
	}

	c.JSON(http.StatusOK, Response{
		Success: true,
		Message: "Application data has been reset successfully",
	})
}

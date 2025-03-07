package handlers

import (
	"database/sql"
	"fmt"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/lang-portal/backend-go/internal/database/repository"
	"github.com/lang-portal/backend-go/internal/errors"
	"github.com/lang-portal/backend-go/internal/models"
	"github.com/lang-portal/backend-go/internal/services"
)

type StudyHandler struct {
	studyRepo    *repository.StudyRepository
	studyService *services.StudyService
}

func NewStudyHandler(studyRepo *repository.StudyRepository, studyService *services.StudyService) *StudyHandler {
	return &StudyHandler{studyRepo: studyRepo, studyService: studyService}
}

// GetStudySessions godoc
func (h *StudyHandler) GetStudySessions(c *gin.Context) {
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "100"))

	sessions, total, err := h.studyRepo.GetStudySessions(page, limit)
	if err != nil {
		_ = c.Error(errors.NewServerError("Failed to fetch study sessions", err))
		return
	}

	response := models.PaginatedResponse{
		Data: sessions,
		Pagination: models.Pagination{
			CurrentPage:  page,
			TotalPages:   (total + limit - 1) / limit,
			TotalItems:   total,
			ItemsPerPage: limit,
		},
	}

	c.JSON(http.StatusOK, response)
}

// GetStudySession godoc
func (h *StudyHandler) GetStudySession(c *gin.Context) {
	id, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, Response{
			Success: false,
			Error:   "Invalid session ID",
		})
		return
	}

	session, err := h.studyRepo.GetStudySession(id)
	if err != nil {
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, Response{
				Success: false,
				Error:   "Study session not found",
			})
			return
		}
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   fmt.Sprintf("Failed to fetch study session: %v", err),
		})
		return
	}

	c.JSON(http.StatusOK, Response{
		Success: true,
		Data:    session,
	})
}

// CreateStudySession godoc
func (h *StudyHandler) CreateStudySession(c *gin.Context) {
	var request struct {
		GroupID         int64 `json:"group_id"`
		StudyActivityID int64 `json:"study_activity_id"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, Response{
			Success: false,
			Error:   "Invalid request data",
		})
		return
	}

	session, err := h.studyService.StartStudySession(request.GroupID, request.StudyActivityID)
	if err != nil {
		if err == services.ErrEmptyGroup {
			c.JSON(http.StatusBadRequest, Response{
				Success: false,
				Error:   err.Error(),
			})
			return
		}
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   fmt.Sprintf("Failed to create study session: %v", err),
		})
		return
	}

	c.JSON(http.StatusCreated, Response{
		Success: true,
		Data: gin.H{
			"study_session_id": session.ID,
			"group_id":         session.GroupID,
		},
	})
}

// ReviewWord godoc
func (h *StudyHandler) ReviewWord(c *gin.Context) {
	sessionID, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, Response{
			Success: false,
			Error:   "Invalid session ID",
		})
		return
	}

	wordID, err := strconv.ParseInt(c.Param("word_id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, Response{
			Success: false,
			Error:   "Invalid word ID",
		})
		return
	}

	var request struct {
		Correct bool `json:"correct" binding:"required"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, Response{
			Success: false,
			Error:   "Invalid request body",
		})
		return
	}

	err = h.studyRepo.CreateWordReview(wordID, sessionID, request.Correct)
	if err != nil {
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   "Failed to record word review",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"data": gin.H{
			"word_id":          wordID,
			"study_session_id": sessionID,
			"correct":          request.Correct,
		},
	})
}

// GetSessionWords godoc
func (h *StudyHandler) GetSessionWords(c *gin.Context) {
	id, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, Response{
			Success: false,
			Error:   "Invalid session ID",
		})
		return
	}

	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "100"))

	words, total, err := h.studyRepo.GetSessionWords(id, page, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   "Failed to fetch session words",
		})
		return
	}

	response := models.PaginatedResponse{
		Data: words,
		Pagination: models.Pagination{
			CurrentPage:  page,
			TotalPages:   (total + limit - 1) / limit,
			TotalItems:   total,
			ItemsPerPage: limit,
		},
	}

	c.JSON(http.StatusOK, response)
}

// GetStudyActivities godoc
func (h *StudyHandler) GetStudyActivities(c *gin.Context) {
	activities, err := h.studyRepo.GetStudyActivities()
	if err != nil {
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   fmt.Sprintf("Failed to fetch study activities: %v", err),
		})
		return
	}

	c.JSON(http.StatusOK, Response{
		Success: true,
		Data:    activities,
	})
}

// GetStudyActivity godoc
func (h *StudyHandler) GetStudyActivity(c *gin.Context) {
	id, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, Response{
			Success: false,
			Error:   "Invalid activity ID",
		})
		return
	}

	activity, err := h.studyRepo.GetStudyActivity(id)
	if err != nil {
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, Response{
				Success: false,
				Error:   "Study activity not found",
			})
			return
		}
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   fmt.Sprintf("Failed to fetch study activity: %v", err),
		})
		return
	}

	c.JSON(http.StatusOK, Response{
		Success: true,
		Data:    activity,
	})
}

// GetActivitySessions godoc
func (h *StudyHandler) GetActivitySessions(c *gin.Context) {
	id, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, Response{
			Success: false,
			Error:   "Invalid activity ID",
		})
		return
	}

	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "100"))

	sessions, total, err := h.studyRepo.GetActivitySessions(id, page, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   fmt.Sprintf("Failed to fetch activity sessions: %v", err),
		})
		return
	}

	response := models.PaginatedResponse{
		Data: sessions,
		Pagination: models.Pagination{
			CurrentPage:  page,
			TotalPages:   (total + limit - 1) / limit,
			TotalItems:   total,
			ItemsPerPage: limit,
		},
	}

	c.JSON(http.StatusOK, response)
}

// GetActivityLaunchData godoc
func (h *StudyHandler) GetActivityLaunchData(c *gin.Context) {
	id, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, Response{
			Success: false,
			Error:   "Invalid activity ID",
		})
		return
	}

	launchData, err := h.studyRepo.GetActivityLaunchData(id)
	if err != nil {
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, Response{
				Success: false,
				Error:   "Study activity not found",
			})
			return
		}
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   fmt.Sprintf("Failed to fetch launch data: %v", err),
		})
		return
	}

	c.JSON(http.StatusOK, Response{
		Success: true,
		Data:    launchData,
	})
}

// CreateStudyActivity godoc
// @Summary Create a new study activity
// @Description Create a new study activity for a group
// @Tags study
// @Accept json
// @Produce json
// @Param request body CreateStudyActivityRequest true "Study Activity Request"
// @Success 201 {object} Response
// @Router /api/study_activities [post]
func (h *StudyHandler) CreateStudyActivity(c *gin.Context) {
	var request struct {
		GroupID int64 `json:"group_id" binding:"required"`
	}

	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, Response{
			Success: false,
			Error:   "Invalid request: " + err.Error(),
		})
		return
	}

	// Use the handler's own repository instance
	activity, err := h.studyRepo.CreateStudyActivity(request.GroupID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   "Failed to create study activity: " + err.Error(),
		})
		return
	}

	// Create study session
	session, err := h.studyService.StartStudySession(request.GroupID, activity.ID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   "Failed to start study session: " + err.Error(),
		})
		return
	}

	c.JSON(http.StatusCreated, Response{
		Success: true,
		Data: gin.H{
			"study_activity":   activity,
			"study_session_id": session.ID,
		},
	})
}

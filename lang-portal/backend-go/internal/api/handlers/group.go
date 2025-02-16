package handlers

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/lang-portal/backend-go/internal/database/repository"
	"github.com/lang-portal/backend-go/internal/models"
)

type GroupHandler struct {
	groupRepo *repository.GroupRepository
}

func NewGroupHandler(groupRepo *repository.GroupRepository) *GroupHandler {
	return &GroupHandler{groupRepo: groupRepo}
}

// GetGroups godoc
func (h *GroupHandler) GetGroups(c *gin.Context) {
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "100"))

	groups, total, err := h.groupRepo.GetGroups(page, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   "Failed to fetch groups",
		})
		return
	}

	response := models.PaginatedResponse{
		Data: groups,
		Pagination: models.Pagination{
			CurrentPage:  page,
			TotalPages:   (total + limit - 1) / limit,
			TotalItems:   total,
			ItemsPerPage: limit,
		},
	}

	c.JSON(http.StatusOK, response)
}

// GetGroup godoc
func (h *GroupHandler) GetGroup(c *gin.Context) {
	id, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, Response{
			Success: false,
			Error:   "Invalid group ID",
		})
		return
	}

	group, err := h.groupRepo.GetGroup(id)
	if err != nil {
		c.JSON(http.StatusNotFound, Response{
			Success: false,
			Error:   "Group not found",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"data": group,
	})
}

// GetGroupWords godoc
func (h *GroupHandler) GetGroupWords(c *gin.Context) {
	id, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, Response{
			Success: false,
			Error:   "Invalid group ID",
		})
		return
	}

	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "100"))

	words, total, err := h.groupRepo.GetGroupWords(id, page, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   "Failed to fetch group words",
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

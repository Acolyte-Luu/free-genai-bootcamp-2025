package handlers

import (
	"fmt"
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
			Error:   fmt.Sprintf("Failed to fetch group words: %v", err),
		})
		return
	}

	c.JSON(http.StatusOK, Response{
		Success: true,
		Data: models.PaginatedResponse{
			Data: words,
			Pagination: models.Pagination{
				CurrentPage:  page,
				TotalPages:   (total + limit - 1) / limit,
				TotalItems:   total,
				ItemsPerPage: limit,
			},
		},
	})
}

// CreateGroup godoc
func (h *GroupHandler) CreateGroup(c *gin.Context) {
	var group models.Group
	if err := c.ShouldBindJSON(&group); err != nil {
		c.JSON(http.StatusBadRequest, Response{
			Success: false,
			Error:   "Invalid group data",
		})
		return
	}

	if err := h.groupRepo.CreateGroup(&group); err != nil {
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   "Failed to create group",
		})
		return
	}

	c.JSON(http.StatusCreated, Response{
		Success: true,
		Data:    group,
	})
}

// CreateGroupWords godoc
func (h *GroupHandler) CreateGroupWords(c *gin.Context) {
	groupID, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, Response{
			Success: false,
			Error:   "Invalid group ID",
		})
		return
	}

	var request struct {
		Words []models.Word `json:"words"`
	}
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, Response{
			Success: false,
			Error:   "Invalid word data",
		})
		return
	}

	createdWords, err := h.groupRepo.CreateGroupWords(groupID, request.Words)
	if err != nil {
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   fmt.Sprintf("Failed to create words: %v", err),
		})
		return
	}

	c.JSON(http.StatusCreated, Response{
		Success: true,
		Data:    createdWords,
	})
}

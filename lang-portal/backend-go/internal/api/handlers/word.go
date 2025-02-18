package handlers

import (
	"database/sql"
	"fmt"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/lang-portal/backend-go/internal/database/repository"
	"github.com/lang-portal/backend-go/internal/models"
)

type WordHandler struct {
	wordRepo *repository.WordRepository
}

func NewWordHandler(wordRepo *repository.WordRepository) *WordHandler {
	return &WordHandler{wordRepo: wordRepo}
}

// GetWords godoc
func (h *WordHandler) GetWords(c *gin.Context) {
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "100"))

	words, total, err := h.wordRepo.GetWords(page, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   "Failed to fetch words",
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

// GetWord godoc
func (h *WordHandler) GetWord(c *gin.Context) {
	id, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, Response{
			Success: false,
			Error:   "Invalid word ID",
		})
		return
	}

	word, err := h.wordRepo.GetWord(id)
	if err != nil {
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, Response{
				Success: false,
				Error:   "Word not found",
			})
			return
		}
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   fmt.Sprintf("Failed to fetch word: %v", err),
		})
		return
	}

	groups, err := h.wordRepo.GetWordGroups(id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   fmt.Sprintf("Failed to fetch word groups: %v", err),
		})
		return
	}

	c.JSON(http.StatusOK, Response{
		Success: true,
		Data:    word,
		Groups:  groups,
	})
}

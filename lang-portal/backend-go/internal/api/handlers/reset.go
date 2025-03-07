package handlers

import (
	"database/sql"
	"fmt"
	"io/ioutil"
	"net/http"

	"github.com/gin-gonic/gin"
)

type ResetHandler struct {
	db *sql.DB
}

func (h *ResetHandler) FullReset(c *gin.Context) {
	// Drop tables...

	// Then explicitly reinitialize the database
	err := h.initializeDatabase() // You'll need to create this method
	if err != nil {
		c.JSON(http.StatusInternalServerError, Response{
			Success: false,
			Error:   fmt.Sprintf("Failed to reinitialize database: %v", err),
		})
		return
	}

	c.JSON(http.StatusOK, Response{
		Success: true,
		Message: "Application data has been reset successfully",
		Data:    []interface{}{}, // Empty array
	})
}

func (h *ResetHandler) initializeDatabase() error {
	// Execute the consolidated migration script
	migrationSQL, err := ioutil.ReadFile("db/migrations/0001_init_complete.sql")
	if err != nil {
		return fmt.Errorf("failed to read migration file: %v", err)
	}

	// Execute the script
	_, err = h.db.Exec(string(migrationSQL))
	if err != nil {
		return fmt.Errorf("failed to initialize database: %v", err)
	}

	return nil
}

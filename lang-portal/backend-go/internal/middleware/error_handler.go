package middleware

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/lang-portal/backend-go/internal/errors"
)

func ErrorHandler() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Next()

		// Check if there are any errors
		if len(c.Errors) > 0 {
			err := c.Errors.Last().Err

			// Handle our custom AppError
			if appErr, ok := err.(*errors.AppError); ok {
				c.JSON(appErr.Code, gin.H{
					"success": false,
					"error": gin.H{
						"type":    appErr.Type,
						"message": appErr.Message,
					},
				})
				return
			}

			// Handle other errors
			c.JSON(http.StatusInternalServerError, gin.H{
				"success": false,
				"error": gin.H{
					"type":    "SERVER_ERROR",
					"message": "An unexpected error occurred",
				},
			})

			// Log the actual error for debugging
			fmt.Printf("Internal Server Error: %v\n", err)
		}
	}
}

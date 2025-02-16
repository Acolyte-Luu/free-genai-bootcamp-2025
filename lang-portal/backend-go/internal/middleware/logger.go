package middleware

import (
	"fmt"
	"time"

	"github.com/gin-gonic/gin"
)

func LoggerMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path

		c.Next()

		latency := time.Since(start)
		status := c.Writer.Status()

		logMsg := fmt.Sprintf("[%d] %s %s (%s)",
			status,
			c.Request.Method,
			path,
			latency,
		)

		if status >= 400 {
			c.Error(fmt.Errorf(logMsg)) // Log errors
		} else {
			fmt.Println(logMsg) // Log normal requests
		}
	}
}

package config

import (
	"log"
	"os"
)

const (
	TestDBPath = "config/database/test.db"
	DevDBPath  = "config/database/development.db"
)

func GetDBPath() string {
	env := os.Getenv("GO_ENV")
	var dbPath string

	if env == "test" {
		dbPath = TestDBPath
	} else {
		dbPath = DevDBPath
	}

	log.Printf("Using database path for %s environment: %s", env, dbPath)
	return dbPath
}

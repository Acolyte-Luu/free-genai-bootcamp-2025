package config

import "os"

const (
	TestDBPath = "config/database/test.db"
	DevDBPath  = "config/database/development.db"
)

func GetDBPath() string {
	if os.Getenv("GO_ENV") == "test" {
		return TestDBPath
	}
	return DevDBPath
}

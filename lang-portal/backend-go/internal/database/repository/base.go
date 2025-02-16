package repository

import (
	"database/sql"
)

// BaseRepository provides common functionality for all repositories
type BaseRepository struct {
	db *sql.DB
}

// NewBaseRepository creates a new base repository
func NewBaseRepository(db *sql.DB) BaseRepository {
	return BaseRepository{db: db}
}

// GetDB returns the database instance
func (r *BaseRepository) GetDB() *sql.DB {
	return r.db
}

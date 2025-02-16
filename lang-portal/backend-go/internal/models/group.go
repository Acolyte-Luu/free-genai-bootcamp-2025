package models

import "time"

type Group struct {
	ID        int64     `json:"id"`
	Name      string    `json:"name"`
	CreatedAt time.Time `json:"created_at"`
}

type GroupWithStats struct {
	Group
	TotalWordCount int `json:"total_word_count"`
}

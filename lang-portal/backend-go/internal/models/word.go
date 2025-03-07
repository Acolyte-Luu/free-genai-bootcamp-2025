package models

import (
	"encoding/json"
	"time"
)

type Word struct {
	ID        int64           `json:"id"`
	Japanese  string          `json:"japanese"`
	Romaji    string          `json:"romaji"`
	English   string          `json:"english"`
	Parts     json.RawMessage `json:"parts,omitempty"`
	CreatedAt time.Time       `json:"created_at"`
}

type WordWithStats struct {
	Word
	CorrectCount   int `json:"correct_count"`
	IncorrectCount int `json:"incorrect_count"`
}

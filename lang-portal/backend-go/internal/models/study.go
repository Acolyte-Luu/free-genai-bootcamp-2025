package models

import "time"

type StudySession struct {
	ID              int64     `json:"id"`
	GroupID         int64     `json:"group_id"`
	StudyActivityID int64     `json:"study_activity_id"`
	CreatedAt       time.Time `json:"created_at"`
}

// StudyActivity represents a study activity
type StudyActivity struct {
	ID           int64     `json:"id"`
	GroupID      int64     `json:"group_id"`
	StartedAt    time.Time `json:"started_at"`
	EndedAt      time.Time `json:"ended_at,omitempty"`
	Name         string    `json:"name,omitempty"`
	ThumbnailURL string    `json:"thumbnail_url,omitempty"`
	Description  string    `json:"description,omitempty"`
}

type WordReviewItem struct {
	WordID         int64     `json:"word_id"`
	StudySessionID int64     `json:"study_session_id"`
	Correct        bool      `json:"correct"`
	CreatedAt      time.Time `json:"created_at"`
}

type StudySessionResponse struct {
	ID               int64     `json:"id"`
	ActivityName     string    `json:"activity_name"`
	GroupName        string    `json:"group_name"`
	StartTime        time.Time `json:"start_time"`
	EndTime          time.Time `json:"end_time"`
	ReviewItemsCount int       `json:"review_items_count"`
}

// ActivityLaunchData represents data needed to launch a study activity
type ActivityLaunchData struct {
	Activity StudyActivity `json:"activity"`
	Groups   []Group       `json:"groups"`
}

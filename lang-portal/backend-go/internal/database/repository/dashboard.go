package repository

import (
	"database/sql"
	"time"
)

type DashboardRepository struct {
	BaseRepository
}

func NewDashboardRepository(db *sql.DB) *DashboardRepository {
	return &DashboardRepository{BaseRepository: NewBaseRepository(db)}
}

type LastStudySession struct {
	ID              int64     `json:"id"`
	GroupID         int64     `json:"group_id"`
	GroupName       string    `json:"group_name"`
	StudyActivityID int64     `json:"study_activity_id"`
	CreatedAt       time.Time `json:"created_at"`
	CorrectCount    int       `json:"correct_count"`
	TotalWords      int       `json:"total_words"`
}

func (r *DashboardRepository) GetLastStudySession() (*LastStudySession, error) {
	var session LastStudySession
	err := r.db.QueryRow(`
		SELECT 
			ss.id,
			ss.group_id,
			g.name as group_name,
			ss.study_activity_id,
			ss.created_at,
			COUNT(CASE WHEN wri.correct THEN 1 END) as correct_count,
			COUNT(wri.word_id) as total_words
		FROM study_sessions ss
		JOIN groups g ON ss.group_id = g.id
		LEFT JOIN word_review_items wri ON ss.id = wri.study_session_id
		GROUP BY ss.id
		ORDER BY ss.created_at DESC
		LIMIT 1
	`).Scan(
		&session.ID,
		&session.GroupID,
		&session.GroupName,
		&session.StudyActivityID,
		&session.CreatedAt,
		&session.CorrectCount,
		&session.TotalWords,
	)
	if err != nil {
		return nil, err
	}

	return &session, nil
}

type StudyProgress struct {
	TotalWords        int `json:"total_words"`
	TotalWordsStudied int `json:"total_words_studied"`
}

func (r *DashboardRepository) GetStudyProgress() (*StudyProgress, error) {
	var progress StudyProgress
	err := r.db.QueryRow(`
		SELECT 
			(SELECT COUNT(*) FROM words) as total_words,
			COUNT(DISTINCT word_id) as total_words_studied
		FROM word_review_items
	`).Scan(&progress.TotalWords, &progress.TotalWordsStudied)
	if err != nil {
		return nil, err
	}

	return &progress, nil
}

type QuickStats struct {
	TotalStudySessions int     `json:"total_study_sessions"`
	ActiveGroups       int     `json:"active_groups"`
	StudyStreak        int     `json:"study_streak"`
	SuccessPercentage  float64 `json:"success_percentage"`
}

func (r *DashboardRepository) GetQuickStats() (*QuickStats, error) {
	var stats QuickStats
	err := r.db.QueryRow(`
		WITH daily_sessions AS (
			SELECT DATE(created_at) as study_date
			FROM study_sessions
			GROUP BY DATE(created_at)
			ORDER BY study_date DESC
		)
		SELECT 
			(SELECT COUNT(*) FROM study_sessions) as total_study_sessions,
			(SELECT COUNT(*) FROM groups WHERE id IN (
				SELECT DISTINCT group_id FROM study_sessions
				WHERE created_at >= datetime('now', '-30 days')
			)) as active_groups,
			(SELECT COUNT(*) FROM daily_sessions
			WHERE study_date >= DATE('now', '-' || (
				SELECT COUNT(*) FROM daily_sessions WHERE study_date >= DATE('now', '-30 days')
			) || ' days')) as study_streak,
			ROUND(CAST(SUM(CASE WHEN correct THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 2) as success_percentage
		FROM word_review_items
		WHERE created_at >= datetime('now', '-30 days')
	`).Scan(
		&stats.TotalStudySessions,
		&stats.ActiveGroups,
		&stats.StudyStreak,
		&stats.SuccessPercentage,
	)
	if err != nil {
		return nil, err
	}

	return &stats, nil
}

func (r *DashboardRepository) ResetHistory() error {
	tx, err := r.db.Begin()
	if err != nil {
		return err
	}

	_, err = tx.Exec("DELETE FROM word_review_items")
	if err != nil {
		tx.Rollback()
		return err
	}

	_, err = tx.Exec("DELETE FROM study_sessions")
	if err != nil {
		tx.Rollback()
		return err
	}

	return tx.Commit()
}

func (r *DashboardRepository) FullReset() error {
	tx, err := r.db.Begin()
	if err != nil {
		return err
	}

	tables := []string{
		"word_review_items",
		"study_sessions",
		"words_groups",
		"words",
		"groups",
	}

	for _, table := range tables {
		_, err = tx.Exec("DELETE FROM " + table)
		if err != nil {
			tx.Rollback()
			return err
		}
	}

	return tx.Commit()
}

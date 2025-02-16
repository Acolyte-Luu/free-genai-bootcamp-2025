package repository

import (
	"database/sql"
	"time"

	"github.com/lang-portal/backend-go/internal/models"
)

type StudyRepository struct {
	BaseRepository
}

func NewStudyRepository(db *sql.DB) *StudyRepository {
	return &StudyRepository{BaseRepository: NewBaseRepository(db)}
}

func (r *StudyRepository) CreateStudySession(groupID, studyActivityID int64) (*models.StudySession, error) {
	session := &models.StudySession{
		GroupID:         groupID,
		StudyActivityID: studyActivityID,
		CreatedAt:       time.Now(),
	}

	result, err := r.db.Exec(`
		INSERT INTO study_sessions (group_id, study_activity_id, created_at)
		VALUES (?, ?, ?)
	`,
		session.GroupID,
		session.StudyActivityID,
		session.CreatedAt,
	)
	if err != nil {
		return nil, err
	}

	id, err := result.LastInsertId()
	if err != nil {
		return nil, err
	}

	session.ID = id
	return session, nil
}

func (r *StudyRepository) GetStudySession(id int64) (*models.StudySessionResponse, error) {
	var session models.StudySessionResponse
	err := r.db.QueryRow(`
		SELECT 
			ss.id,
			g.name as group_name,
			'Flashcards' as activity_name,
			ss.created_at as start_time,
			ss.created_at as end_time,
			COUNT(wri.word_id) as review_items_count
		FROM study_sessions ss
		JOIN groups g ON ss.group_id = g.id
		LEFT JOIN word_review_items wri ON ss.id = wri.study_session_id
		WHERE ss.id = ?
		GROUP BY ss.id
	`, id).Scan(
		&session.ID,
		&session.GroupName,
		&session.ActivityName,
		&session.StartTime,
		&session.EndTime,
		&session.ReviewItemsCount,
	)
	if err != nil {
		return nil, err
	}

	return &session, nil
}

func (r *StudyRepository) CreateWordReview(wordID, sessionID int64, correct bool) error {
	_, err := r.db.Exec(`
		INSERT INTO word_review_items (word_id, study_session_id, correct, created_at)
		VALUES (?, ?, ?, ?)
	`,
		wordID,
		sessionID,
		correct,
		time.Now(),
	)
	return err
}

type ReviewedWord struct {
	Japanese   string    `json:"japanese"`
	Romaji     string    `json:"romaji"`
	English    string    `json:"english"`
	Correct    bool      `json:"correct"`
	ReviewedAt time.Time `json:"reviewed_at"`
}

func (r *StudyRepository) GetSessionWords(sessionID int64, page, limit int) ([]ReviewedWord, int, error) {
	offset := (page - 1) * limit

	// Get total count
	var total int
	err := r.db.QueryRow(`
		SELECT COUNT(*) 
		FROM word_review_items 
		WHERE study_session_id = ?
	`, sessionID).Scan(&total)
	if err != nil {
		return nil, 0, err
	}

	// Get reviewed words
	rows, err := r.db.Query(`
		SELECT 
			w.japanese,
			w.romaji,
			w.english,
			wri.correct,
			wri.created_at as reviewed_at
		FROM word_review_items wri
		JOIN words w ON wri.word_id = w.id
		WHERE wri.study_session_id = ?
		ORDER BY wri.created_at
		LIMIT ? OFFSET ?
	`, sessionID, limit, offset)
	if err != nil {
		return nil, 0, err
	}
	defer rows.Close()

	var words []ReviewedWord
	for rows.Next() {
		var w ReviewedWord
		err := rows.Scan(
			&w.Japanese,
			&w.Romaji,
			&w.English,
			&w.Correct,
			&w.ReviewedAt,
		)
		if err != nil {
			return nil, 0, err
		}
		words = append(words, w)
	}

	return words, total, nil
}

func (r *StudyRepository) GetStudySessions(page, limit int) ([]models.StudySessionResponse, int, error) {
	offset := (page - 1) * limit

	// Get total count
	var total int
	err := r.db.QueryRow(`
		SELECT COUNT(*) 
		FROM study_sessions
	`).Scan(&total)
	if err != nil {
		return nil, 0, err
	}

	// Get sessions with stats
	rows, err := r.db.Query(`
		SELECT 
			ss.id,
			g.name as group_name,
			'Flashcards' as activity_name,
			ss.created_at as start_time,
			ss.created_at as end_time,
			COUNT(wri.word_id) as review_items_count
		FROM study_sessions ss
		JOIN groups g ON ss.group_id = g.id
		LEFT JOIN word_review_items wri ON ss.id = wri.study_session_id
		GROUP BY ss.id
		ORDER BY ss.created_at DESC
		LIMIT ? OFFSET ?
	`, limit, offset)
	if err != nil {
		return nil, 0, err
	}
	defer rows.Close()

	var sessions []models.StudySessionResponse
	for rows.Next() {
		var s models.StudySessionResponse
		err := rows.Scan(
			&s.ID,
			&s.GroupName,
			&s.ActivityName,
			&s.StartTime,
			&s.EndTime,
			&s.ReviewItemsCount,
		)
		if err != nil {
			return nil, 0, err
		}
		sessions = append(sessions, s)
	}

	return sessions, total, nil
}

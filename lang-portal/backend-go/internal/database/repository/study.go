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

func (r *StudyRepository) GetStudyActivityById(id int64) (*models.StudyActivity, error) {
	if id == 1 {
		return &models.StudyActivity{
			ID:           1,
			Name:         "Flashcards",
			ThumbnailURL: "/images/flashcards.png",
			Description:  "Practice vocabulary with flashcards",
		}, nil
	}

	return nil, sql.ErrNoRows
}

func (r *StudyRepository) GetActivitySessions(activityID int64, page, limit int) ([]models.StudySessionResponse, int, error) {
	offset := (page - 1) * limit

	// Get total count
	var total int
	err := r.db.QueryRow(`
		SELECT COUNT(*) 
		FROM study_sessions
		WHERE study_activity_id = ?
	`, activityID).Scan(&total)
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
		WHERE ss.study_activity_id = ?
		GROUP BY ss.id
		ORDER BY ss.created_at DESC
		LIMIT ? OFFSET ?
	`, activityID, limit, offset)
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

func (r *StudyRepository) GetGroupSessions(groupID int64, page, limit int) ([]models.StudySessionResponse, int, error) {
	offset := (page - 1) * limit

	// Get total count
	var total int
	err := r.db.QueryRow(`
		SELECT COUNT(*) 
		FROM study_sessions
		WHERE group_id = ?
	`, groupID).Scan(&total)
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
		WHERE ss.group_id = ?
		GROUP BY ss.id
		ORDER BY ss.created_at DESC
		LIMIT ? OFFSET ?
	`, groupID, limit, offset)
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

func (r *StudyRepository) GetActivityLaunchData(activityID int64) (*models.ActivityLaunchData, error) {
	activity, err := r.GetStudyActivityById(activityID)
	if err != nil {
		return nil, err
	}

	rows, err := r.db.Query(`SELECT id, name FROM groups ORDER BY name`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var groups []models.Group
	for rows.Next() {
		var g models.Group
		if err := rows.Scan(&g.ID, &g.Name); err != nil {
			return nil, err
		}
		groups = append(groups, g)
	}

	return &models.ActivityLaunchData{
		Activity: *activity,
		Groups:   groups,
	}, nil
}

func (r *StudyRepository) GetStudyActivities() ([]models.StudyActivity, error) {
	rows, err := r.db.Query(`
		SELECT id, name, thumbnail_url, description 
		FROM study_activities
		ORDER BY id
	`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var activities []models.StudyActivity
	for rows.Next() {
		var activity models.StudyActivity
		if err := rows.Scan(
			&activity.ID,
			&activity.Name,
			&activity.ThumbnailURL,
			&activity.Description,
		); err != nil {
			return nil, err
		}
		activities = append(activities, activity)
	}

	return activities, nil
}

func (r *StudyRepository) GetStudyActivity(id int64) (*models.StudyActivity, error) {
	var activity models.StudyActivity
	err := r.db.QueryRow(`
		SELECT id, name, thumbnail_url, description 
		FROM study_activities 
		WHERE id = ?
	`, id).Scan(
		&activity.ID,
		&activity.Name,
		&activity.ThumbnailURL,
		&activity.Description,
	)
	if err != nil {
		return nil, err
	}

	return &activity, nil
}

// CreateStudyActivity creates a new study activity
func (r *StudyRepository) CreateStudyActivity(groupID int64) (*models.StudyActivity, error) {
	activity := &models.StudyActivity{
		GroupID:   groupID,
		StartedAt: time.Now(),
	}

	result, err := r.db.Exec(`
		INSERT INTO study_activities (group_id, started_at)
		VALUES (?, ?)
	`, activity.GroupID, activity.StartedAt)

	if err != nil {
		return nil, err
	}

	id, err := result.LastInsertId()
	if err != nil {
		return nil, err
	}

	activity.ID = id
	return activity, nil
}

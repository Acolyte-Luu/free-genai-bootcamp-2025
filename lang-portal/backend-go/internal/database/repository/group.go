package repository

import (
	"database/sql"
	"fmt"
	"log"
	"time"

	"github.com/lang-portal/backend-go/internal/models"
)

type GroupRepository struct {
	BaseRepository
}

func NewGroupRepository(db *sql.DB) *GroupRepository {
	return &GroupRepository{BaseRepository: NewBaseRepository(db)}
}

func (r *GroupRepository) GetGroups(page, limit int) ([]models.Group, int, error) {
	offset := (page - 1) * limit

	// Get total count
	var total int
	err := r.db.QueryRow("SELECT COUNT(*) FROM groups").Scan(&total)
	if err != nil {
		return nil, 0, err
	}

	// Get groups
	rows, err := r.db.Query(`
		SELECT id, name, created_at 
		FROM groups 
		ORDER BY id
		LIMIT ? OFFSET ?
	`, limit, offset)
	if err != nil {
		return nil, 0, err
	}
	defer rows.Close()

	var groups []models.Group
	for rows.Next() {
		var g models.Group
		err := rows.Scan(&g.ID, &g.Name, &g.CreatedAt)
		if err != nil {
			return nil, 0, err
		}
		groups = append(groups, g)
	}

	return groups, total, nil
}

func (r *GroupRepository) GetGroup(id int64) (*models.GroupWithStats, error) {
	var group models.GroupWithStats
	err := r.db.QueryRow(`
		SELECT 
			g.id, 
			g.name, 
			g.created_at,
			COALESCE(COUNT(wg.word_id), 0) as total_word_count
		FROM groups g
		LEFT JOIN words_groups wg ON g.id = wg.group_id
		WHERE g.id = ?
		GROUP BY g.id
	`, id).Scan(
		&group.ID,
		&group.Name,
		&group.CreatedAt,
		&group.TotalWordCount,
	)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("group not found with id: %d", id)
		}
		return nil, fmt.Errorf("failed to fetch group: %v", err)
	}

	return &group, nil
}

type WordWithStats struct {
	Japanese       string `json:"japanese"`
	Romaji         string `json:"romaji"`
	English        string `json:"english"`
	CorrectCount   int    `json:"correct_count"`
	IncorrectCount int    `json:"incorrect_count"`
}

func (r *GroupRepository) GetGroupWords(groupID int64, page, limit int) ([]WordWithStats, int, error) {
	offset := (page - 1) * limit

	// Get total count
	var total int
	err := r.db.QueryRow(`
		SELECT COUNT(*) 
		FROM words_groups 
		WHERE group_id = ?
	`, groupID).Scan(&total)
	if err != nil {
		log.Printf("Error getting total count: %v", err)
		return nil, 0, err
	}
	log.Printf("Total words in group %d: %d", groupID, total)

	// Get group words with stats
	query := `
		SELECT 
			w.japanese,
			w.romaji,
			w.english,
			COALESCE(SUM(CASE WHEN wri.correct THEN 1 ELSE 0 END), 0) as correct_count,
			COALESCE(SUM(CASE WHEN NOT wri.correct THEN 1 ELSE 0 END), 0) as incorrect_count
		FROM words w
		JOIN words_groups wg ON w.id = wg.word_id
		LEFT JOIN word_review_items wri ON w.id = wri.word_id
		WHERE wg.group_id = ?
		GROUP BY w.id
		ORDER BY w.id
		LIMIT ? OFFSET ?
	`

	rows, err := r.db.Query(query, groupID, limit, offset)
	if err != nil {
		return nil, 0, err
	}
	defer rows.Close()

	var words []WordWithStats
	for rows.Next() {
		var w WordWithStats
		err := rows.Scan(
			&w.Japanese,
			&w.Romaji,
			&w.English,
			&w.CorrectCount,
			&w.IncorrectCount,
		)
		if err != nil {
			return nil, 0, err
		}
		words = append(words, w)
	}

	return words, total, nil
}

func (r *GroupRepository) CreateGroup(group *models.Group) error {
	group.CreatedAt = time.Now()
	result, err := r.db.Exec(`
		INSERT INTO groups (name, created_at)
		VALUES (?, ?)
	`,
		group.Name,
		group.CreatedAt,
	)
	if err != nil {
		return err
	}

	id, err := result.LastInsertId()
	if err != nil {
		return err
	}

	group.ID = id
	return nil
}

func (r *GroupRepository) CreateGroupWords(groupID int64, words []models.Word) ([]models.Word, error) {
	tx, err := r.db.Begin()
	if err != nil {
		return nil, err
	}
	defer tx.Rollback()

	createdWords := make([]models.Word, 0, len(words))
	for _, word := range words {
		word.CreatedAt = time.Now()
		result, err := tx.Exec(`
			INSERT INTO words (japanese, romaji, english, created_at)
			VALUES (?, ?, ?, ?)
		`, word.Japanese, word.Romaji, word.English, word.CreatedAt)
		if err != nil {
			return nil, err
		}

		wordID, err := result.LastInsertId()
		if err != nil {
			return nil, err
		}
		word.ID = wordID

		_, err = tx.Exec(`
			INSERT INTO words_groups (word_id, group_id, created_at)
			VALUES (?, ?, ?)
		`, wordID, groupID, time.Now())
		if err != nil {
			return nil, err
		}

		createdWords = append(createdWords, word)
	}

	if err := tx.Commit(); err != nil {
		return nil, err
	}

	return createdWords, nil
}

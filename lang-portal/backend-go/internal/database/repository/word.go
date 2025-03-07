package repository

import (
	"database/sql"
	"time"

	"github.com/lang-portal/backend-go/internal/models"
)

type WordRepository struct {
	BaseRepository
}

func NewWordRepository(db *sql.DB) *WordRepository {
	return &WordRepository{BaseRepository: NewBaseRepository(db)}
}

func (r *WordRepository) GetWords(page, limit int) ([]models.WordWithStats, int, error) {
	offset := (page - 1) * limit

	// Get total count
	var total int
	err := r.db.QueryRow("SELECT COUNT(*) FROM words").Scan(&total)
	if err != nil {
		return nil, 0, err
	}

	// Get words with stats
	query := `
		SELECT 
			w.id,
			w.japanese,
			w.romaji,
			w.english,
			w.created_at,
			COALESCE(SUM(CASE WHEN wri.correct THEN 1 ELSE 0 END), 0) as correct_count,
			COALESCE(SUM(CASE WHEN NOT wri.correct THEN 1 ELSE 0 END), 0) as incorrect_count
		FROM words w
		LEFT JOIN word_review_items wri ON w.id = wri.word_id
		GROUP BY w.id
		ORDER BY w.id
		LIMIT ? OFFSET ?
	`

	rows, err := r.db.Query(query, limit, offset)
	if err != nil {
		return nil, 0, err
	}
	defer rows.Close()

	var words []models.WordWithStats
	for rows.Next() {
		var w models.WordWithStats
		err := rows.Scan(
			&w.ID,
			&w.Japanese,
			&w.Romaji,
			&w.English,
			&w.CreatedAt,
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

func (r *WordRepository) GetWord(id int64) (*models.Word, error) {
	var word models.Word
	err := r.db.QueryRow(`
		SELECT id, japanese, romaji, english, created_at 
		FROM words 
		WHERE id = ?
	`, id).Scan(
		&word.ID,
		&word.Japanese,
		&word.Romaji,
		&word.English,
		&word.CreatedAt,
	)
	if err != nil {
		return nil, err
	}

	return &word, nil
}

func (r *WordRepository) GetWordGroups(wordID int64) ([]models.Group, error) {
	rows, err := r.db.Query(`
		SELECT g.id, g.name, g.created_at
		FROM groups g
		JOIN word_groups wg ON g.id = wg.group_id
		WHERE wg.word_id = ?
	`, wordID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var groups []models.Group
	for rows.Next() {
		var g models.Group
		err := rows.Scan(&g.ID, &g.Name, &g.CreatedAt)
		if err != nil {
			return nil, err
		}
		groups = append(groups, g)
	}

	return groups, nil
}

func (r *WordRepository) CreateWord(word *models.Word) error {
	word.CreatedAt = time.Now()
	result, err := r.db.Exec(`
		INSERT INTO words (japanese, romaji, english, created_at)
		VALUES (?, ?, ?, CURRENT_TIMESTAMP)
	`, word.Japanese, word.Romaji, word.English)
	if err != nil {
		return err
	}

	id, err := result.LastInsertId()
	if err != nil {
		return err
	}

	word.ID = id
	return nil
}

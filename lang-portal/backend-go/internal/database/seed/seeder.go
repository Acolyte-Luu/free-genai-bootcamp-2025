package seed

import (
	"database/sql"
	"fmt"
)

type Seeder struct {
	db *sql.DB
}

func NewSeeder(db *sql.DB) *Seeder {
	return &Seeder{db: db}
}

func (s *Seeder) Seed(data *SeedData) error {
	tx, err := s.db.Begin()
	if err != nil {
		return fmt.Errorf("failed to start transaction: %v", err)
	}

	for _, group := range data.Groups {
		// Insert group
		result, err := tx.Exec(`
			INSERT INTO groups (name, created_at)
			VALUES (?, CURRENT_TIMESTAMP)
		`, group.Name)
		if err != nil {
			tx.Rollback()
			return fmt.Errorf("failed to insert group %s: %v", group.Name, err)
		}

		groupID, err := result.LastInsertId()
		if err != nil {
			tx.Rollback()
			return fmt.Errorf("failed to get group ID for %s: %v", group.Name, err)
		}

		// Insert words and create word-group associations
		for _, word := range group.Words {
			// Insert word
			result, err := tx.Exec(`
				INSERT INTO words (japanese, romaji, english, created_at)
				VALUES (?, ?, ?, CURRENT_TIMESTAMP)
			`, word.Japanese, word.Romaji, word.English)
			if err != nil {
				tx.Rollback()
				return fmt.Errorf("failed to insert word %s: %v", word.Japanese, err)
			}

			wordID, err := result.LastInsertId()
			if err != nil {
				tx.Rollback()
				return fmt.Errorf("failed to get word ID for %s: %v", word.Japanese, err)
			}

			// Create word-group association
			_, err = tx.Exec(`
				INSERT INTO words_groups (word_id, group_id, created_at)
				VALUES (?, ?, CURRENT_TIMESTAMP)
			`, wordID, groupID)
			if err != nil {
				tx.Rollback()
				return fmt.Errorf("failed to associate word %s with group %s: %v", word.Japanese, group.Name, err)
			}
		}
	}

	return tx.Commit()
}

package seed

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"path/filepath"
	"time"
)

// SeedData represents the structure of seed files with nested groups
type SeedData struct {
	Groups []struct {
		Name  string `json:"name"`
		Words []struct {
			Japanese string `json:"japanese"`
			Romaji   string `json:"romaji"`
			English  string `json:"english"`
		} `json:"words"`
	} `json:"groups"`
}

// WordData represents the structure for direct word arrays
type WordData struct {
	Kanji   string          `json:"kanji"`
	Romaji  string          `json:"romaji"`
	English string          `json:"english"`
	Parts   json.RawMessage `json:"parts"`
}

// LoadSeedData loads seed data from JSON files into the database
func LoadSeedData(db *sql.DB, seedsDir string) error {
	// Load study activities first
	if err := seedStudyActivities(db); err != nil {
		return fmt.Errorf("failed to seed study activities: %v", err)
	}

	// Then load vocabulary
	return seedVocabulary(db, seedsDir)
}

// seedStudyActivities inserts default study activities
func seedStudyActivities(db *sql.DB) error {
	// Check if we already have study activities
	var count int
	err := db.QueryRow("SELECT COUNT(*) FROM study_activities").Scan(&count)
	if err != nil {
		return err
	}

	// If we already have data, skip
	if count > 0 {
		log.Println("Study activities already exist, skipping seed")
		return nil
	}

	// Define default activities
	activities := []struct {
		Name         string
		ThumbnailURL string
		Description  string
	}{
		{
			Name:         "Flashcards",
			ThumbnailURL: "/images/flashcards.png",
			Description:  "Practice vocabulary with flashcards",
		},
		{
			Name:         "Writing Practice",
			ThumbnailURL: "/images/writing.png",
			Description:  "Practice writing Japanese characters",
		},
		{
			Name:         "Reading Exercise",
			ThumbnailURL: "/images/reading.png",
			Description:  "Improve reading comprehension",
		},
		{
			Name:         "Listening Practice",
			ThumbnailURL: "/images/listening.png",
			Description:  "Enhance listening skills with audio exercises",
		},
		{
			Name:         "Speaking Drill",
			ThumbnailURL: "/images/speaking.png",
			Description:  "Practice pronunciation and speaking",
		},
	}

	// Begin transaction
	tx, err := db.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback()

	// Insert each activity
	for _, a := range activities {
		_, err := tx.Exec(`
			INSERT INTO study_activities (name, thumbnail_url, description, created_at)
			VALUES (?, ?, ?, ?)
		`, a.Name, a.ThumbnailURL, a.Description, time.Now())
		if err != nil {
			return err
		}
	}

	return tx.Commit()
}

// seedVocabulary loads vocabulary data from JSON files
func seedVocabulary(db *sql.DB, seedsDir string) error {
	// Get all JSON files in the seeds directory
	files, err := filepath.Glob(filepath.Join(seedsDir, "*.json"))
	if err != nil {
		return fmt.Errorf("failed to read seed directory: %v", err)
	}

	for _, file := range files {
		log.Printf("Loading seed data from %s", file)

		// Read the file
		jsonData, err := ioutil.ReadFile(file)
		if err != nil {
			return fmt.Errorf("failed to read seed file %s: %v", file, err)
		}

		// Try to determine the JSON format
		tx, err := db.Begin()
		if err != nil {
			return err
		}
		defer tx.Rollback()

		// First, check if this is a direct word array (adjectives.json, verbs.json format)
		var wordArray []WordData
		err1 := json.Unmarshal(jsonData, &wordArray)

		if err1 == nil && len(wordArray) > 0 {
			// This is the direct word array format
			// Extract group name from filename
			groupName := filepath.Base(file)
			groupName = groupName[:len(groupName)-5] // Remove .json
			log.Printf("Processing file as word array with group name: %s", groupName)

			// Create or get the group
			var groupID int64
			err := tx.QueryRow("SELECT id FROM groups WHERE name = ?", groupName).Scan(&groupID)
			if err == sql.ErrNoRows {
				// Create the group
				result, err := tx.Exec(`
					INSERT INTO groups (name, created_at)
					VALUES (?, ?)
				`, groupName, time.Now())
				if err != nil {
					return fmt.Errorf("failed to create group %s: %v", groupName, err)
				}
				groupID, _ = result.LastInsertId()
				log.Printf("Created group: %s (ID: %d)", groupName, groupID)
			} else if err != nil {
				return err
			} else {
				log.Printf("Group %s already exists, using ID: %d", groupName, groupID)
			}

			// Process each word
			for _, word := range wordArray {
				// Check if word already exists
				var wordID int64
				err := tx.QueryRow(`
					SELECT id FROM words 
					WHERE japanese = ? AND romaji = ? AND english = ?
				`, word.Kanji, word.Romaji, word.English).Scan(&wordID)

				if err == sql.ErrNoRows {
					// Create the word with parts data
					result, err := tx.Exec(`
						INSERT INTO words (japanese, romaji, english, parts, created_at)
						VALUES (?, ?, ?, ?, ?)
					`, word.Kanji, word.Romaji, word.English, word.Parts, time.Now())
					if err != nil {
						return fmt.Errorf("failed to create word %s: %v", word.Kanji, err)
					}
					wordID, _ = result.LastInsertId()
					log.Printf("Created word: %s (ID: %d)", word.Kanji, wordID)
				} else if err != nil {
					return err
				} else {
					log.Printf("Word %s already exists, using ID: %d", word.Kanji, wordID)
				}

				// Link word to group (if not already linked)
				var linkExists bool
				err = tx.QueryRow(`
					SELECT 1 FROM word_groups 
					WHERE word_id = ? AND group_id = ?
				`, wordID, groupID).Scan(&linkExists)

				if err == sql.ErrNoRows {
					// Create the link
					_, err := tx.Exec(`
						INSERT INTO word_groups (word_id, group_id, created_at)
						VALUES (?, ?, ?)
					`, wordID, groupID, time.Now())
					if err != nil {
						return fmt.Errorf("failed to link word %d to group %d: %v", wordID, groupID, err)
					}
					log.Printf("Linked word %d to group %d", wordID, groupID)
				} else if err != nil {
					return err
				} else {
					log.Printf("Word %d already linked to group %d", wordID, groupID)
				}
			}

		} else {
			// Try the nested format (animals.json, greetings.json format)
			var data SeedData
			err2 := json.Unmarshal(jsonData, &data)
			if err2 != nil {
				return fmt.Errorf("failed to parse seed file %s in either format: %v and %v", file, err1, err2)
			}

			// Process each group in the nested format
			for _, group := range data.Groups {
				// Check if group already exists
				var groupID int64
				err := tx.QueryRow("SELECT id FROM groups WHERE name = ?", group.Name).Scan(&groupID)
				if err == sql.ErrNoRows {
					// Create the group
					result, err := tx.Exec(`
						INSERT INTO groups (name, created_at)
						VALUES (?, ?)
					`, group.Name, time.Now())
					if err != nil {
						return fmt.Errorf("failed to create group %s: %v", group.Name, err)
					}
					groupID, _ = result.LastInsertId()
					log.Printf("Created group: %s (ID: %d)", group.Name, groupID)
				} else if err != nil {
					return err
				} else {
					log.Printf("Group %s already exists, using ID: %d", group.Name, groupID)
				}

				// Add words to the group
				for _, word := range group.Words {
					// Check if word already exists
					var wordID int64
					err := tx.QueryRow(`
						SELECT id FROM words 
						WHERE japanese = ? AND romaji = ? AND english = ?
					`, word.Japanese, word.Romaji, word.English).Scan(&wordID)

					if err == sql.ErrNoRows {
						// Create the word without parts data
						result, err := tx.Exec(`
							INSERT INTO words (japanese, romaji, english, created_at)
							VALUES (?, ?, ?, ?)
						`, word.Japanese, word.Romaji, word.English, time.Now())
						if err != nil {
							return fmt.Errorf("failed to create word %s: %v", word.Japanese, err)
						}
						wordID, _ = result.LastInsertId()
						log.Printf("Created word: %s (ID: %d)", word.Japanese, wordID)
					} else if err != nil {
						return err
					} else {
						log.Printf("Word %s already exists, using ID: %d", word.Japanese, wordID)
					}

					// Link word to group (if not already linked)
					var linkExists bool
					err = tx.QueryRow(`
						SELECT 1 FROM word_groups 
						WHERE word_id = ? AND group_id = ?
					`, wordID, groupID).Scan(&linkExists)

					if err == sql.ErrNoRows {
						// Create the link
						_, err := tx.Exec(`
							INSERT INTO word_groups (word_id, group_id, created_at)
							VALUES (?, ?, ?)
						`, wordID, groupID, time.Now())
						if err != nil {
							return fmt.Errorf("failed to link word %d to group %d: %v", wordID, groupID, err)
						}
						log.Printf("Linked word %d to group %d", wordID, groupID)
					} else if err != nil {
						return err
					} else {
						log.Printf("Word %d already linked to group %d", wordID, groupID)
					}
				}
			}
		}

		// Commit transaction for this file
		if err := tx.Commit(); err != nil {
			return fmt.Errorf("failed to commit transaction: %v", err)
		}

		log.Printf("Successfully loaded seed data from %s", file)
	}

	return nil
}

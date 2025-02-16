package seed

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

type WordSeed struct {
	Japanese string `json:"japanese"`
	Romaji   string `json:"romaji"`
	English  string `json:"english"`
}

type GroupSeed struct {
	Name  string     `json:"name"`
	Words []WordSeed `json:"words"`
}

type SeedData struct {
	Groups []GroupSeed `json:"groups"`
}

func LoadSeedData(seedDir string) (*SeedData, error) {
	files, err := filepath.Glob(filepath.Join(seedDir, "*.json"))
	if err != nil {
		return nil, fmt.Errorf("failed to read seed directory: %v", err)
	}

	allData := &SeedData{}
	for _, file := range files {
		data, err := os.ReadFile(file)
		if err != nil {
			return nil, fmt.Errorf("failed to read seed file %s: %v", file, err)
		}

		var seedData SeedData
		if err := json.Unmarshal(data, &seedData); err != nil {
			return nil, fmt.Errorf("failed to parse seed file %s: %v", file, err)
		}

		allData.Groups = append(allData.Groups, seedData.Groups...)
	}

	return allData, nil
}

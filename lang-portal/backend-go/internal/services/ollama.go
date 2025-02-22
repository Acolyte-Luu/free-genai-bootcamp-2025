package services

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
)

type LLMService struct {
	baseURL string
}

func NewLLMService() *LLMService {
	return &LLMService{
		baseURL: "http://localhost:8000/v1/example-service",
	}
}

type GenerateRequest struct {
	Model  string `json:"model"`
	Prompt string `json:"prompt"`
	Stream bool   `json:"stream"`
}

type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type GenerateResponse struct {
	Choices []struct {
		Message struct {
			Content string `json:"content"`
		} `json:"message"`
	} `json:"choices"`
}

func (s *LLMService) GenerateVocabulary(theme string) (string, error) {
	prompt := fmt.Sprintf(`Generate a JSON array of 10 Japanese words about "%s" in this EXACT format:

[
	{
		"japanese": "寿司",
		"romaji": "sushi",
		"english": "sushi"
	},
	{
		"japanese": "天ぷら",
		"romaji": "tempura",
		"english": "tempura"
	}
]

CRITICAL RULES:
1. Use EXACTLY these field names: "japanese", "romaji", "english"
2. NEVER use "kanji" as a field name
3. All fields must have non-empty values
4. Japanese field must contain Japanese characters
5. Output ONLY the JSON array - nothing else
6. Must generate exactly 10 items`, theme)

	systemMsg := `You are a Japanese vocabulary generator.
	Generate ONLY valid JSON arrays.
	Always use these exact field names:
	- "japanese" for Japanese text (not "kanji")
	- "romaji" for pronunciation
	- "english" for translation
	Never leave any fields empty.`

	req := GenerateRequest{
		Model:  "llama3.2:1b",
		Prompt: systemMsg + "\n\n" + prompt,
		Stream: false,
	}

	reqBody, err := json.Marshal(req)
	if err != nil {
		return "", fmt.Errorf("failed to marshal request: %v", err)
	}

	resp, err := http.Post(s.baseURL, "application/json", bytes.NewBuffer(reqBody))
	if err != nil {
		return "", fmt.Errorf("failed to make request: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("failed to read response body: %v", err)
	}

	var genResp GenerateResponse
	if err := json.Unmarshal(body, &genResp); err != nil {
		return "", fmt.Errorf("failed to parse response: %v\nBody was: %s", err, string(body))
	}

	if len(genResp.Choices) == 0 || genResp.Choices[0].Message.Content == "" {
		return "", fmt.Errorf("no response content from LLM")
	}

	content := genResp.Choices[0].Message.Content

	// Find the JSON array
	startIdx := strings.Index(content, "[")
	endIdx := strings.LastIndex(content, "]")
	if startIdx < 0 || endIdx <= startIdx {
		return "", fmt.Errorf("no JSON array found in response: %s", content)
	}
	content = content[startIdx : endIdx+1]

	// More aggressive cleaning
	content = strings.TrimSpace(content)
	content = strings.ReplaceAll(content, "\t", "")
	content = strings.ReplaceAll(content, "\n", "")
	content = strings.ReplaceAll(content, "\\", "")
	content = strings.ReplaceAll(content, "\"\"", "\"")
	content = strings.ReplaceAll(content, "\"kanji\"", "\"japanese\"")
	content = strings.ReplaceAll(content, "/", "")
	content = strings.ReplaceAll(content, "å", "a")
	content = strings.ReplaceAll(content, "ù", "u")
	content = strings.ReplaceAll(content, " ,", ",")
	content = strings.ReplaceAll(content, ", ", ",")
	content = strings.ReplaceAll(content, " \"", "\"")
	content = strings.ReplaceAll(content, "\" ", "\"")

	// Fix double quotes around Japanese text
	content = strings.ReplaceAll(content, "\"\"", "\"")

	// Fix any remaining invalid quotes
	var fixedContent strings.Builder
	inQuotes := false
	for _, r := range content {
		if r == '"' {
			if !inQuotes {
				inQuotes = true
				fixedContent.WriteRune(r)
			} else {
				inQuotes = false
				fixedContent.WriteRune(r)
			}
		} else {
			fixedContent.WriteRune(r)
		}
	}
	content = fixedContent.String()

	// Convert kanji field to japanese field before validation
	var tempArray []map[string]string
	if err := json.Unmarshal([]byte(content), &tempArray); err == nil {
		for _, item := range tempArray {
			if value, exists := item["kanji"]; exists {
				item["japanese"] = value
				delete(item, "kanji")
			}
		}
		newContent, _ := json.Marshal(tempArray)
		content = string(newContent)
	}

	// Verify it's valid JSON
	var jsonTest []map[string]string
	if err := json.Unmarshal([]byte(content), &jsonTest); err != nil {
		return "", fmt.Errorf("invalid JSON format: %s", content)
	}

	// Validate each item
	for i, item := range jsonTest {
		if item["japanese"] == "" || item["romaji"] == "" || item["english"] == "" {
			return "", fmt.Errorf("item %d has empty fields: %v", i, item)
		}
		// Check for invalid values
		if item["japanese"] == "-" || item["romaji"] == "-" || item["english"] == "-" {
			return "", fmt.Errorf("item %d has invalid values: %v", i, item)
		}
	}

	return content, nil
}

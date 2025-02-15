# Technical Specs

## Business Requirements

A language learning school wants to build a prototype of learning portal which will act as three things:
- Inventory of possible vocabulary that can be learned
- Act as a  Learning record store (LRS), providing correct and wrong score on practice vocabulary
- A unified launchpad to launch different learning apps

## Technical Requirements

- The backend should be built using Go language
- The database should be SQLite3
- The API should be built using Gin framework
- The API should always return JSON
- There should be no authentication or authorization
- Everything should be in the scope of a single user


## Database Schema

- words table (stored vocabulary)
    - id integer
    - japanese string
    - romaji string
    - english string
    - parts string
    - created_at datetime

- words_groups table (join table for groups of words many to many)
    - id integer
    - word_id integer
    - group_id integer
    - created_at datetime

- groups table (groups of words)
    - id integer
    - name string
    - created_at datetime

- study_sessions table (records of study sessions grouping word_review_items)
    - id integer
    - group_id integer
    - study_activity_id integer
    - created_at datetime

- study_activities table (specific study activity, linking study session to group)
    - id integer
    - study_session_id integer
    - group_id integer
    - created_at datetime

- word_review_items table (records of word practice determining correct or wrong)
    - word_id integer
    - study_session_id integer
    - correct boolean
    - created_at datetime


## API Endpoints

#### GET /api/words

Returns a paginated list of vocabulary words.
**JSON Response:**
```json
{
    "data": [
    {
    "id": 1,
    "japanese": "猫",
    "romaji": "neko",
    "english": "cat",
    "parts": "noun",
    "created_at": "2024-03-20T15:30:00Z"
    }
    ],
    "pagination": {
    "current_page": 1,
    "total_pages": 10,
    "total_items": 1000,
    "items_per_page": 100
    }
}
```

### GET /api/words/:id

Returns a single word by ID.
**JSON Response:**
```json
{
    "data": {
        "id": 1,
        "japanese": "猫",
        "romaji": "neko",
        "english": "cat",
        "parts": "noun",
        "created_at": "2024-03-20T15:30:00Z"
    }
}
```

### GET /api/groups
Returns a paginated list of word groups.
```json
{
    "data": [
    {
    "id": 1,
    "name": "Animals",
    "created_at": "2024-03-20T15:30:00Z"
    }
    ],
    "pagination": {
    "current_page": 1,
    "total_pages": 10,
    "total_items": 1000,
    "items_per_page": 100
    }
}
```
### GET /api/groups/:id
Returns a single group by ID.
**JSON Response:**
```json
{
    "data": {
        "id": 1,
        "name": "Animals",
        "created_at": "2024-03-20T15:30:00Z"
    }
}
```
### GET /api/groups/:id/words
### GET /api/groups/:id/study_sessions

### GET /api/dashboard/last_study_session
Returns details about the most recent study session.
**JSON Response:**
```json
{
    "data": {
        "id": 1,
        "group_id": 1,
        "group_name": "Animals",
        "study_activity_id": 1,
        "created_at": "2024-03-20T15:30:00Z",
        "correct_count": 15,
        "total_words": 20
    }
}
```
### GET /api/dashboard/study_progress
Returns study progress statistics.
**JSON Response:**
```json
{
    "data": {
        "total_words": 500,
        "total_words_studied": 400,
    }
}
```

### GET /api/dashboard/quick_stats
Returns overview statistics.
**JSON Response:**
```json
{
  "data": {
    "total_study_sessions": 50,
    "active_groups": 10,
    "study_streak": 7,
    "success_percentage": 80
  }
}
```
### GET /api/study_activities/:id
Returns details of a specific study activity.
**JSON Response:**
```json
{
  "data": {
    "id": 1,
    "name": "Flashcards",
    "thumbnail_url": "/images/flashcards.png",
    "description": "Practice vocabulary with flashcards",
    "study_sessions": [
      {
        "id": 1,
        "activity_name": "Flashcards",
        "group_name": "Animals",
        "start_time": "2024-03-20T15:30:00Z",
        "end_time": "2024-03-20T15:45:00Z",
        "review_items_count": 20
      }
    ]
  }
}
```
### GET /api/study_activities/:id/study_sessions

### GET /api/study_sessions
    - Pagination 100 items per page
### GET /api/study_sessions/:id
### GET /api/study_sessions/:id/words

### POST /api/study_activities
    - required params: group_id, study_activity_id

### POST /api/reset_history
### POST /api/full_reset
### POST /api/study_sessions/:id/words/:word_id/review

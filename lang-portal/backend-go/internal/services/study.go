package services

import (
	"database/sql"

	"github.com/lang-portal/backend-go/internal/database/repository"
	"github.com/lang-portal/backend-go/internal/errors"
	"github.com/lang-portal/backend-go/internal/models"
)

var (
	ErrEmptyGroup = errors.NewValidationError("Group has no words", nil)
)

type StudyService struct {
	studyRepo *repository.StudyRepository
	wordRepo  *repository.WordRepository
	groupRepo *repository.GroupRepository
}

func NewStudyService(
	studyRepo *repository.StudyRepository,
	wordRepo *repository.WordRepository,
	groupRepo *repository.GroupRepository,
) *StudyService {
	return &StudyService{
		studyRepo: studyRepo,
		wordRepo:  wordRepo,
		groupRepo: groupRepo,
	}
}

func (s *StudyService) StartStudySession(groupID, activityID int64) (*models.StudySession, error) {
	// Validate group exists
	group, err := s.groupRepo.GetGroup(groupID)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, errors.NewNotFoundError("Group not found")
		}
		return nil, errors.NewServerError("Failed to fetch group", err)
	}

	// Validate group has words
	if group.TotalWordCount == 0 {
		return nil, ErrEmptyGroup
	}

	// Create study session
	session, err := s.studyRepo.CreateStudySession(groupID, activityID)
	if err != nil {
		return nil, errors.NewServerError("Failed to create study session", err)
	}

	return session, nil
}

func (s *StudyService) ReviewWord(sessionID, wordID int64, correct bool) error {
	// Validate session exists and is active
	_, err := s.studyRepo.GetStudySession(sessionID)
	if err != nil {
		if err == sql.ErrNoRows {
			return errors.NewNotFoundError("Study session not found")
		}
		return errors.NewServerError("Failed to fetch study session", err)
	}

	// Record review
	if err := s.studyRepo.CreateWordReview(wordID, sessionID, correct); err != nil {
		return errors.NewServerError("Failed to record word review", err)
	}

	return nil
}

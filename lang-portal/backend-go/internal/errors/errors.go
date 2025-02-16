package errors

import "fmt"

// AppError represents an application-specific error
type AppError struct {
	Code    int    `json:"-"`       // HTTP status code
	Type    string `json:"type"`    // Error type for clients
	Message string `json:"message"` // User-friendly error message
	Err     error  `json:"-"`       // Original error
}

func (e *AppError) Error() string {
	if e.Err != nil {
		return fmt.Sprintf("%s: %v", e.Message, e.Err)
	}
	return e.Message
}

// Common error types
const (
	TypeValidation  = "VALIDATION_ERROR"
	TypeNotFound    = "NOT_FOUND"
	TypeBadRequest  = "BAD_REQUEST"
	TypeServerError = "SERVER_ERROR"
	TypeConflict    = "CONFLICT"
)

// Error constructors
func NewValidationError(message string, err error) *AppError {
	return &AppError{
		Code:    400,
		Type:    TypeValidation,
		Message: message,
		Err:     err,
	}
}

func NewNotFoundError(message string) *AppError {
	return &AppError{
		Code:    404,
		Type:    TypeNotFound,
		Message: message,
	}
}

func NewBadRequestError(message string, err error) *AppError {
	return &AppError{
		Code:    400,
		Type:    TypeBadRequest,
		Message: message,
		Err:     err,
	}
}

func NewServerError(message string, err error) *AppError {
	return &AppError{
		Code:    500,
		Type:    TypeServerError,
		Message: message,
		Err:     err,
	}
}

func NewConflictError(message string) *AppError {
	return &AppError{
		Code:    409,
		Type:    TypeConflict,
		Message: message,
	}
}

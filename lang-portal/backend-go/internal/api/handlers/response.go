package handlers

type Response struct {
	Data    interface{} `json:"data,omitempty"`
	Success bool        `json:"success"`
	Message string      `json:"message,omitempty"`
	Error   string      `json:"error,omitempty"`
	Groups  interface{} `json:"groups,omitempty"`
}

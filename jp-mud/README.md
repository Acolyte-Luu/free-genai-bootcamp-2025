### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd jp-mud
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Edit as needed
cd ..
```

3. Set up the frontend:
```bash
cd frontend
npm install
cd ..
```

### Running the Application

**Important:** Ensure Ollama is running and accessible before starting the backend. If running Ollama in Docker, make sure the `LLM_HOST` and `LLM_PORT` in the `backend/.env` file are configured to point to your Ollama container's exposed address and port (e.g., `LLM_HOST=localhost` and `LLM_PORT=11434` if you mapped port 11434 directly).

1. Start the backend (in a terminal):
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m app.main
```

2. Start the frontend (in a different terminal):
```bash
cd frontend
npm run dev
```

3. Open your browser and navigate to `http://localhost:5173`

## Project Structure

```
jp-mud/
├── backend/           # Python FastAPI backend
│   ├── app/           # Application code
│   │   ├── api/       # API routes
│   │   ├── models/    # Data models
│   │   ├── services/  # Business logic
│   │   └── utils/     # Utility functions
│   └── requirements.txt
│
├── frontend/          # React frontend
│   ├── public/        # Static assets
│   ├── src/           # Application code
│   │   ├── components/# React components
│   │   ├── hooks/     # Custom React hooks
│   │   ├── pages/     # Page components
│   │   ├── services/  # API services
│   │   └── utils/     # Utility functions
│   └── package.json
│
└── README.md          # Project documentation
```

## License

MIT 

## Known Limitations / Areas for Improvement

*   **LLM Reliability:** Game functionality depends heavily on the consistency and performance of the configured local LLMs (Ollama). World generation may fall back to simpler templates if the LLM fails to produce valid JSON. Language validation accuracy and adherence to function-calling instructions can vary.
*   **State Management & Validation:** While efforts have been made to validate the game world structure (e.g., ensuring bidirectional connections, connecting orphans), edge cases might still exist, potentially leading to minor inconsistencies, especially with complex LLM-generated worlds. The simple JSON save format lacks versioning or corruption handling.
*   **Hybrid Logic:** The interaction between the deterministic `GameEngine` and the LLM service for command processing involves potential complexities in ensuring predictable state updates.
*   **Error Handling & Testing:** Error handling, particularly for LLM-specific issues or granular game logic failures, could be expanded. Comprehensive testing remains challenging due to the non-deterministic nature of LLMs. 
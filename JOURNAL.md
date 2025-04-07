# Project Development Journal

This journal details the insights and observations gathered during the free-genai-bootcamp-2025.

## `lang-portal-react` (Frontend)

*   **Goal:** My primary objective here was successfully integrating this React frontend with its Go counterpart (`lang-portal/backend-go`), establishing the link to the `jp-mud` MUD application, implementing the Dark Mode UI feature, and thoroughly documenting these steps in `FRONTEND_INTEGRATION.md`.
*   **Architecture:** I confirmed this is a Vite-powered React application using TypeScript (`tsconfig*.json`, `vite.config.ts`).
    *   Routing is handled by `react-router-dom` (v6, based on `package.json`), defining paths likely within `src/App.tsx` or a similar top-level component.
    *   API state management leverages `@tanstack/react-query` v5. I traced API calls in `src/lib/api.ts`, which defines functions like `fetchGroups`, `fetchWordsByGroup`, etc., using standard `fetch`. These functions construct requests to a backend (base URL not explicitly defined, likely assumes `http://localhost:8080`). They rely heavily on TypeScript types defined in `src/types/api.ts` (e.g., `Word`, `Group`, `StudySession`, `DashboardStats`) for request/response shaping and type safety.
    *   The UI is built using Tailwind CSS (`tailwind.config.ts`) and `shadcn/ui` (`components.json`). I saw common `shadcn/ui` components like `Card`, `Button`, `Table` used across various page components (e.g., in `src/pages/`). The Dark Mode implementation in `src/components/DarkModeToggle.tsx` modifies the `<html>` element's class list and uses `localStorage` for persistence.
    *   Key components I worked with included `src/pages/groups/GroupShow.tsx` (displaying group details and sessions), `src/components/StudyActivities.tsx` (listing activities), and `src/pages/study-sessions/StudyActivityShow.tsx` (showing individual activity details).
*   **Data Storage:** Beyond `localStorage` for the dark mode preference, all application data (user's words, groups, learning progress) seems to be managed entirely server-side via the Go backend API.
*   **Dependencies:** Examining `package.json`, I confirmed key libraries: `react` 18.2, `typescript` ~5.2, `@tanstack/react-query` 5.25, `tailwindcss`, `lucide-react` for icons, and `react-router-dom` 6.22. The presence of both `package-lock.json` and `bun.lockb` suggests flexibility in package management, though `npm` seems implied by the `README.md`.
*   **Status & Activities:**
    *   I successfully replaced mock data by integrating the API functions from `src/lib/api.ts` into components, using `useQuery` hooks for data fetching (e.g., fetching words, groups, sessions, stats).
    *   I encountered runtime discrepancies between the actual Go backend API responses and the definitions in `lang-portal/Backend-Technical-Specs.md`. Specifically, the nesting of words within groups and the occasional absence of the `stats` object required adding defensive checks (like `data?.stats?.totalWords ?? 0`) in components like `GroupShow.tsx` and `Dashboard.tsx` to prevent rendering errors.
    *   I updated the `onClick` handlers for buttons related to the "Adventure MUD" activity in `src/components/StudyActivities.tsx` to navigate the browser directly to `http://localhost:5173/` (the assumed `jp-mud` frontend URL).
    *   I implemented the Dark Mode toggle component, ensuring the `ThemeProvider` context was set up correctly in `src/App.tsx` and the required dark theme variables were present in `src/index.css`.
    *   Upon inspecting `src/components/VocabularyImporter.tsx`, I found it uses `react-hook-form` and attempts a `POST` request to an endpoint (`/generate-vocabulary`) that wasn't documented in the backend specs. I decided to leave its functionality as displaying the raw API response, as saving the results would necessitate backend modifications.
    *   The list of activities available in `src/components/StudyActivities.tsx` remains static/hardcoded, as no API endpoint was identified for fetching these dynamically.
    *   I confirmed the "Reset History" functionality on the `src/pages/Settings.tsx` page is unimplemented, pending necessary `DELETE` endpoints on the backend.
    *   Finally, I consolidated these integration notes and findings into `FRONTEND_INTEGRATION.md` and updated the project's main `lang-portal-react/README.md`.

## `lang-portal` (Backend Specs & Code)

*   **Goal:** This directory serves as the container for the backend specifications (`Backend-Technical-Specs.md`, `Frontend-Technical-Specs.md`) and the actual Go backend source code (`backend-go/`). Its primary role is providing the API layer for the `lang-portal-react` frontend.
*   **Architecture:** The `Backend-Technical-Specs.md` outlines a REST API structure. A look into `backend-go/` would likely reveal a standard Go project layout, possibly using a framework like Gin, Echo, or Chi for routing and middleware. The API specification details endpoints for managing `Words` (CRUD), `Groups` (CRUD), `StudySessions` (primarily GET, linked to Groups), and fetching `DashboardStats`.
*   **Data Storage:** The specifications strongly suggest a relational database backend. Based on typical Go practices, this could be PostgreSQL or MySQL, likely interacted with using standard library `database/sql` potentially augmented by an ORM or helper like `sqlx` or `gorm`. Confirmation would require inspecting database connection and model code within `backend-go`.
*   **Dependencies:** Beyond the Go standard library, dependencies within `backend-go/go.mod` (not viewed) would likely include a router, database driver(s), and possibly libraries for configuration (`viper`) or logging.
*   **Status:** My review focused on `Backend-Technical-Specs.md`, which proved useful but revealed inconsistencies with the actual running API (as noted in the React section) and missing endpoints for features like vocabulary generation (`POST /generate-vocabulary`) and data deletion needed for the settings page. I refrained from modifying the `backend-go` source code.

## `jp-mud`

*   **Goal:** To provide an interactive Multi-User Dungeon experience, potentially focused on language learning activities, as described in `MUD-Tech-Specs.md`. It's designed to be linked from the main `lang-portal-react` application.
*   **Architecture:** The project is divided into `frontend/` and `backend/`. The `frontend/` directory uses Vite and TypeScript (confirmed via `frontend/package.json` if viewed, or inferred from Vite standard). `MUD-Tech-Specs.md` implies a WebSocket connection is essential for the real-time, interactive nature of a MUD, connecting the frontend to the `backend/` server.
*   **Data Storage:** The backend storage mechanism isn't clear. It could range from in-memory state for ephemeral sessions to a persistent database (e.g., SQLite, PostgreSQL) for player data, world state, etc. Needs inspection of `backend/` code.
*   **Dependencies:** Frontend: Vite, TypeScript, likely React and WebSocket client library. Backend: Depends on the chosen language/framework (e.g., Python with `websockets`, Node.js with `ws`, Go with `gorilla/websocket`).
*   **Status:** I performed a cursory examination of the `frontend/` structure. Linking appears straightforward via URL navigation from `lang-portal-react`. No code modifications were undertaken.

## `listening-comp`

*   **Goal:** To offer users practice in listening comprehension, likely involving dynamically generated audio clips and corresponding questions.
*   **Architecture:** This Python project has distinct `backend/` and `frontend/` parts.
    *   The `backend/` likely runs a FastAPI server (based on `README.md` instructions often using `uvicorn main:app`).
    *   Text-to-Speech is a core feature, managed by `tts_helper.py` which probably wraps a library like Coqui TTS (`TTS==0.22.0` often seen in similar projects, hinted at by `Dockerfile`). `patched_tts.py` suggests potential modifications or workarounds for the TTS library. Interaction with PyTorch (`pytorch_patch.py`, `Dockerfile` installing `torch` and `torchaudio`) confirms local model execution for TTS.
    *   The `Dockerfile` defines the runtime environment, installing Python, PyTorch, and TTS dependencies, indicating it's deployable as a container.
    *   It utilizes ChromaDB (`chroma_db/` directory) as a vector store, accessed via the `chromadb` client library. This is likely used to store embeddings of text segments (perhaps dialogue or questions) for semantic search or retrieval during practice sessions.
    *   The `frontend/` could be a separate SPA or potentially a Streamlit application (common for Python ML demos, though not explicitly confirmed).
*   **Data Storage:** Embeddings are stored in ChromaDB (`chroma_db/` persists the database files). Generated `.wav` files are saved in `audio_data/`. User interactions seem to be logged in `question_history.json`.
*   **Dependencies:** `python`, `torch`, `torchaudio`, `TTS` library, `chromadb`, `fastapi`, `uvicorn`. If `requirements.txt` exists within `backend/` or `frontend/`, it would list specifics like `numpy`, `pydantic`, etc.
*   **Status:** Seems like a sophisticated, self-contained application. It's functional based on the files present but requires integration to be used within the main `lang-portal-react` flow.

## `opea-comps`

*   **Goal:** To define and orchestrate a suite of Open Enterprise Audio (OPEA) microservices using Docker Compose, likely forming a reusable audio processing pipeline for AI applications, as explained in `readme.md`.
*   **Architecture:** Driven entirely by `docker-compose.yml`. This file defines multiple services:
    *   `opea-tts`: For text-to-speech.
    *   `opea-asr`: For automatic speech recognition.
    *   `opea-retriever`: Likely performs vector search/retrieval against an indexed dataset.
    *   `opea-embedding`: Probably generates text embeddings.
    *   Others like `opea-analyzer`, `opea-langchain-backend` suggest integration with broader AI frameworks.
    *   These likely use pre-built Docker images specified in the `image:` directive within the compose file. The `mega-service/` directory might contain custom code or configuration for one of these services.
    *   The presence of `.wav` files (`speech.wav`, `output-*.wav`) serves as test data or examples.
*   **Data Storage:** The orchestrator itself is stateless. Persistence depends on volume mounts configured for individual services within `docker-compose.yml` (e.g., a database volume for a service storing metadata, or a vector index volume for the retriever).
*   **Dependencies:** Docker Engine and Docker Compose CLI.
*   **Status:** This provides robust backend infrastructure for audio AI tasks. It's not directly user-facing but likely serves as a dependency or platform for applications like `listening-comp`.

## `writing-practice`

*   **Goal:** To provide users with writing exercises (translation, rewriting) and leverage a local LLM for feedback or generation, according to `Tech-specs.md`.
*   **Architecture:** Implemented as a Python web application using the Flask framework (`app.py`).
    *   `app.py` defines routes like `/`, `/translate`, `/rewrite`, handling user input from web forms.
    *   Interaction with a local LLM is encapsulated in `localllm.py`. This module uses the `ollama` Python library (v0.2.0 or higher likely) to connect to an Ollama server (defaulting to `http://localhost:11434`) and execute prompts using models like `llama3` or `mistral` (as might be configured or passed).
*   **Data Storage:** The application appears simple; `app.py` doesn't show database connections. State seems mostly managed in memory per request, or via simple session handling if configured.
*   **Dependencies:** `Flask`, `ollama`, `python-dotenv` are listed in `requirements.txt`.
*   **Status:** A working, standalone Flask app providing specific LLM-powered writing tools. Integration with `lang-portal-react` would require either exposing its functionality via an API or incorporating its logic elsewhere.

## `song-vocab`

*   **Goal:** As per its `Tech-specs.md`, this service aims to find song lyrics via web search and then use a ReAct-style LLM agent to extract detailed Japanese vocabulary items.
*   **Architecture:** 
    *   The backend is built with Python using FastAPI (`main.py`). It defines two core async endpoints: `POST /api/agent` which takes a `MessageRequest` Pydantic model and returns a `HandlerResponse` containing a job ID, and `GET /api/results/{handler_id}` which returns an `AgentResponse` with lyrics and vocabulary.
    *   The main agent logic resides in `agent.py`. The `run_agent` function orchestrates a loop interacting with an Ollama LLM (`llama3.1:8b` hardcoded) via a `CustomOllamaClient` defined in `tools/custom_client.py` (connecting to `http://localhost:9000`). Crucially, it uses the `instructor` library to get structured JSON output from the LLM, parsing it into Pydantic models like `AgentAction` (specifying `tool` and `tool_input`) or the final `AgentOutput` (containing `lyrics` and `vocabulary` list).
    *   The agent's available tools are defined in the `TOOLS` dictionary in `agent.py` and map strings to functions imported from `tools/`: `search_web.py` (uses `duckduckgo_search`), `get_page_content.py` (uses `requests` and `BeautifulSoup4` for scraping), and `extract_vocabulary.py` (which itself likely uses another `instructor`-based LLM call with the prompt from `prompts/vocabulary_extraction_prompt.py`).
    *   Prompts guiding the agent's reasoning (`REACT_AGENT_PROMPT`), metadata extraction (`SONG_METADATA_PROMPT`), and vocabulary structure are defined in `prompts/`.
*   **Data Storage:**
    *   For asynchronous handling, results are temporarily staged in `outputs/` subdirectories named by handler ID (`uuid.uuid4()`). Each contains `lyrics.txt`, `vocabulary.json`, and `metadata.json`.
    *   Long-term persistence uses a SQLite database (`song_vocabulary.db`). The schema is created and managed by `db_schema.py`, defining `songs` (id, title, artist, lyrics) and `vocabulary` (id, song_id, word, translation, example) tables. The `save_song_and_vocabulary` function handles inserting data, although I noted it doesn't persist the detailed `parts` (like Kanji/Romaji breakdown) from the `VocabularyItem` Pydantic model into the database, opting for a simpler structure.
*   **Dependencies:** The `requirements.txt` file lists `fastapi`, `uvicorn`, `pydantic`, `instructor`, `ollama`, `duckduckgo-search`, `requests`, `beautifulsoup4`.
*   **Status:** This component appears well-structured and functional as a standalone service for its specific task. My detailed analysis of its workflow and components is complete.

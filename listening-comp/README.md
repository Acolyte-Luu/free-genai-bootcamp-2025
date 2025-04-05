# language-learning-assistant
This is for the generative AI bootcamp

**Difficulty:** Level 200 *(Due to RAG implementation and multiple AWS services integration)*

**Business Goal:**
A progressive learning tool that demonstrates how RAG and agents can enhance language learning by grounding responses in real Japanese lesson content. The system shows the evolution from basic LLM responses to a fully contextual learning assistant, helping students understand both the technical implementation and practical benefits of RAG.


**Technical Restrictions:**
* Must use Amazon Bedrock for:
   * API (converse, guardrails, embeddings, agents) (https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
     * Aamzon Nova Micro for text generation (https://aws.amazon.com/ai/generative-ai/nova)
   * Titan for embeddings

#### Novelty
We were supposed to use Amazon Bedrock for the API (converse, guardrails, embeddings, agents) but I decided to use Ollama for the API because it's free and I had already set it up for the opea-comps. The model I used is llama3.1:8b which is free and has a good balance of quality and speed. I am running it locally (localhost:9000) with my GPU (RTX 2070).

- [x] Must implement in Streamlit, pandas (data visualization)
- [x] Must use SQLite for vector storage
- [x] Must handle YouTube transcripts as knowledge source (YouTubeTranscriptApi: https://pypi.org/project/youtube-transcript-api/)
- [x] Must demonstrate clear progression through stages:
   - [x] Base LLM
   - [x] Raw transcript
   - [x] Structured data
   - [ ] RAG implementation
   - [ ] Interactive features
- [x] Must maintain clear separation between components for teaching purposes
- [x] Must include proper error handling for Japanese text processing
- [x] Must provide clear visualization of RAG process
- [x] Should work within free tier limits where possible


## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url> # Replace with your repo URL
    cd language-learning-assistant # Or your project's root directory name
    ```

2.  **Set up Python Environment:**
    ```bash
    # Create and activate a virtual environment (recommended)
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`

    # Install dependencies (assuming a requirements.txt exists in the root or backend)
    # If requirements are split, adjust accordingly (e.g., pip install -r backend/requirements.txt)
    pip install -r requirements.txt # Or specific requirements file if needed
    ```
    *Note: Ensure you have PyTorch installed correctly for your system (CPU/GPU). Check PyTorch official website for instructions.*

3.  **Ensure Ollama is Running (Docker Compose):**
    *   This project assumes Ollama is running and accessible. The following instructions are based on the Docker Compose setup from the `opea-comps` project.
    *   **Prerequisites:**
        *   Docker and Docker Compose installed.
        *   You have the `docker-compose.yml` file from the `opea-comps` project.
        *   **(Optional but Recommended for GPU)** If using an NVIDIA GPU, ensure the NVIDIA Container Toolkit is installed and Docker is configured for GPU access (see `opea-comps/readme.md` for detailed steps).
    *   **Start Ollama Service:**
        Open a terminal in the directory containing the `docker-compose.yml` from `opea-comps` and run:
        ```bash
        # Adjust LLM_ENDPOINT_PORT if needed (this app expects 9000 based on Novelty section)
        # Adjust LLM_MODEL_ID if you want to preload a different default model
        HOST_IP=$(hostname -I | awk '{print $1}') NO_PROXY=localhost LLM_ENDPOINT_PORT=9000 LLM_MODEL_ID="llama3.1:8b" docker compose up -d
        ```
        *Note: The `-d` flag runs the container in detached mode (in the background).* 
    *   **Pull the Required Model:**
        Once the container is running, pull the specific model used by this application (`llama3.1:8b` as mentioned in the Novelty section):
        ```bash
        curl http://localhost:9000/api/pull -d '{ "model": "llama3.1:8b" }'
        ```
        *Wait for the model download to complete.* 
    *   **Verify Accessibility:** Ensure the application can reach Ollama at `http://localhost:9000` (or the configured `LLM_ENDPOINT_PORT`). The application code (e.g., `backend/chat.py`) might need adjustments if the host or port differs from its defaults.

## Running the Application

1.  **Navigate to the frontend directory:**
    ```bash
    cd listening-comp
    ```

2.  **Run the Streamlit application:**
    ```bash
    streamlit run frontend/main.py
    ```

3.  Open your browser and navigate to the local URL provided by Streamlit (usually `http://localhost:8501`).


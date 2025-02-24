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

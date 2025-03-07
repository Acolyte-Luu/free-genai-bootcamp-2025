from fastapi import HTTPException
from comps.cores.proto.api_protocol import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatMessage,
    UsageInfo
)
from comps.cores.mega.constants import ServiceType, ServiceRoleType
from comps import MicroService, ServiceOrchestrator
import os
import logging
import json
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# At the top of the file
EMBEDDING_SERVICE_HOST_IP = os.getenv("EMBEDDING_SERVICE_HOST_IP", "127.0.0.1")
EMBEDDING_SERVICE_PORT = os.getenv("EMBEDDING_SERVICE_PORT", 6000)
LLM_SERVICE_HOST_IP = os.getenv("LLM_SERVICE_HOST_IP", "127.0.0.1")
LLM_SERVICE_PORT = os.getenv("LLM_SERVICE_PORT", 9000)  # Changed to match Ollama's internal port

print(f"LLM_SERVICE_HOST_IP: {LLM_SERVICE_HOST_IP}")
print(f"LLM_SERVICE_PORT: {LLM_SERVICE_PORT}")

class ExampleService:
    def __init__(self, host="0.0.0.0", port=8000):
        logger.info("Initializing ExampleService")
        os.environ["TELEMETRY_ENDPOINT"] = ""
        self.host = host
        self.port = port
        self.endpoint = "/v1/example-service"
        self.megaservice = ServiceOrchestrator()
        logger.info(f"Service initialized with host={host}, port={port}")

    def add_remote_service(self):
        logger.info("Adding remote LLM service")
        llm = MicroService(
            name="llm",
            host=LLM_SERVICE_HOST_IP,
            port=LLM_SERVICE_PORT,
            endpoint="/v1/chat/completions",
            use_remote_service=True,
            service_type=ServiceType.LLM,
        )
        self.megaservice.add(llm)
        logger.info(f"Added LLM service at {LLM_SERVICE_HOST_IP}:{LLM_SERVICE_PORT}")
    
    def start(self):
        logger.info("Starting service")
        self.service = MicroService(
            self.__class__.__name__,
            service_role=ServiceRoleType.MEGASERVICE,
            host=self.host,
            port=self.port,
            endpoint=self.endpoint,
            input_datatype=ChatCompletionRequest,
            output_datatype=ChatCompletionResponse,
        )

        self.service.add_route(self.endpoint, self.handle_request, methods=["POST"])
        logger.info(f"Added route: POST {self.endpoint}")

        logger.info("Starting service...")
        self.service.start()

    async def handle_request(self, request: ChatCompletionRequest | dict) -> ChatCompletionResponse:
        try:
            logger.info(f"Request type: {type(request)}")
            logger.info(f"Request content: {request}")
            
            # Format the prompt based on request type
            if not isinstance(request, dict):
                # Handle ChatCompletionRequest
                combined_prompt = request.messages[-1].content if request.messages else ""
                model = request.model or "llama3.1:8b"
            else:
                # Handle dict
                combined_prompt = request.get("prompt", "")
                model = request.get("model", "llama3.1:8b")
            
            logger.info(f"Combined prompt: {combined_prompt}")
            
            # Format the request exactly as the orchestrator does
            endpoint = f"http://{LLM_SERVICE_HOST_IP}:{LLM_SERVICE_PORT}/v1/chat/completions"
            ollama_request = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": combined_prompt
                    }
                ],
                "stream": True
            }
            
            logger.info(f"Sending request to Ollama at {endpoint}: {ollama_request}")
            
            # Use requests.post directly as the orchestrator does
            import requests
            response = requests.post(
                url=endpoint,
                data=json.dumps(ollama_request),
                headers={"Content-type": "application/json"},
                proxies={"http": None},
                stream=True,
                timeout=1000
            )
            
            content = ""
            for chunk in response.iter_content(chunk_size=None):
                if chunk:
                    chunk_str = chunk.decode('utf-8')
                    logger.info(f"Raw chunk: {chunk_str!r}")
                    
                    # Extract content from the chunk
                    if chunk_str.startswith("data: "):
                        data = chunk_str[6:].strip()
                        if data == "[DONE]":
                            break
                        try:
                            json_data = json.loads(data)
                            if 'choices' in json_data and len(json_data['choices']) > 0:
                                delta = json_data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    content += delta['content']
                                    logger.info(f"Current content: {content}")
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse JSON: {data}")
            
            logger.info(f"Final content: {content}")
            
            # Create the response
            response = ChatCompletionResponse(
                model=model,
                choices=[
                    ChatCompletionResponseChoice(
                        index=0,
                        message=ChatMessage(
                            role="assistant",
                            content=content
                        ),
                        finish_reason="stop"
                    )
                ],
                usage=UsageInfo(
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0
                )
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("Starting ExampleService application")
    example = ExampleService()
    example.add_remote_service()
    example.start()
# --- external imports
import json
from datetime import datetime
from typing import AsyncIterable
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse
from langgraph.execution_graphs import get_generate_response_graph

# --- internal imports
from config import TIMEZONE, DELIMITER, MISTRAL_API_KEY
from api.api_models import PromptInput

router = APIRouter()


async def generate_response(prompt_input: PromptInput) -> AsyncIterable[str]:
    execution_flow_graph = await get_generate_response_graph()

    print("Response generation started...")

    # 1) onStart event
    yield f"data: {json.dumps({'type': 'onStart', 'content': 'Stream is starting!', 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"

    # 2) running a simple LLM inference
    async for event in execution_flow_graph.astream_events(
        input={},
        config={
            "configurable": {
                "prompt_input": prompt_input,
            }
        },
    ):
        pass

        
    # 3) onImageUrl event
    yield f"data: {json.dumps({'type': 'onImageUrl', 'content': 'https://stardewvalleywiki.com/mediawiki/images/a/af/Horse_rider.png', 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"

    # 5) onEnd event
    yield f"data: {json.dumps({'type': 'onEnd', 'content': 'Stream has ended.', 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"


@router.post("/generate-response-endpoint/")
async def generate_response_handler(body: PromptInput) -> StreamingResponse:
    generator = generate_response(prompt_input=body)
    return StreamingResponse(content=generator, media_type="text/event-stream")

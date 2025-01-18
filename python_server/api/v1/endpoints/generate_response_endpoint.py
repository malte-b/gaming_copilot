# --- external imports
import json
from datetime import datetime
from typing import AsyncIterable
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.mistral import MistralModel


# --- internal imports
from config import TIMEZONE, DELIMITER, MISTRAL_API_KEY

router = APIRouter()


class PromptInput(BaseModel):
    user_message: str


async def generate_response(prompt_input: PromptInput) -> AsyncIterable[str]:
    print("Response generation started...")
    model = MistralModel("mistral-small-latest", api_key=MISTRAL_API_KEY)
    agent = Agent(model)

    # 1) onStart event
    yield f"data: {json.dumps({'type': 'onStart', 'content': 'Stream is starting!', 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"

    # 2) running a simple LLM inference via pydantic_ai
    async with agent.run_stream(prompt_input.user_message) as result:
        async for token in result.stream_text(delta=True):
            yield f"data: {json.dumps({'type': 'onTextToken', 'content': token, 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"

    # 3) onImageUrl event
    yield f"data: {json.dumps({'type': 'onImageUrl', 'content': 'https://stardewvalleywiki.com/mediawiki/images/a/af/Horse_rider.png', 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"

    # 5) onEnd event
    yield f"data: {json.dumps({'type': 'onEnd', 'content': 'Stream has ended.', 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"


@router.post("/generate-response-endpoint/")
async def generate_response_handler(body: PromptInput) -> StreamingResponse:
    generator = generate_response(prompt_input=body)
    return StreamingResponse(content=generator, media_type="text/event-stream")

# --- external imports
import json
from datetime import datetime
from typing import AsyncIterable
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# --- internal imports
from config import TIMEZONE, DELIMITER

router = APIRouter()


class PromptInput(BaseModel):
    user_message: str


async def generate_response(prompt_input: PromptInput) -> AsyncIterable[str]:
    yield f"data: {json.dumps({'type': 'onStart', 'content': 'Stream is starting!', 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"


@router.post("/generate-response-endpoint/")
async def generate_response_handler(body: PromptInput) -> StreamingResponse:
    generator = generate_response(prompt_input=body)
    return StreamingResponse(content=generator, media_type="text/event-stream")

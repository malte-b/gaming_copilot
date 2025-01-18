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
    print("Response generation started...")
    # 1) onStart event
    yield f"data: {json.dumps({'type': 'onStart', 'content': 'Stream is starting!', 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"

    # 2) onTextToken event with markdown
    yield f"data: {json.dumps({'type': 'onTextToken', 'content': '### This is a sample **Markdown** text', 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"

    # 3) onImageUrl event
    yield f"data: {json.dumps({'type': 'onImageUrl', 'content': 'https://stardewvalleywiki.com/mediawiki/images/a/af/Horse_rider.png', 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"

    # 4) onTextToken event with more markdown
    yield f"data: {json.dumps({'type': 'onTextToken', 'content': 'Here is another piece of **markdown** text!', 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"

    # 5) onEnd event
    yield f"data: {json.dumps({'type': 'onEnd', 'content': 'Stream has ended.', 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"


@router.post("/generate-response-endpoint/")
async def generate_response_handler(body: PromptInput) -> StreamingResponse:
    generator = generate_response(prompt_input=body)
    return StreamingResponse(content=generator, media_type="text/event-stream")

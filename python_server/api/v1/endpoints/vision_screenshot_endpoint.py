from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from api.api_models import PromptInput
from typing import AsyncIterable, List
import base64
import os
from mistralai import Mistral
import weaviate
from weaviate.auth import AuthApiKey
from langchain_core.documents.base import Document
import json
from datetime import datetime



from config import TIMEZONE, DELIMITER

load_dotenv()

router = APIRouter()

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")


async def retrieve_with_weaviate(prompt_input: PromptInput, image_description: str) -> List[Document]:
    # RETRIEVAL
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=WEAVIATE_URL, auth_credentials=AuthApiKey(WEAVIATE_API_KEY), headers={"X-Mistral-Api-Key": MISTRAL_API_KEY}
    )
    chunks = client.collections.get("StardewWiki")
    retrieved_documents = chunks.query.near_text(query=prompt_input.user_message + "image description: " + image_description, limit=3)
    client.close()
    return retrieved_documents


def run_mistral(user_message, model="mistral-large-latest") -> str:
    client = Mistral(api_key=MISTRAL_API_KEY)
    chat_response = client.chat.complete(model=model, messages=user_message)
    return chat_response.choices[0].message.content


def generate_vision_response(prompt_input: PromptInput) -> str:
    base64_image: str = prompt_input.image
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe the image and use the following user query to guide you: " + prompt_input.user_message},
                {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"},
            ],
        }
    ]

    chat_response = run_mistral(model="pixtral-large-latest", user_message=messages)

    return chat_response


async def generate_rag_response(prompt_input: PromptInput, image_description: str) -> AsyncIterable[str]:
    vector_db_context = await retrieve_with_weaviate(prompt_input, image_description)
    messages = [
        {
            "role": "user",
            "content": f"""
            Given the following the follwing description of the image:
            ---------------------
            {image_description}
            ---------------------
            And given the following context:
            ---------------------
            {vector_db_context}
            ---------------------
            Answer the following question:
            ---------------------
            {prompt_input.user_message}
            ---------------------
            """,
        }
    ]

    chat_response = run_mistral(user_message=messages)

    yield f"data: {json.dumps({'type': 'onStart', 'content': 'Stream is starting!', 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"

    # 2) Text event
    yield f"data: {json.dumps({'type': 'onText', 'content': chat_response, 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"

    # 5) onEnd event
    yield f"data: {json.dumps({'type': 'onEnd', 'content': 'Stream has ended.', 'timestamp': datetime.now(tz=TIMEZONE).isoformat()})}{DELIMITER}"


@router.post("/vision-screenshot-endpoint/")
async def generate_response_handler(body: PromptInput) -> StreamingResponse:
    image_description = generate_vision_response(prompt_input=body)
    rag_response = generate_rag_response(prompt_input=body, image_description=image_description)
    return StreamingResponse(content=rag_response, media_type="text/event-stream")

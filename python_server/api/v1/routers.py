from fastapi import APIRouter

from api.v1.endpoints import generate_langchain_response_endpoint, vision_screenshot_endpoint

api_router = APIRouter()

api_router.include_router(generate_langchain_response_endpoint.router, prefix="", tags=["generate_langchain_response_endpoint"])
api_router.include_router(vision_screenshot_endpoint.router, prefix="", tags=["vision_screenshot_endpoint"])


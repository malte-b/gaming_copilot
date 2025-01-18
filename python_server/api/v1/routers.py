from fastapi import APIRouter

from api.v1.endpoints import generate_response_endpoint

api_router = APIRouter()

api_router.include_router(generate_response_endpoint.router, prefix="", tags=["generate_response_endpoint"])

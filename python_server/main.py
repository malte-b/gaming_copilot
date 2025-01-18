# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.routers import api_router

origins = []
origins.append("http://localhost:3000")

#### run with "poetry run uvicorn main:app --port 5000"
app = FastAPI(title="gaming_copilot")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="")

"""Module to handle the FastAPI application and its routes."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from endpoints.llm_endpoint import router as llm_router


# Instanciando o FastAPI
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(llm_router)

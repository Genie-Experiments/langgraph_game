"""
Main entry point for the application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.backend.apis import game_orchestrator

from app.backend.apis import number_game, word_game

app = FastAPI(
    title="LangGraph Game Hub",
    description="A multi-game system built with LangGraph and FastAPI"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(game_orchestrator.router, prefix="/api", tags=["Game Orchestrator"])
app.include_router(number_game.router, prefix="/api", tags=["Number Game"])
app.include_router(word_game.router, prefix="/api", tags=["Word Game"])

@app.get("/")
async def root():
    return {"message": "Welcome to the LangGraph Game Hub"}
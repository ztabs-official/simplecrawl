# main.py
from fastapi import FastAPI
from app.api.v1.scrape import router as scrape_router

app = FastAPI(
    title="SimpleCrawl",
    description="An API to crawl websites and extract LLM & Agent Friendly data",
    version="1.0.0"
)

app.include_router(scrape_router)

@app.get("/")
async def read_root():
    return {"message": "SimpleCrawl API is running!"}

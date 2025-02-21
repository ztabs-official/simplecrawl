# main.py
from fastapi import FastAPI
from app.api.v1.crawler import router as crawler_router

app = FastAPI(
    title="SimpleCrawl",
    description="An API to crawl websites and extract LLM & Agent Friendly data",
    version="1.0.0"
)

@app.get("/")
async def read_root():
    return {"message": "SimpleCrawl API is running!"}


# Include routers
app.include_router(crawler_router)

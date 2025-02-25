from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import scrape

app = FastAPI(
    title="SimpleCrawl API",
    description="A powerful web scraping and crawling API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    scrape.router,
    prefix="/api/v1",
    tags=["scraping"]
) 
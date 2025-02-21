from fastapi import APIRouter, HTTPException
from app.models.url_model import URLInput
from app.services.crawler_service import CrawlerService

router = APIRouter(prefix="/v1", tags=["crawler"])

@router.post("/getmarkdown")
async def get_markdown(url_input: URLInput):
    try:
        return await CrawlerService.get_markdown(str(url_input.url))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
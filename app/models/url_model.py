from pydantic import BaseModel, HttpUrl

class URLInput(BaseModel):
    url: HttpUrl 
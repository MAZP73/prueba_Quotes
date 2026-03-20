from pydantic import BaseModel
from typing import List, Optional


class TagSchema(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class AuthorSchema(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class QuoteSchema(BaseModel):
    id: int
    text: str
    author: AuthorSchema
    tags: List[TagSchema]

    model_config = {"from_attributes": True}


class QuoteCreateSchema(BaseModel):
    text: str
    author: str
    tags: List[str]


class ScrapeResponseSchema(BaseModel):
    message: str
    total_scraped: int
    total_saved: int
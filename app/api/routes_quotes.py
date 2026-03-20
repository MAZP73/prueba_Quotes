from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.db.schemas import QuoteSchema, ScrapeResponseSchema
from app.services.quote_service import QuoteService

router = APIRouter()


@router.get("/", response_model=List[QuoteSchema])
def get_quotes(
    author: Optional[str] = Query(None, description="Filtrar por nombre de autor"),
    tag: Optional[str] = Query(None, description="Filtrar por etiqueta"),
    search: Optional[str] = Query(None, description="Búsqueda libre en el texto de la cita"),
    db: Session = Depends(get_db),
):
    service = QuoteService(db)
    return service.get_quotes(author=author, tag=tag, search=search)


@router.post("/scrape", response_model=ScrapeResponseSchema)
def trigger_scrape(db: Session = Depends(get_db)):

    service = QuoteService(db)
    return service.run_scraper()
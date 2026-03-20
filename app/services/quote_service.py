from typing import List, Optional
from sqlalchemy.orm import Session

from app.services.scraper_service import ScraperService
from app.repositories.quote_repository import QuoteRepository
from app.db.schemas import QuoteSchema, ScrapeResponseSchema
from app.db.models import Quote
from app.logger import get_logger

logger = get_logger(__name__)


class QuoteService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = QuoteRepository(db)
        self.scraper = ScraperService()

    def run_scraper(self) -> ScrapeResponseSchema:

        logger.info("Iniciando proceso de scraping...")
        raw_quotes = self.scraper.scrape_all_quotes()

        saved = 0
        for quote_data in raw_quotes:
            result = self.repository.save_quote(quote_data)
            if result:
                saved += 1

        logger.info(f"Scraping completo: {len(raw_quotes)} extraídas, {saved} guardadas nuevas.")
        return ScrapeResponseSchema(
            message="Scraping completado exitosamente.",
            total_scraped=len(raw_quotes),
            total_saved=saved,
        )

    def get_quotes(
        self,
        author: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[QuoteSchema]:
        quotes: List[Quote] = self.repository.get_all(author=author, tag=tag, search=search)
        return [QuoteSchema.model_validate(q) for q in quotes]
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.database import SessionLocal, engine, Base
from app.services.quote_service import QuoteService
from app.logger import get_logger

logger = get_logger("run_scraper")


def main():
    logger.info("Creando tablas si no existen...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        service = QuoteService(db)
        result = service.run_scraper()
        logger.info(f"   {result.message}")
        logger.info(f"   Extraídas : {result.total_scraped}")
        logger.info(f"   Guardadas : {result.total_saved}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
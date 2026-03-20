from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.routes_quotes import router as quotes_router
from app.db.database import engine, Base
from app.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicación y verificando tablas...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas verificadas correctamente.")
    yield
    logger.info("Apagando aplicación.")


app = FastAPI(
    title="Quotes Scraper API",
    description="API REST para consultar citas extraídas de quotes.toscrape.com",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(quotes_router, prefix="/quotes", tags=["Quotes"])


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Quotes Scraper API corriendo"}
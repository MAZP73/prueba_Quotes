from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from app.db.models import Quote, Author, Tag
from app.db.schemas import QuoteCreateSchema
from app.logger import get_logger

logger = get_logger(__name__)


class QuoteRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_or_create_author(self, name: str) -> Author:
        author = self.db.query(Author).filter(Author.name == name).first()
        if not author:
            author = Author(name=name)
            self.db.add(author)
            self.db.flush()
            logger.info(f"Autor creado: {name}")
        return author

    def get_or_create_tag(self, name: str) -> Tag:
        tag = self.db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)
            self.db.add(tag)
            self.db.flush()
        return tag

    def quote_exists(self, text: str) -> bool:
        return self.db.query(Quote).filter(Quote.text == text).first() is not None

    def save_quote(self, data: QuoteCreateSchema) -> Optional[Quote]:
        if self.quote_exists(data.text):
            logger.debug(f"Cita duplicada, omitida: {data.text[:50]}...")
            return None

        author = self.get_or_create_author(data.author)
        tags = [self.get_or_create_tag(tag_name) for tag_name in data.tags]

        quote = Quote(text=data.text, author=author, tags=tags)
        self.db.add(quote)
        self.db.commit()
        self.db.refresh(quote)
        logger.info(f"Cita guardada con ID: {quote.id}")
        return quote

    def get_all(
        self,
        author: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Quote]:
        query = self.db.query(Quote).join(Quote.author)

        if author:
            query = query.filter(Author.name.ilike(f"%{author}%"))

        if tag:
            query = query.join(Quote.tags).filter(Tag.name.ilike(f"%{tag}%"))

        if search:
            query = query.filter(Quote.text.ilike(f"%{search}%"))

        return query.all()
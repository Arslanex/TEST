from typing import List, Optional
from datetime import datetime

from ..base.crud import BaseCRUD
from src.models.article import Article
from src.models.enums import NewsSource

class ArticleCRUD(BaseCRUD[Article]):
    """CRUD operations for Article model."""
    
    def __init__(self):
        super().__init__(Article, "articles")

    async def get_by_source(self, source: NewsSource, limit: int = 10) -> List[Article]:
        """Get articles by news source."""
        return await self.get_many(
            filter_query={"article_source": source.value},
            limit=limit,
            sort_by=[("publish_date", -1)]
        )

    async def get_recent_articles(self, days: int = 7, limit: int = 50) -> List[Article]:
        """Get articles published in the last N days."""
        date_threshold = datetime.utcnow() - datetime.timedelta(days=days)
        return await self.get_many(
            filter_query={"publish_date": {"$gte": date_threshold}},
            limit=limit,
            sort_by=[("publish_date", -1)]
        )

    async def find_duplicates(self, article: Article) -> Optional[Article]:
        # Convert article.article_link to a plain string
        filter_query = {"article_link": str(article.article_link)}
        results = await self.get_many(filter_query=filter_query, limit=1)
        return results[0] if results else None

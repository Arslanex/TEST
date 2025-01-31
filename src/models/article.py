from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from bson import ObjectId
from .enums import NewsSource, ScraperStatus

class PyObjectId(ObjectId):
    """Custom type for handling MongoDB ObjectId."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, **kwargs):
        """Return the JSON Schema for the ObjectId type."""
        field_schema.update(type="string")
        return field_schema

class Article(BaseModel):
    """
    Article model with MongoDB support.
    Handles both web scraping and database storage.
    """
    # MongoDB fields
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = Field(default=True)

    # Core article fields
    article_source: NewsSource
    article_name: str
    article_link: HttpUrl
    publish_date: Optional[datetime] = None
    content: str

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        },
        json_schema_extra={
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "article_source": "GROQ",
                "article_name": "Google Gemini Ultra Performans Testleri",
                "article_link": "https://airesearch.blog/gemini-ultra-benchmarks",
                "publish_date": "2024-01-30T00:00:00Z",
                "content": "Gemini Ultra, MMLU'da %92.3 skorla GPT-4'ü geride bıraktı...",
                "created_at": "2024-01-30T00:00:00Z",
                "updated_at": "2024-01-30T00:00:00Z",
                "version": 1,
                "metadata": {},
                "is_active": True
            }
        }
    )

    # Database methods
    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()

    def increment_version(self):
        """Increment the document version."""
        self.version += 1
        self.update_timestamp()

    def add_metadata(self, key: str, value: Any):
        """Add or update metadata."""
        self.metadata[key] = value
        self.update_timestamp()

    def remove_metadata(self, key: str) -> bool:
        """Remove metadata key."""
        if key in self.metadata:
            del self.metadata[key]
            self.update_timestamp()
            return True
        return False

    def soft_delete(self):
        """Mark article as inactive."""
        self.is_active = False
        self.update_timestamp()

    def restore(self):
        """Restore a soft-deleted article."""
        self.is_active = True
        self.update_timestamp()

    # MongoDB conversion methods
    def to_mongo(self, exclude_none: bool = True) -> dict:
        """Convert to MongoDB document format."""
        data = self.dict(by_alias=True, exclude_none=exclude_none)
        if "_id" in data and data["_id"] is None:
            data.pop("_id")
        return data

    @classmethod
    def from_mongo(cls, data: dict):
        """Create instance from MongoDB document."""
        if not data:
            return None
        return cls.parse_obj(data)

    def summarize(self) -> str:
        """Get a brief summary of the article."""
        return (
            f"Article: {self.article_name}\n"
            f"Source: {self.article_source.value}\n"
            f"Date: {self.publish_date.strftime('%Y-%m-%d %H:%M:%S') if self.publish_date else 'N/A'}\n"
            f"URL: {self.article_link}\n"
            f"Status: {'Active' if self.is_active else 'Inactive'}"
        )

class ScrapingEvent(BaseModel):
    """Base model for scraping events"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: NewsSource
    event_type: str
    details: Dict[str, Any] = Field(default_factory=dict)

class ScrapingResult(BaseModel):
    """Result of scraping operation"""
    status: ScraperStatus
    articles: List[Article] = Field(default_factory=list)
    error_message: Optional[str] = None
    execution_time: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    stats: Dict[str, int] = Field(
        default_factory=lambda: {
            'attempted': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0
        }
    )
    events: List[ScrapingEvent] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "status": "SUCCESS",
                "articles": [],
                "error_message": None,
                "execution_time": 1.23,
                "timestamp": "2024-01-30T00:00:00Z",
                "stats": {
                    "attempted": 6,
                    "successful": 4,
                    "failed": 1,
                    "skipped": 1
                },
                "events": []
            }
        }
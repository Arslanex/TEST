from datetime import datetime
from typing import Optional, List, Dict, Any, Annotated
from pydantic import BaseModel, HttpUrl, Field, ConfigDict, GetJsonSchemaHandler, BeforeValidator
from pydantic.json_schema import JsonSchemaValue
from bson import ObjectId
from .enums import NewsSource, ScraperStatus
import json

def validate_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")

PyObjectId = Annotated[ObjectId, BeforeValidator(validate_object_id)]

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
    article_content: str

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        use_enum_values=True,  # Automatically convert enums to their underlying values
        json_encoders={
            ObjectId: str,
            HttpUrl: str,  # Convert HttpUrl to string for JSON serialization
            datetime: lambda dt: dt.isoformat()
        },
        json_schema_extra={
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "article_source": "GROQ",
                "article_name": "Google Gemini Ultra Performans Testleri",
                "article_link": "https://airesearch.blog/gemini-ultra-benchmarks",
                "publish_date": "2024-01-30T00:00:00Z",
                "article_content": "Gemini Ultra, MMLU'da %92.3 skorla GPT-4'ü geride bıraktı...",
                "created_at": "2024-01-30T00:00:00Z",
                "updated_at": "2024-01-30T00:00:00Z",
                "version": 1,
                "metadata": {},
                "is_active": True
            }
        }
    )

    def model_dump(self, *args, **kwargs):
        """Override model_dump to convert HttpUrl to string for MongoDB."""
        data = super().model_dump(*args, **kwargs)
        if 'article_link' in data and isinstance(data['article_link'], HttpUrl):
            data['article_link'] = str(data['article_link'])
        return data

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
        # Manually convert article_link from HttpUrl to str
        if "article_link" in data and data["article_link"] is not None:
            data["article_link"] = str(data["article_link"])
        if data.get("_id") is None:
            data.pop("_id", None)
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
            f"Source: {self.article_source}\n"
            f"Date: {self.publish_date.strftime('%Y-%m-%d %H:%M:%S') if self.publish_date else 'N/A'}\n"
            f"URL: {self.article_link}\n"
            f"Status: {'Active' if self.is_active else 'Inactive'}"
        )

    def to_mongo(self, exclude_none: bool = True) -> dict:
        """
        Convert the Article instance to a dictionary for MongoDB.
        This version uses model_dump_json to ensure all custom encoders are applied.
        """
        # Produce a JSON string with encoders applied
        json_str = self.model_dump_json(by_alias=True, exclude_none=exclude_none)
        # Convert the JSON string back into a Python dict
        data = json.loads(json_str)
        # Remove _id if it is None
        if data.get("_id") is None:
            data.pop("_id", None)
        return data

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

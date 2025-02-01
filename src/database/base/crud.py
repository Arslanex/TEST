from typing import Generic, TypeVar, Optional, List, Any, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel

from ..config import DatabaseConfig

ModelType = TypeVar("ModelType", bound=BaseModel)

class BaseCRUD(Generic[ModelType]):
    """
    Base class for CRUD operations.
    Implements common database operations that can be inherited by specific model CRUDs.
    """
    # Class-level database reference
    _db: Optional[AsyncIOMotorDatabase] = None

    def __init__(self, model: type[ModelType], collection_name: str):
        self.model = model
        self.collection_name = collection_name
        
        # Initialize database connection if not already initialized
        if BaseCRUD._db is None:
            BaseCRUD._db = DatabaseConfig.get_database()
            
        self._collection = BaseCRUD._db[collection_name]

    async def create(self, document: ModelType) -> ModelType:
        """Create a new document in the collection."""
        doc_dict = document.model_dump(by_alias=True, exclude_none=True)
        doc_dict["created_at"] = datetime.utcnow()
        doc_dict["updated_at"] = doc_dict["created_at"]
        
        result = await self._collection.insert_one(doc_dict)
        return await self.get_by_id(result.inserted_id)

    async def get_by_id(self, id: str | ObjectId) -> Optional[ModelType]:
        """Retrieve a document by its ID."""
        if isinstance(id, str):
            id = ObjectId(id)
        
        doc = await self._collection.find_one({"_id": id})
        return self.model.model_validate(doc) if doc else None

    async def get_many(
        self,
        filter_query: Dict[str, Any] = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: List[tuple] = None
    ) -> List[ModelType]:
        """Retrieve multiple documents with filtering, pagination and sorting."""
        filter_query = filter_query or {}
        cursor = self._collection.find(filter_query).skip(skip).limit(limit)
        
        if sort_by:
            cursor = cursor.sort(sort_by)
        
        documents = await cursor.to_list(length=limit)
        return [self.model.model_validate(doc) for doc in documents]

    async def update(
        self,
        id: str | ObjectId,
        update_data: Dict[str, Any],
        upsert: bool = False
    ) -> Optional[ModelType]:
        """Update a document by its ID."""
        if isinstance(id, str):
            id = ObjectId(id)

        update_data["updated_at"] = datetime.utcnow()
        update_dict = {"$set": update_data}
        
        result = await self._collection.find_one_and_update(
            {"_id": id},
            update_dict,
            upsert=upsert,
            return_document=True
        )
        
        return self.model.model_validate(result) if result else None

    async def delete(self, id: str | ObjectId) -> bool:
        """Delete a document by its ID."""
        if isinstance(id, str):
            id = ObjectId(id)
            
        result = await self._collection.delete_one({"_id": id})
        return result.deleted_count > 0

    async def count(self, filter_query: Dict[str, Any] = None) -> int:
        """Count documents matching the filter criteria."""
        filter_query = filter_query or {}
        return await self._collection.count_documents(filter_query)

    async def exists(self, filter_query: Dict[str, Any]) -> bool:
        """Check if any document matches the filter criteria."""
        return await self.count(filter_query) > 0

    async def bulk_create(self, documents: List[ModelType]) -> List[ModelType]:
        """Create multiple documents in one operation."""
        if not documents:
            return []
            
        docs_dict = [
            {
                **doc.model_dump(by_alias=True, exclude_none=True),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            for doc in documents
        ]
        
        result = await self._collection.insert_many(docs_dict)
        return await self.get_many({"_id": {"$in": result.inserted_ids}})

    async def bulk_update(
        self,
        filter_query: Dict[str, Any],
        update_data: Dict[str, Any]
    ) -> int:
        """Update multiple documents matching the filter criteria."""
        update_data["updated_at"] = datetime.utcnow()
        update_dict = {"$set": update_data}
        
        result = await self._collection.update_many(filter_query, update_dict)
        return result.modified_count

    async def bulk_delete(self, filter_query: Dict[str, Any]) -> int:
        """Delete multiple documents matching the filter criteria."""
        result = await self._collection.delete_many(filter_query)
        return result.deleted_count
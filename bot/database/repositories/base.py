"""Base repository with common CRUD operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.base import Base


class BaseRepository[ModelType: Base]:
    """Base repository class with common CRUD operations."""

    def __init__(self, model: type[ModelType], session: AsyncSession):
        """Initialize repository.

        Args:
            model: SQLAlchemy model class
            session: Async database session
        """
        self.model = model
        self.session = session

    async def create(self, **kwargs) -> ModelType:
        """Create a new record.

        Args:
            **kwargs: Model fields and values

        Returns:
            Created model instance
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: int) -> ModelType | None:
        """Get a record by ID.

        Args:
            id: Record ID

        Returns:
            Model instance or None if not found
        """
        return await self.session.get(self.model, id)

    async def get_all(self, limit: int | None = None, offset: int = 0) -> list[ModelType]:
        """Get all records.

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of model instances
        """
        query = select(self.model).offset(offset)
        if limit is not None:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, instance: ModelType, **kwargs) -> ModelType:
        """Update a record.

        Args:
            instance: Model instance to update
            **kwargs: Fields to update

        Returns:
            Updated model instance
        """
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelType) -> None:
        """Delete a record.

        Args:
            instance: Model instance to delete
        """
        await self.session.delete(instance)
        await self.session.flush()

    async def count(self) -> int:
        """Count total number of records.

        Returns:
            Total count
        """
        from sqlalchemy import func

        query = select(func.count()).select_from(self.model)
        result = await self.session.execute(query)
        return result.scalar_one()

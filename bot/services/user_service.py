"""User service for managing Telegram users."""

from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.user import User
from bot.database.repositories.user_repo import UserRepository


class UserService:
    """Service for user operations."""

    def __init__(self, session: AsyncSession):
        """Initialize user service.

        Args:
            session: Async database session
        """
        self.repo = UserRepository(session)

    async def get_or_create_user(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        language_code: str | None = None,
    ) -> tuple[User, bool]:
        """Get existing user or create new one.

        Args:
            telegram_id: Telegram user ID
            username: Telegram username
            first_name: User's first name
            last_name: User's last name
            language_code: User's language code

        Returns:
            Tuple of (User instance, created flag)
        """
        return await self.repo.get_or_create_by_telegram_id(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
        )

    async def get_user_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get user by Telegram ID.

        Args:
            telegram_id: Telegram user ID

        Returns:
            User instance or None
        """
        return await self.repo.get_by_telegram_id(telegram_id)

    async def update_user(
        self,
        user: User,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        language_code: str | None = None,
    ) -> User:
        """Update user information.

        Args:
            user: User instance to update
            username: New username
            first_name: New first name
            last_name: New last name
            language_code: New language code

        Returns:
            Updated user instance
        """
        update_data = {}
        if username is not None:
            update_data["username"] = username
        if first_name is not None:
            update_data["first_name"] = first_name
        if last_name is not None:
            update_data["last_name"] = last_name
        if language_code is not None:
            update_data["language_code"] = language_code

        if update_data:
            return await self.repo.update(user, **update_data)
        return user

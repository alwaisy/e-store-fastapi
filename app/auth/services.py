from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .models import User
from .schema import UserStoreSchema
from .utils import gen_passwd_hash


class AuthService:
    async def store(self, user_data: UserStoreSchema, session: AsyncSession):
        user_dict = user_data.model_dump()
        new_user = User(**user_dict)

        # hash password
        new_user.password_hash = gen_passwd_hash(user_data.password)

        # add and commit
        session.add(new_user)
        await session.commit()

        return new_user

    async def update(self, user: User, user_update: dict, session: AsyncSession):
        for k, v in user_update.items():
            setattr(user, k, v)

        await session.commit()

        return user

    async def show(self, user_email: str, session: AsyncSession):
        query = select(User).where(User.email == user_email)

        response = await session.exec(query)
        user = response.first()

        return user

    async def check_user(self, user_email: str, session: AsyncSession):
        """
        Check if user exists in the database.

        Args:
            user_email (str): Email of the user to check.
            session (AsyncSession): SQLAlchemy async session.

        Returns:
            bool: True if the user exists, False otherwise.
        """
        user = await self.show(user_email, session)

        return True if user is not None else False

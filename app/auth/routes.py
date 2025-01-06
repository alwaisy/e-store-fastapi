from fastapi import APIRouter, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from .schema import UserStoreSchema, UserSchema
from .services import AuthService
from ..db.main import get_session
from ..errors import UserAlreadyExists

auth_router = APIRouter()
auth_service = AuthService()


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserSchema)
async def signup(user_data: UserStoreSchema, session: AsyncSession = Depends(get_session)):
    user_exists = await auth_service.check_user(user_data.email, session)

    if user_exists:
        raise UserAlreadyExists()
    else:
        new_user = await auth_service.store(user_data, session)
        return new_user

from datetime import timedelta, datetime

from fastapi import APIRouter, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from .dependencies import RefreshTokenBearer, get_current_user, RoleChecker
from .schema import UserStoreSchema, UserSchema, UserLoginSchema
from .services import AuthService
from .utils import verify_password, create_access_token
from ..db.main import get_session
from ..errors import UserAlreadyExists, InvalidCredentials, InvalidToken

auth_router = APIRouter()
auth_service = AuthService()
role_checker = RoleChecker(["admin", "user"])


@auth_router.post(
    "/signup", status_code=status.HTTP_201_CREATED, response_model=UserSchema
)
async def signup(
    user_data: UserStoreSchema, session: AsyncSession = Depends(get_session)
):
    user_exists = await auth_service.check_user(user_data.email, session)

    if user_exists:
        raise UserAlreadyExists()
    else:
        new_user = await auth_service.store(user_data, session)
        return new_user


@auth_router.post("/login")
async def login(
    login_data: UserLoginSchema, session: AsyncSession = Depends(get_session)
):
    email = login_data.email
    password = login_data.password

    user = await auth_service.show(email, session)

    if user is not None:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_access_token(
                user_data={"email": user.email, "user_id": str(user.id)}
            )
            refresh_token = create_access_token(
                user_data={"email": user.email, "user_id": str(user.id)},
                refresh=True,
                expiry=timedelta(days=2),
            )

            return JSONResponse(
                content={
                    # "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    # 'user': {
                    #     'email': user.email,
                    #     'id': str(user.id)
                    # }
                }
            )
    else:
        raise InvalidCredentials()


@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])

        return JSONResponse(content={"access_token": new_access_token})

    raise InvalidToken


@auth_router.get("/me", response_model=UserSchema, dependencies=[Depends(role_checker)])
async def get_current_user(user=Depends(get_current_user)):
    return user

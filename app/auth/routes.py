import logging
from datetime import timedelta, datetime

from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from .dependencies import RefreshTokenBearer, get_current_user, RoleChecker
from .schema import (
    UserStoreSchema,
    UserSchema,
    UserLoginSchema,
    EmailSchema,
    PasswordResetConfirmSchema,
    PasswordResetRequestSchema,
)
from .services import AuthService
from .utils import (
    verify_password,
    create_access_token,
    create_url_safe_token,
    gen_password_hash,
    verify_token,
)
from ..config import Config
from ..db.main import get_session
from ..db.redis import add_jti_to_blocklist
from ..errors import UserAlreadyExists, InvalidCredentials, InvalidToken, UserNotFound
from ..mail import mail, create_message

auth_router = APIRouter()
auth_service = AuthService()
role_checker = RoleChecker(["admin", "user"])


@auth_router.post("/send-mail")
async def send_mail(emails: EmailSchema):
    emails = emails.addresses

    html = "<h1>Welcome to the app</h1>"
    subject = "Welcome to our app"

    message = create_message(recipients=emails, subject=subject, body=html)
    await mail.send_message(message)

    return {"message": "Email sent successfully"}


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserStoreSchema, session: AsyncSession = Depends(get_session)
):
    user_exists = await auth_service.check_user(user_data.email, session)

    if user_exists:
        raise UserAlreadyExists()
    else:
        new_user = await auth_service.store(user_data, session)
        email = new_user.email

        token = create_url_safe_token({"email": email}, "email_verification")
        link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

        html = f"""
        <h1>Verify your Email</h1>
        <p>Please click this <a href="{link}">link</a> to verify your email</p>
        """
        emails = [email]
        subject = "Verify Your email"

        await mail.send_message(create_message(emails, subject, html))

        return {
            "message": "Account Created! Check email to verify your account",
            "user": new_user,
        }


@auth_router.get("/verify/{token}")
async def verify_email(token: str, session: AsyncSession = Depends(get_session)):
    payload = await verify_token(token, "email_verification")
    user_email = payload.get("email")

    if user_email:
        user = await auth_service.show(user_email, session)

        if not user:
            raise UserNotFound()

        await auth_service.update(user, {"is_verified": True}, session)
        return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK,
        )
    else:
        return JSONResponse(
            content={"message": "Error occurred during verification"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


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


@auth_router.post("/reset-password")
async def password_reset_request(email_data: PasswordResetRequestSchema):
    email = email_data.email

    token = create_url_safe_token({"email": email}, "password_reset", 6)

    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"

    emails = [email]
    html_message = f"""
    <h1>Reset Your Password</h1>
    <p>Please click this <a href="{link}">link</a> to Reset Your Password</p>
    """
    subject = "Reset Your Password"

    await mail.send_message(create_message(emails, subject, html_message))

    return JSONResponse(
        content={
            "message": "Please check your email for instructions to reset your password",
        },
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/reset-password/{token}")
async def reset_account_password(
    token: str,
    passwords: PasswordResetConfirmSchema,
    session: AsyncSession = Depends(get_session),
):
    try:
        if not passwords.new_password == passwords.confirm_new_password:
            raise HTTPException(
                detail="Passwords do not match", status_code=status.HTTP_400_BAD_REQUEST
            )

        payload = await verify_token(token, "password_reset")
        user_email = payload.get("email")

        user = await auth_service.show(user_email, session)
        if not user:
            raise UserNotFound()

        passwd_hash = gen_password_hash(passwords.new_password)
        await auth_service.update(user, {"password_hash": passwd_hash}, session)
        await add_jti_to_blocklist(payload["jti"])

        return JSONResponse(
            content={"message": "Password reset successfully"},
            status_code=status.HTTP_200_OK,
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions to keep their specific status codes/messages
    except Exception as err:
        logging.error(f"Password reset error: {str(err)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while resetting password",
        )

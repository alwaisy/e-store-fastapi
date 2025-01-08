import logging
import uuid
from datetime import timedelta, datetime

import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext

from app.config import Config
from app.db.redis import token_in_blocklist

passwd_context = CryptContext(schemes=["bcrypt"])

ACCESS_TOKEN_EXPIRY = 3600


def gen_password_hash(password: str) -> str:
    """
    Generates a hashed password based on `password`.

    Args:
        password: The password to be hashed.

    Returns:
        A hashed password string.
    """
    return passwd_context.hash(password)


def verify_password(password: str, passwd_hash: str) -> bool:
    """
    Verifies if a password matches a given passwd_hash.

    Args:
        password: The password to be verified.
        passwd_hash: The passwd_hash to be verified against.

    Returns:
        True if the password matches the passwd_hash, False otherwise.
    """
    return passwd_context.verify(password, passwd_hash)


def create_access_token(
    user_data: dict, expiry: timedelta = None, refresh: bool = False
):
    """
    Creates a JSON Web Token (JWT) for user authentication.

    Args:
        user_data (dict): The user information to include in the token payload.
        expiry (timedelta): The expiration time for the token.
        refresh (bool, optional): A flag indicating if the token is a refresh token. Defaults to False.

    Returns:
        str: The encoded JWT as a string.
    """
    payload = {}

    payload["user"] = user_data
    payload["exp"] = datetime.now() + (
        expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)
    )
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refresh

    token = jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)

    return token


def decode_token(token: str):
    """
    Decodes a JSON Web Token (JWT) to extract the payload.

    Args:
        token (str): The JWT encoded as a string.

    Returns:
        dict: The decoded payload if the token is valid.
        None: If the token is invalid or an error occurs during decoding.

    Raises:
        jwt.PyJWTError: If an error occurs during token decoding.
    """

    # print(token)

    if len(token) == 0:
        return None

    try:
        return jwt.decode(
            jwt=token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM]
        )
    except jwt.PyJWTError as err:
        logging.exception(err)
        return None


def create_url_safe_token(data: dict):
    """
    Create a JWT token for password reset with JTI
    """
    payload = {
        **data,
        "exp": datetime.now() + timedelta(hours=1),
        "jti": str(uuid.uuid4()),
        "type": "password_reset",
    }

    return jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)


async def verify_reset_token(token: str) -> dict:
    """
    Verify password reset token and check blocklist
    """
    payload = decode_token(token)

    if not payload or payload.get("type") != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token"
        )

    if await token_in_blocklist(payload["jti"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has already been used",
        )

    return payload

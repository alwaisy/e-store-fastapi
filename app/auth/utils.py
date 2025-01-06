import logging
import uuid
from datetime import timedelta, datetime

import jwt
from passlib.context import CryptContext

from app.config import Config

passwd_context = CryptContext(schemes=["bcrypt"])

ACCESS_TOKEN_EXPIRY = 3600


def gen_passwd_hash(password: str) -> str:
    """
    Generates a hashed password based on `password`.

    Args:
        password: The password to be hashed.

    Returns:
        A hashed password string.
    """
    return passwd_context.hash(password)


def verify_password(password: str, hash: str) -> bool:
    """
    Verifies if a password matches a given hash.

    Args:
        password: The password to be verified.
        hash: The hash to be verified against.

    Returns:
        True if the password matches the hash, False otherwise.
    """
    return passwd_context.verify(password, hash)


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
    try:
        return jwt.decode(
            jwt=token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM]
        )
    except jwt.PyJWTError as err:
        logging.exception(err)
        return None

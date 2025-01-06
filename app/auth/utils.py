from passlib.context import CryptContext

passwd_context = CryptContext(schemes=['bcrypt'])


def gen_passwd_hash(password: str) -> str:
    """
    Generates a hashed password based on `password`.

    Args:
        password: The password to be hashed.

    Returns:
        A hashed password string.
    """
    return passwd_context.hash(password)


def verify_passwd(password: str, hash: str) -> bool:
    """
    Verifies if a password matches a given hash.

    Args:
        password: The password to be verified.
        hash: The hash to be verified against.

    Returns:
        True if the password matches the hash, False otherwise.
    """
    return passwd_context.verify(password, hash)

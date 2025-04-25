import argon2
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)
from user_registration.database.model import User
from user_registration.database.session import SessionDep

ph = argon2.PasswordHasher()


def get_hash(password: str):
    """Return a hashed password."""
    return ph.hash(password)


def verify_password(password: str, user: User, session: SessionDep):
    """Verify if the given password matches the hashed password."""
    try:
        ph.verify(user.password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False
    # Should do a rehashing when necessary
    # if ph.check_needs_rehash(user.hashed_password):
    #     set_password_hash_for_user(user, ph.hash(password), session)
    return True

"""
CREDIT ASSISTANT - Password Security
Phase 3: bcrypt password hashing helpers

Uses bcrypt (work-factor 12) — deliberately slow to resist brute-force
attacks.  Plaintext passwords are NEVER logged, stored, or returned.
"""

import bcrypt


# Work factor: 12 is a good balance of security vs speed for 2024+.
# Increase to 13-14 for higher-security environments (slower login).
_ROUNDS = 12


def hash_password(plaintext: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Parameters
    ----------
    plaintext : str
        The user''s password as entered (never stored).

    Returns
    -------
    str
        A bcrypt hash string suitable for storage in the database.
    """
    encoded = plaintext.encode("utf-8")
    hashed = bcrypt.hashpw(encoded, bcrypt.gensalt(rounds=_ROUNDS))
    return hashed.decode("utf-8")


def verify_password(plaintext: str, hashed: str) -> bool:
    """
    Verify a plaintext password against a stored bcrypt hash.

    Parameters
    ----------
    plaintext : str
        The password the user typed during login.
    hashed : str
        The bcrypt hash retrieved from the database.

    Returns
    -------
    bool
        True if the password matches, False otherwise.
    """
    try:
        return bcrypt.checkpw(plaintext.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        # Malformed hash, binary mismatch, etc.
        return False

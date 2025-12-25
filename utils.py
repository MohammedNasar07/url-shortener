# utils.py
# Converts numbers into short codes using Base62 (0-9, A-Z, a-z).

ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
BASE = len(ALPHABET)  # = 62


def encode_base62(num: int) -> str:
    """
    Convert a number (like 123) into Base62 text (like "1Z").
    """
    if num == 0:
        return ALPHABET[0]
    result = []
    while num > 0:
        num, remainder = divmod(num, BASE)  # Divide by 62, get remainder
        result.append(ALPHABET[remainder])  # Pick letter from ALPHABET
    return "".join(reversed(result))  # Reverse to get correct order


def validate_code(code: str) -> bool:
    """Check that the code has only Base62 letters and is 1–16 chars."""
    if not (1 <= len(code) <= 16):
        return False
    return all(c in ALPHABET for c in code)

import secrets
import string
import time

ALPHABET = string.digits + string.ascii_letters
BASE = len(ALPHABET)

def genturl():
    num = time.time_ns() % (BASE ** 5)
    return ''.join(ALPHABET[num // (BASE ** i) % BASE] for i in range(4, -1, -1))

def gentoken():
    return secrets.token_hex(16)

# Shuffled alphabet to prevent sequential guessing (Security)
ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
BASE = len(ALPHABET)


def encode_base62(id_num: int) -> str:
    """Converts an integer to a Base62 string."""
    if id_num == 0:
        return ALPHABET[0]
    arr = []
    while id_num:
        id_num, rem = divmod(id_num, BASE)
        arr.append(ALPHABET[rem])
    arr.reverse()
    return "".join(arr)


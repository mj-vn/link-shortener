ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
BASE = len(ALPHABET)
# Map char back to index for fast O(1) lookup
ALPHABET_MAP = {char: index for index, char in enumerate(ALPHABET)}

def encode_base62(id_num: int) -> str:
    """Converts Integer ID -> Base62 String"""
    if id_num == 0:
        return ALPHABET[0]
    arr = []
    while id_num:
        id_num, rem = divmod(id_num, BASE)
        arr.append(ALPHABET[rem])
    arr.reverse()
    return "".join(arr)

def decode_base62(short_code: str) -> int:
    """Converts Base62 String -> Integer ID"""
    id_num = 0
    for char in short_code:
        if char not in ALPHABET_MAP:
            raise ValueError("Invalid character in short code")
        id_num = id_num * BASE + ALPHABET_MAP[char]
    return id_num
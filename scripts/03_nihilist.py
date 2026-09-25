ALPHABET = "PSZLMYQEBJARTFCHNUGVKDOXIW".replace("I", "")
CIPHER = [56, 75, 65, 76, 35, 56, 75, 63, 97, 66, 67, 47, 72]
KEY = "AROUSL"


def square():
    return {ch: divmod(i, 5) for i, ch in enumerate(ALPHABET)}


def coords(text, table):
    out = []
    for ch in text:
        row, col = table[ch]
        out.append((row + 1) * 10 + (col + 1))
    return out


def decrypt(cipher, key):
    table = square()
    key_nums = coords(key, table)
    inv = {v: ch for ch, v in table.items()}
    letters = []
    for i, num in enumerate(cipher):
        diff = num - key_nums[i % len(key_nums)]
        row, col = divmod(diff, 10)
        letters.append(inv[(row - 1, col - 1)])
    return letters


if __name__ == "__main__":
    table = square()
    key_nums = coords(KEY, table)
    letters = decrypt(CIPHER, KEY)
    print("square:")
    for r in range(5):
        print(" ".join(ALPHABET[r * 5:(r + 1) * 5]))
    print("key", KEY, key_nums)
    print("diff", [c - key_nums[i % len(key_nums)] for i, c in enumerate(CIPHER)])
    word = "".join(letters)
    print(word)
    assert word == "JUSTENGAGEWTH"

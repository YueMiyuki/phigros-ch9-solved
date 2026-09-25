LEFT = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
RIGHT = "PSZLMYQEBJARTFCHNUGVKDOXIW"
CT = "ZGJGDGTDNUIOSQQCLIWWCWIIADNOFQDAEMG"


def permute(left, right, pos):
    left = left[pos:] + left[:pos]
    left = left[0:1] + left[2:14] + left[1:2] + left[14:]
    right = right[pos:] + right[:pos]
    right = right[1:] + right[:1]
    right = right[0:2] + right[3:14] + right[2:3] + right[14:]
    return left, right


def decrypt(ct, left=LEFT, right=RIGHT):
    left, right = list(left), list(right)
    out = []
    for ch in ct:
        pos = left.index(ch)
        out.append(right[pos])
        left, right = permute(left, right, pos)
    return "".join(out)


if __name__ == "__main__":
    plain = decrypt(CT)
    assert plain == "WERJETZTALLEINISTWIRDESLANGEBLEIBEN"
    print(plain)

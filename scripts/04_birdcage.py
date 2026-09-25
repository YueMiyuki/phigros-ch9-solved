import json
import random
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

API = "https://wiki.pigeon-games.com/outside_the_birdcage/api.php?fp="


def chrome(v):
    return (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Safari/537.36"
    )


def firefox(v):
    return (
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{v}.0) "
        f"Gecko/20100101 Firefox/{v}.0"
    )


def batch_uas(k=10):
    versions = set()
    while len(versions) < k:
        versions.add(random.randint(1, 131))
    uas = []
    for i, v in enumerate(versions):
        uas.append(chrome(v) if i % 2 == 0 else firefox(v))
    return uas


def fnv(s, seed):
    h = seed & 0xFFFFFFFF
    for ch in s:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def fingerprint(user_agent):
    # Same mix as the page: four FNV-1a hashes of the browser fields.
    langs = random.choice(["en-US", "zh-CN", "ja-JP", "en-GB", "zh-TW"])
    screen = (
        f"{random.randint(1280, 2560)}x{random.randint(720, 1600)}"
        f"x{random.choice([24, 30, 32])}x{random.choice([1, 2])}"
    )
    parts = [
        user_agent,
        langs,
        langs,
        "Win32",
        "hc" + str(random.choice([4, 8, 12, 16])),
        "dm" + str(random.choice([4, 8, 16])),
        "mt" + str(random.choice([0, 1, 5, 10])),
        "sc" + screen,
        "tz" + str(random.choice([-480, -420, -60, 0, 60, 540])),
        "zone" + random.choice(["Asia/Shanghai", "America/Los_Angeles", "Europe/London", "Asia/Tokyo"]),
        "cv" + "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/") for _ in range(80)),
        "gv" + random.choice(["Google Inc. (NVIDIA)", "Google Inc. (Intel)", "Google Inc. (AMD)"]),
        "gr" + random.choice(["ANGLE (NVIDIA, D3D11)", "ANGLE (Intel, D3D11)", "ANGLE (AMD, D3D11)"]),
    ]
    s = "|".join(parts)
    return (
        f"{fnv(s, 2166136261):08x}"
        f"{fnv(s, 1099511628):08x}"
        f"{fnv(s + '#2', 2166136261):08x}"
        f"{fnv(s + '#3', 1099511628):08x}"
    )


def fetch(fp, ua):
    # print("fetching", fp, ua, flush=True)
    req = urllib.request.Request(
        API + fp,
        headers={"User-Agent": ua, "Referer": "https://wiki.pigeon-games.com/outside_the_birdcage/"},
    )
    delay = 5
    for _ in range(6):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print("404", fp, flush=True)
                return None
            if e.code != 502:
                raise
            print("502, retry in", delay, flush=True)
            time.sleep(delay)
            delay = min(delay * 2, 40)
    else:
        raise RuntimeError("502")
    if not data.get("ok"):
        raise RuntimeError(data)
    return data["index"], data["text"], data["total"]


def collect(limit=100000): # fucking limits
    found = {}
    total = None
    n = 0
    repeats = 0
    with ThreadPoolExecutor(max_workers=20) as pool:
        while len(found) < (total or 13) and n < limit:
            uas = batch_uas(10)
            batch = []
            for ua in uas:
                if n >= limit:
                    break
                fp = fingerprint(ua)
                batch.append((fp, ua))
                n += 1
            for got in pool.map(lambda pair: fetch(*pair), batch):
                if got is None:
                    continue
                index, text, got_total = got
                total = got_total
                if index in found:
                    repeats += 1
                    print("repeat", index, repr(text), flush=True)
                    if repeats > 20:
                        print("20 repeats, wait 5s", flush=True)
                        time.sleep(5)
                        repeats = 0
                else:
                    found[index] = text
                    repeats = 0
                    print(index, repr(text), flush=True)
            if len(found) >= (total or 13):
                break
    if total is None or len(found) < total:
        raise RuntimeError(f"got {sorted(found)} of {total} after {n} requests")
    return [found[i] for i in range(total)]


if __name__ == "__main__":
    for i, text in enumerate(collect()):
        print(i, repr(text))

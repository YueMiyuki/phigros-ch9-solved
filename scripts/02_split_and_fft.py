from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "products" / "start-0.png"
OUT = ROOT / "products" / "start-0-fft.png"


def save_fft(src, dest):
    im = Image.open(src).convert("L")
    arr = np.asarray(im, dtype=np.float32)
    spec = np.fft.fftshift(np.fft.fft2(arr))
    mag = np.log1p(np.abs(spec))
    mag = mag / mag.max() * 255
    Image.fromarray(mag.astype(np.uint8)).save(dest)
    return im.size


if __name__ == "__main__":
    size = save_fft(SRC, OUT)
    print(SRC, size)
    print(OUT)

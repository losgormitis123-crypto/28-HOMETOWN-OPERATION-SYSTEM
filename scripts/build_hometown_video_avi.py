from pathlib import Path
import math
import struct
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
IMAGE_PATH = ROOT / "00_INPUT/family_materials/photos/2026-07-09_湖北老家_水田_清晨田边_自己.jpg"
OUT_DIR = ROOT / "output"
OUT_DIR.mkdir(exist_ok=True)
OUT_AVI = OUT_DIR / "2026-07-09_老家水田_最终成片.avi"

W, H = 540, 960
FPS = 6

FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
]


def load_font(size):
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


TITLE_FONT = load_font(31)
SUB_FONT = load_font(28)
SMALL_FONT = load_font(19)

CAPTIONS = [
    ("这是湖北老家老屋旁边的田埂，走路几分钟就到。", 4.5),
    ("我小时候，经常在这样的地方放牛。", 3.5),
    ("清晨的露水很重，绿色的野草上全是水珠。", 4.5),
    ("裤脚一走过去，很快就湿了。", 3.5),
    ("那时候我们会趁着早上还凉快，把家里的黄牛赶到田野上去。", 5.5),
    ("有些时候是一个人去。", 3.0),
    ("有些时候是和小伙伴一起去。", 3.0),
    ("小时候看这些水田、草丛、田埂，真的没觉得有什么特别。", 5.0),
    ("只想着快点长大，快点走出去。", 3.5),
    ("可离开老家18年以后，再看到这样的清晨，心里反而有点说不出来的感觉。", 6.0),
    ("这不是风景。", 2.5),
    ("这是我小时候真实生活过的地方。", 3.5),
    ("我现在42岁了，在工厂上班，也在学AI。", 4.0),
    ("学AI不是为了装成专家。", 3.0),
    ("我只是想把这些老家的照片、童年的记忆，一点点整理下来。", 5.0),
    ("以后孩子长大了，我想让他们知道：爸爸是从哪里来的。", 5.0),
    ("也想让他们知道，普通人只要还愿意学，人生就还能多一点选择。", 5.5),
    ("孩子，这是爸爸小时候清晨放黄牛走过的田边。", 5.0),
]


def aspect_fill(img, size):
    tw, th = size
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return img.crop((left, top, left + tw, top + th))


def wrap_text(draw, text, font, max_width):
    lines = []
    current = ""
    for ch in text:
        test = current + ch
        if draw.textbbox((0, 0), test, font=font)[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines


def make_frame(base, caption, frame_idx, total_frames):
    zoom = 1.0 + 0.025 * frame_idx / max(total_frames - 1, 1)
    zw, zh = int(W * zoom), int(H * zoom)
    z = base.resize((zw, zh), Image.Resampling.LANCZOS)
    left = (zw - W) // 2
    top = (zh - H) // 2
    frame = z.crop((left, top, left + W, top + H))
    draw = ImageDraw.Draw(frame, "RGBA")

    draw.rectangle((0, 0, W, 128), fill=(0, 0, 0, 80))
    draw.text((30, 32), "清晨的露水一上来", font=TITLE_FONT, fill=(255, 255, 255, 255))
    draw.text((30, 74), "我就想起小时候放牛", font=TITLE_FONT, fill=(255, 255, 255, 255))

    box_top = 640
    draw.rounded_rectangle((24, box_top, W - 24, H - 86), radius=18, fill=(0, 0, 0, 155))
    lines = wrap_text(draw, caption, SUB_FONT, W - 82)
    y = box_top + 40
    for line in lines[:5]:
        text_w = draw.textbbox((0, 0), line, font=SUB_FONT)[2]
        draw.text(((W - text_w) / 2, y), line, font=SUB_FONT, fill=(255, 255, 255, 255))
        y += 40

    draw.text((30, H - 55), "AI返乡计划 · 最后一代放牛娃", font=SMALL_FONT, fill=(255, 255, 255, 220))
    return frame.convert("RGB")


def avi_chunk(tag, data):
    pad = b"\0" if len(data) % 2 else b""
    return tag + struct.pack("<I", len(data)) + data + pad


def avi_list(tag, data):
    return b"LIST" + struct.pack("<I", len(data) + 4) + tag + data + (b"\0" if len(data) % 2 else b"")


def write_mjpeg_avi(path, frames, fps):
    frame_chunks = []
    idx_entries = []
    offset = 4
    for jpeg in frames:
        chunk = avi_chunk(b"00dc", jpeg)
        frame_chunks.append(chunk)
        idx_entries.append((b"00dc", 0x10, offset, len(jpeg)))
        offset += len(chunk)
    movi = avi_list(b"movi", b"".join(frame_chunks))

    frame_count = len(frames)
    us_per_frame = int(1_000_000 / fps)
    max_bytes = max(len(f) for f in frames)
    avih = struct.pack(
        "<IIIIIIIIIIIIIIII",
        us_per_frame, max_bytes * fps, 0, 0x10, frame_count, 0, 1,
        max_bytes, W, H, 0, 0, 0, 0, 0, 0
    )
    strh = struct.pack(
        "<4s4sIHHIIIIIIIIhhhh",
        b"vids", b"MJPG", 0, 0, 0, 0, 1, fps, 0,
        frame_count, max_bytes, 0xFFFFFFFF, 0, 0, 0, W, H
    )
    strf = struct.pack("<IiiHH4sIiiII", 40, W, H, 1, 24, b"MJPG", W * H * 3, 0, 0, 0, 0)
    hdrl = avi_list(b"hdrl", avi_chunk(b"avih", avih) + avi_list(b"strl", avi_chunk(b"strh", strh) + avi_chunk(b"strf", strf)))
    idx = b"".join(struct.pack("<4sIII", *entry) for entry in idx_entries)
    riff_data = hdrl + movi + avi_chunk(b"idx1", idx)
    path.write_bytes(b"RIFF" + struct.pack("<I", len(riff_data) + 4) + b"AVI " + riff_data)


def main():
    source = Image.open(IMAGE_PATH).convert("RGB")
    base = aspect_fill(source, (W, H)).filter(ImageFilter.UnsharpMask(radius=1, percent=105, threshold=3))
    total_frames = math.ceil(sum(d for _, d in CAPTIONS) * FPS)
    frames = []
    frame_no = 0
    for caption, seconds in CAPTIONS:
        for _ in range(max(1, round(seconds * FPS))):
            img = make_frame(base, caption, frame_no, total_frames)
            buf = BytesIO()
            img.save(buf, format="JPEG", quality=58, optimize=True)
            frames.append(buf.getvalue())
            frame_no += 1
    write_mjpeg_avi(OUT_AVI, frames, FPS)
    print(f"成片已生成：{OUT_AVI}")


if __name__ == "__main__":
    main()


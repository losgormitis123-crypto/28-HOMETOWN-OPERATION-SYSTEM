from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "00_INPUT/family_materials/photos/2026-07-09_湖北老家_水田_清晨田边_自己.jpg"
SRT = ROOT / "05_CONTENT_OUTPUT/video_scripts/2026-07-09_老家水田_视频成片/2026-07-09_老家水田_字幕.srt"
TEXT = ROOT / "05_CONTENT_OUTPUT/video_scripts/2026-07-09_老家水田_视频成片/2026-07-09_老家水田_口播纯文本.txt"
OUT_DIR = ROOT / "output"
OUT_DIR.mkdir(exist_ok=True)
VOICE = OUT_DIR / "hometown_voice.mp3"
VIDEO = OUT_DIR / "2026-07-09_老家水田_最终成片.mp4"


def run(cmd, check=True):
    print("+", " ".join(str(x) for x in cmd))
    return subprocess.run(cmd, check=check)


def parse_srt_end_seconds(path):
    text = path.read_text(encoding="utf-8")
    times = re.findall(r"-->\s*(\d\d):(\d\d):(\d\d),(\d\d\d)", text)
    if not times:
        return 76.0
    h, m, s, ms = times[-1]
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def try_make_voice():
    try:
        import edge_tts
    except Exception as exc:
        print(f"edge-tts 不可用，改用静音音轨：{exc}")
        return False

    async def make():
        content = TEXT.read_text(encoding="utf-8")
        communicate = edge_tts.Communicate(content, "zh-CN-YunxiNeural", rate="-8%")
        await communicate.save(str(VOICE))

    try:
        import asyncio
        asyncio.run(make())
        return VOICE.exists() and VOICE.stat().st_size > 1000
    except Exception as exc:
        print(f"生成口播音频失败，改用静音音轨：{exc}")
        return False


def build_video(has_voice):
    duration = parse_srt_end_seconds(SRT)
    temp_silent = OUT_DIR / "silent.m4a"
    audio = VOICE
    if not has_voice:
        run([
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
            "-t", str(duration),
            "-c:a", "aac",
            str(temp_silent),
        ])
        audio = temp_silent

    vf = (
        "scale=720:1280:force_original_aspect_ratio=increase,"
        "crop=720:1280,"
        "subtitles='{}':force_style='FontName=Noto Sans CJK SC,FontSize=14,"
        "PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,BorderStyle=1,"
        "Outline=1,Shadow=0,Alignment=2,MarginV=96'"
    ).format(str(SRT).replace("'", r"\'"))

    run([
        "ffmpeg", "-y",
        "-loop", "1",
        "-framerate", "30",
        "-i", str(IMAGE),
        "-i", str(audio),
        "-t", str(duration),
        "-vf", vf,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "medium",
        "-crf", "22",
        "-c:a", "aac",
        "-shortest",
        str(VIDEO),
    ])


def main():
    missing = [p for p in [IMAGE, SRT, TEXT] if not p.exists()]
    if missing:
        for p in missing:
            print(f"缺少文件：{p}")
        sys.exit(1)
    has_voice = try_make_voice()
    build_video(has_voice)
    print(f"成片已生成：{VIDEO}")


if __name__ == "__main__":
    main()


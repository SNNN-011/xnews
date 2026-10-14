"""xnews: X/Twitter video -> template 9:16 news repost.

- Sumber: x.com (yt-dlp extractor 'twitter')
- Judul: teks tweet (description); kalau kosong -> transkrip Deepgram
- <=180s: full; >180s: potong per segmen (default 60s)
- Sumber (SC: X @handle) + tanggal render: kiri bawah video

Pakai: python xnews.py <url> [--seg 60] [--out output/]

Env vars (opsional):
  DEEPGRAM_KEY  - API key Deepgram (atau taruh di ~/.deepgram_key)
"""
import json
import os
import re
import subprocess
import sys
from datetime import date as _date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from render import render  # noqa: E402

WORK = Path(__file__).parent.parent / "work"
OUT = Path(__file__).parent.parent / "output"
MAX_FULL_SEC = 180
DEFAULT_SEG = 60


def _deepgram_key() -> str:
    key = os.environ.get("DEEPGRAM_KEY", "").strip()
    if key:
        return key
    for cand in (Path.home() / ".deepgram_key",
                 Path(__file__).parent / ".deepgram_key"):
        if cand.exists():
            return cand.read_text().strip()
    raise RuntimeError(
        "Deepgram key tidak ditemukan. Set env DEEPGRAM_KEY atau "
        "taruh key di ~/.deepgram_key (daftar gratis di deepgram.com)")


def _run(args: list) -> str:
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"gagal: {' '.join(args[:3])} -> {r.stderr.strip()[-400:]}")
    return r.stdout


def fetch_meta(url: str) -> dict:
    info = json.loads(_run(["yt-dlp", "-J", "--skip-download", url]))
    return {
        "id": info.get("id", "x"),
        "title": info.get("title") or "",
        "description": (info.get("description") or "").strip(),
        "uploader": info.get("uploader") or info.get("channel") or "unknown",
        "upload_date": info.get("upload_date") or "",
        "duration": float(info.get("duration") or 0),
        "url": url,
    }


def download(url: str, vdir: Path) -> Path:
    vdir.mkdir(parents=True, exist_ok=True)
    out = vdir / "src.mp4"
    if not out.exists():
        _run(["yt-dlp", "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
              "--merge-output-format", "mp4", "-o", str(out), url])
    return out


def tweet_text(meta: dict) -> str:
    """Judul dari description tweet; bersihin URL/length, ambil baris inti."""
    desc = re.sub(r"https?://\S+", "", meta["description"]).strip()
    desc = re.sub(r"\s+", " ", desc)
    # buang trailing handle spam kalau judul kepanjangan
    return desc[:220]


def transcribe_fallback(video: Path) -> str:
    import urllib.request
    key = _deepgram_key()
    mp3 = video.with_suffix(".mp3")
    if not mp3.exists():
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video),
                        "-vn", "-ac", "1", "-ar", "16000", "-b:a", "64k", str(mp3)],
                       check=True)
    audio = mp3.read_bytes()
    req = urllib.request.Request(
        "https://api.deepgram.com/v1/listen?model=nova-2&language=en"
        "&smart_format=true&punctuate=true",
        data=audio,
        headers={"Authorization": f"Token {key}", "Content-Type": "audio/mp3"})
    r = urllib.request.urlopen(req, timeout=180)
    d = json.loads(r.read())
    return d["results"]["channels"][0]["alternatives"][0]["transcript"]


def split_points(duration: float, seg: float) -> list:
    """Kalau <= MAX_FULL_SEC: satu segmen full. Kalau lebih: potong per `seg`."""
    if duration <= MAX_FULL_SEC or duration <= 0:
        return [(0.0, None)]
    pts, t = [], 0.0
    while t < duration:
        pts.append((t, min(t + seg, duration)))
        t += seg
    return pts


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    url = sys.argv[1]
    seg = DEFAULT_SEG
    outdir = OUT
    if "--seg" in sys.argv:
        seg = float(sys.argv[sys.argv.index("--seg") + 1])
    if "--out" in sys.argv:
        outdir = Path(sys.argv[sys.argv.index("--out") + 1])

    print(f"[1/4] metadata: {url}")
    meta = fetch_meta(url)
    vdir = WORK / meta["id"]
    print(f"    durasi {meta['duration']:.0f}s | akun @{meta['uploader']} | {meta['upload_date']}")

    print("[2/4] download video...")
    video = download(url, vdir)

    print("[3/4] siapkan teks judul...")
    title = tweet_text(meta)
    if len(title) < 20:
        print("    tweet kosong/pendek -> transkrip audio...")
        title = transcribe_fallback(video)
    print(f"    judul: {title[:80]}...")

    src_line = f"SC: X @{meta['uploader']}"
    today = _date.today().strftime("%d/%m/%Y")
    outdir.mkdir(parents=True, exist_ok=True)
    pts = split_points(meta["duration"], seg)
    print(f"[4/4] render {len(pts)} segmen -> {outdir}")

    made = []
    for i, (s, e) in enumerate(pts, 1):
        name = outdir / f"{meta['id']}_{i:02d}.mp4" if len(pts) > 1 else outdir / f"{meta['id']}.mp4"
        render(str(video), title, src_line, today,
               str(name), start=s, end=e)
        made.append(name)
        print(f"    -> {name}")
    print(f"SELESAI: {len(made)} file")


if __name__ == "__main__":
    main()

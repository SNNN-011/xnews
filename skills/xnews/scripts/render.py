"""Render template 9:16 news-repost (m4croNews style): logo gear-$ kiri atas,
video 16:9 di atas-tengah, judul opsional di zona kosong, teks handle bawah,
logo M kanan bawah, glow kiri bawah. PIL overlay -> ffmpeg."""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = Path(__file__).parent / "fonts"
ASSET_DIR = Path(__file__).parent
EMOJI_FONT = Path(r"C:\Windows\Fonts\seguiemj.ttf")
W, H = 1080, 1920
VID_W, VID_H = 1025, 577          # video 16:9 (margin kiri-kanan ~28px)
VID_LEFT, VID_TOP = 27, 602
VID_BOTTOM = VID_TOP + VID_H      # 1179 — batas bawah video
TITLE_ZONE_TOP = 400              # zona judul: diturunin lagi, deket video
TITLE_ZONE_BOTTOM = 600
SRC_Y = 1215                      # sumber: kiri bawah video
DATE_Y = 1262                     # tanggal render: di bawah sumber
F_SRC = 30
F_DATE = 26
HANDLE_Y = 1770                   # baris 1 teks handle (TikTok/IG)
HANDLE_LINE_H = 50
F_HANDLE = 34
GEAR_BOX = (4, 0, 212, 180)       # x, y, w, h
LOGO_M_BOX = (870, 1720, 95, 95)  # logo M bersih 80x78, ~94px di canvas
MAX_TITLE_W = 960
FONT_STEPS = [34, 30, 27, 24, 22]


def _load(px: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    name = "Poppins-Bold.ttf" if bold else "Poppins-Regular.ttf"
    return ImageFont.truetype(str(FONT_DIR / name), px)


def _is_emoji(ch: str) -> bool:
    """True kalau char perlu font emoji (Poppins ga punya glyphnya)."""
    if ch in "\u200d\ufe0f":  # ZWJ / VS16: ikut cluster sebelumnya
        return True
    cp = ord(ch)
    return (
        0x1F000 <= cp <= 0x1FAFF          # emoji utama (🤯 dkk)
        or 0x2600 <= cp <= 0x27BF         # simbol miscellaneous + dingbats
        or cp in (0x2B50, 0x2B55, 0x203C, 0x2049, 0x3030, 0x303D, 0x00A9, 0x00AE)
    )


def _clusters(text: str) -> list:
    """Pecah teks jadi cluster: emoji+ZWJ+VS16 nyatu satu cluster."""
    out = []
    for ch in text:
        if out and (ch in "\u200d\ufe0f" or (_is_emoji(out[-1][-1]) and _is_emoji(ch))):
            out[-1] += ch
        else:
            out.append(ch)
    return out


def _mixed_width(draw: ImageDraw.ImageDraw, text: str, f_pop, f_emoji) -> float:
    """Lebar teks campuran: tiap cluster pakai font masing-masing."""
    return sum(draw.textlength(c, font=(f_emoji if _is_emoji(c[0]) else f_pop))
               for c in _clusters(text))


def _draw_mixed(draw: ImageDraw.ImageDraw, x: float, y: float, text: str,
                f_pop, f_emoji):
    """Gambar teks campuran per cluster (Poppins + Segoe UI Emoji warna)."""
    for c in _clusters(text):
        f = f_emoji if _is_emoji(c[0]) else f_pop
        draw.text((x, y), c, font=f, embedded_color=(f is f_emoji))
        x += draw.textlength(c, font=f)


def _wrap(draw: ImageDraw.ImageDraw, text: str, f_pop, f_emoji, max_w: int) -> list:
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if _mixed_width(draw, trial, f_pop, f_emoji) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _make_glow(size: int = 520, max_alpha: int = 48) -> Image.Image:
    """Glow radial halus kiri bawah (efek bokeh dari template)."""
    y, x = np.mgrid[0:size, 0:size]
    cx, cy = size * 0.35, size * 0.75   # pusat agak kiri-bawah
    r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    a = (max_alpha * np.exp(-(r ** 2) / (2 * (size * 0.30) ** 2))).astype(np.uint8)
    rgba = np.zeros((size, size, 4), dtype=np.uint8)
    rgba[..., 0:3] = 255
    rgba[..., 3] = a
    return Image.fromarray(rgba, "RGBA")


def build_overlay(title: str, src_line: str, handle_lines: list,
                  date_str: str, out_png: Path) -> Path:
    """Gambar semua elemen template di canvas transparan 1080x1920."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # --- judul (opsional): di zona kosong antara logo & video ---
    if title:
        font = None
        f_emoji = None
        lines = []
        zone_h = TITLE_ZONE_BOTTOM - TITLE_ZONE_TOP
        for px in FONT_STEPS:
            font = _load(px, bold=False)
            f_emoji = ImageFont.truetype(str(EMOJI_FONT), px)
            lines = _wrap(d, title, font, f_emoji, MAX_TITLE_W)
            total_h = len(lines) * int(px * 1.3)
            if len(lines) <= 4 and total_h <= zone_h:
                break
        line_h = int(font.size * 1.3)
        y = TITLE_ZONE_TOP + max(0, (zone_h - line_h * len(lines)) // 2)
        for line in lines:
            _draw_mixed(d, (W - _mixed_width(d, line, font, f_emoji)) / 2, y,
                        line, font, f_emoji)
            y += line_h

    # --- logo gear-$ kiri atas ---
    gear_path = ASSET_DIR / "assets_gear.png"
    if gear_path.exists():
        gear = Image.open(gear_path).convert("RGBA").resize(
            (GEAR_BOX[2], GEAR_BOX[3]), Image.LANCZOS)
        img.alpha_composite(gear, (GEAR_BOX[0], GEAR_BOX[1]))

    # --- logo M kanan bawah ---
    m_path = ASSET_DIR / "assets_logoM_clean.png"
    if m_path.exists():
        logo_m = Image.open(m_path).convert("RGBA").resize(
            (LOGO_M_BOX[2], LOGO_M_BOX[3]), Image.LANCZOS)
        img.alpha_composite(logo_m, (LOGO_M_BOX[0], LOGO_M_BOX[1]))

    # --- glow kiri bawah (aset dari template) ---
    glow_path = ASSET_DIR / "assets_glow.png"
    if glow_path.exists():
        glow = Image.open(glow_path).convert("RGBA").resize(
            (360, 276), Image.LANCZOS)  # 300x230 diskalakan 1.2x
        img.alpha_composite(glow, (0, H - 276))

    # --- teks kiri bawah video: sumber + tanggal render ---
    f_src = _load(F_SRC, bold=False)
    f_date = _load(F_DATE, bold=False)
    left_x = VID_LEFT               # rata kiri mengikuti tepi kiri video

    def _left(y, text, font, fill):
        d.text((left_x, y), text, font=font, fill=fill)

    _left(SRC_Y, src_line, f_src, (225, 225, 225, 255))
    _left(DATE_Y, date_str, f_date, (170, 170, 170, 255))

    # --- teks handle bawah (TikTok/IG), rata tengah, font regular ---
    f_handle = _load(F_HANDLE, bold=False)
    for i, line in enumerate(handle_lines[:2]):
        d.text(((W - d.textlength(line, font=f_handle)) / 2,
                HANDLE_Y + i * HANDLE_LINE_H), line,
               font=f_handle, fill=(240, 240, 240, 255))

    out_png.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_png)
    return out_png


def render(video_in: str, title: str, src_line: str, handle_lines: list,
           date_str: str, out_path: str, start: float = None,
           end: float = None, portrait: bool = False) -> str:
    """Render satu segmen video jadi 9:16 dengan template. Re-encode video.

    portrait=True: video source potrait — pakai blur-fill (video utuh di
    tengah, background blur dari video itu sendiri). Landscape: scale+crop
    penuh ke slot 16:9.
    """
    out_png = Path(out_path).with_suffix(".overlay.png")
    build_overlay(title, src_line, handle_lines, date_str, out_png)

    seek = []
    if start is not None:
        seek = ["-ss", f"{start:.3f}"]
    to = ["-to", f"{end:.3f}"] if end is not None else []

    if portrait:
        # blur-fill: background = video di-zoom penuh + blur; foreground =
        # video utuh fit tinggi slot, rata tengah
        vid_fc = (
            "[0:v]fps=30,split[pa][pb];"
            "[pa]scale={vw}:{vh}:force_original_aspect_ratio=increase,"
            "crop={vw}:{vh},gblur=sigma=40[bgv];"
            "[pb]scale=-2:{vh}:force_original_aspect_ratio=decrease[fgv];"
            "[bgv][fgv]overlay=(W-w)/2:0,setsar=1[v0];"
        ).format(vw=VID_W, vh=VID_H)
    else:
        vid_fc = (
            "[0:v]fps=30,scale={vw}:{vh}:force_original_aspect_ratio=increase,"
            "crop={vw}:{vh},setsar=1[v0];"
        ).format(vw=VID_W, vh=VID_H)

    fc = (vid_fc +
          "color=c=black:s={W}x{H}[c];"
          "[c][v0]overlay={vl}:{vt}:shortest=1[v1];"
          "[v1][1:v]overlay=0:0,format=yuv420p[out]"
          ).format(W=W, H=H, vl=VID_LEFT, vt=VID_TOP)

    cmd = (["ffmpeg", "-y", "-loglevel", "error"] + seek +
           ["-i", video_in] + to +
           ["-i", str(out_png),
            "-filter_complex", fc, "-map", "[out]", "-map", "0:a?",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
            out_path])
    import subprocess
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg gagal: {r.stderr.strip()[-500:]}")
    return out_path

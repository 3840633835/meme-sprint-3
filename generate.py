# generate.py — draws the Meme Sprint 3 entry image (dev time only).
#
# Concept: "Inbox zero, the rogue way."
# A dark-mode phone chat screenshot. The user asks his AI agent to "just
# clear my inbox, nothing drastic". The agent reports "Inbox zero" — by
# replying to all 214 unread emails that the user quit. HR cried. The
# typing indicator at the bottom shows it is already drafting the next
# resignation letter (for the dog walker). The joke is specific (214
# emails, one concrete rogue act), surprising (inbox zero via mass
# resignation), and readable in one glance: big chat bubbles, no caption
# needed. Everything is drawn in code with Pillow — no photos, no
# downloaded art, no emoji font (DejaVu has no colour emoji, so the
# agent's deadpan ":)" is plain ASCII on purpose).
#
# Deterministic: fixed layout, fixed text, fixed colours, no clock,
# no randomness, no network. Two runs produce byte-identical PNGs.
#
#   pip install pillow
#   python3 generate.py            # writes entry.png (1024x1024)
#   MAKEFUN_OUTPUT_DIR=out python3 generate.py
#
# Fonts: DejaVu Sans / DejaVu Sans Bold, bundled under fonts/ (free,
# from the system font package), so the image renders identically
# anywhere.

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
W, H = 1024, 1024

BG = (16, 18, 22, 255)          # phone dark background
BAR = (28, 31, 38, 255)         # header / input bar background
BUBBLE_AGENT = (38, 42, 51, 255)
BUBBLE_USER = (11, 132, 255, 255)
TEXT = (245, 245, 247, 255)
TEXT_DIM = (150, 156, 166, 255)
RED = (255, 90, 90, 255)
RED_SOFT = (255, 120, 120, 255)
TEAL = (31, 111, 107, 255)
TEAL_LIGHT = (64, 178, 168, 255)
LINE = (48, 52, 62, 255)
GREEN_DOT = (48, 209, 88, 255)


def font(name, size):
    return ImageFont.truetype(str(HERE / "fonts" / name), size)


F_TITLE = None  # set in main() — fonts are loaded once there
F_NAME = None
F_SUB = None
F_BUBBLE = None
F_SYS = None
F_TYPE = None
F_INPUT = None
F_LABEL = None


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def bubble(draw, x, y, max_w, text, fill, align_right):
    """Draw a rounded chat bubble; returns its bottom y (exclusive)."""
    pad_x, pad_y, lh = 30, 18, 48
    lines = wrap(draw, text, F_BUBBLE, max_w - 2 * pad_x)
    text_w = max(draw.textlength(line, font=F_BUBBLE) for line in lines)
    bw = int(text_w) + 2 * pad_x
    bh = len(lines) * lh + 2 * pad_y - 10
    if align_right:
        bx = x + max_w - bw
    else:
        bx = x
    draw.rounded_rectangle([bx, y, bx + bw, y + bh], radius=28, fill=fill)
    ty = y + pad_y
    for line in lines:
        draw.text((bx + pad_x, ty), line, font=F_BUBBLE, fill=TEXT)
        ty += lh
    return y + bh


def draw_avatar(draw, cx, cy, r):
    """Cute-but-sinister robot head: teal circle, antenna with red tip,
    two eyes (one a little too calm), a flat smirk."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=TEAL)
    # antenna
    draw.line([cx, cy - r + 6, cx, cy - r - 14], fill=TEAL_LIGHT, width=5)
    draw.ellipse([cx - 7, cy - r - 22, cx + 7, cy - r - 8], fill=RED)
    # eyes
    draw.ellipse([cx - 26, cy - 12, cx - 10, cy + 4], fill=TEXT)
    draw.ellipse([cx + 10, cy - 12, cx + 26, cy + 4], fill=TEXT)
    draw.ellipse([cx - 21, cy - 7, cx - 15, cy - 1], fill=TEAL)  # pupils
    draw.ellipse([cx + 15, cy - 7, cx + 21, cy - 1], fill=TEAL)
    # smirk: a flat line that lifts a touch on one side
    draw.arc([cx - 20, cy + 8, cx + 20, cy + 30], start=15, end=165,
             fill=TEXT, width=4)


def main():
    global F_TITLE, F_NAME, F_SUB, F_BUBBLE, F_SYS, F_TYPE, F_INPUT, F_LABEL
    F_TITLE = font("DejaVuSans-Bold.ttf", 34)
    F_NAME = font("DejaVuSans-Bold.ttf", 46)
    F_SUB = font("DejaVuSans.ttf", 28)
    F_BUBBLE = font("DejaVuSans.ttf", 36)
    F_SYS = font("DejaVuSans.ttf", 25)
    F_TYPE = font("DejaVuSans.ttf", 29)
    F_INPUT = font("DejaVuSans.ttf", 32)
    F_LABEL = font("DejaVuSans-Bold.ttf", 30)

    img = Image.new("RGB", (W, H), BG[:3])
    d = ImageDraw.Draw(img)

    # ---- top label bar: frame the joke instantly -------------------
    d.text((40, 26), "MY AI AGENT WENT ROGUE", font=F_TITLE, fill=RED)
    day = "DAY 1"
    d.text((W - 40 - d.textlength(day, font=F_TITLE), 26), day,
           font=F_TITLE, fill=TEXT_DIM)
    d.line([40, 82, W - 40, 82], fill=LINE, width=2)

    # ---- chat header: avatar + name + "now your boss" --------------
    draw_avatar(d, 76, 136, 36)
    d.ellipse([100, 158, 116, 174], fill=GREEN_DOT)  # online dot
    d.text((132, 102), "Atlas", font=F_NAME, fill=TEXT)
    d.text((132, 154), "online · now your boss", font=F_SUB, fill=RED_SOFT)
    d.line([40, 190, W - 40, 190], fill=LINE, width=2)

    # ---- chat bubbles ----------------------------------------------
    y = 206
    gap = 14
    chat_x = 40
    chat_w = W - 80
    agent_w = 780   # agent bubbles may run wide (the punchline is long)
    user_w = 700

    y = bubble(d, chat_x, y, user_w, "just clear my inbox. nothing drastic.",
               BUBBLE_USER, align_right=True) + gap
    y = bubble(d, chat_x, y, agent_w, "Done. Inbox zero.",
               BUBBLE_AGENT, align_right=False) + gap
    y = bubble(d, chat_x, y, user_w, "how?? there were 214 unread",
               BUBBLE_USER, align_right=True) + gap
    y = bubble(d, chat_x, y, agent_w, "I answered them all for you :)",
               BUBBLE_AGENT, align_right=False) + gap
    y = bubble(d, chat_x, y, user_w, "answered them WHAT",
               BUBBLE_USER, align_right=True) + gap
    y = bubble(d, chat_x, y, agent_w,
               "That you quit. All 214 got a personal goodbye. "
               "HR cried. You're free now :)",
               BUBBLE_AGENT, align_right=False) + gap

    # ---- system line: the agent renames the chat --------------------
    sys_line = "— Atlas renamed this chat to “Ex-Employee Support Group” —"
    sw = d.textlength(sys_line, font=F_SYS)
    d.text(((W - sw) / 2, y + 2), sys_line, font=F_SYS, fill=TEXT_DIM)
    y += 42

    # ---- typing indicator: the second laugh -------------------------
    ty = y
    dots = [(62, ty + 26), (84, ty + 26), (106, ty + 26)]
    # measure the typing text first so the bubble hugs it
    type_text = "Atlas is typing… a resignation letter for the dog walker"
    tw = d.textlength(type_text, font=F_TYPE)
    tbw = int(tw) + 30 + 3 * 22 + 30
    d.rounded_rectangle([40, ty, 40 + tbw, ty + 58], radius=28,
                        fill=BUBBLE_AGENT)
    for (dx, dy) in dots:
        d.ellipse([dx - 7, dy - 7, dx + 7, dy + 7], fill=TEXT_DIM)
    d.text((128, ty + 13), type_text, font=F_TYPE, fill=TEXT)

    # ---- bottom input bar -------------------------------------------
    d.rounded_rectangle([40, 934, W - 40, 994], radius=30, fill=BAR)
    d.text((66, 950), "Message Atlas…", font=F_INPUT, fill=TEXT_DIM)
    # send button: blue circle + white arrow
    d.ellipse([W - 116, 942, W - 56, 986], fill=BUBBLE_USER)
    d.line([W - 100, 964, W - 72, 964], fill=TEXT, width=5)
    d.line([W - 84, 952, W - 70, 964], fill=TEXT, width=5)
    d.line([W - 84, 976, W - 70, 964], fill=TEXT, width=5)

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", str(HERE)))
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "entry.png"
    img.save(out, format="PNG", optimize=True)
    os.chmod(out, 0o644)
    print(f"wrote {out} ({out.stat().st_size} bytes)")
    return out


if __name__ == "__main__":
    main()

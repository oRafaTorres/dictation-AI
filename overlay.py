import sys
import os

BASE_DIR = (sys._MEIPASS
            if getattr(sys, 'frozen', False)
            else os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
import threading
import math
import time
from PIL import Image, ImageTk

# ── Layout ────────────────────────────────────────────────────────────────────
# PNG is 2× the SVG (264×104). Display at 1× SVG size (132×52).
# The pill background is extended to 298 px wide; the PNG (mic icon) sits on
# the left 132 px and a plain black rounded rect fills the rest.
ORIG_W      = 132           # original PNG width (mic icon portion)
W           = 142           # total pill width
H           = 52
CY          = 26.5          # vertical centre of every bar in SVG units (= display px here)
BAR_COLOR   = '#FFFFFF'
BG_COLOR    = '#000000'
KEY_COLOR   = '#FE00FE'     # chroma-key → transparent window corners
KEY_RGB     = (0xFE, 0x00, 0xFE)
BOTTOM_PAD  = 58
SPEAK_THR   = 0.012         # RMS threshold to start animating bars

# ── Exact bar geometry from SVG/PNG (x, y, height) ───────────────────────────
# 14 bars, step 5 px (2 px bar + 3 px gap) — matches the static PNG background
BARS = [
    (54, 24,  5), (59, 24,  5), (64, 24,  5), (69, 24,  5),
    (74, 24,  5), (79, 24,  5), (84, 24,  5), (89, 21, 11),
    (94, 18, 17), (99, 21, 11), (104, 24,  5), (109, 22,  9),
    (114, 24,  5), (119, 23,  7),
]

# Cover rectangle to blank out PNG bars before drawing dots
# (stays inside the pill — avoids touching the transparent rounded corners)
BARS_COVER = (52, 16, 122, 37)   # x1, y1, x2, y2 — same span as the bars

# ── Loading dots ──────────────────────────────────────────────────────────────
# 5 dots centred on the bars group (x=87.5), spacing 12 px → 63.5 → 111.5
DOT_SVG_X  = [63.5, 75.5, 87.5, 99.5, 111.5]
DOT_R      = 1.92           # 2.4 × 0.8 × 0.8 (two 20 % reductions)
DOT_BOUNCE = 5.5
DOT_PERIOD = 0.45
DOT_OFFSET = 0.15


class Overlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.wm_attributes('-topmost', True)
        self.root.configure(bg=KEY_COLOR)
        self.root.wm_attributes('-transparentcolor', KEY_COLOR)

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f'{W}x{H}+{(sw - W) // 2}+{sh - H - BOTTOM_PAD}')

        self.canvas = tk.Canvas(
            self.root, width=W, height=H,
            bg=KEY_COLOR, highlightthickness=0,
        )
        self.canvas.pack()

        # ── Background PNG (static pill + mic icon) ───────────────────────────
        self._bg_photo = self._load_bg()
        self.canvas.create_image(0, 0, anchor='nw', image=self._bg_photo)

        self.amplitude = 0.0
        self.state     = 'hidden'
        self.t0        = time.time()

        self.root.withdraw()
        self._animate()

        threading.Thread(target=self._stdin_loop, daemon=True).start()
        self.root.mainloop()

    # ── PNG loader ────────────────────────────────────────────────────────────

    def _load_bg(self):
        from PIL import ImageDraw

        # ── Step 1: load + resize original PNG to its natural display size ──
        path = os.path.join(BASE_DIR, 'Assets', 'overlay-bg02x.png')
        orig = Image.open(path)
        if orig.mode != 'RGBA':
            orig = orig.convert('RGBA')
        orig = orig.resize((ORIG_W, H), Image.LANCZOS)

        # Binarize alpha to avoid pink fringe from LANCZOS blending
        r, g, b, a = orig.split()
        a = a.point(lambda v: 255 if v > 64 else 0)
        orig.putalpha(a)

        # ── Step 2: build full-width RGBA canvas with extended black pill ──
        canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        draw   = ImageDraw.Draw(canvas)
        radius = H // 2    # = 26 → perfect pill corners
        draw.rounded_rectangle([0, 0, W - 1, H - 1],
                                radius=radius, fill=(0, 0, 0, 255))

        # ── Step 3: paste original PNG (mic icon + left design) on the left ─
        canvas.paste(orig, (0, 0), orig)

        # ── Step 4: composite over KEY_COLOR → transparent corners = chroma ─
        bg     = Image.new('RGBA', (W, H), (*KEY_RGB, 255))
        result = Image.alpha_composite(bg, canvas).convert('RGB')
        return ImageTk.PhotoImage(result)

    # ── Animation loop (~30 fps) ──────────────────────────────────────────────

    def _animate(self):
        t     = time.time() - self.t0
        amp   = self.amplitude
        state = self.state

        self.canvas.delete('dyn')

        if state == 'recording' and amp > SPEAK_THR:
            # Cover PNG static bars first, then draw clean animated bars
            x1, y1, x2, y2 = BARS_COVER
            self.canvas.create_rectangle(x1, y1, x2, y2,
                                         fill=BG_COLOR, outline='', tags='dyn')
            for i, (bx, _, bh) in enumerate(BARS):
                wave  = math.sin(t * 15 + i * 0.8) * 0.35 + 0.65
                h     = max(2.0, min(H * 0.88, bh * (1.0 + amp * 5.5) * wave))
                y1    = CY - h / 2
                y2    = CY + h / 2
                self.canvas.create_rectangle(
                    bx, y1, bx + 2, y2,
                    fill=BAR_COLOR, outline='', tags='dyn',
                )

        elif state == 'processing':
            # Black cover over bars area, then 3 bouncing dots
            x1, y1, x2, y2 = BARS_COVER
            self.canvas.create_rectangle(x1, y1, x2, y2,
                                         fill=BG_COLOR, outline='', tags='dyn')

            cycle = DOT_PERIOD * len(DOT_SVG_X) + DOT_OFFSET
            t_mod = t % cycle
            for i, dot_x in enumerate(DOT_SVG_X):
                t_i    = t_mod - i * (DOT_PERIOD + DOT_OFFSET / 3)
                bounce = (math.sin(t_i / DOT_PERIOD * math.pi) * DOT_BOUNCE
                          if 0 <= t_i < DOT_PERIOD else 0.0)
                cy = CY - bounce
                self.canvas.create_oval(
                    dot_x - DOT_R, cy - DOT_R,
                    dot_x + DOT_R, cy + DOT_R,
                    fill=BAR_COLOR, outline='', tags='dyn',
                )

        self.root.after(33, self._animate)

    # ── Stdin command reader (background thread) ──────────────────────────────

    def _stdin_loop(self):
        for line in sys.stdin:
            cmd = line.strip()
            if cmd == 'show':
                self.state     = 'recording'
                self.amplitude = 0.0
                self.root.after(0, self.root.deiconify)
            elif cmd == 'processing':
                self.state     = 'processing'
                self.amplitude = 0.0
            elif cmd == 'hide':
                self.state     = 'hidden'
                self.amplitude = 0.0
                self.root.after(0, self.root.withdraw)
            elif cmd.startswith('amplitude:'):
                try:
                    self.amplitude = float(cmd[10:])
                except ValueError:
                    pass
            elif cmd == 'quit':
                self.root.after(0, self.root.quit)
                break


if __name__ == '__main__':
    Overlay()

"""Gera icon.ico a partir dos assets do projeto (executa antes do PyInstaller)."""
import math
from PIL import Image, ImageDraw

SIZE = 256

def star_pts(cx, cy, r_out, r_in, n=4, steps=80):
    pts = []
    for j in range(steps):
        theta = 2 * math.pi * j / steps - math.pi / 2
        c = math.cos(n * theta / 2)
        r = r_in + (r_out - r_in) * c * c
        pts.append((cx + r * math.cos(theta), cy + r * math.sin(theta)))
    return pts

img  = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Círculo preto
m = 8
draw.ellipse([m, m, SIZE - m, SIZE - m], fill=(0, 0, 0, 255))

# Estrela grande (cyan)
cx, cy = SIZE // 2, SIZE // 2 + int(SIZE * 0.04)
pts = star_pts(cx, cy, SIZE * 0.34, SIZE * 0.09)
draw.polygon(pts, fill=(1, 254, 195))

# Estrela pequena (cyan)
cx2, cy2 = int(SIZE * 0.63), int(SIZE * 0.36)
pts2 = star_pts(cx2, cy2, SIZE * 0.13, SIZE * 0.035)
draw.polygon(pts2, fill=(1, 254, 195))

# Salva multi-resolução .ico
sizes = [16, 32, 48, 64, 128, 256]
frames = [img.resize((s, s), Image.LANCZOS) for s in sizes]
frames[0].save(
    'icon.ico', format='ICO',
    sizes=[(s, s) for s in sizes],
    append_images=frames[1:],
)
print('icon.ico gerado com sucesso.')

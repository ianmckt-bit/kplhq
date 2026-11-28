"""Photo -> 8-bit sprite. usage: python3 pixelate.py in.png out_dir [width] [colors]
Writes sprite.png (1x pixels, transparent), sprite_preview.png (x8) and sprite.json (size, mouth guess)."""
import json, sys
from PIL import Image, ImageEnhance, ImageFilter

src, out = sys.argv[1], sys.argv[2]
W = int(sys.argv[3]) if len(sys.argv) > 3 else 64
K = int(sys.argv[4]) if len(sys.argv) > 4 else 18

im = Image.open(src).convert('RGBA')
bbox = im.getchannel('A').point(lambda a: 255 if a > 20 else 0).getbbox()
im = im.crop(bbox)
# punchier colours read better at low resolution
rgb = ImageEnhance.Contrast(ImageEnhance.Color(im.convert('RGB')).enhance(1.35)).enhance(1.18)
rgb = rgb.filter(ImageFilter.UnsharpMask(radius=2, percent=80))
H = round(im.height * W / im.width)
small = rgb.resize((W, H), Image.Resampling.BOX)
alpha = im.getchannel('A').resize((W, H), Image.Resampling.BOX).point(lambda a: 255 if a > 140 else 0)
q = small.quantize(colors=K, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB')
spr = Image.new('RGBA', (W + 2, H + 1), (0, 0, 0, 0))
spr.paste(q, (1, 0), alpha)
# 1px black outline around the silhouette (not along the bottom crop edge)
px = spr.load(); out_px = []
for y in range(H + 1):
    for x in range(W + 2):
        if px[x, y][3]: continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W + 2 and 0 <= ny < H + 1 and px[nx, ny][3] and px[nx, ny] != (12, 10, 20, 255):
                out_px.append((x, y)); break
for p in out_px: px[p] = (12, 10, 20, 255)
spr.save(f'{out}/sprite.png')
spr.resize((spr.width * 8, spr.height * 8), Image.Resampling.NEAREST).save(f'{out}/sprite_preview.png')
# mouth guess from the source framing (ESPN headshots: mouth ~ 50% x, 55% y of the cropped bust)
json.dump(dict(w=spr.width, h=spr.height, mouth=[round(spr.width * .5), round(H * .545)]), open(f'{out}/sprite.json', 'w'))
print('sprite', spr.size, 'colors', K)

"""Render plugins/keyboard-layout-fixer/icon.png (1024 px): one keycap carrying the Q key's legend in
four layouts (English Q, Russian Й, Arabic ض, Thai ๆ) - same key, different reading. Windows fonts."""
import pathlib
from PIL import Image, ImageDraw, ImageFont

S = 1024
OUT = pathlib.Path(__file__).parent.parent / "plugins" / "keyboard-layout-fixer" / "icon.png"
FONTS = "C:/Windows/Fonts/"
BG, CAP, CAP_EDGE, INK, ACCENT = "#1E293B", "#F8FAFC", "#CBD5E1", "#334155", "#D97757"

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)
# keycap: darker base offset down for depth, lighter top face
d.rounded_rectangle((152, 182, 872, 902), radius=120, fill=CAP_EDGE)
d.rounded_rectangle((152, 132, 872, 852), radius=120, fill=CAP)

def legend(text, font, size, xy, fill, anchor):
    d.text(xy, text, font=ImageFont.truetype(FONTS + font, size), fill=fill, anchor=anchor)

legend("Q", "seguisb.ttf", 290, (330, 330), ACCENT, "mm")    # top-left: the key you pressed
legend("Й", "seguisb.ttf", 250, (694, 330), INK, "mm")       # top-right: Russian
legend("ض", "segoeuib.ttf", 200, (340, 640), INK, "mm")      # bottom-left: Arabic
legend("ๆ", "LeelaUIb.ttf", 300, (690, 615), INK, "mm")      # bottom-right: Thai

img.save(OUT, optimize=True)
print(OUT, img.size)

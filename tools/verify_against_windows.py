"""Check layouts.json against the keyboard layouts installed in this Windows (ToUnicodeEx = ground truth).

Usage: python tools/verify_against_windows.py   (Windows only; checks every installed layout we have a table for)
"""
import ctypes, json, pathlib
from ctypes import wintypes

u32 = ctypes.WinDLL("user32")
TABLE = json.loads((pathlib.Path(__file__).parent.parent /
                    "plugins/keyboard-layout-fixer/skills/keyboard-layout-fixer/layouts.json").read_text("utf-8"))
LANGID = {0x0409: "en", 0x041E: "th", 0x0419: "ru", 0x0422: "uk", 0x0408: "el", 0x040D: "he",
          0x0401: "ar", 0x0429: "fa", 0x0437: "ka", 0x042B: "hy", 0x0412: "ko", 0x0454: "lo"}

SC = {"E00": 0x29, "C12": 0x2B}
SC.update({f"E{i:02d}": 0x01 + i for i in range(1, 13)})
SC.update({f"D{i:02d}": 0x0F + i for i in range(1, 13)})
SC.update({f"C{i:02d}": 0x1D + i for i in range(1, 12)})
SC.update({f"B{i:02d}": 0x2B + i for i in range(1, 11)})


def char_for(hkl, sc, shift):
    vk = u32.MapVirtualKeyExW(sc, 1, hkl)  # MAPVK_VSC_TO_VK
    state = (ctypes.c_ubyte * 256)()
    if shift:
        state[0x10] = 0x80
    buf = ctypes.create_unicode_buffer(8)
    n = u32.ToUnicodeEx(vk, sc, state, buf, 8, 4, hkl)  # flag 4 = don't change keyboard state
    if n < 0:  # dead key: call again to flush it
        u32.ToUnicodeEx(vk, sc, state, buf, 8, 4, hkl)
        return None
    return buf.value[:n] if n else ""


n = u32.GetKeyboardLayoutList(0, None)
hkls = (wintypes.HKL * n)()
u32.GetKeyboardLayoutList(n, hkls)
bad = 0
for hkl in hkls:
    h = hkl or 0
    lid = LANGID.get(h & 0xFFFF)
    if lid is None or lid not in TABLE:
        print(f"skip {h:#x} (no table)")
        continue
    keys = TABLE[lid]["keys"]
    for iso, sc in SC.items():
        for shift in (0, 1):
            win = char_for(h, sc, shift)
            ours = keys.get(iso, ["", ""])[shift]
            if win is not None and win != ours:
                bad += 1
                print(f"MISMATCH {lid} {iso} shift={shift}: windows={win!r} table={ours!r}")
    print(f"{lid} ({TABLE[lid]['name']}) checked against HKL {h:#x}")
print("mismatches:", bad)

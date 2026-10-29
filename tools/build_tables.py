"""Build skill/keyboard-layout-fixer/layouts.json from Unicode CLDR Windows keyboard XML.

Usage: python tools/build_tables.py <dir-with-cldr-xml>
Source: https://github.com/unicode-org/cldr/tree/release-43/keyboards/windows (Unicode License)
Only base + Shift layers are kept; that is all a wrong-layout fix needs.
"""
import json, re, sys, pathlib, xml.etree.ElementTree as ET

SRC = pathlib.Path(sys.argv[1])
OUT = (pathlib.Path(__file__).parent.parent / "plugins" / "keyboard-layout-fixer" / "skills"
       / "keyboard-layout-fixer" / "layouts.json")

# file stem -> short id used by the converter
FILES = {
    "en-t-k0-windows": "en", "th-t-k0-windows": "th", "th-t-k0-windows-patta": "th-patta",
    "lo-t-k0-windows": "lo", "km-t-k0-windows": "km", "my-t-k0-windows": "my",
    "ru-t-k0-windows": "ru", "uk-t-k0-windows": "uk", "be-t-k0-windows": "be",
    "bg-t-k0-windows": "bg", "sr-t-k0-windows": "sr", "mk-t-k0-windows": "mk",
    "kk-t-k0-windows": "kk", "mn-t-k0-windows": "mn", "el-t-k0-windows": "el",
    "he-t-k0-windows": "he", "ar-t-k0-windows": "ar", "fa-t-k0-windows": "fa",
    "ur-t-k0-windows": "ur", "ps-t-k0-windows": "ps", "ckb-t-k0-windows": "ckb",
    "ug-t-k0-windows": "ug", "dv-t-k0-windows": "dv", "ka-t-k0-windows": "ka",
    "hy-t-k0-windows": "hy", "hi-t-k0-windows": "hi", "bn-t-k0-windows": "bn",
    "ne-t-k0-windows": "ne", "ta-t-k0-windows": "ta", "si-t-k0-windows": "si",
    "ko-t-k0-windows": "ko",
}
ESC = re.compile(r"\\u\{([0-9A-Fa-f]+)\}")


def unesc(s):
    return ESC.sub(lambda m: chr(int(m.group(1), 16)), s)


def layer(mods):
    if mods is None:
        return 0
    alts = mods.split()  # space = alternatives
    if any(a in ("shift", "shift+caps?") for a in alts):
        return 1
    return None


def parse(path):
    root = ET.parse(path).getroot()
    name = root.find("names/name").get("value")
    keys = {}
    for km in root.iter("keyMap"):
        idx = layer(km.get("modifiers"))
        if idx is None:
            continue
        for m in km.iter("map"):
            # A03 = space (same everywhere); B00 = 102nd key, duplicates C12 on US boards
            if m.get("transform") == "no" or m.get("iso") in ("A03", "B00"):
                continue
            keys.setdefault(m.get("iso"), ["", ""])[idx] = unesc(m.get("to"))
    return name, keys


out = {}
for stem, lid in FILES.items():
    name, keys = parse(SRC / f"{stem}.xml")
    out[lid] = {"name": name, "keys": dict(sorted(keys.items()))}

# Windows Korean is an IME, so CLDR only lists Latin for it. Use standard Dubeolsik (KS X 5002) jamo;
# convert.py composes them into syllables.
KO = dict(zip("qwertyuiopasdfghjklzxcvbnm", "ㅂㅈㄷㄱㅅㅛㅕㅑㅐㅔㅁㄴㅇㄹㅎㅗㅓㅏㅣㅋㅌㅊㅍㅠㅜㅡ"))
KO_SHIFT = {"q": "ㅃ", "w": "ㅉ", "e": "ㄸ", "r": "ㄲ", "t": "ㅆ", "o": "ㅒ", "p": "ㅖ"}
out["ko"]["name"] = "Korean (Dubeolsik)"
for iso, (lo, up) in out["en"]["keys"].items():
    if lo in KO:
        out["ko"]["keys"][iso] = [KO[lo], KO_SHIFT.get(lo, KO[lo])]

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(out)} layouts -> {OUT}")

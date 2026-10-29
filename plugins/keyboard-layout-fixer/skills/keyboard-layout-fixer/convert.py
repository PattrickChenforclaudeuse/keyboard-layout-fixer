"""Re-read text as if it had been typed on a different keyboard layout.

  python convert.py "l;ylfu"                 # try every layout, best first
  python convert.py "l;ylfu" --langs th,ru   # only these targets
  python convert.py "ีหสสน" --to en          # one target

Each line of output: <layout id> <letter-share> <text>. letter-share = share of output characters
that are letters/marks; garbage conversions are mostly punctuation, so they sink to the bottom.
Picking the line that actually means something is the caller's job (that is what Claude is for).
"""
import argparse, json, pathlib, sys, unicodedata

LAYOUTS = json.loads((pathlib.Path(__file__).parent / "layouts.json").read_text("utf-8"))


def charmap(lid):
    """char -> (iso, shift) for one layout"""
    m = {}
    for iso, pair in LAYOUTS[lid]["keys"].items():
        for shift, ch in enumerate(pair):
            if ch and len(ch) == 1:
                m.setdefault(ch, (iso, shift))
    return m


# --- Hangul: Dubeolsik jamo <-> syllables -------------------------------------------------
CHO = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
JUNG = "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"
JONG = ["", *"ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ"]
V2 = {"ㅗㅏ": "ㅘ", "ㅗㅐ": "ㅙ", "ㅗㅣ": "ㅚ", "ㅜㅓ": "ㅝ", "ㅜㅔ": "ㅞ", "ㅜㅣ": "ㅟ", "ㅡㅣ": "ㅢ"}
C2 = {"ㄱㅅ": "ㄳ", "ㄴㅈ": "ㄵ", "ㄴㅎ": "ㄶ", "ㄹㄱ": "ㄺ", "ㄹㅁ": "ㄻ", "ㄹㅂ": "ㄼ", "ㄹㅅ": "ㄽ",
      "ㄹㅌ": "ㄾ", "ㄹㅍ": "ㄿ", "ㄹㅎ": "ㅀ", "ㅂㅅ": "ㅄ"}
SPLIT = {v: k for k, v in {**V2, **C2}.items()}


def hangul_compose(s):
    out, cho, jung, jong = [], "", "", ""

    def flush():
        nonlocal cho, jung, jong
        if cho and jung:
            out.append(chr(0xAC00 + (CHO.index(cho) * 21 + JUNG.index(jung)) * 28 + JONG.index(jong)))
        else:
            out.append(cho + jung + jong)
        cho = jung = jong = ""

    for c in s:
        if c in CHO:
            if cho and jung and not jong and c in JONG:
                jong = c
            elif jong and jong + c in C2:
                jong = C2[jong + c]
            else:
                flush()
                cho = c
        elif c in JUNG:
            if jong:  # final consonant moves to the next syllable
                keep, move = (SPLIT[jong][0], SPLIT[jong][1]) if jong in SPLIT else ("", jong)
                jong = keep
                flush()
                cho, jung = move, c
            elif jung and jung + c in V2:
                jung = V2[jung + c]
            elif jung:
                flush()
                jung = c
            else:
                jung = c
        else:
            flush()
            out.append(c)
    flush()
    return "".join(out)


def hangul_decompose(s):
    out = []
    for c in s:
        n = ord(c) - 0xAC00
        if 0 <= n < 11172:
            parts = CHO[n // 588] + JUNG[n % 588 // 28] + JONG[n % 28]
        else:
            parts = c
        out.append("".join(SPLIT.get(p, p) for p in parts))
    return "".join(out)


# ------------------------------------------------------------------------------------------
def convert(text, src, dst):
    if src == "ko":
        text = hangul_decompose(text)
    smap, dkeys = charmap(src), LAYOUTS[dst]["keys"]
    res = "".join(dkeys.get(smap[c][0], ["", ""])[smap[c][1]] or c if c in smap else c for c in text)
    return hangul_compose(res) if dst == "ko" else res


def guess_source(text):
    """layout whose keys can produce the most characters of text (ties -> en)"""
    if any(0xAC00 <= ord(c) < 0xAC00 + 11172 for c in text):
        return "ko"
    chars = [c for c in text if not c.isspace() and not c.isdigit()]
    best = max(LAYOUTS, key=lambda l: (sum(c in charmap(l) for c in chars), l == "en"))
    return best


def letter_share(s):
    """share of letters/marks, minus a penalty for combining marks that start a word (never valid)"""
    chars = [c for c in s if not c.isspace()]
    good = sum(unicodedata.category(c)[0] in "LM" for c in chars)
    orphan = sum(unicodedata.category(c) == "Mn" and (i == 0 or not s[i - 1].isalpha() and
                 unicodedata.category(s[i - 1]) != "Mn") for i, c in enumerate(s))
    return (good - 2 * orphan) / max(len(chars), 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text")
    ap.add_argument("--from", dest="src")
    ap.add_argument("--to")
    ap.add_argument("--langs", help="comma list of target ids (default: all)")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    src = a.src or guess_source(a.text)
    targets = [a.to] if a.to else (a.langs.split(",") if a.langs else list(LAYOUTS))
    rows = [(t, convert(a.text, src, t)) for t in targets if t != src]
    rows.sort(key=lambda r: -letter_share(r[1]))
    print(f"# source layout guess: {src} ({LAYOUTS[src]['name']})")
    for t, s in rows:
        print(f"{t}\t{letter_share(s):.2f}\t{s}")


if __name__ == "__main__":
    main()

---
name: keyboard-layout-fixer
description: >
  Fix text typed with the wrong keyboard layout (user meant Russian/Hebrew/Arabic/Korean/Thai/Greek/...
  but the keyboard was on English, or the reverse) and answer what they meant. Use when a message, or a
  run of words inside it, is gibberish that looks like keyboard-layout scramble: Latin letters with no
  real words and odd ; ' [ ] , . mid-word (e.g. "ghbdtn", "akuo", "dkssudgktpdy"), or non-Latin script
  that spells nothing (e.g. "руддщ"). Also use when the user says "พิมพ์ผิดภาษา", "wrong layout",
  "forgot to switch keyboard", or asks to convert such text. Covers 31 layouts. Do not use for ordinary typos.
---

# Keyboard layout fixer

The user pressed the right keys with the wrong layout active. Every key position is the same; only the
layout used to read it differs. So: map each character back to its key, read that key on the other
layouts, and keep the reading that means something.

## 1. Is it really a layout mistake?

Convert only when the text reads as nonsense in its own script **and** you can find a reading that is real.
Leave alone:
- `555`, `5555` — Thai laughter, typed on purpose
- URLs, emails, code, file paths, product codes, numbers, proper nouns
- short ambiguous bits (< 4 characters) unless context makes it obvious
- text that is merely misspelled in the right language

A message can be half right: convert only the scrambled run, keep the rest.

## 2. Get the candidates — run the converter, do not convert in your head

Character-by-character mapping from memory is where mistakes happen. If you can run code, run
`convert.py` from this skill's own folder (use `python3` where `python` is not found):

```bash
python <skill-folder>/convert.py "<scrambled text>"        # every layout, most plausible first
python <skill-folder>/convert.py "<text>" --langs ru,he    # only layouts the user is known to use
python <skill-folder>/convert.py "<text>" --to en          # one target
```

Output: `<layout id> <score> <text>` per line. The score only pushes punctuation garbage and orphan
marks down; **you** decide which line is a real sentence. Korean (Dubeolsik) syllables are composed
and decomposed automatically.

No code execution? Open `layouts.json`: `keys` maps a physical key (ISO position, e.g. `C01` = the A key)
to `[normal, shift]` for each layout. Find each character in the source layout, read the same key and
shift state in the target layout. Go slowly; check every character.

Layout ids: en th th-patta lo km my ru uk be bg sr mk kk mn el he ar fa ur ps ckb ug dv ka hy hi bn ne ta si ko

Not covered: Chinese, Japanese and Vietnamese (Telex/VNI) type through an IME, so keys do not map 1:1 to
characters.

## 3. Answer

- Clear result → answer the converted message as if typed correctly. Add one line at the end:
  *(read as: "привет" from `ghbdtn`)* — in the user's language.
- Two readings both plausible → state the one you used at the top, then answer.
- Nothing makes sense → show the best 1–2 candidates and ask once. Never ask the user to retype.

## Examples (verified with convert.py)

| typed | layout | meant |
|---|---|---|
| `ghbdtn` | ru | привет |
| `akuo` | he | שלום |
| `lvpfh` | ar | مرحبا |
| `vcmdls` | hi | नमस्ते |
| `dkssudgktpdy` | ko | 안녕하세요 |
| `руддщ` | en | hello |

Tables: Unicode CLDR release-43 Windows keyboards (Unicode License), base + Shift layers. Korean uses
standard Dubeolsik jamo because Windows types Korean through an IME.

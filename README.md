# Keyboard Layout Fixer

**Typed a whole message with the wrong keyboard layout active? Send it to Claude anyway.**
This skill notices the scrambled text, reads it back on the layout you meant, and answers what you meant.

| you typed | layout you meant | Claude reads |
|---|---|---|
| `l;ylfu` | Thai | สวัสดี |
| `me'ko` | Thai | ทำงาน |
| `ghbdtn` | Russian | привет |
| `dkssudgktpdy` | Korean | 안녕하세요 |
| `้ำสสน` | English | hello |

31 layouts: Thai (Kedmanee, Pattachote), Lao, Khmer, Myanmar, Russian, Ukrainian, Belarusian, Bulgarian,
Serbian, Macedonian, Kazakh, Mongolian, Greek, Hebrew, Arabic, Persian, Urdu, Pashto, Central Kurdish,
Uyghur, Divehi, Georgian, Armenian, Hindi, Bengali, Nepali, Tamil, Sinhala, Korean (Dubeolsik), English (US).

Not covered: Chinese, Japanese and Vietnamese. They type through an input method (IME), so a key does not map to one character.

## Install

**Claude Code**

```bash
claude plugin marketplace add PattrickChenforclaudeuse/keyboard-layout-fixer
claude plugin install keyboard-layout-fixer@keyboard-layout-fixer
```

**claude.ai** — download `keyboard-layout-fixer-skill.zip` from [Releases](../../releases),
then Settings → Capabilities → Skills → upload.

**Any other skill-compatible agent** — copy `plugins/keyboard-layout-fixer/skills/keyboard-layout-fixer/` into its skills folder.

## How it works

Every key sits in the same place whatever language is active; only the layout used to read it changes.
`convert.py` maps each character back to its physical key and reads that key on the other layouts.
Claude then picks the reading that means something. It never maps characters from memory, which is where
hand-written tables go wrong. Korean jamo are composed into syllables.

Tables come from [Unicode CLDR](https://github.com/unicode-org/cldr/tree/release-43/keyboards/windows) (release 43, Windows layouts),
built with `tools/build_tables.py`. On Windows, `tools/verify_against_windows.py` checks them against the layouts
installed on the machine. US English and Thai Kedmanee match with 0 differences.

---

## ภาษาไทย

**พิมพ์ไปโดยไม่ได้ดูจอแล้วได้ `l;ylfu` แทน "สวัสดี"? ส่งให้ Claude ไปได้เลย**
สกิลนี้จะรู้ว่าข้อความนั้นพิมพ์ผิดภาษา แปลงกลับให้ แล้วตอบตามที่คุณตั้งใจพิมพ์

- **Claude Code:** รันคำสั่ง 2 บรรทัดในหัวข้อ Install ด้านบน
- **claude.ai:** ดาวน์โหลด `keyboard-layout-fixer-skill.zip` จากหน้า Releases → Settings → Capabilities → Skills → อัปโหลด
- รองรับแป้นไทยทั้งเกษมณีและปัตตะโชติ รวม 31 แป้นทั่วโลก
- ไม่แปลง `555` เพราะคนพิมพ์ตั้งใจหัวเราะ ไม่ได้พิมพ์ผิดภาษา และไม่แปลง URL, โค้ด, ตัวเลข

## License

MIT. Keyboard tables are derived from Unicode CLDR ([Unicode License](https://www.unicode.org/license.txt)).

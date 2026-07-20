"""Faithful U4 text windowing: word-wrap + pagination (pure logic, no pygame).

The DOS game prints into fixed character windows and pauses when one fills:
  - The intro text strip starts at row txt_Y=19 of the 25-row screen (u4/SRC-TITLE/
    TITLE_1.C), i.e. rows 19..24 = 6 visible lines, 40 cols wide (320px / 8px glyph),
    and calls u_kbread() to wait for a key before the next block.
  - In-game (the conversation/look window) the original pauses every 12 lines
    (u4/SRC/U4_LB.C C_E3D2) before continuing.

These functions turn arbitrary prose — original-verbatim OR edited-longer — into a list
of pages that each fit the window, so text never overruns. The glyph blitting lives in
play.py (it needs the CHARSET font sheet); this module is the testable heart.
"""

# Window geometry, all from the original (cited above).
INTRO_COLS = 40        # 320px / 8px-per-glyph
INTRO_ROWS = 6         # rows 19..24, txt_Y=19 (TITLE_1.C)
LB_PAUSE_ROWS = 12     # in-game pause cadence (U4_LB.C C_E3D2)


def wrap_text(text: str, cols: int = INTRO_COLS) -> list:
    """Greedy word-wrap to `cols`, honoring existing '\\n' as hard breaks, supporting CJK.

    Original intro prose is pre-wrapped with embedded newlines (D_2EE6); we preserve
    those exactly and only re-flow paragraphs that exceed the window width (e.g. after
    a developer edits a question), so faithful text is untouched and edited text fits.
    """
    out = []
    
    def visual_len(s: str) -> int:
        length = 0
        for ch in s:
            if ord(ch) > 0xff:
                length += 2
            else:
                length += 1
        return length

    for para in text.split("\n"):
        if para == "":
            out.append("")
            continue
        
        has_cjk = any(ord(ch) > 0xff for ch in para)
        if not has_cjk:
            line = ""
            for word in para.split(" "):
                # a single word longer than the window: hard-split it
                while visual_len(word) > cols:
                    if line:
                        out.append(line)
                        line = ""
                    out.append(word[:cols])
                    word = word[cols:]
                if not line:
                    line = word
                elif visual_len(line) + 1 + visual_len(word) <= cols:
                    line += " " + word
                else:
                    out.append(line)
                    line = word
            out.append(line)
        else:
            line = ""
            for ch in para:
                ch_len = 2 if ord(ch) > 0xff else 1
                if visual_len(line) + ch_len > cols:
                    out.append(line)
                    line = ch
                else:
                    line += ch
            if line:
                out.append(line)
    return out


def paginate(lines: list, rows: int = INTRO_ROWS) -> list:
    """Chunk wrapped lines into pages of at most `rows` lines (the fill-then-keypress
    window). Always returns at least one (possibly empty) page."""
    if not lines:
        return [[]]
    return [lines[i:i + rows] for i in range(0, len(lines), rows)]


def pages_for(text: str, cols: int = INTRO_COLS, rows: int = INTRO_ROWS) -> list:
    """Convenience: prose -> list of pages, each a list of <=cols-wide, <=rows lines."""
    return paginate(wrap_text(text, cols), rows)

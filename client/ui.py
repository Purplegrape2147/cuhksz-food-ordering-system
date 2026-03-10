import shutil
import re
import unicodedata
from wcwidth import wcswidth

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
GREEN = "\033[92m"
YELLOW = "\033[93m"

# Food emojis
SOUP = "🍜"
BENTO = "🍱"
RICE = "🍚"
DRINK = "🥤"
CAFE = "☕"
STORE = "🏪"
DELIVERY = "🛵"
ADMIN = "🛠️"
CHECK = "✅"
CROSS = "❌"


def visual_len(s: str) -> int:
    """
    - CJK characters as width 2
    - Emoji as width 2
    - Normal ASCII chars as width 1
    """
    length = 0
    for ch in s:
        if "EMOJI" in unicodedata.name(ch, ""):
            length += 2
        else:
            # East Asian wide characters (CJK)
            if unicodedata.east_asian_width(ch) in ("W", "F"):
                length += 2
            else:
                length += 1
    return length


def banner_title(title: str, pad: int = 3):
    text = f"{BOLD}{title}{RESET}"
    text_len = visual_len(title)

    total_len = text_len + pad * 2

    # Top border
    print("╭" + "─" * (total_len) + "╮")

    # Centre line
    print(" " * pad + text + " " * pad)

    # Bottom border
    print("╰" + "─" * (total_len) + "╯")


def section(title, emoji="🍽️"):
    content = f"{emoji}  {title}  {emoji}"
    visible = wcswidth(content)

    line = "─" * (visible + 4)
    print(f"\n{line}")
    print(f"  {content}")
    print(f"{line}")


def small_divider():
    print(DIM + " ──────────────────────────────── " + RESET)

def success(msg): print(GREEN + CHECK + " " + msg + RESET)
def error(msg): print("\n" + MAGENTA + CROSS + " " + msg + RESET)
def info(msg): print(CYAN + msg + RESET)


# Table builder
def render_table(headers, rows, *, padding=2, border_style="bold"):
    processed = []
    for row in rows:
        processed.append([str(row.get(h, "")) for h in headers])

    # Calculate column widths using visual_len
    col_widths = {}
    for idx, h in enumerate(headers):
        col_widths[h] = max(
            visual_len(h),
            max((visual_len(r[idx]) for r in processed), default=0)
        ) + padding * 2

    # Choose border style
    if border_style == "bold":
        TL, TR, BL, BR = "╔", "╗", "╚", "╝"
        H, V = "═", "║"
        TSEP, LSEP, RSEP, BSEP = "╦", "╠", "╣", "╩"
    else:
        TL = TR = BL = BR = "+"
        H = "-"
        V = "|"
        TSEP = LSEP = RSEP = BSEP = "+"

    # Build top border
    top = TL
    for h in headers:
        top += H * col_widths[h] + TSEP
    top = top[:-1] + TR
    print(top)

    # Header row
    header_line = V
    for h in headers:
        visible = visual_len(h)
        extra = col_widths[h] - visible - padding
        header_line += " " * padding + BOLD + h + RESET + " " * extra + V
    print(header_line)

    # Header separator
    sep = LSEP
    for h in headers:
        sep += H * col_widths[h] + TSEP
    sep = sep[:-1] + RSEP
    print(sep)

    # Body rows
    for row in processed:
        line = V
        for h, cell in zip(headers, row):
            vis = visual_len(cell)
            extra = col_widths[h] - vis - padding
            line += " " * padding + cell + " " * extra + V
        print(line)

    # Bottom border
    bottom = BL
    for h in headers:
        bottom += H * col_widths[h] + BSEP
    bottom = bottom[:-1] + BR
    print(bottom)
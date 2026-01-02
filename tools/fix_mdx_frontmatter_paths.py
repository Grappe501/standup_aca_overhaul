from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_DIR = ROOT / "src" / "content" / "docs_migrated"

KEYS_TO_NORMALIZE = {"source", "route"}


def strip_bom(s: str) -> str:
    # UTF-8 BOM can cause frontmatter detection to fail
    return s.lstrip("\ufeff")


def fix_frontmatter_block(text: str) -> tuple[str, bool]:
    """
    Fix YAML frontmatter escaping issues caused by Windows backslashes inside
    double-quoted strings, e.g. source: "loopholes\\file.html"

    We only normalize backslashes -> forward slashes on selected keys
    within the frontmatter block (between leading --- and the next ---).
    """
    original = text
    t = strip_bom(text)

    # Must start with frontmatter fence
    if not t.startswith("---"):
        return original, False

    # Find end fence
    # We handle both \n and \r\n by searching line-by-line.
    lines = t.splitlines(keepends=True)
    if not lines:
        return original, False

    if not lines[0].lstrip().startswith("---"):
        return original, False

    # Locate closing fence
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].lstrip().startswith("---"):
            end_idx = i
            break

    if end_idx is None:
        return original, False

    fm_lines = lines[: end_idx + 1]
    body_lines = lines[end_idx + 1 :]

    changed = False
    new_fm = []

    for line in fm_lines:
        # Only normalize inside YAML key lines (source:, route:)
        # Works with:
        #   source: "a\b\c.html"
        #   source: a\b\c.html
        #   source: 'a\b\c.html'
        stripped = line.lstrip()
        for key in KEYS_TO_NORMALIZE:
            prefix = f"{key}:"
            if stripped.lower().startswith(prefix):
                if "\\" in line:
                    line = line.replace("\\", "/")
                    changed = True
                break
        new_fm.append(line)

    if not changed:
        return original, False

    # Rebuild with original BOM if present
    rebuilt = "".join(new_fm) + "".join(body_lines)
    if original.startswith("\ufeff") and not rebuilt.startswith("\ufeff"):
        rebuilt = "\ufeff" + rebuilt
    return rebuilt, True


def main() -> None:
    if not TARGET_DIR.exists():
        raise SystemExit(f"Missing folder: {TARGET_DIR}")

    files = sorted(list(TARGET_DIR.rglob("*.mdx")))
    if not files:
        raise SystemExit(f"No .mdx files found under {TARGET_DIR}")

    fixed = 0
    scanned = 0

    for path in files:
        scanned += 1
        text = path.read_text(encoding="utf-8", errors="strict")
        updated, changed = fix_frontmatter_block(text)
        if changed:
            path.write_text(updated, encoding="utf-8")
            fixed += 1

    print(f"Scanned: {scanned}")
    print(f"Fixed:   {fixed}")


if __name__ == "__main__":
    main()

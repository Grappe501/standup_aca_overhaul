from pathlib import Path

def fix_html_docx_extensions(root_dir: str) -> None:
    root = Path(root_dir)

    if not root.exists():
        raise FileNotFoundError(f"Directory not found: {root}")

    changed = 0

    for path in root.rglob("*"):
        if path.is_file() and path.name.endswith(".html.docx"):
            new_path = path.with_name(path.name.replace(".html.docx", ".html"))

            if new_path.exists():
                print(f"SKIP (already exists): {new_path}")
                continue

            path.rename(new_path)
            print(f"RENAMED: {path} -> {new_path}")
            changed += 1

    print(f"\nDone. Files renamed: {changed}")


if __name__ == "__main__":
    # CHANGE THIS to the directory that contains your files
    TARGET_DIRECTORY = "./"

    fix_html_docx_extensions(TARGET_DIRECTORY)

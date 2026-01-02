from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class Plan:
    src: Path
    dst: Path
    reason: str


def build_plans(folder: Path) -> List[Plan]:
    plans: List[Plan] = []

    for p in folder.iterdir():
        if not p.is_file():
            continue

        name = p.name

        # Catch patterns like "..._docx" and "... ._docx"
        lower = name.lower()

        if lower.endswith("._docx"):
            dst = p.with_name(name[: -len("._docx")])
            plans.append(Plan(p, dst, "remove trailing '._docx'"))
            continue

        if lower.endswith("_docx"):
            dst = p.with_name(name[: -len("_docx")])
            plans.append(Plan(p, dst, "remove trailing '_docx'"))
            continue

    return plans


def validate(plans: List[Plan]) -> Tuple[List[Plan], List[Plan]]:
    ok: List[Plan] = []
    conflicts: List[Plan] = []
    for plan in plans:
        if plan.dst.exists():
            conflicts.append(plan)
        else:
            ok.append(plan)
    return ok, conflicts


def main() -> None:
    # Change this if the files are in a specific subfolder
    target_folder = Path(".").resolve()

    if not target_folder.exists():
        raise FileNotFoundError(target_folder)

    plans = build_plans(target_folder)
    plans.sort(key=lambda x: x.src.name.lower())

    if not plans:
        print(f"No matching files found in: {target_folder}")
        print("Looking for filenames ending with '._docx' or '_docx'.")
        return

    ok, conflicts = validate(plans)

    print(f"\nTarget folder: {target_folder}\n")
    print("=== PROPOSED RENAMES (DRY RUN) ===")
    for plan in ok:
        print(f"OK   : {plan.src.name}  ->  {plan.dst.name}   [{plan.reason}]")

    if conflicts:
        print("\n=== CONFLICTS (SKIPPED — DEST EXISTS) ===")
        for plan in conflicts:
            print(f"SKIP : {plan.src.name}  ->  {plan.dst.name}   [{plan.reason}]")

    print(f"\nSummary: {len(ok)} ready, {len(conflicts)} conflicts, {len(plans)} matches.")

    answer = input("\nType YES to apply these renames: ").strip()
    if answer != "YES":
        print("Aborted. No files were changed.")
        return

    changed = 0
    for plan in ok:
        plan.src.rename(plan.dst)
        changed += 1

    print(f"\nDone. Renamed {changed} files. ({len(conflicts)} skipped due to conflicts.)")


if __name__ == "__main__":
    main()

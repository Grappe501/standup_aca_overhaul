from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class RenamePlan:
    src: Path
    dst: Path
    reason: str


def build_plans(root: Path) -> List[RenamePlan]:
    plans: List[RenamePlan] = []

    for p in root.rglob("*"):
        if not p.is_file():
            continue

        name = p.name

        # Case 1: *.html.docx  ->  *.html
        if name.lower().endswith(".html.docx"):
            dst = p.with_name(name[: -len(".docx")])  # drop only the trailing ".docx"
            plans.append(RenamePlan(p, dst, "strip trailing .docx from .html.docx"))
            continue

        # Case 2: filenames ending with "_docx" (no dot), e.g. "X_y_docx"
        # We only do this if it *literally* ends with "_docx" (case-insensitive).
        if name.lower().endswith("_docx"):
            dst = p.with_name(name[: -len("_docx")])
            plans.append(RenamePlan(p, dst, "strip trailing _docx suffix"))
            continue

        # Optional Case 3: weird cases like "something.html.docx.docx" (rare)
        if ".html" in name.lower() and name.lower().endswith(".docx") and not name.lower().endswith(".html.docx"):
            # This is conservative: only if it contains ".html" and ends in .docx
            # We'll turn "X.html_something.docx" into "X.html_something" (remove .docx)
            dst = p.with_suffix("")  # remove only last suffix
            plans.append(RenamePlan(p, dst, "strip trailing .docx from file containing .html"))
            continue

    return plans


def validate_plans(plans: List[RenamePlan]) -> Tuple[List[RenamePlan], List[RenamePlan]]:
    """
    Returns (safe_plans, conflicting_plans)
    conflict = destination already exists
    """
    safe: List[RenamePlan] = []
    conflicts: List[RenamePlan] = []
    for plan in plans:
        if plan.dst.exists():
            conflicts.append(plan)
        else:
            safe.append(plan)
    return safe, conflicts


def main() -> None:
    root = Path(".").resolve()

    plans = build_plans(root)
    plans.sort(key=lambda x: str(x.src).lower())

    if not plans:
        print("No matching files found. Nothing to do.")
        return

    safe, conflicts = validate_plans(plans)

    print("\n=== PROPOSED RENAMES (DRY RUN) ===")
    for plan in safe:
        print(f"OK   : {plan.src}  ->  {plan.dst}   [{plan.reason}]")

    if conflicts:
        print("\n=== CONFLICTS (SKIPPED — DEST EXISTS) ===")
        for plan in conflicts:
            print(f"SKIP : {plan.src}  ->  {plan.dst}   [{plan.reason}]")

    print(f"\nSummary: {len(safe)} ready, {len(conflicts)} conflicts, {len(plans)} total matches.")

    # Ask for confirmation in-terminal
    answer = input("\nType YES to apply these renames: ").strip()
    if answer != "YES":
        print("Aborted. No files were changed.")
        return

    changed = 0
    for plan in safe:
        plan.src.rename(plan.dst)
        changed += 1

    print(f"\nDone. Renamed {changed} files. ({len(conflicts)} skipped due to conflicts.)")


if __name__ == "__main__":
    main()

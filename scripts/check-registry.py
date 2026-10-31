#!/usr/bin/env python3
"""Check the conformance registry: table shape, row fields, note placement and pins.

The registry is the authority for a conformance claim, so it is checked rather
than trusted: an entry that names a corpus it cannot resolve, a scope that does
not cover the class it signs, or notes filed under the wrong section are all
failures here.

Corpus hashes are verified against the commit the row names, which requires the
commit to exist locally. CI checks this repository out with full history; a
shallow clone fails with a message saying so.
"""

from __future__ import annotations

import calendar
import datetime
import hashlib
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "conformance" / "registry.md"

COLUMNS = [
    "ID",
    "Implementation",
    "Class",
    "Revision",
    "Impl. commit",
    "Corpus commit",
    "Result",
    "Reviewer",
    "Scope / term",
    "Date",
    "Status",
]
STATUSES = {"verified", "superseded", "withdrawn"}
ID_RE = re.compile(r"^`reg-\d{4}-\d{3}`$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TERM_RE = re.compile(r"(\d{4})-(\d{2})\s*$")
PIN_RE = re.compile(r"`(data/[\w./-]+\.json)`\s*`([0-9a-f]{64})`")
COMMIT_RE = re.compile(r"^`[0-9a-f]{7,40}`$")
REQUIRED_CORPUS = {
    "CLC-A": (
        "data/_vectors/clc-v1/vectors.json",
        "data/_vectors/clc-v1/property-cases.json",
    ),
    "CLC-D": (
        "data/_vectors/clc-d/containment-vectors.json",
        "data/_vectors/clc-d/authorize-chain-vectors.json",
    ),
}


def fail(messages: list[str]) -> None:
    for message in messages:
        print(f"  x {message}")
    print(f"registry check FAILED ({len(messages)} problem(s))")
    raise SystemExit(1)


def cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def section(text: str, heading: str) -> str:
    match = re.search(rf"^{re.escape(heading)}\s*$", text, re.M)
    if not match:
        return ""
    rest = text[match.end():]
    end = re.search(r"^## ", rest, re.M)
    return rest[: end.start()] if end else rest


def parse_rows(text: str, problems: list[str]) -> list[dict[str, str]]:
    claims = section(text, "## Verified claims")
    if not claims:
        problems.append("no '## Verified claims' section")
        return []

    header = None
    rows = []
    for number, line in enumerate(claims.splitlines(), 1):
        if not line.startswith("|"):
            continue
        if header is None:
            header = cells(line)
            if header != COLUMNS:
                problems.append(f"table header is {header}, expected {COLUMNS}")
            continue
        if set(line.replace("|", "").strip()) <= {"-"}:
            continue
        values = cells(line)
        if len(values) != len(COLUMNS):
            problems.append(f"row {number}: {len(values)} cells, expected {len(COLUMNS)}")
            continue
        rows.append(dict(zip(COLUMNS, values)))
    if not rows:
        problems.append("no claim rows in '## Verified claims'")
    return rows


def check_row(row: dict[str, str], problems: list[str]) -> None:
    identifier = row["ID"]
    if not ID_RE.match(identifier):
        problems.append(f"{identifier}: ID is not `reg-YYYY-NNN`")
    status = row["Status"]
    if status not in STATUSES:
        problems.append(f"{identifier}: status {status!r} not in {sorted(STATUSES)}")
    date = row["Date"]
    if not DATE_RE.match(date):
        problems.append(f"{identifier}: date {date!r} is not YYYY-MM-DD")
        return
    claimed = datetime.date.fromisoformat(date)
    if claimed > datetime.date.today():
        problems.append(f"{identifier}: claim dated in the future ({date})")
    for column in ("Class", "Reviewer", "Result"):
        if not row[column]:
            problems.append(f"{identifier}: {column} is empty")
    if not COMMIT_RE.match(row["Impl. commit"]):
        problems.append(
            f"{identifier}: implementation commit {row['Impl. commit']!r} is not a hash"
        )
    if not COMMIT_RE.match(row["Corpus commit"]):
        problems.append(
            f"{identifier}: corpus commit {row['Corpus commit']!r} is not a hash"
        )

    term = TERM_RE.search(row["Scope / term"])
    if term:
        year, month = int(term.group(1)), int(term.group(2))
        if not 1 <= month <= 12:
            problems.append(f"{identifier}: scope term month {month} is invalid")
            return
        ends = datetime.date(year, month, calendar.monthrange(year, month)[1])
        if claimed > ends:
            problems.append(
                f"{identifier}: claim dated {date} after its scope ended {ends}"
            )


def check_notes(text: str, rows: list[dict[str, str]], problems: list[str]) -> None:
    claims = section(text, "## Verified claims")
    for row in rows:
        identifier = row["ID"]
        heading = f"### {identifier} — notes"
        if not re.search(rf"^{re.escape(heading)}\s*$", claims, re.M):
            where = "outside '## Verified claims'" if re.search(
                rf"^{re.escape(heading)}\s*$", text, re.M
            ) else "missing"
            problems.append(f"{identifier}: notes section is {where}")
            continue
        match = re.search(rf"^{re.escape(heading)}\s*$", text, re.M)
        rest = text[match.end():]
        end = re.search(r"^## |^### ", rest, re.M)
        body = rest[: end.start()] if end else rest
        if not row["Corpus commit"].strip("`"):
            problems.append(f"{identifier}: no corpus commit")
        if "Independence" not in body:
            problems.append(f"{identifier}: notes do not state independence")
        if "Residual gaps" not in body:
            problems.append(f"{identifier}: notes do not state residual gaps")


def check_pins(text: str, rows: list[dict[str, str]], problems: list[str]) -> None:
    for row in rows:
        identifier = row["ID"]
        commit = row["Corpus commit"].strip("`")
        if not re.fullmatch(r"[0-9a-f]{7,40}", commit):
            problems.append(f"{identifier}: corpus commit {commit!r} is not a hash")
            continue
        probe = subprocess.run(
            ["git", "--no-pager", "cat-file", "-e", f"{commit}^{{commit}}"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if probe.returncode != 0:
            problems.append(
                f"{identifier}: corpus commit {commit} is not in this clone "
                "(fetch full history: actions/checkout with fetch-depth: 0)"
            )
            continue
        match = re.search(rf"^### {re.escape(identifier)} — notes\s*$", text, re.M)
        if not match:
            continue
        rest = text[match.end():]
        end = re.search(r"^## |^### ", rest, re.M)
        body = rest[: end.start()] if end else rest
        pins = PIN_RE.findall(body)
        if not pins:
            problems.append(f"{identifier}: notes pin no corpus file hash")
        pinned = {path for path, _ in pins}
        for family, required in REQUIRED_CORPUS.items():
            if family in row["Class"]:
                for path in required:
                    if path not in pinned:
                        problems.append(
                            f"{identifier}: class {family} needs {path} pinned"
                        )
        for path, expected in pins:
            blob = subprocess.run(
                ["git", "--no-pager", "show", f"{commit}:{path}"],
                cwd=ROOT,
                capture_output=True,
            )
            if blob.returncode != 0:
                problems.append(f"{identifier}: {path} does not exist at {commit}")
                continue
            actual = hashlib.sha256(blob.stdout).hexdigest()
            if actual != expected:
                problems.append(
                    f"{identifier}: {path} at {commit} hashes to {actual[:16]}…, "
                    f"registry says {expected[:16]}…"
                )


def check_closed(text: str, problems: list[str]) -> None:
    body = section(text, "## Superseded or withdrawn").strip()
    if not body or body == "None.":
        return
    rows = [line for line in body.splitlines() if line.startswith("|")]
    if len(rows) < 2:
        problems.append("'## Superseded or withdrawn' has prose but no table")
        return
    header = cells(rows[0])
    for column in ("ID", "Status", "Superseded by"):
        if column not in header:
            problems.append(f"closed-section table has no {column!r} column")
    for line in rows[2:]:
        values = dict(zip(header, cells(line)))
        identifier = values.get("ID", "?")
        if values.get("Status") not in {"superseded", "withdrawn"}:
            problems.append(f"{identifier}: closed row status must be superseded or withdrawn")
        if values.get("Status") == "superseded" and not values.get("Superseded by"):
            problems.append(f"{identifier}: superseded without a replacement ID")


def main() -> int:
    problems: list[str] = []
    text = REGISTRY.read_text(encoding="utf-8")
    rows = parse_rows(text, problems)
    seen = set()
    for row in rows:
        if row["ID"] in seen:
            problems.append(row["ID"] + ": duplicate row")
        seen.add(row["ID"])
        check_row(row, problems)
    check_notes(text, rows, problems)
    check_pins(text, rows, problems)
    check_closed(text, problems)
    if problems:
        fail(problems)
    print(f"registry OK: {len(rows)} claim(s), notes and pins verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())

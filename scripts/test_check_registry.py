#!/usr/bin/env python3
"""Self-test for scripts/check-registry.py.

The registry checker is the only thing standing between a wrong claim and the
public registry, so it is tested against deliberate damage rather than against
the file as it happens to be. Each case mutates a copy of the current registry,
runs the checks, and asserts that the expected complaint appears; a case that
stops failing means a check was weakened or removed.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("check_registry", ROOT / "scripts" / "check-registry.py")
assert SPEC and SPEC.loader
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)

REGISTRY = CHECKER.REGISTRY.read_text(encoding="utf-8")
CONFORMANCE = CHECKER.CONFORMANCE.read_text(encoding="utf-8")

MAINTAINERS_OK = """\
## Conformance reviewers

| Reviewer | Scope | Since | Term ends | Verified |
|---|---|---|---|---|
| Justin D. Kintzele ([@jdieselny](https://github.com/jdieselny)) | CLC-A core corpus: 154 vectors | 2026-10 | 2027-10 | 2026-10-31 |
| Justin D. Kintzele ([@jdieselny](https://github.com/jdieselny)) | CLC-D: 64 containment vectors | 2026-10 | 2027-10 | 2026-10-31 |
"""


def with_maintainers(body: str) -> None:
    handle = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False)
    handle.write(body)
    handle.close()
    CHECKER.MAINTAINERS = pathlib.Path(handle.name)


def with_conformance(body: str) -> None:
    handle = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False)
    handle.write(body)
    handle.close()
    CHECKER.CONFORMANCE = pathlib.Path(handle.name)


def problems(text: str) -> list[str]:
    found, _ = CHECKER.collect(text)
    return found


def expect(name, text, needle, setup=None):
    if setup:
        setup()
    found = problems(text)
    hit = [problem for problem in found if needle in problem]
    ok = bool(hit)
    print(f"{'PASS' if ok else 'FAIL'} {name}")
    if not ok:
        for problem in found:
            print(f"     got: {problem}")
    return name, ok


def main() -> int:
    results = []

    with_maintainers(MAINTAINERS_OK)
    with_conformance(CONFORMANCE)

    results.append(("baseline is clean", not problems(REGISTRY)))

    moved = REGISTRY.replace(
        "### `reg-2026-002` — notes", "### `reg-2026-000` — notes", 1
    )
    results.append(
        expect("orphan notes", moved, "has no row in '## Verified claims'")
    )

    in_verification = REGISTRY.replace("| 2026-10-31 | verified |", "| 2026-10-31 | Verified |", 1)
    results.append(expect("status is an enum", in_verification, "status 'Verified' not in"))

    bad_hash = REGISTRY.replace(
        "3c1a5672d6f107444903f06c51a71ce92451f1b45ca92c5a84a345b0de5a5bbd",
        "3c1a5672d6f107444903f06c51a71ce92451f1b45ca92c5a84a345b0de5a5bb0",
        1,
    )
    results.append(expect("corpus hash is verified", bad_hash, "hashes to"))

    after_term = REGISTRY.replace("bootstrap review; not independent | 2026-10-31", "CLC-A core, 2026-01 | 2026-10-31", 1)
    results.append(expect("claim inside its term", after_term, "after its scope ended"))

    junk_commit = REGISTRY.replace("`8db495ac68f9`", "`not-a-hash`", 1)
    results.append(expect("implementation commit is a hash", junk_commit, "is not a hash"))

    unknown_class = REGISTRY.replace("| CLC-A core | CLC-1.19", "| CLC-E | CLC-1.19", 1)
    results.append(expect("class is a closed set", unknown_class, "is not one of"))

    dropped_pin = REGISTRY.replace(
        "  - `data/_vectors/clc-v1/property-cases.json`\n"
        "    `f00ed1f49299293ac9fff1e10287b9642aa49d6dacf25b2b4a1be2d7103b2f07`\n",
        "",
        1,
    )
    results.append(expect("required corpus is pinned", dropped_pin, "needs data/_vectors"))

    placeholder = REGISTRY.replace(
        "- Independence: cleanroom implementation; no access to the `varwof` reference\n"
        "  implementations, stated by the author and supported by the repository's\n"
        "  cleanroom leash.",
        "- Independence: none",
        1,
    )
    results.append(expect("independence is stated", placeholder, "placeholder"))

    owned_claim = REGISTRY.replace(
        "- Independence: the implementation shares an author with the corpora. It is\n"
        "  regression evidence, not independent evidence, and it does not count towards\n"
        "  P12 or the two-implementation transfer criterion on its own.",
        "- Independence: cleanroom implementation, built without reading any other implementation.",
        1,
    )
    results.append(
        expect("project-owned code cannot claim independence", owned_claim, "shares an author")
    )

    dangling = REGISTRY.replace(
        "## Superseded or withdrawn\n\nNone.",
        "## Superseded or withdrawn\n\n| ID | Status | Superseded by |\n|---|---|---|\n"
        "| `reg-2026-001` | superseded | `reg-2026-999` |",
        1,
    )
    results.append(expect("superseded names a real row", dangling, "which is not a row"))

    future = REGISTRY.replace("| 2026-10-31 | verified |", "| 2099-01-01 | verified |", 1)
    results.append(expect("claim is not dated in the future", future, "in the future"))

    def only_clc_a():
        with_maintainers(
            MAINTAINERS_OK.replace(
                "| Justin D. Kintzele ([@jdieselny](https://github.com/jdieselny)) | CLC-D: 64 containment vectors | 2026-10 | 2027-10 | 2026-10-31 |\n",
                "",
            )
        )

    row_002 = next(
        line for line in REGISTRY.splitlines() if line.startswith("| `reg-2026-002`")
    )
    justin_row = REGISTRY.replace(
        row_002,
        "| `reg-2026-002` | `varwof/register` (Go) | CLC-D | CLC-1.19, Section 12 core corpus | "
        "`e422020b0e55` | `1ef567c` | 154/154 | Justin D. Kintzele | CLC-D, 2027-10 | "
        "2026-10-31 | verified |",
        1,
    )
    results.append(
        expect("reviewer scope covers the class", justin_row, "does not cover", setup=only_clc_a)
    )
    with_maintainers(MAINTAINERS_OK)

    def unknown_reviewer():
        with_maintainers(MAINTAINERS_OK)

    no_reviewer = REGISTRY.replace(
        "Jijie Wei (editor, bootstrap) | bootstrap review; not independent",
        "Nobody Atall | CLC-A core, 2027-10",
        1,
    )
    results.append(
        expect("reviewer is appointed", no_reviewer, "not an appointed reviewer", setup=unknown_reviewer)
    )

    def class_drift():
        with_conformance(CONFORMANCE.replace("`vectors.json` (154) and", "(154) and", 1))

    results.append(
        expect("CONFORMANCE names the corpus", REGISTRY, "does not name vectors.json", setup=class_drift)
    )

    with_conformance(CONFORMANCE)

    failed = [name for name, ok in results if not ok]
    print()
    if failed:
        print(f"registry checker self-test FAILED: {len(failed)} case(s)")
        return 1
    print(f"registry checker self-test OK: {len(results)} cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Enforce D-097 rule 1: content consumes incident mappings, it never mints them.

A spoke page may print `Seen here: Recorded` against a register row ONLY if the
Corrections Register carries an explicit instance mapping for that row.

Mappings are declared in the Corrections Register with a machine-readable marker
on the row that owns the incident:

    ⟪instance-of: TL-10 · TL-14⟫

Note the delimiter: ⟪…⟫, not ⟦…⟧. The ⟦…⟧ pair is already owned by
check-registers.py, whose grammar is ⟦instances=N gate=PATH validated=REF⟧;
reusing it made that checker fail on every row lodged here.

A bare mention of a register ID anywhere else in a corrections row does NOT
count. That is deliberate: most register-ID mentions in that file are about a
row's own classification (residual hygiene, boundary audits, trigger-spelling
collisions, gaps in the register) rather than an incident instantiating the row,
and D-097 rule 2 says published evidence must instantiate the claim, not
resemble it. Requiring an explicit marker makes the producer state which one it
is, at logging time, instead of leaving a reader to infer it later.

Usage:
    check-spoke-evidence.py <spoke.md> [<spoke.md> ...]
    check-spoke-evidence.py --self-test

Exit 1 on any unbacked Recorded line.
"""
import re
import sys
import pathlib

REGISTER = pathlib.Path(__file__).resolve().parents[1].parent / "Corrections Register.md"
ROW_ID = r"(?:TL|RL|AL|PL|IL|CL)-\d\d?[A-Z]?"
MARKER = re.compile(r"⟪instance-of:\s*([^⟫]+)⟫")
# A row entry heading, e.g.  **TL-04 · "I verified it."** · Kind 1 · S4 · ...
ENTRY = re.compile(r"^\*\*(" + ROW_ID + r")\s*·")
SEEN = re.compile(r"^\*\*Seen here:\*\*\s*(Recorded|Not recorded)", re.I)


def mapped_ids(register_text):
    """Every register row ID the Corrections Register declares an instance for."""
    out = {}
    cur = None
    for line in register_text.split("\n"):
        m = re.match(r"^\|\s*(C-\d+)\s*\|", line)
        if m:
            cur = m.group(1)
        for block in MARKER.findall(line):
            for rid in re.findall(ROW_ID, block):
                out.setdefault(rid, set()).add(cur or "?")
    return out


def audit(path, mapped):
    """Return (findings, n_recorded, n_not). A finding is an unbacked Recorded."""
    lines = pathlib.Path(path).read_text(encoding="utf-8").split("\n")
    findings, rec, notrec, current = [], 0, 0, None
    stale = []
    for i, line in enumerate(lines, 1):
        e = ENTRY.match(line)
        if e:
            current = e.group(1)
            continue
        s = SEEN.match(line)
        if not s:
            continue
        if s.group(1).lower() == "recorded":
            rec += 1
            if current and current not in mapped:
                findings.append((i, current))
        else:
            notrec += 1
            if current:
                stale.append(current)
    return findings, rec, notrec, stale


def _unused(mapped, seen_not_recorded):
    """Rows the register HAS an instance for, but the page prints as Not recorded.

    Not a failure: a page may legitimately decline to cite an instance. It is a
    prompt for a decision, because the usual cause is that the mapping was
    lodged after the page was written and the page now understates its own
    evidence — which is how a page ends up claiming a group has no recorded
    failures while using one of them as that group's worked example.
    """
    return sorted(r for r in seen_not_recorded if r in mapped)


def self_test():
    """The gate must fail on known-bad input before it is trusted."""
    ok = True
    mapped = {"TL-04": {"C-41"}}
    import tempfile

    bad = (
        '**TL-04 · "I verified it."** · Class B\n'
        "**Seen here:** Recorded. 13 August 2026.\n"
        '**TL-11 · "This finding is real."** · Class C\n'
        "**Seen here:** Recorded twice, 1 to 11 August 2026.\n"
        '**TL-01 · "The tests pass."** · Class B\n'
        "**Seen here:** Not recorded.\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(bad)
        p = f.name
    findings, rec, notrec, _ = audit(p, mapped)
    if [f[1] for f in findings] != ["TL-11"]:
        print(f"  FAIL: expected TL-11 unbacked, got {[f[1] for f in findings]}")
        ok = False
    if (rec, notrec) != (2, 1):
        print(f"  FAIL: expected 2 recorded / 1 not, got {rec} / {notrec}")
        ok = False

    # marker parsing, including a multi-ID marker
    m = mapped_ids("| C-21 | text ⟪instance-of: TL-10 · RL-3C⟫ |\n| C-04 | mentions TL-10 only |")
    if set(m) != {"TL-10", "RL-3C"}:
        print(f"  FAIL: marker parse got {sorted(m)}")
        ok = False
    if m.get("TL-10") != {"C-21"}:
        print(f"  FAIL: owner attribution got {m.get('TL-10')}")
        ok = False
    print("  self-test: PASS" if ok else "  self-test: FAIL")
    return 0 if ok else 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    if not argv:
        print(__doc__)
        return 2
    mapped = mapped_ids(REGISTER.read_text(encoding="utf-8"))
    print(f"Corrections Register declares instance mappings for {len(mapped)} register rows.")
    rc = 0
    for path in argv:
        findings, rec, notrec, stale = audit(path, mapped)
        name = pathlib.Path(path).name
        print(f"\n{name}: {rec} recorded, {notrec} not recorded")
        if findings:
            rc = 1
            for line_no, rid in findings:
                print(f"  UNBACKED  {rid}  ({name}:{line_no})")
                print(f"            no ⟪instance-of: {rid}⟫ marker in the Corrections Register.")
                print(f"            Lodge the mapping there first, or set this row to Not recorded.")
        else:
            print("  every Recorded row traces to a lodged mapping")
        for rid in _unused(mapped, stale):
            print(f"  REVIEW    {rid} reads Not recorded, but the register lodges an instance")
            print(f"            for it. Cite it, or say on the page why it was rejected.")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

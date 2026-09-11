#!/usr/bin/env python3
"""diff-catalogue.py — what changed in the catalogue since an assessment was taken.

Written for D-261, 2026-09-07. This is the mechanism behind re-assessment: what
has changed for a customer WITHOUT them doing anything. Their own environment
drifting is found by re-running the trust check; this finds the other half —
rows added from other people's research, controls that did not exist when they
were assessed and now do, and rows withdrawn from under them.

WHAT IT COMPARES, AND WHY THAT ARTEFACT. Two committed copies of
tools/trust-check-v1/register-data.json, read with `git show`. That file is the
normalised row set the trust-check tool actually ships, so the diff compares what
two readers SAW, not what canon happened to contain. It also means row identity
comes from the row IDs, which are stable and never reused (registers/README.md,
"Row ID rules") — the property the whole diff rests on.

THE ASSESSMENT CONTRACT. `--assessment` takes JSON:

    {"catalogueVersion": "FF-2026.1", "date": "2026-09-02",
     "rows": {"IL-1A": "open", "IL-1F": "closed", ...}}

Three keys, and `rows` maps a row ID to that row's gap state in the assessed
environment. This is a FLOOR, not the schema: the catalogue/assessment split
(the sibling brief) may give an assessment record many more fields, and this tool
needs only these three to work.

Coverage gaps, declared rather than implied:

  * A release with no recorded commit cannot be diffed FROM by this tool.
    FF-2026.1's commit was never written down, and the tool REFUSES rather than
    reconstructing one from the log — a derived commit presented as a pin is the
    unfounded claim the version scheme exists to prevent. That is a limit of this
    tool, NOT a claim that the release is unrecoverable: the published repository
    holds the registers as shipped, and the row set reads straight out of them.
    catalogue-releases.json records where.
  * Availability is not in canon yet. When neither snapshot carries an
    `availability` field, the availability sections report NOT COMPUTABLE and the
    exit code is 2, never 0 with a zero count. A zero that means "no data" and a
    zero that means "nothing changed" are the same character, and the first one
    silently reads as reassurance.
  * It does not compare row CONTENT. A row whose failure text, severity or
    mechanism was rewritten between versions is not reported. Row wording changes
    constantly (D-258 alone rewrote twelve cells) and reporting them would bury
    the four things a reader can act on.
  * It does not know whether a control is any good. Availability says a control
    of the named shape exists and is obtainable. Maturity is a judgement, and this
    project does not let a judgement carry a count (registers/README.md, Severity).
"""
import argparse, json, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]          # public repository root
SNAPSHOT_PATH = "tools/trust-check/assets/register-data.json"
RELEASES_PATH = pathlib.Path(__file__).resolve().parents[1] / "assets/catalogue-releases.json"

# Gap values that mean the failure is not treated in the assessed environment, and
# so the values for which "a control became available" is news. Taken from
# registers/README.md's Gap vocabulary.
OPEN_GAPS = {"open", "partially closed"}

AVAILABLE = "available"
WITHDRAWN = "withdrawn"


# ---------------------------------------------------------------- pure logic
# Everything below takes dicts and returns dicts. No git, no filesystem, so the
# self-test exercises the real comparison rather than a re-implementation of it.

def index_rows(snapshot):
    return {row["id"]: row for row in snapshot.get("rows", [])}


def has_availability(snapshot):
    return any("availability" in row for row in snapshot.get("rows", []))


def diff(snapshot_from, snapshot_to, assessment=None):
    a, b = index_rows(snapshot_from), index_rows(snapshot_to)
    scored = set((assessment or {}).get("rows", {}))
    gap = (assessment or {}).get("rows", {})

    added = sorted(set(b) - set(a))
    retired = sorted(set(a) - set(b))

    result = {
        "from": snapshot_from.get("catalogueVersion"),
        "to": snapshot_to.get("catalogueVersion"),
        "rowsAdded": added,
        "rowsRetired": retired,
        # An added row was not in the catalogue when the assessment ran, so it was
        # never scored. Stated separately from `rowsAdded` because with no
        # assessment supplied the two are the same list and the distinction is the
        # whole reason a customer cares.
        "rowsNeverScored": [rid for rid in added if rid not in scored] if assessment else None,
        "rowsRetiredThatWereScored": [rid for rid in retired if rid in scored] if assessment else None,
    }

    # BOTH snapshots must carry the field, not either. Found 2026-09-07 when the
    # D-263 migration introduced availability: with `or`, a diff across the
    # migration read every row as "became available", because the old snapshot
    # had no field and absent compared unequal to `available`. That is the worst
    # possible failure for this tool - a fabricated renewal signal on 106 rows,
    # arriving as good news. The self-test now covers it.
    if not (has_availability(snapshot_from) and has_availability(snapshot_to)):
        result["availability"] = None      # NOT COMPUTABLE - see the docstring
        return result

    became, withdrawn = [], []
    for rid in sorted(set(a) & set(b)):
        was, now = a[rid].get("availability"), b[rid].get("availability")
        if was == now:
            continue
        if now == AVAILABLE and was != AVAILABLE:
            became.append(rid)
        elif was == AVAILABLE and now == WITHDRAWN:
            withdrawn.append(rid)

    result["availability"] = {
        "becameAvailable": became,
        "withdrawn": withdrawn,
        # The renewal sentence. Filtered to rows the assessment recorded as not
        # treated: a control arriving for a failure you had already closed is not
        # news, and reporting it is how a real signal gets skimmed past.
        "becameAvailableOnOpenRows":
            [rid for rid in became if gap.get(rid) in OPEN_GAPS] if assessment else None,
        "withdrawnOnRowsYouRelyOn":
            [rid for rid in withdrawn if gap.get(rid) not in OPEN_GAPS and rid in scored]
            if assessment else None,
    }
    return result


# ---------------------------------------------------------------- git access

def releases():
    return json.loads(RELEASES_PATH.read_text(encoding="utf-8"))


def resolve(ref):
    """A release version, or a git rev. Returns (rev, label)."""
    for release in releases()["releases"]:
        if release["version"] == ref:
            if not release.get("commit"):
                raise SystemExit(
                    f"[FAIL] (catalogue diff) {ref} has no recorded commit, so this tool "
                    f"cannot diff from it.\n         {release.get('commitNote', '')}\n"
                    f"         Recoverable from: {release.get('recoverableFrom', '(not recorded)')}\n"
                    f"         Or diff from a later release, or from a commit you name directly.")
            return release["commit"], ref
    return ref, ref


def snapshot_at(rev):
    out = subprocess.run(["git", "show", f"{rev}:{SNAPSHOT_PATH}"],
                         cwd=ROOT, capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"[FAIL] (catalogue diff) no {SNAPSHOT_PATH} at {rev}: "
                         f"{out.stderr.strip()}")
    return json.loads(out.stdout)


# ---------------------------------------------------------------- self-test

def self_test():
    """Run the comparison against inputs it MUST catch, and inputs it must not.

    Every case here failed at least once against a deliberately wrong version of
    diff() while this was being written; they are regression cases, not decoration.
    """
    base_rows = [
        {"id": "IL-1A", "availability": "none"},
        {"id": "IL-1F", "availability": "available"},
        {"id": "TL-09", "availability": "none"},
        {"id": "RL-5C", "availability": "available"},
    ]
    after_rows = [
        {"id": "IL-1A", "availability": "available"},   # became available
        {"id": "IL-1F", "availability": "withdrawn"},   # withdrawn under them
        {"id": "TL-09", "availability": "none"},        # unchanged
        {"id": "CL-9Z", "availability": "available"},   # added
        # RL-5C absent -> retired
    ]
    snap_a = {"catalogueVersion": "FF-2026.1", "rows": base_rows}
    snap_b = {"catalogueVersion": "FF-2026.2", "rows": after_rows}
    assessment = {"catalogueVersion": "FF-2026.1", "date": "2026-09-02",
                  "rows": {"IL-1A": "open", "IL-1F": "closed",
                           "TL-09": "open", "RL-5C": "closed"}}

    failures = []

    def want(label, got, expected):
        if got != expected:
            failures.append(f"{label}: expected {expected!r}, got {got!r}")

    d = diff(snap_a, snap_b, assessment)
    want("rowsAdded", d["rowsAdded"], ["CL-9Z"])
    want("rowsRetired", d["rowsRetired"], ["RL-5C"])
    want("rowsNeverScored", d["rowsNeverScored"], ["CL-9Z"])
    want("rowsRetiredThatWereScored", d["rowsRetiredThatWereScored"], ["RL-5C"])
    want("becameAvailable", d["availability"]["becameAvailable"], ["IL-1A"])
    want("withdrawn", d["availability"]["withdrawn"], ["IL-1F"])
    # The renewal sentence: IL-1A was open, so it is news.
    want("becameAvailableOnOpenRows",
         d["availability"]["becameAvailableOnOpenRows"], ["IL-1A"])
    # And the filter must SUPPRESS a control arriving on a row already closed.
    quiet = diff(snap_a, snap_b,
                 {"catalogueVersion": "FF-2026.1", "rows": {"IL-1A": "closed"}})
    want("closed row suppressed",
         quiet["availability"]["becameAvailableOnOpenRows"], [])
    # IL-1F was relied on (recorded closed) and has been withdrawn.
    want("withdrawnOnRowsYouRelyOn",
         d["availability"]["withdrawnOnRowsYouRelyOn"], ["IL-1F"])

    # THE CASE THIS TOOL EXISTS TO NOT GET WRONG. Canon carries no availability
    # data today. A diff over two snapshots with no availability field must report
    # NOT COMPUTABLE, never an empty list that reads as "nothing changed".
    bare_a = {"catalogueVersion": "FF-2026.1", "rows": [{"id": "IL-1A"}]}
    bare_b = {"catalogueVersion": "FF-2026.2", "rows": [{"id": "IL-1A"}, {"id": "CL-9Z"}]}
    bare = diff(bare_a, bare_b, assessment)
    want("no availability data reports None", bare["availability"], None)
    want("row adds still work without availability", bare["rowsAdded"], ["CL-9Z"])

    # THE MIGRATION CASE. One side carries availability and the other does not,
    # which is exactly what a diff spanning the D-263 migration looks like. It
    # must report NOT COMPUTABLE: absent is not `none`, and treating it as a
    # transition invents a renewal signal on every row in the catalogue.
    half = diff(bare_a, snap_b, assessment)
    want("availability on one side only reports None", half["availability"], None)
    half_rev = diff(snap_a, bare_b, assessment)
    want("availability on the other side only reports None",
         half_rev["availability"], None)

    # A row present in both with availability unchanged must appear nowhere.
    want("unchanged row is silent",
         "TL-09" in d["availability"]["becameAvailable"] + d["availability"]["withdrawn"],
         False)

    if failures:
        print(f"[FAIL] (catalogue diff self-test) {{\"failed\": {len(failures)}}}")
        for f in failures:
            print(f"         {f}")
        return 1
    print('[ ok ] (catalogue diff self-test) {"cases": 13}')
    return 0


# ---------------------------------------------------------------- reporting

def report(d, assessment):
    lines = [f"Catalogue diff: {d['from']} -> {d['to']}"]
    if assessment:
        lines.append(f"Assessment taken {assessment.get('date', '(undated)')} "
                     f"against {assessment.get('catalogueVersion')}")
    lines.append("")
    lines.append(f"Rows added since your assessment: {len(d['rowsAdded'])}"
                 + (f"  {', '.join(d['rowsAdded'])}" if d["rowsAdded"] else ""))
    lines.append(f"Rows retired since your assessment: {len(d['rowsRetired'])}"
                 + (f"  {', '.join(d['rowsRetired'])}" if d["rowsRetired"] else ""))
    if d["rowsRetiredThatWereScored"]:
        lines.append(f"  ...of which you were scored against, and should stop chasing: "
                     f"{', '.join(d['rowsRetiredThatWereScored'])}")
    if d["availability"] is None:
        lines.append("")
        lines.append("Control availability: NOT COMPUTABLE. Neither snapshot carries an "
                     "`availability` field.")
        lines.append("  This is the uncovered class, not a clean result. The field is "
                     "specified in D-261 and is")
        lines.append("  populated as part of the catalogue/assessment split; until then "
                     "no claim can be made about")
        lines.append("  controls appearing or being withdrawn.")
        return "\n".join(lines), 2
    av = d["availability"]
    lines.append("")
    news = av["becameAvailableOnOpenRows"] if assessment else av["becameAvailable"]
    lines.append(f"Controls that became available on rows you had open: {len(news)}"
                 + (f"  {', '.join(news)}" if news else ""))
    gone = av["withdrawnOnRowsYouRelyOn"] if assessment else av["withdrawn"]
    lines.append(f"Controls withdrawn: {len(gone)}" + (f"  {', '.join(gone)}" if gone else ""))
    return "\n".join(lines), 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--from", dest="frm", help="catalogue version (FF-2026.1) or git rev")
    ap.add_argument("--to", dest="to", default="HEAD",
                    help="catalogue version or git rev (default HEAD)")
    ap.add_argument("--assessment", help="assessment JSON; see the module docstring")
    ap.add_argument("--json", action="store_true", help="emit the diff as JSON")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if not args.frm:
        ap.error("--from is required (or use --self-test)")

    assessment = None
    if args.assessment:
        assessment = json.loads(pathlib.Path(args.assessment).read_text(encoding="utf-8"))
        pinned = assessment.get("catalogueVersion")
        if pinned and pinned != args.frm:
            print(f"[FAIL] (catalogue diff) the assessment is pinned to {pinned}, "
                  f"and --from says {args.frm}. Diff from the version it was taken against.")
            return 1

    rev_a, _ = resolve(args.frm)
    rev_b, _ = resolve(args.to)
    d = diff(snapshot_at(rev_a), snapshot_at(rev_b), assessment)
    if args.json:
        print(json.dumps(d, indent=2))
        return 0 if d["availability"] is not None else 2
    text, code = report(d, assessment)
    print(text)
    return code


if __name__ == "__main__":
    sys.exit(main())

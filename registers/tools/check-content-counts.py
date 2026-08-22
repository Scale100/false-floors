#!/usr/bin/env python3
"""
check-content-counts.py - fails when a page in content/ states register counts
that disagree with the registers themselves.

WHY THIS EXISTS
    The cross-register total was published wrong in four documents with three
    different values (25/75/33, 26/74/33, and a per-register list that matched
    no register state), every one hand-copied from another document rather than
    derived. The strategy doc's own rule already said a page/register mismatch
    is a defect in the page; the rule did not bind, because nothing ran. This
    does.

TRUTH SOURCE
    check-registers.py, in this directory. This script never parses a register
    file itself - one derivation, not two. If check-registers.py changes its
    output format, this fails loudly rather than passing silently.

WHAT IS COVERED (each of these fails the run)
    1. TRIPLE      A sentence stating a prevented / detected / survives triple,
                   compared against the cross-register total and against every
                   individual register's triple. Matching none is a failure.
                   Numerals and NUMBER WORDS both count (2026-08-17). House
                   style spells one to nine, so before that change every
                   single-digit count on a style-compliant page was invisible -
                   including the truth spoke's own headline, "zero prevented,
                   nine detected, six surviving", which was unenforced on main
                   while this script reported the page clean. Found by breaking
                   a page on purpose; "passing" had meant nothing.
                   A triple requires THREE DISTINCT number tokens. Without that,
                   class names used as vocabulary ("prevented / detected /
                   survives defined") pick up one nearby number and score 7/7/7.
    2. SLASHFORM   A "133 / 26 / 74 / 33" style compact total.
    3. DOTLIST     A per-register list in "5*12*6 / 2*15*6 / ..." middle-dot
                   form, each triple compared against that register.
    4. EVIDPAIR    A "66 evidenced ... 62 candidate(s)" pair (added 2026-08-21
                   with D-107's tier split). Both numbers on one line, in that
                   order, each anchored to its own keyword; the pair must match
                   the cross-register total or one register's own split. A
                   lone "N evidenced" with no candidate count on the line is
                   NOT checked - same trade as the single-class gap below, and
                   for the same reason (subset claims: "23 of the 66 evidenced
                   rows were confirmed after enumeration" must not fire).
                   Vocabulary lines ("rows are either evidenced or candidate")
                   carry no second number and are ignored; a line where both
                   keywords walk back onto ONE number token is rejected as a
                   pair rather than misread.
WHAT IS NOT COVERED - stated rather than pretended
    - ROW COUNTS ARE NOT CHECKED AT ALL. A first version flagged any "N rows" /
      "N failure modes" that was not a register size. It could not tell a SIZE
      claim ("133 named failure modes") from a SUBSET claim ("96 of 133 rows are
      straight transfers", "11 alien rows"), and on the real corpus 4 of its 9
      hits were legitimate subset statements plus one hit on "48 hours of
      activity into rows". Rather than ship a check that cries wolf, the class
      is declared uncovered here. A wrong ROW total will not be caught. The
      A/B/C checks below do reconcile against rows, so a row error that also
      moves the split is still caught indirectly.
    - Blockquoted lines are SKIPPED, and the count of skipped lines is printed.
      Correction banners quote known-bad numbers on purpose, and a check that
      fired on its own incident report would train the reader to skim. The cost
      is that a genuine count inside a pull quote is invisible to this check.
    - Files carrying "SUPERSEDED" in their first 40 lines are skipped entirely,
      and each one is named in the output. A retired draft keeps its original
      wrong numbers by design; failing on it forever would train the reader to
      ignore the red. "NEEDS A REWRITE" is NOT a skip - those stay red until
      rewritten, which is the point of the flag.
    - Prose ratios ("roughly a third") are not checked. They are not numbers.
    - THE WORD "ONE" IS NOT READ AS A COUNT, and number words from ten up are
      not read at all. Both are stated in NUMWORDS with their reasoning. The
      cost is real and bounded: a triple written entirely in two-digit words
      ("twelve prevented, seventy-six detected...") is not checked. Parsing it
      wrong - "seventy-six" read as 6 - would be worse than not parsing it.
    - A SINGLE class stated alone ("nine of the 15 can be converted") is not
      checked; only complete triples are. The board page states its counts one
      at a time and is therefore covered by nothing here. This gap has already
      cost something real: the essay draft's "the 33 rows that survive
      everything" sat uncaught behind a clean run on that file, and was found
      2026-08-17 by grep, not by this tool. If a stale single-class count
      matters, grep for it - do not read a green run as coverage.
    - A TRIPLE WRITTEN OUT OF CANONICAL ORDER is not checked (added
      2026-08-17). The three classes must appear A, then B, then C, with their
      numbers in that order, or the line is not treated as a triple. This is
      what stops three unrelated clauses on one long bullet being read as a
      triple - the case that produced 4/5/9 on a correct line. The cost is
      that "44 survive, 77 detected, 12 prevented" would go uncaught. Every
      fixture in KNOWN_BAD and every count on every live page is written in
      canonical order, so the exchange buys silence on real prose at the price
      of a form nobody writes.
    - It cannot tell whether a number was correct on the date the page was
      written. It only asks whether the page agrees with the registers today.

USAGE
    python3 registers/tools/check-content-counts.py [--root PATH] [--strict]
    python3 registers/tools/check-content-counts.py --self-test

KNOWN COVERAGE QUIRK (added 2026-08-17, found writing spoke 5)
    A stage-level or group-level triple written in digits is read as a
    cross-register total and fails against the framework total. The line that
    tripped it: "Stage 3 is 0 prevented, 0 detected, 3 survives" - true of one
    stage of one register, nonsense as a framework total. Write per-stage and
    per-group splits in words ("none prevented, five detected, one survives"),
    which every spoke page does. Not worth suppressing: the same pattern also
    catches a genuine stale cross-register triple.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent

# Each register states its classes in its own verbs. The truth register says
# "retired by withholding / converted by executing-then-diffing / nothing
# converts"; the others say "prevented / detected / survives"; recovery says
# "prevented / recoverable / irreversible". All three vocabularies are listed,
# because a check that only knew the README's words missed the truth spoke's
# stale 3/7/5 outright during validation.
PREVENTED = r"prevented|refusable|refused outright|prevent outright|can be refused|withholding|withheld"
DETECTED = r"detected|catchable|caught every time|can be caught|converted|converts|convertible|executing-then-diffing|recoverable"
# "surviving" is here because the truth spoke's headline sentence used it and
# `survives?` did not match, so the flagship page's own split was unenforced.
SURVIVES = r"surviv(?:e|es|ed|ing)|on your desk|land on a person|lands on a person|irreversible|nothing converts"

# House style spells one to nine and uses numerals from 10 (Fairfax). A check
# that only read numerals therefore could not see any single-digit count on a
# style-compliant page - which is every count on the truth register, whose
# split is 0/9/6. Found 2026-08-17 by breaking the board page on purpose: the
# identical error passed in words and failed in digits.
#
# "none" is deliberately NOT mapped to 0. It reads as a quantity in "none can
# be prevented" and as a pronoun in "none of the fifteen", and nothing in a
# 45-character window separates them.
# TWO CLASSES ARE DELIBERATELY NOT PARSED, both found by fixtures during this
# change rather than in review:
#
#   "one" is excluded. In "not one of them is prevented, detected, or survives"
#   every class walks back onto the same pronoun and the line reads 1/1/1. No
#   register currently has a count of one in any class (the A column across the
#   six is 2,0,2,5,3,0), so excluding it costs nothing today and removes the
#   largest false-positive source. A genuine "one prevented" will not be seen.
#
#   Ten and above are excluded. House style writes them as numerals, and the
#   compound forms mis-parse: "seventy-seven" ends in a hyphen-bounded "seven"
#   and read as 7, "forty-four" as 4, turning 12/77/44 into 12/7/4 - a wrong
#   number reported confidently, which is worse than no check at all.
NUMWORDS = {
    "zero": 0, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
}
# Hyphen guards, not \b: \b treats "-" as a boundary, so "seventy-seven" would
# match its own tail.
NUM_RE = re.compile(
    r"(?<![\w-])(\d{1,3}|" + "|".join(sorted(NUMWORDS, key=len, reverse=True)) + r")(?![\w-])",
    re.I)

LOOKBACK = 45

# A class word in `key: value` form takes the number AFTER it, not before.
# Without this, a line quoting register frontmatter - "(`rows: 25`,
# `prevented: 5`, `recoverable: 11`, `irreversible: 9`)" - walks every class
# back onto the PREVIOUS key's value and reads 25/5/11: a systematic
# off-by-one that reported a correct line as wrong. Found 2026-08-17 on the
# recovery spoke's entry in the strategy doc. Reading the colon form properly
# is better than skipping it, because a genuine `prevented: 6` is then still
# caught rather than made invisible.
COLON_VALUE = re.compile(
    r"\s*[:=]\s*(\d{1,3}|" + "|".join(sorted(NUMWORDS, key=len, reverse=True)) + r")(?![\w-])",
    re.I)


def as_int(token):
    """'6' -> 6, 'six' -> 6, 'Six' -> 6."""
    return int(token) if token.isdigit() else NUMWORDS[token.lower()]


def near(line, keywords):
    """(value, position) for the number belonging to a keyword, or None.

    Two forms, in this order:

    1. `keyword: N` - the value FOLLOWS the keyword. See COLON_VALUE.
    2. otherwise, the number nearest-PRECEDING the keyword.

    Form 2 is deliberately NOT 'a number within N chars of the keyword' - that
    was the first implementation and it let all three classes latch onto the
    SAME number, so "5 prevented, 11 recoverable, 9 irreversible" read as 5/5/5
    and passed as a false positive. Anchor on the keyword, then walk back.

    Numerals and number words both count, because the house style guarantees
    the small numbers will be words. See NUMWORDS.

    The POSITION is returned for two reasons. First, so the caller can reject a
    "triple" in which all three classes walked back onto one token: a section
    map reading "the seven duties · prevented / detected / survives defined"
    scored 7/7/7, and a footnote reading "its three columns as prevented ·
    recoverable · irreversible" scored 3/3/3 - in both, the class words are
    vocabulary, not counts. Second, so the caller can require canonical A-B-C
    order; see scan_text.
    """
    for km in re.finditer(r"\b(?:" + keywords + r")\b", line, re.I):
        cm = COLON_VALUE.match(line, km.end())
        if cm:
            return as_int(cm.group(1)), cm.start(1)
        start = max(0, km.start() - LOOKBACK)
        ms = list(NUM_RE.finditer(line[start:km.start()]))
        if ms:
            return as_int(ms[-1].group(1)), start + ms[-1].start()
    return None
EVIDENCED_KW = r"evidenced"
CANDIDATE_KW = r"candidates?"
RE_SLASH = re.compile(r"\b(\d{2,3})\s*[/·]\s*(\d{1,3})\s*[/·]\s*(\d{1,3})\s*[/·]\s*(\d{1,3})\b")
RE_DOTLIST = re.compile(r"\b(\d{1,3})·(\d{1,3})·(\d{1,3})\b")
RE_ROWS = re.compile(r"\b(\d{2,3})\b[^.;\n]{0,25}?\b(?:named failure modes|failure modes|rows)\b", re.I)


def derive_truth():
    """Per-register and total (rows, A, B, C), from check-registers.py only."""
    tool = HERE / "check-registers.py"
    if not tool.exists():
        sys.exit(f"FATAL: truth source missing: {tool}")
    out = subprocess.run([sys.executable, str(tool)], capture_output=True, text=True,
                         cwd=str(PROJECT)).stdout
    regs = {}
    for line in out.splitlines():
        m = re.match(r"\[.{1,4}\]\s+(\S+-layer)\s+(\{.*\})\s*$", line.strip())
        if not m:
            continue
        name, d = m.group(1), json.loads(m.group(2))
        o = d.get("outcome", {})
        if name == "truth-layer":
            # truth uses Class A/B/C headings, not the outcome column
            a = int(re.search(r"Class A .*?\((\d+) claims?", (PROJECT / "registers" / "truth-layer.md").read_text()).group(1))
            b = int(re.search(r"Class B .*?\((\d+) claims?", (PROJECT / "registers" / "truth-layer.md").read_text()).group(1))
            c = int(re.search(r"Class C .*?\((\d+) claims?", (PROJECT / "registers" / "truth-layer.md").read_text()).group(1))
        else:
            a = o.get("prevented", 0)
            b = o.get("detected", o.get("recoverable", 0))
            c = o.get("survives", o.get("irreversible", 0))
        ev = d.get("evidence", {})
        regs[name] = {"rows": d["rows"], "abc": (a, b, c),
                      "ev": (ev.get("evidenced", 0), ev.get("candidate", 0))}
    if len(regs) < 6:
        sys.exit(f"FATAL: parsed {len(regs)} registers from check-registers.py, expected 6. "
                 "Its output format changed - fix this parser rather than trusting the result.")
    for name, r in regs.items():
        if sum(r["abc"]) != r["rows"]:
            sys.exit(f"FATAL: {name} A+B+C={sum(r['abc'])} but rows={r['rows']}. "
                     "The registers do not reconcile; fix them before checking content.")
        if sum(r["ev"]) != r["rows"]:
            sys.exit(f"FATAL: {name} evidenced+candidate={sum(r['ev'])} but rows={r['rows']}. "
                     "The tier split does not reconcile; fix the register before checking content.")
    total_rows = sum(r["rows"] for r in regs.values())
    total_abc = tuple(sum(r["abc"][i] for r in regs.values()) for i in range(3))
    return regs, total_rows, total_abc


def scan_text(text, regs, total_rows, total_abc):
    """Return (failures, advisories, skipped_blockquote_lines)."""
    fails, advis, skipped = [], [], 0
    valid_triples = {r["abc"] for r in regs.values()} | {total_abc}
    valid_rows = {r["rows"] for r in regs.values()} | {total_rows}
    total_ev = tuple(sum(r["ev"][i] for r in regs.values()) for i in range(2))
    valid_ev_pairs = {r["ev"] for r in regs.values()} | {total_ev}

    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if line.startswith(">"):
            skipped += 1
            continue
        if not line or line.startswith("|") and "---" in line:
            continue

        for m in RE_SLASH.finditer(line):
            got = tuple(int(g) for g in m.groups()[1:])
            rows = int(m.group(1))
            if rows == total_rows and got != total_abc:
                fails.append((n, "SLASHFORM", m.group(0),
                              f"{total_rows} / {total_abc[0]} / {total_abc[1]} / {total_abc[2]}"))

        dots = [tuple(int(g) for g in m.groups()) for m in RE_DOTLIST.finditer(line)]
        if len(dots) >= 3:
            bad = [d for d in dots if d not in valid_triples]
            if bad:
                fails.append((n, "DOTLIST", ", ".join("·".join(map(str, d)) for d in bad),
                              "; ".join(f"{k.split('-')[0]} {'·'.join(map(str,v['abc']))}"
                                        for k, v in regs.items())))

        p, d, s = near(line, PREVENTED), near(line, DETECTED), near(line, SURVIVES)
        # Three distinct number tokens, IN CANONICAL A-B-C ORDER, or it is not
        # a triple. Distinctness alone is not enough on a long line: a bullet
        # reading "of 25 ways a change escapes you, 9 are irreversible ... of
        # the 11 S4 rows, 4 are prevented outright and 5 recoverable" has three
        # distinct tokens drawn from three unrelated clauses, and scored 4/5/9.
        # A real triple is a coordinated list and is always written A then B
        # then C - every fixture in KNOWN_BAD is, and so is every count on
        # every live page. See "WHAT IS NOT COVERED" for what this gives up.
        if p is not None and d is not None and s is not None \
                and len({p[1], d[1], s[1]}) == 3 \
                and p[1] < d[1] < s[1]:
            got = (p[0], d[0], s[0])
            if got not in valid_triples:
                fails.append((n, "TRIPLE", " / ".join(map(str, got)),
                              " / ".join(map(str, total_abc)) + " (cross-register total)"))

        # EVIDPAIR (D-107): "66 evidenced ... 62 candidate(s)" on one line, in
        # that order, each keyword anchored to its own number token. A pair
        # matching no register's split and not the total is a failure. A line
        # with only one of the two numbers is not a pair and is not checked -
        # the subset-claim gap, declared in the header.
        e, c = near(line, EVIDENCED_KW), near(line, CANDIDATE_KW)
        if e is not None and c is not None and e[1] != c[1] and e[1] < c[1]:
            got = (e[0], c[0])
            if got not in valid_ev_pairs:
                fails.append((n, "EVIDPAIR", f"{got[0]} evidenced / {got[1]} candidate",
                              f"{total_ev[0]} evidenced / {total_ev[1]} candidate (cross-register total); "
                              + "; ".join(f"{k.split('-')[0]} {v['ev'][0]}·{v['ev'][1]}"
                                          for k, v in regs.items())))

        # ROWCOUNT deliberately not implemented - see "WHAT IS NOT COVERED".

    return fails, advis, skipped


# ---------------------------------------------------------------- self-test

KNOWN_BAD = [
    ("hub one-number", "Across the six populated registers: 133 named failure modes. 26 can be prevented outright. 74 can be detected every time by a mechanism. 33 survive everything and land on a person."),
    ("essay 0.1 inline", "Of the 133: 25 prevented, 75 detected, 33 survive."),
    ("essay 0.1 close", "The registers are a map of that peak: 133 rows, 25 refusable, 75 catchable, 33 on your desk."),
    # Refreshed 2026-08-21: the SLASHFORM check only reads a slashform whose
    # first number is the current row total, so this fixture must carry the
    # live total (128 since D-106) with a wrong split, or it tests nothing.
    ("essay 0.1 footnote", "Register counts used: 128 / 25 / 75 / 33 (sum verified against all six register files)."),
    ("essay 0.2 prose", "133 named failure modes - 26 can be refused outright, 74 can be caught every time by a mechanism, and 33 survive everything and land on a person."),
    ("essay 0.2 dotlist", "states 5·12·6 / 2·15·6 / 3·14·6 / 7·11·7 / 6·15·3 / 3·7·5, totals 133/26/74/33"),
    ("stale truth spoke", "3 claims can be prevented outright by withholding something, 7 can be converted into a committed artefact a machine checks every time, and 5 nothing converts - they stay on your desk."),
    # Added 2026-08-17. Every fixture below fails in words and passed before the
    # NUMWORDS change - these are the exact sentences the gate could not see.
    ("house style, stale truth split", "So the score for this register is three prevented, seven detected, five surviving."),
    ("house style, wrong detected", "So the score for this register is zero prevented, six detected, six surviving."),
    ("house style, wrong survives", "So the score for this register is zero prevented, nine detected, nine surviving."),
    ("mixed words and numerals", "The score is zero prevented, 7 detected, six surviving."),
    ("surviving, the verb form that did not match", "Of the 133: 26 prevented, 74 detected, 33 surviving."),
    # Added 2026-08-17 with COLON_VALUE. This is the form that used to be read
    # off by one; it must now be read correctly, which means a WRONG value in
    # it must fail. Recovery is 5/11/9, so `prevented: 6` is a real error.
    ("colon form, wrong prevented", "Verified against frontmatter (`rows: 25`, `prevented: 6`, `recoverable: 11`, `irreversible: 9`)."),
    ("colon form, wrong survives", "Frontmatter reads `prevented: 5`, `recoverable: 11`, `irreversible: 8`."),
    # Added 2026-08-21 with D-107's EVIDPAIR check. Wrong totals and wrong
    # per-register splits, in digits and in words, must all fail.
    ("evidenced pair, stale total", "Across the six registers: 70 evidenced · 58 candidates."),
    ("evidenced pair, wrong register split", "The instruction register splits 9 evidenced · 13 candidates."),
    ("evidenced pair in words", "So this register carries eight evidenced claims and six candidates."),
]

KNOWN_GOOD = [
    # "corrected" fixtures refreshed 2026-08-21 to the post-D-106 canon
    # (128 rows: 12/73/43; recovery 24: 5/10/9). The previous values were the
    # post-RL-1F canon and had gone stale when D-106 retired six rows - the
    # self-test caught its own drift, which is what it is for.
    ("corrected total", "Across the six registers: 128 named failure modes. 12 can be prevented outright. 73 can be detected every time by a mechanism. 43 survive everything and land on a person."),
    ("corrected slash", "Register counts used: 128 / 12 / 73 / 43."),
    ("corrected dotlist", "states 2·12·8 / 0·14·8 / 2·14·7 / 5·10·9 / 3·14·5 / 0·9·6, totals 128/12/73/43"),
    ("truth register own split", "0 claims retired by withholding, 9 by executing-then-diffing, 6 that nothing converts and stay on your desk."),
    ("truth spoke corrected", "9 can be converted into a committed artefact a machine checks on every commit, 6 come down to a judgement no tool makes, and none can be prevented outright."),
    ("recovery own vocabulary", "5 prevented, 10 recoverable, 9 irreversible."),
    ("prose ratio, not a number", "Roughly a third of them cannot be fixed with any install because they need judgement."),
    ("banner quoting known-bad", "> This draft says 133 / 25 / 75 / 33 at lines 61, 149 and 165."),
    ("bare row count", "The list is at 133 now."),
    # Added 2026-08-17 alongside NUMWORDS. The first three are the live pages;
    # the rest are the false positives number words make possible, and each one
    # fired during development before the lookback and the "none" exclusion were
    # settled. Keep them - they are the reason this change is safe.
    ("truth spoke headline, house style, correct", "So the score for this register is zero prevented, nine detected, six surviving."),
    # DECLARED GAP, not a pass: two-digit number words are not parsed at all,
    # so this WRONG triple (registers say 12/77/44) goes uncaught. It is here to
    # keep the gap visible. Before the hyphen guard it was worse than uncaught -
    # it read as 12/7/4 and failed for the wrong reason.
    ("declared gap: two-digit words unparsed", "Across the six registers: twelve prevented, seventy-six detected, forty-three survive."),
    ("'none' is a pronoun, not a zero", "Nine can be converted into a committed artefact, six come down to a judgement no tool makes, and none can be prevented outright."),
    ("'one' inside 'none' must not match", "None of these is prevented, none is detected, and none survives."),
    ("'one' as a pronoun near a class word", "Every one of those is an assertion, and not one of them is prevented, detected, or survives by construction."),
    ("hyphenated compound must not match its tail", "The split is seventy-seven detected and forty-four survive, against zero prevented."),
    # Both lifted verbatim from live pages. Both fired as 7/7/7 and 3/3/3 when
    # number words were first added, because the class names are vocabulary here
    # and one nearby word-number served all three. They are the reason near()
    # returns a position.
    ("class names as vocabulary, section map", "| 2 | **The contract** | Names the seven duties and the three grades. | **Evidence** | The seven duties - prevented / detected / survives defined |"),
    ("class names as vocabulary, footnote", "Recovery reads its three columns as prevented - recoverable - irreversible, the register grades whether you can get back."),
    ("class list line, single class only", "3. **Class C - survives, judgement only (six claims).** Nothing converts these into machinery."),
    # Both lifted verbatim from the strategy doc's recovery-spoke entry, and
    # both were live FAILURES until 2026-08-17. Each is correct against
    # recovery-layer.md (rows 24 since D-106: 5 prevented, 10 recoverable,
    # 9 irreversible; refreshed 2026-08-21). They
    # are the reason COLON_VALUE and the A-B-C order requirement exist.
    ("colon form quoting frontmatter, correct", "Counts, verified 2026-08-21 against `registers/recovery-layer.md` frontmatter (`rows: 24`, `prevented: 5`, `recoverable: 10`, `irreversible: 9`) and independently re-derived from the six stage headings: **24 failures - 5 prevented, 10 recoverable, 9 irreversible.**"),
    ("class words drawn from three unrelated clauses", "Defining finding: **of 26 ways a change escapes you, 10 are irreversible - and the irreversible ones cluster at the end of a change's life.** Second cross-cut: severity and outcome do not track each other - of the 12 S4 rows, 4 are prevented outright and 5 recoverable, so the residue is the undecided half, not the expensive half."),
    # Added 2026-08-21 with the EVIDPAIR check. The correct total and a correct
    # per-register split must pass; the last three are the false-positive
    # shapes the check must stay silent on - vocabulary with no numbers, both
    # keywords walking back onto one number token, and a subset claim carrying
    # only one of the two numbers (a declared gap, kept visible here).
    ("evidenced pair, correct total", "Across the six registers: 66 evidenced · 62 candidates."),
    ("evidenced pair, correct register split", "22 rows: 8 evidenced, 14 candidates."),
    ("tier vocabulary, no numbers", "Every row is either evidenced or a candidate, and the label is on the row."),
    ("both tier keywords on one number", "The 128 rows split into evidenced and candidate tiers."),
    ("declared gap: subset claim, single number", "23 of the 66 evidenced rows were confirmed after enumeration."),
]


def self_test(regs, total_rows, total_abc):
    ok = True
    print("known-bad fixtures - each MUST fail:")
    for name, text in KNOWN_BAD:
        f, _, _ = scan_text(text, regs, total_rows, total_abc)
        good = bool(f)
        ok &= good
        print(f"  [{'PASS' if good else 'MISS'}] {name}" + ("" if good else "  <-- not caught"))
    print("known-good fixtures - each MUST pass clean:")
    for name, text in KNOWN_GOOD:
        f, _, _ = scan_text(text, regs, total_rows, total_abc)
        good = not f
        ok &= good
        print(f"  [{'PASS' if good else 'FIRE'}] {name}" + ("" if good else f"  <-- false positive: {f}"))
    return ok


def main():
    args = sys.argv[1:]
    regs, total_rows, total_abc = derive_truth()

    print("Derived from check-registers.py:")
    for k, v in regs.items():
        print(f"  {k:26} rows={v['rows']:3}  A={v['abc'][0]:2} B={v['abc'][1]:2} C={v['abc'][2]:2}")
    print(f"  {'TOTAL':26} rows={total_rows:3}  A={total_abc[0]:2} B={total_abc[1]:2} C={total_abc[2]:2}\n")

    if "--self-test" in args:
        ok = self_test(regs, total_rows, total_abc)
        print("\nself-test " + ("PASSED" if ok else "FAILED"))
        return 0 if ok else 1

    # .resolve() and the _disp fallback below are both load-bearing. Without them
    # a relative --root (e.g. "--root public-repo") crashed with a ValueError from
    # relative_to() at the moment it tried to PRINT a failure - so the run passed
    # while nothing was wrong and died only once something was. A gate that works
    # until it has something to report is worse than no gate. Found 2026-08-19 by
    # running the newly wired public-repo step against a deliberately stale count,
    # which is the only reason it was found at all.
    root = (Path(args[args.index("--root") + 1]).resolve() if "--root" in args
            else PROJECT / "content")
    files = sorted(root.rglob("*.md"))
    # The registers' METHODOLOGY.md states counts as its whole job, and
    # OPERATIONS.md may state them in passing, so the default run scans both
    # alongside content/ (METHODOLOGY added 2026-08-21 with D-107;
    # OPERATIONS 2026-08-22 with D-110). Appended BEFORE the empty check below —
    # the public False Floors repo carries registers/METHODOLOGY.md and
    # registers/OPERATIONS.md but never content/ (public-repo/README.md's copy
    # boundary), so an empty content/ must not be FATAL when those two governed
    # files are the real, in-scope thing to scan there.
    if "--root" not in args:
        for name in ("METHODOLOGY.md", "OPERATIONS.md"):
            governed = PROJECT / "registers" / name
            if governed.exists():
                files.append(governed)
    if not files:
        sys.exit(f"FATAL: no markdown found under {root}")

    def _disp(p):
        try:
            return p.relative_to(PROJECT)
        except ValueError:
            return p

    n_fail = n_advis = n_skip = 0
    superseded = []
    for f in files:
        text = f.read_text()
        if "SUPERSEDED" in "\n".join(text.splitlines()[:40]):
            superseded.append(_disp(f))
            continue
        fails, advis, skipped = scan_text(text, regs, total_rows, total_abc)
        n_skip += skipped
        if not fails and not advis:
            continue
        print(f"{_disp(f)}")
        for ln, kind, got, want in fails:
            print(f"  [FAIL] :{ln}  {kind}  states: {got}")
            print(f"         registers say: {want}")
            n_fail += 1
        for ln, kind, got, want in advis:
            print(f"  [ ? ]  :{ln}  {kind}  {got!r} - {want}")
            n_advis += 1
        print()

    if superseded:
        print("Skipped as SUPERSEDED (their wrong numbers are kept as record, by decision):")
        for s in superseded:
            print(f"  - {s}")
        print()
    print(f"{len(files)} files found, {len(files) - len(superseded)} scanned - {n_fail} failures, "
          f"{n_advis} advisories, {n_skip} blockquote lines skipped (declared gap).")
    if "--strict" in args:
        return 1 if (n_fail or n_advis) else 0
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""check-assessment.py — the assessment record is internally honest, and agrees
with the catalogue it was scored against.

Written for D-263, 2026-09-07. Every check in here used to live in
check-registers.py and was moved rather than deleted: each one reads environment
state, and environment state left canon. They were never wrong, they were pointed
at the wrong document.

WHAT MOVED, AND WHAT EACH ONE IS FOR

  * Gap vocabulary                 - the four values, unchanged.
  * Gap derivation (C-06 lineage)  - a `survives` row cannot read closed; a
                                     mechanism that is designed or absent cannot
                                     close a failure with no substitute recorded;
                                     a built mechanism that prevents or detects
                                     must read closed or partially closed.
  * The install gate (C-02)        - gap `closed` on a row whose own next action
                                     is a `ONCE —` install is a lie: the control
                                     is not switched on. Hard where the layer has
                                     no install state to read (provenance),
                                     advisory in the four that do, for exactly
                                     the reason C-02 records - `built` says the
                                     mechanism exists, not that it is in force.
  * Trigger vocabulary (C-07)      - kinds parse, per-event values come from the
                                     controlled list, and one value is not spelled
                                     two ways, which would double it in any
                                     checklist grouped by trigger.

AND ONE CHECK THAT IS NEW, because the split created the failure it catches:

  * Coverage - every catalogue row appears in the assessment exactly once, and
    the assessment scores no row the catalogue does not have. Before D-263 this
    was true by construction, because the two facts were in the same table cell.
    They are now in different files that change on different days, and nothing
    else compares them. A row added to the catalogue and never scored is the
    quiet failure here: it reads as "no gap" rather than "never looked at".

Coverage gaps, declared:
  * It does not check that a gap value is TRUE of the environment. Nothing can.
    `verified:` and the assessment's date are the receipt, and they are human
    claims. This checks internal consistency and catalogue agreement, no more.
  * Provenance rows carry no install state, so the derivation rules that read one
    are skipped there and the install gate is hard instead - the same declared
    exception the registers README has carried since 2026-08-10.
  * An assessment with no `installState` at all is REPORTED, not failed. A future
    assessment of somebody else's environment may legitimately score gaps without
    recording our built/designed vocabulary.
"""
import json, re, sys, pathlib, importlib.util, collections

TOOLS = pathlib.Path(__file__).resolve().parent
PROJECT = TOOLS.parents[1]
ASSESSMENTS = PROJECT / "assessments"

GAP = {'closed', 'closed by substitute', 'partially closed', 'open'}
INSTALL = {'built', 'designed', 'none'}
CADENCE = {'WEEKLY', 'MONTHLY', 'QUARTERLY', 'ANNUALLY'}
EVERY_VALUES = {
    'archive', 'brief', 'claim', 'commit', 'decision', 'draft', 'fan-out',
    'finding', 'handoff', 'import', 'incident', 'late bug', 'merge',
    'migration', 'new client', 'new default', 'new fact', 'new note',
    'prompt', 'record', 'release', 'rename', 'retry', 'review', 'rewrite',
    'rule change', 'run', 'session', 'task', 'template change',
}
LAYERS = ['instruction-layer', 'context-layer', 'authority-access-layer',
          'recovery-layer', 'provenance-layer', 'truth-layer']
NO_INSTALL_STATE = {'provenance-layer', 'truth-layer'}


def load_checker():
    spec = importlib.util.spec_from_file_location(
        "check_registers", TOOLS / "check-registers.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def trigger_of(cell):
    """(kind, value) from a next-action cell. None if it does not parse, which is
    itself a finding: a free-text trigger cannot support a checklist grouped by it."""
    head = cell.split('—')[0].strip()
    if not head:
        return None
    if head == 'ONCE':
        return ('once', 'install')
    if head.startswith('DONE'):
        return ('done', head.split('·', 1)[-1].strip() if '·' in head else '')
    if head in CADENCE:
        return ('cadence', head.lower())
    m = re.match(r'^(?:AT\s+)?EVERY\s+(.+)$', head)
    if m:
        return ('every', m.group(1).strip().lower())
    return None


# ------------------------------------------------------------------ pure logic

def audit(doc, catalogue):
    """doc: the assessment. catalogue: {row_id: {'layer':…, 'outcome':…}}.

    Returns (findings, review, stats). `review` is for calls only a human can
    make, kept separate so it never fails a run.
    """
    fails, review = [], []
    gaps = doc.get('rows', {})
    install = doc.get('installState', {})
    actions = doc.get('nextAction', {})

    # coverage, both directions
    missing = sorted(set(catalogue) - set(gaps))
    extra = sorted(set(gaps) - set(catalogue))
    for rid in missing:
        fails.append(f'{rid} is in the catalogue and unscored in this assessment')
    for rid in extra:
        fails.append(f'{rid} is scored here and is not a catalogue row — retired, '
                     f'or a typo; a retired ID is never reused, so it cannot be either')

    counts = collections.Counter()
    for rid, gap in sorted(gaps.items()):
        if gap not in GAP:
            fails.append(f"{rid}: gap '{gap}' not in vocabulary "
                         f'({", ".join(sorted(GAP))})')
            continue
        counts[gap] += 1
        row = catalogue.get(rid)
        if row is None:
            continue
        outcome, layer = row['outcome'], row['layer']
        state = install.get(rid)
        if state is not None and state not in INSTALL:
            fails.append(f"{rid}: install state '{state}' not in vocabulary "
                         f'({", ".join(sorted(INSTALL))})')
            state = None

        # derivation — the provenance exception is declared in the registers README
        if layer != 'provenance-layer':
            if outcome in ('survives', 'irreversible') and gap != 'open':
                fails.append(f"{rid}: {outcome} but gap '{gap}' (README: always open)")
            if state in ('designed', 'none') and gap == 'closed':
                fails.append(f"{rid}: mechanism {state} but gap 'closed' with no "
                             f'substitute recorded')
            if state == 'built' and outcome in ('prevented', 'detected') \
                    and gap not in ('closed', 'partially closed'):
                fails.append(f"{rid}: built + {outcome} but gap '{gap}'")

    # trigger vocabulary and the install gate
    kinds, heads = collections.Counter(), {}
    for rid, cell in sorted(actions.items()):
        parsed = trigger_of(cell)
        if parsed is None:
            fails.append(f"{rid}: trigger '{cell.split('—')[0].strip()}' parses to no "
                         f'kind — expected ONCE, DONE, a cadence, or EVERY <event>')
            continue
        kind, value = parsed
        kinds[kind] += 1
        heads.setdefault(value, set()).add(cell.split('—')[0].strip())
        if kind == 'every' and value not in EVERY_VALUES:
            fails.append(f"{rid}: trigger value '{value}' is not in the declared "
                         f'per-event vocabulary')
        if kind == 'once' and gaps.get(rid) == 'closed':
            msg = (f"{rid}: gap 'closed' but the next action is a ONCE install — "
                   f'the control is not switched on')
            layer = catalogue.get(rid, {}).get('layer')
            if layer in NO_INSTALL_STATE or layer is None:
                fails.append(msg)
            else:
                review.append(msg + f" (next action: '{cell}')")
    for value, spellings in sorted(heads.items()):
        if len(spellings) > 1:
            fails.append(f"trigger '{value}' is written {len(spellings)} ways "
                         f'({", ".join(sorted(spellings))}) — a checklist grouped '
                         f'by trigger would double it')

    stats = {'scored': len(gaps), 'catalogue': len(catalogue),
             'gap': dict(sorted(counts.items())), 'trigger': dict(sorted(kinds.items())),
             'install_state': 'present' if install else 'absent (reported, not failed)'}
    return fails, review, stats


SPOKE_REGISTER = {
    'spoke-instruction': 'IL', 'spoke-context': 'CL', 'spoke-authority': 'AL',
    'spoke-recovery': 'RL', 'spoke-provenance': 'PL', 'spoke-truth': 'TL',
}
# Deliberately loose on the connective tissue and strict on the two numbers.
# The nine live sentences say it nine slightly different ways - "12 of the 21",
# "twelve of the register's 21", "16 of its 17", with and without "were" - and a
# pattern that matched only the tidy ones would report coverage it does not have.
#
# THE COUNT IS CAPTURED AS \S+, NOT AS A NUMBER, AND THAT IS THE WHOLE POINT.
# The first version listed the number words it knew. Tested 2026-09-07 by setting
# a spoke to "three of the register's 99 tooled rows were not installed": `three`
# was not in the list, so the sentence stopped matching, the claim count dropped
# from 9 to 8, and the run stayed GREEN on a wrong published number. A pattern
# that silently narrows when the text changes is worse than no pattern, because
# the count it reports reads as coverage. An unparseable count now FAILS.
CLAIM_RE = re.compile(
    r"\b(\S+)\s+of\s+(?:the|its)(?:\s+register's)?\s+(\d+)\s+"
    r"tooled rows\b[^.]{0,40}?not installed", re.I)
WORDS = {w: i for i, w in enumerate(
    'zero one two three four five six seven eight nine ten eleven twelve '
    'thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty '
    'twenty-one twenty-two twenty-three twenty-four twenty-five twenty-six '
    'twenty-seven twenty-eight twenty-nine thirty'.split())}


def spoke_install_claims(doc, live=None):
    """Every "N of the M tooled rows were not installed" claim on a live spoke,
    checked against the assessment that the sentence now cites.

    THIS IS THE CHECK 2C BOUGHT. Measured 2026-09-07, before the rewrite: the
    spoke pages carried three such numbers and NOTHING verified any of them.
    A spoke was set to read "Three of the register's 99 tooled rows are not
    built" and check-content-counts, check-spoke-row-counts, check-registers and
    check-spoke-evidence all passed. The claim was undated and derived from a
    field that has now left canon, so after D-263 it could never have been
    checked against canon at all - only against an assessment.

    tooled  = rows naming a mechanism (install state built or designed)
    not installed = install state `designed`
    """
    live = live or (PROJECT / 'content' / 'hub-and-spokes' / 'live')
    install = doc.get('installState', {})
    fails, seen = [], 0
    if not install or not live.is_dir():
        return fails, seen
    for path in sorted(live.glob('spoke-*.md')):
        prefix = SPOKE_REGISTER.get(path.stem)
        if prefix is None:
            continue
        states = [v for k, v in install.items() if k.split('-')[0] == prefix]
        tooled = sum(1 for v in states if v in ('built', 'designed'))
        not_installed = sum(1 for v in states if v == 'designed')
        text = path.read_text(encoding='utf-8')
        for m in CLAIM_RE.finditer(text):
            seen += 1
            raw = m.group(1).lower().strip('*_`"“”')
            n = WORDS.get(raw)
            if n is None:
                n = int(raw) if raw.isdigit() else None
            if n is None:
                fails.append(f'{path.name}: install claim "{m.group(0)[:70]}" has a '
                             f'count this gate cannot parse ({m.group(1)!r}) — write it '
                             f'as a numeral or a number word, so it can be checked')
                continue
            mm = int(m.group(2))
            if (n, mm) != (not_installed, tooled):
                fails.append(
                    f'{path.name}: claims "{m.group(1)} of the {mm} tooled rows were '
                    f'not installed"; the assessment gives {not_installed} of {tooled}')
    return fails, seen


def catalogue_from_canon():
    checker = load_checker()
    out = {}
    for layer in LAYERS:
        _fm, sections, _txt = checker.parse(layer)
        for section in sections:
            for row in section['rows']:
                out[row['ID']] = {
                    'layer': layer,
                    'outcome': row.get('Outcome', '').split(' ', 1)[-1].strip().lower(),
                }
    return out


# ------------------------------------------------------------------- self-test

def self_test():
    cat = {
        'IL-1A': {'layer': 'instruction-layer', 'outcome': 'detected'},
        'IL-1B': {'layer': 'instruction-layer', 'outcome': 'survives'},
        'PL-9A': {'layer': 'provenance-layer', 'outcome': 'prevented'},
        'RL-9A': {'layer': 'recovery-layer', 'outcome': 'recoverable'},
    }
    good = {'rows': {'IL-1A': 'closed', 'IL-1B': 'open', 'PL-9A': 'open',
                     'RL-9A': 'closed'},
            'installState': {'IL-1A': 'built', 'IL-1B': 'designed', 'RL-9A': 'built'},
            'nextAction': {'IL-1A': 'EVERY MERGE — Check it', 'PL-9A': 'ONCE — Install it'}}

    def run(mutate):
        d = json.loads(json.dumps(good))
        mutate(d)
        return audit(d, cat)[0]

    cases = [
        ('clean input passes', lambda d: None, False),
        ('gap value outside the vocabulary',
         lambda d: d['rows'].__setitem__('IL-1A', 'mostly fine'), True),
        ('survives row reading closed',
         lambda d: d['rows'].__setitem__('IL-1B', 'closed'), True),
        ('designed mechanism claiming closed',
         lambda d: (d['installState'].__setitem__('IL-1A', 'designed'),
                    d['rows'].__setitem__('IL-1A', 'closed')), True),
        ('built + detected not reading closed',
         lambda d: d['rows'].__setitem__('IL-1A', 'open'), True),
        ('a catalogue row left unscored',
         lambda d: d['rows'].pop('RL-9A'), True),
        ('a scored row the catalogue does not have',
         lambda d: d['rows'].__setitem__('ZZ-9Z', 'open'), True),
        ('install gate: closed on a ONCE install, hard where there is no install state',
         lambda d: d['rows'].__setitem__('PL-9A', 'closed'), True),
        ('trigger that parses to no kind',
         lambda d: d['nextAction'].__setitem__('IL-1A', 'SOMETIMES — Check it'), True),
        ('per-event value outside the vocabulary',
         lambda d: d['nextAction'].__setitem__('IL-1A', 'EVERY BLUE MOON — Check it'), True),
        ('one ritual spelled two ways',
         lambda d: d['nextAction'].__setitem__('RL-9A', 'AT EVERY MERGE — Check it'), True),
        ('install state outside the vocabulary',
         lambda d: d['installState'].__setitem__('IL-1A', 'switched on'), True),
    ]
    bad = []
    for name, mutate, want_fail in cases:
        got = run(mutate)
        if bool(got) != want_fail:
            bad.append(f'{name}: expected {"a failure" if want_fail else "none"}, '
                       f'got {got or "none"}')
    # the advisory path must NOT fail a run
    adv = json.loads(json.dumps(good))
    adv['rows']['RL-9A'] = 'closed'
    adv['nextAction']['RL-9A'] = 'ONCE — Turn it on'
    f, r, _ = audit(adv, cat)
    if f:
        bad.append(f'install gate should be advisory where install state exists, got {f}')
    if not r:
        bad.append('install gate advisory case produced no review line')

    # The spoke scan, on a fixture directory. It reads the filesystem, so it is
    # not part of audit() and gets its own cases here.
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        live = pathlib.Path(d)
        doc = {'installState': {'IL-1A': 'built', 'IL-1B': 'designed',
                                'IL-1C': 'designed', 'IL-1D': 'none'}}
        spoke = live / 'spoke-instruction.md'
        for label, body, want_fail in [
            ('a correct claim passes',
             'Assessment #1 found 2 of the 3 tooled rows were not installed there.', False),
            ('a wrong not-installed count fails',
             'Assessment #1 found 1 of the 3 tooled rows were not installed there.', True),
            ('a wrong tooled total fails',
             'Assessment #1 found 2 of the 9 tooled rows were not installed there.', True),
            ('a number word this gate cannot parse fails, rather than going unmatched',
             'Assessment #1 found umpteen of the 3 tooled rows were not installed there.', True),
            ('a word-number claim passes',
             'Assessment #1 found two of the 3 tooled rows were not installed there.', False),
            ('no claim on the page is not a failure', 'Nothing numeric here.', False),
        ]:
            spoke.write_text(body, encoding='utf-8')
            got, _seen = spoke_install_claims(doc, live)
            if bool(got) != want_fail:
                bad.append(f'spoke scan / {label}: expected '
                           f'{"a failure" if want_fail else "none"}, got {got or "none"}')

    if bad:
        print(f'[FAIL] (assessment self-test) {{"failed": {len(bad)}}}')
        for b in bad:
            print(f'         {b}')
        return 1
    print(f'[ ok ] (assessment self-test) {{"cases": {len(cases) + 7}}}')
    return 0


def main():
    if '--self-test' in sys.argv:
        return self_test()
    files = sorted(ASSESSMENTS.glob('assessment-*.json'))
    if not files:
        print('[ ok ] (assessment) {"assessments": 0, "note": "none on disk"}')
        return 0
    cat = catalogue_from_canon()
    rc = 0
    for f in files:
        doc = json.loads(f.read_text(encoding='utf-8'))
        fails, review, stats = audit(doc, cat)
        spoke_fails, spoke_seen = spoke_install_claims(doc)
        fails.extend(spoke_fails)
        stats['spoke_install_claims'] = spoke_seen
        label = f'{doc.get("assessmentId", f.stem)} · {doc.get("environment", "?")}'
        if fails:
            rc = 1
            print(f'[FAIL] (assessment {label}) {{"failed": {len(fails)}}}')
            for x in fails:
                print(f'         {x}')
        else:
            print(f'[ ok ] (assessment {label}) {json.dumps(stats)}')
        for x in review:
            print(f'         ? {x}')
    if rc == 0:
        print('         ? = needs a human call, not a defect the tool can settle.')
    return rc


if __name__ == '__main__':
    sys.exit(main())

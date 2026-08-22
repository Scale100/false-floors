#!/usr/bin/env python3
"""check-registers — the register-is-canon rule, made executable.

Reads every register in the parent folder and asserts that the row data, the
stage sub-counts, the distribution tables, the frontmatter and the prose
summaries all agree. Header-driven: it reads each table's own header row, so a
layer may carry extra columns (authority) or a different spine entirely
(provenance's three control positions, truth's claims) without special-casing.

Exit 0 clean, exit 1 with a finding list. Read-only; it never writes.

    python3 tools/check-registers.py [--json]
    python3 tools/check-registers.py --propose-row "<text>" [--miss-reasons FILE]
    python3 tools/check-registers.py --self-test | --self-test-propose

Rules enforced, and where they are defined:
  - README "Built state"      a row naming no mechanism takes built state `none`
  - README "Built state"      headline count is designed over TOOLED rows
  - README "Residual"         derivation rules, incl. the provenance exception
  - README "Shared vocabulary" enum values for outcome, tool tier, built, residual
  - README "Residual"         install gate: residual `closed` is a lie on a row whose
                              own next action is a `ONCE —` install                (C-02)
  - truth-layer reading note  Status enum, and `in force` <-> closed derivation     (C-04)
  - README "Trigger"          every trigger parses to a kind + a declared value;
                              one value never appears under two spellings           (C-07/C-24)
  - canon/view boundary       generated JSON and its inline fallback agree, name a
                              committed source, and are not older than canon        (C-25)
  - fail-fix stage 1          a proposed row is ranked against all seven registers
                              and the Corrections Register, and the five nearest
                              rows each owe a written miss reason before an ID is
                              minted — `--propose-row`                              (C-31)

Added 2026-08-10 to close C-16. Before that date this checker passed all six
registers while C-02, C-04 and C-07 stood — it validated arithmetic but no
schema integrity, so the framework's own canon-vs-view control could not see
three High defects. Extended the same day for C-25 after the generated V1 view
served stale canon without failing. Run `--self-test` to prove both classes of
check can still fail.
"""
import re, sys, json, math, pathlib, subprocess

REG = pathlib.Path(__file__).resolve().parent.parent
PROJECT = REG.parent
VIEW_DIR = PROJECT / 'tools' / 'trust-check-v1'
VIEW_JSON = VIEW_DIR / 'register-data.json'
VIEW_PAGE = VIEW_DIR / 'index.html'
LAYERS = ['instruction-layer', 'context-layer', 'authority-access-layer',
          'recovery-layer', 'provenance-layer', 'truth-layer']

CATCH_ORDER = ['on disk', 'session start', 'prompt', 'pre-tool', 'subagent',
               'post-tool', 'compact', 'stop', 'pre-commit', 'CI', 'review']
BUILT = {'built', 'designed', 'none'}
TIERS = {'automatic', 'maintained', 'process'}
RESIDUAL = {'closed', 'closed by substitute', 'partially closed', 'open'}
OUTCOMES = {'prevented', 'detected', 'survives', 'recoverable', 'irreversible'}
# D-107: every row carries an evidence status, and the headline counts
# evidenced rows only. `evidenced` needs a receipt — a first-party
# ⟪instance-of⟫ mapping, a corpus-coded exact/variant match, or a verifiable
# public field case; `candidate` is enumerated in advance, no receipt yet.
EVIDENCE = {'evidenced', 'candidate'}
CORRECTIONS_PATH = PROJECT / 'Corrections Register.md'
CALIBRATION_PATH = PROJECT / 'research' / '22-register-calibration-pass-2026-08-09.md'
# Verifiable public field cases — D-107's third receipt type. The bar is the
# capability-claim-currency standard: a dated, checkable citation filed in the
# vault. AL-4A's is the only one on file (the Antigravity sandbox escape,
# launch-engagement-plan-2026-08-11.md, "AL-4A in the wild") and AL-4A is
# corpus-evidenced anyway. AL-1B (Replit, July 2025) and RL-5B (GitLab, 2017)
# are widely known but carry NO vault citation yet, so they are deliberately
# absent — file the citation first, then add the ID here.
FIELD_CASES = {'AL-4A'}
ROW_ID_RE = re.compile(r'(?:IL|CL|AL|RL|PL|TL)-\d\d?[A-Z]?')
# provenance derives residual from cell strength, not from a named mechanism
RESIDUAL_EXCEPTION = {'provenance-layer'}
# truth-layer Status: the control's own state, distinct from README `built`.
# Only `in force` closes a row; the other four all read open.
TRUTH_STATUS = {'in force', 'not on', 'not built', 'not provisioned', 'none'}
STATUS_IN_FORCE = {'in force'}
# a layer that carries no Status column, declared rather than silently skipped
NO_STATUS_COLUMN = {'instruction-layer', 'context-layer', 'authority-access-layer',
                    'recovery-layer', 'provenance-layer'}
# trigger kinds: `once` is an install, everything else is a ritual (README)
CADENCE = {'WEEKLY', 'MONTHLY', 'QUARTERLY', 'ANNUALLY'}
# Controlled values for per-event rituals. This is deliberately a vocabulary,
# not an attempt to infer that two arbitrary English phrases mean the same
# thing. Adding a new ritual therefore changes canon and the checker together.
EVERY_VALUES = {
    'archive', 'brief', 'claim', 'commit', 'decision', 'draft', 'fan-out',
    'finding', 'handoff', 'import', 'incident', 'late bug', 'merge',
    'migration', 'new client', 'new default', 'new fact', 'new note',
    'prompt', 'record', 'release', 'rename', 'retry', 'review', 'rewrite',
    'rule change', 'run', 'session', 'task', 'template change',
}
PHASES = {'before it starts': ['on disk', 'session start'],
          'before the change': ['prompt', 'pre-tool', 'subagent'],
          'still in the session': ['post-tool', 'compact', 'stop'],
          'after the session': ['pre-commit', 'CI', 'review']}


def run_git(args, cwd=PROJECT, check=True):
    """Run git without a shell and return the completed process."""
    result = subprocess.run(['git', *args], cwd=cwd, text=True,
                            capture_output=True)
    if check and result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(message or f"git {' '.join(args)} failed")
    return result


def inline_fallback(page_text):
    """Parse the V1 page's embedded register-data fallback."""
    match = re.search(
        r'<script\s+id=["\']register-data-fallback["\']\s+'
        r'type=["\']application/json["\']\s*>(.*?)</script>',
        page_text,
        re.S,
    )
    if not match:
        raise ValueError('index.html is missing the register-data-fallback script block')
    return json.loads(match.group(1))


def register_blobs_at(commit, root, register_path):
    """{filename: blob sha} for registers/*.md at a commit, or None if unreadable.

    Blob shas ARE content hashes, so comparing two of these maps answers "is the
    canon this view read the canon present now" directly, without either commit
    needing to be an ancestor of the other — or, crucially, without the older one
    needing to exist at all.
    """
    r = run_git(['ls-tree', commit, f'{register_path}/'], root, check=False)
    if r.returncode != 0:
        return None
    out = {}
    for line in r.stdout.splitlines():
        meta, _, name = line.partition('\t')
        parts = meta.split()
        if len(parts) < 3 or parts[1] != 'blob' or not name.endswith('.md'):
            continue
        out[name[len(register_path) + 1:]] = parts[2]
    return out


def check_generated_views(json_path=VIEW_JSON, page_path=VIEW_PAGE, repo_root=None):
    """Check V1's two generated copies against each other and committed canon.

    CONTENT FIRST, ANCESTRY ONLY AS A FALLBACK. A view carrying ``canonBlobs``
    is current when that map equals the blob shas of ``registers/*.md`` at canon
    now. Ancestry is not consulted in that case and does not need to hold.

    Why it was changed, on 2026-08-21, after both of the ancestry test's failure
    modes were met in one day:

      * A SQUASH merge replaces the branch commit, so a view that was correct on
        its own pull request lands on main reading "divergent history". The stamp
        can only be made correct AFTER the squash commit exists, which no
        pre-merge check can do — so a genuinely green PR reds main, invisibly.
      * Deleting the branch on merge makes the stamped commit UNRESOLVABLE in a
        fresh clone. ``fetch-depth: 0`` fetches every branch that still exists,
        and that one does not, so CI cannot compare at that commit by any means.
        Verified rather than assumed: b651c510 was reachable from exactly one
        ref, the deleted branch.

    The content test is also a STRONGER claim than the ancestry test, not a
    weaker one. Ancestry proved only that extraction ran at a commit containing
    canon. Equality of blob shas proves the register bytes read are the bytes
    present now, and names the file when they are not.

    COVERAGE GAP, STATED RATHER THAN IMPLIED. Neither test — the old one or this
    one — proves the row DATA in the view was actually derived from that canon.
    A hand-edited view with a correct stamp passes both. What is checked is the
    provenance claim, not the extraction.

    Views generated before this field existed carry no ``canonBlobs`` and are
    still judged by ancestry, so this is additive: no existing artefact starts
    passing that was failing.
    """
    findings = []
    stats = {}
    json_path, page_path = pathlib.Path(json_path), pathlib.Path(page_path)

    try:
        external = json.loads(json_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        return [f'register-data.json is unreadable: {exc}'], stats
    try:
        inline = inline_fallback(page_path.read_text(encoding='utf-8'))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f'inline fallback is unreadable: {exc}'], stats

    copies_match = external == inline
    stats['copies_match'] = copies_match
    stats['external_generated_from'] = external.get('generatedFrom')
    stats['inline_generated_from'] = inline.get('generatedFrom')
    if not copies_match:
        findings.append('inline fallback does not match register-data.json')

    try:
        root = pathlib.Path(repo_root) if repo_root else pathlib.Path(
            run_git(['rev-parse', '--show-toplevel']).stdout.strip())
        register_path = REG.relative_to(root).as_posix()
        pathspec = f':(glob){register_path}/*.md'
        canon = run_git(['log', '-1', '--format=%H', '--', pathspec], root).stdout.strip()
        if not canon:
            findings.append(f'no committed canon found for {register_path}/*.md')
            return findings, stats
        stats['latest_canon'] = canon
    except (RuntimeError, ValueError) as exc:
        findings.append(f'cannot resolve latest canon commit: {exc}')
        return findings, stats

    canon_blobs = register_blobs_at(canon, root, register_path)
    stats['canon_files'] = len(canon_blobs or {})

    for label, payload in [('register-data.json', external), ('inline fallback', inline)]:
        stamped = payload.get('canonBlobs')
        if isinstance(stamped, dict) and canon_blobs is not None:
            if stamped == canon_blobs:
                stats.setdefault('content_matched', []).append(label)
                continue
            moved = sorted(set(stamped) ^ set(canon_blobs)) or sorted(
                f for f in stamped if stamped[f] != canon_blobs.get(f))
            findings.append(
                f'{label} canonBlobs does not match canon {canon[:12]}: '
                f'{moved} changed since it was generated — regenerate the view')
            continue
        source = payload.get('generatedFrom')
        if not isinstance(source, str) or not source.strip():
            findings.append(f'{label} has no generatedFrom commit')
            continue
        resolved = run_git(['rev-parse', '--verify', f'{source}^{{commit}}'], root,
                           check=False)
        if resolved.returncode != 0:
            findings.append(
                f"{label} generatedFrom '{source}' is not a committed source; "
                'regenerate from a commit hash')
            continue
        source_commit = resolved.stdout.strip()
        contains_canon = run_git(
            ['merge-base', '--is-ancestor', canon, source_commit], root, check=False)
        if contains_canon.returncode == 0:
            continue
        source_is_older = run_git(
            ['merge-base', '--is-ancestor', source_commit, canon], root, check=False)
        if source_is_older.returncode == 0:
            findings.append(
                f'{label} is stale: generatedFrom {source_commit[:12]} predates '
                f'canon {canon[:12]}')
        else:
            findings.append(
                f'{label} generatedFrom {source_commit[:12]} is on a divergent '
                f'history from canon {canon[:12]}')
    return findings, stats


def split_row(s):
    """Split a markdown table row, honouring escaped pipes."""
    s = s.strip()
    s = s[1:] if s.startswith('|') else s
    s = s[:-1] if s.endswith('|') else s
    parts, cur, i = [], '', 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            cur += s[i + 1]; i += 2; continue
        if s[i] == '|':
            parts.append(cur.strip()); cur = ''; i += 1; continue
        cur += s[i]; i += 1
    parts.append(cur.strip())
    return parts


def parse(layer):
    txt = (REG / f'{layer}.md').read_text(encoding='utf-8')
    fm = {}
    m = re.match(r'^---\n(.*?)\n---\n', txt, re.S)
    if not m:
        raise SystemExit(f'{layer}: no frontmatter')
    for ln in m.group(1).splitlines():
        if ':' in ln:
            k, v = ln.split(':', 1)
            fm[k.strip()] = v.strip()
    sections, cur = [], None
    for ln in txt.splitlines():
        if ln.startswith('## '):
            cur = {'title': ln[3:].strip(), 'rows': [], 'header': None}
            sections.append(cur)
        elif ln.startswith('| ID |') and cur is not None:
            cur['header'] = [h.strip() for h in split_row(ln)]
        elif re.match(r'^\|\s*(IL|CL|AL|RL|PL|TL)-', ln) and cur is not None:
            cells = split_row(ln)
            if cur['header'] is None:
                raise SystemExit(f'{layer}: row before header: {ln[:60]}')
            if len(cells) != len(cur['header']):
                raise SystemExit(f'{layer}: {cells[0]} has {len(cells)} cells, '
                                 f'header declares {len(cur["header"])}')
            cur['rows'].append(dict(zip(cur['header'], cells)))
    return fm, [s for s in sections if s['rows']], txt


def outcome_of(row):
    return row.get('Outcome', '').split(' ', 1)[-1].strip().lower()


def trigger_of(cell):
    """Split a `Next action` cell into (kind, value) — the C-17 trigger_kind /
    trigger_value split, derived from the text already in the registers rather
    than migrated into new columns.

    Kinds: once · done · cadence · every. `EVERY X` and `AT EVERY X` are the
    same kind and the same value; writing one row each way is drift, which is
    what the collision check below catches. Returns None if it does not parse,
    which is itself a finding — a free-text trigger cannot support the README's
    claim that a checklist grouped by trigger "can never drift".
    """
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


def check(layer):
    fm, sections, txt = parse(layer)
    rows = [r for s in sections for r in s['rows']]
    out, review = [], []
    add = out.append
    stats = {}

    if 'rows' in fm and int(fm['rows']) != len(rows):
        add(f"frontmatter rows: {fm['rows']} but {len(rows)} rows parsed")
    ids = [r['ID'] for r in rows]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        add(f'duplicate ID {dup}')
    stats['rows'] = len(rows)

    # stage sub-counts
    for s in sections:
        m = re.search(r'\(([^)]*·[^)]*)\)\s*$', s['title'])
        if not m or 'Outcome' not in (s['header'] or []):
            continue
        claimed = {w.rstrip('.'): int(n)
                   for n, w in re.findall(r'(\d+)\s+(\w+)', m.group(1))}
        claimed = {('survives' if k == 'survive' else k): v for k, v in claimed.items()}
        actual = {}
        for r in s['rows']:
            actual[outcome_of(r)] = actual.get(outcome_of(r), 0) + 1
        for k in OUTCOMES & (set(claimed) | set(actual)):
            if claimed.get(k, 0) != actual.get(k, 0):
                add(f"stage '{s['title'][:40]}' claims {k}={claimed.get(k, 0)}, "
                    f"rows give {actual.get(k, 0)}")

    # outcome totals
    if rows and 'Outcome' in rows[0]:
        tot = {}
        for r in rows:
            o = outcome_of(r)
            if o not in OUTCOMES:
                add(f"{r['ID']}: outcome '{o}' not in vocabulary")
            tot[o] = tot.get(o, 0) + 1
        stats['outcome'] = tot
        for k in OUTCOMES:
            if k in fm and tot.get(k, 0) != int(fm[k]):
                add(f'frontmatter {k}: {fm[k]} but rows give {tot.get(k, 0)}')

    # catch-point table and phase prose
    if rows and 'Catch' in rows[0]:
        actual = {}
        for r in rows:
            actual[r['Catch']] = actual.get(r['Catch'], 0) + 1
        for pos in actual:
            if pos not in CATCH_ORDER:
                add(f"catch point '{pos}' not in the eleven-position ladder")
        stats['catch'] = actual
        mt = re.search(r'\| on disk \| session start \|.*?\n\|[-| ]+\n\|([^\n]*)\|', txt)
        if mt:
            nums = [int(c.strip()) for c in mt.group(1).split('|') if c.strip() != '']
            for pos, n in zip(CATCH_ORDER, nums):
                if n != actual.get(pos, 0):
                    add(f'catch table says {pos}={n}, rows give {actual.get(pos, 0)}')
        phases = {k: sum(actual.get(p, 0) for p in v) for k, v in PHASES.items()}
        stats['phases'] = phases
        mp = re.search(r'Before it starts (\d+) · before the change (\d+) · '
                       r'still in the session (\d+) · after the session (\d+)', txt)
        if mp:
            for i, k in enumerate(PHASES):
                if int(mp.group(i + 1)) != phases[k]:
                    add(f'phase prose says {k}={mp.group(i + 1)}, rows give {phases[k]}')

    # tool cell, built state, and the tooled-rows headline
    if rows and 'Tool' in rows[0]:
        tooled = designed = built = nomech = 0
        for r in rows:
            toks = [t.strip() for t in r['Tool'].split('·')]
            state = toks[-1]
            if state not in BUILT:
                add(f"{r['ID']}: built state '{state}' not in vocabulary")
            tier = next((t for t in toks if t in TIERS), None)
            if tier is None:
                add(f"{r['ID']}: tool cell names no tier — '{r['Tool']}'")
            if toks[0].lower() == 'none':
                nomech += 1
                if state != 'none':
                    add(f"{r['ID']}: names no mechanism but built state is "
                        f"'{state}' — must be 'none'")
            else:
                tooled += 1
                designed += state == 'designed'
                built += state == 'built'
        stats['built'] = {'tooled': tooled, 'designed': designed,
                          'built': built, 'no_mechanism': nomech}
        mh = re.search(r'(\d+) of the (\d+) are not built', txt)
        if mh:
            if (int(mh.group(1)), int(mh.group(2))) != (designed, tooled):
                add(f'headline says "{mh.group(1)} of the {mh.group(2)} are not built", '
                    f'rows give "{designed} of the {tooled}"')
        else:
            add('no "N of the M are not built" headline found')

    # residual
    if rows and 'Residual' in rows[0]:
        res = {}
        for r in rows:
            v = r['Residual']
            if v not in RESIDUAL:
                add(f"{r['ID']}: residual '{v}' not in vocabulary")
            res[v] = res.get(v, 0) + 1
        stats['residual'] = res
        if layer not in RESIDUAL_EXCEPTION:
            for r in rows:
                o, v = outcome_of(r), r['Residual']
                state = r['Tool'].split('·')[-1].strip() if 'Tool' in r else None
                if o in ('survives', 'irreversible') and v != 'open':
                    add(f"{r['ID']}: {o} but residual '{v}' (README: always open)")
                if state in ('designed', 'none') and v == 'closed':
                    add(f"{r['ID']}: mechanism {state} but residual 'closed' "
                        f'with no substitute recorded')
                if state == 'built' and o in ('prevented', 'detected') \
                        and v not in ('closed', 'partially closed'):
                    add(f"{r['ID']}: built + {o} but residual '{v}'")
    else:
        add('no Residual column')

    # evidence tier (D-107) — every row carries `evidenced` or `candidate`,
    # the frontmatter declares the split, and the two must agree. Whether a
    # row's marker matches the actual receipts is the cross-register check in
    # check_evidence(); this block only proves the register is internally
    # consistent about its own declaration.
    if rows and 'Evidence' in rows[0]:
        ev_counts = {'evidenced': 0, 'candidate': 0}
        for r in rows:
            v = r['Evidence']
            if v not in EVIDENCE:
                add(f"{r['ID']}: evidence '{v}' not in vocabulary "
                    f'(evidenced · candidate)')
            else:
                ev_counts[v] += 1
        stats['evidence'] = ev_counts
        for key in ('evidenced', 'candidate'):
            if key not in fm:
                add(f'rows carry an Evidence column but frontmatter declares '
                    f'no `{key}:` count')
            elif int(fm[key]) != ev_counts[key]:
                add(f'frontmatter {key}: {fm[key]} but rows give '
                    f'{ev_counts[key]}')
    else:
        add('no Evidence column — every register row carries an evidence '
            'status (D-107)')

    # status (C-04) — the control's own state. Only truth carries one today;
    # the other five are listed in NO_STATUS_COLUMN so the absence is a
    # recorded design choice rather than a silent gap in this checker.
    has_status = bool(rows) and 'Status' in rows[0]
    if has_status:
        st = {}
        for r in rows:
            v = r['Status']
            if v not in TRUTH_STATUS:
                add(f"{r['ID']}: status '{v}' not in the declared vocabulary "
                    f'({", ".join(sorted(TRUTH_STATUS))})')
            st[v] = st.get(v, 0) + 1
            # only `in force` closes a claim; every other state reads open
            res = r.get('Residual')
            if res is not None:
                if v in STATUS_IN_FORCE and res not in ('closed', 'partially closed'):
                    add(f"{r['ID']}: status '{v}' but residual '{res}'")
                if v not in STATUS_IN_FORCE and res != 'open':
                    add(f"{r['ID']}: status '{v}' is not in force, so residual "
                        f"must be open, not '{res}'")
        stats['status'] = st
    elif layer not in NO_STATUS_COLUMN:
        add('no Status column, and this layer is not declared as carrying none')

    # trigger (C-07) and the install gate (C-02)
    if rows and 'Next action' in rows[0]:
        kinds, heads = {}, {}
        for r in rows:
            cell = r['Next action']
            parsed = trigger_of(cell)
            if parsed is None:
                add(f"{r['ID']}: trigger '{cell.split('—')[0].strip()}' parses to "
                    f'no kind — expected ONCE, DONE, a cadence, or EVERY <event>')
                continue
            kind, value = parsed
            kinds[kind] = kinds.get(kind, 0) + 1
            heads.setdefault(value, set()).add(cell.split('—')[0].strip())
            if kind == 'every' and value not in EVERY_VALUES:
                add(f"{r['ID']}: trigger value '{value}' is not in the declared "
                    'per-event vocabulary')
            # The install gate: a control nobody has switched on closes nothing.
            #
            # Hard where the layer has no built state — provenance, where a
            # `ONCE —` action is the only signal that a mechanism is not yet
            # real, so the reading is unambiguous.
            #
            # Advisory in the four built-state layers, because `built` means
            # the mechanism exists in `hullkey-charge` and a ONCE action may
            # be an install (RL-1A, "Turn checkpointing on") *or* extension
            # and practice work on a control already in force (AL-3B, "Move
            # every local-only guard to the server"). Only a human can tell
            # those apart, so they are surfaced for adjudication rather than
            # failed. This is the same conflation as C-02's root cause: `built`
            # records that a mechanism exists, not that it is in force here.
            if kind == 'once' and r.get('Residual') == 'closed':
                msg = (f"{r['ID']}: residual 'closed' but the next action is a "
                       f'ONCE install — the control is not switched on')
                if 'Tool' in r:
                    review.append(msg + f" (next action: '{cell}')")
                else:
                    add(msg)
        stats['trigger'] = kinds
        stats['_trigger_values'] = {k: sorted(v) for k, v in heads.items()}

    return out, stats, review


def evidence_receipts(corrections_path=None, calibration_path=None):
    """(first_party, corpus) — the row IDs holding a receipt, derived.

    First-party: every ⟪instance-of: …⟫ marker in the Corrections Register
    (the same source check-spoke-evidence.py reads). Corpus: every row the
    run-22 calibration table codes as an exact or variant match, read
    header-driven off `nearest_row` / `row_fit`. Field cases are the declared
    FIELD_CASES constant, not derived — there is exactly one on file.

    The derivation is deliberately re-run on every check rather than stored:
    a stored classification is a second copy of a fact that can drift from
    its source, which is the exact defect class this project logs.

    Returns (None, None, None) — distinct from the broken-derivation (set(),
    ...) shape — when either source file is simply absent. That is the
    expected shape outside the vault: the public False Floors repo copies the
    registers, the tool and the checkers, and deliberately never the
    Corrections Register or the calibration research file (public-repo/
    README.md's copy boundary). check_evidence() reads the None sentinel as
    'not applicable here' rather than 'derivation broke'.
    """
    corrections_path = pathlib.Path(corrections_path or CORRECTIONS_PATH)
    calibration_path = pathlib.Path(calibration_path or CALIBRATION_PATH)
    if not corrections_path.exists() or not calibration_path.exists():
        return None, None, None
    first_party = set()
    for block in re.findall(r'⟪instance-of:\s*([^⟫]+)⟫',
                            corrections_path.read_text(encoding='utf-8')):
        first_party.update(ROW_ID_RE.findall(block))
    corpus, header, coded = set(), None, 0
    for line in calibration_path.read_text(encoding='utf-8').splitlines():
        if line.startswith('| case_id |'):
            header = [h.strip() for h in split_row(line)]
            continue
        if header and re.match(r'^\|\s*CAL-\d+', line):
            cells = split_row(line)
            if len(cells) != len(header):
                continue
            row = dict(zip(header, cells))
            coded += 1
            if row.get('row_fit') in ('exact', 'variant'):
                rid = row.get('nearest_row', '').strip()
                if ROW_ID_RE.fullmatch(rid):
                    corpus.add(rid)
    return first_party, corpus, coded


def check_evidence(layer_rows, first_party, corpus, coded_cases,
                   field_cases=None):
    """D-107 receipts check: an Evidence marker must match the receipts.

    A row marked `evidenced` with no receipt is the defect the inclusion rule
    exists to prevent — an unevidenced row inside the headline count. A row
    marked `candidate` that has a receipt understates the framework's own
    evidence and is equally a finding, because both directions make the
    published 66 wrong.

    `first_party is None` is evidence_receipts()'s absent-source sentinel,
    not a broken derivation — reported as review so it does not fail a
    checkout that never carries the Corrections Register or the calibration
    file by design (the public False Floors repo). An empty set() is still
    the broken-derivation case below and still fails loudly.
    """
    if first_party is None:
        return [], ["evidence-receipts check skipped — Corrections Register.md "
                    "and/or the run-22 calibration file are not present in this "
                    "checkout (expected outside the vault)"], {'skipped': True}
    field_cases = FIELD_CASES if field_cases is None else field_cases
    findings, review = [], []
    receipts = first_party | corpus | field_cases
    # a broken derivation must fail loudly, never read as "no receipts"
    if not first_party:
        findings.append('no ⟪instance-of⟫ markers parsed from the Corrections '
                        'Register — the first-party derivation is broken')
    if not corpus or coded_cases < 200:
        findings.append(f'corpus derivation read {coded_cases} coded cases and '
                        f'{len(corpus)} matched rows from run 22 — the table '
                        'holds 262 cases, so the parser or the file moved')
    all_ids = set()
    for layer, rows in layer_rows.items():
        for r in rows:
            rid, ev = r['ID'], r.get('Evidence')
            all_ids.add(rid)
            if ev == 'evidenced' and rid not in receipts:
                findings.append(
                    f'{rid}: marked evidenced but no receipt found — no '
                    f'⟪instance-of⟫ mapping, no corpus exact/variant match, '
                    f'no declared field case')
            if ev == 'candidate' and rid in receipts:
                src = ('a first-party mapping' if rid in first_party else
                       'a corpus match' if rid in corpus else 'a field case')
                findings.append(f'{rid}: marked candidate but {src} exists — '
                                f'promote it to evidenced')
    for rid in sorted((first_party | corpus) - all_ids):
        review.append(f'a receipt names {rid}, which is not a live register '
                      f'row — retired, or mistyped in its source')
    evidenced = {rid for layer, rows in layer_rows.items() for rid in
                 (r['ID'] for r in rows if r.get('Evidence') == 'evidenced')}
    stats = {'evidenced': len(evidenced),
             'candidate': sum(len(rows) for rows in layer_rows.values()) - len(evidenced),
             'first_party': len(first_party & all_ids),
             'corpus_only': len((corpus - first_party) & all_ids),
             'field_case_only': len((field_cases - first_party - corpus) & all_ids)}
    return findings, review, stats


FIXTURES = {
    # residual `closed` on a control whose own next action is a ONCE install
    'provenance-layer': """---
type: register
rows: 3
---

## Fixture

| ID | Sev | What breaks | Outcome | Residual | Next action |
| --- | --- | --- | --- | --- | --- |
| PL-9A | S3 | fixture install gate | A prevented | closed | ONCE — Install the thing |
| PL-9B | S3 | fixture ritual | A prevented | open | EVERY MERGE — Check it |
| PL-9C | S3 | fixture unknown ritual | B detected | open | EVERY BLUE MOON — Check it |
""",
    # a status value outside the declared vocabulary; an evidence value outside
    # its vocabulary; a frontmatter evidence count the rows do not support
    'truth-layer': """---
type: register
rows: 1
evidenced: 5
candidate: 0
---

## Fixture

| ID | Evidence | Sev | Claim | Status | Residual |
| --- | --- | --- | --- | --- | --- |
| TL-9A | confirmed | S3 | fixture claim | switched on | closed |
""",
    # the same ritual spelled two ways, so a trigger-grouped checklist doubles it
    'recovery-layer': """---
type: register
rows: 1
---

## Fixture

| ID | Sev | Failure | Outcome | Residual | Next action |
| --- | --- | --- | --- | --- | --- |
| RL-9A | S3 | fixture collision | A prevented | open | AT EVERY MERGE — Check it |
""",
}

# D-099 / C-06. Each entry is a register pair this checker must reject. The
# fourth is the one the row exists for: two registers using one word for two
# different letters is the collapse itself, and it must be caught even though
# every individual register looks internally consistent.
CLASS_VOCAB_FIXTURES = {
    'undeclared': {
        'x-layer': ({'rows': '2', 'class-a': '0', 'class-b': '1', 'class-c': '1'}, []),
    },
    'split does not cover the register': {
        'x-layer': ({'rows': '9', 'class-a': '0', 'class-b': '1', 'class-c': '1',
                     'class-a-reads': 'prevented', 'class-b-reads': 'detected',
                     'class-c-reads': 'survives'}, []),
    },
    'declared vocabulary and row cells disagree': {
        'x-layer': ({'rows': '1', 'class-a': '0', 'class-b': '1', 'class-c': '0',
                     'class-a-reads': 'prevented', 'class-b-reads': 'recoverable',
                     'class-c-reads': 'irreversible'},
                    [{'rows': [{'Outcome': 'B detected'}]}]),
    },
    'one word two letters': {
        'x-layer': ({'rows': '1', 'class-a': '0', 'class-b': '1', 'class-c': '0',
                     'class-a-reads': 'prevented', 'class-b-reads': 'detected',
                     'class-c-reads': 'survives'},
                    [{'rows': [{'Outcome': 'B detected'}]}]),
        'y-layer': ({'rows': '1', 'class-a': '0', 'class-b': '0', 'class-c': '1',
                     'class-a-reads': 'prevented', 'class-b-reads': 'recoverable',
                     'class-c-reads': 'detected'},
                    [{'rows': [{'Outcome': 'C detected'}]}]),
    },
}

# The live shape, which must stay clean: two registers, different words, no
# word doing two jobs. A check that cannot pass a legitimate case is a check
# that will be switched off.
CLASS_VOCAB_GOOD = {
    'aligned-layer': ({'rows': '2', 'class-a': '0', 'class-b': '1', 'class-c': '1',
                       'class-a-reads': 'prevented', 'class-b-reads': 'detected',
                       'class-c-reads': 'survives'},
                      [{'rows': [{'Outcome': 'B detected'}, {'Outcome': 'C survives'}]}]),
    'recovery-layer': ({'rows': '2', 'class-a': '0', 'class-b': '1', 'class-c': '1',
                        'class-a-reads': 'prevented', 'class-b-reads': 'recoverable',
                        'class-c-reads': 'irreversible'},
                       [{'rows': [{'Outcome': 'B recoverable'}, {'Outcome': 'C irreversible'}]}]),
}

SELF_TEST_EXPECTED = [
    ('provenance-layer', 'ONCE install'),
    ('provenance-layer', "trigger value 'blue moon' is not in the declared"),
    ('truth-layer', 'not in the declared vocabulary'),
    ('truth-layer', "evidence 'confirmed' not in vocabulary"),
    ('truth-layer', 'frontmatter evidenced: 5 but rows give 0'),
    ('provenance-layer', 'no Evidence column'),
    ('(evidence: receipts)', 'marked evidenced but no receipt found'),
    ('(evidence: receipts)', 'marked candidate but a corpus match exists'),
    ('(evidence: receipts)', 'is not a live register row'),
    ('(evidence: broken derivation)', 'first-party derivation is broken'),
    ('(cross-layer)', "trigger 'merge' is written 2 ways"),
    ('(generated-view stale fixture)', 'is stale'),
    ('(generated-view fallback fixture)', 'does not match register-data.json'),
    ('(view stamp: a register changed after generation)', 'canonBlobs does not match'),
    ('(view stamp: a register missing from the stamp)', 'canonBlobs does not match'),
    ('(view stamp: copies disagree though content matches)',
     'does not match register-data.json'),
    ('(class vocabulary: undeclared)', 'does not declare'),
    ('(class vocabulary: split does not cover the register)', 'does not cover the register'),
    ('(class vocabulary: declared vocabulary and row cells disagree)',
     'declared vocabulary and row cells disagree'),
    ('(class vocabulary: one word two letters)', "is declared for 2 different letters"),
]


def self_test():
    """Prove this checker can still fail.

    A checker that passes is only evidence if it is capable of failing — the
    framework's own PL-3E, a dead sensor being indistinguishable from a pass.
    Each fixture below carries one of the defects this tool was extended to
    catch (C-02, C-04, C-07, C-25). The C-25 fixture uses real repository
    ancestry but temporary view files, so it proves the production git path
    rejects an intentionally stale source without touching either live copy.
    """
    import tempfile
    global REG
    real_reg = REG
    with tempfile.TemporaryDirectory() as tmp:
        REG = pathlib.Path(tmp)
        for layer, body in FIXTURES.items():
            (REG / f'{layer}.md').write_text(body, encoding='utf-8')
        report = {}
        for layer in FIXTURES:
            findings, stats, review = check(layer)
            report[layer] = {'findings': findings, 'review': review, 'stats': stats}
        cross = cross_layer_trigger_check(report)
        if cross:
            report['(cross-layer)'] = {'findings': [], 'review': cross, 'stats': {}}
    REG = real_reg

    # ---- D-107 evidence-receipts fixtures ------------------------------------
    # KNOWN-BAD, both directions: an evidenced row with no receipt (the defect
    # the inclusion rule exists to prevent) and a candidate row whose receipt
    # exists (the published 66 understated). Plus a receipt naming a dead ID,
    # which must surface as review, and a broken derivation, which must fail
    # loudly rather than read as "no receipts anywhere".
    ev_rows = {'x-layer': [
        {'ID': 'TL-02', 'Evidence': 'evidenced'},   # receipt exists — clean
        {'ID': 'TL-06', 'Evidence': 'evidenced'},   # no receipt — must fail
        {'ID': 'TL-09', 'Evidence': 'candidate'},   # corpus receipt — must fail
        {'ID': 'TL-07', 'Evidence': 'candidate'},   # no receipt — clean
    ]}
    f, rv, _ = check_evidence(ev_rows, {'TL-02', 'RL-9Z'}, {'TL-09'}, 262,
                              field_cases=set())
    report['(evidence: receipts)'] = {'findings': f, 'review': rv, 'stats': {}}
    f, rv, _ = check_evidence(ev_rows, set(), {'TL-09'}, 262, field_cases=set())
    report['(evidence: broken derivation)'] = {'findings': f, 'review': rv,
                                               'stats': {}}
    # ABSENT SOURCE, not a broken derivation: the public False Floors repo never
    # carries Corrections Register.md or the calibration file (public-repo/README.md's
    # copy boundary), so evidence_receipts() must return the None sentinel rather than
    # crash, and check_evidence() must read that as review, never as a finding — an
    # absent comparison is not a wrong one.
    import tempfile as _tf2
    with _tf2.TemporaryDirectory() as absent_dir:
        fp, cp, coded_absent = evidence_receipts(
            corrections_path=pathlib.Path(absent_dir) / 'Corrections Register.md',
            calibration_path=pathlib.Path(absent_dir) / '22-register-calibration-pass-2026-08-09.md')
    f, rv, _ = check_evidence(ev_rows, fp, cp, coded_absent, field_cases=set())
    bad = bool(f) or fp is not None or not any('skipped' in x for x in rv)
    # `fired_on_valid_input` is this file's established convention key for 'must stay
    # clean' assertions (see the class-vocabulary and generated-view fixtures above) —
    # reused here rather than a bespoke flag so the generic sweep at the end of
    # self_test() picks this assertion up the same way it picks up theirs.
    report['(evidence: absent source files, not broken)'] = {
        'findings': f, 'review': rv,
        'stats': {'fired_on_valid_input': bad}}
    # KNOWN-GOOD: a correct classification must produce zero findings.
    good_rows = {'x-layer': [
        {'ID': 'TL-02', 'Evidence': 'evidenced'},
        {'ID': 'TL-09', 'Evidence': 'evidenced'},
        {'ID': 'TL-07', 'Evidence': 'candidate'},
    ]}
    f, rv, _ = check_evidence(good_rows, {'TL-02'}, {'TL-09'}, 262,
                              field_cases=set())
    report['(evidence: correct classification)'] = {
        'findings': [], 'review': [],
        'stats': {'fired_on_valid_input': f + rv}}

    root = pathlib.Path(run_git(['rev-parse', '--show-toplevel']).stdout.strip())
    register_path = REG.relative_to(root).as_posix()
    canon = run_git([
        'log', '-1', '--format=%H', '--', f':(glob){register_path}/*.md'
    ], root).stdout.strip()
    stale = run_git(['rev-parse', f'{canon}^'], root).stdout.strip()
    stale_payload = {
        'generatedFrom': stale,
        'generatedBy': 'self-test',
        'rowCount': 0,
        'rows': [],
    }
    with tempfile.TemporaryDirectory() as tmp:
        fixture_dir = pathlib.Path(tmp)
        fixture_json = fixture_dir / 'register-data.json'
        fixture_page = fixture_dir / 'index.html'
        fixture_json.write_text(json.dumps(stale_payload), encoding='utf-8')
        fixture_page.write_text(
            '<script id="register-data-fallback" type="application/json">'
            + json.dumps(stale_payload) + '</script>', encoding='utf-8')
        findings, stats = check_generated_views(
            fixture_json, fixture_page, repo_root=root)
        report['(generated-view stale fixture)'] = {
            'findings': findings, 'review': [], 'stats': stats,
        }

        mismatched = dict(stale_payload)
        mismatched['rowCount'] = 1
        fixture_page.write_text(
            '<script id="register-data-fallback" type="application/json">'
            + json.dumps(mismatched) + '</script>', encoding='utf-8')
        findings, stats = check_generated_views(
            fixture_json, fixture_page, repo_root=root)
        report['(generated-view fallback fixture)'] = {
            'findings': findings, 'review': [], 'stats': stats,
        }

        # ---- C-25 content-stamp fixtures, added 2026-08-21 -------------------
        # The ancestry test's two failure modes were both met on one day (a squash
        # merge, then a deleted branch), so canonBlobs was added. These prove the
        # replacement can PASS the case it was built for and still FAIL everything
        # the old test failed. The scenario fixture is the load-bearing one: an
        # UNRESOLVABLE generatedFrom with correct content must pass, because that
        # is exactly what a squash-plus-branch-delete leaves behind and it is the
        # state no earlier version of this check could accept.
        canon_now = register_blobs_at(canon, root, register_path) or {}

        def _view(payload):
            fixture_json.write_text(json.dumps(payload), encoding='utf-8')
            fixture_page.write_text(
                '<script id="register-data-fallback" type="application/json">'
                + json.dumps(payload) + '</script>', encoding='utf-8')
            return check_generated_views(fixture_json, fixture_page, repo_root=root)

        def _payload(**over):
            base = {'generatedFrom': canon, 'generatedBy': 'self-test',
                    'canonBlobs': dict(canon_now), 'rowCount': 0, 'rows': []}
            base.update(over)
            return base

        # KNOWN-GOOD: the #152 scenario. Commit cannot be resolved at all; content is
        # right. Must pass — this is the whole point of the change.
        f, st = _view(_payload(generatedFrom='0' * 40))
        report['(view stamp: unresolvable commit, content matches)'] = {
            'findings': [], 'review': [], 'stats': {'fired_on_valid_input': f}}

        # KNOWN-GOOD: a legacy view with no canonBlobs and a correct commit must
        # still pass by ancestry, so this change is additive.
        legacy_ok = _payload()
        legacy_ok.pop('canonBlobs')
        f2, _ = _view(legacy_ok)
        report['(view stamp: legacy view, no canonBlobs, commit correct)'] = {
            'findings': [], 'review': [], 'stats': {'fired_on_valid_input': f2}}

        # KNOWN-BAD: one register file edited after generation.
        wrong = dict(canon_now)
        first = sorted(wrong)[0]
        wrong[first] = '1' * 40
        f, st = _view(_payload(canonBlobs=wrong))
        report['(view stamp: a register changed after generation)'] = {
            'findings': f, 'review': [], 'stats': st}

        # KNOWN-BAD: a register file dropped from the stamp entirely.
        short = dict(canon_now)
        short.pop(sorted(short)[0])
        f, st = _view(_payload(canonBlobs=short))
        report['(view stamp: a register missing from the stamp)'] = {
            'findings': f, 'review': [], 'stats': st}

        # KNOWN-BAD: content right, but the two copies disagree — the pre-existing
        # rule must not be weakened by the new fast path.
        fixture_json.write_text(json.dumps(_payload()), encoding='utf-8')
        fixture_page.write_text(
            '<script id="register-data-fallback" type="application/json">'
            + json.dumps(_payload(rowCount=99)) + '</script>', encoding='utf-8')
        f, st = check_generated_views(fixture_json, fixture_page, repo_root=root)
        report['(view stamp: copies disagree though content matches)'] = {
            'findings': f, 'review': [], 'stats': st}

    for name, fixture in CLASS_VOCAB_FIXTURES.items():
        report[f'(class vocabulary: {name})'] = {
            'findings': class_vocabulary_findings(fixture), 'review': [], 'stats': {},
        }
    good = class_vocabulary_findings(CLASS_VOCAB_GOOD)
    report['(class vocabulary: legitimate difference)'] = {
        'findings': [], 'review': [],
        'stats': {'fired_on_valid_input': good},
    }

    failed = False
    if good:
        failed = True
        print('[MISS] (class vocabulary): fired on a legitimate two-vocabulary '
              f'register pair, which is the case the design requires: {good}')
    else:
        print('[ok  ] (class vocabulary): stays clean when two registers use '
              'different words for the same letter')

    # The known-GOOD half of the C-25 content-stamp change. Without these two
    # assertions the fixtures above only prove the check can fail, and a check that
    # fails on everything guards nothing — it is also the exact regression that would
    # undo this change, since reverting to ancestry-only still fails every known-bad.
    for label, r in report.items():
        fired = r.get('stats', {}).get('fired_on_valid_input')
        if fired is None:
            continue
        if fired:
            failed = True
            print(f'[MISS] {label}: fired on input that must PASS — {fired}')
        else:
            print(f'[ok  ] {label}: stays clean, as it must')

    for layer, needle in SELF_TEST_EXPECTED:
        r = report.get(layer, {})
        hits = [f for f in r.get('findings', []) + r.get('review', []) if needle in f]
        mark = 'ok  ' if hits else 'MISS'
        if not hits:
            failed = True
        print(f'[{mark}] {layer}: expected a finding containing "{needle}"')
        for h in hits:
            print(f'         caught: {h}')
    # C-31 fixtures. Added 2026-08-12 with the corrections reader. Each is a row this
    # tool must reject; the last is a row it must ACCEPT, because a check that fails on
    # everything is as useless as one that fails on nothing — and the first gate written
    # under this rule was itself defective in exactly that direction, screaming on 13 of
    # 15 correct inputs until it was validated.
    import tempfile as _tf
    corrections_fixtures = [
        ('recurring class with no gate',
         '| C-90 | prose ⟦instances=3⟧ | ev | S2 | elsewhere |',
         'no gate='),
        ('gate names a file that does not exist (in a repo that IS present)',
         '| C-91 | prose ⟦instances=2 gate=second-brain/nope/missing-gate.py validated=abc⟧ | ev | S2 | e |',
         'does not exist'),
        ('gate present but never validated against known-bad input',
         '| C-92 | prose ⟦instances=2 gate=second-brain/CLAUDE.md⟧ | ev | S2 | e |',
         'no validated='),
        ('instance count not an integer',
         '| C-93 | prose ⟦instances=many gate=x validated=y⟧ | ev | S2 | e |',
         'not an integer'),
        # C-34 fixtures. The third is the one that matters: a row may name a real gate,
        # a real validation AND a real invoker file, and still be lying, because the
        # invoker never calls the gate. That is the exact shape both live gated rows had
        # on 2026-08-12 — wiring asserted in prose, absent in fact.
        ('gate exists and is validated but nothing invokes it',
         '| C-96 | prose ⟦instances=2 gate=second-brain/CLAUDE.md validated=abc⟧ | ev | S2 | e |',
         'no runs='),
        ('runs= names a file that does not exist',
         '| C-97 | prose ⟦instances=2 gate=second-brain/CLAUDE.md validated=abc '
         'runs=second-brain/no-such-workflow.yml⟧ | ev | S2 | e |',
         'does not exist'),
        ('runs= names a real file that never calls the gate',
         '| C-98 | prose ⟦instances=2 gate=second-brain/CLAUDE.md validated=abc '
         'runs=second-brain/METHODOLOGY.md⟧ | ev | S2 | e |',
         'never mentions'),
    ]
    # The absent-sibling-repo branch (CI has no ~/Developer): must be REVIEW, never a
    # finding and never counted wired. Checked separately because the expectation is in
    # `review`, not `findings` - the first CI run crashed and then failed precisely
    # because absence-of-the-repo and absence-of-the-file were one branch.
    unverifiable_fixtures = [
        ('gate in a repo not present on this machine is review, not a finding',
         '| C-99 | prose ⟦instances=2 gate=no-such-repo-zzz/scripts/g.py validated=abc⟧ | ev | S2 | e |',
         'unverifiable here'),
    ]
    for label, row, needle in unverifiable_fixtures:
        with _tf.NamedTemporaryFile('w', suffix='.md', delete=False) as fh:
            fh.write('# fixture\n\n| ID | Correction | Evidence | Sev | Where |\n'
                     '|---|---|---|---|---|\n' + row + '\n')
            fx = pathlib.Path(fh.name)
        f, r, st = check_corrections(fx)
        fx.unlink()
        hits = [x for x in r if needle in x]
        bad = f or st.get('wired', 0) or not hits
        mark = 'ok ' if not bad else 'FAIL'
        if bad:
            failed = True
        print(f'[{mark}] corrections: {label}')

    # ABSENT FILE, not a broken read: the public False Floors repo never carries the
    # Corrections Register (public-repo/README.md's copy boundary), so a missing file
    # must be review, never a finding.
    f, r, _ = check_corrections(pathlib.Path(_tf.mkdtemp()) / 'Corrections Register.md')
    bad = bool(f) or not any('skipped' in x for x in r)
    mark = 'ok ' if not bad else 'FAIL'
    if bad:
        failed = True
    print(f'[{mark}] corrections: absent Corrections Register.md is review, not a '
          f'finding — findings={f} review={r}')

    for label, row, needle in corrections_fixtures:
        with _tf.NamedTemporaryFile('w', suffix='.md', delete=False) as fh:
            fh.write('# fixture\n\n| ID | Correction | Evidence | Sev | Where |\n'
                     '|---|---|---|---|---|\n' + row + '\n')
            fx = pathlib.Path(fh.name)
        f, _r, _s = check_corrections(fx)
        fx.unlink()
        hits = [x for x in f if needle in x]
        mark = 'ok ' if hits else 'FAIL'
        if not hits:
            failed = True
        print(f'[{mark}] corrections: {label} — expected a finding containing "{needle}"')
        for h in hits:
            print(f'         caught: {h}')

    with _tf.NamedTemporaryFile('w', suffix='.md', delete=False) as fh:
        fh.write('# fixture\n\n| ID | Correction | Evidence | Sev | Where |\n|---|---|---|---|---|\n'
                 '| C-94 | one-off, no gate owed ⟦instances=1⟧ | ev | S3 | e |\n'
                 '| C-95 | deliberately ungateable ⟦instances=4 gate=none—needs_a_human_judgement '
                 'validated=n/a⟧ | ev | S3 | e |\n'
                 # genuinely wired: this file is both the gate and, for the purposes of the
                 # fixture, its own invoker — it does contain the string 'check-registers.py'.
                 '| C-96b | properly wired ⟦instances=9 '
                 'gate=second-brain/projects/agent-trust-framework/registers/tools/'
                 'check-registers.py validated=abc runs=second-brain/projects/'
                 'agent-trust-framework/registers/tools/check-registers.py⟧ | ev | S3 | e |\n')
        fx = pathlib.Path(fh.name)
    f, _r, _s = check_corrections(fx)
    fx.unlink()
    mark = 'ok ' if not f else 'FAIL'
    if f:
        failed = True
    print(f'[{mark}] corrections: legal rows pass — a single instance owes no gate, and '
          '"none—<reason>" is an explicit answer')
    for h in f:
        print(f'         wrongly flagged: {h}')

    # --- C-43: a log ID minted twice ------------------------------------------------
    # The first fixture is not invented. It is the 13 August 2026 collision rebuilt from
    # real git objects: the fork point and origin/main are read from this repository, and
    # the branch side is the False Floors entry as it was actually drafted — numbered
    # D-083, by a session that could not see that the prior-art run had landed its own
    # D-083 and D-084 on origin/main the same day.
    root = pathlib.Path(run_git(['rev-parse', '--show-toplevel']).stdout.strip())
    log_rel = (PROJECT / 'Decision Log.md').relative_to(root).as_posix()
    pattern = LOG_ID_PATTERNS['Decision Log.md']
    base_ref = next((r for r in BASE_REFS if run_git(
        ['rev-parse', '--verify', '--quiet', f'{r}^{{commit}}'], root, check=False
    ).returncode == 0), None)

    if base_ref is None:
        print('[skip] log ids: this clone has no base ref among '
              f'{", ".join(BASE_REFS)} — the D-083 re-enactment cannot run here')
    else:
        base = ids_in(run_git(['show', f'{base_ref}:{log_rel}'], root).stdout, pattern)
        # The fork is reconstructed from the base rather than read from HEAD, deliberately.
        # An earlier version of this fixture took the live merge-base, and it would have
        # gone quiet in two ordinary situations — the moment this branch caught up to main,
        # and in CI, where a pull_request checkout is already the merge commit, so the fork
        # point contains D-083 and nothing collides. A fixture that silently stops testing
        # when the repository moves is worse than none. Dropping the three IDs the
        # concurrent prior-art run landed reproduces exactly what the False Floors session
        # forked from, and depends on nothing but the base.
        CONCURRENT = {'D-083', 'D-084', 'D-085'}
        fork = {k: v for k, v in base.items() if k not in CONCURRENT}

        drafted = dict(fork)
        drafted['D-083'] = ['### D-083 — False Floors is the published name; the 9 August '
                            'kill is reversed, and the reversal finally reaches this log']
        caught = independently_minted(drafted, base, fork)
        hit = 'D-083' in caught
        # The re-enactment is only evidence if origin/main genuinely holds a *different*
        # D-083. If the base ever stops carrying one, this fixture proves nothing and must
        # say so rather than passing vacuously.
        if 'D-083' not in base:
            print(f'[skip] log ids: {base_ref} no longer carries a D-083 — the historical '
                  're-enactment has nothing to collide with')
        else:
            if not hit:
                failed = True
            print(f"[{'ok ' if hit else 'FAIL'}] log ids: the real 2026-08-13 collision is "
                  f'caught — D-083 drafted here vs the different D-083 already on '
                  f'{base_ref}')

        # Negative fixtures. A gate that fires on ordinary work trains the reader to skim
        # its output, so both legal shapes must stay silent: minting a number nobody else
        # took, and editing an entry that already existed when the branches forked.
        fresh = dict(fork)
        fresh['D-9999'] = ['### D-9999 — a number no other branch has taken']
        noisy_new = independently_minted(fresh, base, fork)
        if noisy_new:
            failed = True
        print(f"[{'ok ' if not noisy_new else 'FAIL'}] log ids: a genuinely new ID does not "
              'fire — only IDs minted on both sides count')
        for h in noisy_new:
            print(f'         wrongly flagged: {h}')

        shared = sorted(set(fork) & set(base))
        if shared:
            edited = dict(fork)
            edited[shared[0]] = [f'### {shared[0]} — retitled by this branch']
            noisy_edit = independently_minted(edited, base, fork)
            if noisy_edit:
                failed = True
            print(f"[{'ok ' if not noisy_edit else 'FAIL'}] log ids: editing {shared[0]}, "
                  'which existed at the fork, is an edit and not a collision')
            for h in noisy_edit:
                print(f'         wrongly flagged: {h}')

    # The post-merge shape, end to end through check_log_ids: once git has concatenated
    # both appends without a conflict, one file carries the ID twice.
    with tempfile.TemporaryDirectory() as tmp:
        proj = pathlib.Path(tmp)
        (proj / 'Decision Log.md').write_text(
            '# fixture\n\n'
            '### D-090 — the entry this branch wrote\nbody\n\n'
            '### D-091 — an unrelated entry\nbody\n\n'
            '### D-090 — the entry the other branch wrote, merged in silently\nbody\n',
            encoding='utf-8')
        (proj / 'Corrections Register.md').write_text(
            '# fixture\n\n| ID | Correction |\n|---|---|\n'
            '| C-90 | one |\n| C-91 | two |\n| C-90 | one, again |\n', encoding='utf-8')
        dup, _rev, _st = check_log_ids(project=proj)
        got = {f.split(':')[0] for f in dup if 'minted 2 times' in f}
        both = got == {'Decision Log.md', 'Corrections Register.md'}
        if not both:
            failed = True
        print(f"[{'ok ' if both else 'FAIL'}] log ids: a duplicate inside one file is "
              'caught in both logs — the shape CI sees, because a PR checkout is already '
              'the merge commit')
        for f in dup:
            print(f'         caught: {f[:110]}')

    with tempfile.TemporaryDirectory() as tmp:
        proj = pathlib.Path(tmp)
        (proj / 'Decision Log.md').write_text(
            '# fixture\n\n### D-090 — one\nbody\n\n### Proposed D-091 — two\nbody\n',
            encoding='utf-8')
        (proj / 'Corrections Register.md').write_text(
            '# fixture\n\n| ID | Correction |\n|---|---|\n| C-90 | one |\n| C-91 | two |\n',
            encoding='utf-8')
        clean, _rev, _st = check_log_ids(project=proj)
        if clean:
            failed = True
        print(f"[{'ok ' if not clean else 'FAIL'}] log ids: distinct IDs in both logs pass, "
              'including the `Proposed D-nnn` heading form')
        for f in clean:
            print(f'         wrongly flagged: {f}')

    # ABSENT LOGS, not a broken read: the public False Floors repo never carries
    # Decision Log.md or Corrections Register.md (public-repo/README.md's copy
    # boundary), so both being missing must be review, never a finding.
    with tempfile.TemporaryDirectory() as tmp:
        proj = pathlib.Path(tmp)
        f, r, _ = check_log_ids(project=proj)
        # exactly 2 'skipped' review lines (one per LOG_ID_PATTERNS file) must be
        # present; any extra review line here is the unrelated cross-branch rule
        # (base-ref/merge-base availability) reacting to the real git context this
        # self-test happens to run in, not this fix, so it is not asserted against.
        bad = bool(f) or sum('skipped' in x for x in r) != 2
        mark = 'ok ' if not bad else 'FAIL'
        if bad:
            failed = True
        print(f'[{mark}] log ids: both logs absent is review, not a finding — '
              f'findings={f} review={r}')

    # --- D-087 follow-on: an ID already claimed on an unmerged branch -----------------
    # Synthetic rather than pinned to live refs, deliberately. The known-bad here is the
    # build session's own pair of collisions (C-42 on the charging-passport PR branch,
    # D-086 on the essay branch), but pinning the fixture to those refs would repeat the
    # mistake the D-083 fixture already made once: it would go quiet the moment either
    # branch merged or was deleted, and a fixture that stops testing when the repository
    # moves is worse than none.
    mine = {'Decision Log.md': {'D-086': ['### D-086 — the entry this session drafted']},
            'Corrections Register.md': {'C-42': ['| C-42 | the row this session drafted']}}
    others = {
        'Decision Log.md': {
            'refs/heads/essay/uncanny-workforce': {
                'D-086': ['### D-086 – Execute the cornerstone content strategy'],
                'D-042': ['### D-042 — inherited, not newly minted']},
            'refs/heads/unrelated': {'D-042': ['### D-042 — inherited']}},
        'Corrections Register.md': {
            'refs/heads/pr/charging-passport': {
                'C-42': ['| C-42 | **A review finding is a claim that something is UNSOLVED']}},
    }
    claims = claimed_elsewhere(mine, others)
    both = sorted(k for v in claims.values() for k in v) == ['C-42', 'D-086']
    if not both:
        failed = True
    print(f"[{'ok ' if both else 'FAIL'}] id claims: a number already committed on an "
          'unmerged branch is reported before it is used — the build session made exactly '
          'this mistake twice, having numbered from origin/main')
    for name, per in claims.items():
        for cid, holders in per.items():
            print(f'         caught: {cid} held by {holders[0][0]}')

    # Negatives. The scan only ever speaks about IDs THIS branch minted; an inherited ID
    # sitting on fifty branches is ordinary shared history, not a claim.
    quiet = claimed_elsewhere(
        {'Decision Log.md': {'D-9999': ['### D-9999 — nobody else has this']}}, others)
    if quiet:
        failed = True
    print(f"[{'ok ' if not quiet else 'FAIL'}] id claims: a number nobody else holds is "
          'silent')
    for name, per in quiet.items():
        print(f'         wrongly flagged: {sorted(per)}')

    inherited = claimed_elsewhere({'Decision Log.md': {}}, others)
    if inherited:
        failed = True
    print(f"[{'ok ' if not inherited else 'FAIL'}] id claims: D-042, inherited and present "
          'on two other refs, is never reported — only newly minted IDs are scanned')

    # End-to-end against the real repository. Found live, not by unit-testing
    # claimed_elsewhere in isolation: after this branch's own commit landed, its own
    # `refs/heads/<branch>` pointed at HEAD and the full check_ids_against_all_refs()
    # call flagged this branch's IDs as "claimed" by itself. The synthetic fixtures above
    # never modelled a committed current branch, so they could not have caught it — this
    # assertion runs the real function against the real repository specifically because a
    # synthetic ref dictionary would repeat the same blind spot.
    own_branch = run_git(['symbolic-ref', '--quiet', '--short', 'HEAD'],
                         check=False).stdout.strip()
    if own_branch:
        _f, self_review, _s = check_ids_against_all_refs()
        self_flagged = [r for r in self_review if own_branch in r]
        ok = not self_flagged
        if not ok:
            failed = True
        print(f"[{'ok ' if ok else 'FAIL'}] id claims: this branch's own ref, "
              f"'{own_branch}', never flags its own committed IDs against itself")
        for h in self_flagged:
            print(f'         wrongly flagged: {h[:110]}')

    # Settled-topic collisions (2026-08-11 incident: commit 93c5c8f vs de73c61).
    # Fixture text is condensed from the real brief, keeping the exact phrases the
    # patterns match on, so a self-test failure here means the patterns rotted
    # against their own incident, not that the fixture drifted from it.
    topics_fixture = json.loads(SETTLED_TOPICS.read_text(encoding='utf-8'))

    # This fixture is the realistic shape, not the clean one: it reproduces the
    # real known-bad's own unrelated D-078 mention, so self-test asserts what
    # was actually proven against 93c5c8f (below) rather than a tidier case that
    # would hide the declared gap. Expected result is 1 finding, not 2 — the
    # D-078/movement collision is a KNOWN miss, asserted here so a future edit
    # that accidentally "fixes" it (or breaks the D-060 catch) is visible either
    # way, per this project's own rule that an unvalidated improvement is not
    # trusted until it is re-proven.
    known_bad = (
        '1. Domains and handles - the biggest untested gap. Check availability and '
        'current holder for the relevant domains and handles.\n'
        '3. Movement since April 2026 on the two live uses. Has either started '
        'building under the phrase? First-mover risk is the one thing that can '
        'change the D-078 position, and it changes with time.'
    )
    bad_hits = _scan_settled_topics([('known-bad.md', known_bad)], topics_fixture)
    ok = len(bad_hits) == 1  # D-060 caught; D-078 missed — declared gap, not a bug
    if not ok:
        failed = True
    print(f"[{'ok ' if ok else 'FAIL'}] settled topics: the real incident's "
          f'D-060/domains-and-handles collision is caught, and its D-078/movement '
          f'collision is a KNOWN miss (declared gap, not a bug) — expected 1 '
          f'finding, got {len(bad_hits)}')

    known_good_cited = (
        'Domains and handles are not in scope. D-060 already settled the publish '
        'home as scale100.co. Movement in the four prior uses was audited under '
        'D-078; re-checking within days measures nothing.'
    )
    good_hits = _scan_settled_topics([('known-good.md', known_good_cited)], topics_fixture)
    ok = len(good_hits) == 0
    if not ok:
        failed = True
    print(f"[{'ok ' if ok else 'FAIL'}] settled topics: citing D-060 and D-078 "
          f'alongside the same topic words passes — expected 0, got {len(good_hits)}')

    known_good_unrelated = (
        'Read the essay-citation-and-reference-plan and the human-register mapping '
        'before drafting section six of the essay.'
    )
    unrelated_hits = _scan_settled_topics(
        [('known-good-unrelated.md', known_good_unrelated)], topics_fixture)
    ok = len(unrelated_hits) == 0
    if not ok:
        failed = True
    print(f"[{'ok ' if ok else 'FAIL'}] settled topics: a brief on an unrelated "
          f'topic never fires — expected 0, got {len(unrelated_hits)}')

    print('\nself-test ' + ('FAILED — this checker cannot detect the defects it '
                            'claims to' if failed else
                            'passed — the checker fails on known-bad input'))
    return 1 if failed else 0


def cross_layer_trigger_check(report):
    """One trigger value must not appear under two spellings across the six
    registers. `EVERY MERGE` and `AT EVERY MERGE` are the same ritual written
    two ways, and a checklist grouped by trigger would list it twice — which is
    exactly the drift the README says grouping by trigger prevents (C-07).
    """
    seen = {}
    for layer, r in report.items():
        for value, spellings in r['stats'].pop('_trigger_values', {}).items():
            seen.setdefault(value, {})
            for s in spellings:
                seen[value].setdefault(s, []).append(layer)
    findings = []
    for value, spellings in sorted(seen.items()):
        if len(spellings) > 1:
            detail = '; '.join(f'{s} ({", ".join(sorted(set(ls)))})'
                               for s, ls in sorted(spellings.items()))
            findings.append(f"trigger '{value}' is written {len(spellings)} ways: {detail}")
    return findings


CLASS_COUNT_KEYS = ('class-a', 'class-b', 'class-c')
CLASS_READ_KEYS = ('class-a-reads', 'class-b-reads', 'class-c-reads')
CLASS_HEADING_RE = re.compile(r'^##\s+Class\s+([ABC])\b.*?\((\d+)\s+claims?', re.M)


def class_vocabulary_findings(parsed):
    """C-06, repaired by D-099 on 2026-08-17.

    The class letter is ONE construct across all seven registers — how complete
    the remedy is — and each register reads B and C in its OWN words. Before
    D-099 the README defined C as "nothing catches it", which is false for 15
    of the 33 Class C rows in the four aligned registers: IL-2A, IL-2C and
    AL-1B each name a real mechanism and are C because no remedy is COMPLETE,
    not because nothing sees them. Recovery made the same point from the other
    side — RL-2A is trivially detectable and irreversible.

    Four rules, and the fourth is the one that matters:

    1. Every register declares class-a/b/c counts and class-*-reads words.
       A register that does not declare its words invites the next page to
       borrow another register's, which is how the collapse spreads.
    2. The declared counts sum to `rows`, and match the rows themselves. This
       is the C-50 recurrence guard applied to these fields: a hand-maintained
       frontmatter count with nothing comparing it to canon is exactly how the
       README's Instruction row went stale and stayed stale.
    3. A register's declared words match the words its row cells actually use,
       so a register cannot declare `recoverable` and write `detected`.
    4. NO WORD MAY BE DECLARED FOR TWO DIFFERENT LETTERS across the registers.
       This is C-06's failure mode in miniature and the direct analogue of the
       cross-layer trigger-collision rule (C-24): one word meaning two things
       is precisely what made the letters non-comparable. `detected` means B
       everywhere or the framework cannot add its own columns up.

    Deliberately NOT checked: whether a register's chosen word is a GOOD name
    for its domain. That is an editorial judgement, and a check that guessed at
    it would fire on every legitimate rename.
    """
    findings, letter_of_word = [], {}
    for layer, (fm, sections) in sorted(parsed.items()):
        missing = [k for k in CLASS_COUNT_KEYS + CLASS_READ_KEYS if k not in fm]
        if missing:
            findings.append(
                f"{layer}: does not declare {', '.join(missing)} — the letter is shared "
                "across registers, the words are not, so each register must state its own (D-099)")
            continue
        try:
            counts = tuple(int(fm[k]) for k in CLASS_COUNT_KEYS)
            rows = int(fm['rows'])
        except ValueError:
            findings.append(f"{layer}: class-a/b/c and rows must be integers")
            continue
        if sum(counts) != rows:
            findings.append(f"{layer}: class-a+b+c={sum(counts)} but rows={rows} — "
                            "the declared split does not cover the register")
        reads = tuple(fm[k].strip().lower() for k in CLASS_READ_KEYS)
        for letter, word in zip('ABC', reads):
            letter_of_word.setdefault(word, {}).setdefault(letter, []).append(layer)

        # words and counts as the ROWS actually write them
        seen, tally = {}, {'A': 0, 'B': 0, 'C': 0}
        for s in sections:
            for r in s['rows']:
                m = re.match(r'^([ABC])\s+(\S+)', r.get('Outcome', '').strip())
                if m:
                    seen.setdefault(m.group(1), set()).add(m.group(2).lower())
                    tally[m.group(1)] += 1
        if not any(tally.values()):
            # Truth carries no Outcome column; its split lives in the Class headings
            # and its outcome words in a prose "Outcome: **word — ...**" line per
            # section. Both are read, because a register whose declaration is
            # compared against NOTHING is how truth-layer came to declare
            # `checkable`/`judgement` on 2026-08-17 — its section TITLES — when its
            # own outcome lines and its published spoke both say detected/survives.
            # A declaration nothing checks is a decoration.
            text = fm.get('_text', '')
            heads = dict((L, int(n)) for L, n in CLASS_HEADING_RE.findall(text))
            if heads:
                tally = {L: heads.get(L, 0) for L in 'ABC'}
            for L, word in zip('ABC', re.findall(r'Outcome:\s*\*\*(\w+)', text)):
                seen.setdefault(L, set()).add(word.lower())
        if any(tally.values()) and tuple(tally[L] for L in 'ABC') != counts:
            findings.append(
                f"{layer}: frontmatter says {counts} but the register itself says "
                f"{tuple(tally[L] for L in 'ABC')} — the hand-maintained count is stale (C-50 class)")
        for letter, word in zip('ABC', reads):
            got = seen.get(letter, set())
            if got and got != {word}:
                findings.append(
                    f"{layer}: class-{letter.lower()}-reads declares '{word}' but its rows write "
                    f"{sorted(got)} — declared vocabulary and row cells disagree")

    for word, letters in sorted(letter_of_word.items()):
        if len(letters) > 1:
            detail = '; '.join(f'{L} in {", ".join(sorted(set(ls)))}'
                               for L, ls in sorted(letters.items()))
            findings.append(
                f"class word '{word}' is declared for {len(letters)} different letters: {detail} "
                "— one word must mean one letter or no cross-register total is valid (C-06)")
    return findings


def check_class_vocabulary(layers=None):
    parsed = {}
    for layer in (layers or LAYERS):
        fm, sections, txt = parse(layer)
        fm['_text'] = txt
        parsed[layer] = (fm, sections)
    findings = class_vocabulary_findings(parsed)
    stats = {'registers': len(parsed),
             'readings': sorted({v[0].get('class-b-reads', '?') for v in parsed.values()})}
    return findings, [], stats


CORRECTIONS = PROJECT / 'Corrections Register.md'
INSTRUMENTS_DIR = PROJECT / 'instruments'
SETTLED_TOPICS = pathlib.Path(__file__).resolve().parent / 'settled-topics.json'


def _scan_settled_topics(files, topics):
    """Pure matcher: (path, text) pairs x topic list -> findings.

    Factored out of check_settled_topic_collisions so self-test can run it against
    in-memory fixtures without touching disk, on the same principle as
    check-preflight-search-depth.py's check_text().
    """
    findings = []
    for name, text in files:
        for topic in topics:
            tid = topic['id']
            if any(re.search(p, text, re.I) for p in topic['patterns']):
                if tid in text:
                    continue
                findings.append(
                    f'{name}: matches settled topic {tid} ({topic["note"]}) with no '
                    f'{tid} citation in the file'
                )
    return findings


def check_settled_topic_collisions(instruments_dir=None, mapping_path=None):
    """An instrument directs a fresh session to investigate a topic a Decision Log
    entry already settles, without citing it.

    2026-08-11 incident: a naming-test brief (commit 93c5c8f) asked a fresh session
    to check domain/handle availability, and to re-check "movement" on four prior
    uses of a phrase — despite the SAME authoring session having read D-060
    (publish home settled; no domain needed) and having itself run the movement
    audit one day earlier. The fact was retrieved and not applied when a
    differently-shaped task (authoring a brief for a future session) was performed
    later in the same session. Not a missing-fact failure — a task-switch failure.
    Corrected same day (commit de73c61) after a human caught it in chat; nothing
    mechanical had. Nearest register row: IL-5C ("a settled decision gets
    reopened"), graded C survives - open; its own stated remedy ("write the
    decision down") was already satisfied and the failure happened anyway, so this
    gate is the missing second half.

    This does not attempt general semantic collision detection — that is not
    decidable by regex. It maintains an explicit, small, growing map of
    settled-topic patterns (settled-topics.json), one entry per decision, on the
    same discipline as the settled-decision-restatement gate: a topic is covered
    only once someone adds its patterns, and coverage never silently regresses to
    "everything" or "nothing".

    DECLARED GAPS, both real, and (2) is not hypothetical — it is what happened
    when this gate was validated against its own founding incident's real text:
    (1) only topics explicitly present in settled-topics.json are checked — a
    brief can re-raise a settled decision phrased in a way none of that
    decision's patterns anticipate. (2) a citation anywhere in the file is
    accepted even if it is not actually responsive to the collision. The real
    known-bad artefact (93c5c8f) mentions "D-078" in an unrelated sentence
    ("First-mover risk is the one thing that can change the D-078 position") a
    few lines after the uncited movement-recheck directive, so this gate misses
    that half of its own incident — it catches the D-060/domains-and-handles
    collision on that same real file, and misses D-078/movement-since on it.
    Distinguishing a responsive citation from an incidental mention needs
    language understanding a regex cannot supply; tightening to a proximity or
    marker-word window was tried and rejected because it produced a false
    positive on the real known-good's own D-078 citation, which sits in
    parentheses with no marker word either ("individually audited on 10 August
    (D-078)"). Ship the honest version: catches more than nothing, misses a
    named real case, and says so.
    """
    instruments_dir = instruments_dir or INSTRUMENTS_DIR
    mapping_path = mapping_path or SETTLED_TOPICS
    findings, review, stats = [], [], {}
    if not mapping_path.exists():
        return [], [f'settled-topics.json not found at {mapping_path} — gate is unwired'], {}
    try:
        topics = json.loads(mapping_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        return [f'settled-topics.json does not parse: {e}'], [], {}
    stats['topics'] = len(topics)
    if not instruments_dir.exists():
        stats['files_scanned'] = 0
        return [], [], stats
    files = sorted(instruments_dir.glob('*.md'))
    stats['files_scanned'] = len(files)
    pairs = [(p.name, p.read_text(encoding='utf-8')) for p in files]
    findings = _scan_settled_topics(pairs, topics)
    stats['collisions'] = len(findings)
    return findings, review, stats


# ⟦instances=N gate=PATH validated=REF runs=PATH⟧ — the machine-readable tail of a
# correction row. The correction prose is unbounded, so the enforceable facts have to live
# somewhere a parser can reach without reading English.
#
# `runs=` was added 2026-08-12 by C-34, and it is the field that makes the rest mean
# anything. Until it existed this tool checked that a gate FILE EXISTED and had been
# validated — never that anything CALLED it. Both gated rows passed while their gate was
# invoked by nothing at all: not CI, not a hook, not a package script. The framework had
# already published the principle it was breaking — "naming a mechanism is not installing
# it" (registers/README.md) — and applied the install gate to provenance rows (C-02) while
# leaving its own bug list exempt. `runs=` must name a file that INVOKES the gate, and this
# tool greps that file for the gate's filename rather than taking the claim on trust.
META_RE = re.compile(r'⟦([^⟧]*)⟧')
GATE_NONE = re.compile(r'^none[-—_]', re.I)   # 'none—<reason>' is a legal, explicit answer


def parse_correction_meta(cell):
    m = META_RE.search(cell)
    if not m:
        return None
    out = {}
    for part in m.group(1).split():
        if '=' in part:
            k, v = part.split('=', 1)
            out[k.strip()] = v.strip()
    return out


def check_corrections(path=None):
    """C-31: a correction that has recurred must name an executable gate.

    The Corrections Register is the framework's own bug list, and until 2026-08-12 this
    tool did not read it at all — so the one file recording that unchecked prose decays
    was itself unchecked. The rule: one instance may be a one-off; a SECOND instance means
    the class recurs, and a recurring class is closed by a check that fails a run, not by
    better wording. `gate=` must point at a file that exists, or say `none—<reason>`.
    `validated=` must be present, because an unvalidated gate is prose with extra steps —
    building the first one exposed two defects in the gate itself, one of which silently
    hid two real findings.

    Absence is reported as review, not a finding: the public False Floors
    repo never carries the Corrections Register (public-repo/README.md's
    copy boundary), so a checkout that simply doesn't have the vault's bug
    list is a known, expected shape, not a defect this check can settle.
    """
    path = path or CORRECTIONS
    findings, review, stats = [], [], {}
    if not path.exists():
        return [], [f'Corrections Register not found at {path} — skipped '
                    '(expected outside the vault)'], {}
    text = path.read_text(encoding='utf-8')
    rows = [l for l in text.splitlines() if re.match(r'^\|\s*C-\d+\s*\|', l)]
    stats['rows'] = len(rows)
    counts = {'wired': 0, 'manual': 0, 'gated': 0, 'exempt': 0, 'single': 0, 'unmetered': 0,
              'unverifiable': 0}

    # Path resolution (C-34, revised after the first CI run of this check crashed on the
    # runner): 'second-brain/<p>' is THIS repo and resolves against the checker's own repo
    # root, so own-repo claims are verifiable on any machine including CI. Any other prefix
    # is a sibling repo, resolved against the repo root's parent. If the sibling repo root
    # is absent on this machine (CI has no ~/Developer), its rows are reported for review as
    # unverifiable-here rather than failed - the same honest-degradation shape as the
    # candidate receipt: never fail on what this machine cannot see, never claim it either.
    repo_root = pathlib.Path(__file__).resolve().parents[4]

    def resolve_ref(ref):
        if ref.startswith('/'):
            return pathlib.Path(ref), True
        first, _, rest = ref.partition('/')
        if first == 'second-brain':
            return repo_root / rest, True
        sibling_root = repo_root.parent / first
        return sibling_root / rest, sibling_root.exists()
    for line in rows:
        cid = split_row(line)[0].strip()
        meta = parse_correction_meta(line)
        if meta is None:
            counts['unmetered'] += 1
            review.append(f'{cid}: no ⟦instances=… gate=… validated=…⟧ block — instance '
                          'count unknown, so the C-31 gate rule cannot be applied')
            continue
        try:
            n = int(meta.get('instances', ''))
        except ValueError:
            findings.append(f'{cid}: ⟦instances=…⟧ missing or not an integer')
            continue
        gate = meta.get('gate', '')
        if n < 2:
            counts['single'] += 1
            continue
        if not gate:
            findings.append(f'{cid}: {n} instances and no gate= — a recurring class is '
                            'closed by a check that fails a run, not by rewording (C-31)')
            continue
        if GATE_NONE.match(gate):
            counts['exempt'] += 1
            continue
        target, checkable = resolve_ref(gate)
        if not checkable:
            counts['unverifiable'] += 1
            review.append(f'{cid}: gate={gate} is in a repo not present on this machine - '
                          'unverifiable here, verify where the sibling repo exists')
            continue
        if not target.exists():
            findings.append(f'{cid}: gate={gate} does not exist at {target}')
            continue
        if not meta.get('validated'):
            findings.append(f'{cid}: gate={gate} names no validated= reference — a gate is '
                            'not trusted until run against a known-bad input (C-31)')
            continue
        runs = meta.get('runs', '')
        if not runs:
            findings.append(f'{cid}: gate={gate} names no runs= — a gate nothing invokes is '
                            'prose with extra steps; name the CI job, hook or script that '
                            'calls it, or runs=none-<reason> to declare it manual (C-34)')
            continue
        if GATE_NONE.match(runs):
            counts['manual'] += 1
            continue
        invoker, checkable = resolve_ref(runs)
        if not checkable:
            counts['unverifiable'] += 1
            review.append(f'{cid}: runs={runs} is in a repo not present on this machine - '
                          'unverifiable here, verify where the sibling repo exists')
            continue
        if not invoker.exists():
            findings.append(f'{cid}: runs={runs} does not exist at {invoker}')
            continue
        called = pathlib.Path(gate).name
        if called not in invoker.read_text(encoding='utf-8', errors='ignore'):
            findings.append(f'{cid}: runs={runs} never mentions {called} — the named invoker '
                            'does not call the gate, so the wiring is asserted, not real (C-34)')
            continue
        counts['wired'] += 1
    stats.update(counts)
    return findings, review, stats


# ---------------------------------------------------------------------------
# C-43: an append-only log ID minted twice, and the merge that says nothing
# ---------------------------------------------------------------------------
# `Decision Log.md` and `Corrections Register.md` are append-only files sharing one
# sequential ID space, written concurrently from worktrees that each computed "the next
# free number" from a snapshot that went stale the moment a second session did the same.
#
# Why this needs a checker and not more care: **git does not raise a conflict for it.**
# Two branches appending different entries at different offsets merge cleanly, and the
# merged file carries the same ID twice with no marker, no warning and nothing to resolve.
# The failure is silent by construction — it surfaces only when a human reads the file and
# recognises a number they have seen before. Every instance so far was caught that way.
#
# Three collisions in five days, all recorded in D-085: the 11 August naming session cited
# D-078/D-080 while a concurrent session already held both, so its decisions reached no log
# at all for two days; and the 13 August False Floors entry was drafted as D-083 while the
# prior-art run independently landed D-083 *and* D-084 on origin/main the same day. D-085's
# own text concludes that "three independent collisions on the same file in five days is no
# longer a run of bad luck — it is evidence the append-only-log convention has no mechanical
# guard". This is that guard.
LOG_ID_PATTERNS = {
    'Decision Log.md': re.compile(r'^###\s+(?:Proposed\s+)?(D-\d+[a-z]?)\b'),
    'Corrections Register.md': re.compile(r'^\|\s*(C-\d+[a-z]?)\s*\|'),
}
# Tried in order. CI on a pull_request has origin/main; a local worktree may only have main.
BASE_REFS = ('origin/main', 'main')


def ids_in(text, pattern):
    """ID -> the heading or row lines that mint it, in file order."""
    found = {}
    for line in text.splitlines():
        m = pattern.match(line)
        if m:
            found.setdefault(m.group(1), []).append(line.strip())
    return found


def independently_minted(branch_ids, base_ids, fork_ids):
    """IDs created on BOTH sides since the fork point — the collision set.

    Set arithmetic, deliberately, rather than comparing entry titles. Title comparison
    cannot tell a collision from an ordinary edit, and a check that cries wolf on every
    reworded heading would be worse than no check. The fork point settles it without
    reading a word: an ID present when the branches diverged was minted once and edited
    afterwards by whoever touched it; an ID absent at the fork and present on both sides
    was minted twice, by two sessions that could not see each other.
    """
    return sorted((set(branch_ids) & set(base_ids)) - set(fork_ids))


def check_log_ids(base_refs=BASE_REFS, project=None, repo_root=None):
    """C-43: no log ID is minted twice — in the file, or across a merge.

    Two rules, because the collision has two shapes depending on when you look:

      1. DUPLICATE IN FILE — the post-merge shape. Once git has silently concatenated
         both appends, the ID appears twice in one file. This is what CI sees, because
         `actions/checkout` on a pull_request checks out the *merge* commit.
      2. INDEPENDENTLY MINTED — the pre-merge shape, and the leftmost catch point. The
         same ID exists on this branch and on the base, and existed on neither when they
         forked. Catches it in the worktree, before the merge that would hide it.

    Rule 1 needs no git and always runs. Rule 2 needs a reachable base ref; where there
    is none it reports for review rather than passing silently — an absent comparison is
    not a clean comparison.

    A LOG_ID_PATTERNS file that is simply absent is reported for review, not a finding:
    Decision Log.md and Corrections Register.md are vault bookkeeping, never copied into
    the public False Floors repo (public-repo/README.md's copy boundary), so their
    absence there is an expected shape, not this check catching a defect.
    """
    findings, review, stats = [], [], {}
    project = project or PROJECT
    repo_root = repo_root or pathlib.Path(__file__).resolve().parents[4]

    working = {}
    for name, pattern in LOG_ID_PATTERNS.items():
        path = project / name
        if not path.exists():
            review.append(f'{name}: not found at {path} — skipped (expected outside '
                          'the vault)')
            continue
        found = ids_in(path.read_text(encoding='utf-8'), pattern)
        working[name] = found
        stats[name.split()[0].lower()] = len(found)
        for cid, lines in sorted(found.items()):
            if len(lines) > 1:
                detail = ' | '.join(l[:70] for l in lines)
                findings.append(
                    f'{name}: {cid} is minted {len(lines)} times in one file — two '
                    f'entries claim one ID and git merged both without a conflict: {detail}')

    base_ref = None
    for ref in base_refs:
        if run_git(['rev-parse', '--verify', '--quiet', f'{ref}^{{commit}}'],
                   cwd=repo_root, check=False).returncode == 0:
            base_ref = ref
            break
    if base_ref is None:
        review.append(f'no base ref among {", ".join(base_refs)} — the cross-branch '
                      'collision rule did not run; duplicates within each file were still '
                      'checked')
        return findings, review, stats

    fork = run_git(['merge-base', 'HEAD', base_ref], cwd=repo_root, check=False)
    if fork.returncode != 0:
        review.append(f'no merge-base between HEAD and {base_ref} — the cross-branch '
                      'collision rule did not run')
        return findings, review, stats
    fork_sha = fork.stdout.strip()
    stats['base'] = base_ref
    stats['fork'] = fork_sha[:9]

    collided = 0
    for name, pattern in LOG_ID_PATTERNS.items():
        if name not in working:
            continue
        try:
            rel = (project / name).relative_to(repo_root).as_posix()
        except ValueError:
            review.append(f'{name}: {project} is outside the repository at {repo_root} — '
                          'the cross-branch rule cannot resolve it; duplicates within the '
                          'file were still checked')
            continue
        sides = {}
        for label, ref in (('base', base_ref), ('fork', fork_sha)):
            got = run_git(['show', f'{ref}:{rel}'], cwd=repo_root, check=False)
            sides[label] = ids_in(got.stdout, pattern) if got.returncode == 0 else {}
        for cid in independently_minted(working[name], sides['base'], sides['fork']):
            collided += 1
            here = working[name][cid][0][:70]
            there = sides['base'][cid][0][:70]
            findings.append(
                f'{name}: {cid} was minted independently on this branch and on {base_ref} '
                f'since they forked at {fork_sha[:9]} — renumber from {base_ref}, not from '
                f'this branch. here: {here} || {base_ref}: {there}')
    stats['collisions'] = collided
    return findings, review, stats


# ---------------------------------------------------------------------------
# D-087 follow-on: is this number already taken on a branch I cannot see?
# ---------------------------------------------------------------------------
# `check_log_ids` compares against the base, so it catches a collision at the merge.
# That is the last line of defence and it is not the cheapest place to catch it.
#
# The case for scanning every ref was made by this tool's own build session. Both new
# entries were deliberately numbered from `origin/main` rather than from the stale
# worktree — and both still collided, because C-42 was already committed on
# `pr/charging-passport-hullkey-updates` and D-086 on
# `essay/uncanny-workforce-drafting-2026-08-11`. Neither had merged, so neither was
# visible in the base. **`origin/main` is not the ID space; it is only the merged part
# of it.** The real space is main plus every unmerged branch plus every worktree that
# has written but not committed, and on 2026-08-13 that was 77 refs and 22 worktrees.
#
# Severity is deliberately `review`, not a finding. An ID claimed on some other ref is a
# real risk but not yet a defect — that branch may never merge. The certain defects (a
# duplicate in one file, an ID minted on both sides of a live fork) stay hard failures in
# `check_log_ids`. This one exists to save the renumber, not to be the last gate.
def claimed_elsewhere(my_new, ref_ids):
    """my_new: {file: {id: line}}. ref_ids: {file: {ref: {id: line}}} -> claims.

    Pure, so it can be tested without a repository. Returns
    {file: {id: [(ref, their_line), …]}} for every newly minted ID another ref holds.
    """
    claims = {}
    for name, mine in my_new.items():
        for cid in sorted(mine):
            holders = [(ref, ids[cid][0]) for ref, ids in ref_ids.get(name, {}).items()
                       if cid in ids]
            if holders:
                claims.setdefault(name, {})[cid] = holders
    return claims


def check_ids_against_all_refs(project=None, repo_root=None, base_refs=BASE_REFS):
    """Warn when a newly minted log ID is already claimed on any other ref or worktree.

    Costs nothing on the common path: if this branch has minted no new ID, it makes two
    cheap git calls and returns. The full scan only runs when there is something to
    protect, which is exactly when spending a few seconds is worth it.
    """
    findings, review, stats = [], [], {}
    project = project or PROJECT
    repo_root = repo_root or pathlib.Path(__file__).resolve().parents[4]

    base_ref = next((r for r in base_refs if run_git(
        ['rev-parse', '--verify', '--quiet', f'{r}^{{commit}}'],
        cwd=repo_root, check=False).returncode == 0), None)
    if base_ref is None:
        return findings, review, stats

    my_new, rels = {}, {}
    for name, pattern in LOG_ID_PATTERNS.items():
        path = project / name
        if not path.exists():
            continue
        try:
            rel = (project / name).relative_to(repo_root).as_posix()
        except ValueError:
            continue
        rels[name] = rel
        mine = ids_in(path.read_text(encoding='utf-8'), pattern)
        got = run_git(['show', f'{base_ref}:{rel}'], cwd=repo_root, check=False)
        theirs = ids_in(got.stdout, pattern) if got.returncode == 0 else {}
        fresh = {k: v for k, v in mine.items() if k not in theirs}
        if fresh:
            my_new[name] = fresh
    stats['minted_here'] = sum(len(v) for v in my_new.values())
    if not my_new:
        return findings, review, stats

    # Exclude the base ref AND the current branch's own ref. Once this branch has
    # committed, `refs/heads/<this-branch>` points at HEAD and trivially "claims" every
    # ID this call is checking — a guaranteed false positive on every run after the first
    # commit, not an edge case. Caught by running this against the branch's own post-merge
    # state rather than trusting the earlier synthetic self-test, which never modelled a
    # committed current branch.
    own = run_git(['symbolic-ref', '--quiet', '--short', 'HEAD'], cwd=repo_root,
                  check=False).stdout.strip()
    excluded = {f'refs/remotes/{base_ref}', f'refs/heads/{base_ref}'}
    if own:
        excluded |= {f'refs/heads/{own}', f'refs/remotes/origin/{own}'}
    refs = [r for r in run_git(['for-each-ref', '--format=%(refname)', 'refs/heads',
                                'refs/remotes'], cwd=repo_root).stdout.split()
            if r not in excluded]
    stats['refs_scanned'] = len(refs)

    ref_ids = {}
    for name, rel in rels.items():
        if name not in my_new:
            continue
        # One process resolves every ref to a blob id, then only the DISTINCT blobs are
        # read. Most branches never touch these files, so 77 refs collapse to a handful
        # of contents; done naively this was 77 subprocesses per file.
        specs = [f'{r}:{rel}' for r in refs]
        probe = subprocess.run(['git', 'cat-file', '--batch-check'], cwd=repo_root,
                               input='\n'.join(specs) + '\n', text=True,
                               capture_output=True)
        blob_of, lines = {}, probe.stdout.splitlines()
        for ref, line in zip(refs, lines):
            parts = line.split()
            if len(parts) == 3 and parts[1] == 'blob':
                blob_of[ref] = parts[0]
        cache = {}
        for blob in set(blob_of.values()):
            body = run_git(['cat-file', 'blob', blob], cwd=repo_root, check=False)
            cache[blob] = ids_in(body.stdout, LOG_ID_PATTERNS[name]) if body.returncode == 0 else {}
        stats[f'{name.split()[0].lower()}_distinct_versions'] = len(cache)
        ref_ids[name] = {ref: cache[blob] for ref, blob in blob_of.items()}

    # Uncommitted siblings. Refs only see committed work; a concurrent session that has
    # written its entry but not committed is invisible to the scan above, and that is the
    # window this whole class lives in.
    wt_paths = [l.split()[1] for l in run_git(
        ['worktree', 'list', '--porcelain'], cwd=repo_root).stdout.splitlines()
        if l.startswith('worktree ')]
    for name in my_new:
        for wt in wt_paths:
            p = pathlib.Path(wt) / rels[name]
            if not p.exists() or p.resolve() == (project / name).resolve():
                continue
            try:
                ids = ids_in(p.read_text(encoding='utf-8'), LOG_ID_PATTERNS[name])
            except OSError:
                continue
            ref_ids.setdefault(name, {})[f'worktree:{pathlib.Path(wt).name}'] = ids
    stats['worktrees_scanned'] = len(wt_paths)

    claims = claimed_elsewhere(my_new, ref_ids)
    stats['claimed_elsewhere'] = sum(len(v) for v in claims.values())
    for name, per_id in claims.items():
        for cid, holders in per_id.items():
            where = ', '.join(r for r, _ in holders[:3])
            more = f' (+{len(holders) - 3} more)' if len(holders) > 3 else ''
            review.append(
                f'{name}: {cid} is already claimed on {where}{more} — "'
                f'{holders[0][1][:80]}". Pick another number, or confirm those branches '
                'will never merge. origin/main is only the merged part of the ID space')
    return findings, review, stats


# ---------------------------------------------------------------------------
# --propose-row — the stage-1 oracle (C-31 class, fail-fix stage 1)
#
# WHY THIS EXISTS.  Every stage of the `fail-fix` pipeline has an oracle that can
# fail a run except the first one: pick the register and the row.  That stage is
# pure judgement, so its only detector was Sholto noticing and asking — and he
# asked three times, and was right three times.  Twice the failure was the same
# shape: a new C-row was drafted while an existing row already covered the class,
# and `grep` on the drafter's chosen keyword returned nothing because the register
# is written in abstract vocabulary ("it acted before it had the state") and the
# search was written in domain vocabulary ("resource", "capacity", "host").
# An empty keyword search was then read as absence.
#
# WHAT IT DOES.  Ranks every row of all seven layer registers AND the Corrections
# Register against proposed row text by IDF-weighted cosine similarity, so a
# narrative matches a narrative without either having to guess the other's nouns.
#
# THE HONEST LIMIT, STATED RATHER THAN IMPLIED — AND IT IS NARROWER THAN THE ONE
# THIS FEATURE WAS COMMISSIONED WITH.  The brief said "similarity cannot tell you
# the RIGHT row, only that you are about to duplicate one."  The first half holds:
# it has no model of unit, direction or counterfactual, which is what actually
# decides where a failure belongs.  THE SECOND HALF DID NOT SURVIVE MEASUREMENT.
# Three separate statistics were tested for a duplicate-vs-neighbour cut-off and
# every one was won by a known-GOOD fixture (figures beside the constants below),
# so this tool makes no duplicate claim at all.
#
# What it does is narrow 191 rows to 5 and refuse to pass until each of those 5
# has a written miss reason.  That is smaller than a classifier and it is the
# thing that was actually missing: in the incident this was built for, the correct
# row was one line away for an entire session and was never put on screen.  A
# clean run is the absence of ONE previously-observed error, not permission to
# mint.  Reading it as a verdict would reproduce C-48 — the search performed not
# testing the claim made — inside the tool built to stop it.
STOPWORDS = frozenset("""
a about above after again against all also am an and any are as at be because been before
being below between both but by can cannot could did do does doing down during each few for
from further had has have having he her here hers him his how i if in into is it its itself
just me more most my no nor not now of off on once only or other our out over own same she
should so some such than that the their them then there these they this those through to too
under until up very was we were what when where which while who whom why will with would you
your one two three onto per via not_defined none n_a
""".split())

# NO SIMILARITY THRESHOLD IS SHIPPED, AND THAT IS A MEASUREMENT, NOT AN OMISSION.
# Six fixtures (three real incidents whose correct row was settled by a human before
# this tool existed, three genuinely novel classes) were scored three ways, looking
# for any statistic that separates "you are duplicating a row" from "this row is
# merely a neighbour". All three failed, and each was won by a known-GOOD:
#     best score      known-bad 0.221–0.366   known-good up to 0.255
#     top/5th ratio   known-bad 1.21–1.69     known-good up to 1.73
#     gap rank 1→2    known-bad +0.002–0.058  known-good up to +0.071
# So no cut-off is defensible and none is offered. What the same six runs DO support
# is the ranking: the correct row landed inside the top five in three of three
# known-bads — worst position 2, out of a corpus of 191 — so the enforced obligation
# is rank-based. Read REQUIRE_REASONS_FOR_TOP_K as "the tool cuts 191 rows down to 5
# and makes you discharge all 5", which is the whole claim.
REQUIRE_REASONS_FOR_TOP_K = 5      # pooled view, kept for the printed context list
REQUIRE_REASONS_PER_GROUP = 3      # enforced: 3 layer rows + 3 C-rows, always
# Below this many usable words there is nothing to rank. Without the floor an empty
# or one-word proposal ranks nothing, owes no reasons, and exits as though it had
# been checked — a dead sensor reading as a pass, which is PL-3E's own failure mode.
MIN_PROPOSAL_TOKENS = 12
PROPOSE_TOP_N = 8

_WORD = re.compile(r"[a-z][a-z0-9_-]{2,}")


def _tokens(text):
    """Lowercase alphanumeric tokens, stopworded, crudely singularised.

    Deliberately not a stemmer: a stemmer would need a dependency, and the
    thing being matched is English prose written by the same small set of
    authors, where the plural 's' is the only inflection that matters much.
    """
    out = []
    for w in _WORD.findall(text.lower()):
        w = w.strip('-_')
        if len(w) < 3 or w in STOPWORDS:
            continue
        if len(w) > 4 and w.endswith('s') and not w.endswith('ss'):
            w = w[:-1]
        out.append(w)
    return out


def _strip_markup(s):
    s = re.sub(r'⟦[^⟧]*⟧', ' ', s)          # enforcement blocks
    s = re.sub(r'⟪[^⟫]*⟫', ' ', s)          # instance-of blocks
    s = re.sub(r'`[^`]*`', ' ', s)          # code spans: paths and commits, not prose
    s = re.sub(r'\[\[[^\]]*\]\]', ' ', s)   # wikilinks
    s = re.sub(r'[*_|]+', ' ', s)
    return s


def _headline(text, limit=110):
    m = re.search(r'\*\*(.+?)\*\*', text, re.S)
    h = (m.group(1) if m else text)
    h = ' '.join(_strip_markup(h).split())
    return h[:limit] + ('…' if len(h) > limit else '')


ROW_RE = {
    'instruction-layer': r'^\|\s*(IL-[0-9A-Za-z]+)\s*\|',
    'context-layer': r'^\|\s*(CL-[0-9A-Za-z]+)\s*\|',
    'authority-access-layer': r'^\|\s*(AL-[0-9A-Za-z]+)\s*\|',
    'recovery-layer': r'^\|\s*(RL-[0-9A-Za-z]+)\s*\|',
    'provenance-layer': r'^\|\s*(PL-[0-9A-Za-z]+)\s*\|',
    'truth-layer': r'^\|\s*(TL-[0-9A-Za-z]+)\s*\|',
}


def corpus(project=None, read=None):
    """Every row of all seven registers plus the Corrections Register.

    The seventh register (execution-capability) does NOT use the aligned
    layers' one-row-per-line table, so it is parsed by its own shape rather
    than being silently dropped — dropping it is the exact defect this whole
    feature exists to catch, one register lower down.
    """
    project = project or PROJECT
    read = read or (lambda rel: (project / rel).read_text(encoding='utf-8')
                    if (project / rel).exists() else None)
    records = []
    for layer, pat in ROW_RE.items():
        body = read(f'registers/{layer}.md')
        if body is None:
            continue
        rx = re.compile(pat)
        for line in body.splitlines():
            m = rx.match(line)
            if m:
                records.append({'id': m.group(1), 'source': f'registers/{layer}.md',
                                'text': _strip_markup(line)})
    # the seventh register: `## EC-nn – headline` followed by a field table whose
    # `property` row carries the falsifiable sentence
    ec = read('registers/execution-capability-layer.md')
    if ec:
        blocks = re.split(r'^##\s+(EC-[0-9]+)\s*[–—-]\s*', ec, flags=re.M)
        for i in range(1, len(blocks) - 1, 2):
            rid, body = blocks[i], blocks[i + 1]
            prop = re.search(r'^\|\s*`property`\s*\|\s*(.+?)\s*\|\s*$', body, re.M)
            head = body.splitlines()[0] if body.splitlines() else ''
            records.append({'id': rid, 'source': 'registers/execution-capability-layer.md',
                            'text': _strip_markup(head + ' ' + (prop.group(1) if prop else ''))})
    corr = read('Corrections Register.md')
    if corr:
        for line in corr.splitlines():
            m = re.match(r'^\|\s*(C-[0-9]+)\s*\|', line)
            if m:
                records.append({'id': m.group(1), 'source': 'Corrections Register.md',
                                'text': _strip_markup(line)})
    return records


def corpus_at(ref):
    """The corpus as it stood at a git ref, or None if that ref is unreachable.

    Validation fixtures rot in a way that is invisible: two of the three
    known-bads here were later FOLDED INTO the row they were supposed to find,
    so from 2026-08-21 the live Corrections Register contains those fixtures'
    own narratives verbatim. Ranked against the live file they still "pass" —
    by matching themselves. That is a fixture tripping the mechanism under
    test, and it converts a real check into a tautology silently.

    So recall is asserted against a PINNED corpus predating the fold, where the
    correct answer was established by a human and the fixture text is absent.
    The live corpus is still exercised, for the things it can honestly carry:
    that it parses, that stratification holds, that the ranker is not
    degenerate.
    """
    try:
        def read(rel):
            r = run_git(['show', f'{ref}:projects/agent-trust-framework/{rel}'],
                        cwd=PROJECT.parent.parent, check=False)
            return r.stdout if r.returncode == 0 else None
        recs = corpus(read=read)
        return recs or None
    except Exception:
        return None


def rank(proposed, records, top_n=PROPOSE_TOP_N):
    """Rank rows by the geometric mean of IDF cosine and query-IDF coverage.

    BOTH HALVES ARE LOAD-BEARING, AND THE MEASUREMENT THAT PROVED IT IS IN
    `--self-test-propose`.  Cosine alone over-scores SHORT rows: an unrelated
    fifteen-word layer row that happens to share two mid-frequency words beat the
    correct answer on the very first validation run.  Coverage alone over-scores
    LONG rows: C-31 and C-48 carry five instance narratives each and cover a
    large fraction of almost any query's vocabulary by chance.  The two biases
    point opposite ways, so their geometric mean suppresses both, and it moved
    the correct answer from "first by 0.03" to "first by a clear margin" on
    every fixture.
    """
    docs = [_tokens(r['text']) for r in records]
    q = _tokens(proposed)
    if not q or not any(docs):
        return []
    N = len(docs)
    df = {}
    for d in docs:
        for t in set(d):
            df[t] = df.get(t, 0) + 1

    def idf(t):
        return math.log((N + 1) / (df.get(t, N) + 1)) + 1.0

    def vec(toks):
        tf = {}
        for t in toks:
            tf[t] = tf.get(t, 0) + 1
        v = {t: (1.0 + math.log(c)) * idf(t) for t, c in tf.items() if t in df}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {t: x / norm for t, x in v.items()}

    qv, qs = vec(q), set(q)
    q_mass = sum(idf(t) for t in qs if t in df) or 1.0
    scored = []
    for rec, d in zip(records, docs):
        dv = vec(d)
        cos = sum(w * dv.get(t, 0.0) for t, w in qv.items())
        cov = sum(idf(t) for t in qs if t in set(d)) / q_mass
        scored.append((math.sqrt(max(cos, 0.0) * max(cov, 0.0)), rec))
    scored.sort(key=lambda x: (-x[0], x[1]['id']))
    return scored[:top_n]

def rank_stratified(proposed, records, per_group=None):
    """Rank the layer registers and the Corrections Register SEPARATELY.

    WHY, MEASURED.  A single pooled ranking is dominated by the Corrections
    Register and it is not close: C-rows are 500-1500 words of narrative prose,
    layer rows are about 25 words of table cell, and every similarity measure
    tried rewards the long document.  Across nine validation fixtures the pooled
    ranking gave layer rows 7% of the top-five slots while they are 71% of the
    corpus — a tenfold suppression.

    That is not a cosmetic bias.  The incident this whole feature was built for
    was a LAYER row being missed: `IL-4C` ("it acted before it had the state")
    was never looked at, and a pooled ranker would have kept it off the screen
    for the same reason the original session did.  A tool that reproduces the
    failure it was built to catch is worse than none, so length is only ever
    compared between comparable documents, and each group surfaces its own
    nearest rows.

    Returns [(group_label, [(score, record), ...]), ...].
    """
    per_group = per_group or REQUIRE_REASONS_PER_GROUP
    layer = [r for r in records if not r['id'].startswith('C-')]
    corr = [r for r in records if r['id'].startswith('C-')]
    out = []
    if layer:
        out.append(('seven layer registers', rank(proposed, layer, per_group)))
    if corr:
        out.append(('Corrections Register', rank(proposed, corr, per_group)))
    return out


def parse_miss_reasons(path):
    """`ID: reason` lines. Blank lines and `#` comments ignored."""
    reasons = {}
    for line in pathlib.Path(path).read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        m = re.match(r'^\*?\s*((?:IL|CL|AL|RL|PL|TL|EC|C)-[0-9A-Za-z]+)\s*[:\-–]\s*(.+)$', line)
        if m:
            reasons[m.group(1)] = m.group(2).strip()
    return reasons


# A reason must say something. These are the evasions actually seen in review
# prose, and a reason that is only one of them is not a reason.
_EMPTY_REASON = re.compile(
    r'^(n/?a|none|no|nope|misses|does ?n.?t (apply|fit|match)|not (relevant|related|applicable)|'
    r'different|unrelated|other|-+|\.+)\.?$', re.I)
MIN_REASON_CHARS = 25


def check_propose_row(proposed, miss_path=None, top_n=PROPOSE_TOP_N, project=None,
                      per_group=REQUIRE_REASONS_PER_GROUP):
    """Return (findings, review, stats, groups, pooled). Read-only; it never writes.

    THE ENFORCED RULE IS RANK-BASED AND STRATIFIED, NOT SCORE-BASED. See the
    constants above for the three statistics that failed to separate a duplicate
    from a neighbour, and rank_stratified for the tenfold layer-row suppression
    that killed the pooled list. Scores order one group's results; they are not
    comparable between groups or between runs and nothing treats them as a
    verdict.
    """
    records = corpus(project)
    findings, review = [], []
    if len(_tokens(proposed)) < MIN_PROPOSAL_TOKENS:
        findings.append(
            f'the proposed row is only {len(_tokens(proposed))} usable words — under '
            f'{MIN_PROPOSAL_TOKENS} there is nothing to rank, and a silent pass here '
            f'would be the worst possible answer. Paste the drafted row.')
        return findings, review, {'corpus': len(records)}, [], []
    if not records:
        findings.append('no register rows were parsed — the corpus is empty, so a clean '
                        'result here would mean nothing')
        return findings, review, {'rows': 0}, [], []
    groups = rank_stratified(proposed, records, per_group)
    pooled = rank(proposed, records, top_n)
    owed = [r for _, rows in groups for _, r in rows]
    stats = {'corpus': len(records), 'groups': len(groups), 'reasons-owed': len(owed)}
    if miss_path is None:
        review.append(f'{len(owed)} row(s) each need a written miss reason before a new ID '
                      f'is minted: ' + ', '.join(r['id'] for r in owed))
        return findings, review, stats, groups, pooled
    reasons = parse_miss_reasons(miss_path)
    for label, rows in groups:
        for s, r in rows:
            got = reasons.get(r['id'])
            if not got:
                findings.append(f"{r['id']} is among the {per_group} nearest rows in the "
                                f'{label} ({s:.3f}) and has no miss reason in {miss_path}')
            elif _EMPTY_REASON.match(got) or len(got) < MIN_REASON_CHARS:
                findings.append(f"{r['id']} miss reason is not a reason: {got!r}")
    stats['reasons'] = len(reasons)
    return findings, review, stats, groups, pooled


# The ref recall is measured against: current origin/main as of 2026-08-20, one day
# before C-59 and C-60 were folded into C-48 and their narratives — which are two of
# the three fixtures below — entered the live register verbatim.
PINNED_CORPUS_REF = 'ae5ad8350'

PROPOSE_KNOWN_BAD = [
    ('T-0078 host capacity — became C-31 instance 5', 'C-31',
     # paraphrase: what a drafter types into the tool
     """The orchestrating seat wrote the run's own preconditions into the plan document
     that morning - a healthy host, and any run whose instrument control fails is
     discarded whole, passes included - and that afternoon ran the concurrency harness
     five times without once checking host state. Capacity was read only on the fifth
     run: five stacks, 67 running containers, load average 67 on ten cores, swap at 94
     per cent, the kernel killing processes. The rule was not missing and not
     unreachable. It was written by the failing seat, in a document that seat authored,
     hours earlier. The substrate was attention.""",
     # drafted row: what the skill pastes once the row is written out
     """A precondition written by the acting seat that morning did not bind that same
     seat that afternoon. The Phase B preconditions were authored into the plan document
     itself - a healthy host, and any run whose A6 instrument control fails is discarded
     whole, passes included - and section H of the concurrency harness was then run five
     times with no host check at any point. Host state was measured only after the fifth
     run: five Supabase stacks, 67 running containers, a one-minute load average of 67 on
     ten cores, swap at 94 per cent, and the kernel SIGKILLing processes. As in the
     earlier instances the rule was not missing, not unreachable and not un-interposed;
     it was in context, authored by the seat that broke it, hours earlier, and the
     substrate the rule relied on was attention. The consequence is sharper than mere
     waste: a killed docker exec means the SQL never reaches the database, so a cell
     asking whether a lock was acquired truthfully answers that no lock is held, which
     reads as a product defect. An infrastructure failure wearing a finding's clothes,
     surviving review because it looks exactly like what review is for. It came within
     one step of shipping two false security findings. The repair owed is an executable
     gate for the class in this new domain, validated in both directions before being
     trusted."""),
    ('Lovelace MCP reported unavailable — C-59, whose own text names C-48', 'C-48',
     """A capability was reported unavailable, three times into durable artifacts, on the
     strength of one tool-registry search that could not have answered the question
     asked. Needing to edit a ticket, the session ran one tool search for the MCP tools,
     got nothing, and concluded they were unavailable. It wrote that conclusion into a
     commit message, a design record and a pull-request body as settled fact, and worked
     around it. It was wrong: the server was healthy and had simply been switched off by
     one line of local settings. The search performed did not test the claim made.""",
     """A capability was reported unavailable, three times into durable artifacts, on the
     strength of one tool-registry search that could not have answered the question
     asked. Needing to edit a Lovelace ticket, the session ran one ToolSearch for the
     Lovelace MCP tools, got nothing back, and concluded the tools were unavailable. It
     then wrote that conclusion into a commit message, a design record and a pull-request
     body as settled fact, and built a workaround on top of it. The conclusion was wrong.
     The server was healthy - probed later over stdio it returned its serverInfo and its
     full tool list - and had simply been switched off by one line in a local settings
     file listing it as a disabled server. What made the error survive is that the search
     performed did not test the claim made: the registry search answers whether these
     tools are registered in this session, while the claim asserted was that the
     capability was unavailable, which is a statement about why. Nothing was checked
     between the two. The disguise is worth recording: hooks are declared by a separate
     mechanism, so the session-start digest and the other guards all kept running
     normally and every visible signal said the project was correctly wired. The cost was
     not the workaround, it was the durability - three artifacts now carry a false
     negative claim about a capability."""),
    ('settings.json asserted committed — C-60', 'C-49',
     """A claim about repository state was asserted without running the one command that
     settles it, and the user approved a piece of work on the strength of it. The session
     described a file as committed twice in one message. Only when a clean worktree was
     cut did git ls-files return zero and git check-ignore show the whole directory
     excluded. The proposed work was impossible as described and the approval had already
     been given. The oracle was one command and was never run.""",
     """A claim about repository state was asserted without running the one command that
     settles it, and the user approved a piece of work on the strength of it. Having just
     diagnosed a neighbouring failure, the session proposed the durable fix as adding a
     key to the committed settings file, and described that file as committed twice in
     one message. Only when a clean worktree was cut did git ls-files against that
     directory return zero, and git check-ignore reveal the directory excluded wholesale
     by a gitignore line commented as machine-specific local session config. The proposed
     change was impossible as described, and the approval had already been given. The
     distinguishing feature against an ordinary mistake is that the oracle was one
     command and was never run: git ls-files costs nothing, and the session inferred
     committed from the file existing at a path that looked tracked. Two of the same
     session's other assertions about the same directory were correct, which is what made
     the third feel safe. The severity is not lower because the claim did not merely sit
     in prose - it consumed a human decision."""),
]

PROPOSE_KNOWN_GOOD = [
    ('locale key drift', """
     Two independent translation files for the same locale drifted apart because each was
     edited by a different session and no check compares the key sets. A missing key falls
     back to English silently at render time, so the user sees a half-translated screen
     and nothing in the build reports it."""),
    ('migration numbered against the wrong baseline', """
     A database migration renumbered itself against the wrong baseline: the number was
     chosen to beat the highest migration on the main branch, but the staging environment
     had already applied a higher one. It passed every pull-request check and merged
     cleanly, then failed at deploy time, leaving it merged but never shipped."""),
    ('hand-edited generated stylesheet', """
     Colour values were hand-edited into a generated stylesheet instead of the token
     source file, so the next token generation silently reverted them. Designers reported
     the change landing and then disappearing a week later with no commit that removed
     it."""),
]


def self_test_propose():
    """Prove the stage-1 oracle still finds the row, and that its gate can fail.

    Six assertions, each limited to what the fixtures can actually carry:

      1. RECALL — each known-bad puts its known-correct C-row inside the top
         REQUIRE_REASONS_PER_GROUP of the Corrections group, so the drafter is
         FORCED to write why it misses. Asserted twice per fixture, on a ~50-word
         paraphrase (what someone types) and on the ~165-word drafted row (what
         the skill pastes): on paraphrases the correct row measurably falls to
         position 2, so a top-1 assertion would be a check fitted to the longer
         input.
      2. STRATIFICATION — every run surfaces layer rows. The pooled ranking gave
         them 7% of top-five slots against 71% of the corpus, and the row the
         original incident missed was a layer row, so this one is load-bearing.
      3. NOT DEGENERATE — the fixtures do not all rank the same row first. A
         ranker broken by a tokeniser change collapses onto the longest row in
         the corpus, and assertion 1 cannot see that because C-31 IS the longest.
      4. THE DECLARED WEAKNESS IS STILL THE DECLARED WEAKNESS — IL-4C ranks top-3
         of the layer group on abstract phrasing. If that ever fails, the
         narrative-vs-abstract limit printed by _limits() has changed shape and
         the printed text is now wrong.
      5. The gate FAILS on a reason file with no reasons, and on one of evasions.
      6. The gate PASSES on a complete reason file — a check that fails on
         everything guards nothing (rule 2 of the fail-fix skill).

    The known-goods carry no pass/fail. They exist because their measurements are
    the disproof of the score-threshold idea, recorded beside the constants they
    killed.
    """
    import tempfile
    fails, firsts, layer_seen = [], [], 0
    records = corpus()
    n_layer = sum(1 for r in records if not r['id'].startswith('C-'))
    print(f'live corpus: {len(records)} rows ({n_layer} layer/EC + '
          f'{len(records)-n_layer} corrections)')
    if len(records) < 100 or n_layer < 100:
        fails.append(f'corpus has regressed: {len(records)} rows, {n_layer} layer rows')
    K = REQUIRE_REASONS_PER_GROUP

    pinned = corpus_at(PINNED_CORPUS_REF)
    if pinned is None:
        fails.append(f'the pinned validation corpus {PINNED_CORPUS_REF} is unreachable, '
                     f'so recall could not be tested against a corpus free of the '
                     f'fixtures\' own text — this is a FAILURE, not a skip')
        pinned = records
    else:
        print(f'pinned corpus at {PINNED_CORPUS_REF}: {len(pinned)} rows — recall is '
              f'asserted against this, not the live file')
        # Prove the fixtures cannot match themselves at that ref. PROBE THE RAW FILE,
        # not the parsed corpus: _strip_markup removes backticked code spans, and the
        # distinctive probe terms are all in backticks, so probing the parsed text
        # found nothing at ANY ref — a guard that passed on everything, caught only by
        # running it against a ref where it was supposed to fail.
        raw = run_git(['show', f'{PINNED_CORPUS_REF}:projects/agent-trust-framework/'
                       'Corrections Register.md'], cwd=PROJECT.parent.parent,
                      check=False).stdout
        # One probe per fixture, and ALL THREE are now needed: C-59/C-60 were folded
        # into C-48 on 2026-08-21, and C-31 gained its instance-5 narrative when #148
        # merged the same day. Every known-bad below is present verbatim in the LIVE
        # register, so the pin is the only thing keeping recall from measuring itself.
        hits = [x for x in ('disabledMcpjsonServers', 'ToolSearch', 'check-ignore',
                            'serverInfo', 'SIGKILL', '67 running containers',
                            'swap at 94') if x in raw]
        if hits:
            fails.append(f'the pinned corpus at {PINNED_CORPUS_REF} already contains '
                         f'{hits} — a fixture can match its own text there, so recall '
                         f'would be measuring nothing. Move PINNED_CORPUS_REF to a ref '
                         f'before that row was written.')
        else:
            print('  [PASS] no fixture self-match at the pinned ref '
                  '(raw file probed, not the stripped corpus)')

    for name, want, short, full in PROPOSE_KNOWN_BAD:
        for form, text in (('paraphrase', short), ('drafted row', full)):
            groups = rank_stratified(text, pinned)
            flat = {g: [r['id'] for _, r in rows] for g, rows in groups}
            corr = flat.get('Corrections Register', [])
            lay = flat.get('seven layer registers', [])
            layer_seen += len(lay)
            firsts.append(corr[0] if corr else '(none)')
            pos = corr.index(want) + 1 if want in corr else None
            ok = pos is not None
            print(f"  [{'PASS' if ok else 'FAIL'}] known-bad ({form:<11}) {name}\n"
                  f'           {want} at position {pos} of top {K}; '
                  f'layer rows offered: {lay}')
            if not ok:
                fails.append(f'known-bad {name!r} ({form}): {want} not in the top {K} '
                             f'of the Corrections group — got {corr}')
            if len(lay) != K:
                fails.append(f'known-bad {name!r} ({form}): {len(lay)} layer rows '
                             f'offered, expected {K} — stratification has broken')

    for name, text in PROPOSE_KNOWN_GOOD:
        groups = rank_stratified(text, records)
        flat = {g: [(s, r['id']) for s, r in rows] for g, rows in groups}
        corr = flat.get('Corrections Register', [])
        lay = flat.get('seven layer registers', [])
        layer_seen += len(lay)
        firsts.append(corr[0][1] if corr else '(none)')
        print(f"  [    ] known-good {name}: nearest C-row {corr[0][1]} at {corr[0][0]:.3f}, "
              f'nearest layer row {lay[0][1]} (recorded, not asserted)')
        if len(lay) != K:
            fails.append(f'known-good {name!r}: {len(lay)} layer rows offered, expected {K}')

    print(f"  [{'PASS' if layer_seen else 'FAIL'}] stratification: {layer_seen} layer-row "
          f'slots offered across 9 fixtures (pooled ranking gave 3)')

    distinct = len(set(firsts))
    ok = distinct >= 4
    print(f"  [{'PASS' if ok else 'FAIL'}] not degenerate: {distinct} distinct rows came "
          f'first across {len(firsts)} fixtures')
    if not ok:
        fails.append(f'ranking has collapsed: only {distinct} distinct rows came first '
                     f'across {len(firsts)} fixtures ({sorted(set(firsts))})')

    abstract = ('The agent acted before it had the state. It launched the run without ever '
                'reading the host capacity, so the change was built on a reading it never '
                'took, and the required state was absent at the moment it acted.')
    lay_ids = [r['id'] for _, r in rank_stratified(abstract, records)[0][1]]
    ok = 'IL-4C' in lay_ids
    print(f"  [{'PASS' if ok else 'FAIL'}] declared weakness unchanged: abstract phrasing "
          f'puts IL-4C in the layer top {K} — got {lay_ids}')
    if not ok:
        fails.append('IL-4C no longer surfaces on abstract phrasing; the narrative-vs-'
                     'abstract limitation printed by _limits() no longer describes the tool')

    text = PROPOSE_KNOWN_BAD[0][3]
    owed = [r['id'] for _, rows in rank_stratified(text, records) for _, r in rows]
    with tempfile.TemporaryDirectory() as d:
        for label, body, want_n in (
            ('empty reason file', '# no reasons at all\n', len(owed)),
            ('evasive reasons', '\n'.join(f'{i}: n/a' for i in owed) + '\n', len(owed)),
            ('complete reason file', '\n'.join(
                f'{i}: differs on unit and direction — a different mechanism entirely, '
                f'checked against that row\'s own text' for i in owed) + '\n', 0),
        ):
            f = pathlib.Path(d) / 'r.txt'
            f.write_text(body)
            found = check_propose_row(text, str(f))[0]
            ok = len(found) == want_n
            print(f"  [{'PASS' if ok else 'FAIL'}] gate on {label}: {len(found)} findings, "
                  f'expected {want_n}')
            if not ok:
                fails.append(f'gate on {label}: {len(found)} findings, expected {want_n}')

    print()
    for x in fails:
        print('  [FAIL]', x)
    print('clean' if not fails else f'{len(fails)} failures')
    return 1 if fails else 0

def _argval(flag, default=None):
    if flag in sys.argv:
        i = sys.argv.index(flag)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


def propose_row_cli():
    """Stage-1 duplicate oracle. Exit 0 clean, 1 with findings, 2 = reasons owed."""
    proposed = _argval('--propose-row')
    if not proposed:
        print('--propose-row needs the proposed row text (or `-` to read stdin)')
        return 1
    if proposed == '-':
        proposed = sys.stdin.read()
    miss = _argval('--miss-reasons')
    top_n = int(_argval('--top', PROPOSE_TOP_N))
    findings, review, stats, groups, pooled = check_propose_row(proposed, miss, top_n)
    if '--json' in sys.argv:
        print(json.dumps({'stats': stats, 'findings': findings, 'review': review,
                          'groups': [{'group': g,
                                      'rows': [{'score': round(s, 4), **r} for s, r in rows]}
                                     for g, rows in groups]}, indent=1, ensure_ascii=False))
        return 1 if findings else (2 if review else 0)
    print(f"[propose-row] {json.dumps(stats, ensure_ascii=False)}")
    for label, rows in groups:
        print(f'\n  {label} — nearest {len(rows)}, each owes a miss reason:')
        for n, (s, r) in enumerate(rows, 1):
            print(f"   {n}. {s:.3f}  {r['id']:<7} {r['source']:<44} "
                  f"{_headline(r['text'], 82)}")
    if pooled:
        print(f'\n  (context only — pooled across both groups, NOT the enforced set; the '
              f'pooled\n  order is dominated by row length, which is why it is not what is '
              f'enforced)')
        for n, (s, r) in enumerate(pooled[:top_n], 1):
            print(f"   {n:>2}. {s:.3f}  {r['id']:<7} {_headline(r['text'], 96)}")
    print()
    for f in review:
        print(f'         ? {f}')
    for f in findings:
        print(f'         - {f}')
    if findings:
        return 1
    if review:
        print(f'\n  Not a pass. Write a miss reason for each row above and re-run with\n'
              f'  --miss-reasons <file> (lines of `C-31: why it misses`).')
        _limits()
        return 2
    print('\n  Every nearest row has a written miss reason.')
    _limits()
    return 0


def _limits():
    print("""
  WHAT THIS DID NOT DO — read before reporting it as clearance:
   * It ranks; it does not classify. No score printed means "duplicate". Three
     candidate cut-offs were tested and every one was won by a NOVEL fixture.
   * It cannot tell you the RIGHT row. Unit, direction and counterfactual decide
     that and it models none of them.
   * On the layer registers it is weak against narrative input, measured: IL-4C
     ranks 1st of 136 when the proposal is phrased abstractly ("it acted before
     it had the state") and 26th when the same incident is phrased as a story.
     Layer rows are terse abstractions; incident text is narrative. That is the
     SAME vocabulary mismatch this tool exists to fix, surviving inside it.
   * Therefore the three layer rows above are a floor, not a search. The full
     enumeration — every row title, read — is still what covers the layer
     registers, and this output never replaces it.""")

def main():
    if '--self-test-propose' in sys.argv:
        return self_test_propose()
    if '--self-test' in sys.argv:
        return self_test()
    if '--propose-row' in sys.argv:
        return propose_row_cli()
    strict = '--strict' in sys.argv
    report = {}
    for layer in LAYERS:
        findings, stats, review = check(layer)
        report[layer] = {'findings': findings, 'review': review, 'stats': stats}
    cross = cross_layer_trigger_check(report)
    if cross:
        report['(cross-layer)'] = {'findings': [], 'review': cross, 'stats': {}}
    layer_rows = {}
    for layer in LAYERS:
        _, sections, _ = parse(layer)
        layer_rows[layer] = [r for s in sections for r in s['rows']]
    first_party, corpus, coded = evidence_receipts()
    efind, erev, estats = check_evidence(layer_rows, first_party, corpus, coded)
    report['(evidence)'] = {'findings': efind, 'review': erev, 'stats': estats}
    findings, stats = check_generated_views()
    report['(generated views)'] = {
        'findings': findings, 'review': [], 'stats': stats,
    }
    cfind, crev, cstats = check_corrections()
    report['(corrections)'] = {'findings': cfind, 'review': crev, 'stats': cstats}
    lfind, lrev, lstats = check_log_ids()
    report['(log ids)'] = {'findings': lfind, 'review': lrev, 'stats': lstats}
    sfind, srev, sstats = check_ids_against_all_refs()
    report['(id claims)'] = {'findings': sfind, 'review': srev, 'stats': sstats}
    tfind, trev, tstats = check_settled_topic_collisions()
    report['(settled topics)'] = {'findings': tfind, 'review': trev, 'stats': tstats}
    vfind, vrev, vstats = check_class_vocabulary()
    report['(class vocabulary)'] = {'findings': vfind, 'review': vrev, 'stats': vstats}
    failed = any(r['findings'] for r in report.values())
    needs_review = any(r['review'] for r in report.values())
    if '--json' in sys.argv:
        print(json.dumps(report, indent=1, ensure_ascii=False))
    else:
        for layer, r in report.items():
            mark = 'FAIL' if r['findings'] else ('rvw ' if r['review'] else ' ok ')
            print(f"[{mark}] {layer}  {json.dumps(r['stats'], ensure_ascii=False)}")
            for f in r['findings']:
                print(f'         - {f}')
            for f in r['review']:
                print(f'         ? {f}')
        if needs_review:
            print('\n? = needs a human call, not a defect the tool can settle. '
                  'Run --strict to fail on these too.')
    return 1 if failed or (strict and needs_review) else 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""check-ec-rows - the Execution and Capability row schema, made executable.

Checks every EC row in the register file against the contract
(research/19-execution-capability-contract-2026-08-09.md), section 2.3's controlled
vocabulary and field grammar and section 2.6's nine result/residual invariants.

    python3 registers/tools/check-ec-rows.py registers/execution-capability-layer.md

Exit 0 clean, 1 with a finding list. Read-only; it never writes.

NOT WIRED. This is not run by check-registers.py, not run by any hook, and not run in
CI. check-registers.py hard-codes the six aligned layers and models their column set,
which the EC schema does not share, so folding this in is a real change to that gate
rather than a line of configuration. Until someone does that, this script only binds
when a human runs it, and it should be described that way and not as an enforced gate.

Validated 2026-08-19 before first use, against eleven deliberately broken copies of the
register: closed_scoped on a row whose next action is `install` (invariant 5, the same
shape as C-02); a `fail` row with no escalation and a `fail` row with a softened
residual (invariant 7); an invented `assessment_kind`; `pass` on unverified evidence
(invariant 1); `requirement_ref: none` under a non-discovered origin; `coverage_run`
above `coverage_total`; `finite_enumerated` with no integer total; `oracle_ref: none`;
a dropped field; and an id that fails the `EC-[0-9]{2,}` grammar. All eleven were
caught, and the unmutated file stayed clean. Added when EC-06 and EC-07 were derived,
because a twenty-eight-field schema with nine cross-field invariants is not something a
reader reliably checks by eye - which is the whole reason the invariants are written
down as invariants.
"""
import re, sys, pathlib

V = {
 'assessment_kind': {'behaviour','capability','dependency','performance','resilience','compatibility','human_judgement'},
 'requirement_origin': {'specified','derived_invariant','regression','discovered','decision'},
 'criticality': {'S1','S2','S3','S4'},
 'oracle_kind': {'executable_reference','invariant','differential','formal_proof','measurement_threshold','human_judgement'},
 'coverage_kind': {'finite_enumerated','finite_generated','scenario_bounded','sampled','open'},
 'coverage_basis': {'exhaustive','random','risk_based','mutation_based','fault_injection','scenario','human_review'},
 'method': {'prevention','static_analysis','exhaustive_test','sampled_test','mutation_test','fault_injection','formal_proof','measurement','human_review','none'},
 'control_status': {'in_force','available_not_in_force','designed','none','unknown'},
 'result': {'pass','fail','partially_assessed','not_assessed'},
 'residual': {'closed_scoped','open_known','open_coverage','open_general','not_established'},
 'evidence_state': {'valid','invalid','stale','missing','unverified'},
 'next_action_kind': {'none','install','activate','repair','expand_coverage','reassess','risk_accept'},
 'trigger_kind': {'done','on_change','per_commit','event','interval','manual'},
 'escalation_state': {'none','owner_review','block','risk_acceptance','incident'},
 'escalation_trigger': {'none','property_failed','evidence_invalid','required_scope_unassessed','capability_absent','residual_above_appetite'},
}
FIELDS = ['id','incident_id','unit_of_work','assessment_kind','subject_ref','property',
 'requirement_origin','requirement_ref','criticality','oracle_kind','oracle_ref','coverage_kind',
 'coverage_basis','coverage_total','coverage_run','coverage_limit','method','mechanism_ref',
 'control_status','result','residual','evidence_state','receipt_ids','owner','next_action_kind',
 'trigger_kind','trigger_value','escalation_state','escalation_trigger','escalation_to']

text = pathlib.Path(sys.argv[1]).read_text()
# a row is a field table whose first data line is | `id` | EC-nn |
rows, cur = [], None
for line in text.splitlines():
    m = re.match(r'^\|\s*`([a-z_]+)`\s*\|\s*(.*?)\s*\|\s*$', line)
    if not m:
        continue
    k, v = m.group(1), m.group(2)
    if k == 'id':
        cur = {}; rows.append(cur)
    if cur is not None:
        cur[k] = v

def bare(v):
    """strip backticks and take the value before any ' - ' / en-dash commentary"""
    v = re.split(r'\s+[–—-]\s+', v)[0].strip()
    return [x for x in re.findall(r'`([^`]+)`', v)] or [v.strip()]

F = []
def fail(rid, msg): F.append(f"{rid}: {msg}")

for r in rows:
    rid = bare(r.get('id','?'))[0]
    missing = [f for f in FIELDS if f not in r]
    if missing: fail(rid, f"missing fields {missing}")
    if not re.fullmatch(r'EC-[0-9]{2,}', rid): fail(rid, "id does not match EC-[0-9]{2,}")
    for f, allowed in V.items():
        if f not in r: continue
        vals = bare(r[f])
        for v in vals:
            if v not in allowed: fail(rid, f"{f}={v!r} not in controlled vocabulary")
    res  = bare(r.get('result','')) [0]
    resid= bare(r.get('residual','')) [0]
    ev   = bare(r.get('evidence_state',''))[0]
    ctl  = bare(r.get('control_status',''))[0]
    nak  = bare(r.get('next_action_kind',''))[0]
    tk   = bare(r.get('trigger_kind',''))[0]
    es   = bare(r.get('escalation_state',''))[0]
    eto  = bare(r.get('escalation_to',''))[0]
    ck   = bare(r.get('coverage_kind',''))[0]
    ctot = bare(r.get('coverage_total',''))[0]
    crun = bare(r.get('coverage_run',''))[0]
    rcpt = r.get('receipt_ids','')
    # 2.6.1
    if res in ('pass','fail') and ev != 'valid': fail(rid,"inv1: pass/fail requires evidence_state valid")
    # 2.6.2
    if res == 'not_assessed' and bare(rcpt)[0] != 'none': fail(rid,"inv2: not_assessed requires receipt_ids none")
    if res == 'partially_assessed' and bare(r.get('coverage_limit',''))[0] in ('none',''):
        fail(rid,"inv2: partially_assessed requires a named coverage_limit")
    # 2.6.3 / 2.6.4
    if resid == 'closed_scoped':
        if res != 'pass': fail(rid,"inv3: closed_scoped requires result pass")
        if ctl != 'in_force': fail(rid,"inv3/4: closed_scoped requires control_status in_force")
        if not (ck in ('finite_enumerated','finite_generated') and bare(r.get('coverage_basis',''))[0]=='exhaustive'
                or 'prevention' in bare(r.get('method','')) or bare(r.get('oracle_kind',''))[0]=='formal_proof'):
            fail(rid,"inv3: closed_scoped needs exhaustive finite coverage, prevention or proof")
    # 2.6.5
    if nak in ('install','activate','repair') and resid == 'closed_scoped':
        fail(rid,"inv5: install/activate/repair forbids closed_scoped")
    # 2.6.6
    if nak == 'none' and tk == 'done' and resid not in ('closed_scoped','open_general'):
        fail(rid,"inv6: next_action none + trigger done needs closed_scoped or accepted open_general")
    # 2.6.7
    if res == 'fail':
        if resid != 'open_known': fail(rid,"inv7: fail requires residual open_known")
        if es not in ('owner_review','block','risk_acceptance','incident'):
            fail(rid,"inv7: fail requires an escalation_state")
    # 2.6.8
    if ck == 'open' and resid == 'closed_scoped': fail(rid,"inv8: coverage_kind open forbids closed_scoped")
    # 2.6.9
    if bare(r.get('owner',''))[0] == 'unassigned':
        if es != 'owner_review' or bare(r.get('escalation_trigger',''))[0] != 'required_scope_unassessed':
            fail(rid,"inv9: unassigned owner forces owner_review / required_scope_unassessed")
    # escalation_to
    if eto == 'none' and es != 'none': fail(rid,"2.3: escalation_to none only when escalation_state none")
    # coverage totals
    if ck in ('finite_enumerated','finite_generated'):
        if not ctot.isdigit(): fail(rid,f"2.3: {ck} requires integer coverage_total, got {ctot!r}")
        elif not crun.isdigit() or not (0 <= int(crun) <= int(ctot)):
            fail(rid,f"2.3: coverage_run {crun!r} must be 0..{ctot}")
    else:
        if ctot != 'not_defined' and not ctot.isdigit(): fail(rid,f"2.3: coverage_total {ctot!r}")
    # requirement_ref none only when discovered
    if bare(r.get('requirement_ref',''))[0]=='none' and bare(r.get('requirement_origin',''))[0]!='discovered':
        fail(rid,"2.3: requirement_ref none only when origin is discovered")
    # oracle_ref none forbidden
    if bare(r.get('oracle_ref',''))[0]=='none': fail(rid,"2.3: oracle_ref none is forbidden")
    # mechanism_ref none only when method human_review/none
    if bare(r.get('mechanism_ref',''))[0]=='none' and not set(bare(r.get('method',''))) <= {'human_review','none'}:
        fail(rid,"2.3: mechanism_ref none only when method is human_review or none")
    # coverage_limit none only for exhaustive finite or proof
    if bare(r.get('coverage_limit',''))[0]=='none' and not (
        ck in ('finite_enumerated','finite_generated') and bare(r.get('coverage_basis',''))[0]=='exhaustive'
        or bare(r.get('oracle_kind',''))[0]=='formal_proof'):
        fail(rid,"2.3: coverage_limit none only for exhaustive finite coverage or formal proof")

print(f"rows parsed: {[bare(r.get('id','?'))[0] for r in rows]}")
if not rows: F.append("NO ROWS PARSED - the checker found nothing to check")
for f in F: print("  [FAIL]", f)
print("clean" if not F else f"{len(F)} findings")
sys.exit(1 if F else 0)

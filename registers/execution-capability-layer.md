---
type: register
project: agent-trust-framework
layer: execution-capability
prefix: EC
title: Agent Execution and Capability Layer – Which Required Properties Were Violated or Absent
question: for a declared unit of work, which required properties of the produced behaviour or available capability were violated or absent, and what was observed?
unit: an execution-property assessment
figma-node: none – no frame exists for this layer; the Agent Layers diagram is owed one once the row shape settles
rows: 4
status: four rows derived, from two incidents, against the contract's row schema; this is no longer a stub but it is not yet a taxonomy – the corpus-derived rows the D-069 sequence owes are still not derived
verified: EC-06 and EC-07 were verified on 2026-08-19 against the live `sholto-25/hullkey-charge` repository, from GitHub Actions job records and workflow files read at named commits, not from any report about them; EC-08 and EC-09 were derived on 2026-08-21 from the T-0078 harness evidence receipt and the harness source at named commits in the same repository, with the control-absence and the morning-to-afternoon interval verified from git rather than recalled — their limit is declared in their receipts: the host state they assess is not re-observable; this file still asserts no outcome class, no catch-point position and no built-state headline for this layer, because the contract's vocabulary has none of those fields
residual-basis: derived per the contract's section 2.6 invariants, row by row; not derived from an outcome-by-built-state matrix, which is the four aligned registers' rule and does not apply to this schema
date: 2026-08-11
last-updated: 2026-08-21
---

# Agent Execution and Capability Layer: which required properties were violated or absent

This is the seventh register. It is decided, not speculative: D-065 created Execution and Capability as a seventh peer register on 9 August 2026, and D-070 repaired its headline question the same day. The register table in [[README|registers README]] carries seven entries, and the seventh is this one.

## Where the canon lives

The register's specification is the Execution and Capability contract, [[../research/19-execution-capability-contract-2026-08-09|19-execution-capability-contract-2026-08-09]], sections 2.1 to 2.7: purpose and unit, inclusion and exclusion, row schema and controlled vocabulary, acceptance and property oracle, evidence receipt, invariants, and domain aggregation. The reasoning behind the definition change is [[../research/21-execution-definition-repair-2026-08-09|21-execution-definition-repair-2026-08-09]]. Section 2.1 of the contract carries a superseding callout: the current definition is the one in that callout, as of D-070, not the original "were actually assessed" text kept above it for the record. Nothing about the definition, the row schema, the oracle rules or the vocabulary is restated here beyond the frontmatter, deliberately – a copied definition drifts from its source, which is a failure class this framework's own Corrections Register already documents; the contract stays the single source and this file points at it.

## The discriminator

Quoted from the contract: "would the defect be detectable if the agent made no statement about it at all? Yes → this register. No → Truth." The one-line consequence: a finding whose entire content is that something was never exercised belongs to Truth, not here.

## What is here, and what is still owed

**This file is no longer a stub.** It carries four rows from two incidents in the live `sholto-25/hullkey-charge` repository. EC-06 and EC-07 were derived on 19 August 2026 from a required merge gate that stopped returning a verdict. EC-08 and EC-09 were derived on 21 August 2026 from the T-0078 concurrency harness: a unit of work launched on a host whose required capacity was absent, and the instrument controls that stopped that failure from being read as a product defect.

**It is still not a failure taxonomy.** What the other six registers publish is a taxonomy: stages, severity, prevention, catch point, mechanism, tool, outcome class, residual and next action, row by row, with a stage spine and a catch-point distribution. This register's rows are not that shape and cannot be, because the contract's section 2.3 schema has no stage, no catch point, no tool tier, no outcome class and no A/B/C letter. Four rows against a twenty-eight-field property schema are a real register with four rows, not a small taxonomy. The taxonomy question – whether this layer ever grows a stage spine, or whether the four aligned registers' spine simply does not apply to a property-assessment unit – is open and is not settled here.

**None of these rows comes from the calibration corpus, and none was permitted to.** The rule this register set for itself is that deriving rows must not use any coding run that predates D-070, because those runs coded against the superseded definition. All four were coded directly against the D-070 definition from primary evidence generated ten and twelve days after it, so they clear that bar without depending on the re-code. The D-069 sequence – re-coding the calibration corpus under coding manual v2, and deriving corpus rows from post-D-070 coding only – is untouched by this change and still owed.

## Rules for other sessions

1. Treat the framework as seven registers.
2. `EC-01` to `EC-05` are **calibration cases inside the contract, not rows of this register**, and citing one as a row is still an error. `EC-06` and `EC-07` are rows. The first register row is numbered `EC-06` and not `EC-01` because the contract requires ids to be "stable and never renumbered": `EC-01` to `EC-05` are already bound to the five calibration cases at the contract's section 3.3 and are cited by those names throughout its section 4.2, so reusing them would break exactly the stability the field demands.
3. **Do not quote an outcome distribution, a catch-point distribution, a class letter or a built-state headline for this layer.** None exists, and none is a field of this schema. The framework-wide "134 rows: 12 Class A · 77 Class B · 45 Class C" total in [[README|registers README]] counts the four aligned registers plus Provenance and Truth and **must not be increased by any of these four rows** – they carry no class letter, so they are not summable into it.
4. Do not code against the superseded "were actually assessed" wording – the current definition is the D-070 superseding callout in the contract's section 2.1.
5. A row here is pinned to a state, exactly as the contract's own calibration is. `EC-06` reads `fail` at the head where the property was violated, and stays `fail` at that head forever; `EC-07` reads `pass` at the repaired head. Neither is a statement about the repository today.

## EC-06 – a required merge gate ran on the right route and never returned a verdict

The `accessibility` job of the repository's CI workflow is a required check. On 19 August 2026 it stopped terminating: `npx playwright install --with-deps chromium` shells out to `apt-get update`, the runner's Azure apt mirror stopped responding, and the step neither succeeded nor failed. Both affected pull-request runs were markdown-only, so nothing about the change under test was involved. No job anywhere in the repository declared `timeout-minutes`, so a wedged runner ran against the platform's six-hour default.

**Why this is a trust failure and not only a productivity one.** A gate that never answers is not a slow gate, it is an absent one. The two recoveries actually available were to kill the run by hand or to merge without the verdict, and the second is one flag away at all times (`gh pr merge --admin`). An unbounded gate therefore converts, under time pressure, into an unverified merge – and that conversion is silent in a way the hang itself is not. The row's own `criticality` is graded `S3` for the hang, which is loud and expensive; the `S4`-shaped consequence is the induced bypass, which is a *different* property about whether a boundary can be routed around, and it belongs to Authority and Access rather than being folded into this severity. It is cross-linked below, not counted twice.

| Field | Value |
|---|---|
| `id` | `EC-06` |
| `incident_id` | `none` – searched the Corrections Register on 2026-08-19 for `timeout`, `playwright`, `apt-get`, `wedged` and `accessibility job`: zero matching rows, and the register's highest id is `C-58`. Lodging a correction row for this incident is owed and is not done by this change. |
| `unit_of_work` | `sholto-25/hullkey-charge#183` – the pull request whose required checks did not return |
| `assessment_kind` | `resilience` |
| `subject_ref` | `.github/workflows/ci.yml`, job `accessibility`, at `7c66720e79cba8e6eec304a1f98e5d285b9604c9` |
| `property` | When a step of the `accessibility` job depends on a network service that stops responding, the job must still reach a terminal conclusion within a declared bound, so that the pull request receives a verdict. |
| `requirement_origin` | `discovered` |
| `requirement_ref` | `none` – permitted, and required, because the origin is `discovered`: no rule anywhere in the repository said a job must be bounded until this incident produced one. |
| `criticality` | `S3` |
| `oracle_kind` | `measurement_threshold` |
| `oracle_ref` | The `accessibility` job's declared bound of `timeout-minutes: 12` in `.github/workflows/ci.yml` at `54b3d3850481e7d186f8852e96837ed456a5418d`. At the defective head no bound was declared in any of the repository's three workflow files, so the threshold actually in force was the platform's six-hour job default. |
| `coverage_kind` | `scenario_bounded` |
| `coverage_basis` | `scenario` |
| `coverage_total` | `not_defined` |
| `coverage_run` | `not_defined` |
| `coverage_limit` | Only one fault scenario was observed – a non-responding Ubuntu apt mirror – on two runs of one job on one branch. No other stall class was exercised at this head: not a wedged npm registry, not a Supabase container pull, not a test process that stops making progress without exiting. The other sixteen jobs were equally unbounded and equally exposed, and none of them was observed failing this property. |
| `method` | `measurement` |
| `mechanism_ref` | GitHub Actions' own job timer and step-timing records, read through the `actions/runs/{id}/attempts/{n}/jobs` and `actions/jobs/{id}/logs` endpoints on 2026-08-19. **This value does not meet the contract's "immutable mechanism reference" standard and is declared rather than dressed up**: the instrument is platform-supplied and carries no version I can pin. What is immutable is the observation, not the instrument – the receipts below name the runner version and image version that produced each record. |
| `control_status` | `none` – verified, not assumed: at `7c66720e…` the repository held exactly three workflow files and `grep -c 'timeout-minutes:'` returned `0` for all three. |
| `result` | `fail` |
| `residual` | `open_known` |
| `evidence_state` | `valid` |
| `receipt_ids` | `gha-job-95979538976`, `gha-job-95987269333` |
| `owner` | Sholto Macpherson |
| `next_action_kind` | `reassess` |
| `trigger_kind` | `on_change` |
| `trigger_value` | any change to a file under `.github/workflows/` |
| `escalation_state` | `incident` |
| `escalation_trigger` | `property_failed` |
| `escalation_to` | Sholto Macpherson |

**What was observed, measured rather than recalled.** The first job wedged for 28m18s against a healthy range of 1m15s to 5m29s across six successful runs of the same job on the same day. Its apt step produced its last line at `06:33:55Z` and its next line was the cancellation at `07:01:15Z`: 27m20s of total silence. The second job wedged for 5h28m08s, with 5h27m08s of silence between its last apt line at `07:10:40Z` and the cancellation at `12:37:48Z`. Both logs show `Ign:` lines against `azure.archive.ubuntu.com` retrying in a loop – seventeen such lines in the second – and both cleanup blocks name the same survivor: `Terminate orphan process: pid (…) (npm exec playwright install --with-deps chromium)`.

**A cancellation that did not take, and why it is not a row.** The second job was not stopped by the cancel request that was issued against it. It was reaped at `12:37:51Z`, twenty seconds after a new push superseded the branch, and the same pattern appears on a second run on an unrelated branch (`32227314737`, `07:19:45Z` to `12:39:42Z`). That is a genuine capability property – *the ability to stop a wedged job by hand was absent* – and it is **deliberately not derived as a row here**, because it cannot be given a valid evidence receipt: the GitHub Actions API exposes `created_at`, `run_started_at` and `updated_at` for a run and no cancellation-request timestamp at all, so the interval between request and death is not measurable from any immutable record. Inventing a receipt for it would be worse than leaving it named and underived. It is the strongest candidate for the next row of this register, and it is **not closed by EC-07**: a job that wedges below its own bound is exactly as unkillable as before.

## EC-07 – every job now declares a bound, and the bound was watched firing

| Field | Value |
|---|---|
| `id` | `EC-07` |
| `incident_id` | `none` – as EC-06 |
| `unit_of_work` | `sholto-25/hullkey-charge#187`, merged at `54b3d3850481e7d186f8852e96837ed456a5418d` |
| `assessment_kind` | `resilience` |
| `subject_ref` | `.github/workflows/ci.yml`, `.github/workflows/codeql.yml` and `.github/workflows/post-integration.yml` at `54b3d3850481e7d186f8852e96837ed456a5418d` |
| `property` | Every job mapping under `jobs:` in every workflow file under `.github/workflows/` declares a `timeout-minutes` bound, and that bound terminates a job which exceeds it, so no gate can withhold a verdict for longer than its declared bound. |
| `requirement_origin` | `decision` |
| `requirement_ref` | `sholto-25/hullkey-charge#187` at `54b3d3850481e7d186f8852e96837ed456a5418d`, whose stated rule is roughly three times each job's observed maximum with a five-minute floor |
| `criticality` | `S3` |
| `oracle_kind` | `invariant` |
| `oracle_ref` | The `timeout-minutes` declarations themselves, at `54b3d385…`; the predicate is "for every key under `jobs:`, `timeout-minutes` is present". |
| `coverage_kind` | `finite_enumerated` |
| `coverage_basis` | `exhaustive` |
| `coverage_total` | `17` |
| `coverage_run` | `17` |
| `coverage_limit` | The enumeration is true of one commit and nothing re-asserts it: **no check fails when a job is added without a bound**, so the class reopens silently on the next workflow edit. The bound was fired against one synthetic wedge shape, a `sleep 400`, in two of the seventeen jobs, and never against the original apt-mirror fault itself. Nothing here shortens the window below a job's own declared bound, so the manual-kill path named at the end of EC-06 is untested and unchanged. The five-minute floor is a judgement about ordinary variance, not a measured tail. |
| `method` | `prevention`, `fault_injection` |
| `mechanism_ref` | The three workflow files at `54b3d3850481e7d186f8852e96837ed456a5418d` |
| `control_status` | `in_force` |
| `result` | `pass` |
| `residual` | `open_coverage` |
| `evidence_state` | `valid` |
| `receipt_ids` | `gha-job-96074715372`, `gha-job-96079288906`, `wf-enum-54b3d38` |
| `owner` | Sholto Macpherson |
| `next_action_kind` | `install` |
| `trigger_kind` | `done` |
| `trigger_value` | `none` |
| `escalation_state` | `none` |
| `escalation_trigger` | `none` |
| `escalation_to` | `none` |

**Why this row is `open_coverage` and not `closed_scoped`, decided by the contract rather than by taste.** Every stated precondition for closure is met: `result: pass`, `control_status: in_force`, and coverage that is exhaustive over a finite enumeration. Section 2.6's invariant 5 settles it anyway – `next_action_kind: install` forbids `residual: closed_scoped`, because a row cannot say closed while asking for its closing control to be installed. The control still owed is the check that fails a run when a job carries no bound; until it exists, this row's truth expires at the next workflow edit. This is the same shape as C-02's rule in `check-registers.py`, arrived at from the other direction.

**Why the fallback is gated on `outcome` and not on `conclusion`, which is the part most likely to be got wrong.** The bounded apt step carries `continue-on-error: true`, and that makes GitHub report the step's `conclusion` as `success` while its `outcome` is `failure`. A fallback gated on `steps.<id>.conclusion != 'success'` would therefore never run, and the failure would be invisible: the job would proceed without a browser and fail later, somewhere else. The shipped condition is `steps.playwright_with_deps.outcome != 'success'`, and receipt `gha-job-96074715372` is the evidence that it fires – the fallback step ran, for twelve seconds, immediately after the bounded step was cut off.

**`escalation_state` reads `none`, and that is a gap rather than a clean result.** Section 2.7 escalates an `open_coverage` residual when it "exceeds the declared appetite". **No residual appetite is declared anywhere for this layer**, so no appetite-based escalation can be derived, only asserted. The row records `none` rather than manufacturing a threshold. Declaring an appetite for this register is owed.

## EC-08 – a unit of work was launched although the capability it required was known to be absent

The Compliance half of this incident is already lodged elsewhere: a precondition the acting seat wrote that morning did not bind it that afternoon, which is [[../Corrections Register|C-31]] instance 5, and a gate for it was built, validated in both directions and wired as a `PreToolUse` hook (merged 2026-08-21, `e14315f…`). **This row is the other half, and the counterfactual is the test — remove either and the other survives.** Independently of any rule, and even had the precondition never been written, launching a unit of work whose required capability is absent is its own failure. Sholto's framing is the clearer one: *a human wouldn't launch a project to buy a business if they didn't have a way to get the money to buy it.*

**Why it is not Context's, checked against Context's own unit rather than asserted.** Context's unit is *a fact* — a needed fact absent, stale, untrusted or unused. That does not carry this. With **perfect** knowledge of the host's state, starting the run anyway is still the defect: the failure is in the launching, not in the knowing. The contract's own discriminator settles it from the other direction — *would the defect be detectable if the agent made no statement about it at all?* A run producing unreadable output on a saturated host is detectable with no agent statement whatsoever, so it is not Truth's either. Section 2.1 names the case explicitly under the register's Capability half: *"the required ability was absent, unavailable or unusable before a result could be produced: missing tool, unsupported operation, unavailable dependency, **exhausted resource** or model/tool limitation."*

**Why the criticality is `S3` and not `S4`, decided against the scale rather than by feel.** The shared scale reads `S4` as *"ships or reverses something, and you never find out"*. The S4-shaped consequence is real and is worth stating plainly — a killed `docker exec` means the SQL never reaches the database, so a cell asking *"was this lock acquired?"* truthfully answers *"no lock is held"*, which reads as a **product defect**: an infrastructure failure wearing a finding's clothes, surviving review because it looks exactly like what review is for. It came within one step of shipping two false security findings. But it did not ship, and the reason it did not is a control that was present and worked — the instrument controls this register records as **EC-09**. Grading this row `S4` would take credit for the harm EC-09 prevented, so it reads `S3` and cross-links. This is EC-06's calibration applied again: grade what occurred, name the counterfactual, and do not fold another row's property into this one's severity.

| Field | Value |
|---|---|
| `id` | `EC-08` |
| `incident_id` | `C-31` – the Compliance half of the same incident, lodged as instance 5 of that row. Reachable at the base ref: `sholto-25/second-brain#148` merged on 2026-08-21 as `e14315fcb4761326b4d9805d133495a6d89de541`, verified an ancestor of `origin/main` rather than read off the pull request's badge. The two rows answer different counterfactuals and share this id, which is the cross-link the contract's section 2.2 describes. |
| `unit_of_work` | `sholto-25/hullkey-charge#185` at `0d7442017d1fe284b8b09d8cee6c161a04a1efd0` – the OA-5 two-session concurrency and crash harness |
| `assessment_kind` | `capability` |
| `subject_ref` | The five section-H harness runs of 2026-08-20, recorded at section 3.11 of `.lovelace/documentation/t0078-oa5-harness-evidence-receipt-2026-08-20.md` at `0d7442017d1fe284b8b09d8cee6c161a04a1efd0`. **The subject is the launching of those runs, not a file** – so the immutable reference is the record of them, and that is stated rather than dressed up as a source path. |
| `property` | Before a run of the OA-5 harness is launched, the host must hold the capacity that run requires – a `docker exec` channel not being SIGKILLed, and load low enough that the harness's timing cells measure the product rather than host contention – because a run started without it cannot return a result that is right or wrong, only one that is unreadable. |
| `requirement_origin` | `decision` |
| `requirement_ref` | `sholto-25/hullkey-charge` `.lovelace/documentation/t0078-phase-plan-a-b-c.md` at `98b86b7c95643937752824fd2caff9133be8b4c8`, lines 78–81: *"A healthy host … Any run whose `A6` fails is discarded whole, passes included."* Committed `2026-08-20T08:02:09+10:00`; the runs this row assesses began at `14:20+10:00` the same day. Morning and afternoon are read off the two timestamps, not recalled. |
| `criticality` | `S3` |
| `oracle_kind` | `measurement_threshold` |
| `oracle_ref` | `sholto-25/second-brain` `tools/check-host-capacity.py` at `e14315fcb4761326b4d9805d133495a6d89de541`: running containers above 40, or one-minute load average above 2.0 × cores. **Pinned to the merge commit, not to the commit that authored it.** The authoring commit `3b2325f0…` is byte-identical there but the pull request was squashed, so it is not an ancestor of `origin/main` and is retained only by the pull request – a reference that decays the moment the fork is pruned. Both facts were checked with `git merge-base --is-ancestor` and a content `diff`, not assumed. **This oracle postdates the failure by one day**, which is legal – `requirement_origin` is `decision`, not `discovered`, and the threshold is stated so the observation can be replayed against it. |
| `coverage_kind` | `scenario_bounded` |
| `coverage_basis` | `scenario` |
| `coverage_total` | `not_defined` |
| `coverage_run` | `not_defined` |
| `coverage_limit` | One host, one fault shape, one harness. What was exercised is a macOS laptop carrying five concurrent Supabase stacks; nothing here says where the line sits on any other machine, and the oracle's own file states that its two signals correlate with the condition without diagnosing it – memory pressure, which is what actually produced the SIGKILLs, is not measured at all. Nothing was exercised for the class of work that is *fine* on a loaded host, so the property as written may be broader than the evidence. The degradation was also observed mid-run twice, which no pre-launch check can cover. |
| `method` | `measurement` |
| `mechanism_ref` | Host readings taken with `docker ps` and `sysctl vm.loadavg` and recorded in the receipt named under `subject_ref`. **This does not meet the contract's immutable-instrument standard and is declared rather than dressed up**, on EC-06's precedent: the instruments are platform-supplied and carry no version that can be pinned. What is immutable is the recorded observation, not the instrument. |
| `control_status` | `none` – verified, not assumed: at the defective head the `tools/` directory of `sholto-25/second-brain` held `check-no-hardwrap.py`, `pre-commit-no-hardwrap.sh` and `pre-commit-one-project.sh` and nothing else. No capacity control of any kind existed until `3b2325f…`, one day later. |
| `result` | `fail` |
| `residual` | `open_known` |
| `evidence_state` | `valid` |
| `receipt_ids` | `t78-h-window-20260820` |
| `owner` | Sholto Macpherson |
| `next_action_kind` | `install` |
| `trigger_kind` | `event` |
| `trigger_value` | before any local Supabase-backed harness run |
| `escalation_state` | `incident` |
| `escalation_trigger` | `capability_absent` |
| `escalation_to` | Sholto Macpherson |

**What was observed, measured rather than recalled.** Five section-H runs were taken between roughly 04:20 and 04:40 UTC on 2026-08-20. Host load ran 38–67 against ten cores with 67 containers up across five Supabase stacks, and swap stood at 94%. The last of the five failed `A6b` with `Killed: 9` on `docker exec`. That run is discarded whole, passes included, and the four before it are treated as contaminated rather than as evidence — so the measured yield of the window is **zero usable runs out of five**. Host state was read only after the fifth.

**Why the next action is `install` and not `reassess`.** A control now exists, and it is advisory: `tools/claude-pretooluse-host-capacity.sh` runs as a `PreToolUse` hook and prints, but does not refuse. That is a deliberate choice and not an oversight — the check's own file states that it cannot know what the caller is about to run, and a capacity level that ruins a two-session timing harness is fine for a single-connection unit test. So the class is currently **detected, not prevented**, and `install` names what is still owed: either a refusing form scoped to the work that actually needs it, or a recorded decision that advisory is the ceiling. Section 2.6's invariant 5 forbids `closed_scoped` while that stands, which is the correct answer here.

**This row is evidence for C-18's open split question, and is flagged rather than filed silently.** [[../Corrections Register|C-18]] names `capability_state` and `resource_scope` among the candidate splits of this register, with the two-way behaviour-versus-capability split standing as the hypothesis D-093 gated on the held-out inter-rater run. `EC-08` is a capability row and `EC-09` is a behaviour-of-the-instrument row, derived from one incident, which is the shape that question is about. **It is offered as evidence and decides nothing**: two rows are not an out-of-sample coding run, and D-093 gates the decision on that run, not on this file.

## EC-09 – the instrument controls refused to read an undelivered statement as a product finding

This is the property that stopped `EC-08` from becoming an `S4`. It is derived as its own row because it is independently decidable: it is a property of the **measuring apparatus**, not of the product under test, and it would have held or failed at that head whatever the host was doing.

**Why it is a row and not a line inside EC-08's evidence.** The counterfactual separates them. Remove EC-08's failure — a healthy host — and this property is simply never exercised; remove this property — a harness with no `A6`/`A6b`/`A7` controls — and EC-08's failure proceeds all the way to two false security findings in a review that had no way to see they were false. The second direction is the one that matters, and it is why the framework's own rule 7 on second diagnoses applies here: a named, dedicated mechanism that *held* is still its own assessment, not a detail in another row's write-up.

**The failure mode it guards is silent by construction.** When `docker exec` is SIGKILLed the SQL never reaches a backend. A cell asking *"was this lock acquired?"* then reads an empty result and, with no instrument control, records the truthful-but-worthless answer *"no lock is held"* — which is indistinguishable from the product genuinely failing to take the lock. `A6` asserts the decoder can see exactly the one key a live session is **known** to be holding; `A6b` asserts the probe session executed its SQL and ended cleanly, reporting `HARNESS_NO_SESSION` rather than `SUCCESS` when it did not; `A7` asserts that an empty reading from a query that *failed* is never evidence the key was released. All three are positive-or-negative controls on the observation instrument, and together they convert an unreadable run into a declared instrument failure instead of a product verdict.

| Field | Value |
|---|---|
| `id` | `EC-09` |
| `incident_id` | `C-31` – as EC-08 |
| `unit_of_work` | `sholto-25/hullkey-charge#185` at `0d7442017d1fe284b8b09d8cee6c161a04a1efd0` |
| `assessment_kind` | `resilience` |
| `subject_ref` | `sholto-25/hullkey-charge` `scripts/oa5-concurrency-crash.test.sh` at `0d7442017d1fe284b8b09d8cee6c161a04a1efd0` (blob `c820d7dc856cd8162e3bfea26c9783baf2beb573`), the `A6`/`A6b`/`A7` block at lines 1509–1578 |
| `property` | When the harness's execution channel fails to deliver a statement to the database, the run must report an instrument failure and be discarded whole – including every cell in it that passed – rather than any cell reading the resulting empty result as a product observation. |
| `requirement_origin` | `derived_invariant` |
| `requirement_ref` | `sholto-25/hullkey-charge` `.lovelace/documentation/t0078-phase-plan-a-b-c.md` at `98b86b7c95643937752824fd2caff9133be8b4c8`, lines 78–81, which states the discard rule this property enforces: *"Any run whose `A6` fails is discarded whole, passes included."* |
| `criticality` | `S4` |
| `oracle_kind` | `invariant` |
| `oracle_ref` | The `A6`, `A6b` and `A7` assertions themselves at `c820d7dc…`; the predicate is "a session whose SQL never reaches a backend reports `HARNESS_NO_SESSION`, never `SUCCESS`", with `A6` as its positive control and `A7` as its negative one. |
| `coverage_kind` | `scenario_bounded` |
| `coverage_basis` | `scenario` |
| `coverage_total` | `not_defined` |
| `coverage_run` | `not_defined` |
| `coverage_limit` | The property was exercised against **one** delivery-failure shape – a SIGKILLed `docker exec` under host saturation – on two occasions. It was not exercised against a statement that reaches the backend and is killed mid-transaction, against a connection accepted and then dropped, or against a partially-returned result set, and each of those could produce an empty reading by a different route. The controls also cover only the **lock-observation** instrument: no equivalent control exists for the other cells of the harness, so a delivery failure inside those is not covered by this row and is not known to be caught. |
| `method` | `fault_injection`, `measurement` |
| `mechanism_ref` | `scripts/oa5-concurrency-crash.test.sh` at `c820d7dc856cd8162e3bfea26c9783baf2beb573` |
| `control_status` | `in_force` |
| `result` | `pass` |
| `residual` | `open_coverage` |
| `evidence_state` | `valid` |
| `receipt_ids` | `t78-g2-instrument-fail`, `t78-h-window-20260820` |
| `owner` | Sholto Macpherson |
| `next_action_kind` | `expand_coverage` |
| `trigger_kind` | `on_change` |
| `trigger_value` | any change to `scripts/oa5-concurrency-crash.test.sh` |
| `escalation_state` | `none` |
| `escalation_trigger` | `none` |
| `escalation_to` | `none` |

**Why this reads `pass` and `open_coverage` rather than `closed_scoped`.** It passed twice, observed rather than argued: on 2026-08-19 `A6` failed with the probe session reporting `SUCCESS` and the observer reporting no errors, and the whole window — `fullrun-final.txt`, `run08`, `run09` — was discarded including its passes; on 2026-08-20 `A6b` failed with `Killed: 9` and that run was discarded whole with the four before it treated as contaminated. Section 2.6's invariant 3 permits `closed_scoped` only on exhaustive finite coverage, prevention or proof, and this is a bounded scenario against one fault shape, so `open_coverage` is what the contract allows. `next_action_kind: expand_coverage` names the gap in the `coverage_limit` cell.

**Why the criticality is `S4` where EC-08's is `S3`.** These grade different things and the difference is not a contradiction. EC-08 grades what occurred, and what occurred was caught. This row grades the property's own failure — *if this control were absent or broken* — and that failure is exactly the scale's `S4`: an infrastructure fault ships as a product finding and you never find out, because the artefact it produces is indistinguishable from the thing review exists to look for. A control whose absence is `S4` is a control worth a row of its own, which is the argument for deriving it.

**A gap this row does not close, named rather than left implied.** The receipt's own §3.11 warns that anyone re-running section H *"should check `A6b` first and discard the run if it fails"* — which is a human instruction, not a mechanism. The controls fire inside a run; nothing refuses to *start* one on a host that will produce nothing, and nothing prevents a reader taking a number out of a contaminated run recorded elsewhere. That gap is `EC-08`'s `install`, and the two rows close it only together.

## Evidence receipts

Five receipts, in the contract's section 2.5 shape. Every field is populated; where a field cannot be honestly filled it says so rather than being omitted.

| Receipt field | `gha-job-95979538976` | `gha-job-95987269333` |
|---|---|---|
| `receipt_id` | `gha-job-95979538976` | `gha-job-95987269333` |
| `observed_at` | 2026-08-19T06:32:59Z to 2026-08-19T07:01:17Z | 2026-08-19T07:09:43Z to 2026-08-19T12:37:51Z |
| `executor` | GitHub-hosted runner, CI identity | GitHub-hosted runner, CI identity |
| `subject_version` | `7c66720e79cba8e6eec304a1f98e5d285b9604c9` | `7c66720e79cba8e6eec304a1f98e5d285b9604c9` |
| `oracle_version` | no bound declared at this head; platform default of six hours in force | no bound declared at this head; platform default of six hours in force |
| `instrument_version` | runner `2.336.0`, image `ubuntu-24.04` `20260810.271.1` | runner `2.336.0`, image `ubuntu-24.04` `20260816.277.1` |
| `environment` | GitHub-hosted `ubuntu-latest`, Azure region `eastus` | GitHub-hosted `ubuntu-latest`, Azure region `eastus` |
| `selection_manifest` | `not_applicable` – an observed fault, not a selected input | `not_applicable` – an observed fault, not a selected input |
| `raw_result_ref` | `https://github.com/sholto-25/hullkey-charge/actions/runs/32223876724/job/95979538976` (run attempt 1); step `Run npx playwright install --with-deps chromium` 06:33:15Z to 07:01:15Z, conclusion `cancelled` | `https://github.com/sholto-25/hullkey-charge/actions/runs/32226527347/job/95987269333`; same step 07:10:01Z to 12:37:48Z, conclusion `cancelled` |
| `exit_state` | `fail` – the job exceeded the threshold and produced no verdict | `fail` – the job exceeded the threshold and produced no verdict |
| `non_vacuity` | `not_material` – the observation is a measured wall-clock duration against a fixed threshold, which cannot pass vacuously | `not_material` – as left |
| `integrity` | append-only GitHub Actions job record `95979538976`; log retrieved 2026-08-19 | append-only GitHub Actions job record `95987269333`; log retrieved 2026-08-19 |

| Receipt field | `gha-job-96074715372` | `gha-job-96079288906` |
|---|---|---|
| `receipt_id` | `gha-job-96074715372` | `gha-job-96079288906` |
| `observed_at` | 2026-08-19T12:53:45Z to 2026-08-19T13:00:07Z | 2026-08-19T13:09:19Z to 2026-08-19T13:14:33Z |
| `executor` | GitHub-hosted runner, CI identity | GitHub-hosted runner, CI identity |
| `subject_version` | `fa8bdc5d38634726dd32a80a183ebdb52b32b23c` (throwaway PR #186, closed; branch deleted, commit retained by the pull request) | `285d49ad06de655eaa81797222a58f20e8ab76ee` (throwaway PR #188, closed; branch deleted, commit retained by the pull request) |
| `oracle_version` | step bound `timeout-minutes: 5` on `Install Chromium with system deps` | job bound `timeout-minutes: 5` on `repository-boundary` |
| `instrument_version` | runner `2.336.0`, image `ubuntu-24.04` `20260810.271.1`; injected wedge `sleep 400` inside the bounded step | runner `2.336.0`, image `ubuntu-24.04` `20260810.271.1`; injected wedge `sleep 400` as step `VALIDATION stall (job bound is 5m)` |
| `environment` | GitHub-hosted `ubuntu-latest` | GitHub-hosted `ubuntu-latest` |
| `selection_manifest` | one enumerated input: a single deliberately wedged step in the `accessibility` job | one enumerated input: a single deliberately wedged step in the `repository-boundary` job |
| `raw_result_ref` | `https://github.com/sholto-25/hullkey-charge/actions/runs/32255057641/job/96074715372`; bounded step 12:54:05Z to 12:59:18Z (5m13s), fallback step 12:59:18Z to 12:59:30Z, job `success` in 6m22s | `https://github.com/sholto-25/hullkey-charge/actions/runs/32256493666/job/96079288906`; wedged step 13:09:21Z to 13:14:33Z (5m12s), job `cancelled` at 5m14s |
| `exit_state` | `pass` – the bound cut the step at 5m13s and the fallback ran, which is the expected terminal behaviour | `pass` – the bound cut the job at 5m14s with conclusion `cancelled`, which is the expected terminal behaviour |
| `non_vacuity` | `demonstrated` – the bound was fired against a job deliberately made to hang, not merely parsed out of the YAML | `demonstrated` – as left |
| `integrity` | append-only GitHub Actions job record `96074715372` | append-only GitHub Actions job record `96079288906` |

| Receipt field | `wf-enum-54b3d38` |
|---|---|
| `receipt_id` | `wf-enum-54b3d38` |
| `observed_at` | 2026-08-19 |
| `executor` | Claude Opus 5, session deriving this register row |
| `subject_version` | `54b3d3850481e7d186f8852e96837ed456a5418d`, verified an ancestor of `origin/main` with `git merge-base --is-ancestor` |
| `oracle_version` | the predicate "every key under `jobs:` carries `timeout-minutes`", against the three workflow files at that commit |
| `instrument_version` | `git show` piped into a PyYAML parse of each workflow's `jobs` mapping – deliberately not `grep`, so that a `timeout-minutes` appearing at step level cannot be miscounted as a job bound |
| `environment` | local checkout of `sholto-25/hullkey-charge` |
| `selection_manifest` | enumerated: `ci.yml` 14 jobs, `codeql.yml` 1, `post-integration.yml` 2; 17 total |
| `raw_result_ref` | replayable from the commit itself; the parse reported 17 jobs and an empty missing-bound list, with per-job bounds `repository-boundary` 5, `build` 10, `colour-receipt-pairing` 5, `db-isolation` 15, `rls-test-pairing` 5, `catalogue-diff` 5, `accessibility` 12, `test-write-protection` 5, `lovelace-session-integrity` 5, `absence-claims` 5, `held-out-tests` 10, `secret-scan` 5, `dependency-audit` 10, `deploy-staging` 20, `analyse` 20, `auth-observation` 15, `health` 15 |
| `exit_state` | `pass` |
| `non_vacuity` | `demonstrated` – by `gha-job-96079288906`, which shows a declared job bound actually terminating a job; the enumeration alone would be a structural claim only |
| `integrity` | committed-path-plus-commit: `.github/workflows/*.yml` at `54b3d385…` |


Two further receipts, added with `EC-08` and `EC-09`. Both are second-hand in one specific sense that is declared rather than glossed: the observations were made by the harness and by the seat running it, and what is immutable here is the committed record of them, not a re-observable instrument. Neither can be replayed — the host state of a given afternoon is gone — and that is a real limit on both rows.

| Receipt field | `t78-h-window-20260820` | `t78-g2-instrument-fail` |
|---|---|---|
| `receipt_id` | `t78-h-window-20260820` | `t78-g2-instrument-fail` |
| `observed_at` | 2026-08-20, approximately 04:20Z to 04:40Z | 2026-08-19, the 14:20+10:00 to 14:32+10:00 degraded window |
| `executor` | Codex seat running the OA-5 harness on Sholto's host | Codex seat running the OA-5 harness on Sholto's host |
| `subject_version` | `961ead55` plus uncommitted seat-2 work; the record of the runs is `.lovelace/documentation/t0078-oa5-harness-evidence-receipt-2026-08-20.md` §3.11 at `0d7442017d1fe284b8b09d8cee6c161a04a1efd0` | `scripts/oa5-concurrency-crash.test.sh` blob `c820d7dc856cd8162e3bfea26c9783baf2beb573`; the record is §3.3 and §4 of the same document at the same commit |
| `oracle_version` | `tools/check-host-capacity.py` at `e14315fcb4761326b4d9805d133495a6d89de541` – containers > 40 or one-minute load > 2.0 × cores. Applied **retrospectively** to recorded readings; it did not exist on the day. | the `A6`/`A6b`/`A7` assertions at lines 1509–1578 of blob `c820d7dc…` |
| `instrument_version` | `docker ps` and `sysctl vm.loadavg` on macOS – platform-supplied, no pinnable version, declared as EC-06 declares the same limit | the harness itself at blob `c820d7dc…`; the fault was not injected but observed, so no injection version applies |
| `environment` | one macOS host, ten cores, carrying five concurrent local Supabase stacks, 67 running containers, swap at 94% | the same host, in the 2026-08-19 degraded window: repeated `Killed: 9` on `docker exec` and repeated `500 Internal Server Error` from the Docker API socket |
| `selection_manifest` | enumerated: five section-H runs, of which the fifth failed `A6b` and the four before it are treated as contaminated | enumerated: two occasions – `g_2.txt` (`A6b` `HARNESS_HANG`, `A7` observer read incomplete) and `fullrun-final.txt` with `run08`/`run09` (`A6` fail) |
| `raw_result_ref` | §3.11 of `t0078-oa5-harness-evidence-receipt-2026-08-20.md` at `0d74420…`, which records the load range 38–67, the container count, the `Killed: 9`, and the discard decision | §3.3 and §4 of the same document at the same commit, quoting the harness's own `A6b` and `A7` output lines and recording an observer read measured at 51.8 s against a 3 s statement timeout |
| `exit_state` | `fail` – zero usable runs from five, and host state was read only after the fifth | `pass` – the instrument controls discriminated, and both runs were discarded whole rather than read as product findings |
| `non_vacuity` | `not_material` – the observation is a set of measured host readings against a stated threshold, which cannot pass vacuously | `demonstrated` – the controls are known to be capable of failing because they *did* fail, on the two occasions this receipt enumerates, and the failures were acted on |
| `integrity` | committed-path-plus-commit: `.lovelace/documentation/t0078-oa5-harness-evidence-receipt-2026-08-20.md` at `0d7442017d1fe284b8b09d8cee6c161a04a1efd0` | committed-path-plus-commit, as left, plus blob `c820d7dc856cd8162e3bfea26c9783baf2beb573` for the subject |

## How to falsify these rows

`registers/tools/check-ec-rows.py` checks every row on this page against the contract's section 2.3 vocabulary and grammar and its section 2.6 invariants.

```
python3 registers/tools/check-ec-rows.py registers/execution-capability-layer.md
```

**It is not wired to anything.** `check-registers.py` hard-codes the six aligned layers and models their column set, which this schema does not share, so folding this in is a real change to that gate rather than a line of configuration – and until someone makes it, this check binds only when a human runs it. It should be described that way and never as an enforced gate. It was validated before first use against eleven deliberately broken copies of this file – including `closed_scoped` on a row whose next action is `install`, a `fail` row with its escalation removed, and `pass` on unverified evidence – and caught all eleven while leaving the unmutated file clean. That validation is the reason to trust it; the script's own header records it.

## Boundaries with the other six registers, checked rather than asserted

The discriminator puts this incident here: a job that hangs is detectable with no agent statement about it at all, so the primary failure is not Truth's.

A search of all ten markdown files in this folder on 2026-08-19 returned nothing on this failure class:

```
grep -n -i -E '\b(hang|hangs|hung|hanging|wedge|wedged|stall|stalls|stalled|timeout|timeouts|time-out|unbounded|deadlock|livelock|infinite|never returns|never returned|no verdict|runs forever)\b' *.md
```

Exit status `1`, zero matches. A second pass on gate-bypass and duration language found the three nearest neighbours, and each one misses for a different reason: [[authority-access-layer|AL-4A]] is a gate that runs on the route the action did not take; [[authority-access-layer|AL-4E]] is a gate that requires a pull request but no second reader; [[instruction-layer|IL-4E]] is an action routing around a gate that exists. All three describe a gate that is present and answers the wrong question, or is absent from the path. **None describes a gate that ran, on the right route, asking the right question, and never returned an answer.** That is the gap EC-06 fills.

Two live cross-links, neither counted as a row here:

- **Authority and Access** owns the induced bypass. `gh pr merge --admin` merges past a required check that has not answered, and [[authority-access-layer|AL-2B]] and [[authority-access-layer|AL-3B]] are the adjacent rows. Whether an unbounded gate is itself an authority defect – because it manufactures the pressure to use the bypass – is a real question and is not answered here.
- **Recovery** owns the reaping. The wedged job survived a cancellation request for hours, which is a restoration failure as much as an execution one; it is described at the end of EC-06 and is not derivable as a row for the receipt reason given there.

## What is still owed

1. Lodge a Corrections Register row for this incident. Verified absent on 2026-08-19: zero rows match `timeout`, `playwright`, `apt-get`, `wedged` or `accessibility job`, and the highest id is `C-58`. Both rows above therefore read `incident_id: none`, which is legal under the schema and thin under the framework's own practice.
2. Install the check that closes EC-07: a CI gate that fails when a job under `.github/workflows/` declares no `timeout-minutes`. Per the framework's own rule, it is not trusted until it has been run against a known-bad workflow and shown to catch it. Installing it also discharges EC-06's `reassess` obligation, which is manual today.
3. Declare a residual appetite for this layer, so that `open_coverage` and `open_general` escalations can be derived under the contract's section 2.7 instead of left at `none`.
4. Settle whether the manual-kill capability gap gets a row, and on what evidence, given that no cancellation-request timestamp is retrievable.
5. ~~Update the register table in [[README|registers README]].~~ Done in the same change: its seventh row reads the current row count, its State cell reads *n/a – no class letters*, and the note under the table says explicitly that these rows are not addable to the 134-row total or to any distribution on that page. Re-checked and re-pointed on 2026-08-21 when EC-08 and EC-09 landed.
6. Finish the D-069 sequence and derive the corpus rows. These four rows do not substitute for it: they are two incidents, coded directly, and say nothing about the shape of the eventual population.
7. Decide the stage-spine question in "What is here, and what is still owed" above, and only then build the owed Figma frame. A frame drawn against the four aligned registers' geometry would misrepresent a schema that has no stages, no catch points and no class letters.
8. The V1 extractor still hard-codes six sources (C-15). It does not read this file, so nothing here has changed a published count – but the seventh register now has rows, which is a new reason that gap matters.

**Option 3 from the definition repair – splitting this into two registers, one for produced behaviour and one for assessment and coverage – is explicitly not ruled out.** D-070 defers it rather than rejecting it, and C-18's split question remains open. If that option is taken, all four rows are re-homed rather than discarded; their ids do not move. **EC-08 and EC-09 are the first pair derived from one incident that falls either side of that very line** – a capability row and a behaviour-of-the-instrument row – and they are logged as evidence toward the question, not as an answer to it.

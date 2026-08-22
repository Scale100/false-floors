# Agent Layer Registers — canon source files

**These files are canon. The Figma diagrams are generated views.** Any scan, correction, or new row lands here first; the diagram is then re-derived (or hand-synced and verified) from the register. Never edit a diagram and leave the register behind — a register/diagram mismatch is a defect in the diagram.

Figma file: `KDkIqr0lzbcAUvJLGAcExk` (HullKey UI Kit · Design System), page **Pathways**, frame **Agent Layers** (`1274:20994`).

| Register | Question it asks | Unit of life | Prefix | Figma node | Rows | Evidenced · candidate | State (A·B·C) |
|---|---|---|---|---|---|---|---|
| [[instruction-layer]] | Did it do what it was told? | a rule | IL | `1358:139` (rev 3) | 22 | 8 · 14 | 2 · 12 · 8 |
| [[context-layer]] | Did it know what it needed to know? | a fact | CL | `1386:139` (rev 2) | 22 | 11 · 11 | 0 · 14 · 8 |
| [[authority-access-layer]] | What could it reach? | a permission | AL | `1379:139` (rev 2) | 23 | 16 · 7 | 2 · 14 · 7 |
| [[recovery-layer]] | Can you get it back? | a change | RL | `1389:139` (rev 2) | 24 | 11 · 13 | 5 · 10 · 9 |
| [[provenance-layer]] | Is the record of what was done trustworthy? | a unit of work | PL | `1395:139` (rev 2) | 22 | 12 · 10 | 3 · 14 · 5 |
| [[truth-layer]] | Can its claims about its own work be trusted? | a claim | TL | `1392:139` (rev 2) | 15 | 8 · 7 | 0 · 9 · 6 |
| [[execution-capability-layer]] | Which required properties were violated or absent, and what was observed? | an execution-property assessment | EC | none | 4 | *n/a – incident-derived by construction* | *n/a – no class letters* |

**The State column is A · B · C for every row of this table**, so the six are comparable and the column sums. Read each register's own words off the class-reading table below: Recovery's B · C are recoverable · irreversible, and the other five are detected · survives. The six registers hold 128 rows in total: 12 Class A · 73 Class B · 43 Class C – stated in letters, because no single register's words are true of all six. (Before the D-106 retirement pass of 2026-08-21 the total read 134: six rows were retired or merged, each recorded in its register's own Retired rows section.)

**The headline count is 66 evidenced rows — never 128 (D-107).** Every row carries an evidence status, and the split per register is the Evidenced · candidate column above: **66 evidenced · 62 candidate** across the six. A published count of the framework's failure modes counts the evidenced rows only; candidates are published and labelled, and stated alongside, never inside, the headline number. `check-registers.py` derives the receipts and fails on any row whose marker disagrees with them.

**The seventh register is no longer a stub, and its four rows are deliberately outside that 134.** [[execution-capability-layer]] carries `EC-06` and `EC-07`, derived on 2026-08-19, and `EC-08` and `EC-09`, derived on 2026-08-21 — two live incidents, coded against the contract's own row schema. **They are not addable to any total or distribution on this page.** The contract's schema has no class letter, no outcome class, no catch point and no tool tier, so there is nothing for the A · B · C column to hold and nothing for the cross-register sum to absorb; its State cell reads *n/a* rather than a dash, so that no later reader takes an empty cell for an unfilled one. Its own `result` and `residual` vocabulary is defined in the contract, not here, and its `EC-01` to `EC-05` remain calibration cases in the contract rather than rows.

## Row ID rules

1. **IDs are stable and never renumbered.** A newly discovered failure appends a letter inside its stage (IL-1E was added 6 August 2026); nothing else moves. IDs are how scan runs stay comparable and findings stay linkable. **A retired ID is never reused**: a row leaves the counts by moving to its register's Retired rows section with a dated reason (D-106 pass, 2026-08-21 — `IL-3B`, `CL-6C`, `RL-5C`, `RL-6A`, `PL-1B`, `PL-4D`), and any old scan citing the ID still resolves there.
2. **PL and TL IDs are assigned by these registers**, not by the diagrams — the provenance and truth frames predate the ID scheme, and both adopted the register IDs at their rev 2 on 9 August 2026. PL rows are numbered by category order (1 orientation and continuity, 2 claiming the work, 3 the record itself, 4 linking intent to code, 5 landing, 6 many agents); TL rows keep the diagram's claim numbers (TL-01 to TL-15).

## Shared vocabulary

**Outcome (Class) – the letter grades how complete the remedy is.** One construct, six domain readings (D-099, 17 August 2026). It is a property of the mechanism applied to the unit, not of the rule, fact, permission, change, record or claim itself:

- **Class A** – the failure cannot occur. Something refuses it, so there is nothing to check afterwards.
- **Class B** – it occurs, and something handles it completely. Every instance is caught, or every instance can be undone.
- **Class C** – it occurs and no available remedy is complete. Something may still see it, narrow it or slow it; nothing closes it.

**Each register reads B and C in its own words, and those words are canonical for that register.** The letter is what travels between registers; the words are what make the row true inside one. Never restate one register's words as the framework's.

| Register | Class A reads | Class B reads | Class C reads |
|---|---|---|---|
| Instruction, Context, Authority and Access, Provenance, Truth | prevented | **detected** | **survives** |
| Recovery | prevented | **recoverable** | **irreversible** |

**Recovery is the only register with different words**, and the divergence is exactly 10 rows of Class B and 9 of Class C. Truth's section titles – *By construction*, *Checkable*, *Judgement* – name its classes and are **not** its outcome vocabulary; its own outcome lines and its published spoke both read prevented · detected · survives. Quoting those titles as a third vocabulary is a mistake this file made on 17 August and `check-registers.py` now refuses.

**Why this replaced the previous definition, which was wrong on the rows.** Until 17 August this section defined Class C as "nothing catches it". That is false for **15 of the 33 Class C rows** in the four aligned registers, every one of which names a real, built or designed mechanism: IL-2A and IL-2C have Claude Code delivering and re-injecting the rule file, and are C because delivery is not compliance; AL-1B names a deny rule the agent can edit, and is C because the boundary is bypassable. In each case the operative reason for the letter is that **no remedy is complete**, not that nothing sees it. Recovery made the same point from the other side: RL-2A is trivially detectable and still irreversible. The letters were sorting remedy-completeness all along; the wording had picked one register's instance of it and generalised. That is C-06, and this is its repair.

**Two rules follow, and both are enforced by `check-registers.py`:**

1. **A cross-register total is stated in letters, never in one register's words.** "77 Class B", not "77 detected" – 11 of those 77 are Recovery's *recoverable*, and 9 of the 44 Class C are its *irreversible*.
2. **A register's own count may use its own words**, because inside one register the word is unambiguous and is the more useful thing to read.

What this does **not** fix: severity is still two incompatible scales sharing one name (C-08), the catch ladder still mixes four kinds of position (C-11), and lifecycle stage still has no classification rule (C-12). Those are separate rows and stay open. "The registers share one vocabulary" remains an overclaim.

**Evidence** (added D-107, 21 August 2026) — whether reality has confirmed the row, and the field that sets what a headline count may claim:

- **evidenced** — at least one receipt exists. Three receipt types count, and nothing else does: a first-party incident mapped in the Corrections Register with an `⟪instance-of⟫` marker; a corpus-coded finding from the 262-item calibration pass ([[../research/22-register-calibration-pass-2026-08-09|run 22]]) graded exact or variant; or a verifiable public field case with a dated, checkable citation filed in the vault.
- **candidate** — enumerated in advance, no receipt yet. Still a row: published, classed, graded, labelled. Not counted in any headline.

Three rules follow, all enforced or exercised by `check-registers.py`:

1. **Headline counts count evidenced rows only.** On the receipts as at 2026-08-21 that is 66 evidenced · 62 candidate. The evidenced number moves only when a receipt lands or a row retires, so it is grounded by construction.
2. **The marker is derived, not asserted.** The checker re-derives the receipt sets from the Corrections Register and the run-22 table on every run and fails on any row whose Evidence cell disagrees — in either direction, because an understated 66 is as wrong as an overstated one.
3. **Promotion and decay.** A candidate is promoted by its first receipt. A candidate that a stated review window passes over with no instance, no corpus match and no field case is retired to the candidate pen ([[truth-layer]], "Candidate rows, not yet evidenced" — the pen holds gaps that are not yet rows, which is one step below a published candidate row).

Enumeration is thereby demoted from row source to hypothesis source: it proposes candidates, and its track record is published — of the 113 rows standing as unconfirmed predictions at enumeration, 23 (about one in five) were confirmed by a first dated incident within eleven days, in the derivation environment ([[METHODOLOGY]] section 4 carries the denominator, the dates and the scope caveats). It never again sets a published total. Full rationale and the decision: [[METHODOLOGY]] and D-107.

**Severity** — cost multiplied by how silently it fails; a judgement, not a measurement:
- **S1** — a round trip, noticed at once
- **S2** — rework you catch at review
- **S3** — real rework or a wrong outcome, found late
- **S4** — ships or reverses something, and you never find out

The recovery layer grades the same scale by cost-to-undo: S1 undone in seconds · S2 undone with effort · S3 undone only by rebuilding by hand · S4 cannot be undone at any price.

**Tool tier** — prefer a tool that maintains itself, over a tool you maintain, over a process you remember:
- **automatic** — runs itself, nothing to maintain
- **maintained** — only as good as the file you keep current
- **process** — you have to remember, every time

**Built state** — naming a mechanism is not installing it. **Scope: the `hullkey-charge` repo** (D-058) — not the vault repo, not the machine generally. Harness features that are machine-level rather than repo-level (plan mode, the CLAUDE.md hierarchy loading into subagents) are `built` on their own terms, since they are in force wherever the agent runs.
- **built** — in force in `hullkey-charge` today
- **designed** — the mechanism is designed, not installed (the diagram's amber edge marker)
- **none** — no mechanism exists; the row survives on a convention or nothing

Two rules make `built` comparable across layers, both settled 9 August 2026 after a parse check found the six registers disagreeing with each other:

1. **A row that names no mechanism takes built state `none`, never `designed`.** There is nothing to design. Authority and Recovery carried twelve rows reading `none · … · designed` — and one reading `none · … · built`, which asserted that the nothing was installed. Both are now `none`.
2. **The headline count is `designed` over *tooled rows*, not over all rows** — for example Instruction now reads "12 of the 21", where 21 excludes the process-only rows because they have no mechanism to build. The four row registers previously used three different denominators in identical language (21 tooled, 23 all, 25 all), which made the most quotable number in the framework non-comparable between its own layers. A benchmark or a vendor scorecard needs `built` to mean one thing (D-053, D-054); this is what makes that true.

**Residual** (added D-061) — what is actually true about the failure today, given everything in place. **This is not `built`.** `built` is a fact about the *named* mechanism; residual is a fact about the *failure*, and the two come apart in both directions — IL-3C's mechanism is built and the row still survives, while IL-1F's named mechanism was never built and the failure is largely closed by a gate the row did not name.
- **closed** — the failure is treated; nothing further is owed
- **closed by substitute** — a mechanism this row does not name closes it. **This is a compensating control** in the sense security, SOC 2 and ISO assessors already use the term: a different control, standing in for the specified one, carrying its own evidence. The framework's own name for the field is kept because the register grades failure modes rather than requirements, but the two mean the same thing and the audit term is the one to reach for when explaining it (added 2026-08-11)
- **partially closed** — one part is closed and another is not; the boundary must be named
- **open** — nothing closes it today

Two rules that make the field honest rather than decorative:

1. **A substitute carries its own catch point; it never inherits the named mechanism's.** IL-1F's named schema lint sat at `on disk` while the gate that actually closes it runs in CI, which moved the layer's catch-point distribution and two phase totals. A substitute that inherited would silently corrupt the most load-bearing column in the framework.
2. **A substitute or partial claim needs a receipt, not an assertion** — identifier, its own catch point, one line on why it closes the failure and where it stops, and the date observed. **Two further fields, added 2026-08-11, borrowed from the compensating-control worksheets the audit standards already publish**, because they are the two that stop a substitute quietly rotting: the **constraint** (why the row's named mechanism cannot be used, which is what makes a substitute legitimate rather than merely convenient) and the **maintenance owner** (who re-checks that the substitute still closes the failure, and on what trigger). A substitute with no stated constraint is an unexamined preference; one with no maintenance owner is a control nobody is watching.

**One declared exception: the provenance layer derives residual from its own cell strengths, gated on install state.** Because a provenance row has three control positions rather than one named mechanism, its rule is: **a row whose next action is a `ONCE —` install reads `open`** — the control it names is not switched on, so it closes nothing today; otherwise any `closes` reads `closed`, otherwise any `partial` reads `partially closed`, otherwise `open`. That legitimately produces `C survives · partially closed` — PL-4B, PL-6A and PL-6F — which the global rule below forbids. The exception is declared here rather than only in [[provenance-layer]], because a rule stated in two places without one of them naming the other is how the two drift apart.

The install gate was added 2026-08-10 to correct C-02. Provenance has no `built` field, so cell strength alone described what a control was *designed* to do and nothing recorded whether it existed; 14 of the layer's then-24 rows read `closed` while their own next action said to install the mechanism. The `ONCE —` next action is the de facto state field until the layer gains a real one. Residual now reads 6 closed · 3 partially closed · 13 open (22 rows since the D-106 retirements).

**How far to trust a residual value.** Most values today are *derived*, not observed: outside the provenance exception above, `survives`/`irreversible` is always `open`; `prevented`/`detected` on a `built` mechanism reads `closed`; anything whose named mechanism is `designed` or `none` reads `open` unless a substitute is recorded. A derived value is only as good as its register's own `verified:` stamp, so residual on a design-only register is a restatement of an unverified build state, not evidence. `closed by substitute` and `partially closed` are never derived — they are entered by hand against evidence. Full argument: [[register-view-design-rationale]] section 7.

**Authority** — who can switch the control off:
- **unbypassable** — runs where the agent cannot reach it
- **bypassable** — a login, a local hook, or a settings file the agent can edit

**Catch point** — where in the turn the failure is caught, earliest to latest: `on disk · session start · prompt · pre-tool · subagent · post-tool · compact · stop · pre-commit · CI · review`. Prevention lives only where the mechanism can refuse; the earlier it refuses, the less has already been spent. The provenance layer uses its own three positions instead: **harness gate** (at the moment of work) · **repo artefact** (committed with the code) · **control-plane check** (on the commit).

**Provenance cell key** — per control position: **closes** (refuses or catches it every time) · **partial** (conditional, or not switched on) · **nothing** (nothing here closes it) · **n/a** (not this layer's job).

**Trigger** — how often the operator must act. The field parses to a kind and a value: `once` is an install; `done` is a dated completion; `weekly` / `monthly` / `quarterly` / `annually` are cadences; `every` is a per-event ritual. Per-event values are a controlled vocabulary, enforced by `check-registers.py`: `archive · brief · claim · commit · decision · draft · fan-out · finding · handoff · import · incident · late bug · merge · migration · new client · new default · new fact · new note · prompt · record · release · rename · retry · review · rewrite · rule change · run · session · task · template change`. `EVERY X` and `AT EVERY X` are both legal English forms, but one value may use only one form across the registers. The cross-layer checklist can therefore be derived mechanically without syntax drift; semantic overlap between two declared values remains a review question, not something the parser claims to solve.

## Verification stamps

Each register carries its own `verified:` state in frontmatter. As of 7 August 2026: the instruction layer was verified 6 August 2026 against this machine and repo (stream 78 run 1); the authority layer was read 6 August 2026 against the HullKey project's security register; the context and recovery layers are designs whose install-state markers are provisional and owed a verification pass; the provenance and truth layers describe the HullKey control set and repo checks.

## Why the views look the way they do

[[register-view-design-rationale]] holds the argument behind the presentation: which columns earn a place in a diagram, what each colour and marker encodes, and which encodings were removed and why. Vocabulary is not duplicated there — this file remains the single definition source. Decisions are logged as D-057.

## Downstream views derived from these files

The Figma frames; the cross-layer trigger checklist (group all rows by `trigger`); the install list (all `once` rows, ordered by what each buys); the catch-point map (row counts per position per layer); the tool coverage matrix (tools × the rows they hold).

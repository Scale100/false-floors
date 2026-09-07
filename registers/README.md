# Agent Layer Registers — canon source files

**These files are canon. The Figma diagrams are generated views.** Any scan, correction, or new row lands here first; the diagram is then re-derived (or hand-synced and verified) from the register. Never edit a diagram and leave the register behind — a register/diagram mismatch is a defect in the diagram.

Figma file: `9KIzmsPS1EzWNQiOFKjWzX` (**Diagrams**), page **Page 1**, frame **LIVE Register Diagrams** (`1:2`). Moved into their own file on 2026-08-22, out of a client design-system file they never belonged to. They are drawn on the Scale100 palette as of the rev 3 on-brand rebuild (2026-09-05): the stop-light indicator colours were replaced by a single-hue tint ramp, so the diagrams no longer need a scheme the brand does not carry. Resolve every reference through assets.md's Figma table by stable name; the node IDs below are the current values, not addresses to copy elsewhere.

| Register | Question it asks | Unit of life | Prefix | Figma node | Rows | Evidenced · candidate | State (A·B·C) |
|---|---|---|---|---|---|---|---|
| [instruction-layer](instruction-layer.md) | Did it do what it was told? | a rule | IL | `1:2930` (rev 3) | 22 | 8 · 14 | 2 · 12 · 8 |
| [context-layer](context-layer.md) | Did it know what it needed to know? | a fact | CL | `1:3839` (rev 2) | 22 | 12 · 10 | 0 · 14 · 8 |
| [authority-access-layer](authority-access-layer.md) | What could it reach? | a permission | AL | `1:3386` (rev 2) | 23 | 16 · 7 | 2 · 14 · 7 |
| [recovery-layer](recovery-layer.md) | Can you get it back? | a change | RL | `1:4294` (rev 2) | 24 | 11 · 13 | 4 · 10 · 10 |
| [provenance-layer](provenance-layer.md) | Is the record of what was done trustworthy? | a unit of work | PL | `1:5011` (rev 2) | 22 | 12 · 10 | 3 · 14 · 5 |
| [truth-layer](truth-layer.md) | Can its claims about its own work be trusted? | a claim | TL | `1:4767` (rev 2) | 15 | 8 · 7 | 0 · 9 · 6 |
| execution-capability-layer | Which required properties were violated or absent, and what was observed? | an execution-property assessment | EC | none | 4 | *n/a – incident-derived by construction* | *n/a – no class letters* |

**The State column is A · B · C for every row of this table**, so the six are comparable and the column sums. Read each register's own words off the class-reading table below: Recovery's B · C are recoverable · irreversible, and the other five are detected · survives. The six registers hold 128 rows in total: 11 Class A · 73 Class B · 44 Class C – stated in letters, because no single register's words are true of all six. (Before the D-106 retirement pass of 2026-08-21 the total read 134: six rows were retired or merged, each recorded in its register's own Retired rows section.)

**The headline count is 67 evidenced rows — never 128 (D-107).** Every row carries an evidence status, and the split per register is the Evidenced · candidate column above: **67 evidenced · 61 candidate** across the six. A published count of the framework's failure modes counts the evidenced rows only; candidates are published and labelled, and stated alongside, never inside, the headline number. `check-registers.py` derives the receipts and fails on any row whose marker disagrees with them.

**The seventh register is no longer a stub, and its four rows are deliberately outside that 128.** execution-capability-layer carries `EC-06` and `EC-07`, derived on 2026-08-19, and `EC-08` and `EC-09`, derived on 2026-08-21 — two live incidents, coded against the contract's own row schema. **They are not addable to any total or distribution on this page.** The contract's schema has no class letter, no outcome class, no catch point and no tool tier, so there is nothing for the A · B · C column to hold and nothing for the cross-register sum to absorb; its State cell reads *n/a* rather than a dash, so that no later reader takes an empty cell for an unfilled one. Its own `result` and `gap` vocabulary is defined in the contract, not here, and its `EC-01` to `EC-05` remain calibration cases in the contract rather than rows.

## Row ID rules

1. **IDs are stable and never renumbered.** A newly discovered failure appends a letter inside its stage (IL-1E was added 6 August 2026); nothing else moves. IDs are how scan runs stay comparable and findings stay linkable. **A retired ID is never reused**: a row leaves the counts by moving to its register's Retired rows section with a dated reason (D-106 pass, 2026-08-21 — `IL-3B`, `CL-6C`, `RL-5C`, `RL-6A`, `PL-1B`, `PL-4D`), and any old scan citing the ID still resolves there.
2. **PL and TL IDs are assigned by these registers**, not by the diagrams — the provenance and truth frames predate the ID scheme, and both adopted the register IDs at their rev 2 on 9 August 2026. PL rows are numbered by category order (1 orientation and continuity, 2 claiming the work, 3 the record itself, 4 linking intent to code, 5 landing, 6 many agents); TL rows keep the diagram's claim numbers (TL-01 to TL-15).

## Reading the `C-` and `D-` citations

Rows and prose here cite identifiers of the form **`C-nn`** and **`D-nnn`**. They are entries in this project's **Corrections Register** (its own defect list) and **Decision Log**, and **neither of those files is published**. They are cited so that every claim in these registers has a checkable provenance on our side; they are not links, and following them is not possible from the published catalogue.

They are kept rather than stripped because a claim whose origin is named is more honest than one asserted flat, even when the reader cannot open the source. Where the substance matters to an outside reader it is stated in the row itself, not left to the citation. `EC-nn` refers to the Execution and Capability register, also unpublished — see the note above on why it is held back.

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

What this does **not** fix: the catch ladder still mixes four kinds of position (C-11), and lifecycle stage still has no classification rule (C-12). Those are separate rows and stay open. (Severity was a third such row — C-08, two incompatible scales sharing one name — and was repaired on 28 August 2026 under D-205; see the Severity entry below.) "The registers share one vocabulary" remains an overclaim.

**Evidence** (added D-107, 21 August 2026) — whether reality has confirmed the row, and the field that sets what a headline count may claim:

- **evidenced** — at least one receipt exists. Three receipt types count, and nothing else does: a first-party incident mapped in the Corrections Register with an `⟪instance-of⟫` marker; a corpus-coded finding from the 262-item calibration pass (run 22) graded exact or variant; or a verifiable public field case with a dated, checkable citation filed in the vault.
- **candidate** — enumerated in advance, no receipt yet. Still a row: published, classed, graded, labelled. Not counted in any headline.

Three rules follow, all enforced or exercised by `check-registers.py`:

1. **Headline counts count evidenced rows only.** On the receipts as at 2026-08-25 that is 67 evidenced · 61 candidate. The evidenced number moves only when a receipt lands or a row retires, so it is grounded by construction.
2. **The marker is derived, not asserted.** The checker re-derives the receipt sets from the Corrections Register and the run-22 table on every run and fails on any row whose Evidence cell disagrees — in either direction, because an understated 66 is as wrong as an overstated one.
3. **Promotion and decay.** A candidate is promoted by its first receipt. A candidate that a stated review window passes over with no instance, no corpus match and no field case is retired to the candidate pen ([truth-layer](truth-layer.md), "Candidate rows, not yet evidenced" — the pen holds gaps that are not yet rows, which is one step below a published candidate row).

Enumeration is thereby demoted from row source to hypothesis source: it proposes candidates, and its track record is published — of the 113 rows standing as unconfirmed predictions at enumeration, 23 (about one in five) were confirmed by a first dated incident within eleven days, in the derivation environment ([METHODOLOGY](../METHODOLOGY.md) section 4 carries the denominator, the dates and the scope caveats). It never again sets a published total. Full rationale and the decision: [METHODOLOGY](../METHODOLOGY.md) and D-107.

**Severity** — the cost of the failure multiplied by how silently it fails; a judgement, not a measurement. **One construct, two domain readings** (D-205, 28 August 2026 — the C-08 repair, built on C-06's precedent): every register multiplies by silence, and they differ only in what *cost* reads as.

| Grade | Five aligned registers read cost as **the wrong outcome** | Recovery reads cost as **getting back** |
|---|---|---|
| **S1** | a round trip, noticed at once | undone in seconds |
| **S2** | rework you catch at review | undone with effort |
| **S3** | real rework or a wrong outcome, found late | undone only by rebuilding by hand |
| **S4** | it ships, and you never find out | cannot be undone at any price |

**The grade travels; the cost term is local.** This is the same standing the outcome letter has: an S4 anywhere means *this register's most expensive failure, arriving in silence*, so S-grades sort and rank across registers. What never travels is the cost term itself — Recovery's S4 is not "a worse Instruction S4", it is the same grade of a different cost.

**Two limits, both load-bearing.** It is a judgement, not a measurement, so **no count, total or published claim may rest on it** — the rationale removed severity from the diagram views for exactly this reason and reserved it for filtering and sorting. And it is not derived by any checker: `check-registers.py` does not validate severity, so a wrong S-grade is caught by reading, not by running.

*What this repaired.* Until 28 August this section read *"The recovery layer grades the same scale by cost-to-undo"*, which named one scale and described two — cost × silence in five registers, cost-to-undo alone in Recovery — so an S3 could not be compared across the boundary. That was **C-08**. The repair is a correction to this file only: [recovery-layer](recovery-layer.md) itself already read *"the cost of getting back multiplied by how quietly the change goes unnoticed"*, and so did the published Recovery spoke. This summary was the only surface still carrying the broken definition, which makes C-08 an instance of C-50's class — the README drifting from the register it summarises.

**Tool tier** — prefer a tool that maintains itself, over a tool you maintain, over a process you remember:
- **automatic** — runs itself, nothing to maintain
- **maintained** — only as good as the file you keep current
- **process** — you have to remember, every time

**Availability** — does a control of this shape exist at all. **This is a claim about the world, not about anyone's setup** (D-263), and it is the only thing the catalogue says about a control's existence:

- **available** — a control of the named shape exists and can be obtained or built today
- **none** — no control of this shape exists anywhere; the row survives on a convention or on nothing, which is what Class C means
- **withdrawn** — one existed and no longer does, because it was discontinued, unmaintained or removed from the platform it lived in

The four aligned row registers carry it as the last term of the `Tool` cell; the truth register carries it as its own column. **Provenance carries none**, because it has three control positions rather than one named mechanism and no cell to put it in — a declared gap, not an oversight.

**Availability is not maturity.** A control can be available and immature, available and awkward, available and rarely used. Grading that would be a judgement, and this framework does not let a judgement carry a count — the same limit severity carries. Where maturity matters it belongs in [controls-reference](controls-reference.md)'s prose.

*What this replaced, and why it was not simply renamed.* Until 2026-09-07 this section defined **built state** — `built` · `designed` · `none` — scoped by D-058 to the single codebase the registers were derived from. That is one operator's install state, and it published: 84 cells across the six registers carried it, with nothing beside them to say whose environment or on what date. `TL-09` is the receipt. It read `not built` for mutation and property testing while both had been running in that codebase's CI for weeks, and nothing announced the staleness, because a status column does not announce its own age. Under D-263 the distinction that survives is *a control of this shape exists*; the distinction that left is *is it switched on here*, which is now an assessment.

**Gap, and where it went.** Gap said what was actually true about a failure today — `closed` · `closed by substitute` · `partially closed` · `open` — and it is **not in these registers any more** (D-263). It was never independent of install state: 122 of its 128 values were derived from the outcome letter and the built state of the named mechanism, so removing built state left it uncomputable for all but the six `partially closed` rows that were entered by hand. It lives in an assessment now, with its derivation rules, the compensating-control receipt requirements and the C-02 install gate intact and enforced by `tools/check-assessment.py`.

**Where to read one.** `../assessments/` holds the assessment records, and `assessment-001-project-alpha.json` is this framework's own — the derivation codebase, scored on the dates each register's `derived:` line names. `tools/diff-catalogue.py` reports what has changed in the catalogue since any assessment was taken.

**Authority** — who can switch the control off:
- **unbypassable** — runs where the agent cannot reach it
- **bypassable** — a login, a local hook, or a settings file the agent can edit

**Catch point** — where in the turn the failure is caught, earliest to latest: `on disk · session start · prompt · pre-tool · subagent · post-tool · compact · stop · pre-commit · CI · review`. Prevention lives only where the mechanism can refuse; the earlier it refuses, the less has already been spent. The provenance layer uses its own three positions instead: **harness gate** (at the moment of work) · **repo artefact** (committed with the code) · **control-plane check** (on the commit).

**Provenance cell key** — per control position: **closes** (refuses or catches it every time) · **partial** (conditional, or not switched on) · **nothing** (nothing here closes it) · **n/a** (not this layer's job).

**Trigger** — how often the operator must act. The field parses to a kind and a value: `once` is an install; `done` is a dated completion; `weekly` / `monthly` / `quarterly` / `annually` are cadences; `every` is a per-event ritual. Per-event values are a controlled vocabulary, enforced by `check-registers.py`: `archive · brief · claim · commit · decision · draft · fan-out · finding · handoff · import · incident · late bug · merge · migration · new client · new default · new fact · new note · prompt · record · release · rename · retry · review · rewrite · rule change · run · session · task · template change`. `EVERY X` and `AT EVERY X` are both legal English forms, but one value may use only one form across the registers. The cross-layer checklist can therefore be derived mechanically without syntax drift; semantic overlap between two declared values remains a review question, not something the parser claims to solve.

## Provenance stamps

Each register carries a `derived:` line in frontmatter saying **where its rows came from and when** — the source read, the date, and any row whose behaviour was read from vendor documentation rather than observed. That is a fact about the catalogue and it does not go stale as environments change.

It replaced a `verified:` line on 2026-09-07 (D-263). The old stamp mixed catalogue provenance with install verification — two of the six still read "against this machine", and two described install-state markers as provisional and owed a verification pass. Those are facts about one environment on one date, and they are kept verbatim in `../assessments/assessment-001-project-alpha.json` under `registerVerification` rather than rewritten or dropped.

**What a `derived:` line does not claim.** It does not say the rows are complete, and it does not say any control is installed anywhere. Completeness is what the evidence column and the prediction record speak to; installation is what an assessment says.

## Why the views look the way they do

register-view-design-rationale holds the argument behind the presentation: which columns earn a place in a diagram, what each colour and marker encodes, and which encodings were removed and why. Vocabulary is not duplicated there — this file remains the single definition source. Decisions are logged as D-057.

## Downstream views derived from these files

The Figma frames; the cross-layer trigger checklist (group all rows by `trigger`); the install list (all `once` rows, ordered by what each buys); the catch-point map (row counts per position per layer); the tool coverage matrix (tools × the rows they hold).

---

*False Floors is a trade mark of Digital First Pty Ltd, trading as Scale100 (AU application AMCZ-2616155657). This content is CC BY 4.0; the name is not part of that licence. Citing, mapping to, or claiming conformance with the catalogue needs no permission – see `LICENSE-CONTENT`.*

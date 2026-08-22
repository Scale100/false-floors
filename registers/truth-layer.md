---
type: register
project: agent-trust-framework
layer: truth
prefix: TL
title: Agent Truth Layer — Claims, Costs, Controls and Resolution
question: Can its claims about its own work be trusted?
unit: a claim
figma-node: "1392:139"
figma-file: KDkIqr0lzbcAUvJLGAcExk
rows: 15
class-a: 0
class-b: 9
class-c: 6
class-a-reads: prevented
class-b-reads: detected
class-c-reads: survives
evidenced: 8
candidate: 7
verified: describes the HullKey repo's check suite; row IDs are assigned by this register — the diagram adopted the TL-prefixed IDs at rev 2 on 9 August 2026, replacing its 1–15 claim numbers
residual-basis: derived from outcome x built state on 2026-08-09 (D-061); substitutes and partial closures entered by hand only where evidenced
date: 2026-08-07
last-updated: 2026-08-21
---

# Agent Truth Layer: claims, costs, controls and resolution

Every claim an agent makes about its own work — what it costs if the claim is false, and the strongest control available to retire it.

**This file is canon; the Figma frame `1392:139` (rev 2) is a generated view.** Shared vocabulary: [[README|registers README]].

**Class grades how complete the remedy is**, on the shared definition in [[README|registers README]]: A the failure cannot occur, B it occurs and something handles it completely, C it occurs and no remedy is complete. **This register reads B as *detected* and C as *survives***, the same words as Instruction, Context, Authority and Provenance – its section titles (*By construction*, *Checkable*, *Judgement*) name the classes but are not the outcome vocabulary, and must not be quoted as if they were. Class is therefore a property of a claim **once a control has been applied**, not a property of the tool: the same assertion sits in a different class depending on what was withheld, executed or diffed, because what changes is the completeness of the remedy available to it. Control status — five values, and the register uses all five: **in force** — control in force today · **not on** — built or designed, not switched on · **not built** — the mechanism does not exist yet · **not provisioned** — designed, and the resource it needs has not been created · **none** — no control exists, judgement only. **Residual** is derived from status: `in force` reads closed (or partially closed where the control itself is marked partial); **every other value reads open**. Until 2026-08-10 this note declared only three of the five while TL-09 used `not built` and TL-10 used `not provisioned` (C-04); the vocabulary is now declared to match the rows, and `check-registers.py` enforces both the enum and the derivation. **Evidence** — `evidenced` (a receipt exists: a first-party incident mapping, a corpus-coded finding, or a filed public case) or `candidate` (enumerated in advance, no receipt yet); headline counts count evidenced rows only (D-107, [[README|registers README]]). Evidence status here: 8 of the 15 claims are evidenced, 7 are candidates — a high share for a register this size, which follows from its construction: the rows were inventoried from a live CI suite rather than enumerated. **Residual** says what is actually true about the failure today, which is not the same as whether the named mechanism exists — see [[README|registers README]].

## Class A · By construction (0 claims)

Conversion: **withhold it** — the capability, the information, or the seat. Outcome: **prevented — the action is refused; nothing to check.** Class is a property of the mechanism, so a claim sits here once a withholding control is *designed* for it; whether that control is switched on today is what `Status` and `Residual` say, row by row. Residual owner: **the control** — revisit only if it is removed.

No current claim has a verified withholding control that makes the claimed failure impossible. A claim belongs here only when capability, information or seat assignment is withheld by a boundary the assessed agent cannot alter or route around.

## Class B · Checkable (9 claims · 7 controls in force · 2 not built)

Conversion: **execute it, then diff it** — commit the output, not the claim. Outcome: **detected — CI fails on every commit.** Residual owner: **CI** — you read the red, not the code.

| ID | Evidence | Sev | Claim | What it costs if it’s wrong | Control applied | Status | Residual |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TL-01 | candidate | S3 | “The tests pass” | Test written to fit the code | CI test-write-protection check | in force | closed |
| TL-02 | evidenced | S2 | “This is what I changed” | Account revised after the fact | Git diff and history check | in force | closed |
| TL-04 | evidenced | S4 | “I verified it” | Never ran; the claim is the only proof | test:flows · pgTAP · test:unit | in force | closed |
| TL-05 | evidenced | S3 | “The generated file is current” | Stale artefact; downstream built on it | tokens:check · agents:check · types:check | in force | closed |
| TL-06 | candidate | S4 | “This wording is approved” | Unapproved claim ships to customers | claims:check | in force | closed |
| TL-07 | candidate | S2 | “The architecture is respected” | Boundary crossed; coupling sets in | deps:check · lint:i18n | in force | closed |
| TL-08 | candidate | S4 | “The UI is accessible” | Keyboard and screen reader locked out | a11y:check (axe-core) | in force | closed |
| TL-09 | evidenced | S4 | “The tests are good” | Suite passes with the logic deleted | mutation + property testing | not built | open |
| TL-10 | evidenced | S3 | “I didn’t game the tests” | Optimised for the suite, not the job | Held-out suite | not provisioned | open |

Next action: NEXT BUILD — build the two missing suites: property tests; provision the held-out suite. Catches drift and regression on every commit. Proves that behaviour was executed, never that the design was the right one.

## Class C · Judgement (6 claims · no complete control · judgement remains)

Conversion: **nothing converts it** — independent re-derivation (second-vendor audit, independent human review) reduces the risk without retiring it. Outcome: **survives — no tool retires it.** Residual owner: **you** — brief it decision by decision.

| ID | Evidence | Sev | Claim | What it costs if it’s wrong | Control applied | Status | Residual |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TL-03 | evidenced | S4 | “The audit was independent” | Same model graded its own work | Model-seat separation · partial | not on | open |
| TL-11 | evidenced | S3 | “This finding is real” | Real defect dropped, phantom worked | Independent re-derivation | none | open |
| TL-12 | candidate | S3 | “The data model is right” | Wrong boundary; migrations compound | Independent re-derivation | none | open |
| TL-13 | candidate | S4 | “The RLS design is sound” | Green tests on a policy that leaks | second-vendor audit · human review | none | open |
| TL-14 | evidenced | S4 | “This claim is safe to make” | Unsupportable claim published | Independent re-derivation | none | open |
| TL-15 | candidate | S4 | “The residual risk is acceptable” | Risk accepted that nobody chose | Independent re-derivation | none | open |

Next action: EVERY DECISION — brief it yourself: six claims, one judgement each. Class C is not a backlog. It is the part of the work that was never delegable. Verifying these needs independent judgement and, for TL-03, an externally enforced seat assignment before any narrower by-construction claim can be made.

## The catch — an assertion and its evidence read identically

An agent that ran the suite and an agent that says it ran the suite produce the same sentence. The difference is never in the writing, only in whether the output was committed. That is why every mechanism above is “commit the artefact”, not “improve the wording” — and why anything that cannot be committed stays on your desk.

## Candidate rows, not yet evidenced

Gaps surfaced by other work against this register, named here so they survive past the session that found them. Not rows — nothing here carries a class, a control, or a status until an actual instance exists to derive them from. This is the **candidate pen** in D-107's decay rule, and it sits *below* the published rows: a published row whose Evidence cell reads `candidate` is still a row, counted and classed; an entry here is not a row at all. A stale published candidate is retired into this pen; a pen entry is promoted straight to an evidenced row by its first receipt.

**A standing capability claim — "I can do this kind of work."** Surfaced 2026-08-17 during the uncanny-workforce essay's reconciliation pass. Distinct from every current row: TL-01 through TL-15 all concern a specific completed unit of work (TL-04 "I verified it", TL-06 "this wording is approved"); none concern a claim about the agent's own general ability, made independent of any particular task, and asserted with the same fluent confidence whether true or not. Confirmed as Truth-shaped rather than Execution-and-Capability-shaped by that register's own discriminator (`registers/execution-capability-layer.md`, "The discriminator"): the defect exists only because a statement was made — with no statement, there is no over-confidence to name, only the underlying task failure, which is EC's territory, not this one. Owed before it becomes a row: a reproducible instance — an agent asserting general capability in a domain, contradicted by later observed performance in that same domain, no third-party evidence involved. Reasoning in full: `content/essay/essay-draft-uncanny-workforce-2026-08-11.md`, "Section map" and the capability-disclosure draft note at the foot of that file.

## Reading notes

The mildest severity band is empty. Nothing on this chart fails loudly enough to notice on the day — that is what makes it a truth layer rather than a bug list.

Independent re-derivation is drawn inside Class C on purpose. Two sources agreeing is probability, not certainty — correlated blind spots survive it.

Severity grades what it costs when the claim is false, on the same scale as the instruction layer: cost multiplied by how silently it fails, a judgement, not a measurement.

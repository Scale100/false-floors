---
type: register
project: agent-trust-framework
layer: truth
prefix: TL
# The column holding the failure title. Declared rather than inferred from
# position: C-117 shipped a gate that took the column after `Sev`, and a metadata
# column inserted between the two silently replaced every title while the gate
# reported ok. Identity survives insertion and reordering; adjacency does not.
title-column: Claim
title: Agent Truth Layer — Claims, Costs, Controls and Resolution
question: Can its claims about its own work be trusted?
unit: a claim
figma-node: "71:2"
figma-file: 9KIzmsPS1EzWNQiOFKjWzX
rows: 15
class-a: 0
class-b: 9
class-c: 6
class-a-reads: prevented
class-b-reads: detected
class-c-reads: survives
evidenced: 10
candidate: 5
derived: 2026-08-06 — rows describe project-alpha’s check suite; row IDs are assigned by this register, and the diagram adopted the TL-prefixed IDs at rev 2 on 2026-08-09, replacing its 1–15 claim numbers
gap-basis: derived from outcome x built state on 2026-08-09 (D-061); substitutes and partial closures entered by hand only where evidenced
date: 2026-08-07
last-updated: 2026-08-23
---

# Agent Truth Layer: claims, costs, controls and resolution

Every claim an agent makes about its own work — what it costs if the claim is false, and the strongest control available to retire it.

**This file is canon; the Figma frame `1:4767` (rev 2) is a generated view.** Shared vocabulary: [registers README](README.md).

**Class grades how complete the remedy is**, on the shared definition in [registers README](README.md): A the failure cannot occur, B it occurs and something handles it completely, C it occurs and no remedy is complete. **This register reads B as *detected* and C as *survives***, the same words as Instruction, Context, Authority and Provenance – its section titles (*By construction*, *Checkable*, *Judgement*) name the classes but are not the outcome vocabulary, and must not be quoted as if they were. Class is therefore a property of a claim **once a control has been applied**, not a property of the tool: the same assertion sits in a different class depending on what was withheld, executed or diffed, because what changes is the completeness of the remedy available to it. Control status — five values, and the register uses all five: **in force** — control in force today · **not on** — built or designed, not switched on · **not built** — the mechanism does not exist yet · **not provisioned** — designed, and the resource it needs has not been created · **none** — no control exists, judgement only. **Availability** says whether a control of the named shape exists at all — `available` · `none` · `withdrawn`. Until 2026-09-07 this column was `Status`, five values deep, and four of them (`in force` · `not on` · `not built` · `not provisioned`) described whether the control was switched on in the codebase these rows were derived from. That is one environment on one date, it went stale silently — `TL-09` published `not built` while mutation and property testing were running in that codebase's CI — and under D-263 it moved to an assessment. What survives here is the claim about the world: a control of this shape exists, or none does. **Evidence** — `evidenced` (a receipt exists: a first-party incident mapping, a corpus-coded finding, or a filed public case) or `candidate` (enumerated in advance, no receipt yet); headline counts count evidenced rows only (D-107, [registers README](README.md)). Evidence status here: 8 of the 15 claims are evidenced, 7 are candidates — a high share for a register this size, which follows from its construction: the rows were inventoried from a live CI suite rather than enumerated.

## Class A · By construction (0 claims)

Conversion: **withhold it** — the capability, the information, or the seat. Outcome: **prevented — the action is refused; nothing to check.** Class is a property of the mechanism, so a claim sits here once a withholding control is *designed* for it; whether that control is switched on today is what `Status` and `Gap` say, row by row. Gap owner: **the control** — revisit only if it is removed.

No current claim has a verified withholding control that prevents the claimed failure by construction. A claim belongs here only when capability, information or seat assignment is withheld by a boundary the assessed agent cannot alter or route around.

## Class B · Checkable (9 claims · 7 controls in force · 2 not built)

Conversion: **execute it, then diff it** — commit the output, not the claim. Outcome: **detected — CI fails on every commit.** Gap owner: **CI** — you read the red, not the code.

| ID | Evidence | Sev | Claim | What it costs if it’s wrong | Control applied | Availability |
| --- | --- | --- | --- | --- | --- | --- |
| TL-01 | candidate | S3 | “The tests pass” | Test written to fit the code | CI test-write-protection check | available |
| TL-02 | evidenced | S2 | “This is what I changed” | Account revised after the fact | Git diff and history check | available |
| TL-04 | evidenced | S4 | “I verified it” | Never ran; the claim is the only proof | End-to-end · unit · pgTAP database tests | available |
| TL-05 | evidenced | S3 | “The generated file is current” | Stale artefact; downstream built on it | Regenerate-and-byte-diff on generated files | available |
| TL-06 | evidenced | S4 | “This wording is approved” | Unapproved claim ships to customers | Approved-claims check on published wording | available |
| TL-07 | candidate | S2 | “The architecture is respected” | Boundary crossed; coupling sets in | Dependency-boundary and i18n lint | available |
| TL-08 | candidate | S4 | “The UI is accessible” | Keyboard and screen reader locked out | Automated accessibility scan (axe-core) | available |
| TL-09 | evidenced | S4 | “The tests are good” | Suite passes with the logic deleted | mutation + property testing | available |
| TL-10 | evidenced | S3 | “I didn’t game the tests” | Optimised for the suite, not the job | Held-out suite | available |

What this class buys, and what it does not: executable evidence catches drift and regression on every commit, and proves that behaviour was executed — never that the design was the right one. Which of these suites exists in any particular environment is an assessment, not a property of the class.

## Class C · Judgement (6 claims · no complete control · judgement remains)

Conversion: **nothing converts it** — independent re-derivation (second-vendor audit, independent human review) reduces the risk without retiring it. Outcome: **survives — no tool retires it.** Gap owner: **you** — brief it decision by decision.

| ID | Evidence | Sev | Claim | What it costs if it’s wrong | Control applied | Availability |
| --- | --- | --- | --- | --- | --- | --- |
| TL-03 | evidenced | S4 | “The audit was independent” | Same model graded its own work | Model-seat separation · partial | available |
| TL-11 | evidenced | S3 | “This finding is real” | Real defect dropped, phantom worked | Independent re-derivation | none |
| TL-12 | candidate | S3 | “The data model is right” | Wrong boundary; migrations compound | Independent re-derivation | none |
| TL-13 | evidenced | S4 | “The RLS design is sound” | Green tests on a policy that leaks | second-vendor audit · human review | none |
| TL-14 | evidenced | S4 | “This claim is safe to make” | Unsupportable claim published | Independent re-derivation | none |
| TL-15 | candidate | S4 | “The remaining risk is acceptable” | Risk accepted that nobody chose | Independent re-derivation | none |

Each of these claims needs a judgement of its own, at every decision, briefed rather than delegated. Class C is not a backlog. It is the part of the work that was never delegable. Verifying these needs independent judgement and, for TL-03, an externally enforced seat assignment before any narrower by-construction claim can be made.

## The catch — an assertion and its evidence read identically

An agent that ran the suite and an agent that says it ran the suite produce the same sentence. The difference is never in the writing, only in whether the output was committed. That is why every mechanism above is “commit the artefact”, not “improve the wording” — and why anything that cannot be committed stays on your desk.

## Candidate rows, not yet evidenced

Gaps surfaced by other work against this register, named here so they survive past the session that found them. Not rows — nothing here carries a class, a control, or a status until an actual instance exists to derive them from. This is the **candidate pen** in D-107's decay rule, and it sits *below* the published rows: a published row whose Evidence cell reads `candidate` is still a row, counted and classed; an entry here is not a row at all. A stale published candidate is retired into this pen; a pen entry is promoted straight to an evidenced row by its first receipt.

**A standing capability claim — "I can do this kind of work."** Surfaced 2026-08-17 during the uncanny-workforce essay's reconciliation pass. Distinct from every current row: TL-01 through TL-15 all concern a specific completed unit of work (TL-04 "I verified it", TL-06 "this wording is approved"); none concern a claim about the agent's own general ability, made independent of any particular task, and asserted with the same fluent confidence whether true or not. Confirmed as Truth-shaped rather than Execution-and-Capability-shaped by that register's own discriminator (`registers/execution-capability-layer.md`, "The discriminator"): the defect exists only because a statement was made — with no statement, there is no over-confidence to name, only the underlying task failure, which is EC's territory, not this one. Owed before it becomes a row: a reproducible instance — an agent asserting general capability in a domain, contradicted by later observed performance in that same domain, no third-party evidence involved. Reasoning in full: `content/essay/essay-draft-uncanny-workforce-2026-08-11.md`, "Section map" and the capability-disclosure draft note at the foot of that file.

## Reading notes

The mildest severity band is empty. Nothing on this chart fails loudly enough to notice on the day — that is what makes it a truth layer rather than a bug list.

Independent re-derivation is drawn inside Class C on purpose. Two sources agreeing is probability, not certainty — correlated blind spots survive it.

Severity grades what it costs when the claim is false, on the same scale as the instruction layer: cost multiplied by how silently it fails, a judgement, not a measurement.

---

*False Floors is a trade mark of Digital First Pty Ltd, trading as Scale100 (AU application AMCZ-2616155657). This content is CC BY 4.0; the name is not part of that licence. Citing, mapping to, or claiming conformance with the catalogue needs no permission – see `LICENSE-CONTENT`.*

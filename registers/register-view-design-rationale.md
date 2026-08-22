---
type: design-rationale
project: agent-trust-framework
title: Register View Design Rationale — why the diagrams look the way they do
status: draft
scope: all six register diagrams
date: 2026-08-09
last-updated: 2026-08-10
---

# Register view design rationale

**What this file is.** The argument behind the *presentation* of the six registers: which columns earn a place in a diagram, what each colour and marker encodes, and which encodings were removed and why. It exists so those choices can be debated on the record instead of relitigated every time a frame is edited.

**What this file is not.** It is not the data and it is not the vocabulary. The registers in this folder are canon; the Figma frames are generated views. The definitions of prevented, detected and survives — along with severity, tool tier, built state, authority, catch points and triggers — live once, in [[README|registers README]], and are deliberately **not** copied here. A second copy of a definition is a second thing that can drift.

**Status: draft, for debate.** Nothing below is a chosen decision until it is logged in [[Decision Log]].

---

## 1. The load-bearing claim: catch point

The catch point is the column that separates these registers from the security-organised frameworks. It is the only column that asks *when in the agent's turn* the failure is caught, and therefore how much has already been spent by the time anyone knows. Prevention exists only where a mechanism can refuse; everything to the right of that is undoing rather than preventing. That is why the instruction layer was restructured on 8 August 2026 to give the catch point its own aligned column rather than burying it as a tag above the mechanism sentence.

**One correction to how this gets stated, and it matters.** It is tempting to say "the catch point is the main difference between our schema and the security frameworks". That is the broad form, and the broad form is dead — killed by the 8 August adversarial review and retired in [[Decision Log|D-052]]. ARC (arXiv 2512.22211) and Agentic Risks both publish row-level agentic risk registers with failure modes, controls and residual scoring. The claim that survived is a five-way conjunction, and D-052 requires that all public claims use it:

> No published register we found combines **lifecycle stage × catch-point position inside the agent's turn × prevented/detected/survives as a property of the mechanism × residual state**, at single-coding-agent harness depth.

So the catch point is one of five conjuncts, not the differentiator on its own. It is fair to call it the most *visible* and most *teachable* of the five, and the one a reader grasps fastest, but a brief that promotes it to "the main difference" re-opens a claim that was deliberately narrowed and would have to be narrowed again under review.

The reason the security actors do not have this column is structural rather than accidental, and is already recorded in [[Decision Log|D-053]]: their organising question is adversarial ("is the agent attacked, rogue, or out of bounds?"), and an adversarial question does not need to know whether a control fires at pre-tool or at CI, only whether it fires. Ours is a non-adversarial trust question, where *when* changes the answer.

---

## 2. Why each column earns its place

The test applied to every column: **does removing it change a decision the reader would make?** A column that only adds context fails the test and becomes a legend row the reader has to hold.

| Column | The decision it changes | Verdict |
|---|---|---|
| **What you see** (symptom) | Whether the reader can find their row at all. They arrive holding a symptom, not a diagnosis. | Earns it — and earns being first |
| **Why** (ID + failure) | What is actually broken, plus the stable row ID that makes scan runs comparable and findings linkable across time (see row ID rules in [[README|registers README]]) | Earns it |
| **Catch point** | How much has already been spent when this is caught, and therefore whether the work is to move it left | Earns it — see section 1 |
| **Tool** | What to install, and at which tier of maintenance burden | Earns it |
| **The mechanism** | Whether the check watches the failure or a proxy for it. IL-3A, IL-5C and IL-6A all have checks that watch the wording, the link and the declaration rather than the failure. | Earns it |
| **Outcome** | Everything. Prevented, detected and survives is the spine every count on the page is drawn from. | Earns it |
| **Your action** + trigger | The only column that produces work. The trigger is what the cross-layer checklist is derived from, so it cannot drift from the registers. | Earns it |

### The column that was removed

**"How to prevent it" failed the test and was cut on 8 August 2026.** It sat between the mechanism and the action and was squeezed flat by both. Six of twenty-three rows restated the mechanism almost verbatim (IL-1D, IL-1F, IL-3B, IL-4B, IL-5A, IL-6C), roughly ten more overlapped heavily, and IL-3C's prevention text was word-for-word identical to its own next action. The seven rows where it genuinely added something were all cases where the mechanism watches a proxy, and the mechanism column already carries that nuance in better words.

**Canon keeps the field.** The `Prevention` column still exists in every register file. This is a view decision, not a data deletion: the registers hold the full record, and a diagram shows the subset that changes a decision. That distinction is the whole reason the register/view split exists.

---

## 3. Colour and encoding rationale

Two governing rules, both learned the hard way on the instruction-layer frame:

1. **An encoding must feed a conclusion the diagram itself draws.** If no count, no total and no closing paragraph rests on it, it is decoration that costs the reader a legend row.
2. **No two encodings may share a colour.** Sharing one makes the diagram actively misleading, not merely busy.

### Encodings that survive

| Encoding | Where | What it means | The conclusion it feeds |
|---|---|---|---|
| **Outcome** | Outcome chip: green solid, yellow solid, red dashed | Prevented / detected / survives | Every per-stage count, the totals, and "the six that still reach you" |
| **Tool tier** | Tool chip: filled, outlined, or absent | Automatic / maintained / process | "Prefer a tool that maintains itself, over a tool you maintain, over a process you remember" |
| **Trigger cadence** | Action cell: green, yellow, red | Once / on an interval / every single time | The install-versus-ritual split, and the cross-layer checklist |
| **Built state** | Amber 5px left edge marker | Designed, not installed | "12 of the 21 are not built in `hullkey-charge` today", and it is the only per-row record of what actually exists |
| **Catch-point earliness** | Catch-point tag: green through red | Earliest to latest in the turn | Reinforces the ladder and "the work is to move each row left" |

The dashed border on **survives** is deliberate redundancy with its colour, and is the one place redundancy is wanted: it is the state the whole framework exists to surface, and it must survive a greyscale print and a colour-blind reader.

### Encodings that were removed, and why

**Severity (four-step red ramp on the leftmost column).** Removed 8 August 2026. It failed rule 1: no count, total or closing paragraph on the frame rested on it, and the frame's own footnote conceded it is "a judgement, not a measurement". It also broke rule 2 — its third step was `#c00`, the same red as **survives** — so the visually loudest rows read as "this one gets through" when mostly they do not. Of the six instruction-layer rows that actually survive, two are pale yellow and two are amber. The most prominent colour on the page was pointing the wrong way. **S1–S4 is retained in canon** and can return to a view as a filter or a sort, which is what a judgement scale is actually good for.

**Authority (green/red swatches).** Removed from the instruction-layer frame only. It was applied to zero instruction-layer rows — the register has no authority column, by design — while its swatches duplicated the outcome colours exactly. It remains a real and load-bearing encoding on [[authority-access-layer]], which does carry an Authority column and where eleven of twenty-three rows are enforced beyond the agent's reach. The lesson is narrower than "drop authority": a shared legend must not advertise an encoding a given view does not use.

**Runtime sub-label colour.** Removed. Two greys applied across twenty-three rows with six off-pattern, encoding nothing the word beside it did not already say. An inconsistent tonal difference reads as meaningful and is worse than no difference at all.

**Best-case to worst-case gradient bar.** Removed. It restated the "best on the left, worst on the right" line already in the how-to-read box.

### Legend order

The legend blocks are ordered widest first (catch point spans the full frame width, outcome and tool are half-width), so the widest block sets the edge and the narrow rows tuck beneath it. This is presentation only and carries no meaning.

---

## 4. Open questions for debate

1. **Is the catch point the primary differentiator, or one of five conjuncts?** D-052 says the latter and binds public claims to the narrow form. If the position has genuinely moved, that needs a new Decision Log entry reversing part of D-052, not a quiet restatement in a brief.
2. **Should severity return as a filter rather than a fill?** The data is in canon and unused by any view.
3. ~~**Do the other five frames adopt the rev 3 column set?**~~ **Settled 9 August 2026 — yes, all five were brought across.** See the view decision log below for what applied to each and the three cases where a shared item deliberately did not.
4. **Does the amber built-state marker survive its own success?** Once most rows are built it marks the exception rather than the rule, and the sensible inversion is to mark what *is* built.
5. **Named mechanism versus closure of the failure** — the live one. Full argument in section 7.

---

## 5. View decision log

| Date | Frame | Decision |
|---|---|---|
| 2026-08-08 | Instruction (`1358:139`, rev 3) | Cut "how to prevent it"; promote catch point to its own column; put the symptom first; drop severity, authority, runtime-label colour and the gradient bar; drop the Class A/B/C letters from the outcome legend; reorder legends widest-first |
| 2026-08-09 | Authority and Access (`1379:139`, rev 2) | Brought onto the rev 3 column set: symptom column first, catch point promoted to its own aligned column at x960, "how to prevent it" cut, severity fill replaced by a neutral cell with the row ID in bold, runtime sub-labels and the gradient bar removed, legends reordered widest-first, Class letters dropped from the outcome legend, headers conformed (`PROCESS` → `THE MECHANISM`, `NEXT ACTION` → `YOUR ACTION`). **Authority kept, as this layer's exception** — see the note below. The severity footnote was rewritten as a provenance note, since the encoding it explained is no longer on the frame. Supersedes `1317:19795` (retained) |
| 2026-08-09 | Context (`1386:139`, rev 2) | Same conformance pass, no structural exception. The **authority legend was removed** — this layer has no authority column and applies the encoding to zero rows, which is the rule D-057 set on the instruction frame. Every stale layer name was rewritten: the frame was built from an instruction-layer copy and 364 layers still carried `il_` prefixes and instruction-layer text as their names, while their content was correct context-layer content. The severity footnote was cut back to the layer-contrast sentence it also carried. Supersedes `1315:139` (retained) |
| 2026-08-09 | Recovery (`1389:139`, rev 2) | Same conformance pass on 25 rows. **Exception honoured:** the outcome triad stays prevented · recoverable · irreversible, and the severity scale it grades by cost-to-undo was already gone with the severity legend. Class letters dropped from the outcome legend, but the recovery wording kept. The authority legend was removed — no authority column in this register, zero rows encoded. No runtime sub-labels existed to remove; this layer's tool cells were always runtime-agnostic. The severity footnote was cut back to its second half, which is the provisional-markers warning, so that warning survives on the frame. Supersedes `1326:139` (retained) |
| 2026-08-09 | Truth (`1392:139`, rev 2) | **ID migration done:** all fifteen claims now carry their register IDs, `TL-01` to `TL-15`, bold-prefixed as on rev 3, at 12pt so the longer IDs keep their padding. Class A/B/C vocabulary kept throughout, per the exception. Gradient bar removed; `NEXT ACTION` → `YOUR ACTION`; the claim and cost layer names, which still carried pre-renumbering IDs, were rewritten. **Most of the rev 3 column set does not apply here** — see the note below. Supersedes `1169:2` (retained) |
| 2026-08-09 | Provenance (`1395:139`, rev 2) | **ID migration done:** all twenty-four rows now carry `PL-1A` to `PL-6F`, bold-prefixed, at 11pt — the size chosen by measurement, because the IDs made the longest failure text wrap in the 300px column at 11.5. Severity fill removed from the failure cells and its legend with it; the cost column beside it was already neutral, so nothing was left explaining a colour the frame no longer shows. Gradient bar removed; Class letters dropped from the outcome legend; legends reordered so the full-width "where it closes" band leads; `NEXT ACTION` → `YOUR ACTION`. **Exception honoured:** the three control positions — harness gate, repo artefact, control-plane check — and the layer's own closes/partial/nothing/n-a cell key are untouched. `WHAT BREAKS` was **not** renamed to `WHY`: on rev 3 that header is one half of a pair with `WHAT YOU SEE`, and this layer has no symptom column for it to pair with. Supersedes `1185:2` (retained) |

**Truth is a flow diagram, not a row register, and only part of the rev 3 set can land on it.** It reads claim → cost → control → conversion mechanism → outcome → next action, with the fifteen claims converging by class into three outcome and three action boxes. It has no symptom column, no catch-point tag, no per-row tool chip, no per-row outcome chip and no built-state marker, so six of the nine conformance items have nothing to act on. The one that had to be decided rather than skipped is **severity, which stays**. On the row registers the severity fill was cut because nothing on the frame counted it and its third step duplicated the *survives* red. Here severity *is* a column — "what it costs if it's wrong" — the register's own reading notes are built on it ("the mildest severity band is empty"), and the ramp on the frame matches the register exactly: two S2, five S3, eight S4, and S1 unused. Cutting it would remove a column, not an encoding, and D-057 does not reach that far.

**Authority is encoded on the mechanism cell, not in a column of its own.** The exception is real but its shape is worth recording, because the conformance brief described it as "an extra Authority column" and the frame has never had one. Authority is carried by the mechanism cell's fill — green solid where the control is unbypassable, red dashed where it is bypassable or absent — and by the `AUTHORITY` legend block, and the how-to box says so in words. Checked row by row against [[authority-access-layer]]: exactly eleven cells are green, which is the eleven the register names. Giving authority its own column would have meant narrowing four other columns and then handing the freed mechanism cell back to the rev 3 survives-red-dash rule, which duplicates the outcome chip — so it would have bought nothing and cost the shared geometry. Left as found.

**All six frames now share one column set — 9 August 2026.** The five listed above were brought across in the order Authority · Context · Recovery · Truth · Provenance, one at a time. The originals are all retained; nothing was edited in place. What "one column set" means in practice is narrower than it sounds: the four row registers (instruction, authority, context, recovery) are now geometrically identical, and Truth and Provenance share the shared *encodings and legend order* while keeping the layouts their subject matter requires — a class-flow diagram and a three-position control band respectively.

---

## 6. Canon defects found while writing this

Items 1 to 3 were surfaced by the rev 3 work and live in [[instruction-layer]], not in the diagram. Items 4 and 5 were surfaced by the 9 August conformance pass, put to Sholto, and **resolved the same day as D-062** — see the note under item 5 for what the root cause turned out to be.

1. **"All eight mechanisms that act inside the session are Claude Code only" was wrong; it is seven.** The eight in-session rows are IL-1B, IL-2A, IL-2C, IL-3B, IL-3C, IL-4C, IL-5A and IL-5B, but IL-3B's tool is `none · any runtime · process · none`, so it is not a mechanism. Seven mechanisms, all Claude Code. Corrected in the diagram on 8 August and in the register on 9 August.
2. **IL-6B contradicted itself. Resolved 9 August 2026 — the gates are built.** Its tool cell read `built` (correctly, hence no amber marker) while its next action still read "ONCE — Install the CI artefact gates". Read against `hullkey-charge`, which D-058 fixes as the scope for `built`, three regenerate-and-byte-diff gates are live in CI: `check-generated-types.sh` and `check-generated-tokens.sh` from 31 July 2026, and `check-generated-agents.sh` from 5 August. Each regenerates an artefact and diffs it against the committed copy, which is exactly the mechanism IL-6B names. The next action now reads `DONE · 31 JUL 2026`. The count was unchanged by this fix, and then changed to 14 of 21 later the same day by D-059.

3. **IL-1F's failure is closed by a mechanism the register does not name — open.** IL-1F is "the rule was superseded and still loads", and the register names its mechanism as a schema lint requiring effective and expiry dates, marked `designed`. That schema lint genuinely does not exist. But `check-generated-agents.sh` closes the same failure by a different route: it regenerates `AGENTS.md` and byte-diffs it, making a stale rule file structurally impossible. Its own header records the incident that prompted it — on 5 August 2026 the hand-maintained `AGENTS.md` was found restating the control baseline two versions stale, "in the one file every AI coding tool loads on startup", which is IL-1F happening in the field. **The question this raises is general, not local: does `built` describe the named mechanism, or the closure of the failure?** Today the registers answer "the named mechanism", which is defensible and keeps the install list honest, but it means a row can read `designed` while its failure is in fact closed. **Owner: Sholto. Nothing changed pending that call.**

4. **[[authority-access-layer]] counts eleven designed rows in prose and fourteen in its own tables — open.** The stage tables mark AL-1A, AL-1B, AL-1C, AL-1D, AL-1E, AL-1F, AL-2A, AL-2B, AL-3C, AL-4C, AL-4D, AL-5A, AL-6A and AL-6C as `designed`. That is fourteen. But "What that buys" says "for 11 of the 23 rows the control shown is designed and not built today", and the diagram carries exactly eleven amber markers — the fourteen minus AL-5A, AL-6A and AL-6C. So the prose and the diagram agree with each other and disagree with the row data. Under the register-is-canon rule the diagram is the defect and three markers are missing; but adding them makes the frame contradict its own footer, and correcting the prose changes a published number. **Not touched at rev 2. Owner: Sholto** — the call is whether those three rows are genuinely `built`, in which case the tables are wrong, or genuinely `designed`, in which case the sentence and three markers are.
5. **[[recovery-layer]] counts seventeen designed rows and the diagram carries thirteen markers — open, and downstream of the verification pass that is already owed.** The register marks seventeen of twenty-five rows `designed` and eight `built`; the frame has thirteen amber markers. Unlike item 4 this layer has no prose count to arbitrate between them, and its own `verified:` field already says the install states are provisional and unverified against this machine. **Not touched at rev 2**, and it should be settled by the verification pass the register asks for rather than by editing either artefact now.

**Resolved 9 August 2026 as D-062, and the root cause was neither layer's markers.** Both counts were wrong because two layers were marking mechanism-less rows as `designed` — a designed nothing — and because the headline sentence used a different denominator on every layer. Authority now reads 9 of the 18 with 9 markers, Recovery 11 of the 18 with 11, and all four row frames carry marker sets identical to their register's designed list. Recovery's install states are still `verified: design only`; what changed is that the number is now internally consistent and comparable, not that it has been verified. Both were found by `tools/check-registers.py` in a single run.

---

## 7. Named mechanism versus closure of the failure

**Status: settled 9 August 2026 by D-061 — the residual field is adopted across all six registers.** The argument below is kept as written because it is the reasoning the decision rests on. What changed: the proposal in "three fields, not one" is now the schema, and IL-1F (D-059) is the worked example that produced it. What remains open is not *whether* to have the field but *what its values are worth* — see the verification note at the end of this section.

### The question

`built` currently means "the *named* mechanism is in force". The alternative reading is "the *failure* is closed, by whatever means". IL-1F exposed the gap: its named mechanism (a schema lint requiring effective and expiry dates) does not exist, yet the failure is largely closed by a different mechanism (regenerate `AGENTS.md`, byte-diff the committed copy) that no register row named.

### These are not alternatives. They are two different facts

The framework already knows this, and the proof is sitting in the register. IL-3A, IL-5C and IL-6A all have real, nameable mechanisms, and all three still read **C survives** — because a grep gate watches the wording, a link check watches reachability, and a schema lint watches whether a check exists, none of which is the failure. So **"the mechanism exists" and "the failure is closed" already come apart in this model**, and the Outcome column is where that is recorded.

The gap is narrower than the framing suggests. It is not that the register picked the wrong reading. It is that `built` is keyed to the named mechanism with **no field in which to record a substitute**. One field is being asked to carry two facts.

### Why the named mechanism must stay the spine

This is the correct instinct and the reasons are stronger than "it makes recommendations easier":

1. **It is the product's teeth.** "Install X" is concrete, linkable and testable. A register that said only "this risk is closed somehow" would have nothing to recommend and nothing to sell.
2. **It is what makes rows comparable across users.** A benchmark needs everyone's `built` to mean the same thing. "Closed somehow" is not comparable between two organisations.
3. **It is what makes a vendor scorecard possible.** Asking a platform "do you supply this control?" requires naming the control. A closure-only register cannot generate that question.
4. **It preserves the roadmap.** Moving a row from maintained to preventable requires knowing which mechanism to reach for.

None of that is weakened by adding a residual field. It is weakened by *replacing* the named mechanism with one, which is not what is proposed.

### What the closure reading actually buys

Not a better spine. It prevents two specific errors, and both damage the recommendations:

1. **It stops the install list recommending redundant work.** Under the strict named reading, IL-1F sits on the install list forever, telling you to build an expiry-date schema lint that would add nothing, because the byte-diff already makes a stale rule file structurally impossible to commit. **A roadmap that recommends work you do not need is a roadmap people stop following** — which is the direct cost to the thing the named mechanism exists to serve.
2. **It stops the register misreporting risk.** Saying "not built" about a failure that is demonstrably closed is simply wrong, and the first assessor who catches it discredits the framework, not the user.

On the compliance question specifically: **every mature control framework already accepts this.** ISO 27001 Annex A, SOC 2 and NIST all permit compensating controls — you demonstrate the control *objective* is met, not that you used the named control. Being stricter than ISO here is not extra rigour, it is a modelling error. But note what those frameworks demand in exchange: the compensating control must be *documented and assessed*, not asserted. That is the discipline the field has to carry.

### Proposal: three fields, not one

| Field | Meaning | Feeds |
|---|---|---|
| **Mechanism** (unchanged) | The named control this row calls for | Recommendations, vendor scorecards, the roadmap |
| **Built** (unchanged) | Is the *named* mechanism in force in `hullkey-charge`? | The install list, "N of the 21 are not built", the amber marker |
| **Residual** (new) | What is actually true about this failure now | Honest risk reporting, and leverage recommendations |

Residual values: `closed` · `closed by substitute` · `partially closed` · `open`.

**`partially closed` is not padding.** IL-1F is the proof: the byte-diff proves `AGENTS.md` matches its committed inputs, but cannot prove those inputs match the live control plane, because CI cannot reach the vault. Half the failure is closed by a machine and half by a human-run exporter receipt. A binary field would have to lie in one direction or the other.

### The payoff the named field cannot produce

A residual field creates a **second and better class of recommendation: leverage.** Once substitutes are recorded, the register can say *"this one gate already closes three rows — point it at a fourth and you close that too"*, which is a stronger and more persuasive roadmap than a flat install list. The `check-generated-*` family in `hullkey-charge` is exactly this shape: one pattern (deterministic renderer, committed artefact, byte-diff) already closing IL-1F and IL-6B, and extensible to any generated file. That insight is invisible under the named reading and is the kind of thing that makes a tool feel intelligent rather than clerical.

### How much information a substitute claim needs

Four sub-fields, roughly one line. The rule is that a substitute must carry a **receipt, not an assertion**:

1. **Identifier** — the file path or CI job name, so it can be checked (`scripts/check-generated-agents.sh`)
2. **Its own catch point** — *not* inherited from the named mechanism
3. **One line on why it closes the failure**, and where it stops
4. **Date observed**

**Sub-field 2 is the one that will get missed, and it moves headline numbers.** IL-1F's named mechanism was a schema lint at `on disk`; its substitute runs in CI. Recording the substitute therefore moved the row two columns right and changed the catch-point distribution (`on disk` 6→5, `CI` 5→6) and the phase totals (before it starts 7→6, after the session 9→10). A substitute that inherits the named mechanism's catch point would silently corrupt the single most load-bearing column in the framework.

### If the residual field is rejected

The fallback is to leave `built` strictly named and record substitutes only in prose reading notes, as IL-1F does today. That keeps the schema simple and the install list pure, at the cost of the register overstating open risk and the leverage recommendations staying invisible. It is a defensible choice, but it should be a chosen one rather than a default.

### What the residual column is worth today, register by register

The field is in. Its *values* are only as good as the verification behind each register, and that varies enormously. This table is the thing to read before quoting any residual number publicly.

| Register | Residual split | Verification behind it | Safe to publish? |
|---|---|---|---|
| **Instruction** | 7 closed · 1 partially · 15 open | Verified 6 Aug 2026 against `hullkey-charge`, plus Claude Code baseline controls verified against Anthropic documentation on 10 Aug 2026; IL-1F hand-entered against repo evidence | **Yes** |
| **Authority** | 9 closed · 14 open | Read 6 Aug 2026 against the HullKey security register | Qualified — say what "read against" means |
| **Truth** | 7 closed · 8 open | Describes the HullKey repo's check suite; not independently re-checked | Qualified |
| **Context** | 1 closed · 22 open | `verified: design only` — install states never checked | **No** |
| **Recovery** | 7 closed · 18 open | `verified: design only` — markers provisional | **No** |
| **Provenance** | 7 closed · 3 partially · 14 open | Describes the HullKey control set; never checked against a running system | Qualified — was **No**, and the reason why is below |

**Provenance was the number to watch, and it did not hold.** Until 10 August 2026 this row read *21 closed · 3 partially · **0 open***, and this section flagged it as the most flattering result in the set, the most likely to be quoted onward, and the least grounded — because Provenance has no built-state field, so its residual derived entirely from cells asserting `closes` with nothing confirming those controls were switched on.

That warning was correct. Fourteen of the 24 rows carried a `ONCE —` install as their own next action while reporting the failure closed. They now read `open` (C-02, D-075), and the derivation rule is gated on install state: a row whose next action is an install closes nothing. **A register that reported zero open risk in fact had the majority of its rows open.**

Two things follow, and both are worth more than the correction itself. **First, the mechanism that caught it was reading the rows against each other, not a verification pass against a running system** — the contradiction was visible inside the file the whole time, and the checker that was supposed to hold canon together did not look for it. **Second, the same conflation is in `built`**, which records that a mechanism exists in `hullkey-charge` rather than that it is in force there; applying the same gate to the four built-state layers surfaced seven more candidate rows (C-23). Provenance was the worst case, not the only one.

The pattern is worth stating generally, because it will recur as the registers grow: **a derived field inherits the confidence of its inputs but not their caveats.** `built` at least carried an amber marker and a verification stamp that made its provisionality visible. Residual, presented as a clean word in a table cell, looks like a finding. Until a verification pass has run, four of the six registers' residual columns are restatements of unverified assumptions wearing the costume of evidence.

**Owed before launch:** a verification pass on Context, Recovery and Provenance, in that order of cheapness, or an explicit "unverified" watermark on their residual columns wherever they are shown. The 10 August correction removed the most misleading single number but did **not** discharge this — Provenance's remaining 7 closed rows are still derived from cells nothing has checked against a running system.

**Added 10 August 2026, and it belongs in this section rather than only in the bug list:** the V1 trust-check tool had been serving a copy of the registers extracted from a commit predating the 9 August built-state normalisation. Regenerating it changed twelve rows' built state. Canon moved, the generated view stayed green, and nothing compared them — the failure this whole document exists to prevent, occurring in the framework's own instrument (C-25). The Figma frames carry the same exposure and still have no equivalent check.

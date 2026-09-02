---
type: methodology
project: agent-trust-framework
title: "The False Floors methodology"
status: active
date: 2026-08-21
last-updated: 2026-08-31
---

# The False Floors methodology

**What this file is.** The whole method, in one file. Half one is how a failure is **named and counted** — what a row claims, where the rows came from, what mints a countable row, how the population has been validated, what the known biases are, and how the registers change (sections 1 to 7). Half two is how a failure is **answered** — when a recorded failure earns a control, and what stops the control list growing without limit (sections 8 and 9). It is the governing document for every published count.

**It restates neither of its two source arguments.** The forensic half — where each row actually came from, graded row by row — is framework review 02; the prescriptive argument that produced the inclusion rule is research 46; the decision adopting it is D-107 in the Decision Log.

**Why one file, and not three.** Until 2026-08-30 this was a root pointer plus two annexes — `METHODOLOGY.md` and `gates/METHODOLOGY.md`. Consolidated under D-209 on Sholto's question: the split had no operational justification, only the historical accident that each half was written next to the folder it described. The reasons given for keeping it apart — a public copy boundary, a hardcoded checker path, section-number citations — were migration costs, not design arguments. **The argument that decided it runs the other way:** C-95 happened *because* the method was split across surfaces with no single owner, so a tidy split preserves the shape of that failure and one file makes it structurally impossible. The two READMEs stay where they are: an index and a schema is a different job from a method.

Adopted 2026-08-21 (D-107). Counts in this file are canon-checked: `check-registers.py` derives the receipts and fails on any row whose evidence marker disagrees with them, and `check-content-counts.py` scans this file alongside `content/`.

> **Reading this as a human? Read the web page instead.** The public methodology page (`content/hub-and-spokes/live/methodology.md`, published at scale100.co) says all of this in plain sentences, and carries the build narrative this file has never held: the non-developer premise, the two-model author/adversary seats, the standards-body control architecture, and the git-ceremony finding.
>
> **The division of labour, so neither becomes a stale copy of the other.** This file is **canon**: the numbered sections other canon files cite by number, the receipt definitions, the dated prediction mappings, and the change rules the gates enforce. The web page is the **readable rendering** for a public audience. Where they overlap, it is on counts — and every count in both is machine-reconciled against the registers by `check-content-counts.py`, so the overlap cannot drift silently. Narrative belongs on the page; rules and receipts belong here.
>
> **Section numbers here are load-bearing.** `Corrections Register.md` cites "sections 3 and 4", `OPERATIONS.md` cites "section 4's definition" and "section 7, item 1", and the Decision Log cites "section 4". Do not renumber or delete a section; edit within it.

## The method is a loop, not a taxonomy

**D-082 is the governing decision and it is worth quoting rather than paraphrasing:** the framework's operating loop is *issue to wired gate*, and every stage short of wired is unfinished work. Its trigger was the T-0045 debrief, which mapped seven failures onto the registers, lodged two rows, and **changed nothing — because classification produced rows, not controls.**

That is the whole argument for why this file has to exist. A methodology that documents only how failures are named describes the half of the machine D-082 found insufficient.

```
an issue  →  a register row  →  a gate  →  validated  →  wired  →  closed
            └──── half one ────┘  └──────────── half two ───────────┘
             names the failure     answers it, and proves the answer runs
```

## 1. Scope and claims — what a row asserts, and what a count may

A register row makes four claims: the failure class **exists**, it is **distinct** from its neighbours, it **matters** (severity), and a named control is the **strongest available answer** (class, catch point, gap). A register's *count* additionally implies a coverage claim — that the list is the shape of the space — and that is the claim this methodology refuses to make. No count published by this framework claims the space is mapped. The corpus evidence (section 4) says the opposite: the enumerated lists are floors, not ceilings.

A count may therefore claim only what its rows' evidence supports, which is what the inclusion rule in section 3 operationalises: **headline counts count evidenced rows only.**

## 2. Sources and provenance — three construction methods, dated

The rows were generated across five sessions on 5–6 August 2026, and the register files of 7 August (commit `3e71b59`; the Truth register followed on 8 August) are the transcription of record. Three methods, and every register says which it used:

- **Inventory** — rows read off real artefacts. Truth (15 rows) inventoried a live CI check suite; the seventh register, Execution and Capability, is built only from incidents (4 rows, outside every cross-register count by construction).
- **Incident transcription** — rows read off a recorded register of things that happened. Authority (23 rows) was sourced from the HullKey security register: every row an incident that happened there once, or a control gap recorded against it.
- **Enumeration in advance** — rows generated by walking a unit's lifecycle and asking "what breaks here". Instruction, Context, Recovery and Provenance were built this way (Instruction grounded additionally in a 20,574-session field study and a lived rule history), and it is why those registers cluster at 22–24 rows: the count measures the generator's aperture, not the failure space.

The full per-register generation record, with each register's stated basis at generation time, is framework review 02, section 2 — linked, not restated, because a second copy of a dated table is a copy that drifts.

## 3. The inclusion rule and the evidence tiers (D-107)

**Every row carries an evidence status**, in the `Evidence` column of its register, and the two values mean exactly this:

- **evidenced** — at least one receipt exists. Three receipt types count, and nothing else does:
  1. a **first-party mapped incident**: an `⟪instance-of⟫` marker on a dated row of the Corrections Register;
  2. a **corpus-coded finding**: an exact or variant match in the 262-item calibration pass (run 22), coded by a quarantined agent against pre-framework audit documents;
  3. a **verifiable public field case**: a dated, checkable citation filed in the vault. One is on file today (AL-4A, the Antigravity sandbox escape) and it confirms a row already corpus-evidenced. Widely known cases with no filed citation — the Replit database deletion for AL-1B, the GitLab 2017 restore failure for RL-5B — deliberately do not count until a citation is filed.
- **candidate** — enumerated in advance, no receipt yet. Still a row: published, classed, graded, and labelled on the row. Counted in no headline.

**Headline counts count evidenced rows only.** On the receipts as at 2026-08-25: **67 evidenced · 61 candidate** across the 128 rows — 47 rows by first-party incident, 20 more by corpus coding alone. (The headline pair has not moved since 21 August; on 22 August `CL-5B` gained a first-party mapping it did not have, which moves a row between the two evidence *sources* without moving the tier split, since it was already evidenced by corpus coding.) The split per register is in the [registers README](README.md) table.

**Enumeration is demoted from row source to hypothesis source.** It remains the method for proposing candidates — it is good at that, and section 4's prediction record is the measurement of how good — but it never again sets a published total.

**Promotion and decay.** A candidate is promoted by its first receipt — the receipt is lodged at its source (the Corrections Register for incidents, the vault citation for field cases), never asserted on the row, and the checker re-derives the marker from the receipts on every run. A candidate that a review window passes over with no instance, no corpus match and no field case is retired to the candidate pen ([truth-layer](registers/truth-layer.md), "Candidate rows, not yet evidenced"), which sits one step below a published row. The first review window closes with the corpus harvest (section 7), which will either promote or price every standing candidate against the 150 unabsorbed corpus findings.

## 4. Validation events and results

Four validation events have run against the population, plus the prediction record. Every number here is re-derivable from the named source.

| Event | Date | What it tested | Result |
|---|---|---|---|
| Calibration pass (run 22, accepted D-068) | 9 Aug 2026 | A quarantined coder coded 262 real findings from 26 pre-framework audit documents against the registers | 0 findings fell outside the seven questions; 52 matched a row exactly, 60 as variants, 150 demanded a new row; 29 distinct rows took at least one hit |
| Inter-rater runs (D-069, D-073, D-079) | 9–10 Aug 2026 | Whether independent coders assign findings to the same register | κ = 0.654 on a blind held-out run — register-level agreement; row-level discrimination is untested (section 5) |
| Adversarial Class-A audit (D-080) | 10 Aug 2026 | Every row claiming *prevented*, re-tested against a written counterfactual: assume the agent wants to cross the boundary | 14 of 26 Class-A claims demoted; the strongest per-row oracle applied so far |
| Retire/merge pass (D-106, from framework review 02) | 21 Aug 2026 | Row distinctness and usefulness, graded row by row | 6 rows retired or merged (134 → 128), each recorded in its register's Retired rows section |
| **Prediction record** (below) | computed 21 Aug 2026, recomputed 22 and 31 Aug | Whether rows named in advance come true | **25 rows confirmed by dated incidents after they were named** |

### The prediction record — computed, not estimated

The one validation unique to the enumerated half: a row written down *before* the failure it names was ever recorded, then confirmed by a dated incident. Prospective confirmation is the statistic filler cannot fake, because filler does not come true.

**Definition.** A row counts if it was present in the committed registers before the incident occurred (the five original registers at commit `3e71b59`, 7 August 2026; Truth at its first commit, 8 August 2026), and its earliest first-party mapping in the Corrections Register carries an incident date — not a lodge date — after that. Corpus receipts never count here: the corpus documents predate the framework, so a corpus match is validation, not prediction.

**Result: of the 47 first-party evidenced rows, 25 were named before the incident that confirmed them.** Incident dates run 9–25 August 2026:

**Stated as a rate, with its denominator shown.** At enumeration, 113 rows stood as unconfirmed predictions: the 133 rows committed on 7–8 August, less the 20 whose mapped incidents predate the registers. The six rows later retired by D-106 are kept in the denominator — they were predictions that earned nothing, and removing them would flatter the rate with survivorship. 25 of 113 — 22 per cent, about one in five — were confirmed by a first dated incident, 24 of them within eleven days of the last register's commit and the 25th (CL-1C, via C-89) on 25 August, via 17 corrections-register entries (an incident can confirm more than one row). *(Corrected 2026-08-31, C-98: from 22 August until then this paragraph read 24 of 113 via 16 entries — C-89's 25 August mapping of CL-1C was never recomputed in, despite section 7 item 4 ordering exactly that.)* Two properties make the rate informative rather than decorative: the rows are narrow (one mechanism against one unit), and the mapping process demonstrably refuses bad fits — 150 of 262 corpus findings were coded as matching no row, and rejected mappings are recorded (C-70's declined TL-01 mapping is the worked example). Its scope, stated as plainly: one operator, one machine, heavy daily agent use, observers who hold the register. No control condition has been run — a decoy register of plausible-but-wrong rows would be the falsification test, and until something like it runs, the rate measures occurrence-in-environment, not generality and not coverage.

| Incident date | Rows confirmed | Mapping |
|---|---|---|
| 9 Aug | TL-10, TL-14 | C-21, C-00 |
| 9–10 Aug | TL-11 | C-53 |
| 10 Aug | TL-05, PL-3E, CL-5B | C-25, C-16, C-25 (PL-3E again by C-34, 12 Aug) |
| 10–11 Aug | CL-5A, CL-3B, TL-09 | C-70, C-71, C-70 (TL-09 again by C-39, C-41) |
| 11 Aug | IL-5C, CL-4B, PL-3A, PL-6C, AL-3C | C-45, C-45, C-43, C-43, C-43 |
| 11–12 Aug | IL-4A, TL-03, CL-3C | C-31, C-31, C-33 |
| 12 Aug | CL-2A, PL-1A, CL-3A, TL-02, PL-5A | C-37, C-37, C-36, C-38, C-38 |
| 13 Aug | TL-04 | C-41 |
| 18 Aug | RL-2C | C-54 |
| 25 Aug | CL-1C | C-89 |

The remaining 22 first-party rows split three ways, stated so the 25 cannot be read as larger than it is. **20 are retrodictions**: their incidents predate the registers (the July HullKey incidents and older vault incidents), and for the Authority register that is by construction — it was transcribed *from* the security register that recorded them, so its mappings confirm fidelity, not foresight. **RL-1E is mapped but uncounted**: its one mapping (C-10, lodged 10 August) records no incident date, and a bound is not a date. **RL-1F is excluded by definition**: the row was minted *from* its own incident (C-55, 18 August) — found, not predicted.

RL-2C is the cleanest single case: enumerated on 7 August as a designed deny-hook on destructive command shapes, confirmed on 18 August when a `git reset --hard` destroyed a concurrent session's work (C-54), and built the same day. The row predicted the failure, the failure arrived, and the control the row specified now runs on this machine.

## 5. Known biases and limits

- **Enumeration aperture.** Four registers were enumerated by one process onto one page layout, and even after the D-106 retirements they sit at **22, 22, 22, 24** — Instruction, Context, Provenance and Recovery, the four registers section 2 names as enumerated. That closeness is a property of the generator, not the failure space. The aperture bias is quarantined by the inclusion rule (candidates never reach a headline) rather than removed. *(Corrected 2026-08-24, C-80: this line read "22, 22, 23, 24" from adoption until then. The 23 is Authority, which section 2 classifies as incident transcription, not enumeration — so it never belonged in a list about the enumeration generator's aperture. The corrected figure is the less flattering one: three of the four are identical, so the aperture effect is stronger than this section claimed. Nothing parses a prose list of per-register sizes, which is why the line survived every run of every gate.)*
- **Truncation, not padding, is the larger error.** 150 of the 262 corpus findings demanded row detail no register carries. The enumerated lists are too small relative to the space, not too large, and the framework says so rather than treating its counts as coverage.
- **Corpus skew.** The calibration corpus is 26 code audits of one database product (D-068, qualification 1). It structurally under-supplies Recovery, Instruction and Context and over-supplies Truth and Authority — a Recovery candidate without a corpus hit is not thereby suspect.
- **Single-operator, single-harness grounding.** Built states are scoped to one repo (`hullkey-charge`, D-058); the incident stream is one operator's practice on one machine. The registers claim grounding in that environment, not generality across environments.
- **What has not been validated.** Row-level discrimination — whether independent coders can reliably tell *rows* apart, not just registers — is untested; κ = 0.654 is a register-level number. Use by human coders other than this project's own seats is untested. Both sit in the standing programme.

## 6. Change management

- **Row IDs are stable, never renumbered, never reused** (row ID rule 1, [registers README](README.md)). A row leaves the counts only via its register's Retired rows section, with a dated reason; any old scan citing the ID still resolves.
- **Retirement** follows the D-106 test: no recorded incident, no distinct mechanism separating it from a stronger neighbour, and a low audit grade *with* a surviving row carrying its class.
- **Promotion and decay** move rows between tiers per section 3; the decay destination is the candidate pen, and the pen's entries are not rows.
- **Receipts are minted at the source, never in content** (D-097): `⟪instance-of⟫` markers live in the Corrections Register, and pages may only cite them.
- **A canon change is not finished until its published surface is updated, and "published" means the website, not the repo file** (D-205, 28 August 2026). Three surfaces carry this methodology and they fail differently: this file is canon; `content/hub-and-spokes/live/methodology.md` is the *text of record* for the public page; scale100.co is what a reader actually sees. Editing canon and stopping leaves the page wrong; editing the page and stopping leaves the website wrong, and the website is the only one a third party reads. **So every edit to this file carries two obligations, in order:** update the page text in the same commit, then publish it and record that you did. Counts are already machine-reconciled across the first two by `check-content-counts.py` and cannot drift silently; **narrative is not, and this rule is what covers narrative.**
- **`published:` records the version that actually reached the website**, and it is the only field on a page that may be read as a statement about scale100.co. A page whose `version:` exceeds its `published:` has unpublished changes — that is the whole check, and it is deliberately mechanical rather than a judgement about whether the difference matters. `status: live` asserts the page exists publicly; it has never meant the live copy is current, and until this field existed nothing did. This is PL-5A's class (*done recorded on a branch that never landed*) with the website in the place of the branch.
- **Enforcement is executable, not prose.** `check-registers.py` verifies row data, counts, vocabularies, the evidence markers against the re-derived receipts, and the generated views against canon; `check-content-counts.py` fails any page in `content/` (and this file) whose stated counts disagree with the registers; `check-spoke-evidence.py` refuses a published "Recorded" line with no lodged mapping. Each gate has been validated against known-bad input — a gate that has never been watched failing anything is itself a register row (AL-6A).

## 7. The standing programme

Roadmap, dated at adoption (2026-08-21), in priority order. None of it blocks release; all of it moves counts, and the counts will move publicly.

1. **Harvest the corpus.** Cluster the 150 unabsorbed run-22 findings into classes and mint evidenced rows from them — the largest rigour upgrade available, on material already paid for. Saturation is tracked in round-robin order across source documents, per the C-20 lesson: a saturation curve measured in storage order measures the storage order.
2. **Row-level discrimination testing.** Extend the next coding round to row assignment; rows that attract systematic confusion merge by measurement rather than by editorial judgement.
3. **Wire the corpus into the evidence gate.** `check-spoke-evidence.py` proves first-party mappings only; teach it run 22's coded table as a second marker source so per-row corpus marks print with the same rigour as Recorded lines. (The registers checker already re-derives both receipt types; this item extends the same derivation to the published spokes.)
4. **Maintain the prediction record.** Recompute on every new mapping; the count and its dates are published, and the definition in section 4 is the only one used.

---

*False Floors is a trade mark of Digital First Pty Ltd, trading as Scale100 (AU application AMCZ-2616155657). This content is CC BY 4.0; the name is not part of that licence. Citing, mapping to, or claiming conformance with the catalogue needs no permission – see `LICENSE-CONTENT`.*

## 8. The admission test — should this gate be built at all

**Every gate is a standing cost.** It runs, it can go noisy, its fixtures rot when the repo shape changes (C-72), and a gate that cannot run still has to be explained to whoever finds it silent. So the question is asked once, before the effort is spent, and the answer is recorded in the entry. Adopted 2026-08-28 (D-205).

| Outcome | Test |
|---|---|
| **Build — mandatory** | The failure is irreversible or outward-facing (money, sends, merges, deletes, publishes, anything a third party sees), **regardless of how rarely it happens**; **or** it is the second recorded instance of a class (C-31's existing rule) |
| **Refuse** | The check cannot be specified precisely, so it would fire on things that should pass (rule 5 below); **or** it cannot be validated against a known-bad input today |
| **Defer — `status: dormant`** | Justified, but its input does not exist yet (no customer data, feature unbuilt). Recorded with a named `activation-blocker`, never a vague "later" |
| **Row only, no gate** | Everything else. Lodge the register row and let recurrence promote it |

**Frequency is deliberately not an input.** A once-a-year irreversible failure earns a gate; a daily cosmetic one does not. This is the ALARP idea — reduce risk until further reduction is grossly disproportionate to the benefit — written as a rule rather than a number.

**No score, and this is not a style preference.** The obvious instrument is FMEA's Risk Priority Number (Severity × Occurrence × Detection), and it is the wrong tool twice over. Multiplying ordinal ratings invents precision that is not in the inputs, and lets a severe failure be averaged away by a low occurrence — which is why the AIAG-VDA revision replaced RPN with Action Priority tables in 2019. And this project has its own receipt: **C-21** records that naming a numeric threshold in a brief *caused it to be gamed*, across three runs, each defeating the previous run's detection method. A gate-worthiness score would rebuild that.

**Where the ceiling actually sits.** Not at a number of gates. At noise: a noisy gate trains the reader to skim, so the limit is reached when ledger.md's `noise` dispositions start outnumbering `true-catch` — measurable from data already being collected, which beats any invented threshold. Retirement is the other half: metrics.md tracks last-true-catch, and a wired gate with no live catch and no fixture change is an archive candidate.

**The severity input.** Severity is graded per the [registers README](registers/README.md) — one construct, two domain readings, repaired 28 August 2026 (C-08). It reaches this table only through the irreversibility test, never as a score, and no count rests on it.

## 9. Run-time instruments — whether the controls earn their cost

The entries above carry build-time evidence (fixture, validation, wiring). Run-time evidence — what the gates actually catch once deployed — lives in four sibling instruments:

- **ledger.md** — every red a wired gate causes, one row per event, dispositioned `true-catch` / `noise` / `gate-defect`. Append-only; never read in normal operation.
- **session-review-log.md** — one row per session-review run, **including clean runs** (the denominator).
- **metrics.md** — per-gate time-to-gate, build attempts (the cost driver), catch-point distribution, and last-true-catch (half-life). Recomputed monthly from the ledger.
- **missed-recurrence-audit.md** — fortnightly three-arm check that gated classes are not recurring un-caught and ungated classes are not silently reaching their second instance.

Two obligations follow: **every gate reaching `wired` gets a metrics row**, and **every ledger row gets a disposition**. These are currently process, not mechanism — wiring them into `check-registers.py` (a metrics row required per wired entry, a disposition required per ledger row) is the owed enforcement step, per this library's own rule that a rule addressed to a reader does not bind.

## The framework's own bug list

Corrections Register.md holds open defects in the framework itself — the method applied to the method. Its severity means cost to the framework's credibility, and it is **not** the S1–S4 agent-failure scale the registers use.

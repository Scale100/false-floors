---
type: register
project: agent-trust-framework
layer: context
prefix: CL
title: Agent Context Layer — Did It Know What It Needed To Know
question: Did it know what it needed to know?
unit: a fact
figma-node: "1:3839"
figma-file: 9KIzmsPS1EzWNQiOFKjWzX
rows: 22
class-a: 0
class-b: 14
class-c: 8
class-a-reads: prevented
class-b-reads: detected
class-c-reads: survives
evidenced: 12
candidate: 10
verified: design only — install-state markers not yet verified against this machine (every row carries a designed marker except CL-5B)
gap-basis: derived from outcome x built state on 2026-08-09 (D-061); substitutes and partial closures entered by hand only where evidenced
date: 2026-08-07
last-updated: 2026-09-01
---

# Agent Context Layer: did it know what it needed to know

The life of a fact, stage by stage, and what happens when the agent works from the wrong one. The instruction layer asks whether the agent obeyed; this layer asks whether what it obeyed with was true.

**This file is canon; the Figma frame `1:3839` (rev 2) is a generated view.** Shared vocabulary: [registers README](README.md).

Column key: **Evidence** — `evidenced` (at least one receipt: a first-party incident mapping, a corpus-coded finding, or a filed public case) or `candidate` (enumerated in advance, no receipt yet); headline counts count evidenced rows only (D-107, [registers README](README.md)) · Sev S1–S4 · Tool cell reads `name · runtime · tier · built state` · Outcome A / B / C – class grades how complete the remedy is ([registers README](README.md)); **this register reads B as *detected* and C as *survives*** · Next action carries its trigger in caps. **Gap** says what is actually true about the failure today, which is not the same as whether the named mechanism exists — see [registers README](README.md).

## Stage 1 · CAPTURED — does the fact exist outside a head? (0 prevented · 5 detected · 1 survives)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome | Gap | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CL-1A | candidate | S3 | The fact only ever existed in a chat thread | “We worked this out weeks ago” | Archive every working conversation to disk | stop | Stop hook offers to archive the turn’s findings | Claude Code · Claude Code · automatic · designed | B detected | open | ONCE — Install the conversation-archive stop hook |
| CL-1B | evidenced | S3 | The decision was recorded, the reason was not | “You know what was chosen, not why” | Require a rationale field before it counts | on disk | Schema on the decision log fails on a missing why | Schema lint · any runtime · maintained · designed | B detected | open | AT EVERY DECISION — Write the reason while you still remember it |
| CL-1C | evidenced | S2 | Written somewhere retrieval never looks | “The note exists and search never sees it” | One canonical folder per class of fact | pre-commit | Path lint refuses a file filed off-taxonomy | Path lint · any runtime · maintained · designed | B detected | open | ONCE — Ticket-obligation reachability gate BUILT 2026-08-25 (hullkey-charge/scripts/check-ticket-obligations.mjs, wired in verify:fast); AT EVERY NEW NOTE — Check the taxonomy before you write |
| CL-1D | evidenced | S1 | Two notes disagree, nothing says which is current | “It quoted the stale one, plausibly” | One source of truth; every copy points home | on disk | Supersedes pointer in the front matter | none · any runtime · process · none | C survives | open | AT EVERY REWRITE — Retire the old note, do not just add a new one |
| CL-1E | candidate | S3 | Captured as a summary; the source was discarded | “You cannot check the claim back to anything” | Keep the raw source beside the distillation | on disk | A curated note must name its raw source file | Schema lint · any runtime · maintained · designed | B detected | open | AT EVERY IMPORT — Archive the raw file first, distil second |
| CL-1F | candidate | S4 | A spoken fact was never written down at all | “The only record is that someone remembers” | Every call produces a transcript on disk | on disk | Recorder writes the transcript; triage files it | Transcripts · any runtime · automatic · designed | B detected | open | ONCE — Turn on recording for every call |

## Stage 2 · RETRIEVED — did it reach the agent when it mattered? (0 prevented · 2 detected · 1 survives)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome | Gap | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CL-2A | evidenced | S4 | Nobody looked; the answer came from training | “Confident answer, no file opened” | Ground every factual answer in a read | pre-tool | A prior read cannot bind a natural-language claim to evidence | Claude Code · Claude Code · automatic · designed | C survives | open | ONCE — Design a structured claim channel that requires an evidence reference |
| CL-2B | evidenced | S3 | The search terms did not match the wording | “The note exists and was never found” | Index the old names, not only the current ones | on disk | Naming changelog resolves every retired path | Alias index · any runtime · maintained · designed | B detected | open | AT EVERY RENAME — Add the old name to the changelog table |
| CL-2C | candidate | S3 | Retrieved, then compacted away | “Cited it early, contradicted it late” | Re-inject the working set after compaction | compact | PostCompact hook re-reads the open files | Claude Code · Claude Code · automatic · designed | B detected | open | ONCE — Install the PostCompact re-read |

## Stage 3 · TRUSTED — is what came back actually true? (0 prevented · 1 detected · 2 survive)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome | Gap | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CL-3A | evidenced | S3 | Someone’s claim was read as established fact | “Quoted a vendor’s framing as a finding” | Every claim carries who said it, and when | prompt | Source-attribution convention inside the note | none · any runtime · process · none | C survives | open | EVERY CLAIM — Name the source in the sentence, not the footer |
| CL-3B | evidenced | S4 | An absence was reported as a finding | “Nothing covers this” — one grep settles it | Prove a negative before you relay it | prompt | Show-the-search convention: name where you looked | none · any runtime · process · none | C survives | open | EVERY FINDING — Show the search, not just the conclusion |
| CL-3C | evidenced | S3 | The index was checked instead of the artefact | “The register row was right, the file was wrong” | Verify the work, not the thing describing it | CI | CI diffs the register against the files it names | CI · any runtime · maintained · designed | B detected | open | ONCE — Build the register-versus-artefact diff |

## Stage 4 · USED — did it change what was produced? (0 prevented · 3 detected · 2 survive)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome | Gap | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CL-4A | candidate | S3 | The right file was read and then ignored | “Opened it, then wrote something else” | Make the output cite the file it used | CI | Citation check on every generated document | CI · any runtime · maintained · designed | B detected | open | AT EVERY TEMPLATE CHANGE — Require a citation line per factual claim |
| CL-4B | evidenced | S3 | A trained default overrode the retrieved fact | “Used the standard figure, not yours” | Name the specific wrong value to block | pre-commit | Banned-value grep gate, run pre-commit | Grep gate · any runtime · maintained · designed | B detected | open | AT EVERY NEW DEFAULT — List the wrong values you keep seeing |
| CL-4C | candidate | S4 | A gap was filled by inference, not a question | “Plausible number, no source” | Mark unknowns; never estimate silently | prompt | Unsourced-figure convention in the draft | none · any runtime · process · none | C survives | open | EVERY DRAFT — Ask instead of estimating |
| CL-4D | candidate | S3 | Context from one project leaked into another | “Applied one client’s rule to another” | Scope the knowledge, and test the boundary | on disk | Directory-scoped context files | Rule file · most runtimes · maintained · designed | B detected | open | AT EVERY NEW CLIENT — Decide what each folder is allowed to see |
| CL-4E | candidate | S4 | A qualified finding was used without its caveat | “The hedge was dropped on the way through” | Carry the confidence marker with the fact | on disk | Verification status travels with the claim | none · any runtime · process · none | C survives | open | EVERY HANDOFF — Repeat the caveat wherever the fact goes |

## Stage 5 · CURRENT — is it still true today? (0 prevented · 2 detected · 1 survives)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome | Gap | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CL-5A | evidenced | S3 | True when it was written, not true now | “Quoted a price you changed in March” | Effective and review dates on every fact | on disk | Schema requires an effective and a review date | Schema lint · any runtime · maintained · designed | B detected | open | AT EVERY REVIEW — Date the fact; expire it on review |
| CL-5B | evidenced | S3 | The copy drifted from the live source | “The vault says one thing, the system another” | Derive the copy; never hand-maintain it | session start | Live connector is available but does not force its use | MCP connector · any runtime · automatic · built | C survives | open | ONCE — Bind the generated view directly to the system of record |
| CL-5C | candidate | S2 | A superseded document still surfaces first | “Retrieval keeps returning the archived one” | Archive out of the search path, not beside it | on disk | Archive folder excluded from the retrieval path | Link check · any runtime · maintained · designed | B detected | open | AT EVERY ARCHIVE — Move it out of reach, do not just rename it |

## Assurance · CHECKED — would you find out if it had been wrong? (0 prevented · 1 detected · 1 survives)

Not a sixth step. This band applies across stages 1 to 5 — each row asks whether the stage above would have told you.

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome | Gap | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CL-6A | evidenced | S4 | The wrong fact is invisible in the output | “Reads perfectly, is factually wrong” | A check per load-bearing fact, or accept none | on disk | Schema finds facts with no check, not wrong facts | Schema lint · any runtime · maintained · designed | C survives | open | AT EVERY NEW FACT — Decide which facts are worth a check |
| CL-6B | candidate | S4 | It reports a source it never opened | “Cited a file that was never read” | Compare citations against the read log | stop | Cited files diffed against the session read log | CI · Claude Code · automatic · designed | B detected | open | ONCE — Install the citation-versus-read-log check |

## Catch-point distribution

Before it starts 11 · before the change 4 · still in the session 3 · after the session 4.

| on disk | session start | prompt | pre-tool | subagent | post-tool | compact | stop | pre-commit | CI | review |
|---|---|---|---|---|---|---|---|---|---|---|
| 10 | 1 | 3 | 1 | 0 | 0 | 1 | 2 | 2 | 2 | 0 |

Read left to right: how much has already happened by the time the failure is caught. The work is to move each row left.

## The stack for this layer

- Vault taxonomy, placement and path lint — CL-1C, CL-4D
- Naming changelog and alias index — CL-2B
- Hooks: Stop, PreToolUse, PostCompact — CL-1A, CL-2A, CL-2C, CL-6B
- Schema lints: rationale, raw source, effective and review dates — CL-1B, CL-1E, CL-5A, CL-6A
- Transcript pipeline, and live MCP reads instead of copied figures — CL-1F, CL-5B
- CI gates: banned-value grep, citation check — CL-3C, CL-4A, CL-4B
- Archive excluded from the retrieval path — CL-5C

## What that buys

Of 22 failures: none are prevented, 14 are detected, and 8 survive. 17 name a tool or an automated check; five are convention only. Naming a mechanism is not installing it — 16 of the 17 are not built in `hullkey-charge` today; only the live MCP connector behind CL-5B exists, and availability does not force the agent to use its result.

Evidence status (D-107): 12 of the 22 are evidenced — a recorded incident or corpus-coded finding has landed on the row — and 10 are candidates, enumerated in advance and still waiting for their receipt.

## The six that still reach you

- CL-1D — a rule for which of two notes is current
- CL-3A — a check that a claim carries its source
- CL-3B — a check that an absence was actually searched
- CL-4C — a check that a figure came from somewhere
- CL-4E — a check that a caveat travelled with the fact
- CL-6A — a check that fires on a fact that is simply wrong

Five are conventions you have to remember — nothing runs. The sixth has a check that watches a proxy: it finds facts with no check, never a fact that is wrong.

## Reading notes

Failure class is a property of the mechanism, not of the fact. Re-reading a note every session changes how often the wrong fact is used, never what happens when it is. Re-injection alone is still Class C; CL-2C moves because the re-read itself is observable.

Severity is cost multiplied by how silently it fails. It is a judgement, not a measurement. This layer is a design, not an audit — every row carries a designed marker except CL-5B, and the install-state pass is owed before the diagram is shown.

## Retired rows

Retired IDs are never reused and never renumbered (row ID rule 1). Each retirement carries its reason and its date; the full audit behind the pass is framework review 02 and the decision is D-106.

- `CL-6C` — *caught only because you happened to know* — retired 2026-08-21, merged into [IL-6C](instruction-layer.md). The two rows were the same assurance failure with the same mechanism (promote repeat findings into checks) stated once per register; the class is not context-specific, IL-6C is the copy whose mechanism is actually in force in this vault (the fail-fix loop), and neither copy had a recorded incident. The promote-repeat-findings ritual still covers facts exactly as it covers rules.

---

*False Floors is a trade mark of Digital First Pty Ltd, trading as Scale100 (AU application AMCZ-2616155657). This content is CC BY 4.0; the name is not part of that licence. Citing, mapping to, or claiming conformance with the catalogue needs no permission – see `LICENSE-CONTENT`.*

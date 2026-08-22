---
type: register
project: agent-trust-framework
layer: provenance
prefix: PL
title: Agent Provenance Layer — The Record of What Was Done
question: Is the record of what was done trustworthy?
unit: a unit of work
figma-node: "1395:139"
figma-file: KDkIqr0lzbcAUvJLGAcExk
rows: 22
class-a: 3
class-b: 14
class-c: 5
class-a-reads: prevented
class-b-reads: detected
class-c-reads: survives
evidenced: 12
candidate: 10
verified: describes the HullKey control set; row IDs are assigned by this register — the diagram adopted them at rev 2 on 9 August 2026, having predated the ID scheme
residual-basis: derived from cell strength gated on install state, corrected 2026-08-10 (C-02) — a `ONCE —` next action means the control is not switched on and the row reads open; otherwise any `closes` reads closed, else any `partial` reads partially closed, else open. This layer has no `built` field; the `ONCE —` next action is what stands in for one. Supersedes the "outcome x built state" basis recorded 2026-08-09 (D-061), which named a built state this layer never carried (C-03)
date: 2026-08-07
last-updated: 2026-08-21
---

# Agent Provenance Layer: the record of what was done

What breaks in the record of a unit of work, what it costs, and which layer can close it. Independent of any particular tracker.

**This file is canon; the Figma frame `1395:139` (rev 2) is a generated view.** Shared vocabulary: [[README|registers README]].

This layer uses its own three control positions instead of the eleven catch points — **harness gate** (at the moment of work), **repo artefact** (committed with the code), **control-plane check** (on the commit). Cell strength: **closes** — refuses or catches it every time · **partial** — conditional, or not switched on · **nothing** — nothing here closes it · **n/a** — not this layer's job. A row's class is set by its strongest cell, which is this register's instance of the shared rule that the letter grades how complete the remedy is ([[README|registers README]]) – the remedy here is the union of what the three positions do, so the strongest cell is the completeness of the best one available. **This register reads B as *detected* and C as *survives***. Its **residual** is derived from the same cells, but gated on install state first: **a row whose next action is a `ONCE —` install reads open**, because the control it names has not been switched on and therefore closes nothing today. For every other row, any `closes` reads closed, otherwise any `partial` reads partially closed, otherwise open. The install gate is what stops a cell describing control *design* from being read as control *state* — the defect that had 14 of these 24 rows reading closed on mechanisms nobody had turned on (C-02, corrected 2026-08-10). **Evidence** — `evidenced` (a receipt exists: a first-party incident mapping, a corpus-coded finding, or a filed public case) or `candidate` (enumerated in advance, no receipt yet); headline counts count evidenced rows only (D-107, [[README|registers README]]). **Residual** says what is actually true about the failure today, which is not the same as whether the named mechanism exists — see [[README|registers README]].

## 1 · Orientation and continuity (0 prevented · 1 detected · 1 survives)

| ID | Evidence | Sev | What breaks | What it costs | Harness gate | Repo artefact | Control-plane check | Outcome | Residual | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PL-1A | evidenced | S3 | Agent starts blind to prior work | Redoes finished work, or reverses last session’s decision | partial — Session-start digest | partial — Open questions in the record | n/a | C survives | open | ONCE — Install the session-start digest |
| PL-1C | candidate | S4 | Compaction drops a decision held only in context — or a constraint agreed in turn 3 is gone by turn 30 | Silently reverts to a default you ruled out | partial — Checkpoint before compaction; re-inject, not just recall | closes — Decision log entry; constraints as files, not chat | n/a | B detected | closed | AT EVERY DECISION — Log the decision before compaction |

## 2 · Claiming the work (1 prevented · 2 detected · 0 survive)

| ID | Evidence | Sev | What breaks | What it costs | Harness gate | Repo artefact | Control-plane check | Outcome | Residual | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PL-2A | candidate | S2 | Work done with no unit of work attached | Nobody can say later what it was for | closes — Require an active ticket | partial — Ticket committed with the code | partial — Assert every range has one | A prevented | open | ONCE — Require a ticket before work starts |
| PL-2B | candidate | S4 | The gate only fires once a ticket is claimed | Never engaging reads as a clean pass | nothing — Cannot catch its own absence | n/a | closes — Check the merged range | B detected | open | ONCE — Move the claim check into CI |
| PL-2C | candidate | S2 | Scope quietly expands mid-task | Files changed that nobody asked about | partial — Declare scope up front | closes — Ticket states intended scope | closes — Diff touched files vs declared | B detected | closed | EVERY TASK — Declare the scope when you brief the task |

## 3 · The record itself (1 prevented · 4 detected · 0 survive)

| ID | Evidence | Sev | What breaks | What it costs | Harness gate | Repo artefact | Control-plane check | Outcome | Residual | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PL-3A | evidenced | S3 | No record written at all | The reasoning is gone the moment the turn ends | closes — Block the turn ending | partial — Record is a committed file | partial — Assert a record exists | A prevented | open | ONCE — Install the turn-ending block |
| PL-3B | evidenced | S3 | Record omits the parts that matter | Reads fine, answers nothing you will ask later | n/a | closes — Required headings, validated | closes — Reject on missing sections | B detected | open | ONCE — Fix the record template, then validate it |
| PL-3C | evidenced | S4 | The doer writes its own success report | The record inherits the same blind spot | n/a | partial — Require SHAs and output, not prose | closes — Recompute rather than read | B detected | closed | EVERY RECORD — Require SHAs and output, not prose |
| PL-3D | candidate | S4 | Record edited after the fact | You review a tidied version of events | partial — Local append-only convention | closes — Git history exposes the revision | closes — Diff history against the accepted record | B detected | open | ONCE — Add an external append-only store if edits must be refused |
| PL-3E | evidenced | S4 | The gate fails open and says nothing | A dead sensor is indistinguishable from a pass | nothing — It is the thing that failed | n/a | closes — Assert the gate ran | B detected | open | ONCE — Assert in CI that the gate ran |

## 4 · Linking intent to code (1 prevented · 1 detected · 1 survives)

| ID | Evidence | Sev | What breaks | What it costs | Harness gate | Repo artefact | Control-plane check | Outcome | Residual | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PL-4A | candidate | S3 | Unlinked commit lands on a protected branch | Six months on, nobody knows why it changed | partial — Inject the ID on commit | partial — ID carried in the message | closes — Reject an unlinked exact revision | A prevented | open | ONCE — Install the commit-ID landing gate |
| PL-4B | evidenced | S3 | Commit linked to the wrong unit of work | Two sessions, one shared marker | partial — Per-session markers | n/a | n/a | C survives | partially closed | EVERY SESSION — Give each session its own marker |
| PL-4C | candidate | S2 | Decision made in chat, written nowhere | Re-litigated next month from scratch | partial — Prompt for a log entry | closes — Decision log is a file | partial — Require one per change | B detected | closed | AT EVERY DECISION — Write the decision down when you make it |

## 5 · Landing (0 prevented · 3 detected · 0 survive)

| ID | Evidence | Sev | What breaks | What it costs | Harness gate | Repo artefact | Control-plane check | Outcome | Residual | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PL-5A | evidenced | S4 | Done recorded on a branch that never landed | Shipped is asserted, never verified | n/a | partial — Board state on the target branch | closes — Check the artefact on target | B detected | closed | AT EVERY MERGE — Check the artefact on the target branch |
| PL-5B | candidate | S3 | Board diverges from the code | The tracker quietly becomes fiction | n/a | closes — Derive the board from the repo | partial — Diff derived vs published | B detected | open | ONCE — Derive the board from the repo |
| PL-5C | evidenced | S4 | Squash-merge breaks the ancestry | The provenance check answers the wrong question | n/a | n/a | closes — Test file existence, not ancestry | B detected | open | ONCE — Teach the check your merge strategy |

## 6 · Many agents, and who did what (0 prevented · 3 detected · 3 survive)

| ID | Evidence | Sev | What breaks | What it costs | Harness gate | Repo artefact | Control-plane check | Outcome | Residual | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PL-6A | evidenced | S3 | Parent returns before its children finish | Completed work is stranded, then paid for twice | partial — A synthesis stage that gathers | n/a | n/a | C survives | partially closed | EVERY RUN — Add a gather stage to every fan-out |
| PL-6B | evidenced | S3 | Large artefact held in context, never written | Finished work dies with the context | partial — Save incrementally, not at the end | closes — Partial work on disk is recoverable | n/a | B detected | closed | EVERY BRIEF — Brief agents to save as they go |
| PL-6C | evidenced | S4 | Two agents conflict; one overwrites the other | A correct change silently disappears | partial — Advisory mutation lock | partial — Atomic writes prevent torn files only | n/a | C survives | open | ONCE — Put every mutation behind an externally owned exclusive lock |
| PL-6D | candidate | S2 | Cannot tell which code an agent wrote | Review effort spread evenly over uneven risk | partial — Provenance trailer on commits | closes — Trailer carried in history | partial — Require the trailer | B detected | open | ONCE — Add the provenance trailer to commits |
| PL-6E | evidenced | S2 | Cannot tell which model produced it | A model-specific defect cannot be traced back | partial — Record the seat | closes — Seat in the session record | n/a | B detected | open | ONCE — Record the model seat in the session record |
| PL-6F | candidate | S1 | Record invisible without a repo clone | Nobody outside the terminal can see the state | n/a | partial — Generated board file | partial — Publish a projection | C survives | partially closed | WEEKLY — Publish the board projection |

**PL-6C is one of three rows on concurrent writes.** Atomic writes prevent torn files, not last-writer-wins, and an advisory lock does not constrain a writer that can ignore or remove it. [[recovery-layer|RL-1E]] covers fan-out worktree separation; [[authority-access-layer|AL-3C]] covers an ambient second session. All three remain open until every mutation is mediated by an externally owned lock or isolated write surface.

## Where it closes

At the moment of work 2 · committed with the code 9 · on the commit 6 · no layer closes it 5.

| Harness gate | Repo artefact | Control-plane check | Nothing |
|---|---|---|---|
| 2 | 9 | 6 | 5 |

Read left to right: how much has already happened by the time the record is closed. The harness gate acts while the work is being done; the repo artefact closes it at the commit; the control-plane check closes it after the merge, when the work is already finished. Only the harness gate can refuse before the record is wrong — every layer after it is telling you about something that has already happened. The work is to move each row left.

Evidence status (D-107): 12 of the 22 are evidenced — a recorded incident or corpus-coded finding has landed on the row — and 10 are candidates, enumerated in advance and still waiting for their receipt.

## The three positions

**Harness gate — at the moment of work.** Hooks and gates inside the agent's own runtime: session digests, blocking stop conditions, refusing direct edits to the record. Strength: the only layer that can stop a bad turn before it ends; nothing else acts in time. Weakness: it is the thing being checked. It cannot catch its own absence, and when it breaks it usually breaks silently open. Two of the twenty-two close here.

**Repo artefact — committed with the code.** The record as files in the repository: tickets, session records and decision logs, all moving in the same commit as the change. Strength: portable, diffable and readable at the version the work was done; exit cost near zero. Weakness: a file can be complete and still say nothing — structure is not substance. Nine close here: the largest single block, and the cheapest of the three to adopt.

**Control-plane check — on the commit.** CI running against the merged result, external to both the agent and the tracker; verifies the artefact rather than trusting the sensor. Strength: survives a change of tool, and is the only layer that can assert another layer actually ran. Weakness: runs late — it tells you the record is missing after the work is done, not before. Six close here. Five close nowhere at all, and those carry the survives outcome.

## The five that still reach you

- PL-1A — a digest that an adversarial agent cannot ignore
- PL-4B — a session marker that proves which unit of work a commit belongs to
- PL-6A — a fan-out without a gather stage is the defect itself
- PL-6C — an externally owned mutation boundary between concurrent writers
- PL-6F — a board projection someone outside the terminal can see

These are the open problems in this category, not omissions in the drawing.

## Reading notes

Provenance is not the truth layer. An agent can be perfectly honest and leave no usable trace, and it can leave an immaculate trace of work it misreported. Different failures, different controls.

Severity is cost multiplied by how silently it fails — a judgement, not a measurement. Acts early, but cannot check itself (harness gate); acts late, but is the only thing that can check the rest (control plane).

## Retired rows

Retired IDs are never reused and never renumbered (row ID rule 1). Each retirement carries its reason and its date; the full audit behind the pass is [[../framework-reviews/2026-08-21-framework-review-02-row-provenance|framework review 02]] and the decision is D-106.

- `PL-1B` — *earlier constraints not carried forward* — retired 2026-08-21, merged into `PL-1C`. The two rows shared one failure (session state silently lost between turn 3 and turn 30), one repair (write it to a file, not chat) and one class; PL-1B's distinct wording added a scenario, not a unit, and it carried no recorded incident. PL-1C's cells now carry the constraint case alongside the decision case. The instruction-shaped and context-shaped twins ([[instruction-layer|IL-1B]], [[context-layer|CL-1A]]) are unaffected — CL-1A is the copy with the recorded incident (D-084).
- `PL-4D` — *ticket text changed since the work* — retired 2026-08-21. The narrowest row in the register: a real audit concern (requirements edited after the fact) but one whose named mechanism is an architecture choice (move the tracker into the repo) rather than a control, with no recorded incident and no path to one while the tracker already lives in the repo here. The after-the-fact-editing class this row gestured at is carried by `PL-3D`, which is corpus-backed.

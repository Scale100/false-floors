---
type: register
project: agent-trust-framework
layer: recovery
prefix: RL
title: Agent Recovery Layer — Can You Get It Back
question: Can you get it back?
unit: a change
figma-node: "1389:139"
figma-file: KDkIqr0lzbcAUvJLGAcExk
rows: 24
class-a: 5
class-b: 10
class-c: 9
class-a-reads: prevented
class-b-reads: recoverable
class-c-reads: irreversible
evidenced: 11
candidate: 13
verified: design only except RL-1A, whose Claude Code baseline behaviour was verified against Anthropic documentation on 2026-08-10; all remaining install-state markers are provisional and still require machine verification before the diagram is shown
residual-basis: derived from outcome x built state on 2026-08-09 (D-061); substitutes and partial closures entered by hand only where evidenced
date: 2026-08-07
last-updated: 2026-08-21
---

# Agent Recovery Layer: can you get it back?

The life of a change, from the moment it exists to the moment it can no longer be undone.

**This file is canon; the Figma frame `1389:139` (rev 2) is a generated view.** Shared vocabulary: [[README|registers README]].

**Class grades how complete the remedy is**, on the shared definition in [[README|registers README]]. **This register reads B as *recoverable* and C as *irreversible*** – canonical here, and not interchangeable with the four aligned registers' *detected* and *survives*, which is why a cross-register total is stated in letters only (D-099). The readings: **Prevented · Class A** — it cannot be done irreversibly; **Recoverable · Class B** — it happened; you can get back; **Irreversible · Class C** — nothing gets you back. Note that C here does not mean undetectable: RL-2A is trivially detectable and still irreversible, because detection is not a complete remedy for a change you cannot take back. Severity grades cost-to-undo: S1 undone in seconds · S2 undone with effort · S3 undone only by rebuilding by hand · S4 cannot be undone at any price. Tool cells here carry no runtime tag — the mechanisms are runtime-agnostic unless named. **Evidence** — `evidenced` (a receipt exists: a first-party incident mapping, a corpus-coded finding, or a filed public case) or `candidate` (enumerated in advance, no receipt yet); headline counts count evidenced rows only (D-107, [[README|registers README]]). **Residual** says what is actually true about the failure today, which is not the same as whether the named mechanism exists — see [[README|registers README]].

## Stage 1 · CAPTURED — is there a point to go back to? (1 prevented · 2 recoverable · 3 irreversible)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome | Residual | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RL-1A | candidate | S3 | No restore point between the last good state and now | “It worked an hour and forty edits ago” | Automatic checkpoint before each user prompt | prompt | Claude Code checkpoints direct file-tool edits; rewind restores | Claude Code · automatic · built | A prevented | closed | DONE · 10 AUG 2026 — Built into Claude Code; no configuration required |
| RL-1B | candidate | S4 | Work happened where Git cannot see it | “It edited a file the repo has never held” | Keep every writable path under version control | on disk | Untracked-path audit on the working set | Git · maintained · designed | B recoverable | open | ONCE — Bring the stray working folders under Git |
| RL-1C | candidate | S4 | The data changed with no restore point | “The migration ran; the old rows are gone” | Snapshot before any schema or data change | pre-tool | Snapshot or branch gate before migrate | Supabase · maintained · designed | B recoverable | open | AT EVERY MIGRATION — Take the snapshot before you run it |
| RL-1D | candidate | S3 | The restore point caught the files, not the state | “The code came back; the data did not” | Decide what a restore point must include, per system | on disk | Restore scope declared per system | none · process · none | C irreversible | open | ONCE — Write down what a restore point must cover |
| RL-1E | evidenced | S3 | Two agents in a fan-out you started wrote the same tree at once | “Whose version is this?” | Give each agent an isolated writable surface | pre-tool | Git worktrees separate default paths but remain mutually reachable | Git worktree · maintained · built | C irreversible | open | AT EVERY FAN-OUT — Isolate each writable surface beyond the other agent's reach |
| RL-1F | evidenced | S4 | The backup you trusted has a snapshot cadence too coarse to catch a live incident | “Time Machine had a snapshot before and one after — nothing in between” | Give the at-risk tree a restore point taken at the moment of risk, not on a fixed background cadence | on disk | OS/vendor snapshot cadence is fixed and not agent-controllable | none · process · none | C irreversible | open | ONCE — Decide whether at-risk shared checkouts need an agent-native restore point (auto-stash / auto-commit) beyond what any OS backup guarantees |

**RL-1E is one of three rows on concurrent writes.** Worktrees reduce accidental collisions but are not an adversarial boundary when each agent can reach the other tree on the same writable filesystem. [[authority-access-layer|AL-3C]] covers the ambient second-session route; [[provenance-layer|PL-6C]] covers a correct change disappearing from the record. All three remain open until an externally enforced write boundary or mandatory broker exists.

**RL-1A is a baseline row (D-077): it records a vendor-supplied baseline control, not an installation recommendation.** It counts only edits made through Claude Code's direct file-editing tools. Bash commands, most subagent edits, external changes and long-term version history remain outside that checkpoint boundary and still require Git or another restore path.

**RL-1F was found, not designed.** The 2026-08-18 incident (Corrections Register C-55) hit exactly the gap this row describes: Time Machine's local snapshots skipped from the day before the loss to after it, for both affected files, and the only reason either file came back was Obsidian Sync's own incidental local File Recovery database — a feature of a paid third-party product with no backup mandate — which happened to hold a snapshot of one of the two lost files from roughly 20 minutes before the loss. The other file's edit window fell in exactly the same kind of gap in Obsidian's own cadence and was never recovered. **Residual reads *open*, per the global rule that Class C is always open outside the provenance exception ([[README|registers README]])** — the row names no mechanism, so nothing here is entitled to a substitute. In practice, [[recovery-layer#Stage 2 · CONTAINED|RL-2C]]'s gate does close one named subclass without changing this row's formal residual: a destructive git command blocked on a dirty tree forces a `git stash` before it can proceed, and that stash is a restore point taken at the exact moment of risk with zero cadence gap. That closes "destructive git command against a tracked file", the class that caused the incident — but not any other class of loss (an untracked file, a non-git edit, an editor overwrite outside a git-tracked path). Those remain exactly as exposed as before RL-2C existed, protected only by luck when the file happens to be open in a tool with its own incidental versioning at the time.

## Stage 2 · CONTAINED — how far can one mistake reach? (2 prevented · 0 recoverable · 2 irreversible)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome | Residual | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RL-2A | candidate | S4 | The agent could write anywhere on the machine | “It tidied a folder you never named” | Bound the writable surface before the turn starts | on disk | Agent-editable settings do not bound the operating-system principal | Claude Code · automatic · built | C irreversible | open | ONCE — Enforce an OS or host sandbox the agent cannot modify |
| RL-2B | candidate | S4 | Permissions were waived for the whole session | “It was faster with the prompts off” | Waive per action, never per session | prompt | Skip-permissions only inside a sandbox | none · process · none | C irreversible | open | EVERY SESSION — Never open a session with permissions off |
| RL-2C | evidenced | S4 | A destructive command ran before you saw it | “rm -rf, and it was already gone” | Refuse the command shape, not the intent | pre-tool | Deny pattern on destructive shell shapes, conditioned on a dirty working tree | Hook · maintained · built | A prevented | closed | DONE · 18 AUG 2026 — `~/.claude/hooks/destructive-git-guard.sh`, wired via `PreToolUse` in `~/.claude/settings.json`; C-54 |
| RL-2D | evidenced | S4 | The change reached production directly | “There was nothing in between” | Make production reachable only through a gate | CI | Deploy only from a protected branch | Branch rules · maintained · built | A prevented | closed | ONCE — Protect the branch that deploys |

## Stage 3 · NOTICED — do you find out while it is still cheap? (0 prevented · 3 recoverable · 1 irreversible)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome | Residual | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RL-3A | candidate | S2 | Nobody read the diff before it was committed | “It said done, so it was done” | Read the diff, not the summary | pre-commit | Diff review gate on agent commits | Git · maintained · built | B recoverable | closed | EVERY COMMIT — Read the diff before you accept it |
| RL-3B | candidate | S4 | The damage surfaced weeks later | “This has been wrong since July” | A check that would have failed at the time | CI | Regression test on the broken invariant | CI · maintained · built | B recoverable | closed | AT EVERY LATE BUG — Add the test that would have caught it |
| RL-3C | evidenced | S3 | Success was reported on work never finished | “The report says done; the file is not there” | Verify the artifact, not the report | stop | Artifact existence check at end of turn | Hook · maintained · designed | B recoverable | open | EVERY TASK — Check the file on disk, not the summary |
| RL-3D | evidenced | S3 | Partial work stayed in context, never written | “The agent finished and the work went with it” | Save incrementally, never once at the end | subagent | Incremental-write instruction in every brief | none · process · none | C irreversible | open | EVERY BRIEF — Tell the agent to write as it goes |

## Stage 4 · REVERSIBLE — can the change be taken back? (2 prevented · 3 recoverable · 0 irreversible)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome | Residual | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RL-4A | evidenced | S2 | The merge was squashed and the branch reused | “The next PR re-applied everything” | Cut a fresh branch after a squash merge | on disk | Parent-count check before branching | Git · maintained · designed | B recoverable | open | AT EVERY MERGE — Cut a new branch; never reuse the merged one |
| RL-4B | candidate | S4 | History was rewritten over the only copy | “Force-pushed, and the old commits are gone” | Refuse force-push on shared branches | on disk | Force-push blocked server-side | Branch rules · maintained · built | A prevented | closed | ONCE — Block force-push on the shared branches |
| RL-4C | candidate | S3 | The migration has no way back | “You can go forward or nowhere” | Write the reversal with the change | pre-commit | Migration refused without a down script | CI · maintained · designed | B recoverable | open | AT EVERY MIGRATION — Write the down script first |
| RL-4D | evidenced | S3 | Files were moved rather than copied | “The move flattened the folders” | Copy, verify, then delete | pre-tool | Copy-and-verify gate in place of move | rsync · maintained · designed | B recoverable | open | AT EVERY MIGRATION — Copy and verify before you delete |
| RL-4E | evidenced | S4 | The side effect left the machine | “The email has already gone” | Hold outbound actions behind a human gate | pre-tool | Confirm gate on outbound and paid actions | Hook · maintained · designed | A prevented | open | ONCE — Gate every action that leaves the machine |

## Stage 5 · RESTORED — does undoing it put you back? (0 prevented · 1 recoverable · 2 irreversible)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome | Residual | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RL-5A | evidenced | S3 | The revert restored the code and broke the data | “The rollback made it worse” | Reverse code and data as one unit | CI | Paired code and data rollback plan | none · process · none | C irreversible | open | AT EVERY RELEASE — Say how the data comes back, too |
| RL-5B | candidate | S4 | The restore was never once tested | “The backups existed; none of them worked” — including a runbook that exists and has never been run | Restore on a schedule, not on an incident | review | Scheduled restore drill that must pass, dated, with a time on it | Cron · maintained · designed | B recoverable | open | QUARTERLY — Restore from backup and time it |
| RL-5D | evidenced | S3 | The retry re-derived work already paid for | “It started again from nothing” | Feed the finished output into the retry | subagent | Orphan output collected before retry | none · process · none | C irreversible | open | EVERY RETRY — Give the retry what the last run finished |

## Assurance · REHEARSED — would you get back if you had to today? (0 prevented · 1 recoverable · 1 irreversible)

Not a sixth step. This band applies across stages 1 to 5 — each row asks whether the stage above would actually hold.

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome | Residual | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RL-6B | candidate | S4 | The restore point is older than you think | “The last good snapshot is from March” | Alert on snapshot age, not on its existence | CI | Snapshot freshness check | Supabase · maintained · designed | B recoverable | open | ONCE — Alert on snapshot age |
| RL-6C | candidate | S3 | Nobody knows who calls the rollback | “Everyone waited for someone else” | Name the decider before the incident | on disk | Named rollback authority, required field | Schema lint · maintained · designed | C irreversible | open | ONCE — Write down who calls the rollback |

## Catch-point distribution

Before it starts 7 · before the change 9 · still in the session 1 · after the session 7.

| on disk | session start | prompt | pre-tool | subagent | post-tool | compact | stop | pre-commit | CI | review |
|---|---|---|---|---|---|---|---|---|---|---|
| 7 | 0 | 2 | 5 | 2 | 0 | 0 | 1 | 2 | 4 | 1 |

Read left to right: how much has already been done by the time you try to take it back. Before it starts, there is nothing to undo. A change that was never made needs no recovery, and the earlier it is refused, the less there is to get back.

## The stack for this layer

- Checkpointing and rewind: Claude Code session state — RL-1A
- Permissions, deny rules, confirm and Stop gates: hooks — RL-2A, RL-2C, RL-3C, RL-4E
- Version control: commits, stashes, untracked-path audit — RL-1B, RL-3A
- Worktrees: one writable tree per parallel agent — RL-1E
- Database snapshots and branches, plus a freshness alert — RL-1C, RL-6B
- Branch protection: protected deploys, no force-push — RL-2D, RL-4B
- Pre-commit and CI: down script, regression test, parent count — RL-3B, RL-4A, RL-4C
- Copy-and-verify in place of move; scheduled restore drill — RL-4D, RL-5B

## What that buys

Of 24 failures: 5 are prevented, 10 are recoverable, and 9 are irreversible. 18 name a tool or an automated check; six are process only. Naming a mechanism is not installing it — 10 of the 18 are not built in `hullkey-charge` today (RL-2C moved from designed to built 2026-08-18, C-54). Worktree separation and agent-editable settings reduce accidental damage but do not constrain an adversarial agent; prevention requires a boundary outside its writable authority.

Evidence status (D-107): 11 of the 24 are evidenced — a recorded incident or corpus-coded finding has landed on the row — and 13 are candidates, enumerated in advance and still waiting for their receipt.

## The seven that still reach you

- RL-1D — a restore point that covers state, not just files
- RL-1F — a backup cadence tight enough to catch a live incident, for anything outside a git-tracked, RL-2C-gated file
- RL-2B — a way to waive one action without waiving the session
- RL-3D — a guarantee that partial work reaches disk
- RL-5A — a rollback that reverses code and data together
- RL-5D — a retry that inherits what the last run finished
- RL-6C — a named person who calls the rollback

Four are decisions nobody has written down. Three are orchestration gaps — the work exists and nothing carries it across the handoff.

## Reading notes

Recovery class is a property of the mechanism, not of the change. Writing a rollback plan changes how often you need it, never whether the change can be taken back. Only a mechanism that refuses the action yields Class A.

Severity is the cost of getting back multiplied by how quietly the change goes unnoticed. It is a judgement, not a measurement. The install-state markers on this layer are provisional — they have not been verified against this machine, and that pass is owed before the diagram is shown.

## Retired rows

Retired IDs are never reused and never renumbered (row ID rule 1). Each retirement carries its reason and its date; the full audit behind the pass is [[../framework-reviews/2026-08-21-framework-review-02-row-provenance|framework review 02]] and the decision is D-106.

- `RL-5C` — *recovery cost more than the work it saved* — retired 2026-08-21. A planning heuristic, not a failure a control can refuse or catch: it named no mechanism, carried no recorded incident, and its "stated abandon threshold" is briefing advice rather than a register row. The advice survives in operating practice; it no longer counts as a failure mode.
- `RL-6A` — *the runbook exists and nobody has run it* — retired 2026-08-21, merged into `RL-5B`. Both rows demanded the same control on the same cadence (a dated, timed restore drill, quarterly); RL-6A restated RL-5B's failure from the assurance band without adding a distinct mechanism or class. RL-5B's symptom and mechanism cells now carry the unrun-runbook case explicitly.

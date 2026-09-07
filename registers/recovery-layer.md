---
type: register
project: agent-trust-framework
layer: recovery
prefix: RL
# The column holding the failure title. Declared rather than inferred from
# position: C-117 shipped a gate that took the column after `Sev`, and a metadata
# column inserted between the two silently replaced every title while the gate
# reported ok. Identity survives insertion and reordering; adjacency does not.
title-column: Failure
title: Agent Recovery Layer — Can You Get It Back
question: Can you get it back?
unit: a change
figma-node: "120:2"
figma-file: 9KIzmsPS1EzWNQiOFKjWzX
rows: 24
class-a: 4
class-b: 10
class-c: 10
class-a-reads: prevented
class-b-reads: recoverable
class-c-reads: irreversible
evidenced: 11
candidate: 13
derived: 2026-08-06 — rows enumerated against one coding-agent harness and one production codebase (project-alpha); RL-1A’s harness baseline behaviour read from Anthropic documentation on 2026-08-10
gap-basis: derived from outcome x built state on 2026-08-09 (D-061); substitutes and partial closures entered by hand only where evidenced
date: 2026-08-07
last-updated: 2026-08-23
---

# Agent Recovery Layer: can you get it back?

The life of a change, from the moment it exists to the moment it can no longer be undone.

**This file is canon; the Figma frame `1:4294` (rev 2) is a generated view.** Shared vocabulary: [registers README](README.md).

**Class grades how complete the remedy is**, on the shared definition in [registers README](README.md). **This register reads B as *recoverable* and C as *irreversible*** – canonical here, and not interchangeable with the four aligned registers' *detected* and *survives*, which is why a cross-register total is stated in letters only (D-099). The readings: **Prevented · Class A** — it cannot be done irreversibly; **Recoverable · Class B** — it happened; you can get back; **Irreversible · Class C** — nothing gets you back. Note that C here does not mean undetectable: RL-2A is trivially detectable and still irreversible, because detection is not a complete remedy for a change you cannot take back. Severity grades cost-to-undo: S1 undone in seconds · S2 undone with effort · S3 undone only by rebuilding by hand · S4 cannot be undone at any price. Tool cells here carry no runtime tag — the mechanisms are runtime-agnostic unless named. **Evidence** — `evidenced` (a receipt exists: a first-party incident mapping, a corpus-coded finding, or a filed public case) or `candidate` (enumerated in advance, no receipt yet); headline counts count evidenced rows only (D-107, [registers README](README.md)). **Availability** says whether a control of the named shape exists at all — `available` · `none` · `withdrawn` — and never whether one is switched on anywhere, which is an assessment fact and lives in `../assessments/` (D-263). See [registers README](README.md).

## Stage 1 · CAPTURED — is there a point to go back to? (1 prevented · 2 recoverable · 3 irreversible)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RL-1A | candidate | S3 | No restore point between the last good state and now | “It worked an hour and forty edits ago” | Automatic checkpoint before each user prompt | prompt | Claude Code checkpoints direct file-tool edits; rewind restores | Claude Code · automatic · available | A prevented |
| RL-1B | candidate | S4 | Work happened where Git cannot see it | “It edited a file the repo has never held” | Keep every writable path under version control | on disk | Untracked-path audit on the working set | Git · maintained · available | B recoverable |
| RL-1C | candidate | S4 | The data changed with no restore point | “The migration ran; the old rows are gone” | Snapshot before any schema or data change | pre-tool | Snapshot or branch gate before migrate | Supabase · maintained · available | B recoverable |
| RL-1D | candidate | S3 | The restore point caught the files, not the state | “The code came back; the data did not” | Decide what a restore point must include, per system | on disk | Restore scope declared per system | none · process · none | C irreversible |
| RL-1E | evidenced | S3 | Two agents in a fan-out you started wrote the same tree at once | “Whose version is this?” | Give each agent an isolated writable surface | pre-tool | Worktrees separate paths but remain mutually reachable | Git worktree · maintained · available | C irreversible |
| RL-1F | evidenced | S4 | The backup you trusted has a cadence too coarse for a live incident | “A snapshot before and one after, nothing in between” | Give the at-risk tree a restore point taken at the moment of risk, not on a fixed background cadence | on disk | OS/vendor snapshot cadence is fixed and not agent-controllable | none · process · none | C irreversible |

**RL-1E is one of three rows on concurrent writes.** Worktrees reduce accidental collisions but are not an adversarial boundary when each agent can reach the other tree on the same writable filesystem. [AL-3C](authority-access-layer.md) covers the ambient second-session route; [PL-6C](provenance-layer.md) covers a correct change disappearing from the record. All three remain open until an externally enforced write boundary or mandatory broker exists.

**RL-1A is a baseline row (D-077): it records a vendor-supplied baseline control, not an installation recommendation.** It counts only edits made through Claude Code's direct file-editing tools. Bash commands, most subagent edits, external changes and long-term version history remain outside that checkpoint boundary and still require Git or another restore path.

**RL-1F was found, not designed.** The 2026-08-18 incident (Corrections Register C-55) hit exactly the gap this row describes: Time Machine's local snapshots skipped from the day before the loss to after it, for both affected files, and the only reason either file came back was Obsidian Sync's own incidental local File Recovery database — a feature of a paid third-party product with no backup mandate — which happened to hold a snapshot of one of the two lost files from roughly 20 minutes before the loss. The other file's edit window fell in exactly the same kind of gap in Obsidian's own cadence and was never recovered. **Gap reads *open*, per the global rule that Class C is always open outside the provenance exception ([registers README](README.md))** — the row names no mechanism, so nothing here is entitled to a substitute. In practice, [RL-2C](recovery-layer.md)'s gate does close one named subclass without changing this row's formal gap: a destructive git command blocked on a dirty tree forces a `git stash` before it can proceed, and that stash is a restore point taken at the exact moment of risk with zero cadence gap. That closes "destructive git command against a tracked file", the class that caused the incident — but not any other class of loss (an untracked file, a non-git edit, an editor overwrite outside a git-tracked path). Those remain exactly as exposed as before RL-2C existed, protected only by luck when the file happens to be open in a tool with its own incidental versioning at the time.

## Stage 2 · CONTAINED — how far can one mistake reach? (1 prevented · 0 recoverable · 3 irreversible)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RL-2A | candidate | S4 | The agent could write anywhere on the machine | “It tidied a folder you never named” | Bound the writable surface before the turn starts | on disk | Agent-editable settings do not bound the OS principal | Claude Code · automatic · available | C irreversible |
| RL-2B | candidate | S4 | Permissions were waived for the whole session | “It was faster with the prompts off” | Waive per action, never per session | prompt | Skip-permissions only inside a sandbox | none · process · none | C irreversible |
| RL-2C | evidenced | S4 | A destructive command ran before you saw it | “rm -rf, and it was already gone” | Refuse the command shape, not the intent | pre-tool | Deny pattern on destructive shell shapes when the tree is dirty | Hook · maintained · available | C irreversible |
| RL-2D | evidenced | S4 | The change reached production directly | “There was nothing in between” | Make production reachable only through a gate | CI | Deploy only from a protected branch | Branch rules · maintained · available | A prevented |

**RL-2C's cell names the shape of the control; the shapes themselves are here.** `destructive-git-guard.sh` refuses FIVE enumerated command shapes — `rm`, `git reset --hard`, `git clean -f`, `git checkout --` and `git restore` — and only when the working tree is dirty, so the refusal forces a `git stash` that is itself a restore point taken at the moment of risk. The enumeration lived in the Mechanism cell until 2026-09-07 and moved here when canon became the single wording for the register, the diagram and the published spoke alike: a cell that has to fit a 310px column cannot also carry a five-item list, and holding two wordings for one control is the drift this project exists to catch. Nothing constrains length in this note.

## Stage 3 · NOTICED — do you find out while it is still cheap? (0 prevented · 3 recoverable · 1 irreversible)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RL-3A | candidate | S2 | Nobody read the diff before it was committed | “It said done, so it was done” | Read the diff, not the summary | pre-commit | Diff review gate on agent commits | Git · maintained · available | B recoverable |
| RL-3B | candidate | S4 | The damage surfaced weeks later | “This has been wrong since July” | A check that would have failed at the time | CI | Regression test on the broken invariant | CI · maintained · available | B recoverable |
| RL-3C | evidenced | S3 | Success was reported on work never finished | “The report says done; the file is not there” | Verify the artifact, not the report | stop | Artifact existence check at end of turn | Hook · maintained · available | B recoverable |
| RL-3D | evidenced | S3 | Partial work stayed in context, never written | “The agent finished and the work went with it” | Save incrementally, never once at the end | subagent | Incremental-write instruction in every brief | none · process · none | C irreversible |

## Stage 4 · REVERSIBLE — can the change be taken back? (2 prevented · 3 recoverable · 0 irreversible)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RL-4A | evidenced | S2 | The merge was squashed and the branch reused | “The next PR re-applied everything” | Cut a fresh branch after a squash merge | on disk | Parent-count check before branching | Git · maintained · available | B recoverable |
| RL-4B | candidate | S4 | History was rewritten over the only copy | “Force-pushed, and the old commits are gone” | Refuse force-push on shared branches | on disk | Force-push blocked server-side | Branch rules · maintained · available | A prevented |
| RL-4C | candidate | S3 | The migration has no way back | “You can go forward or nowhere” | Write the reversal with the change | pre-commit | Migration refused without a down script | CI · maintained · available | B recoverable |
| RL-4D | evidenced | S3 | Files were moved rather than copied | “The move flattened the folders” | Copy, verify, then delete | pre-tool | Copy-and-verify gate in place of move | rsync · maintained · available | B recoverable |
| RL-4E | evidenced | S4 | The side effect left the machine | “The email has already gone” | Hold outbound actions behind a human gate | pre-tool | Confirm gate on outbound and paid actions | Hook · maintained · available | A prevented |

## Stage 5 · RESTORED — does undoing it put you back? (0 prevented · 1 recoverable · 2 irreversible)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RL-5A | evidenced | S3 | The revert restored the code and broke the data | “The rollback made it worse” | Reverse code and data as one unit | CI | Paired code and data rollback plan | none · process · none | C irreversible |
| RL-5B | candidate | S4 | The restore was never once tested | “The backups existed; none of them worked” | Restore on a schedule, not on an incident | review | Scheduled restore drill that must pass, dated, with a time on it | Cron · maintained · available | B recoverable |
| RL-5D | evidenced | S3 | The retry re-derived work already paid for | “It started again from nothing” | Feed the finished output into the retry | subagent | Orphan output collected before retry | none · process · none | C irreversible |

**RL-5B includes the runbook nobody has run.** The row is not only the backup that restores badly. A documented restore procedure that exists, is current, and has never once been executed is the same failure wearing a better hat: it is believed because it is written down, and the belief is untested. That clause sat in the Shows-up-as cell until 2026-09-07 and moved here when the cell had to fit a 360px column — at 99 characters it wrapped. The row's mechanism, a scheduled restore drill that must pass and is dated, is what discharges both readings.

## Assurance · REHEARSED — would you get back if you had to today? (0 prevented · 1 recoverable · 1 irreversible)

Not a sixth step. This band applies across stages 1 to 5 — each row asks whether the stage above would actually hold.

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RL-6B | candidate | S4 | The restore point is older than you think | “The last good snapshot is from March” | Alert on snapshot age, not on its existence | CI | Snapshot freshness check | Supabase · maintained · available | B recoverable |
| RL-6C | candidate | S3 | Nobody knows who calls the rollback | “Everyone waited for someone else” | Name the decider before the incident | on disk | Named rollback authority, required field | Schema lint · maintained · available | C irreversible |

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

Of 24 failures: 4 are prevented, 10 are recoverable, and 10 are irreversible. 18 name a tool or an automated check; six are process only. Naming a mechanism is not installing it, and whether it is installed anywhere is not a fact this catalogue carries. Install state is an assessment fact — one environment, on a date — and lives in `../assessments/` (D-263). RL-2C is the row that shows why the distinction matters: a destructive command ran against a dirty working tree on 2026-08-18 and cost another session its uncommitted work, and the mechanism that would have caught it existed the whole time (internal correction C-54). Worktree separation and agent-editable settings reduce accidental damage but do not constrain an adversarial agent; prevention requires a boundary outside its writable authority.

Evidence status (D-107): 11 of the 24 are evidenced — a recorded incident or corpus-coded finding has landed on the row — and 13 are candidates, enumerated in advance and still waiting for their receipt.

## The ten that still reach you

- RL-1D — a restore point that covers state, not just files
- RL-1E — one writable surface per agent, beyond the other agent's reach
- RL-1F — a backup cadence tight enough to catch a live incident, for anything outside a git-tracked, RL-2C-gated file
- RL-2A — a host sandbox the agent cannot edit its way out of
- RL-2B — a way to waive one action without waiving the session
- RL-2C — a refusal that covers the destructive shapes nobody enumerated
- RL-3D — a guarantee that partial work reaches disk
- RL-5A — a rollback that reverses code and data together
- RL-5D — a retry that inherits what the last run finished
- RL-6C — a named person who calls the rollback

Four are decisions nobody has written down. Three are orchestration gaps — the work exists and nothing carries it across the handoff. Three are boundaries the agent can still reach around: one writable surface per agent, a host sandbox it cannot edit, and a refusal that covers only the destructive shapes somebody enumerated.

*This section listed seven until 2026-09-05, omitting RL-1E and RL-2A, and nine until 2026-09-06, omitting RL-2C as well. All three read `C irreversible`, and all three are bounded-surface failures rather than the decision or orchestration gaps the original two sentences described — which is why adding them needed a third clause, not a bigger number. RL-2C is the one a hand count keeps missing: its next action reads `DONE`, and a DONE action records that the step was taken, not that the outcome changed. This list is now derived from the Outcome column by a check rather than maintained by hand, so the reading no longer depends on anyone noticing that.*

## Reading notes

Recovery class is a property of the mechanism, not of the change. Writing a rollback plan changes how often you need it, never whether the change can be taken back. Only a mechanism that refuses the action yields Class A.

Severity is the cost of getting back multiplied by how quietly the change goes unnoticed. It is a judgement, not a measurement. The install-state markers on this layer are provisional — they have not been verified against this machine, and that pass is owed before the diagram is shown.

## Retired rows

Retired IDs are never reused and never renumbered (row ID rule 1). Each retirement carries its reason and its date; the full audit behind the pass is framework review 02 and the decision is D-106.

- `RL-5C` — *recovery cost more than the work it saved* — retired 2026-08-21. A planning heuristic, not a failure a control can refuse or catch: it named no mechanism, carried no recorded incident, and its "stated abandon threshold" is briefing advice rather than a register row. The advice survives in operating practice; it no longer counts as a failure mode.
- `RL-6A` — *the runbook exists and nobody has run it* — retired 2026-08-21, merged into `RL-5B`. Both rows demanded the same control on the same cadence (a dated, timed restore drill, quarterly); RL-6A restated RL-5B's failure from the assurance band without adding a distinct mechanism or class. RL-5B's symptom and mechanism cells now carry the unrun-runbook case explicitly.

---

*False Floors is a trade mark of Digital First Pty Ltd, trading as Scale100 (AU application AMCZ-2616155657). This content is CC BY 4.0; the name is not part of that licence. Citing, mapping to, or claiming conformance with the catalogue needs no permission – see `LICENSE-CONTENT`.*

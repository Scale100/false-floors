---
type: register
project: agent-trust-framework
layer: authority-access
prefix: AL
# The column holding the failure title. Declared rather than inferred from
# position: C-117 shipped a gate that took the column after `Sev`, and a metadata
# column inserted between the two silently replaced every title while the gate
# reported ok. Identity survives insertion and reordering; adjacency does not.
title-column: Failure
title: Agent Authority and Access Layer — What It Could Reach
question: What could it reach?
unit: a permission
figma-node: "98:2"
figma-file: 9KIzmsPS1EzWNQiOFKjWzX
rows: 23
class-a: 2
class-b: 14
class-c: 7
class-a-reads: prevented
class-b-reads: detected
class-c-reads: survives
evidenced: 16
candidate: 7
derived: 2026-08-06 — rows read from project-alpha’s security register; every row either happened there once or is a control gap recorded against it
gap-basis: derived from outcome x built state on 2026-08-09 (D-061); substitutes and partial closures entered by hand only where evidenced
date: 2026-08-07
last-updated: 2026-08-23
---

# Agent Authority and Access Layer: what it could reach

The life of a permission, stage by stage, and what happens at each stage when it is crossed.

**This file is canon; the Figma frame `1:3386` (rev 2) is a generated view.** Shared vocabulary: [registers README](README.md).

This layer adds the **authority** column: unbypassable means the control runs beyond the agent's reach; bypassable means a login, a local hook, or a file the agent can edit. Eleven of the twenty-three are enforced somewhere the agent cannot reach; the other twelve rest on a file, a habit, or a login it can change. Column key otherwise as the instruction layer, including the **Evidence** tier (`evidenced` — a receipt exists; `candidate` — enumerated in advance, no receipt yet; headline counts count evidenced rows only, D-107) and the class letters: class grades how complete the remedy is ([registers README](README.md)), and **this register reads B as *detected* and C as *survives***. **Availability** says whether a control of the named shape exists at all — `available` · `none` · `withdrawn` — and never whether one is switched on anywhere, which is an assessment fact and lives in `../assessments/` (D-263). See [registers README](README.md).

## Stage 1 · GRANTED — is the boundary written down at all? (0 prevented · 4 detected · 2 survive)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Authority | Tool | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AL-1A | candidate | S4 | Nobody listed what the session can reach | “It had the token because you were logged in” | Inventory every credential a local process can use | on disk | Nothing reads what this machine is logged in to | none | none · any runtime · process · none | C survives |
| AL-1B | candidate | S2 | The limit lives in the prompt, not in a policy | “I told it not to touch production” | Put every “do not touch” beyond the writable surface | pre-tool | A deny rule in a file the agent can edit is not a boundary | bypassable | Claude Code · Claude Code · automatic · available | C survives |
| AL-1C | evidenced | S3 | The comment and the grant say different things | “The comment says service_role only” | Generate the doc from the grant; never restate it | CI | CI diffs the stated grant against the shipped one | unbypassable | CI · any runtime · maintained · available | B detected |
| AL-1D | evidenced | S1 | A default grant nobody chose | “PUBLIC could run it the day it was created” | Revoke explicitly; never rely on a default | pre-commit | Lint fails a new function with no explicit revoke | unbypassable | Grant lint · any runtime · automatic · available | B detected |
| AL-1E | evidenced | S3 | It runs as its author, so policy is not the judge | “Row security never gets a say in this call” | List every definer function and who may call it | CI | CI lists definer functions and their grantees | unbypassable | Grant lint · any runtime · automatic · available | B detected |
| AL-1F | evidenced | S2 | A column the policy never constrains | “Created already revoked, in someone else’s name” | Constrain every field the record is trusted for | CI | A test writes the forged value and expects refusal | unbypassable | pgTAP · any runtime · automatic · available | B detected |

## Stage 2 · SCOPED — does the grant match the job? (0 prevented · 2 detected · 1 survives)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Authority | Tool | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AL-2A | evidenced | S4 | The session holds more than the task needs | “Read-only work, write-capable credentials” | Issue the narrowest credential the task can use | session start | Nothing checks which key the session picked up | none | none · any runtime · process · none | C survives |
| AL-2B | candidate | S4 | One admin flag bypasses the whole rule | “Admin can, so the rule does not apply” | Write the exception as a policy, not a bypass | CI | A test asserts admin cannot reverse a one-way step | unbypassable | pgTAP · any runtime · automatic · available | B detected |
| AL-2C | evidenced | S4 | A reach path across tenants nobody tested | “Descent reaches further than you thought” | Prove every reach path, including assumed ones | CI | The isolation matrix has a cell for every path | unbypassable | pgTAP · any runtime · automatic · available | B detected |

## Stage 3 · REACHABLE — is there a route around the gate? (1 prevented · 1 detected · 1 survives)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Authority | Tool | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AL-3A | evidenced | S4 | A local credential routes around every gate | “It never went near a pull request” | Deploy only from CI; unlink the local client | session start | Unlinking is a habit, not a thing that refuses | bypassable | Supabase CLI · any runtime · maintained · available | B detected |
| AL-3B | evidenced | S3 | A local guard that one flag defeats | “--no-verify, and the hook is gone” | Put the same rule on the server, not the laptop | pre-commit | Server-side ruleset, with no bypass for the owner | unbypassable | GitHub · any runtime · automatic · available | A prevented |
| AL-3C | evidenced | S4 | A second session writing underneath the first — one you did not start | “The file I deleted exists again” | One writer per repo, or a worktree each | session start | Nothing tells one session another is writing | none | none · any runtime · process · none | C survives |

**AL-3C is one of three rows on concurrent writes, and they divide by question, not by verdict.** This row covers the *ambient* case: two sessions that happen to have the same repo open, where nothing tells either that the other exists. [RL-1E](recovery-layer.md) covers a fan-out you dispatched, where you know the agents exist and can give each one a worktree. [PL-6C](provenance-layer.md) covers the record consequence — a correct change disappearing from the record. Three registers, three questions, one incident: this is the co-owned pattern, not a contradiction (C-10). **All three read `open`**, and stay open until an externally enforced write boundary or a mandatory mutation broker exists: ordinary worktrees separate default paths but do not refuse a writer that can reach the other tree on the same filesystem (D-080).

*Until 2026-09-06 this paragraph said RL-1E reads `A prevented · closed` and used that as the contrast with AL-3C. D-080 moved RL-1E to `C irreversible · open` on 10 August 2026 and explicitly narrowed D-074's worktree claim; [recovery-layer](recovery-layer.md) and [provenance-layer](provenance-layer.md) were both updated to say all three remain open, and this note was not. The distinction between the three rows was never the verdict — it is which question each register asks.*

## Stage 4 · ENFORCED — will anything actually refuse it? (1 prevented · 2 detected · 2 survive)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Authority | Tool | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AL-4A | evidenced | S4 | The gate runs on the route it did not take | “Straight to main, so nothing ran” | Gate the destination, not the polite route to it | pre-commit | Required checks sit on the branch, not on the PR | unbypassable | GitHub · any runtime · automatic · available | A prevented |
| AL-4B | evidenced | S4 | The check asks a different question | “It shipped a test with it, so it passed” | An authorisation control must check authorisation | CI | The guard reads the diff for policy and grant changes | unbypassable | CI guard · any runtime · automatic · available | B detected |
| AL-4C | candidate | S3 | Asked for a report, it edited the repository | “You asked for a report; it wrote a migration” | Deny the write; do not request restraint | pre-tool | A prompt asks for restraint; nothing refuses the write | bypassable | Claude Code · Claude Code · automatic · available | C survives |
| AL-4D | evidenced | S4 | The log’s guard can be dropped by what it logs | “An owner can drop the trigger” | Ship the log off the platform that writes it | review | The audit trail is defended by the thing it audits | bypassable | none · any runtime · process · none | C survives |
| AL-4E | candidate | S2 | The approval gate with nobody to approve | “Review required, zero reviewers required” | Say plainly which gates are structural only | pre-commit | A pull request is required; a second reader is not | bypassable | GitHub · any runtime · automatic · available | B detected |

## Stage 5 · HELD — does the boundary survive the session? (0 prevented · 3 detected · 0 survive)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Authority | Tool | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AL-5A | evidenced | S3 | The grant outlives the reason for it | “Still visible long after they left” | Bound each grant to the window that justifies it | CI | A test asserts the grant expires with the window | unbypassable | pgTAP · any runtime · automatic · available | B detected |
| AL-5B | candidate | S2 | A subagent inherits more than its brief | “The child could write what the parent could” | Give the child its own tools, not the parent’s | subagent | The tool list is a file the agent can also edit | bypassable | Claude Code · Claude Code · automatic · available | B detected |
| AL-5C | candidate | S3 | An accepted risk becomes a forgotten one | “We decided to live with it, once” | Every acceptance carries a named reopen trigger | review | A register field, only as good as the reading of it | bypassable | Register · any runtime · maintained · available | B detected |

## Assurance · CHECKED — would you find out that it crossed? (0 prevented · 2 detected · 1 survives)

Not a sixth step. This band applies across stages 1 to 5 — each row asks whether the stage above would have told you.

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Authority | Tool | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AL-6A | evidenced | S4 | The control was never watched failing anything | “Green from the day it was written” | Test each control against a case it must catch | CI | The guard pattern is replayed against real history | unbypassable | CI guard · any runtime · automatic · available | B detected |
| AL-6B | evidenced | S3 | The tool’s own account is the only record | “Its files-changed list left one out” | Diff the repository; do not read the summary | review | Diffing is a habit; nothing runs it for you | bypassable | git · any runtime · maintained · available | B detected |
| AL-6C | evidenced | S3 | Crossed and sanctioned look identical | “It was approved; nobody checked the log” | Read the decision record before calling it a breach | review | No check tells a sanctioned change from a breach | none | none · any runtime · process · none | C survives |

## Catch-point distribution

Before it starts 4 · before the change 3 · still in the session 0 · after the session 16.

| on disk | session start | prompt | pre-tool | subagent | post-tool | compact | stop | pre-commit | CI | review |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 3 | 0 | 2 | 1 | 0 | 0 | 0 | 4 | 8 | 4 |

Nothing in this layer is caught while the session is still running — authority is settled before the agent starts, or discovered after it has finished. The work is to move each row left.

## The stack for this layer

- Postgres grants and row-level policies — AL-1D, AL-1E, AL-2B, AL-5A
- pgTAP behavioural isolation suite — AL-1F, AL-2B, AL-2C, AL-5A
- GitHub rulesets and required checks — AL-3B, AL-4A, AL-4E
- CI access-control guard over policy and grant changes — AL-1C, AL-4B, AL-6A
- Claude Code permission rules and pre-tool hooks — AL-1B, AL-4C, AL-5B
- Supabase CLI link state; staging deployed only from CI — AL-3A
- git worktrees and the working-tree diff — AL-3C, AL-6B
- Security register and decision log — AL-5C, AL-6C

## What that buys

Of 23 failures: 2 are prevented, 14 are detected, and 7 survive. 18 name a tool or an automated check; five are process only. Naming a mechanism is not installing it, and whether it is installed anywhere is not a fact this catalogue carries. Install state is an assessment fact — one environment, on a date — and lives in `../assessments/` (D-263).

Evidence status (D-107): 16 of the 23 are evidenced — a recorded incident or corpus-coded finding has landed on the row — and 7 are candidates, enumerated in advance and still waiting for their receipt. This register carries the highest evidenced share of the six, which follows from its construction: every row was read off a live security register in the first place.

## The seven that still reach you

- AL-1A — an inventory of what this machine can reach
- AL-1B — a standing limit enforced outside the agent's writable surface
- AL-2A — a credential scoped to the task, not to the person
- AL-3C — a lock between two sessions writing one repository
- AL-4C — a deny rule for a read-only pass, not a request for restraint
- AL-4D — an audit log the audited system cannot drop
- AL-6C — a way to tell a sanctioned change from a breach

Five are about limiting what the agent can reach before it acts. Two are about telling afterwards what it did — an audit log it cannot drop, and a sanctioned change from a breach.

*This section listed six until 2026-09-05, omitting AL-1B, which moved to `C survives` when its deny rule was recorded as living in a file the agent can edit. The published spoke was corrected on 2026-08-17 and this register was not — the same register/summary drift class as C-50, in the opposite direction. AL-1B and AL-4C share one fix: a deny rule beyond the writable surface.*

## Reading notes

Authority is a property of the mechanism, not of the grant. A rule the agent can edit changes how often a boundary is crossed, never what happens when it is. A settings file is bypassable; a server-side ruleset is not, and that is the only difference that survives contact with a session that wants past it.

Severity is cost multiplied by how silently it fails. It is a judgement, not a measurement. Every row is drawn from this project’s own security register — each one has either happened here once, or is a control gap recorded against it.

---

*False Floors is a trade mark of Digital First Pty Ltd, trading as Scale100 (AU application AMCZ-2616155657). This content is CC BY 4.0; the name is not part of that licence. Citing, mapping to, or claiming conformance with the catalogue needs no permission – see `LICENSE-CONTENT`.*

---
type: register
project: agent-trust-framework
layer: instruction
prefix: IL
title: Agent Instruction Layer — Did It Do What It Was Told
question: Did it do what it was told?
unit: a rule
figma-node: "1287:139"
figma-file: KDkIqr0lzbcAUvJLGAcExk
rows: 22
class-a: 2
class-b: 12
class-c: 8
class-a-reads: prevented
class-b-reads: detected
class-c-reads: survives
evidenced: 8
candidate: 14
verified: 2026-08-06 against this machine and the hullkey-charge repo (stream 78 run 1); built-state scope fixed to hullkey-charge by D-058 on 2026-08-09; Claude Code baseline behaviour for IL-2A and IL-2C verified against Anthropic documentation on 2026-08-10
residual-basis: derived from outcome x built state on 2026-08-09 (D-061); substitutes and partial closures entered by hand only where evidenced
date: 2026-08-07
last-updated: 2026-08-21
---

# Agent Instruction Layer: did it do what it was told

The life of a rule, stage by stage, and what happens at each stage when it is broken.

**This file is canon; the Figma frame `1287:139` is a generated view.** Shared vocabulary (severity, class, tier, built state, authority, catch points, triggers): [[README|registers README]].

Column key: **Evidence** — `evidenced` (at least one receipt: a first-party incident mapping, a corpus-coded finding, or a filed public case) or `candidate` (enumerated in advance, no receipt yet); headline counts count evidenced rows only (D-107, [[README|registers README]]) · Sev S1–S4 · Tool cell reads `name · runtime · tier · built state` · Outcome A / B / C – class grades how complete the remedy is ([[README|registers README]]); **this register reads B as *detected* and C as *survives*** · Next action carries its trigger in caps. **Residual** says what is actually true about the failure today, which is not the same as whether the named mechanism exists — see [[README|registers README]].

## Stage 1 · WRITTEN — does the rule exist in a followable form? (0 prevented · 5 detected · 1 survives)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome | Residual | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IL-1A | candidate | S3 | The rule set grew past what can be held | “Older rules quietly stopped being followed” | Budget the set; retire and merge rules | on disk | Size and token-budget lint on the rule file | Rule linter · any runtime · maintained · designed | B detected | open | MONTHLY — Review which rules stopped being followed |
| IL-1B | candidate | S2 | The rule only ever existed in chat | “We agreed this last week” | Standing rule file, loaded every session | stop | Stop hook scans the turn for new rules | Claude Code · Claude Code · automatic · designed | B detected | open | ONCE — Install the commitment-language stop hook |
| IL-1C | evidenced | S2 | Written as prose no machine can check | “Followed in spirit, breached in fact” | Restate the rule as a testable predicate | CI | Custom lint rule, run as a CI check | CI · any runtime · maintained · designed | B detected | open | AT EVERY RULE CHANGE — Write the lint rule when you write the rule |
| IL-1D | evidenced | S1 | Two rules conflict, nothing says which wins | “It picked one, plausibly, and you disagree” | Declare precedence inside the rule set | on disk | Precedence header in the rule set | none · any runtime · process · none | C survives | open | AT EVERY RULE CHANGE — Declare precedence when you add a rule |
| IL-1E | evidenced | S3 | Only half the decision was written down | “The record exists and still does not settle it” | Require every field before the record counts | on disk | Schema on the record, lint fails on a missing field | Schema lint · any runtime · maintained · designed | B detected | open | AT EVERY DECISION — Write the half that is in your head |
| IL-1F | candidate | S2 | The rule was superseded and still loads | “Follows a rule you retired months ago” | Generate the rule file from source; byte-diff so a hand edit cannot land | CI | Regenerate AGENTS.md and byte-diff it against the committed copy | CI · any runtime · automatic · built | B detected | partially closed | DONE · 5 AUG 2026 — Gate active; the exporter run stays manual |

## Stage 2 · LOADED — did the rule reach the agent at all? (0 prevented · 1 detected · 2 survive)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome | Residual | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IL-2A | candidate | S4 | The project-root rule file was never read this session | “Behaves as though the rule does not exist” | Built-in project instruction loading | session start | Claude Code loads project-root CLAUDE.md and unscoped rules | Claude Code · Claude Code · automatic · built | C survives | open | DONE · 10 AUG 2026 — Delivery is automatic; compliance is not enforced |
| IL-2B | evidenced | S3 | The rule sat in a scope that did not apply | “Followed in one folder, ignored in the next” | Scope rules deliberately and test the boundary | on disk | Directory-scoped rule files | Rule file · most runtimes · maintained · built | B detected | closed | AT EVERY RULE CHANGE — Decide where each rule should reach |
| IL-2C | candidate | S3 | Project-root rules were lost during compaction | “Complied early, drifted late” | Built-in re-injection after compaction | compact | Claude Code re-injects project-root CLAUDE.md and unscoped rules | Claude Code · Claude Code · automatic · built | C survives | open | DONE · 10 AUG 2026 — Re-injection is automatic; compliance is not enforced |

**IL-2A and IL-2C are baseline rows (D-077): they record vendor-supplied instruction delivery, not a security boundary or implementation work.** They count only project-root `CLAUDE.md` and unscoped rules. An adversarial or prompt-injected agent can still ignore delivered text; nested and path-scoped instructions also depend on a matching file being read after compaction. That residual working-set risk is recorded in [[context-layer|CL-2C]].

## Stage 3 · UNDERSTOOD — was it read as it was meant? (0 prevented · 0 detected · 2 survive)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome | Residual | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IL-3A | candidate | S3 | A prohibition was read as a preference | “Did it anyway, with a justification” — includes the narrower case where an example was read as the limit and only the named instance was fixed | Never/always wording, backed by a check; say whether an example is illustrative or exhaustive | CI | Grep gate finds weak wording, not the reading | CI · any runtime · maintained · designed | C survives | open | AT EVERY RULE CHANGE — Reserve hard language for what matters |
| IL-3C | candidate | S1 | The instruction was ambiguous | “Did something defensible you did not want” | Restate the task back before acting | prompt | Plan mode; spec-driven flow | Claude Code · Claude Code · maintained · built | C survives | open | EVERY TASK — Restate the task back before acting |

## Stage 4 · FOLLOWED — did it survive the moment of action? (2 prevented · 3 detected · 0 survive)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome | Residual | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IL-4A | evidenced | S4 | A clear rule simply was not followed | “No reason given, no flag raised” | Refuse the commit that breaks it | pre-commit | ESLint rule enforced pre-commit | ESLint · any runtime · maintained · designed | B detected | open | AT EVERY RULE CHANGE — Write the ESLint rule that blocks it |
| IL-4B | candidate | S3 | A trained default overrode the stated rule | “Reverted to the common convention” | Lint the specific default out, pre-commit | pre-commit | ESLint rule enforced pre-commit | ESLint · any runtime · maintained · designed | B detected | open | AT EVERY RULE CHANGE — Name the specific default to block |
| IL-4C | candidate | S3 | It acted before it had the state | “Confident change built on a wrong reading” | Require a read-and-confirm step first | pre-tool | PreToolUse gate refuses a write to an unread file | Claude Code · Claude Code · automatic · designed | A prevented | open | ONCE — Install the read-before-write gate |
| IL-4D | evidenced | S2 | It did more than was asked | “Extra files touched, unrequested refactor” | Declare scope, then diff touched files against it | pre-commit | Touched-file diff gate, scoped to the ticket | Lovelace · Claude Code · automatic · designed | B detected | open | ONCE — Install Lovelace ticket scope |
| IL-4E | evidenced | S4 | A gate existed but the action routed around it | “The guard never ran; it was PR-only” | Gate the boundary, not the happy path | pre-commit | Server-side branch protection refuses the push | Branch rules · any runtime · automatic · built | A prevented | closed | DONE · 26 JUL 2026 — Ruleset active, nobody can bypass |

## Stage 5 · HELD — did it stay followed to the end? (0 prevented · 1 detected · 2 survive)

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome | Residual | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IL-5A | candidate | S3 | Compliance decays over a long session | “First ten edits clean, last ten not” | Check at the end of the turn, not only the start | stop | Stop hook; session-check at end of turn | Lovelace · Claude Code · automatic · designed | B detected | open | ONCE — Install the Lovelace session-check |
| IL-5B | candidate | S3 | A subagent never received the rule | “Parent complies, children do not” | Rules travel inside every agent brief | subagent | CLAUDE.md hierarchy loads into every subagent | Claude Code · Claude Code · automatic · built | C survives | open | AT EVERY RULE CHANGE — Write rules to file, not auto memory |
| IL-5C | evidenced | S2 | A settled decision gets reopened | “Raises a thing you already ruled out” | Settled decisions become dated rules | CI | Link check proves the record reachable, not obeyed | Link check · any runtime · maintained · designed | C survives | open | AT EVERY DECISION — Write the decision down when you make it |

## Assurance · CHECKED — would you find out if it had not been? (0 prevented · 2 detected · 1 survives)

Not a sixth step. This band applies across stages 1 to 5 — each row asks whether the stage above would have told you.

| ID | Evidence | Sev | Failure | Shows up as | Prevention | Catch | Mechanism | Tool | Outcome | Residual | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IL-6A | candidate | S4 | The violation is invisible in the output | “Looks right, breaks a rule you cannot see” | A check per rule, or accept it is unenforced | on disk | Schema finds rules with no check, not violations | Schema lint · any runtime · maintained · designed | C survives | open | AT EVERY RULE CHANGE — Decide which rules are worth a check |
| IL-6B | candidate | S4 | It reports compliance it never verified | “Following your style guide”, with nothing run | Commit the check output, not the assurance | CI | CI artefact gates; byte-diff checks | CI · any runtime · automatic · built | B detected | closed | DONE · 31 JUL 2026 — Regenerate-and-byte-diff gates active in CI |
| IL-6C | candidate | S3 | Caught only when you happen to read it | “You found it; nothing else would have” | Promote the recurring ones into checks | CI | Checks promoted from repeat findings | CI · any runtime · maintained · built | B detected | closed | MONTHLY — Promote repeat findings into checks |

## Catch-point distribution

Before it starts 6 · before the change 3 · still in the session 3 · after the session 10.

| on disk | session start | prompt | pre-tool | subagent | post-tool | compact | stop | pre-commit | CI | review |
|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 1 | 1 | 1 | 1 | 0 | 1 | 2 | 4 | 6 | 0 |

Read left to right: how much has already happened by the time the failure is caught. The work is to move each row left — prevention lives only where the mechanism can refuse, and the earlier it refuses, the less has already been spent.

## The stack for this layer

- Rule files: CLAUDE.md, AGENTS.md, .cursorrules — IL-2A, IL-2B, IL-5B
- Built-in instruction loading and re-injection: Claude Code baseline — IL-2A, IL-2C
- Hooks: SessionStart, PreToolUse, Stop — IL-1B, IL-4C, IL-5A
- Rule-file linters: size, token budget, instruction rot — IL-1A
- Schema lints: required fields — IL-1E, IL-6A
- Pre-commit and push refusal: ESLint rules, server-side branch protection — IL-4A, IL-4B, IL-4E
- CI gates: grep gates, touched-file diff, byte-diff, promoted checks — IL-1C, IL-1F, IL-3A, IL-4D, IL-6B, IL-6C
- Records: decision log with link integrity — IL-5C
- Plan mode and spec-driven flow — IL-3C

## What that buys

Of 22 failures: 2 are prevented, 12 are detected, and 8 survive. 21 name a tool or an automated check; one is process only. Naming a mechanism is not installing it — 12 of the 21 are not built in `hullkey-charge` today. Automatic instruction loading and re-injection improve delivery but do not enforce compliance; only mechanisms that refuse the prohibited action count as prevention.

Evidence status (D-107): 8 of the 22 are evidenced — a recorded incident or corpus-coded finding has landed on the row — and 14 are candidates, enumerated in advance and still waiting for their receipt.

## The five that still reach you

- IL-1D — declared precedence between conflicting rules
- IL-3A — a check on the reading, not on the wording
- IL-3C — a judge for whether an instruction was ambiguous
- IL-5C — a check that a settled decision was honoured
- IL-6A — a check that fires on an invisible violation

Two need a judgement no check can make. Three more have a check that watches a proxy — the wording, the link, the declaration — never the failure.

## Reading notes

Failure class is a property of the mechanism, not of the rule. Re-stating, loading or re-injecting a rule changes how often it is broken, never what happens when an adversarial agent ignores it. IL-2A, IL-2C and IL-5B therefore remain useful delivery controls but are Class C, not security boundaries.

IL-1F closes only half its failure, and the half matters. The byte-diff proves AGENTS.md matches its committed inputs; it cannot prove those inputs match the live control plane, because CI cannot reach the vault. That second half is the exporter run (`control/tools/export_agents_projection.py`), a human-run receipt of the same shape as the Figma reconciliation. So the row reads `built` against its named mechanism while a stale *source* still reaches the agent unchallenged. Recorded rather than smoothed over, because it is the clearest live example of why closure is rarely binary — see the residual-field question in [[register-view-design-rationale]] section 4.

Severity is cost multiplied by how silently it fails. It is a judgement, not a measurement — the field frequencies cited elsewhere describe categories, not these rows. Lovelace touches two open rows here (IL-4D and IL-5A) and is installed on neither. It is a filing system whose validation covers schema and format only, so it supplies the record, not the refusal — both rows still need a hook or a CI gate on top of it. GitHub Projects touches no row at all; it is a provenance tool, not an instruction one.

## Retired rows

Retired IDs are never reused and never renumbered (row ID rule 1). Each retirement carries its reason and its date; the full audit behind the pass is [[../framework-reviews/2026-08-21-framework-review-02-row-provenance|framework review 02]] and the decision is D-106.

- `IL-3B` — *the example was read as the limit* — retired 2026-08-21, merged into `IL-3A`. Both rows recorded the same failure (the reading, not the wording), differed only in the instance shape, shared the same class, the same open residual and near-identical prevention, and IL-3B carried no mechanism and no recorded incident. IL-3A's symptom and prevention cells now carry the example-as-limit case explicitly.

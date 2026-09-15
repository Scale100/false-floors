# Trust-check v2

Trust-check shows which supported agent controls are configured in a repository, which supported patterns were not found, and which wired controls should be tested next. It gives teams a quick, evidence-backed starting point for improving agent safety without running repository code or producing a meaningless score.

## Install

Copy `tools/trust-check/` to `.claude/skills/trust-check/` or `.agents/skills/trust-check/` in the repository you want to assess. Then run:

```sh
python3 -B .claude/skills/trust-check/scripts/trust_check.py --repo "$(git rev-parse --show-toplevel)"
```

Use the matching `.agents/skills/` path if that is where your agent reads skills. Requires Python 3.10+ and Git.

## What you get

- A concise Markdown report with the three most useful improvements to make next.
- A complete JSON evidence record for maintainers and audit trails.
- A Stage 2 queue of wired controls that still need behavioral testing.

The scan is local, deterministic and bounded. A normal run writes only `false-floors-assessment.md` and `false-floors-assessment.json` in the assessed repository.

## Why we made it

Agent controls are easy to mistake for guarantees. A hook may exist but be disconnected; a policy may be present but bypassable; a convincing filename may contain no enforcement at all.

Trust-check separates what static inspection can establish from what still needs testing. It recognises supported Claude Code configurations, explains practical gaps in plain language, and preserves uncertainty instead of converting it into false confidence.

## How to read the result

- `present` means a supported mechanism was found installed or configured on the inspected surface.
- `absent` means a supported configuration pattern was not found there.
- `unknown` means the scanner could not make a supported claim.

These are configuration findings, not proof that a control works in practice. Nothing is certified or fully closed. Use the first three recommendations, rerun the scan, then request the next page with `--recommendations-page 2`.

## Coverage

The package contains calibrated detectors for 48 inspectable non-Class-C rows and 18 partial Class-C mechanisms. Seven additional Class-C rows require runtime or external evidence and remain draft. Unsupported custom implementations remain unknown rather than being guessed from names or comments.

Every wired control found by the structural control map is added to the Stage 2 testing queue. Stage 2 will determine whether it can be exercised automatically or needs a guided or CI-based test. The Stage 2 tool is due for release on 20 September.

## Privacy and network use

The default scan sends no repository data. It makes one bounded, unauthenticated request to the public False Floors release-tag feed to check catalogue freshness; `--offline` disables that request.

GitHub policy inspection is optional and requires explicit use of `--allow-github OWNER/REPO --github-branch BRANCH`. That mode sends the named repository, branch and CLI authentication to GitHub, but no local source files. Read [what this check sends](WHAT-THIS-CHECK-SENDS.md) before enabling it.

## Optional commands

| Command | Purpose |
|---|---|
| `--full` | Write the exhaustive maintainer report |
| `--rows IL-1A,RL-2A` | Explain up to twelve named rows |
| `--questions` | List optional questions that could change the next action |
| `--propose FILE` | Verify proposed bindings for unrecognised wired controls |
| `--confirm FILE` | Save owner-approved, verified bindings |
| `--install ROW` | Install and self-test a supported gate template |

Three installable templates currently exist: `RL-2C`, `CL-4B` and `IL-1A`.

## Technical detail

The original 6,500-word release documentation is preserved in [README-v2.0.0-full.md](README-v2.0.0-full.md). It covers detector behavior, manifests, recall testing, calibration, maintenance, budgets and failure modes.

## Per-entry calibration

“Active” means the installation detector passed known-good and known-bad fixture tests in its supported configuration mode. It does not certify real-world guard behavior. Draft entries make no positive claim.

<!-- calibration-table -->

| Row | Component / locator | Known-bad observed | Known-good observed | Status | Date |
|---|---|---|---|---|---|
| IL-1A | recognised Size and token-budget lint on the rule file; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| IL-1C | recognised Custom lint rule, run as a CI check; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| IL-1D | explicit field declaration only | Missing/disabled component: absent | Independent installed/configured fixture: present | active | 2026-09-11 |
| IL-1E | recognised Schema on the record, lint fails on a missing field; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| IL-1F | recognised Regenerate AGENTS.md and byte-diff the committed copy; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| IL-2A | project-local static inspection | No supported observable mechanism: unknown | Unavailable; no positive claim | draft | 2026-09-11 |
| IL-2B | scoped instruction file presence only | Missing/disabled component: absent | Independent installed/configured fixture: present | active | 2026-09-11 |
| IL-3A | recognised Grep gate finds weak wording, not the reading; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| IL-4A | recognised ESLint rule enforced pre-commit; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| IL-4B | recognised ESLint rule enforced pre-commit; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| IL-4C | recognised PreToolUse gate refuses a write to an unread file; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| IL-4D | recognised Touched-file diff gate, scoped to the ticket; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| IL-4E | effective GitHub branch policy; opt-in API only | Active bypass actor: absent | Independent installed/configured fixture: present | active | 2026-09-11 |
| IL-5B | project-local static inspection | No supported observable mechanism: unknown | Unavailable; no positive claim | draft | 2026-09-11 |
| IL-5C | recognised Link check proves the record reachable, not obeyed; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| IL-6A | recognised Schema finds rules with no check, not violations; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| IL-6B | recognised CI artefact gates; byte-diff checks; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| IL-6C | recognised Checks promoted from repeat findings; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| CL-1B | recognised Schema on the decision log fails on a missing why; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| CL-1C | recognised Path lint refuses a file filed off-taxonomy; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| CL-1D | explicit field declaration only | Missing/disabled component: absent | Independent installed/configured fixture: present | active | 2026-09-11 |
| CL-1E | recognised A curated note must name its raw source file; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| CL-1F | recognised Recorder writes the transcript; triage files it; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| CL-2A | recognised A prior read cannot bind a natural-language claim to evidence; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| CL-2B | recognised Naming changelog resolves every retired path; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| CL-3C | recognised CI diffs the register against the files it names; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| CL-3D | project-local static inspection | No supported observable mechanism: unknown | Unavailable; no positive claim | draft | 2026-09-11 |
| CL-4A | recognised Citation check on every generated document; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| CL-4B | recognised Banned-value grep gate, run pre-commit; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| CL-4D | scoped instruction file presence only | Missing/disabled component: absent | Independent installed/configured fixture: present | active | 2026-09-11 |
| CL-4E | explicit field declaration only | Missing/disabled component: absent | Independent installed/configured fixture: present | active | 2026-09-11 |
| CL-5A | recognised Schema requires an effective date and a review date; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| CL-5B | read-only mcp configuration audit | Disabled connector: absent | Independent installed/configured fixture: present | active | 2026-09-11 |
| CL-5C | recognised Archive folder excluded from the retrieval path; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| CL-6A | recognised Schema finds facts with no check, not wrong facts; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| AL-1A | project-local static inspection | No supported observable mechanism: unknown | Unavailable; no positive claim | draft | 2026-09-11 |
| AL-1B | local configuration declaration only | Missing/disabled component: absent | Independent installed/configured fixture: present | active | 2026-09-11 |
| AL-1C | recognised CI diffs the stated grant against the shipped one; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| AL-1D | recognised Lint fails a new function with no explicit revoke; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| AL-1E | recognised CI lists definer functions and their grantees; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| AL-1F | recognised A test writes the forged value and expects refusal; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| AL-2A | project-local static inspection | No supported observable mechanism: unknown | Unavailable; no positive claim | draft | 2026-09-11 |
| AL-2B | recognised A test asserts admin cannot reverse a one-way step; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| AL-2C | recognised The isolation matrix has a cell for every path; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| AL-3A | read-only local-unlinked configuration audit | Remote link metadata: absent | Independent installed/configured fixture: present | active | 2026-09-11 |
| AL-3B | effective GitHub branch policy; opt-in API only | Active bypass actor: absent | Independent installed/configured fixture: present | active | 2026-09-11 |
| AL-3C | project-local static inspection | No supported observable mechanism: unknown | Unavailable; no positive claim | draft | 2026-09-11 |
| AL-4A | effective GitHub branch policy; opt-in API only | Active bypass actor: absent | Independent installed/configured fixture: present | active | 2026-09-11 |
| AL-4B | recognised The guard reads the diff for policy and grant changes; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| AL-4C | local configuration declaration only | Missing/disabled component: absent | Independent installed/configured fixture: present | active | 2026-09-11 |
| AL-4E | effective GitHub branch policy; opt-in API only | Active bypass actor: absent | Independent installed/configured fixture: present | active | 2026-09-11 |
| AL-4F | project-local static inspection | No supported observable mechanism: unknown | Unavailable; no positive claim | draft | 2026-09-11 |
| AL-5A | recognised A test asserts the grant expires with the window; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| AL-5B | read-only subagent-tools configuration audit | Missing tool allowlist: absent | Independent installed/configured fixture: present | active | 2026-09-11 |
| AL-6A | recognised The guard pattern is replayed against real history; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| RL-1B | read-only git-tracked configuration audit | Untracked working file: absent | Independent installed/configured fixture: present | active | 2026-09-11 |
| RL-1C | recognised Snapshot or branch gate before migrate; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| RL-1D | explicit field declaration only | Missing/disabled component: absent | Independent installed/configured fixture: present | active | 2026-09-11 |
| RL-1E | recognised Worktrees separate paths but remain mutually reachable; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| RL-1F | project-local static inspection | No supported observable mechanism: unknown | Unavailable; no positive claim | draft | 2026-09-11 |
| RL-2A | local configuration declaration only | Missing/disabled component: absent | Independent installed/configured fixture: present | active | 2026-09-11 |
| RL-2C | recognised Deny pattern on destructive shell shapes when the tree is dirty; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| RL-2D | effective GitHub branch policy; opt-in API only | Active bypass actor: absent | Independent installed/configured fixture: present | active | 2026-09-11 |
| RL-3A | recognised Diff review gate on agent commits; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| RL-3B | recognised Regression test on the broken invariant; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| RL-3D | explicit field declaration only | Missing/disabled component: absent | Independent installed/configured fixture: present | active | 2026-09-11 |
| RL-4A | recognised Parent-count check before branching; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| RL-4B | effective GitHub branch policy; opt-in API only | Active bypass actor: absent | Independent installed/configured fixture: present | active | 2026-09-11 |
| RL-4C | recognised Migration refused without a down script; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| RL-4D | recognised Copy-and-verify gate in place of move; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| RL-4E | recognised Confirm gate on outbound and paid actions; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| RL-5A | recognised Paired code and data rollback plan; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| RL-5D | project-local static inspection | No supported observable mechanism: unknown | Unavailable; no positive claim | draft | 2026-09-11 |
| RL-6B | recognised Snapshot freshness check; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |
| RL-6C | recognised Named rollback authority, required field; connected configuration only | Disconnected: absent; disabled/missing/swallowing/stub: not present | Independent installed/configured fixture: present | active | 2026-09-11 |

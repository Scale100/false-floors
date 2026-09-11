# Trust-check v2 – Stage 1 configuration results and Stage 2 queue

This skill checks supported Claude Code installations and configuration against the pinned False Floors catalogue. Python performs detection and writes the reports; the model reads a compact summary. It runs from Claude Code or Codex, without an agent fan-out or target-code execution.

## Install

Copy `tools/trust-check/` into either `.claude/skills/trust-check/` or `.agents/skills/trust-check/` at the root of the repository you want to assess. Then run:

```sh
python3 -B .claude/skills/trust-check/scripts/trust_check.py --repo "$(git rev-parse --show-toplevel)"
```

Use the matching `.agents/skills/` path when that is where your agent reads skills. The scan writes `false-floors-assessment.json` and `false-floors-assessment.md` in the assessed repository.

Read [what this check sends](WHAT-THIS-CHECK-SENDS.md) before using the optional GitHub policy inspection mode.

## Version 2 presentation

The default terminal and Markdown reports are the public Stage 1 result. They show only static configuration findings the scanner established: supported components found and supported configuration patterns not found. The Markdown summary calls this configuration coverage, not check effectiveness. They do not display unresolved, judgement, draft-detector or unsupported catalogue rows as gaps, and they do not use an “ignored rows” headline.

Every wired repository control found by the structural control map is also counted as **identified for Stage 2 testing**. That is a plan to reach a behavioral result, not a claim that the control was tested. Stage 2 determines which candidates can be exercised automatically and which require a guided or CI-based test. The Stage 2 tool is due for release on 20 September.

Immediately after its four result bullets, the Markdown report gives `Summary` the same heading level as `Result` and `Recommended next steps`. It then turns the supported patterns not found into three practical improvements. Each improvement has a short name, a relatable example of the failure and its cause, one concrete `What to do` instruction, and `Read more` links to the relevant public register plus official tool documentation when a tool is named. Catalogue row codes remain provenance rather than the visible structure of the advice. Each supported component appears as its own compact bullet block, separated by one blank line, with status, scope, inspected location and evidence rendered on separate lines. The report tells the operator to implement the first three, rerun the check and then ask for the next three; if the failure later appears in practice, it gives them a copyable question for bringing the incident back into a session. `--recommendations-page N` returns three more without rewriting either assessment file. The complete ordered set remains in the JSON and `--full` maintainer report.

The JSON remains the complete evidence record, including every catalogue row and every unresolved reason. Maintainers can deliberately replace the default Markdown with that exhaustive view by running with `--full`; it is not the public report.

## Completed scope

All **48 non-Class-C inspectable rows** have calibrated detector entries. A further **18 Class C rows** have calibrated partial-mechanism checks. Seven Class C rows require runtime or external evidence: AL-1A, AL-2A, AL-3C, IL-2A, IL-5B, RL-1F and RL-5D. The 19 judgement rows and 36 residual rows remain in the evidence JSON; the residual bucket includes stop, compact, prompt and review positions as well as null catch points.

`present` means the supported mechanism was found installed/configured on the named surface. `absent` means the scanner established that a supported configuration pattern was not found on that surface; it is not labelled a missing control while unclassified controls remain. Neither result proves that the predicate is correct, the runtime obeys it, or every bypass is blocked. Non-Class-C present rows are `partially closed` on that limited configuration basis. Class C, absent, unresolved, self-reported-only and unhandled rows remain open. Nothing is fully closed by this scanner.

Supported guard entrypoints and source-shape terms are explicit in `assets/detectors.json`; this is a recogniser for supported configurations, not a universal interpreter for arbitrary guard programs. The scanner follows enabled workflow steps, effective Git pre-commit hook paths, synchronous Claude command hooks, npm/pnpm/yarn script indirection, a root assignment of the form `repo_root="$(git rev-parse --show-toplevel)"` with an optional `2>/dev/null || pwd` fallback, a backslash line continuation inside a workflow `run` block, and the aggregate-then-fail dispatcher (`fail=0`, only `guard || fail=1` lines, then `exit "$fail"` as the last line). That dispatcher is recognised exactly: an `exit 0`, a `|| true`, a missing or repeated initialiser, an unguarded line among the guards, a conditional, or an exit of a different variable each fall back to the ordinary rules and earn no credit. It checks that the referenced source is readable, recognises the row-specific guard shape and finds input-reading and rejection code. A filename, comment-only bait or pass-through stub does not qualify. Unknown custom implementations, conditional dispatchers, unsupported YAML features and indirect commands remain unknown. It never runs the candidate to resolve uncertainty.

Other detectors inspect scoped rule files, explicit process fields, permissions/sandbox declarations, subagent tool lists, connector declarations, the Git working set and local CLI link metadata. These observations are limited to the named project-local surface; they do not infer global or managed settings, runtime delivery, the correctness of scope or external recovery guarantees.

## Why a row is unknown

An unknown finding on a gate row says which of three things happened. If a candidate guard with a recognised name was connected, the reason names the file and says whether it was reached through a conditional, asynchronous, failure-swallowing or compound invocation, registered under a hook matcher that does not cover the tool, or missing the recognised source shape. If a surface could not be interpreted, the reason names the configuration file and the line that stopped the walk, for example a shell variable in command position in `.githooks/pre-commit` or a `$(...)` substitution in a `.claude/settings.json` hook command. If the surface was interpretable but only unrecognised files were connected, the reason lists those files and the entry names the recogniser accepts. Only read errors on configuration the connection graph actually touched count against a gate row; a read failure elsewhere in the tree no longer turns an absent gate row into unknown. If nothing else is connected and a workflow step uses a third-party GitHub Action, the reason names the action references and says an action step's behaviour is not inspected: an action's own code is never fetched or read, so a gate implemented that way is uncertain rather than missing. Steps using a well-known setup action (`actions/checkout`, `actions/setup-python`, `actions/setup-node`, `actions/cache`, `actions/upload-artifact`, `actions/download-artifact`) are exempt from that, matched on the owner and name before the `@`, so `actions/checkout-evil@v1` is not exempt. At most six action references are named.

Measured on this vault on 2026-09-09 before this change: 60 unknown rows, 46 of them carrying the same sentence with no pointer to a line. The pre-commit surface was stopped by the dispatcher's own `repo_root="$(git rev-parse --show-toplevel)"` assignment, the pre-tool and session-start surfaces by `$(...)` inside hook commands, and CI by a reusable-workflow job in `authority-scope.yml`. The vault's pre-commit dispatcher is the aggregate-then-fail shape above, which is why that idiom is now recognised. After the change the same 60 rows are still unknown on this vault, because its seven pre-commit checks and three hook scripts are not named in any detector entry and each carries control flow inside; what changed is that every one of those rows now names the file and line that stopped the walk and lists the connected files it did not recognise, at most one reason per file. In a fixture repository shaped like the vault's dispatcher with a recognised guard name, CL-4B moves from unknown to present. Recall against real repositories is still the open measurement; see the review that produced this section on PR #533.

Measured again on this vault on 2026-09-09, after CL-4A was allowed to score on the pre-commit surface as well as CI: 60 unknown, 11 absent and 2 present, where the same scan minutes earlier read 61 unknown, 11 absent and 1 present. CL-4A is the row that moved, on `tools/pre-commit-claim-sources.sh` reached through the dispatcher, and its evidence is the dispatcher's own invocation line. The action-step change moved nothing on this vault, because every `uses:` step in these workflows is a well-known setup action; it changes what a repository whose gate is a third-party action reads as, which was absent and is now unknown.

## The control map, the confirm loop, and the gate library

The scanner does not try to recognise a repository's gates by their filenames. It maps them by structure and a reading seat says what each is for.

**The map.** Every wired control gets an entry in `controlMap` in the record: where it is triggered, whether a failure of it would actually stop anything, what its source reads, the comment it opens with, the string literals it prints near a line that refuses, and its refusing lines. No filename vocabulary and no row terms are involved, and no entry carries a row. `boundTo` says whether anything has bound the control to a catalogue row yet, and `bindingSource` says on whose authority: `verified` when a detector recognised it without help, `confirmed` when the owner accepted a binding.

**The confirm loop.** The invoking agent reads the map entries with no binding and proposes one row each, evidence quoted verbatim. `--propose FILE` verifies each proposal and writes nothing at all: it re-establishes that the file is connected on one of the row's surfaces, that the invocation is synchronous and enabled rather than conditional or failure-swallowing, that the source reads an input, and that it has a path that refuses. The row's own term list is waived, because a binding is exactly the claim that this file implements the row under a name the recogniser does not know. `--confirm FILE` writes only what verification has just re-established, into `.false-floors.json`, with the date. The second run of a bound repository has nothing left to read, which is what makes it deterministic.

A seat proposes and never credits. That is the whole guardrail: independent readers can disagree about adjacent rows, so a proposed binding stays a proposal until its owner confirms it.

**Recall, measured rather than calibrated.** The table at the end of this file is the calibration receipt: every detector against its own fixtures. It is not a recall figure and must never be read as one, because a real repository does not name its guards after the catalogue.

The recall figure comes from real repositories and is scored against settled ground truth rather than one model's labels. On a 17-repository corpus with 129 gates enumerated by hand, 60 disputed labels settled by human rulings and 38 settled gates carrying a catalogue row, this version of the scanner with no manifest credits **1** and produces **0 false presents**, measured against catalogue FF-2026.3. The same figure held on FF-2026.2; it is re-measured on each release rather than carried forward, because a catalogue that gains rows can move it.

Against the earlier, unsettled labels the same scanner reported 2 present and 0 false presents. The settled figure is worse and it is the true one. Two things account for it, and neither is a failure to recognise a guard.

**A control may implement two rows, and one of them did.** `<your repo>/tools/pre-commit-claim-sources.sh` in the corpus refuses a number with no traceable source, or one that has drifted from the source it cites. Those are two different catalogue rows and the guard's own self-test exercises both. Forcing a single label on it made a true credit read as a false one, so a settled control may now carry one additional row, evidenced by a verbatim quotation from its own text and decided by a reader outside the session that wrote the rule. Eight of the eighteen contested controls carry one. Six such pairs of rows recur across this corpus and two careful readers split on one control in eight because of them, so the row boundaries remain a defect even though the scoring no longer punishes the scanner for it.

The second row is asymmetric on purpose: it stops a credit being counted as false, and it does not earn a recall credit. Recall stays on the primary row. A control found only under its second row is still a row the owner sees as open, and counting it as found would raise this figure by hiding that.

**The reach, not the recognition, is the ceiling. 18 of those 38 gates name a row this scanner can never credit**, because those rows' catch points sit outside the six surfaces a static scan inspects. The honest denominator is 20, not 38. Six of the eighteen are recoverable: four RL-3C gates and two IL-5A gates sit at catch point `stop`, a surface the command graph already walks, and they lack a detector only because `stop` is not in the inspectable set. The other twelve sit at `prompt`, at `review`, or at no catch point at all, and no amount of static inspection reaches them. A report should name those as beyond a static scan rather than as gaps you could close.

The confirmed-binding path is the other half and cannot be scored by a script, because confirmation is a person’s decision. In the same corpus, writing a reading seat’s proposals straight into a manifest produced **3 correct presents and 3 false presents**. Three false credits against a bar of zero is why the owner’s confirmation sits between a proposal and a credit rather than being offered as a convenience. Giving a reading seat each guard’s whole source halves its wrong bindings and does not raise recall.

**The gate library.** `--install ROW` writes a gate from the skill's own library, wires it to its surface, and runs that guard's `--self-test` against fixtures the guard carries. The receipt in `.false-floors.json` holds the guard's digest and what the self-test found, and a later scan repeats that result only while the digest still matches. Three rows have a template today, and a row without one is refused in plain words rather than skipped:

| Row | Guard | Surface | What it refuses |
|---|---|---|---|
| RL-2C | `<your repo>/tools/destructive-git-guard.py` | PreToolUse on Bash | a destructive shell command shape while the working tree is dirty |
| CL-4B | `<your repo>/tools/check-banned-values.py` | pre-commit | a commit that adds a value listed in `<your repo>/tools/banned-values.txt` |
| IL-1A | `<your repo>/tools/check-rule-budget.py` | pre-commit | a commit that pushes the agent rule set past its byte budget |

The installer (`.claude/skills/trust-check/scripts/install.py`) is its own gate: run it and it installs all three into throwaway repositories, runs each guard's self-test, checks the scanner sees the wiring as synchronous and enabled, tampers with each guard to prove the receipt stops speaking for it, and installs a deliberately silent guard to prove a zero exit is not accepted as a passing self-test. Five mutations of the installer were killed by it on 2026-09-09, and a sixth survived until the silent-guard fixture was added, which is why that fixture exists.

**The one place code runs.** A scan executes nothing belonging to the repository. The installer executes exactly one thing: the `--self-test` of a guard it has itself just written, with no arguments from the repository. That boundary is narrow deliberately, and the report states it.

## Repository manifest

A repository can name its own guards. `.false-floors.json` at the assessed repository root maps a catalogue row to the repository-relative paths that implement it, for example `{"gates": {"CL-4B": ["tools/pre-commit-ai-tells.sh"]}}`.

A declaration supplies two things for a `gate` row and no more: an accepted entry filename in addition to that row's own pattern, and a waiver of that row's term check. Everything else is still established by inspection. The named file must be connected on one of the row's listed surfaces through the same command graph, invoked synchronously and enabled, readable and inside the repository, and it must still show an input read and a rejection path. Where any of those fails, the outcome is what it would have been without the manifest and the reason says the file was declared.

A declaration never produces `present` for a row whose detector is not a gate, for a draft or unobservable detector, or for a Class C or judgement row. Those are recorded as declared and not creditable, with the reason, and the row stays where the detector left it. Top-level keys other than `gates` are ignored and noted, and an unknown row ID is noted and ignored. Invalid JSON, or a `gates` value that is not an object, leaves every gate row unknown with a reason naming the file, because the scanner cannot tell which bindings it is failing to read. Declaring one file for two rows is allowed and each row is then decided on its own evidence.

Every declaration appears in the report's manifest section with what happened to it: credited, declared but not connected, declared but not creditable, declared but unreadable, declared and not credited with the detector's reason, or not evaluated because the row was already credited to another file. The record's `readBudget` says whether the manifest was read, absent or unusable.

Why this exists. Measured on this vault on 2026-09-09, 45 of the 46 gate rows returned unknown while seven pre-commit checks and three Claude hook scripts were wired and running, because a gate detector accepts only the filenames written into its own `entry` pattern. Growing those lists cannot keep pace with how people name things, and a scanner that cannot see a real gate reports a gap that is not there. The repository supplies the row binding and the scanner verifies the rest.

## Lightweight operation

- Python 3.10+ and Git; a pinned pure-Python PyYAML parser is bundled with its MIT licence. No runtime installation, compilation, container or model call. Node is used only for build-time editorial parity checking.
- Shallow, bounded file inspection: 400 candidate paths per enumeration, 400 cached reads, 256 KiB per file and 4 MiB of target file content. The configured command graph is capped at 400 edges and five levels. A repository manifest contributes at most 40 declared rows and 60 declared paths to the same budget. Unsupported/deep configuration and unreadable input remain unknown.
- Two Git time budgets. Metadata calls (`rev-parse --show-toplevel`, `config --get core.hooksPath`, `remote get-url origin`) answer from the index and get four seconds. The working-set audit behind RL-1B – `git ls-files --others --directory --no-empty-directory --exclude-standard` – walks the entire working tree and gets thirty seconds; measured on a 160,000-file checkout it takes 2.2 to 2.5 seconds. On a very large repository expect that one command to dominate the scan's elapsed time. If it still runs out of time, RL-1B is `unknown` with the command and the limit named in its reason, the compact summary's `incompleteAudits` is non-empty, and the report gains an "Incomplete audits" section; an audit that did not finish is never reported as a smaller count. The first metadata call, `rev-parse --show-toplevel`, runs before anything is inspected: if it runs out of time the scan stops and names that command and its budget, rather than telling the operator the path is not a repository root, because a Git that never answered says nothing about the path. A wall-clock budget is not determinism. It is a bound set wide enough that exceeding it is an event worth naming rather than a routine outcome – before it was split in two, a shared four-second budget flapped between runs on that same checkout and moved the headline with nothing changed in the repository.
- The complete catalogue, editorial maps and reports stay on disk. Normal stdout is a summary; `--rows` projects only six fields for at most twelve requested IDs. No model needs to consume the catalogue, rewrite the report or read the full assessment JSON.
- Only the two assessment files are written by a normal run. No cache, lock, receipt, hook, setting, bytecode or workflow is written into the target. The developer calibration command is separate and writes package-maintenance artifacts only.
- Actual elapsed time and target bytes read appear in stdout. These are measurements of the particular scan, not a model token bill or a fixed runtime promise. Optional network calls are separately bounded.

## Network and freshness

The default scan sends no repository data. Its only request is an unauthenticated GET to the catalogue's existing [published release-tag feed](https://api.github.com/repos/Scale100/false-floors/tags?per_page=100). Only tags matching the catalogue version scheme participate. Numeric version ordering handles release 10 after release 9. No credentials, local repository name, branch, path or source content are sent with this fixed request. Redirects/proxies are disabled; the request has a three-second timeout and response-size/pagination caps. Offline mode makes no request. Failure explicitly retains the pinned catalogue.

This replaces the brief's public `registers/catalogue-releases.json` URL, which returned 404. The authoritative public repository already has version tags, so no publication or new service is needed. The package still retains the canonical release registry for historical resolution. A newer release produces an update notice; no catalogue or code is silently downloaded or executed.

GitHub repository-policy inspection is an **explicit opt-in exception** to the default local-only data boundary:

```sh
python3 -B /path/to/trust-check/scripts/trust_check.py --repo /path/to/repo --allow-github OWNER/REPO --github-branch BRANCH
```

This sends the specified repository identity and the GitHub CLI's authentication to GitHub, with no local source contents sent. The skill requires the operator's consent for that repository/branch before using the flag. It performs read-only queries for effective branch rules, legacy branch protection and at most five source rulesets; no more than seven requests, each with a five-second timeout. Missing permissions, omitted bypass fields, unsupported inherited sources and incomplete pagination remain unknown. Without the flag, the six server-policy detectors return unknown without contacting GitHub.

Both current rulesets and legacy branch protection are supported. The detector checks active enforcement, bypass actors, required checks, required reviewers and force-push settings as appropriate to the row. The deployment detector also requires a supported deployment workflow restricted to the inspected branch. Configuration observations do not involve a push or deployment. This follows GitHub's [effective branch-rule API](https://docs.github.com/en/rest/repos/rules#get-rules-for-a-branch). Claude connection recognition follows the [hooks reference](https://code.claude.com/docs/en/hooks); async hooks and the wrong event/matcher are not credited as synchronous gates.

A hosted assistant still receives its compact summary and any excerpts deliberately read into the conversation. The product's local-only statement applies to default scanner I/O, not to the entire hosted model interaction. Both output files state the actual network mode used.

## Source reuse and assessment contracts

The catalogue and canonical release registry are copied byte for byte. The original ten questions, twenty install groups and thirteen workflow actions are extracted unchanged from the web tool. Five optional question groups retain relevant nonjudgement rows outside the detector set; answers change the next action and remain self-reported. A detector's unknown result never silently becomes a question.

Upstream `check-assessment.py` and `diff-catalogue.py` are bundled unchanged. The runtime uses their pure functions rather than rebuilding their logic. Every emitted record contains the reference assessment's top-level keys, catalogueVersion, generatedFrom, row-keyed findings, installation state, next actions and explicit limitations. The canonical validator checks identity and consistency; it does not prove environmental truth.

The prior assessment is read before replacement. Identical recorded pins compare directly using the existing diff function. Other releases can be resolved through local history using `--source-root` for a trusted local public-repository clone. Missing historical commits are reported as unavailable. FF-2026.1's missing source commit is never reconstructed or silently treated as zero change. No Git history is fetched and no operator code is executed by the history resolver.

## Calibration and maintenance

The [validation script](scripts/validate.py) seeds isolated temporary Git repositories with HOME and Git configuration isolation. Fixtures in [fixture_cases.py](scripts/fixture_cases.py) are independent of the detector signature data. Each of the 66 active entries must refuse its known-bad installation and admit its known-good installation. All 46 connected-guard detectors also refuse disabled, missing, swallowed-failure and pass-through configurations. No fixture grants closure to an operator control; it tests whether the detector recognises installation correctly.

The repository manifest has its own directions: a declared guard the entry pattern does not name becomes present on a vault-shaped dispatcher, and a declaration is refused when the file is not connected, is a pass-through stub, is reached through `|| true` or a conditional, is a symlink, or sits outside the repository. Invalid JSON and a non-object `gates` leave every gate row unknown, a Class C row, a draft detector and a non-gate detector take no credit, an unknown row ID is ignored, and every one of those appears in the report. Each of those checks was run against a deliberately broken build of the feature before it was relied on.

Additional tests cover the vault-shaped pre-commit dispatcher scoring the citation row on that surface, and refusing the same hook once its failure is swallowed; third-party action steps reading as unknown while the setup-action allowlist reads as absent, with the allowlist matched exactly on owner and name; YAML comments, duplicate keys, aliases and custom tags; npm indirection and cycles; hook event/matcher/async behavior; local overrides; untracked files; disabled settings; inherited and legacy GitHub policy; missing API fields and bypasses; branch-restricted deployments; exact output file set; all-row rendering; unknown/Class C gap handling; optional self-report; selective projection; output symlink/hardlink safety; prior-report preservation; stale calibration; source integrity; freshness success/newer/offline/failure; and upstream self-tests.

Calibration hashes cover the runner, detectors, tests, independent fixtures, signatures, catalogue and every bundled parser module. Missing or stale calibration demotes active detectors to unknown/draft. Maintainers should validate a candidate package in an isolated repository before publishing a changed integrity lock or calibration receipt.

## Corrections to the original brief

The four counts reproduce, but a catch-point label is a detection location rather than a guarantee of arbitrary program semantics. This implementation recognises supported configured mechanisms and keeps behavioral effectiveness separate. The initial partial implementation incorrectly required the latter before finishing the former; that implementation gap is now closed.

The residual bucket is not exclusively null catch points. The requested public JSON URL does not exist; the existing release tags supply freshness. The brief's consented `gh api` allowance conflicts with its unconditional no-repository-data claim; default mode preserves that claim and the explicit opt-in reports its narrower privacy boundary. The assessment CLI has no arbitrary-path option, so its existing audit function is reused. The diff CLI requires a source version and local historical snapshots. Severity order is the catalogue's exposure order, not a score or ranking of repositories. The 10 August runtime-default reading is dated and receives no present-day credit.

## Operational limit

Do not run concurrent assessments of the same target. Both payloads are generated and validated before either destination opens, but the two writes are not an atomic filesystem transaction. A disk failure after the first write can leave mixed generations. The two-file-only contract is preserved; no hidden temporary output or lock is created.

## Per-entry calibration

“Active” below means the installation detector passed both calibration directions in its supported configuration mode. It never certifies the operator's guard behavior. The seven draft entries have no supported positive observation and never grade.

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

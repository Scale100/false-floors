# False Floors trust check

## What it is for

Trust-check gives you a grounded starting point for improving the controls around coding agents. It looks at a supported set of Claude Code and Codex configuration surfaces, identifies mechanisms it can establish are installed, and flags supported patterns it could not find. The aim is not a score, badge or verdict that a repository is safe. It is a practical answer to a narrower question: which checks, rules and guardrails are visibly configured here, and what should we look at next? It turns the False Floors catalogue into a short, repository-specific action list without asking a model to read your whole codebase. You can use it before deciding what to build, tighten or test next.

## How it works

The scanner maps configured controls by their structure rather than trusting filenames or comments. It reads the relevant local configuration, follows supported command and hook connections, and records where a mechanism is wired, missing, or cannot be interpreted safely. It does not run code belonging to the repository being assessed. Its default report gives three next improvements in plain language; the accompanying JSON retains the evidence and any uncertainty for maintainers. Controls that are connected but need behavioural proof are placed in a Stage 2 testing queue. An installed hook is evidence of configuration, not proof that it catches every real failure. Unsupported custom patterns stay explicit rather than being guessed into coverage.

## How to read the result

`present` means the scanner found a supported mechanism installed or configured on the named surface. `absent` means it established that a supported configuration pattern was not found there. `unknown` means the scanner could not make a supported claim — for example, because a custom implementation or connection falls outside the patterns it can safely interpret. None of these findings certify runtime behaviour, close every pathway around a control, or prove the correctness of your agent’s output. They are evidence-bound observations, not a replacement for review or testing. Start with the first three recommended improvements, rerun the check, then request the next page when you are ready.

## Install and run

Copy `tools/trust-check/` into `.claude/skills/trust-check/` or `.agents/skills/trust-check/` at the repository root, then run:

```sh
python3 -B .claude/skills/trust-check/scripts/trust_check.py --repo "$(git rev-parse --show-toplevel)"
```

The check requires Python 3.10+ and Git and writes `false-floors-assessment.md` plus `false-floors-assessment.json` in that repository. A normal run makes no repository-code execution and no model call. Read [what the check sends](WHAT-THIS-CHECK-SENDS.md) before enabling optional GitHub policy inspection. The complete technical description, detector scope, calibration, limitations, control-map workflow and Stage 2 queue remain in [the long-format guide](README-long.md).

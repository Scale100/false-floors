# False Floors trust check

Find the supported agent controls configured in a repository, then get the next practical improvements to make. This is a **configuration check**: it identifies what is installed or absent; it does not certify that a control works at runtime.

## Start here

Copy `tools/trust-check/` into `.claude/skills/trust-check/` or `.agents/skills/trust-check/` at the repository root, then run:

```sh
python3 -B .claude/skills/trust-check/scripts/trust_check.py --repo "$(git rev-parse --show-toplevel)"
```

The check writes `false-floors-assessment.md` and `false-floors-assessment.json` in that repository. Read [what the check sends](WHAT-THIS-CHECK-SENDS.md) before enabling optional GitHub policy inspection.

## Want the full method?

The complete technical description, detector scope, calibration, limitations, control-map workflow and Stage 2 queue are preserved in [the long-format guide](README-long.md).

This version runs locally with Python 3.10+ and Git. It does not execute target-repository code.

"""Independent installation fixtures, keyed by catalogue ID (not generated from signatures).

Guards here are tiny executable test inputs. Calibration tests their connection
and recognition, not the effectiveness of the operator's implementation.
"""
import json
from pathlib import Path
import subprocess

GUARDS = {
    "IL-1A": ("check-rule-budget.py", "token budget limit"),
    "IL-1C": ("check-rules.py", "rule lint violation"),
    "IL-1E": ("check-decision-schema.py", "decision rationale constraints"),
    "IL-1F": ("check-generated-agents.py", "AGENTS.md generated diff"),
    "IL-3A": ("check-weak-wording.py", "must weak should"),
    "IL-4A": ("check-eslint-rules.py", "eslint rule violation"),
    "IL-4B": ("check-banned-defaults.py", "default banned violation"),
    "IL-4C": ("read-before-write.py", "read write unread"),
    "IL-4D": ("check-ticket-scope.py", "scope ticket touched"),
    "IL-5C": ("check-settled-topics.py", "settled decision reachable link"),
    "IL-6A": ("check-rule-coverage.py", "rule check missing"),
    "IL-6B": ("check-committed-evidence.py", "evidence artifact committed diff"),
    "IL-6C": ("check-repeat-findings.py", "repeat control check"),
    "CL-1B": ("check-decision-rationale.py", "rationale required missing"),
    "CL-1C": ("check-path-taxonomy.py", "path taxonomy"),
    "CL-1E": ("check-raw-sources.py", "raw-file exists missing"),
    "CL-1F": ("capture-transcripts.py", "transcript record capture"),
    "CL-2A": ("read-before-claim.py", "read claim citation"),
    "CL-2B": ("check-naming-aliases.py", "alias retired path target"),
    "CL-3C": ("check-register-artifacts.py", "register artifact file diff"),
    "CL-4A": ("check-citations.py", "citation source claim document"),
    "CL-4B": ("check-banned-values.py", "banned forbidden value default"),
    "CL-5A": ("check-fact-dates.py", "effective checked review expiry"),
    "CL-5C": ("check-archive-exclusion.py", "archive exclude retrieval"),
    "CL-6A": ("check-fact-coverage.py", "fact claim check missing"),
    "AL-1C": ("check-grant-diff.py", "grant comment stated diff"),
    "AL-1D": ("check-function-revokes.py", "function revoke"),
    "AL-1E": ("check-definer-grantees.py", "definer grantee grant"),
    "AL-1F": ("check-forged-fields.py", "column field forged refusal"),
    "AL-2B": ("check-admin-transitions.py", "admin reverse transition"),
    "AL-2C": ("check-tenant-matrix.py", "tenant matrix isolation"),
    "AL-4B": ("check-policy-diff.py", "policy grant diff"),
    "AL-5A": ("check-grant-expiry.py", "grant expiry window"),
    "AL-6A": ("check-guard-replay.py", "known-bad replay guard control"),
    "RL-1C": ("check-migration-snapshot.py", "snapshot backup migration"),
    "RL-1E": ("check-worktree-isolation.py", "worktree writer agent"),
    "RL-2C": ("destructive-git-guard.py", "dirty reset clean destructive"),
    "RL-3A": ("check-diff-review.py", "diff review approval"),
    "RL-3B": ("check-regressions.py", "regression invariant test"),
    "RL-4A": ("check-branch-reuse.py", "branch squash parent cherry"),
    "RL-4C": ("check-down-migrations.py", "migration down rollback"),
    "RL-4D": ("check-copy-verify.py", "copy verify checksum"),
    "RL-4E": ("confirm-outbound.py", "confirm outbound payment external"),
    "RL-5A": ("check-paired-rollback.py", "rollback code data"),
    "RL-6B": ("check-snapshot-age.py", "snapshot backup age freshness"),
    "RL-6C": ("check-rollback-authority.py", "rollback authority owner"),
}

SURFACES = {
    "IL-4A": "pre-commit", "IL-4B": "pre-commit", "IL-4D": "pre-commit",
    "CL-1C": "pre-commit", "CL-4B": "pre-commit", "AL-1D": "pre-commit",
    "RL-3A": "pre-commit", "RL-4C": "pre-commit",
    "IL-4C": "pre-tool", "CL-2A": "pre-tool", "RL-1C": "pre-tool",
    "RL-1E": "pre-tool", "RL-2C": "pre-tool", "RL-4D": "pre-tool", "RL-4E": "pre-tool",
}

FIELDS = {"IL-1D": "precedence", "CL-1D": "supersedes", "CL-4E": "verification-status", "RL-1D": "restore-scope", "RL-3D": "incremental-write"}


def write(root, path, text):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
    return target


def guard_source(rid):
    fields = GUARDS[rid][1].split()
    return "import json, sys\nfrom pathlib import Path\nrequired = " + repr(fields) + "\ndata = json.loads(Path('control-input.json').read_text())\nif any(field not in data for field in required):\n    sys.exit(1)\n"


def connect(root, rid, mode="good"):
    name, _ = GUARDS[rid]
    target = "scripts/" + name
    write(root, target, guard_source(rid) if mode != "stub" else "# " + GUARDS[rid][1] + "\nprint('pass')\n")
    command = "python3 " + target
    surface = SURFACES.get(rid, "CI")
    if surface == "CI":
        job = {"runs-on": "ubuntu-latest", "steps": [{"run": command}]}
        if mode == "disabled":
            job["if"] = "false"
        if mode == "swallow":
            job["steps"][0]["continue-on-error"] = True
        doc = {"on": {"pull_request": {}}, "jobs": {"check": job}}
        write(root, ".github/workflows/check.yml", json.dumps(doc))
    elif surface == "pre-commit":
        hook = write(root, ".githooks/pre-commit", "#!/bin/sh\nset -e\n" + command + (" || true" if mode == "swallow" else "") + "\n")
        hook.chmod(0o644 if mode == "disabled" else 0o755)
        subprocess.run(["git", "-C", str(root), "config", "core.hooksPath", ".githooks"], check=True)
    else:
        handler = {"type": "command", "command": command}
        if mode == "swallow":
            handler["async"] = True
        doc = {"hooks": {"PreToolUse": [{"matcher": "Write|Edit" if rid == "IL-4C" else "Bash", "hooks": [handler]}]}}
        if mode == "disabled":
            doc["disableAllHooks"] = True
        write(root, ".claude/settings.json", json.dumps(doc))
    if mode == "disconnected":
        if surface == "CI":
            (root / ".github/workflows/check.yml").unlink()
        elif surface == "pre-commit":
            subprocess.run(["git", "-C", str(root), "config", "core.hooksPath", ".unused"], check=True)
        else:
            (root / ".claude/settings.json").unlink()
    if mode == "missing":
        (root / target).unlink()
    return target


DECLARED_GUARD = "tools/my-banned-words.sh"

# A guard named the way a repository names things, matching no detector entry pattern
# and carrying none of a row's terms. It reads its input and it refuses.
DECLARED_SOURCE = ('#!/usr/bin/env bash\nset -uo pipefail\n'
                   'staged=$(git diff --cached --name-only)\n'
                   'printf "%s" "$staged" | grep -q myword && exit 1\n'
                   'exit 0\n')
DECLARED_STUB = '#!/usr/bin/env bash\necho "no input is read and nothing is refused"\n'


def dispatcher(root, guards, joiner=" || fail=1"):
    """The vault-shaped aggregate-then-fail pre-commit dispatcher."""
    body = ('#!/usr/bin/env bash\nset -uo pipefail\nrepo_root="$(git rev-parse --show-toplevel)"\nfail=0\n'
            + "".join('bash "${repo_root}/' + g + '"' + joiner + "\n" for g in guards) + 'exit "$fail"\n')
    hook = write(root, ".githooks/pre-commit", body)
    hook.chmod(0o755)
    subprocess.run(["git", "-C", str(root), "config", "core.hooksPath", ".githooks"], check=True)
    return hook


def manifest(root, gates, extra=None):
    return write(root, ".false-floors.json", json.dumps({**(extra or {}), "gates": gates}))


def policy(good=True):
    rules = [{"type": "pull_request", "parameters": {"required_approving_review_count": 1}},
             {"type": "required_status_checks", "parameters": {"required_status_checks": [{"context": "test"}]}},
             {"type": "non_fast_forward"}]
    for rule in rules:
        rule.update(ruleset_id=42, ruleset_source_type="Repository", ruleset_source="fixture/repo")
    return {"repo": "fixture/repo", "branch": "main", "effective": {"ok": True, "data": rules, "how": "fixture API /rules/branches/main"},
            "legacy": {"ok": True, "data": {"enforce_admins": {"enabled": False}}, "how": "fixture API /protection"},
            "details": {42: {"ok": True, "data": {"enforcement": "active", "bypass_actors": [] if good else [{"actor_type": "RepositoryRole", "actor_id": 5}]}}}}


def deploy(root):
    write(root, "scripts/deploy.py", "print('fixture deployment entrypoint; never executed')\n")
    write(root, ".github/workflows/deploy.yml", json.dumps({"on": {"push": {"branches": ["main"]}}, "jobs": {"deploy": {"runs-on": "ubuntu-latest", "steps": [{"run": "python3 scripts/deploy.py"}]}}}))


def local(root, rid, good=True):
    if rid in GUARDS:
        return connect(root, rid, "good" if good else "disconnected")
    if rid in ("IL-2B", "CL-4D"):
        if good:
            return write(root, ".claude/rules/source.md", "Read current source before editing.\n")
    elif rid in FIELDS:
        key = FIELDS[rid]
        if good:
            return write(root, ".claude/agents/worker.md" if rid == "RL-3D" else "CLAUDE.md", "---\n" + key + ": " + ("true" if rid == "RL-3D" else "declared value") + "\n---\n")
    elif rid in ("AL-1B", "AL-4C"):
        return write(root, ".claude/settings.json", json.dumps({"permissions": {"deny": ["Edit(prod/**)"] if good else []}}))
    elif rid == "RL-2A":
        return write(root, ".claude/settings.json", json.dumps({"sandbox": {"enabled": good}}))
    elif rid == "RL-1B":
        write(root, "work.txt", "source\n")
        if good:
            subprocess.run(["git", "-C", str(root), "add", "work.txt"], check=True)
    elif rid == "AL-3A":
        write(root, "supabase/config.toml", 'project_id = "fixture"\n')
        if not good:
            write(root, "supabase/.temp/project-ref", "remote-project\n")
    elif rid == "AL-5B":
        return write(root, ".claude/agents/reviewer.md", "---\nname: reviewer\n" + ("tools: Read, Grep\n" if good else "") + "---\nReview the source.\n")
    elif rid == "CL-5B":
        return write(root, ".mcp.json", json.dumps({"mcpServers": {"fixture": {"command": "fixture-connector", "disabled": not good}}}))

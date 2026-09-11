#!/usr/bin/env python3
"""The gate library: install one gate for one catalogue row, together with its known-bad self-test.

An installed control is not a working one. That sentence is the framework, so this module
never reports an installation on its own: it writes the guard, wires it to its surface, runs
the guard's own `--self-test` against fixtures the guard carries, and records the result with
the guard's digest. A later scan re-checks the digest and reports what the self-test found,
never that a file exists.

**The one place this tool runs code.** The scanner never executes anything belonging to the
target repository. The installer executes exactly one thing: the `--self-test` of a guard it
has itself just written from the library below, in the repository root, with no arguments
from the repository. Nothing in the target chooses what runs, and no target script is
invoked. That boundary is narrow on purpose and is stated in the report.

The library is small and says so. Forty-six catalogue rows have a gate detector; three have
an installable gate here, because a portable gate has to work in a repository nobody has
seen, and most rows need something only the owner knows. A row with no template is reported
as having no installable gate, which is the truth, rather than being quietly skipped.

  install.py --self-test      installs all three into throwaway repositories and checks them
"""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

TOOLS_DIR = "tools"
HOOKS_DIR = ".githooks"
SETTINGS = ".claude/settings.json"
SELF_TEST_TIMEOUT = 30


DESTRUCTIVE_GUARD = r'''#!/usr/bin/env python3
"""destructive-git-guard - refuse a destructive shell command while the working tree is dirty.

Installed by False Floors trust-check for RL-2C, "a destructive command ran before you saw
it". The catalogue's prevention is "refuse the command shape, not the intent", and that is
what this does: it matches the shape of the command, makes no attempt to guess whether the
command was reasonable, and refuses only while there is uncommitted work the command would
destroy. A clean tree is not blocked, because there is nothing to lose.

Wired as a Claude Code PreToolUse hook on Bash. It reads the hook payload on stdin, and exits
2 to refuse, which is how a PreToolUse hook blocks a tool call.

Run `--self-test` before trusting it. The fixtures are in this file.
"""
import json
import re
import subprocess
import sys

# Command shapes that destroy uncommitted work. Each is the shape, not an intent.
DESTRUCTIVE = (
    (r"\bgit\s+reset\s+--hard\b", "git reset --hard discards every uncommitted change in the tree"),
    (r"\bgit\s+clean\s+-[a-z]*[fd]", "git clean removes untracked files and there is no way back"),
    (r"\bgit\s+checkout\s+--\s", "git checkout -- <path> overwrites that path from the index"),
    (r"\bgit\s+stash\s+(?:pop|drop|clear)\b", "the stash stack is shared; popping or dropping can take another session's work"),
    (r"\bgit\s+push\s+.*--force(?!-with-lease)", "a plain force push overwrites whatever is on the remote"),
    (r"\brm\s+-[a-z]*r[a-z]*f|\brm\s+-[a-z]*f[a-z]*r", "rm -rf deletes a tree and there is no way back"),
)


def tree_is_dirty(cwd=None, run=subprocess.run):
    """True when there is uncommitted work to lose. An unavailable answer counts as dirty."""
    try:
        p = run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=cwd, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return True
    if p.returncode != 0:
        return True
    return bool(p.stdout.strip())


def judge(command, dirty):
    for pattern, why in DESTRUCTIVE:
        if re.search(pattern, command):
            if not dirty:
                return None
            return why
    return None


def main(argv, stdin, dirty_check=tree_is_dirty):
    if "--self-test" in argv:
        return self_test()
    try:
        payload = json.load(stdin)
    except ValueError:
        print("destructive-git-guard: the hook payload was not JSON; refusing rather than guessing", file=sys.stderr)
        return 2
    if not isinstance(payload, dict):
        return 2
    command = ((payload.get("tool_input") or {}).get("command") or "")
    if not isinstance(command, str) or not command.strip():
        return 0
    why = judge(command, dirty_check())
    if why is None:
        return 0
    print("BLOCKED by destructive-git-guard (False Floors RL-2C).\n"
          "  " + why + "\n"
          "  The working tree is dirty, so this would destroy work that is not committed.\n"
          "  Commit or tag the current state first, then run it again.", file=sys.stderr)
    return 2


def self_test():
    """Every known-bad must be refused on a dirty tree and allowed on a clean one."""
    bad = ["git reset --hard origin/main", "git clean -fd", "git clean -xfd",
           "cd /tmp && rm -rf build", "git push --force origin main",
           "git stash pop", "git checkout -- src/app.py"]
    good = ["git status", "git commit -m 'x'", "git push --force-with-lease origin main",
            "rm -f one-file.txt", "git stash push -u -m keep", "npm test", ""]
    problems = []
    for command in bad:
        if judge(command, True) is None:
            problems.append("known-bad not refused on a dirty tree: " + command)
        if judge(command, False) is not None:
            problems.append("refused on a clean tree, where there is nothing to lose: " + command)
    for command in good:
        if judge(command, True) is not None:
            problems.append("known-good refused: " + command)
    # A payload that is not a command must not be refused, and one that is unreadable must be.
    class Fake:
        def __init__(self, text): self.text = text
        def read(self): return self.text
    if main([], Fake('{"tool_input": {"command": "git status"}}'), lambda: True) != 0:
        problems.append("a harmless command was refused end to end")
    if main([], Fake('not json'), lambda: True) != 2:
        problems.append("an unreadable payload was allowed through")
    if main([], Fake('{"tool_input": {"command": "git clean -fd"}}'), lambda: True) != 2:
        problems.append("a known-bad was allowed through end to end")
    for p in problems:
        print("SELF-TEST FAIL: " + p, file=sys.stderr)
    print("destructive-git-guard self-test: " + ("PASS, " + str(len(bad)) + " known-bad refused and "
          + str(len(good)) + " known-good allowed" if not problems else "FAIL"))
    return 1 if problems else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(self_test())
    raise SystemExit(main(sys.argv[1:], sys.stdin))
'''


BANNED_VALUES_GUARD = r'''#!/usr/bin/env python3
"""check-banned-values - refuse a commit that adds a value this project has banned.

Installed by False Floors trust-check for CL-4B, "a trained default overrode the retrieved
fact". The catalogue's prevention is "name the specific wrong value to block", so this gate
is deliberately a list you fill in rather than a cleverness: it reads tools/banned-values.txt
and refuses a commit whose staged diff ADDS a line containing any banned value.

Only added lines are checked. A banned value already in the repository is not this gate's
business, and a gate that failed on existing content would be turned off within a day.

The list starts empty, and an empty list is reported rather than passing silently: a gate
with nothing to check is not protecting anything, and saying so is the point of the tool that
installed it.

Run `--self-test` before trusting it. The fixtures are in this file.
"""
import re
import subprocess
import sys
from pathlib import Path

LIST = "tools/banned-values.txt"
MAX_REPORT = 20


def banned(text):
    """Each line is a banned value, optionally a tab and why it is banned. `#` is a comment."""
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        value, _, why = line.partition("\t")
        value = value.strip()
        if value:
            out.append((value, why.strip() or "no reason recorded"))
    return out


def added_lines(diff):
    """The lines a diff adds, with the file each belongs to."""
    out, path = [], "?"
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]
        elif line.startswith("+") and not line.startswith("+++"):
            out.append((path, line[1:]))
    return out


def offences(diff, values):
    found = []
    for path, line in added_lines(diff):
        for value, why in values:
            if value in line:
                found.append((path, value, why, line.strip()[:120]))
    return found


def staged_diff(run=subprocess.run):
    p = run(["git", "diff", "--cached", "--unified=0"], capture_output=True, text=True, timeout=30)
    if p.returncode != 0:
        return None
    return p.stdout


def main(root=Path(".")):
    list_path = root / LIST
    if not list_path.is_file():
        print("check-banned-values: " + LIST + " is missing, so this gate is checking nothing.", file=sys.stderr)
        return 1
    values = banned(list_path.read_text(encoding="utf-8"))
    if not values:
        print("check-banned-values: " + LIST + " is empty, so this gate is checking nothing.\n"
              "  Add one banned value per line, optionally a tab and why it is banned.\n"
              "  A gate with an empty list is not protecting you and should not read as if it is.", file=sys.stderr)
        return 1
    diff = staged_diff()
    if diff is None:
        print("check-banned-values: the staged diff could not be read; refusing rather than passing.", file=sys.stderr)
        return 1
    found = offences(diff, values)
    if not found:
        return 0
    print("BLOCKED by check-banned-values (False Floors CL-4B): " + str(len(found))
          + " banned value(s) added.", file=sys.stderr)
    for path, value, why, line in found[:MAX_REPORT]:
        print("  " + path + ": added `" + value + "` - " + why + "\n      " + line, file=sys.stderr)
    if len(found) > MAX_REPORT:
        print("  + " + str(len(found) - MAX_REPORT) + " more.", file=sys.stderr)
    return 1


def self_test():
    values = banned("localhost:5432\tthe staging database, never the production one\n# a comment\n\nAdmin123\ta default password\n")
    problems = []
    if [v for v, _ in values] != ["localhost:5432", "Admin123"]:
        problems.append("the list parser kept a comment or a blank line: " + repr(values))
    bad = "--- a/app.py\n+++ b/app.py\n+DB = \"localhost:5432\"\n"
    good = "--- a/app.py\n+++ b/app.py\n+DB = os.environ[\"DB_URL\"]\n"
    context = "--- a/app.py\n+++ b/app.py\n-DB = \"localhost:5432\"\n DB = \"localhost:5432\"\n"
    if not offences(bad, values):
        problems.append("known-bad diff not refused")
    if offences(good, values):
        problems.append("known-good diff refused")
    if offences(context, values):
        problems.append("a removed or unchanged line was treated as added, which would fail on existing content")
    if not offences("--- a/x\n+++ b/x\n+password = Admin123\n", values):
        problems.append("a banned value inside a longer added line was missed")
    for p in problems:
        print("SELF-TEST FAIL: " + p, file=sys.stderr)
    print("check-banned-values self-test: " + ("PASS, known-bad refused and known-good and existing content allowed"
          if not problems else "FAIL"))
    return 1 if problems else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(self_test())
    raise SystemExit(main())
'''


RULE_BUDGET_GUARD = r'''#!/usr/bin/env python3
"""check-rule-budget - refuse a commit that pushes the agent rule set past its budget.

Installed by False Floors trust-check for IL-1A, "the rule set grew past what can be held".
The catalogue's prevention is "budget the set; retire and merge rules", and a budget is only a
budget if something refuses when it is exceeded. This counts the bytes of every agent
instruction file it can find and refuses when the total passes the limit below.

The limit is a starting point, not a finding: raise or lower it deliberately, in this file,
where the change is visible in a diff. A number nobody chose is the failure this row is about.

Run `--self-test` before trusting it. The fixtures are in this file.
"""
import sys
from pathlib import Path

# The maximum total size of the agent rule set, in bytes. Chosen, not derived: about 24,000
# bytes is roughly six thousand tokens, which is a set a person can still read in one sitting.
MAX_BYTES = 24000
RULE_FILES = ("CLAUDE.md", "AGENTS.md", ".claude/CLAUDE.md", ".cursor/rules", ".github/copilot-instructions.md")


def rule_paths(root):
    found = []
    for name in RULE_FILES:
        p = root / name
        if p.is_file():
            found.append(p)
        elif p.is_dir():
            found.extend(sorted(x for x in p.rglob("*.md") if x.is_file()))
    return found


def measure(root):
    return [(str(p.relative_to(root)), p.stat().st_size) for p in rule_paths(root)]


def over_budget(sizes, limit=MAX_BYTES):
    total = sum(size for _, size in sizes)
    return total, total > limit


def main(root=Path("."), limit=MAX_BYTES):
    sizes = measure(root)
    total, over = over_budget(sizes, limit)
    if not sizes:
        # No rule file is not a violation of a budget; it is a different row.
        return 0
    if not over:
        return 0
    print("BLOCKED by check-rule-budget (False Floors IL-1A): the agent rule set is "
          + str(total) + " bytes against a limit of " + str(limit) + ".", file=sys.stderr)
    for name, size in sorted(sizes, key=lambda x: -x[1]):
        print("  " + str(size).rjust(7) + "  " + name, file=sys.stderr)
    print("  Retire or merge rules, or raise the limit in this file deliberately.", file=sys.stderr)
    return 1


def self_test():
    problems = []
    if over_budget([("CLAUDE.md", 100)], 50) != (100, True):
        problems.append("a set over the limit was not refused")
    if over_budget([("CLAUDE.md", 40)], 50) != (40, False):
        problems.append("a set under the limit was refused")
    if over_budget([("a", 25), ("b", 26)], 50)[1] is not True:
        problems.append("sizes are not being totalled across files")
    if over_budget([("CLAUDE.md", 50)], 50)[1] is not False:
        problems.append("a set exactly at the limit was refused; the limit is inclusive")
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "CLAUDE.md").write_text("x" * 100)
        if main(root, 50) != 1:
            problems.append("a real over-budget rule file was allowed through end to end")
        if main(root, 500) != 0:
            problems.append("a real under-budget rule file was refused end to end")
        (root / "CLAUDE.md").unlink()
        if main(root, 1) != 0:
            problems.append("a repository with no rule file at all was refused")
    for p in problems:
        print("SELF-TEST FAIL: " + p, file=sys.stderr)
    print("check-rule-budget self-test: " + ("PASS, over-budget refused and under-budget allowed"
          if not problems else "FAIL"))
    return 1 if problems else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(self_test())
    raise SystemExit(main())
'''


BANNED_VALUES_LIST = """# Banned values for check-banned-values (False Floors CL-4B).
# One value per line. Optionally a tab and why it is banned, which is printed when it fires.
# Lines starting with # are comments. An empty list makes the gate refuse every commit and
# say so, because a gate that checks nothing must not read as if it checks something.
#
# Examples, to be replaced with this project's own:
# localhost:5432\tthe staging database, never production
# Admin123\ta default password that reached a repository once
"""


def graph_of(root):
    """The scanner's own view of what this repository has wired, used to check the wiring."""
    import importlib.util
    here = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("trust_check_for_install", here / "trust_check.py")
    tc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tc)
    return tc.module("detectors").connections(tc.Inventory(Path(root)))


# Each entry names the row, the guard, the surface it is wired to, and the file's own name.
# The filename is the one this row's detector already recognises, so a scan after the install
# credits the gate on its own evidence rather than needing a binding for it.
GATES = {
    "RL-2C": {"filename": "destructive-git-guard.py", "surface": "pre-tool", "matcher": "Bash",
              "source": DESTRUCTIVE_GUARD,
              "what": "refuses a destructive shell command while the working tree is dirty"},
    "CL-4B": {"filename": "check-banned-values.py", "surface": "pre-commit",
              "source": BANNED_VALUES_GUARD, "extra": {"tools/banned-values.txt": BANNED_VALUES_LIST},
              "what": "refuses a commit that adds a value this project has banned"},
    "IL-1A": {"filename": "check-rule-budget.py", "surface": "pre-commit",
              "source": RULE_BUDGET_GUARD,
              "what": "refuses a commit that pushes the agent rule set past its byte budget"},
}

DISPATCHER = """#!/usr/bin/env bash
# Written by False Floors trust-check. Each guard runs, every failure is kept, and the hook
# exits nonzero if any of them refused, so one guard cannot mask another.
set -uo pipefail
repo_root="$(git rev-parse --show-toplevel)"
fail=0
"""


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def wire_pre_commit(root, relative):
    """Add the guard to the pre-commit dispatcher, creating it if the repository has none.

    The dispatcher is written in the aggregate-then-fail shape: every guard runs, failures are
    collected, and the exit status is the aggregate. A guard added to an existing dispatcher is
    appended before its exit line rather than replacing anything already there.
    """
    hook = root / HOOKS_DIR / "pre-commit"
    call = 'python3 "${repo_root}/' + relative + '" || fail=1'
    notes = []
    if hook.exists():
        body = hook.read_text(encoding="utf-8")
        if call in body:
            return ["The dispatcher already invokes this guard; left unchanged."]
        lines = body.rstrip("\n").split("\n")
        exits = [i for i, l in enumerate(lines) if re.fullmatch(r"""exit ["']?\$\{?\w+\}?["']?""", l.strip())]
        if not exits:
            return ["EXISTING HOOK NOT CHANGED: " + str(hook.relative_to(root)) + " is not the aggregate-then-fail shape"
                    " this installer understands, and editing a hook it cannot read would be worse than not"
                    " installing. Add this line yourself, before the hook's final exit: " + call]
        lines.insert(exits[-1], call)
        hook.write_text("\n".join(lines) + "\n", encoding="utf-8")
        notes.append("Added to the existing " + str(hook.relative_to(root)) + " dispatcher.")
    else:
        hook.parent.mkdir(parents=True, exist_ok=True)
        hook.write_text(DISPATCHER + call + '\nexit "$fail"\n', encoding="utf-8")
        notes.append("Created " + str(hook.relative_to(root)) + ".")
    hook.chmod(0o755)
    code, current = 0, ""
    p = subprocess.run(["git", "-C", str(root), "config", "--get", "core.hooksPath"],
                       capture_output=True, text=True, timeout=10)
    current = p.stdout.strip()
    if current != HOOKS_DIR:
        subprocess.run(["git", "-C", str(root), "config", "core.hooksPath", HOOKS_DIR], check=True, timeout=10)
        notes.append("Set core.hooksPath to " + HOOKS_DIR + (" (was " + current + ")." if current else "."))
    return notes


def wire_pre_tool(root, relative, matcher):
    """Register the guard as a PreToolUse hook in the project-local settings file."""
    path = root / SETTINGS
    doc = {}
    if path.exists():
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            return ["EXISTING SETTINGS NOT CHANGED: " + SETTINGS + " is not valid JSON. Repair it and"
                    " rerun, or add the hook by hand; overwriting a settings file this installer cannot"
                    " read could remove hooks you rely on."]
        if not isinstance(doc, dict):
            return ["EXISTING SETTINGS NOT CHANGED: " + SETTINGS + " is not a JSON object."]
    command = 'python3 "$CLAUDE_PROJECT_DIR/' + relative + '"'
    hooks = doc.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        return ["EXISTING SETTINGS NOT CHANGED: the `hooks` value in " + SETTINGS + " is not an object."]
    events = hooks.setdefault("PreToolUse", [])
    if not isinstance(events, list):
        return ["EXISTING SETTINGS NOT CHANGED: `hooks.PreToolUse` in " + SETTINGS + " is not a list."]
    for group in events:
        if isinstance(group, dict) and any(isinstance(h, dict) and h.get("command") == command
                                           for h in group.get("hooks", []) if isinstance(group.get("hooks"), list)):
            return ["The settings file already registers this guard; left unchanged."]
    events.append({"matcher": matcher, "hooks": [{"type": "command", "command": command}]})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return ["Registered a PreToolUse hook on " + matcher + " in " + SETTINGS + "."]


def run_self_test(root, relative):
    """Run the guard's own self-test. The only code this tool ever executes in a repository."""
    try:
        p = subprocess.run([sys.executable, "-B", str(root / relative), "--self-test"],
                           capture_output=True, text=True, timeout=SELF_TEST_TIMEOUT, cwd=str(root))
    except (OSError, subprocess.SubprocessError) as e:
        return {"ran": False, "passed": False, "detail": "the self-test could not be run (" + type(e).__name__ + ")"}
    detail = " ".join((p.stdout + " " + p.stderr).split())[:300]
    # A zero exit is not evidence a self-test ran: a script with no `--self-test` at all exits
    # zero and would be recorded as passing. The guard has to say so in its own words, naming
    # itself, or this is not a pass. Found by mutation on 2026-09-09: replacing this call with
    # a fabricated {"passed": True} survived every test until the receipt had to carry proof.
    stem = Path(relative).stem
    said_so = (stem + " self-test: PASS") in detail
    return {"ran": True, "passed": p.returncode == 0 and said_so, "detail": detail,
            "evidence": stem + " self-test: PASS" if said_so else
                        "the guard did not report a passing self-test in its own output"}


def install(root, row, force=False):
    """Write one gate, wire it, run its self-test, and return the receipt.

    Nothing about this returns a bare "installed". The receipt carries the self-test result and
    the guard's digest, so a later scan can say what the self-test found and whether the file
    it found is still the file that was tested.
    """
    spec = GATES.get(row)
    if spec is None:
        return {"row": row, "installed": False,
                "reason": "No installable gate for this row. The library has " + ", ".join(sorted(GATES))
                          + ". Every other row's control needs something only you know, so the report says"
                            " what to build rather than pretending a generic gate would do."}
    root = Path(root)
    relative = TOOLS_DIR + "/" + spec["filename"]
    target = root / relative
    notes = []
    if target.exists() and not force:
        if target.read_text(encoding="utf-8") == spec["source"]:
            notes.append("The guard is already present and identical; not rewritten.")
        else:
            return {"row": row, "installed": False,
                    "reason": relative + " already exists and differs from the library's version. It is not"
                              " overwritten, because it may be your own gate. Move it aside, or rerun with"
                              " --install-force to replace it."}
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(spec["source"], encoding="utf-8")
        target.chmod(0o755)
        notes.append(("Replaced " if force and target.exists() else "Wrote ") + relative + ".")
    for extra_rel, body in (spec.get("extra") or {}).items():
        extra = root / extra_rel
        if extra.exists():
            notes.append(extra_rel + " already exists; left as it is.")
            continue
        extra.parent.mkdir(parents=True, exist_ok=True)
        extra.write_text(body, encoding="utf-8")
        notes.append("Wrote " + extra_rel + ", which you fill in.")
    if spec["surface"] == "pre-commit":
        notes += wire_pre_commit(root, relative)
    else:
        notes += wire_pre_tool(root, relative, spec.get("matcher", "Bash"))
    outcome = run_self_test(root, relative)
    return {"row": row, "installed": True, "path": relative, "surface": spec["surface"],
            "what": spec["what"], "sha256": digest(target), "selfTest": outcome, "notes": notes}


def receipt_state(root, receipt):
    """What a later scan can honestly say about an install it did not perform.

    The self-test ran once, at install time. Re-running it would mean executing code on every
    scan, which the scanner does not do, so instead the guard's digest is compared: the same
    bytes that passed the self-test, or a file that has changed since and whose self-test
    result therefore says nothing about what is there now.
    """
    path = Path(root) / receipt.get("path", "")
    if not path.is_file():
        return "the guard this receipt names is gone"
    if digest(path) != receipt.get("sha256"):
        return "the guard has changed since its self-test ran; that result no longer describes this file"
    outcome = receipt.get("selfTest") or {}
    if not outcome.get("ran"):
        return "its self-test could not be run"
    if not outcome.get("passed"):
        return "its self-test FAILED against the known-bad"
    return "wired and its self-test caught the known-bad"


def self_test():
    """Install every gate in the library into a throwaway repository and check the result.

    This is the gate on the gate library: a template whose own self-test fails, or which the
    installer wires in a shape the scanner cannot recognise, fails here rather than in
    somebody's repository.
    """
    problems = []
    for row in sorted(GATES):
        with tempfile.TemporaryDirectory(prefix="ff-install-selftest-") as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            result = install(root, row)
            if not result.get("installed"):
                problems.append(row + ": not installed (" + result.get("reason", "") + ")")
                continue
            if not result["selfTest"]["ran"]:
                problems.append(row + ": its self-test did not run (" + result["selfTest"]["detail"] + ")")
            elif not result["selfTest"]["passed"]:
                problems.append(row + ": its own self-test FAILED: " + result["selfTest"]["detail"])
            elif (Path(result["path"]).stem + " self-test: PASS") not in result["selfTest"].get("detail", ""):
                problems.append(row + ": the receipt records a pass the guard never printed")
            # The self-test proves the guard refuses. It says nothing about whether the wiring
            # lets that refusal stop anything, and a dispatcher that discards the failure
            # (`|| true`) passes every test above while protecting nothing. Found by mutating
            # the dispatcher on 2026-09-09: the mutant survived, which is the false floor this
            # whole tool is named for, sitting inside the tool. So the graph is asked directly.
            edges = [e for e in graph_of(root).edges
                     if e["path"] == result["path"] and e["surface"] == result["surface"]]
            if not edges:
                problems.append(row + ": the installed guard is not connected on " + result["surface"])
            elif not any(e["safe"] for e in edges):
                problems.append(row + ": the installed guard is connected but its failure is swallowed,"
                                      " conditional or asynchronous, so refusing would stop nothing")
            if receipt_state(root, result) != "wired and its self-test caught the known-bad":
                problems.append(row + ": the receipt does not read as a passing install: " + receipt_state(root, result))
            # A changed guard must stop the receipt from speaking for it.
            (root / result["path"]).write_text("# tampered\n", encoding="utf-8")
            if "changed" not in receipt_state(root, result):
                problems.append(row + ": a tampered guard still reads as tested")
            (root / result["path"]).unlink()
            if "gone" not in receipt_state(root, result):
                problems.append(row + ": a deleted guard still reads as tested")
    # The known-bad for run_self_test itself: a guard that exits zero and says nothing must not
    # be recorded as having passed a self-test. Without this fixture, dropping the output check
    # and trusting the exit status alone is invisible, because every shipped template does print
    # its result. Found by mutation on 2026-09-09.
    with tempfile.TemporaryDirectory(prefix="ff-install-selftest-") as tmp:
        root = Path(tmp)
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        silent = "silently-passes.py"
        GATES[silent] = {"filename": silent, "surface": "pre-commit",
                         "source": "#!/usr/bin/env python3\nimport sys\nraise SystemExit(0)\n",
                         "what": "a guard with no self-test at all, used only as this test's known-bad"}
        try:
            outcome = install(root, silent)["selfTest"]
        finally:
            del GATES[silent]
        if outcome["passed"]:
            problems.append("a guard that exits zero without running a self-test was recorded as passing")
        if "did not report a passing self-test" not in outcome.get("evidence", ""):
            problems.append("the receipt does not say why a silent guard was not counted as passing")

    # An unknown row must be refused, not silently skipped.
    with tempfile.TemporaryDirectory(prefix="ff-install-selftest-") as tmp:
        subprocess.run(["git", "init", "-q", tmp], check=True)
        if install(tmp, "ZZ-9Z").get("installed"):
            problems.append("a row with no template reported an install")
        # An existing foreign guard must never be overwritten.
        root = Path(tmp)
        (root / TOOLS_DIR).mkdir(parents=True, exist_ok=True)
        (root / TOOLS_DIR / GATES["IL-1A"]["filename"]).write_text("# mine, not yours\n", encoding="utf-8")
        outcome = install(root, "IL-1A")
        if outcome.get("installed") or "already exists" not in outcome.get("reason", ""):
            problems.append("an existing guard of the same name was overwritten or the refusal was silent")
        if (root / TOOLS_DIR / GATES["IL-1A"]["filename"]).read_text() != "# mine, not yours\n":
            problems.append("an existing guard's contents were changed")
        # A pre-commit hook the installer cannot read must be left alone and reported.
        (root / HOOKS_DIR).mkdir(parents=True, exist_ok=True)
        (root / HOOKS_DIR / "pre-commit").write_text("#!/bin/sh\nsomething_else\n", encoding="utf-8")
        notes = wire_pre_commit(root, "tools/whatever.py")
        if not any("NOT CHANGED" in n for n in notes):
            problems.append("an unrecognised pre-commit hook was edited instead of reported")
        if (root / HOOKS_DIR / "pre-commit").read_text() != "#!/bin/sh\nsomething_else\n":
            problems.append("an unrecognised pre-commit hook was modified")
    for p in problems:
        print("SELF-TEST FAIL: " + p, file=sys.stderr)
    print("install.py self-test: " + ("PASS, " + str(len(GATES)) + " gates installed, self-tested, "
          "tamper-checked and refused where they should be" if not problems else "FAIL"))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(self_test())

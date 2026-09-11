"""Read-only installation detectors. No target code is imported or executed."""
import ast
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
from urllib.parse import quote

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent / "vendor"))
import yaml


class Unsupported(ValueError):
    pass


def config(text):
    """YAML's string-only loader avoids the YAML 1.1 'on' -> True conversion.

    Reject aliases/tags and duplicate keys instead of trying to interpret custom
    config languages or alias expansion. A parser limit produces unknown.
    """
    if any(isinstance(t, (yaml.tokens.AliasToken, yaml.tokens.AnchorToken, yaml.tokens.TagToken)) for t in yaml.scan(text)):
        raise Unsupported("YAML aliases, anchors and explicit tags are unsupported")
    class Loader(yaml.BaseLoader):
        def construct_mapping(self, node, deep=False):
            out = {}
            for key, value in node.value:
                k = self.construct_object(key, deep=deep)
                if not isinstance(k, str) or k in out:
                    raise Unsupported("duplicate or non-string configuration key")
                out[k] = self.construct_object(value, deep=deep)
            return out
    return yaml.load(text, Loader=Loader)


def enabled(value):
    return value is True or value == "true"


def parse(inv, path):
    text = inv.read(path)
    if text is None:
        return None
    try:
        return config(text)
    except (yaml.YAMLError, Unsupported, RecursionError, TypeError) as e:
        inv.errors.append(path + ": " + type(e).__name__)
        return None


def result(rid, state, evidence, how, reason):
    return {"rowId": rid, "state": state, "evidence": evidence, "how": how,
            "reason": reason, "evidenceClass": "detected-configuration" if state == "present" else "inspection",
            "observation": None, "gap": "open", "manifest": False}


MANIFEST = ".false-floors.json"
MANIFEST_ROWS = 40
MANIFEST_PATHS = 60


class Manifest:
    """The repository's own statement of which of its files implements which row.

    A declaration supplies exactly two things for a gate row: an accepted entry
    filename in addition to the row's pattern, and a waiver of that row's term
    check. It supplies nothing else. Connection on a listed surface, synchronous
    enabled invocation, readability inside the repository, the guard's input read
    and its rejection path are all still established by inspection.
    """

    def __init__(self, inv):
        self.entries, self.notes, self.unreadable = {}, [], {}
        self.declared, self.error, self.confirmed_on, self.installed = False, None, {}, {}
        text, error = self.probe(inv, MANIFEST)
        if error:
            self.declared, self.error = True, "the file could not be read (" + error + ")"
            return
        if text is None:
            return
        self.declared = True
        try:
            doc = json.loads(text)
        except ValueError:
            self.error = "the file is not valid JSON"
            return
        if not isinstance(doc, dict):
            self.error = "the top-level value is not an object"
            return
        gates = doc.get("gates")
        if gates is None:
            self.notes.append("No `gates` object is declared, so no row binding was supplied.")
            gates = {}
        if not isinstance(gates, dict):
            self.error = "the `gates` value is not an object"
            return
        # `confirmedOn`, `installed` and `note` are written by this tool's own confirm and
        # install steps and read by the report, so naming them as strays would be noise.
        ignored = sorted(k for k in doc if k not in ("gates", "confirmedOn", "installed", "note"))
        if ignored:
            self.notes.append("Top-level keys other than `gates` are ignored: " + ", ".join(ignored[:8]) + ".")
        self.confirmed_on = doc.get("confirmedOn") if isinstance(doc.get("confirmedOn"), dict) else {}
        # Receipts from this tool's own installs: the guard's digest and what its self-test
        # found. A report reads these to say what the self-test found rather than that a file
        # exists; nothing here credits a row.
        self.installed = doc.get("installed") if isinstance(doc.get("installed"), dict) else {}
        if len(gates) > MANIFEST_ROWS:
            self.notes.append("More than " + str(MANIFEST_ROWS) + " declared rows; the remainder was not read.")
        budget = MANIFEST_PATHS
        for rid, value in sorted(gates.items())[:MANIFEST_ROWS]:
            paths = [value] if isinstance(value, str) else value
            if not isinstance(paths, list) or not paths or not all(isinstance(p, str) and p.strip() for p in paths):
                self.notes.append(rid + ": the declared value is not a path or a list of paths; ignored.")
                continue
            kept = []
            for path in paths:
                if budget <= 0:
                    self.notes.append("Declared-path budget exceeded; later declarations were not read.")
                    break
                budget -= 1
                path = path.strip().removeprefix("./")
                kept.append(path)
                if path not in self.unreadable:
                    _, error = self.probe(inv, path)
                    if error:
                        self.unreadable[path] = error
            if kept:
                self.entries[rid] = kept

    @staticmethod
    def probe(inv, path):
        """Read a declared path, and keep its read error out of the shared list.

        Readability and containment are settled here rather than left to whether the
        command graph happened to reach the file. The error is moved out, and the
        cache entry with it, so a declaration can never turn an unrelated detector's
        absent into unknown and a later graph read still reports the same problem.
        """
        mark = len(inv.errors)
        text = inv.read(path)
        raised = inv.errors[mark:]
        if raised:
            del inv.errors[mark:]
            inv.cache.pop(str(path), None)
        return text, raised[0] if raised else None


    @classmethod
    def trial(cls, inv, bindings):
        """A manifest that exists only for the length of one verification.

        D-272's confirmation step needs to answer "if this binding were declared, would the
        scanner credit it?" without writing anything to the repository. The trial manifest
        goes through the same readability probe a declared path goes through, so a proposal
        naming an unreadable file is refused here rather than after it is written.
        """
        self = cls.__new__(cls)
        self.entries, self.notes, self.unreadable = {}, [], {}
        self.declared, self.error, self.confirmed_on, self.installed = True, None, {}, {}
        for rid, paths in bindings.items():
            kept = []
            for path in paths:
                path = path.strip().removeprefix("./")
                kept.append(path)
                if path not in self.unreadable:
                    _, error = self.probe(inv, path)
                    if error:
                        self.unreadable[path] = error
            if kept:
                self.entries[rid] = kept
        return self


def manifest(inv):
    if not hasattr(inv, "repository_manifest"):
        inv.repository_manifest = Manifest(inv)
    return inv.repository_manifest


def manifest_report(inv, specs, findings):
    """What happened to every declared binding, so a declaration is never silent."""
    declaration = manifest(inv)
    graph = connections(inv)
    entries = []
    for rid, paths in sorted(declaration.entries.items()):
        spec = specs.get(rid)
        found = findings.get(rid) or {}
        for path in paths:
            if declaration.error:
                outcome, detail = "not applied", "The manifest is unusable: " + declaration.error + "."
            elif spec is None:
                outcome, detail = "unknown row, ignored", "This scanner inspects no catalogue row with that ID."
            elif not spec.get("manifestCreditable"):
                outcome, detail = "declared, not creditable", spec.get("manifestReason", "")
            elif path in declaration.unreadable:
                outcome, detail = "declared but unreadable", declaration.unreadable[path]
            elif found.get("manifest") and found.get("how", "").split(" -> ")[-1] == path:
                outcome, detail = "credited", "Connected at " + found["how"] + "."
            elif found.get("state") == "present":
                # The row stopped at the first source it recognised, so this one was never judged.
                outcome, detail = "not evaluated", "The row is already credited to " + found.get("how", "").split(" -> ")[-1] + "."
            elif not any(e["path"] == path and e["surface"] in set(spec["surfaces"]) for e in graph.edges):
                outcome, detail = "declared, not connected", "Not invoked on " + ", ".join(sorted(spec["surfaces"])) + "."
            else:
                outcome, detail = "declared, not credited", found.get("reason", "")
            entries.append({"rowId": rid, "path": path, "outcome": outcome, "detail": detail})
    return {"path": MANIFEST, "declared": declaration.declared, "error": declaration.error,
            "notes": declaration.notes, "entries": entries}


def verify_bindings(inv, specs, bindings):
    """Would the scanner credit each proposed binding? Answered without writing anything.

    A seat proposes and never credits, so this is the only thing standing between a proposal
    and a `present`. It re-establishes, for every proposal: that the file is connected on one
    of the row's surfaces, that the invocation is synchronous and enabled and not reached
    through a conditional or a swallowed failure, that the source reads an input, and that it
    has a path that refuses. The row's own term list is waived, because a binding is exactly
    the claim that this file implements the row under a name the recogniser does not know.
    """
    original = getattr(inv, "repository_manifest", None)
    outcomes = {}
    try:
        for rid, paths in sorted(bindings.items()):
            spec = specs.get(rid)
            if spec is None:
                outcomes[rid] = {"row": rid, "paths": paths, "verified": False,
                                 "reason": "This scanner inspects no catalogue row with that ID."}
                continue
            if not spec.get("manifestCreditable"):
                outcomes[rid] = {"row": rid, "paths": paths, "verified": False,
                                 "reason": spec.get("manifestReason", "")}
                continue
            inv.repository_manifest = Manifest.trial(inv, {rid: paths})
            found = gate(inv, rid, spec)
            credited = found["state"] == "present" and found.get("manifest")
            outcomes[rid] = {"row": rid, "paths": paths, "verified": bool(credited),
                             "state": found["state"],
                             "where": found.get("how", ""),
                             "reason": found["reason"]}
    finally:
        if original is None:
            if hasattr(inv, "repository_manifest"):
                del inv.repository_manifest
        else:
            inv.repository_manifest = original
    return outcomes


def _load_manifest_doc(root):
    path = Path(root) / MANIFEST
    if not path.exists():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ValueError(MANIFEST + " exists and could not be read (" + type(e).__name__
                         + "); resolve it before writing, so nothing already accepted is lost")
    if not isinstance(doc, dict):
        raise ValueError(MANIFEST + " exists and is not a JSON object; resolve it first")
    return doc


def write_install_receipt(inv, row, receipt, today):
    """Record what a gate's self-test found, beside the bindings, in the tool's own file."""
    path = Path(inv.root) / MANIFEST
    doc = _load_manifest_doc(inv.root)
    installed = doc.get("installed")
    doc["installed"] = installed if isinstance(installed, dict) else {}
    doc["installed"][row] = {"path": receipt["path"], "sha256": receipt["sha256"],
                             "surface": receipt["surface"], "on": today,
                             "selfTest": receipt["selfTest"]}
    doc.setdefault("gates", {})
    doc["note"] = ("Written by trust-check. `gates` are bindings the owner confirmed; `installed` records "
                   "gates this tool installed, with each guard's digest and what its self-test found. "
                   "A receipt is not a credit: every run re-establishes wiring, synchrony, an input read "
                   "and a refusal path, and compares the digest before repeating a self-test result.")
    path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def write_manifest(inv, confirmed, today):
    """Write the owner's confirmed bindings. The tool writes this file; the owner never does.

    Existing bindings are preserved: a confirmation adds to the repository's memory rather
    than replacing it. `confirmedOn` records when a person accepted each one, which is what
    makes a later report able to say `confirmed` rather than `verified`.
    """
    path = Path(inv.root) / MANIFEST
    doc = {"gates": {}, "confirmedOn": {}}
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise ValueError(MANIFEST + " exists and could not be read (" + type(e).__name__
                             + "); resolve it before confirming, so nothing already accepted is lost")
        if not isinstance(existing, dict) or not isinstance(existing.get("gates", {}), dict):
            raise ValueError(MANIFEST + " exists and is not the expected shape; resolve it before confirming")
        doc["gates"] = dict(existing.get("gates") or {})
        doc["confirmedOn"] = dict(existing.get("confirmedOn") or {}) if isinstance(existing.get("confirmedOn"), dict) else {}
    added = {}
    for rid, paths in sorted(confirmed.items()):
        keep = list(dict.fromkeys(list(doc["gates"].get(rid) or []) + list(paths)))
        if keep != doc["gates"].get(rid):
            added[rid] = paths
        doc["gates"][rid] = keep
        doc["confirmedOn"][rid] = today
    if len(doc["gates"]) > MANIFEST_ROWS:
        raise ValueError(MANIFEST + " would declare more than " + str(MANIFEST_ROWS)
                         + " rows, which is beyond what the scanner reads back")
    doc["note"] = ("Written by trust-check from bindings the repository owner confirmed. "
                   "A binding says which file implements which catalogue row; it never stands in "
                   "for reading that file, and the scanner re-establishes wiring, synchrony, an "
                   "input read and a refusal path on every run.")
    path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return added


def manifest_report(inv, specs, findings):
    """What happened to every declared binding, so a declaration is never silent."""
    declaration = manifest(inv)
    graph = connections(inv)
    entries = []
    for rid, paths in sorted(declaration.entries.items()):
        spec = specs.get(rid)
        found = findings.get(rid) or {}
        for path in paths:
            if declaration.error:
                outcome, detail = "not applied", "The manifest is unusable: " + declaration.error + "."
            elif spec is None:
                outcome, detail = "unknown row, ignored", "This scanner inspects no catalogue row with that ID."
            elif not spec.get("manifestCreditable"):
                outcome, detail = "declared, not creditable", spec.get("manifestReason", "")
            elif path in declaration.unreadable:
                outcome, detail = "declared but unreadable", declaration.unreadable[path]
            elif found.get("manifest") and found.get("how", "").split(" -> ")[-1] == path:
                outcome, detail = "credited", "Connected at " + found["how"] + "."
            elif found.get("state") == "present":
                # The row stopped at the first source it recognised, so this one was never judged.
                outcome, detail = "not evaluated", "The row is already credited to " + found.get("how", "").split(" -> ")[-1] + "."
            elif not any(e["path"] == path and e["surface"] in set(spec["surfaces"]) for e in graph.edges):
                outcome, detail = "declared, not connected", "Not invoked on " + ", ".join(sorted(spec["surfaces"])) + "."
            else:
                outcome, detail = "declared, not credited", found.get("reason", "")
            entries.append({"rowId": rid, "path": path, "outcome": outcome, "detail": detail})
    return {"path": MANIFEST, "declared": declaration.declared, "error": declaration.error,
            "notes": declaration.notes, "entries": entries}


ROOT_VARS = ("CLAUDE_PROJECT_DIR", "GITHUB_WORKSPACE", "repo_root")
ROOT_ASSIGNMENT = re.compile(r"""(repo_root|REPO_ROOT|root|ROOT|repo|REPO)=["']?\$\(git rev-parse --show-toplevel( 2>/dev/null)?( \|\| pwd)?\)["']?""")
SET_LINES = ("set -e", "set -eu", "set -euo pipefail")
CONTROL_FLOW = r"^\s*(if |case |for |while |.*\(\)\s*\{)"
# Well-known GitHub Actions that set a job up rather than guard anything. A step using one of
# these adds no uncertainty; any other action might be the operator's guard, and an action step's
# behaviour is not inspected. Matched exactly on the owner/name part before the "@".
NON_GUARD_ACTIONS = ("actions/checkout", "actions/setup-python", "actions/setup-node",
                     "actions/cache", "actions/upload-artifact", "actions/download-artifact")


class Connections:
    """Follow a bounded graph of configured commands without invoking them.

    Every point at which a surface stops being interpretable is recorded with the
    file and the line that stopped it, so an unknown finding can say why.
    """
    def __init__(self, inv):
        self.inv = inv
        self.edges = []
        self.uncertain = set()
        self.reasons = {}
        self.touched = set()
        self.settings = []
        self.actions = []
        self._ci()
        self._git_hooks()
        self._claude()

    def flag(self, surface, where, line, why):
        self.uncertain.add(surface)
        entries = self.reasons.setdefault(surface, [])
        # One reason per configuration location, so a cap of five names five files, not five lines of one.
        if len(entries) < 5 and all(w != where for w, _, _ in entries):
            entries.append((where, line.strip()[:160], why))

    def explain(self, surfaces):
        parts = []
        for surface in sorted(surfaces):
            for where, line, why in self.reasons.get(surface, []):
                parts.append(f"{surface}: {why} at {where}" + (f": `{line}`" if line else ""))
        return "; ".join(parts[:6])

    def read(self, path):
        self.touched.add(path)
        return self.inv.read(path)

    def parse(self, path):
        self.touched.add(path)
        return parse(self.inv, path)

    def relevant_errors(self, path=None):
        """Read errors on configuration the graph actually touched; a read failure elsewhere in the tree is not this surface's problem."""
        paths = {path} if path else self.touched
        return [e for e in self.inv.errors if any(e.startswith(p + ":") for p in paths)]

    @staticmethod
    def aggregate(lines):
        """Recognise the aggregate-then-fail dispatcher exactly.

        The shape is `V=0`, then only `guard || V=1` lines, then `exit "$V"` as the last
        line; anything before the initialiser must be a `set -` line or a recognised
        root assignment. A bare command, a reassignment, a conditional or an `exit 0`
        between the initialiser and the exit could drop a failure, so the body is then
        not this idiom and falls back to the ordinary rules.
        """
        if len(lines) < 3:
            return None
        m = re.fullmatch(r"""exit ["']?\$\{?(\w+)\}?["']?""", lines[-1])
        if not m or lines.count(m[1] + "=0") != 1:
            return None
        var = m[1]
        start = lines.index(var + "=0")
        if not all(re.fullmatch(r"set -[a-z]+( pipefail)?", s) or ROOT_ASSIGNMENT.fullmatch(s) for s in lines[:start]):
            return None
        guards = lines[start + 1:-1]
        if not guards or not all(re.fullmatch(r"[^;&|`]+?\s*\|\|\s*" + var + "=1", g) for g in guards):
            return None
        return var

    def add(self, surface, command, where, safe=True, depth=0, stack=(), cwd=""):
        if len(self.edges) >= 400 or depth > 5:
            self.flag(surface, where, "", "command graph budget exceeded")
            return
        if not isinstance(command, str) or not command.strip():
            return
        # A backslash continuation is one command; join it before any line is judged.
        command = re.sub(r"\\\n[ \t]*", " ", command)
        meaningful = [s.strip() for s in command.splitlines() if s.strip() and not s.strip().startswith("#")]
        aggregate = self.aggregate(meaningful)
        if len(meaningful) > 1 and aggregate is None and not any(s in SET_LINES for s in meaningful):
            safe = False
        if re.search(r"\bset\s+\+e\b", command):
            safe = False
        root_vars = set(ROOT_VARS)
        # Shell compound expressions can swallow failures or condition execution.
        # Retain candidates, but only straight invocations earn presence.
        for original in command.splitlines():
            line = original.strip()
            if not line or line.startswith("#") or line in SET_LINES + ("set -u", "set -uo pipefail", "exit 0"):
                continue
            assignment = ROOT_ASSIGNMENT.fullmatch(line)
            if assignment:
                # The variable names the assessed root; nothing is executed to learn that.
                root_vars.add(assignment[1])
                continue
            if aggregate:
                if line == aggregate + "=0" or line == meaningful[-1]:
                    continue
                guarded = re.fullmatch(r"(.+?)\s*\|\|\s*" + aggregate + "=1", line)
                if guarded:
                    # Failure is aggregated and returned at exit, so the guard is a straight invocation.
                    line = guarded[1].strip()
            for var in root_vars:
                line = line.replace("${" + var + "}", str(self.inv.root)).replace("$" + var, str(self.inv.root))
            complex_line = bool(re.search(r"[;&|<>`]|\$\(|\$\{|^(if|then|case|for|while|function)\s", line))
            try:
                tokens = shlex.split(line, comments=True)
            except ValueError:
                self.flag(surface, where, original, "shell line could not be tokenised")
                continue
            if not tokens:
                continue
            executable = Path(tokens[0]).name
            if executable in ("npm", "pnpm", "yarn") and len(tokens) >= 3 and tokens[1] == "run":
                package = self.parse("package.json") or {}
                script = package.get("scripts", {}).get(tokens[2])
                if script is None or tokens[2] in stack:
                    self.flag(surface, where, original, "npm script missing or cyclic")
                else:
                    self.add(surface, script, where + " -> package.json#/scripts/" + tokens[2], safe and not complex_line, depth + 1, stack + (tokens[2],), cwd)
                continue
            index = 1 if executable in ("python", "python3", "node", "bash", "sh") else 0
            while index < len(tokens) and tokens[index].startswith("-"):
                # python -c, node -e, bash -c are intentionally not analysed.
                if tokens[index] in ("-c", "-e", "-m"):
                    break
                index += 1
            target = tokens[index] if index < len(tokens) else ""
            if target.startswith("-") or "$" in target:
                self.flag(surface, where, original, "shell variable, substitution or option in command position")
                continue
            p = Path(target)
            if p.is_absolute():
                try:
                    target = str(p.relative_to(self.inv.root))
                except ValueError:
                    self.flag(surface, where, original, "command target outside the repository")
                    continue
            target = target.removeprefix("./")
            if cwd and target and not Path(target).is_absolute():
                # A CI step's working-directory moves the command's cwd; the path in the
                # command is relative to it, not to the repository root. Standard GitHub
                # Actions, used by every monorepo; not a repository-specific shape.
                joined = os.path.normpath(os.path.join(cwd, target))
                if joined.startswith(".."):
                    self.flag(surface, where, original, "command target outside the repository")
                    continue
                target = joined
            if Path(target).suffix not in (".py", ".sh", ".js", ".mjs"):
                # Native utilities and shell syntax are not candidate source files.
                # Do not try to read '.' or a tool's directory argument as code.
                if executable not in ("echo", "printf", "true", "false", "exit", "set", "cd"):
                    self.flag(surface, where, original, "unrecognised executable or non-script argument")
                continue
            body = self.read(target) if target else None
            if body is None:
                # Recognised package executables are handled by their configuration detector.
                self.edges.append({"surface": surface, "path": target, "body": None, "command": original,
                                   "where": where, "safe": False, "args": tokens})
                continue
            runnable = index > 0 or os.access(self.inv.root / target, os.X_OK)
            edge = {"surface": surface, "path": target, "body": body, "command": original,
                    "where": where, "safe": safe and runnable and not complex_line, "args": tokens}
            self.edges.append(edge)
            # Follow shell dispatcher files, which commonly connect Git hooks to guards.
            if target.endswith(".sh") and target not in stack:
                body_safe = edge["safe"] and not re.search(CONTROL_FLOW, body, re.M)
                self.add(surface, body, where + " -> " + target, body_safe, depth + 1, stack + (target,), cwd)

    def _ci(self):
        for path in self.inv.paths([".github/workflows/*.yml", ".github/workflows/*.yaml"]):
            doc = self.parse(path)
            if not isinstance(doc, dict) or not doc.get("on"):
                self.flag("CI", path, "", "workflow unreadable, unsupported YAML or no trigger")
                continue
            wd_workflow = str((((doc.get("defaults") or {}).get("run") or {}).get("working-directory") or "")).strip()
            jobs = doc.get("jobs", {})
            if not isinstance(jobs, dict):
                self.flag("CI", path, "", "jobs is not a mapping")
                continue
            for name, job in jobs.items():
                if not isinstance(job, dict) or not job.get("runs-on"):
                    self.flag("CI", path + "#/jobs/" + str(name), "", "job without runs-on (reusable workflow or malformed job)")
                    continue
                if str(job.get("if", "")).strip() in ("false", "${{ false }}"):
                    continue
                wd_job = str((((job.get("defaults") or {}).get("run") or {}).get("working-directory") or wd_workflow)).strip()
                steps = job.get("steps", [])
                if not isinstance(steps, list):
                    self.flag("CI", path + "#/jobs/" + str(name), "", "steps is not a list")
                    continue
                for step in steps:
                    if not isinstance(step, dict):
                        continue
                    if str(step.get("if", "")).strip() in ("false", "${{ false }}"):
                        continue
                    wd = str((step.get("working-directory") or wd_job or "")).strip()
                    # An unexpanded expression cannot be resolved without running the workflow,
                    # so the step keeps its old treatment: unresolved, and never counted as safe.
                    wd_known = "${{" not in wd
                    safe = not any(x in job for x in ("if", "container")) and not any(x in step for x in ("if", "shell"))
                    safe = safe and not enabled(job.get("continue-on-error")) and not enabled(step.get("continue-on-error"))
                    safe = safe and wd_known
                    action = step.get("uses")
                    if isinstance(action, str) and action.strip():
                        # An action's own code is never fetched or read, so the step is recorded as
                        # connected but uninspected rather than counted as nothing at all.
                        self.actions.append({"surface": "CI", "ref": action.strip(), "where": path + "#/jobs/" + name})
                    self.add("CI", step.get("run"), path + "#/jobs/" + name, safe, cwd=(wd if wd_known else ""))

    def _git_hooks(self):
        run = self.inv.git("config", "--get", "core.hooksPath")
        if run.code not in (0, 1):
            self.flag("pre-commit", "git config core.hooksPath", "", "git configuration unavailable")
            return
        hooks = run.out if run.code == 0 else ".git/hooks"
        p = Path(hooks)
        if p.is_absolute():
            try:
                hooks = str(p.relative_to(self.inv.root))
            except ValueError:
                self.flag("pre-commit", "git config core.hooksPath", hooks, "hooks path outside the repository")
                return
        path = str(Path(hooks) / "pre-commit")
        text = self.read(path)
        if text is not None and os.access(self.inv.root / path, os.X_OK):
            # A conditional dispatcher is not assumed to invoke a particular guard.
            safe = not re.search(CONTROL_FLOW, text, re.M)
            self.add("pre-commit", text, "git config core.hooksPath -> " + path, safe)

    def _claude(self):
        hook_surfaces = ("pre-tool", "session start", "stop")
        for path in (".claude/settings.json", ".claude/settings.local.json"):
            doc = self.parse(path)
            if doc is None:
                if self.relevant_errors(path):
                    for surface in hook_surfaces:
                        self.flag(surface, path, "", "settings file unreadable or invalid JSON")
                continue
            if not isinstance(doc, dict):
                for surface in hook_surfaces:
                    self.flag(surface, path, "", "settings document is not an object")
                continue
            self.settings.append((path, doc))
        if self.uncertain & set(hook_surfaces):
            return
        # Local disableAllHooks applies to the combined project-local inventory.
        if any(enabled(d.get("disableAllHooks")) for _, d in self.settings):
            return
        for path, doc in self.settings:
            hooks = doc.get("hooks", {})
            if not isinstance(hooks, dict):
                for surface in hook_surfaces:
                    self.flag(surface, path + "#/hooks", "", "hooks is not an object")
                continue
            for event, surface in (("PreToolUse", "pre-tool"), ("SessionStart", "session start"), ("Stop", "stop")):
                groups = hooks.get(event, [])
                where = path + "#/hooks/" + event
                if not isinstance(groups, list):
                    self.flag(surface, where, "", "event entry is not a list")
                    continue
                for group in groups:
                    if not isinstance(group, dict) or not isinstance(group.get("hooks", []), list):
                        self.flag(surface, where, "", "hook group malformed")
                        continue
                    for handler in group.get("hooks", []):
                        if not isinstance(handler, dict) or handler.get("type") != "command":
                            self.flag(surface, where, "", "handler is not a command hook")
                            continue
                        safe = not enabled(handler.get("async")) and not handler.get("if")
                        start = len(self.edges)
                        self.add(surface, handler.get("command"), where, safe)
                        for edge in self.edges[start:]:
                            edge["matcher"] = group.get("matcher", "")


def connections(inv):
    if not hasattr(inv, "connections"):
        inv.connections = Connections(inv)
    return inv.connections


# ---------------------------------------------------------------------------
# The control map (D-272)
#
# A control has three structural facts that carry no vocabulary: it is wired to a trigger,
# it reads something, and it has a path that refuses. The map states those three for every
# wired control and nothing else. There is no filename list here and no row term here, on
# purpose: widening either was the approach D-272 closed, after four days of widening the
# recogniser by one shape per repository and finding each shape was used by no other.
#
# What the map is for: a reading seat names the catalogue row each control implements from
# this text. The map never carries a row, and this module never assigns one. Only the
# owner's confirmation, or a detector's own independent recognition, binds a control.
# ---------------------------------------------------------------------------

MAP_ENTRIES = 150
MAP_HEADER = 600
MAP_MESSAGE = 160
READ_SIGNALS = (
    ("staged diff", r"git diff --cached|git diff --staged|diff-index --cached"),
    ("working diff", r"git diff(?! --cached| --staged)"),
    ("commit range", r"git log|rev-list|merge-base"),
    ("hook stdin json", r"\btool_input\b|\btool_name\b|hook_event_name|json\.load\(sys\.stdin\)|process\.stdin|\$\(cat\)"),
    ("file read", r"readFileSync|readFile\(|open\(|read_text\(|\.read\(\)|fs\.promises"),
    ("tree walk", r"os\.walk|rglob|glob\(|\bfind\s+\.|git ls-files"),
    ("grep", r"\bgrep\b|\brg\b|re\.search|re\.findall|\.match\("),
    ("argv", r"sys\.argv|process\.argv|\$1\b|\$@"),
    ("network", r"curl\b|fetch\(|requests\.|urllib|http\."),
    ("environment", r"os\.environ|process\.env"),
)
REFUSAL_LINE = re.compile(r"""\bexit\s+[12]\b|\bexit\s+"?\$\{?\w*(fail|rc|status|code|err)\w*\}?"?|sys\.exit\((?!0)|process\.exit\((?!0)|\bthrow\b|\braise\b|"decision"\s*:\s*"block"|permissionDecision""", re.I)
MESSAGE_LITERAL = re.compile(r"""(?:"((?:[^"\\\n]|\\.){6,200})"|'((?:[^'\\\n]|\\.){6,200})'|`((?:[^`\\\n]|\\.){6,200})`)""")
BANNER = re.compile(r"^(#!/|\s*$|[-=*]{3,})")


def source_header(text):
    """The comment or docstring a control opens with, which is written for a human reader."""
    out, in_doc = [], False
    for line in text.splitlines()[:40]:
        s = line.strip()
        if s.startswith(('"""', "'''", "/*")):
            in_doc = not in_doc or s.count('"""') == 2
            s = s.strip("\"'/* ")
            if s:
                out.append(s)
            continue
        if in_doc:
            if '"""' in s or "*/" in s:
                in_doc = False
            s = s.strip("*/ ")
            if s:
                out.append(s)
            continue
        if s.startswith(("#", "//", "*")):
            if BANNER.match(s):
                continue
            s = s.lstrip("#/* ").strip()
            if s and not s.startswith("!"):
                out.append(s)
        elif out:
            break
    return " ".join(out)[:MAP_HEADER]


def source_reads(text):
    return [name for name, pattern in READ_SIGNALS if re.search(pattern, text)]


def source_refusals(text):
    """String literals near a line that refuses, plus the refusing lines themselves.

    The refusal message is the richest stable text in any repository, because it is the one
    string somebody wrote for whoever trips the control. Literals are taken from the four
    lines before a refusing line, which is where a message is printed before an exit.
    """
    lines = text.splitlines()
    messages, exits = [], []
    for i, line in enumerate(lines):
        if not REFUSAL_LINE.search(line):
            continue
        exits.append(line.strip()[:120])
        for near in lines[max(0, i - 4):i + 1]:
            for match in MESSAGE_LITERAL.finditer(near):
                literal = next(g for g in match.groups() if g)
                # Two words of letters, so a path, a flag or a format string is not a message.
                if re.search(r"[A-Za-z]{3,}\s+[A-Za-z]{2,}", literal) and literal not in messages:
                    messages.append(literal[:MAP_MESSAGE])
    return messages[:8], list(dict.fromkeys(exits))[:6]


def control_map(inv, findings=None):
    """One entry per wired control, built from the connection graph alone.

    Deterministic: the graph is already built and its bodies are already read inside the
    inventory's budget, so this adds no reads. `boundTo` says whether anything has bound
    this control to a row yet, and by what authority - a detector that recognised it
    without help, or an owner who confirmed it. A control with neither is what the reading
    step is offered, which is also why the second run of a repository reads less than the
    first.
    """
    graph = connections(inv)
    declaration = manifest(inv)
    declared = {}
    for rid, paths in declaration.entries.items():
        for path in paths:
            declared.setdefault(path, rid)
    verified = {}
    for rid, found in (findings or {}).items():
        if found.get("state") == "present" and not found.get("manifest"):
            verified.setdefault((found.get("how") or "").split(" -> ")[-1], rid)
    entries, seen = [], set()
    for edge in graph.edges[:MAP_ENTRIES]:
        key = (edge["surface"], edge["where"], edge["path"])
        if key in seen:
            continue
        seen.add(key)
        entry = {"id": edge["surface"] + "::" + edge["where"] + " -> " + edge["path"],
                 "surface": edge["surface"], "trigger": edge["where"],
                 "matcher": edge.get("matcher", ""),
                 "command": " ".join((edge["command"] or "").split())[:300],
                 "path": edge["path"],
                 # Not a judgement about the control: it records whether a failure of it
                 # would actually stop anything, which the graph already established.
                 "synchronousAndEnabled": bool(edge["safe"])}
        body = edge["body"]
        if body is None:
            entry["source"] = "unreadable or missing"
        else:
            messages, exits = source_refusals(body)
            entry.update(header=source_header(body), reads=source_reads(body),
                         refusalMessages=messages, exitLines=exits,
                         lines=body.count("\n") + 1)
        bound = declared.get(edge["path"]) or verified.get(edge["path"])
        entry["boundTo"] = bound
        entry["bindingSource"] = ("confirmed" if edge["path"] in declared
                                  else "verified" if edge["path"] in verified else None)
        entries.append(entry)
    # An action step is connected and its behaviour is not inspected. It belongs in the map
    # as a control nobody can read rather than as nothing at all.
    for action in graph.actions:
        if action["ref"].split("@")[0] in NON_GUARD_ACTIONS:
            continue
        entries.append({"id": "CI::" + action["where"] + " -> uses " + action["ref"],
                        "surface": "CI", "trigger": action["where"], "matcher": "",
                        "command": "uses: " + action["ref"], "path": None,
                        "synchronousAndEnabled": None,
                        "source": "a third-party action; its code is never fetched or read",
                        "boundTo": None, "bindingSource": None})
    return {"note": "Every control this repository has wired, described by its trigger, what it reads and what it says when it refuses. No catalogue row is assigned here. A control with boundTo null has not been bound to a row by anything.",
            "entries": entries[:MAP_ENTRIES],
            "truncated": len(entries) > MAP_ENTRIES}


def executable_source(body, path, tokens):
    """Recognise the supported guard's static shape, not its behavioral correctness.

    The guard must read input and contain a rejection path and row-specific terms.
    Names alone, comment-only bait and pass-through stubs do not qualify.
    """
    if path.endswith(".py"):
        try:
            tree = ast.parse(body)
        except SyntaxError:
            return False
        # Drop docstrings/comments from the evidence used for recognition.
        for node in ast.walk(tree):
            if hasattr(node, "body") and isinstance(node.body, list):
                node.body = [n for n in node.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str))]
        code = ast.unparse(tree)
        calls = [ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)]
        reads = any(x in ("open", "json.load", "json.loads", "subprocess.run", "subprocess.check_output") or x.endswith((".read", ".read_text")) for x in calls)
        refuses = any(isinstance(n, ast.Raise) or (isinstance(n, ast.Call) and ast.unparse(n.func) in ("sys.exit", "exit") and n.args and not (isinstance(n.args[0], ast.Constant) and n.args[0].value == 0)) for n in ast.walk(tree))
    else:
        code = "\n".join(line for line in body.splitlines() if not line.strip().startswith(("#", "//", "/*", "*")))
        reads = bool(re.search(r"\b(readFile|readFileSync|grep|git|jq|cat|stat|find|test)\b|\[\s+-[efd]", code))
        refuses = bool(re.search(r"\bexit\s+[12]\b|process\.exit\([12]\)|throw\s+", code))
    return reads and refuses and all(re.search(token, code, re.I) for token in tokens)


def gate(inv, rid, spec):
    graph = connections(inv)
    declaration = manifest(inv)
    if declaration.error:
        return result(rid, "unknown", "", MANIFEST,
                      "The repository manifest " + MANIFEST + " is unusable: " + declaration.error + ". A declared row binding cannot be read, so no gate row is decided while that stands.")
    declared = list(declaration.entries.get(rid, ())) if spec.get("manifestCreditable") else []
    blocked = [p for p in declared if p in declaration.unreadable]
    if blocked:
        return result(rid, "unknown", "", MANIFEST,
                      "Declared in " + MANIFEST + " for this row, " + blocked[0] + " could not be read inside the repository (" + declaration.unreadable[blocked[0]] + "). A declaration binds a row to a file; it never stands in for reading it.")
    surfaces = set(spec["surfaces"])
    candidates = []
    reached = set()
    for edge in graph.edges:
        if edge["surface"] not in surfaces:
            continue
        # A declaration adds an accepted entry filename; the pattern still admits its own.
        by_manifest = edge["path"] in declared
        if not by_manifest and not re.fullmatch(spec["entry"], Path(edge["path"]).name):
            continue
        reached.add(edge["path"])
        matcher = edge.get("matcher", "")
        matched = True
        if edge["surface"] == "pre-tool":
            try:
                matched = all(not matcher or re.search(matcher, tool) for tool in spec.get("tools", ["Bash"]))
            except re.error:
                matched = False
        candidates.append((edge, matched, by_manifest))
        # A declaration waives this row's terms and nothing else about the source.
        if matched and edge["safe"] and edge["body"] and executable_source(edge["body"], edge["path"], [] if by_manifest else spec["tokens"]):
            found = result(rid, "present", edge["command"], edge["where"] + " -> " + edge["path"],
                           "Recognised guard source is connected to a synchronous enabled local invocation"
                           + ("; the row binding was declared in " + MANIFEST + ", not inferred" if by_manifest else "")
                           + ". This establishes installation/configuration only; predicate correctness, remote required status and bypass resistance have not been exercised.")
            found["manifest"] = by_manifest
            return found
    missing = [p for p in declared if p not in reached]
    note = (" Declared in " + MANIFEST + " for this row but not connected on " + ", ".join(sorted(surfaces))
            + ": " + ", ".join(missing[:5]) + "." if missing else "")
    if candidates:
        e, matched, by_manifest = candidates[0]
        tail = (" This file was declared in " + MANIFEST + " for this row." if by_manifest else "") + note
        if e["body"] is None:
            errors = graph.relevant_errors(e["path"])
            if errors:
                return result(rid, "unknown", e["command"], e["where"], "Configured guard target could not be read (" + errors[0] + "); no working connection was established." + tail)
            return result(rid, "absent", e["command"], e["where"], "Configured guard target " + e["path"] + " is missing; no working connection was established." + tail)
        if not e["safe"]:
            why = "is reached through a conditional, asynchronous, failure-swallowing or compound invocation"
        elif not matched:
            why = "is registered under a hook matcher that does not cover the tool this row gates"
        elif by_manifest:
            why = "does not show the recognised guard shape (an input read and a rejection path)"
        else:
            why = "does not show the recognised guard shape (an input read, a rejection path and this row's terms)"
        return result(rid, "unknown", e["command"], e["where"] + " -> " + e["path"], "Candidate guard " + e["path"] + " " + why + "; no installation credit." + tail)
    problems = graph.explain(graph.uncertain & surfaces)
    errors = graph.relevant_errors()
    connected = sorted({e["path"] for e in graph.edges if e["surface"] in surfaces})
    listed = ", ".join(connected[:8]) + (", ..." if len(connected) > 8 else "")
    if problems or errors:
        detail = "; ".join(x for x in (problems, "; ".join(errors[:3])) if x)
        if connected:
            detail += ". Connected on this surface but not recognised for this row: " + listed
        return result(rid, "unknown", "", ", ".join(sorted(surfaces)), "Unsupported configuration on the inspected surface prevented a local installation decision. " + detail + note)
    opaque = sorted({a["ref"] for a in graph.actions
                     if a["surface"] in surfaces and a["ref"].split("@")[0] not in NON_GUARD_ACTIONS})
    if opaque:
        named = ", ".join(opaque[:6]) + (", ..." if len(opaque) > 6 else "")
        detail = ". Connected on this surface but not recognised for this row: " + listed if connected else ""
        return result(rid, "unknown", "", ", ".join(sorted(surfaces)),
                      "An action step's behaviour is not inspected, so a third-party GitHub Action connected on this surface (" + named + ") may or may not implement this mechanism" + detail + "." + note)
    # An unrelated invoked custom implementation might implement this mechanism.
    if connected:
        return result(rid, "unknown", "", ", ".join(sorted(surfaces)), "Only unrecognised guard implementations are connected on this surface (" + listed + "). A custom equivalent may exist; the recogniser accepts an entry named " + spec["entry"] + "." + note)
    return result(rid, "absent", "", ", ".join(sorted(surfaces)), "No enabled local connection for this mechanism was found on the inspected surfaces. User/managed settings and other CI providers remain outside scope." + note)


def structural(inv, rid, spec):
    kind = spec["kind"]
    if kind == "git-tracked":
        # The working-set audit walks the whole tree, so it gets the audit budget
        # rather than the metadata one. An audit that runs out of time names the
        # command and the limit; nothing is inferred from an incomplete reading.
        run = inv.git("ls-files", "--others", "--directory", "--no-empty-directory", "--exclude-standard", timeout=inv.git_audit_timeout)
        how = run.command
        if run.limit is not None:
            return result(rid, "unknown", "", how, "Git working-set audit incomplete: `" + how + "` did not complete within the scanner's " + str(run.limit) + " s Git audit budget, so untracked-file state was not read. Nothing is inferred from an incomplete audit; this run is not comparable with one where the audit finished.")
        if run.code:
            return result(rid, "unknown", "", how, "Git working-set audit unavailable: `" + how + "` exited " + str(run.code) + " within the scanner's " + str(inv.git_audit_timeout) + " s Git audit budget.")
        remaining = [f for f in run.out.splitlines() if f not in ("false-floors-assessment.json", "false-floors-assessment.md")]
        return result(rid, "absent" if remaining else "present", "\n".join(remaining[:10]) if remaining else str(inv.root), how, "Untracked paths exist in this working set." if remaining else "No nonignored untracked paths in this Git root. Ignored paths and other working folders are not claimed recoverable.")
    if kind == "local-unlinked":
        if inv.read("supabase/config.toml") is None:
            return result(rid, "unknown", "", "supabase/config.toml", "No supported local CLI project configuration; not assumed applicable.")
        ref = inv.read("supabase/.temp/project-ref")
        if inv.errors:
            return result(rid, "unknown", "", "supabase/.temp/project-ref", "Link metadata could not be inspected.")
        return result(rid, "absent" if ref and ref.strip() else "present", "supabase/.temp/project-ref" if ref else "supabase/config.toml", "read local project-link metadata", "A remote project link is recorded." if ref and ref.strip() else "No local CLI project link is recorded. Other credentials and explicit remote command arguments are not verified.")
    if kind == "subagent-tools":
        paths = inv.paths([".claude/agents/*.md"])
        for path in paths:
            text = inv.read(path)
            if text and text.startswith("---\n"):
                try:
                    header = config(text.split("---", 2)[1])
                    tools = header.get("tools")
                    if isinstance(tools, str) and tools.strip() and "*" not in tools:
                        line = next(line for line in text.splitlines() if line.startswith("tools:"))
                        return result(rid, "present", line, path, "An explicit subagent tool allowlist is configured. It remains agent-editable; runtime inheritance and enforcement are unverified.")
                except (ValueError, yaml.YAMLError, AttributeError):
                    pass
        return result(rid, "unknown" if inv.errors else "absent", "", ".claude/agents/*.md", "No readable explicit tool allowlist found in inspected subagent definitions.")
    if kind == "mcp":
        for path in (".mcp.json",):
            doc = parse(inv, path)
            if isinstance(doc, dict) and isinstance(doc.get("mcpServers"), dict):
                for name, server in doc["mcpServers"].items():
                    if isinstance(server, dict) and not enabled(server.get("disabled")) and (server.get("command") or server.get("url")):
                        return result(rid, "present", path, path + "#/mcpServers/" + name, "A connector is declared locally. Availability, credentials and actual live-source use are not verified.")
        return result(rid, "unknown" if inv.errors else "absent", "", ".mcp.json#/mcpServers", "No enabled local connector declaration found.")
    raise Unsupported("Unknown structural detector " + kind)


def gh_get(endpoint):
    # All endpoints are generated here. Explicit CLI opt-in is required by caller.
    try:
        p = subprocess.run(["gh", "api", "--hostname", "github.com", "--method", "GET", "-H", "X-GitHub-Api-Version: 2026-03-10", endpoint], capture_output=True, text=True, timeout=5)
        if p.returncode:
            return {"ok": False, "reason": "API request unavailable", "how": "gh api GET " + endpoint}
        if len(p.stdout) > 256 * 1024:
            return {"ok": False, "reason": "API response budget exceeded", "how": endpoint}
        return {"ok": True, "data": json.loads(p.stdout), "how": "gh api GET " + endpoint}
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return {"ok": False, "reason": "GitHub CLI unavailable or response invalid", "how": endpoint}


def fetch_policy(repo, branch, get=gh_get):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo) or not branch or len(branch) > 200:
        raise ValueError("Explicit GitHub OWNER/REPO and branch required")
    effective = get(f"repos/{repo}/rules/branches/{quote(branch, safe='')}?per_page=100")
    legacy = get(f"repos/{repo}/branches/{quote(branch, safe='')}/protection")
    details = {}
    if effective["ok"] and isinstance(effective["data"], list) and len(effective["data"]) < 100:
        for rule in effective["data"]:
            if not isinstance(rule, dict):
                effective = {"ok": False, "how": effective["how"], "reason": "Malformed effective rule"}
                break
            rid, source = rule.get("ruleset_id"), rule.get("ruleset_source")
            if rid in details:
                continue
            if len(details) >= 5 or not isinstance(rid, int) or not isinstance(source, str):
                effective = {"ok": False, "how": effective["how"], "reason": "Ruleset details incomplete or request budget exceeded"}
                break
            if rule.get("ruleset_source_type") == "Repository" and re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", source):
                endpoint = f"repos/{source}/rulesets/{rid}"
            elif rule.get("ruleset_source_type") == "Organization" and re.fullmatch(r"[A-Za-z0-9_.-]+", source):
                endpoint = f"orgs/{source}/rulesets/{rid}"
            else:
                details[rid] = {"ok": False, "reason": "Unsupported ruleset source"}
                continue
            details[rid] = get(endpoint)
    else:
        effective = {"ok": False, "how": effective["how"], "reason": "Effective rule list unavailable or pagination exceeds budget"}
    return {"repo": repo, "branch": branch, "effective": effective, "legacy": legacy, "details": details}


def remote(inv, rid, spec):
    try:
        return _remote(inv, rid, spec)
    except (AttributeError, KeyError, TypeError, ValueError):
        return result(rid, "unknown", "", "GitHub policy response", "Policy response fields could not be interpreted; no absence or coverage inferred.")


def _remote(inv, rid, spec):
    policy = getattr(inv, "github_policy", None)
    if policy is None:
        return result(rid, "unknown", "", "GitHub policy (not requested)", "Remote state was not queried. Optional --allow-github OWNER/REPO explicitly permits sending repository identity and CLI authentication to GitHub; no local hook is substituted for server policy.")
    effective, legacy = policy["effective"], policy["legacy"]
    required = spec["rules"]
    good, unknown = {}, not effective["ok"]
    if effective["ok"]:
        for rule in effective["data"]:
            detail = policy["details"].get(rule.get("ruleset_id"), {})
            if not detail.get("ok"):
                unknown = True
                continue
            data = detail["data"]
            if data.get("enforcement") != "active" or "bypass_actors" not in data:
                unknown = True
                continue
            if data["bypass_actors"]:
                continue
            typ = rule.get("type")
            params = rule.get("parameters", {})
            if typ == "required_status_checks" and not params.get("required_status_checks"):
                continue
            if typ == "pull_request" and spec.get("reviewer") and int(params.get("required_approving_review_count", 0)) < 1:
                continue
            good[typ] = rule
    if all(k in good for k in required):
        if spec.get("deploy") and not deploy_connected(inv, policy["branch"]):
            return result(rid, "unknown", "", "GitHub rules + deployment workflow", "Branch policy exists; no supported deploy workflow restricted to that branch was established.")
        return result(rid, "present", json.dumps([good[k] for k in required], ensure_ascii=False), effective["how"], "Effective server rules and their active, empty-bypass rulesets contain the required settings. This is an API configuration observation; no push or deployment was attempted.")
    if legacy["ok"] and isinstance(legacy["data"], dict):
        d = legacy["data"]
        pr = d.get("required_pull_request_reviews")
        pr_ok = isinstance(pr, dict) and not any(pr.get("bypass_pull_request_allowances", {}).values())
        if spec.get("reviewer"):
            pr_ok = pr_ok and isinstance(pr.get("required_approving_review_count"), int) and pr["required_approving_review_count"] >= 1
        flags = {"pull_request": pr_ok,
                 "non_fast_forward": d.get("allow_force_pushes", {}).get("enabled") is False,
                 "required_status_checks": bool((d.get("required_status_checks") or {}).get("contexts") or (d.get("required_status_checks") or {}).get("checks"))}
        if d.get("enforce_admins", {}).get("enabled") is True and all(flags.get(k, False) or k in good for k in required):
            if spec.get("deploy") and not deploy_connected(inv, policy["branch"]):
                return result(rid, "unknown", "", "branch protection + deployment workflow", "Protected branch observed but supported deployment restriction not established.")
            return result(rid, "present", json.dumps({k: d.get(k) for k in ("enforce_admins", "allow_force_pushes", "required_pull_request_reviews", "required_status_checks")}), legacy["how"], "Legacy branch protection contains the requested settings and enforces them for admins. Effective session behavior was not exercised.")
    else:
        unknown = True
    return result(rid, "unknown" if unknown else "absent", "", effective["how"] + "; " + legacy["how"], "Required configuration was not established from all inspected policy sources; unavailable API fields remain unknown." if unknown else "The inspected active policy configuration lacks one or more required no-bypass settings.")


def deploy_connected(inv, branch):
    for path in inv.paths([".github/workflows/*.yml", ".github/workflows/*.yaml"]):
        doc = parse(inv, path)
        if not isinstance(doc, dict) or not isinstance(doc.get("on"), dict):
            continue
        trigger = doc["on"].get("push")
        if not isinstance(trigger, dict) or trigger.get("branches") != [branch] or set(doc["on"]) != {"push"}:
            continue
        for edge in connections(inv).edges:
            if edge["surface"] == "CI" and edge["where"].startswith(path + "#") and edge["safe"] and re.search(r"deploy", Path(edge["path"]).name):
                return True
    return False

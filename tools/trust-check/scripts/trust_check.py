#!/usr/bin/env python3
"""False Floors installation check. Bundled parser; never executes target code."""
import argparse
import collections
import datetime as dt
import hashlib
import functools
import contextlib
import io
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import stat
import subprocess
import sys
import time
import urllib.request
import urllib.error

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parents[1]
ASSETS = BASE / "assets"
TOOL_VERSION = "2"
INSPECTABLE = {"on disk", "CI", "pre-commit", "pre-tool", "session start", "subagent"}
EXPECTED = {"inspectable": 48, "inspectableClassC": 27, "judgement": 21, "unhandled": 35}
FEED = "https://api.github.com/repos/Scale100/false-floors/tags?per_page=100"
UPDATE = "https://github.com/Scale100/false-floors/releases"
MAX_FILE = 256 * 1024
MAX_FILES = 400
MAX_TOTAL = 4 * 1024 * 1024
# Two Git budgets. Metadata calls answer from the index in milliseconds. The
# working-set audit walks the whole tree, so it gets an order of magnitude more
# room: measured 2.2-2.5 s on a 160,000-file checkout, where a shared 4 s budget
# flapped between runs and moved a count with nothing changed in the repository.
GIT_TIMEOUT = 4
GIT_AUDIT_TIMEOUT = 30
NAMES = ("false-floors-assessment.json", "false-floors-assessment.md")
LOCKED_FILES = {
    "assets/register-data.json",
    "assets/catalogue-releases.json",
    "assets/editorial.json",
    "assets/detectors.json",
    "scripts/check-assessment.py",
    "scripts/diff-catalogue.py",
}
# limit carries the exceeded budget on a timeout and is None on any completed run,
# so a caller can tell an incomplete audit from a Git that answered with an error.
GitRun = collections.namedtuple("GitRun", "code out command limit")


@functools.lru_cache(maxsize=8)
def module(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), BASE / "scripts" / (name + ".py"))
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def calibration_inputs():
    paths = {"scripts/trust_check.py", "scripts/detectors.py", "scripts/validate.py", "scripts/fixture_cases.py", "scripts/install.py", "assets/detectors.json", "assets/register-data.json"}
    paths.update(str(p.relative_to(BASE)) for p in (BASE / "scripts/vendor/yaml").glob("*.py"))
    return paths


def judgement(row):
    return (row["tool"] == "none" and row["tier"] == "process") or bool(re.match(r"^C\s", row["outcome"] or ""))


def bucket(row):
    if row["catchPoint"] in INSPECTABLE:
        return "inspectableClassC" if judgement(row) else "inspectable"
    return "judgement" if judgement(row) else "unhandled"


def load_assets():
    lock = json.loads((ASSETS / "integrity.json").read_text())
    if set(lock.get("sha256", {})) != LOCKED_FILES:
        raise ValueError("Shipped asset integrity lock does not name the exact required file set")
    for relative, digest in lock["sha256"].items():
        if hashlib.sha256((BASE / relative).read_bytes()).hexdigest() != digest:
            raise ValueError("Shipped asset changed; rebuild and revalidate: " + relative)
    data = json.loads((ASSETS / "register-data.json").read_text())
    counts = dict(collections.Counter(bucket(r) for r in data["rows"]))
    if counts != EXPECTED or len({r["id"] for r in data["rows"]}) != len(data["rows"]):
        raise ValueError("Catalogue bucket/identity mismatch: " + json.dumps(counts))
    specs = json.loads((ASSETS / "detectors.json").read_text())
    if set(specs) != {r["id"] for r in data["rows"] if r["catchPoint"] in INSPECTABLE}:
        raise ValueError("Detector coverage does not match the catalogue")
    try:
        receipt = json.loads((ASSETS / "calibration.json").read_text())
        expected_paths = calibration_inputs()
        current = set(receipt["sha256"]) == expected_paths and all(hashlib.sha256((BASE / p).read_bytes()).hexdigest() == digest for p, digest in receipt["sha256"].items())
        current = current and set(receipt["active"]) == {rid for rid, s in specs.items() if s["status"] == "active"}
    except (OSError, ValueError, KeyError, TypeError):
        current = False
    if not current:
        for rid, s in list(specs.items()):
            if s["status"] == "active":
                specs[rid] = {"kind": "unobservable", "status": "draft", "scope": s.get("scope", s["kind"]), "reason": "Calibration receipt missing or stale; detector demoted to draft and not credited."}
    # A repository manifest can bind a row only where a positive observation would count.
    judged = {r["id"] for r in data["rows"] if judgement(r)}
    for rid, s in specs.items():
        if s["status"] != "active":
            why = "This row's detector is draft, so nothing observed for it is credited."
        elif s["kind"] != "gate":
            why = "This row's detector is " + s["kind"] + ", not a gate; a manifest supplies a gate row's entry filename only."
        elif rid in judged:
            why = "This is a Class C or judgement row; it stays open whatever is installed."
        else:
            why = ""
        s["manifestCreditable"], s["manifestReason"] = not why, why
    return data, specs, json.loads((ASSETS / "editorial.json").read_text()), counts


class Inventory:
    """Bounded reads, no symlinks or target programs, no global credential inspection."""
    def __init__(self, root):
        self.root = root.resolve()
        self.cache = {}
        self.bytes = 0
        self.errors = []
        self.git_cache = {}
        # Audits that ran out of time. Kept apart from self.errors on purpose:
        # detectors branch on that list being empty, so appending here would let
        # one slow command change an unrelated row's state.
        self.incomplete = []
        self.git_audit_timeout = GIT_AUDIT_TIMEOUT

    def read(self, relative):
        path = self.root / relative
        key = str(relative)
        if key in self.cache:
            return self.cache[key]
        try:
            if path.is_symlink() or not path.resolve().is_relative_to(self.root):
                raise ValueError("symlink or path outside assessment root")
            info = path.stat()
            if not stat.S_ISREG(info.st_mode):
                raise ValueError("not a regular file")
            if info.st_size > MAX_FILE or self.bytes + info.st_size > MAX_TOTAL or len(self.cache) >= MAX_FILES:
                raise ValueError("read budget exceeded")
            with path.open("rb") as f:
                raw = f.read(MAX_FILE + 1)
            if len(raw) > MAX_FILE:
                raise ValueError("file grew beyond read budget")
            self.bytes += len(raw)
            text = raw.decode("utf-8")
        except FileNotFoundError:
            text = None
        except (OSError, UnicodeError, ValueError) as e:
            self.errors.append(key + ": " + str(e))
            text = None
        self.cache[key] = text
        return text

    def paths(self, patterns):
        found = set()
        for pattern in patterns:
            # Patterns are shipped, shallow, and never recurse through the operator's tree.
            for p in self.root.glob(pattern):
                found.add(str(p.relative_to(self.root)))
                if len(found) > MAX_FILES:
                    self.errors.append("path enumeration budget exceeded")
                    return sorted(found)[:MAX_FILES]
        return sorted(found)

    def git(self, *args, timeout=None):
        limit = timeout or GIT_TIMEOUT
        key = args + (limit,)
        if key in self.git_cache:
            return self.git_cache[key]
        command = "git " + " ".join(args)
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        env.update(GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
        try:
            p = subprocess.run(["git", "--no-pager", "-c", "core.fsmonitor=false", "-c", "core.untrackedCache=false", "-C", str(self.root), *args], env=env,
                               capture_output=True, text=True, timeout=limit)
            run = GitRun(p.returncode, p.stdout.strip(), command, None)
        except subprocess.TimeoutExpired:
            run = GitRun(2, "", command, limit)
            note = command + ": did not complete within the scanner's " + str(limit) + " s Git budget"
            if note not in self.incomplete:
                self.incomplete.append(note)
        except OSError as e:
            run = GitRun(2, str(e), command, None)
        self.git_cache[key] = run
        return run


def finding(rid, state, evidence, how, reason, *, observation=None):
    return {"rowId": rid, "state": state, "evidence": evidence, "how": how,
            "reason": reason, "evidenceClass": "local-configuration" if state == "present" else "inspection",
            "observation": observation, "gap": "open"}


def detect(inv, rid, spec):
    """Present means the specified component is observable, never that a row closes.

    Code matches are candidates and stay unknown: a script's name or text cannot
    establish its semantics. There is no way to turn a generic grep into coverage.
    """
    kind = spec["kind"]
    if kind == "gate":
        return module("detectors").gate(inv, rid, spec)
    if kind == "remote":
        return module("detectors").remote(inv, rid, spec)
    if kind in {"git-tracked", "local-unlinked", "subagent-tools", "mcp"}:
        return module("detectors").structural(inv, rid, spec)
    how = "; ".join(spec.get("paths", [])) or spec.get("scope", "not locally observable")
    if kind == "unobservable":
        return finding(rid, "unknown", "", how, spec["reason"])
    errors_before = len(inv.errors)
    paths = inv.paths(spec.get("paths", []))
    candidates = []
    settings_seen = []
    settings_matches = []
    for path in paths:
        text = inv.read(path)
        if text is None:
            continue
        if kind == "schema":
            try:
                doc = json.loads(text)
            except (ValueError, TypeError):
                inv.errors.append(path + ": schema JSON could not be parsed")
                continue
            required = doc.get("required", []) if isinstance(doc, dict) else []
            if isinstance(doc, dict) and "$schema" in doc and isinstance(required, list) and all(x in required for x in spec["fields"]):
                return finding(rid, "present", path, path + " # /required",
                               "Required fields exist in a schema; application to records and semantic completeness remain unverified.")
        elif kind == "rules":
            if text.strip():
                return finding(rid, "present", path, path,
                               "A scoped instruction file exists. Runtime loading, scope correctness and compliance are unverified.")
        elif kind == "field":
            # Only explicit frontmatter / field lines, not incidental mention in prose.
            for line in text.splitlines():
                if re.fullmatch(spec["pattern"], line, re.I):
                    return finding(rid, "present", line, path,
                                   spec["qualification"])
        elif kind == "settings":
            try:
                doc = json.loads(text)
            except ValueError:
                inv.errors.append(path + ": settings JSON could not be parsed")
                continue
            try:
                value = doc
                for key in spec["keys"]:
                    value = value[key]
            except (ValueError, TypeError, KeyError):
                continue
            settings_seen.append(value)
            if spec["test"] == "nonempty-list" and isinstance(value, list) and any(isinstance(x, str) and x.strip() for x in value):
                # Quote a key and type, not credential-like values from a settings file.
                settings_matches.append(finding(rid, "present", json.dumps(spec["keys"][-1]), path + " # /" + "/".join(spec["keys"]), spec["qualification"]))
            if spec["test"] == "true" and value is True:
                settings_matches.append(finding(rid, "present", "true", path + " # /" + "/".join(spec["keys"]), spec["qualification"]))
        else:
            for line in text.splitlines():
                if line.lstrip().startswith(("#", "//", "<!--")):
                    continue
                if re.search(spec["pattern"], line, re.I):
                    candidates.append((path, line))
                    break
    if settings_matches:
        conflicting = any(x != settings_seen[0] for x in settings_seen[1:])
        unreadable = any(any(e.startswith(p + ":") for p in paths) for e in inv.errors)
        if conflicting or unreadable:
            return finding(rid, "unknown", "", how, "Project and local settings are conflicting or unreadable; effective configuration is not inferred.")
        return settings_matches[0]
    if candidates:
        path, line = candidates[0]
        return finding(rid, "unknown", line, path,
                       "Candidate configuration or guard text found. Its enforcement, activation and row-specific predicate are unverified; it is not credited.", observation="candidate")
    # Absent is only a statement about the declared local surface, not all mechanisms.
    relevant_errors = [e for e in inv.errors if any(e.startswith(p + ":") for p in paths)]
    if kind in {"schema", "rules", "field", "settings"} and not relevant_errors:
        return finding(rid, "absent", "", how,
                       "The specified component was not found in the listed local paths. Other paths, user/managed settings and runtime state were not assessed.")
    return finding(rid, "unknown", "", how,
                   "No verified implementation identified in the bounded local inspection. Custom paths, indirect invocation and external controls remain unverified."
                   + (" Read unavailable: " + "; ".join(inv.errors[errors_before:]) if inv.errors[errors_before:] else ""))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def version_key(version):
    match = re.fullmatch(r"FF-(\d{4})\.(\d+)", version)
    if not match:
        raise ValueError("invalid release version")
    return tuple(map(int, match.groups()))


def freshness(version, offline=False, opener=None):
    result = {"inUse": version, "status": "skipped", "url": FEED, "update": UPDATE}
    if offline:
        result["reason"] = "Offline mode requested; pinned catalogue in use."
        return result
    try:
        op = opener or urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect()).open
        request = urllib.request.Request(FEED, headers={"User-Agent": "false-floors-trust-check", "Accept": "application/json"})
        with op(request, timeout=3) as response:
            raw = response.read(MAX_FILE + 1)
        if len(raw) > MAX_FILE:
            raise ValueError("release feed exceeds read budget")
        releases = json.loads(raw)
        if not isinstance(releases, list) or len(releases) >= 100:
            raise ValueError("tag feed incomplete or beyond pagination budget")
        versions = [x["name"] for x in releases if isinstance(x, dict) and re.fullmatch(r"FF-\d{4}\.\d+", str(x.get("name", "")))]
        newest = max(versions, key=version_key)
        comparison = version_key(newest) > version_key(version.rstrip("+"))
        result.update(status="newer-available" if comparison else "checked", latest=newest, source="published catalogue release tags")
        if version.endswith("+"):
            result["reason"] = "Using unreleased canon; this is not a published release."
    except (OSError, ValueError, KeyError, TypeError) as e:
        status = type(e).__name__ + (" " + str(e.code) if isinstance(e, urllib.error.HTTPError) else "")
        result["reason"] = "Version check unavailable (" + status + "); pinned catalogue in use."
    return result


def catalogue_diff(prior, data, source_root=None):
    if prior is None:
        return {"status": "not-applicable", "reason": "No prior assessment."}
    if not isinstance(prior, dict) or not isinstance(prior.get("rows"), dict) or not isinstance(prior.get("catalogueVersion"), str):
        return {"status": "unavailable", "reason": "Prior assessment does not satisfy the diff contract."}
    diff_tool = module("diff-catalogue")
    if prior.get("generatedFrom") == data["generatedFrom"] and prior.get("catalogueVersion") == data["catalogueVersion"]:
        return {"status": "checked", "result": diff_tool.diff(data, data, prior)}
    if source_root:
        original = source_root / "tools/trust-check/scripts/diff-catalogue.py"
        if original.is_file():
            # Use existing diff logic and its historical snapshot resolver. Never run target code.
            diff_tool.ROOT = source_root
            diff_tool.RELEASES_PATH = ASSETS / "catalogue-releases.json"
            try:
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    rev, _ = diff_tool.resolve(prior["catalogueVersion"])
                    before = diff_tool.snapshot_at(rev)
                return {"status": "checked", "result": diff_tool.diff(before, data, prior)}
            except (Exception, SystemExit):
                pass
    return {"status": "unavailable", "reason": "Historical snapshot unavailable locally. Existing diff-catalogue.py needs the source repository history and a recorded release commit; no history was fetched or inferred."}


def questions(data, editorial, findings):
    # Do not turn detector unknowns or judgement rows into an interview.
    by_id = {r["id"]: r for r in data["rows"]}
    result = []
    for q in editorial["QUESTIONS"]:
        ids = [rid for rid in q["rowIds"] if rid not in findings and not judgement(by_id[rid])]
        # A report may explicitly declare unsupported row shapes. Asking about them
        # does not establish a mechanism, but can change the recommended human action.
        if ids:
            result.append({"id": q["id"], "title": q["title"], "rowIds": ids,
                           "detail": "Answer only for these remaining rows; optional self-report, never closes a row."})
    return result


def action_for(row, editorial):
    install = [g["install"] for g in editorial["INSTALL_GROUPS"] if row["id"] in g["rowIds"]]
    workflow = [g["instruction"] for g in editorial["WORKFLOW_ACTIONS"] if row["id"] in g["rowIds"]]
    # The web maps predate some canon changes. Canon's prevention wins on conflict;
    # the maps remain attributed suggestions, never a coverage oracle.
    return "EVERY REVIEW — " + (row.get("prevention") or row.get("mechanism") or "Review this row with a person."), install + workflow


def make_record(inv, data, specs, editorial, counts, fresh, previous, answers):
    if not isinstance(answers, dict):
        raise ValueError("Answers must be a JSON object of question IDs and booleans")
    # Read the manifest before any detector, so its own read never depends on row order.
    detectors = module("detectors")
    declaration = detectors.manifest(inv)
    findings = {r["id"]: {"manifest": False, **detect(inv, r["id"], specs[r["id"]]), "detectorStatus": specs[r["id"]]["status"]} for r in data["rows"] if r["id"] in specs}
    manifest_state = "not present" if not declaration.declared else ("unusable: " + declaration.error if declaration.error else "read")
    qs = questions(data, editorial, findings)
    allowed = {q["id"]: q for q in qs}
    if set(answers) - set(allowed) or any(not isinstance(x, bool) for x in answers.values()):
        raise ValueError("Answers must map only offered question IDs to JSON true/false")
    self_report = {rid: {"questionId": qid, "answer": answer, "evidenceClass": "self-reported"}
                   for qid, answer in answers.items() for rid in allowed[qid]["rowIds"]}
    actions, suggestions = {}, {}
    for row in data["rows"]:
        rid = row["id"]
        actions[rid], suggestions[rid] = action_for(row, editorial)
        if rid in self_report:
            actions[rid] = "EVERY REVIEW — " + ("Verify the self-reported control with an independent receipt. " if self_report[rid]["answer"] else "Plan the missing control with the operator. ") + (row.get("prevention") or "Review this row.")
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    record = {
        "assessmentId": "trust-check-" + today,
        "toolVersion": TOOL_VERSION,
        "environment": str(inv.root), "environmentNote": "Claude Code project-local configuration; invoker may be Codex. No target code executed. Global/managed settings and runtime behavior remain outside scope. GitHub policy is inspected only with explicit opt-in, recorded separately.",
        "catalogueVersion": data["catalogueVersion"], "generatedFrom": data["generatedFrom"],
        "date": today, "dateNote": "UTC assessment date; local observations at run time.",
        "liftedFromCanonAt": data["generatedFrom"],
        "schemaNote": "Present means the supported mechanism is installed/configured on the named surface, not behaviorally proven. Non-Class-C present rows are partially closed on that limited basis; Class C, absent, unknown and unhandled rows stay open. No row is fully closed by this scanner.",
        "rows": {r["id"]: ("partially closed" if findings.get(r["id"], {}).get("state") == "present" and not judgement(r) else "open") for r in data["rows"]},
        "installState": {rid: ("built" if f["state"] == "present" else "none") for rid, f in findings.items() if f["state"] in ("present", "absent")}, "truthStatus": {},
        "nextAction": actions, "registerVerification": {"scope": "Local static inventory; no runtime defaults credited. Previous Claude Code defaults reading dated 2026-08-10 has not been reverified. Repository manifest " + detectors.MANIFEST + ": " + manifest_state + "."},
        "bucketCounts": counts, "findings": findings, "selfReport": self_report,
        "questions": qs, "freshness": fresh, "catalogueDiff": previous,
        "privacy": ("Default scan: no repository data sent; only the fixed public catalogue release-tag request (unless offline). " if not getattr(inv, "github_policy", None) else "GitHub opt-in used: repository identity and the GitHub CLI authentication were sent to GitHub for read-only policy queries; no local source content was sent. ") + "A hosted assistant receives the compact summary and any excerpts read into its session.",
        "githubPolicyScope": ({"repository": inv.github_policy["repo"], "branch": inv.github_policy["branch"]} if getattr(inv, "github_policy", None) else "not requested"),
        "readBudget": {"filesReadOrAttempted": len(inv.cache), "bytesRead": inv.bytes, "unavailable": inv.errors, "incompleteAudits": list(inv.incomplete), "manifest": manifest_state},
        "manifest": detectors.manifest_report(inv, specs, findings),
        # D-272: the structural map of every wired control, which is what a reading seat is
        # offered. It carries no row and assigns none; only a confirmation or an independent
        # detector recognition binds one.
        "controlMap": detectors.control_map(inv, findings),
        "editorialSuggestions": {rid: v for rid, v in suggestions.items() if v},
    }
    checker = module("check-assessment")
    layer_names = {"instruction": "instruction-layer", "context": "context-layer", "authority-access": "authority-access-layer", "recovery": "recovery-layer", "provenance": "provenance-layer", "truth": "truth-layer"}
    catalogue = {r["id"]: {"layer": layer_names[r["layer"]], "outcome": (r["outcome"] or "").split(" ", 1)[-1].lower()} for r in data["rows"]}
    fails, review, stats = checker.audit(record, catalogue)
    if fails:
        raise ValueError("Canonical assessment validator: " + "; ".join(fails))
    record["validation"] = {"checker": "check-assessment.py audit (unchanged upstream)", "status": "pass", "stats": stats, "review": review}
    return record


def literal(value):
    return "<pre>" + str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") + "</pre>"


def inline_literal(value):
    compact = " ".join(str(value).split())
    return "<code>" + compact.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") + "</code>"


def manifest_section(man):
    """One short section, so a declared binding is never silent about its outcome."""
    lines = ["## Repository manifest", ""]
    if not man["declared"]:
        return lines + ["No `" + man["path"] + "` in the assessed repository root, so every row binding below was inferred by the detectors.", ""]
    lines += ["`" + man["path"] + "` lets the repository state which of its own files implements which row. A declaration supplies an accepted entry filename and waives that row's term check; connection on a listed surface, synchronous enabled invocation, readability inside the repository, the guard's input read and its rejection path are all still established by inspection. A declaration never credits a non-gate detector, a draft detector or a Class C row.", ""]
    if man["error"]:
        lines += ["The manifest was not applied: " + man["error"] + ". Every gate row is unknown while that stands.", ""]
    if man["notes"]:
        lines += ["- " + note for note in man["notes"]] + [""]
    if not man["entries"]:
        return lines + ["No row binding was declared.", ""]
    lines += ["| Row | Declared file | Outcome | Detail |", "|---|---|---|---|"]
    for e in man["entries"]:
        detail = " ".join((e["detail"] or "").split()).replace("|", "\\|")[:300]
        lines.append("| " + " | ".join([e["rowId"], "`" + e["path"].replace("|", "\\|") + "`", e["outcome"], detail]) + " |")
    return lines + [""]


def render_full(record, data):
    lines = ["---", "type: assessment", "status: static-inventory", "tool-version: " + TOOL_VERSION, "date: " + record["date"], "catalogue-version: " + record["catalogueVersion"], "---", "", "# False Floors assessment — full evidence", "", "This is the exhaustive maintainer view. The default v2 report contains only established Stage 1 results and the Stage 2 testing queue.", "", record["environmentNote"], "", record["schemaNote"], "", record["privacy"], "", "Catalogue: " + record["catalogueVersion"] + "; source: `" + record["generatedFrom"] + "`.", "", record["registerVerification"]["scope"], "", "## Freshness", "", literal(json.dumps(record["freshness"], ensure_ascii=False)), "", "## Catalogue changes since the previous assessment", "", literal(json.dumps(record["catalogueDiff"], ensure_ascii=False)), "", "## Inspection scope", ""]
    lines += [f"- {k}: {v}" for k, v in record["bucketCounts"].items()]
    lines += ["", "The remaining bucket includes stop, compact, prompt and review positions as well as null catch points. No score, badge, certification or environment ranking is produced. Severity order below is the catalogue's exposure order; it is not a ranking of repositories.", ""]
    lines += manifest_section(record["manifest"])
    sections = collections.OrderedDict((name, []) for name in ["Observed components and missing local components", "Judgement required", "Unknown inspection results", "Unhandled row shapes"])
    for row in data["rows"]:
        f = record["findings"].get(row["id"])
        if bucket(row) == "judgement":
            section = "Judgement required"
        elif not f:
            section = "Unhandled row shapes"
        elif f["state"] == "unknown":
            section = "Unknown inspection results"
        else:
            section = "Observed components and missing local components"
        sections[section].append(row)
    for heading, rows in sections.items():
        lines += ["## " + heading + f" ({len(rows)})", ""]
        for row in sorted(rows, key=lambda r: (r["severity"], r["id"])):
            rid = row["id"]
            lines += [f"### {rid} · {row['severity']} · {row['failure']}", ""]
            f = record["findings"].get(rid)
            if f:
                lines += [f"**{f['state']}** — {f['reason']}", "", "Inspected: " + literal(f["how"]), ""]
                if f["evidence"]:
                    lines += ["Literal evidence:", "", literal(f["evidence"]), ""]
            else:
                lines += ["Requires a person's judgement; no question asked." if section == "Judgement required" else "Unsupported by the static scanner: this row's control or claim shape is not assessed.", ""]
            if judgement(row):
                lines += ["**Class C: this row stays open even when a partial component is present.**", ""]
            if rid in record["selfReport"]:
                lines += ["Self-reported (not detected): " + str(record["selfReport"][rid]["answer"]).lower() + ". No closure credit.", ""]
            lines += [record["nextAction"][rid], ""]
    lines += ["## Installing missing gates", "", "Review the row-specific prevention actions above, choose the enforcement surface and owner, then test a known-bad and a known-good before relying on a gate. Installing or changing controls is a separate consented fail-fix task. This run installed nothing.", "", "The reused web editorial maps are retained in the JSON as suggestions. They are not proof of coverage and must be reconciled with current row wording before installation.", ""]
    if record["readBudget"]["unavailable"]:
        lines += ["## Unavailable reads", "", literal("\n".join(record["readBudget"]["unavailable"])), ""]
    if record["readBudget"]["incompleteAudits"]:
        lines += ["## Incomplete audits", "", "A command below ran out of the scanner's time budget, so the rows depending on it are unknown for that reason and not because of anything observed in this repository. Counts from this run are not comparable with a run where every audit finished.", "", literal("\n".join(record["readBudget"]["incompleteAudits"])), ""]
    return "\n".join(lines)


def established(record, data):
    """Rows for which the static scan produced a usable configuration result."""
    return [(row, record["findings"][row["id"]]) for row in data["rows"]
            if row["id"] in record["findings"]
            and record["findings"][row["id"]]["state"] in ("present", "absent")]


def stage2_controls(record):
    """Every wired control is a concrete Stage 2 test candidate, never proof it works."""
    return record.get("controlMap", {}).get("entries", [])


def count_label(count, singular, plural=None):
    return str(count) + " " + (singular if count == 1 else (plural or singular + "s"))


RECOMMENDATIONS_PER_PAGE = 3

REGISTER_LINKS = {
    "IL": ("Instruction register", "https://github.com/Scale100/false-floors/blob/main/registers/instruction-layer.md"),
    "CL": ("Context register", "https://github.com/Scale100/false-floors/blob/main/registers/context-layer.md"),
    "AL": ("Authority register", "https://github.com/Scale100/false-floors/blob/main/registers/authority-access-layer.md"),
    "RL": ("Recovery register", "https://github.com/Scale100/false-floors/blob/main/registers/recovery-layer.md"),
    "PL": ("Provenance register", "https://github.com/Scale100/false-floors/blob/main/registers/provenance-layer.md"),
    "TL": ("Truth register", "https://github.com/Scale100/false-floors/blob/main/registers/truth-layer.md"),
}

TOOL_GUIDES = {
    "Claude Code": ("Claude Code permissions", "https://code.claude.com/docs/en/permissions"),
    "Rule file": ("Claude Code rules", "https://code.claude.com/docs/en/memory#organize-rules-with-claude-rules"),
}

# The public report translates catalogue rows into improvements a non-specialist can
# recognise and act on. The row still supplies ordering and provenance, but is no
# longer the visible organising unit.
IMPROVEMENT_COPY = {
    "CL-1D": {
        "title": "Canonical files",
        "explanation": "Sometimes your agent follows an outdated rule instead of one you changed yesterday. For example, you might change your calendar rule from meetings until 5pm to no meetings after 3pm on Friday, but an older file still says 5pm. When both copies are available, the agent has no reliable way to know which one is current. The fix is to choose one canonical file and make every older copy point back to it.",
        "whatToDo": "The next time your agent follows an outdated rule, ask which file the rule came from and whether another copy exists. If there is more than one, choose the current file as canonical and ask the agent to add a `supersedes` or source pointer to every older copy.",
    },
    "IL-1D": {
        "title": "Rule precedence",
        "explanation": "Sometimes two rules are both current but point in different directions. For example, one rule says to refund any unhappy customer immediately, while another says refunds over $100 need your approval. When a customer asks for a $250 refund, the agent needs an explicit way to know that the approval rule wins. The fix is to add a precedence section to the rule set.",
        "whatToDo": "The next time your agent follows the wrong rule, ask whether the rule set has a precedence section. If it does not, ask the agent to add one that says which rule wins, then test the same conflicting request again.",
    },
    "AL-1B": {
        "title": "Enforced boundaries",
        "explanation": "Sometimes an instruction says “do not touch production”, but the agent still has permission to change it. For example, the prompt may tell the agent never to edit the production database while its account still has the credentials and write access to do exactly that. One mistaken command can still change live customer data. The fix is to enforce the boundary somewhere the agent cannot change.",
        "whatToDo": "Ask where each sensitive restriction is enforced. If the answer is only “in the prompt”, move it to a Claude Code permission deny or an externally managed hook, then test one forbidden action and one allowed action.",
    },
    "AL-5B": {
        "title": "Restricted subagents",
        "explanation": "Sometimes a small delegated task receives all the tools and file access of the main agent. That means a research or review subagent may be able to edit files, run commands or reach data it never needed. The fix is to give each subagent only the access required for its brief.",
        "whatToDo": "Before delegating a task, ask what tools and files the subagent actually needs. Give it an explicit narrower allowlist stored beyond its write access, then check that one excluded tool is refused.",
    },
    "AL-4C": {
        "title": "Read-only reviews",
        "explanation": "Sometimes you ask an agent to review or report on something and it changes the repository while investigating. The words “review only” express your intention, but they do not prevent a write. The fix is to make review tasks technically read-only.",
        "whatToDo": "For the next review task, deny edit and write tools before it starts. Ask the agent to attempt one harmless test write and confirm the runtime refuses it before relying on the review boundary.",
    },
    "CL-4D": {
        "title": "Project-scoped context",
        "explanation": "Sometimes rules, names or assumptions from one project appear in work for another. This happens when shared context is available everywhere instead of only where it belongs. The fix is to keep project-specific context inside that project's directory scope.",
        "whatToDo": "When your agent brings the wrong project's context into an answer, ask which context file supplied it and where that file applies. Move project-specific context into a directory-scoped rule file, then test one request inside the project and one outside it.",
    },
    "IL-2B": {
        "title": "Rules in the right scope",
        "explanation": "Sometimes the right rule exists but the agent does not apply it to the file being changed. The rule may live too high, too low or in a different directory, so it is invisible where the work happens. The fix is to put the rule in the scope it is meant to govern.",
        "whatToDo": "When a rule is ignored, ask which directories it applies to and whether the affected file is inside that scope. Move or copy the rule to the correct directory scope, then test one file inside the boundary and one outside it.",
    },
    "RL-1D": {
        "title": "Complete restore points",
        "explanation": "Sometimes a restore brings back the files but not the working system. Database state, generated assets, credentials or external settings may still be missing. The fix is to define what a complete restore point must contain for each system.",
        "whatToDo": "Ask what the current restore point covers besides files. Add every required data store and external setting to its declared scope, run one restore drill, and record anything that did not come back.",
    },
    "RL-3D": {
        "title": "Incremental saves",
        "explanation": "Sometimes a long task is interrupted and all useful progress disappears because it existed only in the conversation. Saving once at the end makes every earlier step fragile. The fix is to write durable checkpoints as the work proceeds.",
        "whatToDo": "For the next long task, ask the agent to save each completed section or batch to disk. Interrupt a test run after one checkpoint and confirm that the completed work is still available.",
    },
    "CL-4E": {
        "title": "Claims with caveats",
        "explanation": "Sometimes a tentative or conditional finding is copied into another document and starts to look like a settled fact. The caveat was separate from the claim, so it was lost in transit. The fix is to make verification status travel with the claim.",
        "whatToDo": "The next time the agent records an uncertain finding, ask it to store the verification status or caveat in the same structured record. Copy the claim into a derived view and check that the qualifier comes with it.",
    },
    "RL-2A": {
        "title": "Bounded workspaces",
        "explanation": "Sometimes an agent working on one repository can also change files elsewhere on the machine. A prompt can ask it to stay inside the project, but the operating system still permits the wider write. The fix is to bound the writable workspace before the task starts.",
        "whatToDo": "Run the agent inside a sandbox, container or worktree boundary that permits writes only to the intended workspace. Test one write inside the boundary and one outside it, and confirm the outside write is refused.",
    },
}


def improvement(row):
    return IMPROVEMENT_COPY.get(row["id"], {
        "title": " ".join((row.get("prevention") or row["failure"]).split()),
        "explanation": " ".join((row.get("showsUpAs") or row["failure"]).split()).strip("\"“”") + ".",
        "whatToDo": ("Add this supported pattern to the named control surface: "
                     + " ".join((row.get("mechanism") or row.get("prevention")
                                  or "review the catalogue entry").split())
                     + ". Verify it with one known-bad and one known-good example before relying on it."),
    })


def recommendation_references(row, markdown=True):
    references = []
    tool = tool_name(row)
    if tool in TOOL_GUIDES:
        label, url = TOOL_GUIDES[tool]
        references.append((label, url))
    register = REGISTER_LINKS.get(row["id"].split("-", 1)[0])
    if register:
        label, url = register
        references.append(("False Floors " + label, url))
    if markdown:
        return ", ".join("[" + label + "](" + url + ")" for label, url in references)
    return ", ".join(label + ": " + url for label, url in references)


def recommendation_lines(record, absent, page=1, markdown=True):
    """Render one deterministic page without pretending configuration is behavioral proof."""
    ordered = sorted(absent, key=lambda item: (item[0]["severity"], item[0]["id"]))
    start = (page - 1) * RECOMMENDATIONS_PER_PAGE
    selected = ordered[start:start + RECOMMENDATIONS_PER_PAGE]
    lines = []
    for offset, (row, _) in enumerate(selected, start=start + 1):
        copy = improvement(row)
        references = recommendation_references(row, markdown=markdown)
        if markdown:
            lines += ["### " + str(offset) + ". " + copy["title"], "",
                      copy["explanation"], "",
                      "**What to do:** " + copy["whatToDo"], "",
                      "**Read more:** " + references + ".", ""]
        else:
            lines += [str(offset) + ". " + copy["title"], "",
                      copy["explanation"], "",
                      "What to do: " + copy["whatToDo"], "",
                      "Read more: " + references, ""]
    return lines, len(ordered), start, len(selected)


def recommendation_page_text(record, data, page):
    absent = [(row, finding) for row, finding in established(record, data)
              if finding["state"] == "absent"]
    lines, total, start, shown = recommendation_lines(record, absent, page=page, markdown=False)
    if not shown:
        return "No recommendations remain on page " + str(page) + ". " + str(total) + " available in total.\n"
    end = start + shown
    header = "Recommendations " + str(start + 1) + "–" + str(end) + " of " + str(total)
    remaining = total - end
    if remaining:
        lines += ["", str(remaining) + " more available. Ask for the next three recommendations."]
    return header + "\n\n" + "\n".join(lines) + "\n"


def render_stage1(record, data):
    """The v2 public report: established static results and a route to Stage 2."""
    results = established(record, data)
    present = [(row, finding) for row, finding in results if finding["state"] == "present"]
    absent = [(row, finding) for row, finding in results if finding["state"] == "absent"]
    controls = stage2_controls(record)
    lines = [
        "---", "type: assessment", "status: static-inventory", "tool-version: " + TOOL_VERSION,
        "date: " + record["date"], "catalogue-version: " + record["catalogueVersion"], "---", "",
        "# False Floors trust check — Stage 1", "",
        "This report contains only configuration results the static scan could establish.", "",
        "Stage 1 does not test whether a control fires against a real failure. The wired controls "
        "found here form the queue for Stage 2 testing. Our Stage 2 tool is due for release on 20 September.", "",
        "## Result", "",
        "- Static configuration checks completed: " + str(len(results)),
        "- Supported components found: " + str(len(present)),
        "- Supported configuration patterns not found: " + str(len(absent)),
        "- Controls identified for Stage 2 testing: " + str(len(controls)), "",
        "## Summary", "",
        "The scan found " + count_label(len(present), "supported component")
        + " visibly configured, while " + count_label(len(absent), "configuration pattern")
        + " the scanner knows how to recognise " + ("was" if len(absent) == 1 else "were")
        + " not found. This is a view of configuration coverage, not whether the checks work. The "
        + count_label(len(controls), "wired control") + " identified here "
        + ("is" if len(controls) == 1 else "are") + " queued for Stage 2 testing.", "",
    ]
    recommendation_block, total_recommendations, _, shown_recommendations = recommendation_lines(record, absent)
    lines += ["## Recommended next steps", ""]
    if shown_recommendations:
        recommendation_intro = ("Here are three improvements" if shown_recommendations == 3
                                else ("Here is one improvement" if shown_recommendations == 1
                                      else "Here are two improvements"))
        lines += [recommendation_intro + " you can add to your agent to make it more reliable.", ""]
        lines += recommendation_block
    else:
        lines += ["No supported configuration improvement was identified from this Stage 1 scan.", ""]
    lines += ["Catalogue: " + record["catalogueVersion"] + ". " + record["privacy"], ""]
    if record["manifest"].get("error"):
        lines += ["## Repository bindings", "",
                  "The repository binding file could not be used: " + record["manifest"]["error"]
                  + ". Repair it before relying on a complete static inventory.", ""]
    lines += ["## Supported components found (" + str(len(present)) + ")", ""]
    if not present:
        lines += ["No supported component was established as configured in this run.", ""]
    for row, finding in sorted(present, key=lambda item: (item[0]["severity"], item[0]["id"])):
        authority = "confirmed" if finding.get("manifest") else "verified"
        scope = ("Partial component only; this Class C row remains open."
                 if judgement(row) else "Installed/configured component only; effectiveness is not tested here.")
        lines += ["- **" + row["id"] + " · " + row["severity"] + " · " + row["failure"] + "**",
                  "  - **Status:** " + authority + " — " + finding["reason"],
                  "  - **Scope:** " + scope,
                  "  - **Inspected:** " + inline_literal(finding["how"]),
                  "  - **Evidence:** " + (inline_literal(finding["evidence"])
                                          if finding["evidence"] else "None recorded."), ""]
    surface_counts = collections.Counter((entry.get("surface") or "unclassified") for entry in controls)
    lines += ["## Stage 2 testing (" + str(len(controls)) + " controls identified)", ""]
    if controls:
        lines += [str(len(controls)) + " wired controls were identified for Stage 2 testing. Stage 2 will determine "
                  "which can be exercised automatically and which need a guided or CI-based test. Being listed here "
                  "does not credit a control as working.", "",
                  "The complete testing queue is in `false-floors-assessment.json` at `.controlMap`.", ""]
        lines += ["- " + surface + ": " + str(count) for surface, count in sorted(surface_counts.items())] + [""]
    else:
        lines += ["No wired controls were identified for the Stage 2 testing queue in this run.", ""]
    if record["readBudget"]["incompleteAudits"]:
        lines += ["## Incomplete audits", "",
                  "A scanner audit ran out of its time budget. Results depending on it were excluded from this Stage 1 report.", "",
                  literal("\n".join(record["readBudget"]["incompleteAudits"])), ""]
    improvement_phrase = ("this improvement" if shown_recommendations == 1
                          else ("these two improvements" if shown_recommendations == 2
                                else "these three improvements"))
    if shown_recommendations and total_recommendations > shown_recommendations:
        next_action = ("After you have implemented " + improvement_phrase
                       + ", rerun the trust check and ask for the next three recommendations for the remaining "
                       + str(total_recommendations - shown_recommendations) + ".")
    elif shown_recommendations:
        next_action = ("After you have implemented " + improvement_phrase
                       + ", rerun the trust check to see whether the configuration result changed.")
    else:
        next_action = "Keep this assessment and rerun the trust check after the repository configuration changes."
    incident_action = ("If you see one of these failures, paste the example into this session"
                       if shown_recommendations else
                       "If you see an agent failure you want help with, paste what happened into this session")
    next_text = (next_action + " " + incident_action + " and ask: “Which False Floors failure is this, and what should I change?” "
                 + "No score, badge, certification or claim of runtime effectiveness is produced.")
    lines += ["## Next", "", next_text, ""]
    return "\n".join(lines)


def render(record, data, full=False):
    return render_full(record, data) if full else render_stage1(record, data)


# The terminal is the product (D-272). It is hard capped because a person reading a scan
# result in a shell reads the first screen and nothing else. Complete evidence remains in JSON.
TERMINAL_MAX = 3000
TERMINAL_CONTROLS = 6
TERMINAL_RECOMMENDATIONS = 3


def install_line(row):
    """One available response, in the catalogue's own words rather than a paraphrase."""
    return " ".join((row.get("prevention") or row.get("mechanism") or "Review this row with a person.").split())


def tool_name(row):
    """The catalogue's own tool for this row's mechanism, or empty for Class C."""
    name = " ".join((row.get("tool") or "").split())
    return "" if name.lower() in ("", "none") else name


def tool_tag(row):
    """Where the response lives, prefixed so a result line says what to open."""
    name = tool_name(row)
    return "[" + name[:12] + "] " if name else ""


def terminal_report(inv, record, data, seconds):
    """The v2 first-screen report: established static results, then the Stage 2 queue."""
    rows = {r["id"]: r for r in data["rows"]}
    findings = record["findings"]
    control_map = record["controlMap"]
    installed = module("detectors").manifest(inv).installed
    established_ids = [rid for rid, f in findings.items() if f["state"] in ("present", "absent")]
    credited = sorted((rid for rid in established_ids if findings[rid]["state"] == "present"),
                      key=lambda rid: (rows[rid]["severity"], rid))
    not_found = sorted((rid for rid in established_ids if findings[rid]["state"] == "absent"),
                       key=lambda rid: (rows[rid]["severity"], rid))
    controls = stage2_controls(record)
    out = ["False Floors trust check v" + TOOL_VERSION + " - " + Path(record["environment"]).name,
           "Catalogue " + record["catalogueVersion"] + " - " + str(len(established_ids))
           + " static configuration checks completed - " + str(len(credited))
           + " supported components found, " + str(len(not_found)) + " patterns not found - "
           + str(seconds) + "s", "",
           "STATIC RESULTS (" + str(len(established_ids)) + " established)"]
    if not established_ids:
        out.append("  No static configuration result could be established in this run.")
    for rid in credited[:TERMINAL_CONTROLS]:
        f = findings[rid]
        authority = "confirmed" if f.get("manifest") else "verified"
        where = (f.get("how") or "").split(" -> ")[-1]
        label = authority + (" partial" if judgement(rows[rid]) else "")
        out.append("  " + label.ljust(16) + " " + rid.ljust(6) + " " + where[:36].ljust(36)
                   + " " + " ".join(rows[rid]["failure"].split())[:52])
        receipt = installed.get(rid)
        if receipt:
            out.append("            installed " + str(receipt.get("on", "?")) + " - "
                       + module("install").receipt_state(inv.root, receipt))
    if len(credited) > TERMINAL_CONTROLS:
        out.append("  + " + str(len(credited) - TERMINAL_CONTROLS) + " more in the report.")
    for rid, receipt in sorted(installed.items()):
        if rid in credited[:TERMINAL_CONTROLS]:
            continue
        out.append("  installed " + rid.ljust(6) + " " + str(receipt.get("on", "?")) + " - "
                   + module("install").receipt_state(inv.root, receipt))
    if not_found:
        out += ["", "RECOMMENDED NEXT STEPS (" + str(min(len(not_found), TERMINAL_RECOMMENDATIONS))
                + " of " + str(len(not_found)) + " shown)"]
    for index, rid in enumerate(not_found[:TERMINAL_RECOMMENDATIONS], start=1):
        out.append("  " + str(index) + ". " + improvement(rows[rid])["title"][:74])
    if len(not_found) > TERMINAL_RECOMMENDATIONS:
        out.append("  Instructions and links: " + record["readBudget"].get("reportPath", NAMES[1]))
    out += ["", "STAGE 2 TESTING (" + str(len(controls)) + " controls identified)"]
    if controls:
        out += ["  " + str(len(controls)) + " wired controls identified for Stage 2 testing.",
                "  Stage 2 will determine which can run automatically and which need a",
                "  guided or CI-based test. Listing a control does not prove it works.",
                "  Testing queue: " + NAMES[0] + " at .controlMap"]
    else:
        out.append("  No wired controls were identified for the Stage 2 queue.")
    out += ["", "OPTIONAL CLASSIFICATION",
            "  --propose FILE   verify proposed row bindings; writes nothing",
            "  --confirm FILE   accept verified bindings into " + module("detectors").MANIFEST,
            "  --install ROW    install a supported gate with its known-bad self-test",
            "  No score, badge or certification is produced. Report: " + record["readBudget"].get("reportPath", NAMES[1])]
    if record["readBudget"].get("incompleteAudits"):
        out.append("  An audit ran out of budget; dependent results were excluded from Stage 1.")
    if not_found:
        remaining = max(0, len(not_found) - TERMINAL_RECOMMENDATIONS)
        out += ["", "NEXT",
                "  Implement the first three improvements, rerun the trust check, then ask for",
                "  the next three recommendations" + (" for the remaining " + str(remaining) if remaining else "") + "."]
    text = "\n".join(out) + "\n"
    if len(text) > TERMINAL_MAX:
        # A cap that silently drops the confirm step would be worse than a long report, so
        # the overrun is stated rather than trimmed from the bottom.
        text = text[:TERMINAL_MAX] + "\n[output truncated at " + str(TERMINAL_MAX) + " characters; the full record is the JSON]\n"
    return text


MAX_PROPOSALS = 40


def read_proposals(path, control_map):
    """Load a reading seat's proposals. Treated as untrusted data throughout.

    The file is written by a model, so nothing in it is followed as an instruction and every
    field is checked: the row must be a plain ID, the control must be one the map actually
    carries, and the path is taken from the map rather than from the proposal, so a proposal
    can never name a file the scanner did not find wired.
    """
    raw = Path(path).read_bytes()
    if len(raw) > MAX_FILE:
        raise ValueError("Proposals file exceeds the read budget")
    doc = json.loads(raw.decode("utf-8"))
    if not isinstance(doc, dict) or not isinstance(doc.get("proposals"), list):
        raise ValueError('Proposals file must be {"proposals": [ ... ]}')
    entries = {e["id"]: e for e in control_map["entries"]}
    bindings, notes, accepted = collections.defaultdict(list), [], []
    for item in doc["proposals"][:MAX_PROPOSALS]:
        if not isinstance(item, dict):
            notes.append("A proposal that is not an object was ignored.")
            continue
        rid, cid = item.get("row"), item.get("controlId")
        if not isinstance(rid, str) or not re.fullmatch(r"[A-Z]{2}-[0-9]{1,2}[A-Z]?", rid):
            notes.append("Ignored a proposal whose row is not a catalogue ID: " + json.dumps(rid)[:40] + ".")
            continue
        entry = entries.get(cid)
        if entry is None:
            notes.append("Ignored a proposal for a control this scan did not find wired: " + json.dumps(cid)[:80] + ".")
            continue
        if not entry.get("path"):
            notes.append("Ignored a proposal for " + rid + ": that control has no file in this repository to bind.")
            continue
        if entry["path"] not in bindings[rid]:
            bindings[rid].append(entry["path"])
        accepted.append({"row": rid, "controlId": cid, "path": entry["path"],
                         "confidence": str(item.get("confidence", ""))[:10],
                         "evidence": str(item.get("evidence", ""))[:200],
                         "reason": str(item.get("reason", ""))[:200]})
    if len(doc["proposals"]) > MAX_PROPOSALS:
        notes.append("Only the first " + str(MAX_PROPOSALS) + " proposals were read.")
    return dict(bindings), accepted, notes


def proposal_report(outcomes, accepted, notes, confirmed=None):
    """What each proposal would do, or did. Text, because this is the confirm step."""
    verified = [o for o in outcomes.values() if o["verified"]]
    refused = [o for o in outcomes.values() if not o["verified"]]
    by_row = {a["row"]: a for a in accepted}
    out = ["Proposed bindings: " + str(len(outcomes)) + " rows, " + str(len(verified))
           + " the scanner can verify, " + str(len(refused)) + " it refuses.", ""]
    if verified:
        out.append("WOULD BE CREDITED" if confirmed is None else "CONFIRMED AND WRITTEN")
        for o in sorted(verified, key=lambda x: x["row"]):
            out.append("  " + o["row"].ljust(6) + " " + ", ".join(o["paths"])[:60])
            note = by_row.get(o["row"], {})
            if note.get("evidence"):
                out.append("         evidence the seat quoted: " + " ".join(note["evidence"].split())[:90])
        out.append("")
    if refused:
        out.append("REFUSED (no credit; the reason is the scanner's, not the seat's)")
        for o in sorted(refused, key=lambda x: x["row"]):
            out.append("  " + o["row"].ljust(6) + " " + " ".join(o["reason"].split())[:110])
        out.append("")
    for note in notes:
        out.append("  note: " + note)
    if confirmed is None:
        out += ["", "Nothing was written. Rerun with --confirm to accept the verified bindings;",
                "the tool writes " + module("detectors").MANIFEST + " and the next scan reports them as confirmed."]
    else:
        out += ["", "Written to " + module("detectors").MANIFEST + ". Run the scan again to see them credited as confirmed."]
    return "\n".join(out) + "\n"


def install_gate(inv, data, specs, row):
    """Install one gate for one row, then say what its self-test found.

    An installed control is not a working one, so nothing here reports an install on its own.
    The library runs the guard's own known-bad self-test, the outcome and the guard's digest go
    into the repository's manifest, and the next scan repeats the self-test result only while
    the digest still matches the file that was tested.
    """
    rows = {r["id"]: r for r in data["rows"]}
    if row not in rows:
        raise ValueError("No catalogue row with that ID. Run --rows to see a row's text.")
    installer = module("install")
    receipt = installer.install(inv.root, row)
    if not receipt["installed"]:
        print("Not installed: " + receipt["reason"])
        return 1
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    module("detectors").write_install_receipt(inv, row, receipt, today)
    outcome = receipt["selfTest"]
    out = ["Installed a gate for " + row + " - " + " ".join(rows[row]["failure"].split()),
           "  " + receipt["path"] + " on " + receipt["surface"] + ": " + receipt["what"], ""]
    out += ["  " + note for note in receipt["notes"]]
    out += ["", "SELF-TEST: " + ("PASSED - it refused its known-bad and allowed its known-good"
                                 if outcome["passed"] else "FAILED - do not rely on this gate"),
            "  " + outcome["detail"][:200], "",
            "The gate is wired and its self-test has been run once, on the bytes now on disk.",
            "The next scan repeats that result only while those bytes are unchanged, and says so",
            "if they are not. Installation on its own is never reported as coverage.",
            "", "Fill in any list the gate needs, then run the scan again."]
    print("\n".join(out))
    return 0 if outcome["passed"] else 1


def compact_summary(record, data, previous, inv, started):
    """Machine-readable v2 summary; unresolved catalogue observations remain in the full record."""
    results = established(record, data)
    states = collections.Counter(f["state"] for _, f in results)
    return {"toolVersion": TOOL_VERSION, "catalogueVersion": data["catalogueVersion"],
            "staticResults": {"completed": len(results), "componentsFound": states["present"],
                              "configurationPatternsNotFound": states["absent"]},
            "stage2ControlsIdentified": len(stage2_controls(record)),
            "scopeNote": "Static configuration results only; runtime effectiveness is a separate Stage 2 test.",
            "incompleteAudits": record["readBudget"]["incompleteAudits"],
            "freshness": record["freshness"], "priorDiff": previous["status"],
            "optionalQuestions": len(record["questions"]), "outputs": [str(inv.root / n) for n in NAMES],
            "validation": "pass", "seconds": round(time.perf_counter() - started, 3),
            "bytesRead": inv.bytes, "privacy": record["privacy"]}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--questions", action="store_true", help="Inspect and emit only optional questions; write nothing")
    ap.add_argument("--answers", default="{}", help="Small inline JSON object of question-id: boolean")
    ap.add_argument("--rows", help="Comma-separated catalogue IDs; read-only selective projection")
    ap.add_argument("--source-root", type=Path, help="Trusted catalogue source checkout for existing diff history; never target code")
    ap.add_argument("--allow-github", metavar="OWNER/REPO", help="Explicit consent to read-only GitHub policy queries; sends repository identity and gh authentication")
    ap.add_argument("--github-branch", help="Exact branch to inspect with --allow-github")
    ap.add_argument("--json-summary", action="store_true", help="Print the machine-readable summary instead of the terminal report")
    ap.add_argument("--full", action="store_true", help="Write the exhaustive maintainer report, including unresolved and out-of-scope catalogue rows")
    ap.add_argument("--recommendations-page", type=int, help="Print one read-only page of three recommendations; page 1 is in the default report")
    ap.add_argument("--propose", metavar="FILE", help="A reading seat's proposed row bindings; verified and reported, nothing written")
    ap.add_argument("--confirm", metavar="FILE", help="The same file, accepted by the owner; verified again and the verified bindings written to the manifest")
    ap.add_argument("--install", metavar="ROW", help="Install a gate for one catalogue row, together with its known-bad self-test")
    args = ap.parse_args()
    if args.recommendations_page is not None and args.recommendations_page < 1:
        raise ValueError("Recommendation page must be 1 or greater")
    if args.allow_github and (args.offline or not args.github_branch):
        raise ValueError("GitHub opt-in requires --github-branch and cannot be used with --offline")
    started = time.perf_counter()
    data, specs, editorial, counts = load_assets()
    if args.rows:
        ids = set(args.rows.split(","))
        selected = [{k: r[k] for k in ("id", "severity", "failure", "prevention", "mechanism", "outcome")} for r in data["rows"] if r["id"] in ids]
        if ids != {r["id"] for r in selected} or len(ids) > 12:
            raise ValueError("Request 1–12 known row IDs per projection")
        print(json.dumps(selected, ensure_ascii=False))
        return 0
    inv = Inventory(args.repo)
    top = inv.git("rev-parse", "--show-toplevel")
    # limit is set only on a timeout, so a Git that never answered is named as that
    # rather than reported as the operator having pointed at a non-repository.
    if top.limit:
        raise ValueError(top.command + ": did not complete within the scanner's " + str(top.limit)
                         + " s Git budget, so the repository root was never established and nothing was inspected")
    if top.code or Path(top.out).resolve() != inv.root:
        raise ValueError("--repo must be an existing Git repository root")
    if args.allow_github:
        remote = inv.git("remote", "get-url", "origin")
        match = re.fullmatch(r"(?:https://github\.com/|git@github\.com:)([^/]+/[^/]+?)(?:\.git)?", remote.out)
        if remote.code or not match or match[1].lower() != args.allow_github.lower():
            raise ValueError("GitHub policy scope must match this repository's GitHub origin before any API request")
        inv.github_policy = module("detectors").fetch_policy(args.allow_github, args.github_branch)
    if args.questions:
        fs = {rid: detect(inv, rid, spec) for rid, spec in specs.items()}
        print(json.dumps(questions(data, editorial, fs), ensure_ascii=False))
        return 0
    if args.propose or args.confirm:
        # A seat proposes and never credits (D-272). This mode exists so the credit decision
        # is taken by the script and the acceptance by a person, in two separate steps that
        # cannot be collapsed: --propose writes nothing at all, and --confirm writes only
        # what verification has just re-established.
        if args.propose and args.confirm:
            raise ValueError("Propose and confirm are two steps; run --propose first, then --confirm on the same file")
        detectors = module("detectors")
        findings = {rid: detect(inv, rid, spec) for rid, spec in specs.items()}
        control_map = detectors.control_map(inv, findings)
        bindings, accepted, notes = read_proposals(args.propose or args.confirm, control_map)
        if not bindings:
            print("No proposal in that file could be bound to a control this scan found wired.\n"
                  + "".join("  note: " + n + "\n" for n in notes), end="")
            return 0
        outcomes = detectors.verify_bindings(inv, specs, bindings)
        written = None
        if args.confirm:
            confirmed = {rid: o["paths"] for rid, o in outcomes.items() if o["verified"]}
            if not confirmed:
                print(proposal_report(outcomes, accepted, notes + ["Nothing verified, so nothing was written."]), end="")
                return 0
            written = detectors.write_manifest(inv, confirmed, dt.datetime.now(dt.timezone.utc).date().isoformat())
        print(proposal_report(outcomes, accepted, notes, written), end="")
        return 0
    if args.install:
        return install_gate(inv, data, specs, args.install)
    for name in NAMES:
        p = inv.root / name
        if p.is_symlink() or (p.exists() and (not p.is_file() or p.stat().st_nlink != 1)):
            raise ValueError("Refusing non-regular output: " + name)
    prior_text = inv.read(NAMES[0])
    prior = None
    if prior_text is not None:
        try:
            prior = json.loads(prior_text)
        except ValueError:
            raise ValueError("Prior assessment is invalid JSON; preserve and resolve it before replacing outputs")
    elif (inv.root / NAMES[0]).exists():
        raise ValueError("Prior assessment could not be read; outputs preserved")
    previous = catalogue_diff(prior, data, args.source_root)
    record = make_record(inv, data, specs, editorial, counts, freshness(data["catalogueVersion"], args.offline), previous, json.loads(args.answers))
    if args.recommendations_page is not None:
        print(recommendation_page_text(record, data, args.recommendations_page), end="")
        return 0
    doc = render(record, data, full=args.full)
    # Generate and validate both payloads before opening either destination.
    payload = json.dumps(record, ensure_ascii=False, indent=2) + "\n"
    for name, text in zip(NAMES, (payload, doc)):
        flags = os.O_WRONLY | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
        with os.fdopen(os.open(inv.root / name, flags, 0o600), "w", encoding="utf-8") as f:
            info = os.fstat(f.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise ValueError("Output changed to an unsafe file: " + name)
            os.ftruncate(f.fileno(), 0)
            f.write(text)
    if args.json_summary:
        print(json.dumps(compact_summary(record, data, previous, inv, started), ensure_ascii=False))
    else:
        print(terminal_report(inv, record, data, round(time.perf_counter() - started, 3)), end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, TypeError) as error:
        print("trust-check: " + str(error), file=sys.stderr)
        raise SystemExit(1)

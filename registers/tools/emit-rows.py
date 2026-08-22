#!/usr/bin/env python3
"""Emit the register projection that each current Figma frame is meant to show.

The markdown parser lives in check-registers.py.  This tool imports and reuses
its split_row and parse functions so table parsing has one implementation.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import pathlib
import re
import sys


# Importing check-registers.py must not leave binary __pycache__ files in this
# text-only vault.
sys.dont_write_bytecode = True


TOOLS = pathlib.Path(__file__).resolve().parent
REG = TOOLS.parent
BUILD = REG / "build"


def load_checker():
    path = TOOLS / "check-registers.py"
    spec = importlib.util.spec_from_file_location("check_registers", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = load_checker()

LAYER_FILES = {
    "instruction": "instruction-layer",
    "context": "context-layer",
    "authority-access": "authority-access-layer",
    "recovery": "recovery-layer",
    "provenance": "provenance-layer",
    "truth": "truth-layer",
}


def read_current_frames():
    """Read node IDs and row counts from the README's canonical register table."""
    lines = (REG / "README.md").read_text(encoding="utf-8").splitlines()
    header = None
    result = {}
    for line in lines:
        if line.startswith("| Register |"):
            header = CHECKER.split_row(line)
            continue
        if header is None or not line.startswith("| [["):
            continue
        cells = CHECKER.split_row(line)
        if len(cells) != len(header):
            raise RuntimeError(f"README register row has {len(cells)} cells: {line}")
        row = dict(zip(header, cells))
        match = re.fullmatch(r"\[\[([^]]+)\]\]", row["Register"])
        node = re.search(r"`([^`]+)`", row["Figma node"])
        if not match or not node:
            raise RuntimeError(f"cannot parse README register row: {line}")
        result[match.group(1)] = {
            "node_id": node.group(1),
            "row_count": int(row["Rows"]),
        }
    missing = set(LAYER_FILES.values()) - set(result)
    if missing:
        raise RuntimeError(f"README table is missing: {', '.join(sorted(missing))}")
    return result


def split_action(value):
    parts = re.split(r"\s+[—–]\s+", value, maxsplit=1)
    if len(parts) != 2:
        raise RuntimeError(f"next action has no dash separator: {value}")
    return parts[0].strip(), parts[1].strip()


def action_type(cadence, action=""):
    upper = cadence.upper()
    if upper.startswith("DONE") and "manual" in action.lower():
        # IL-1F is marked done for the installed gate, while its exporter run
        # remains a manual interval ritual; the frame correctly stays amber.
        return "interval"
    if upper == "ONCE" or upper.startswith("DONE"):
        return "once"
    if upper.startswith("EVERY "):
        return "every_time"
    return "interval"


def tool_parts(value):
    parts = [part.strip() for part in value.split("·")]
    if len(parts) not in {3, 4}:
        raise RuntimeError(f"tool cell has an unsupported shape: {value}")
    return {
        "tool_name": parts[0],
        # Recovery deliberately omits the runtime sub-label and therefore has
        # name · tier · state rather than the four-part form used elsewhere.
        "runtime": " · ".join(parts[1:-2]) if len(parts) == 4 else None,
        "tool_tier": parts[-2].lower(),
        "built_state": parts[-1].lower(),
    }


def outcome(value):
    return value.split(" ", 1)[-1].strip().lower()


def row_register_projection(layer, rows):
    projected = []
    for row in rows:
        cadence, action = split_action(row["Next action"])
        item = {
            "id": row["ID"],
            "failure": row["Failure"],
            "symptom": row["Shows up as"],
            "catch": row["Catch"].lower(),
            "mechanism": row["Mechanism"],
            "outcome": outcome(row["Outcome"]),
            "cadence": cadence,
            "action": action,
            "action_type": action_type(cadence, action),
            "marker": tool_parts(row["Tool"])["built_state"] == "designed",
            **tool_parts(row["Tool"]),
        }
        if layer == "authority-access":
            item["authority"] = row["Authority"].lower()
            item["authority_encoding"] = (
                "unbypassable" if item["authority"] == "unbypassable"
                else "bypassable_or_none"
            )
        projected.append(item)
    return projected


def provenance_cell(value):
    if value.strip().lower() == "n/a":
        return {"state": "n/a", "text": "n/a"}
    parts = re.split(r"\s+[—–]\s+", value, maxsplit=1)
    if len(parts) != 2:
        raise RuntimeError(f"provenance cell has no state separator: {value}")
    return {"state": parts[0].lower(), "text": parts[1]}


def provenance_projection(rows):
    projected = []
    for row in rows:
        cadence, action = split_action(row["Next action"])
        projected.append({
            "id": row["ID"],
            "failure": row["What breaks"],
            "cost": row["What it costs"],
            "harness_gate": provenance_cell(row["Harness gate"]),
            "repo_artefact": provenance_cell(row["Repo artefact"]),
            "control_plane_check": provenance_cell(row["Control-plane check"]),
            "outcome": outcome(row["Outcome"]),
            "cadence": cadence,
            "action": action,
            "action_type": action_type(cadence, action),
        })
    return projected


def truth_classes(txt, sections):
    classes = []
    for section in sections:
        match = re.match(r"Class ([ABC])\s+·", section["title"])
        if not match:
            continue
        letter = match.group(1)
        block_match = re.search(
            rf"^## Class {letter}\s+·.*?\n(.*?)(?=^## |\Z)", txt, re.M | re.S
        )
        if not block_match:
            raise RuntimeError(f"truth class {letter} body not found")
        block = block_match.group(1)
        conversion = re.search(r"Conversion:\s+\*\*(.+?)\*\*", block)
        out = re.search(r"Outcome:\s+\*\*([a-z]+)\s+[—–]", block)
        next_action = re.search(
            r"Next action:\s*([^—–\n]+)\s+[—–]\s+(.+?)\.\s", block, re.S
        )
        if not conversion or not out or not next_action:
            raise RuntimeError(f"truth class {letter} projection text is incomplete")
        summary = " ".join(next_action.group(2).split())
        if ": " in summary:
            title, detail = summary.split(": ", 1)
        else:
            title, detail = summary, ""
        title = title[:1].upper() + title[1:]
        controls = []
        for row in section["rows"]:
            control = row["Control applied"]
            if control not in controls:
                controls.append(control)
        classes.append({
            "class": letter,
            "conversion": conversion.group(1)[:1].upper() + conversion.group(1)[1:],
            "outcome": out.group(1).lower(),
            "cadence": next_action.group(1).strip(),
            "action": title,
            "action_detail": detail,
            "action_type": action_type(next_action.group(1).strip(), summary),
            "shared_control": " · ".join(controls) if letter == "C" else None,
        })
    if [item["class"] for item in classes] != ["A", "B", "C"]:
        raise RuntimeError("truth register does not contain Class A, B and C in order")
    return classes


def truth_projection(sections):
    projected = []
    for section in sections:
        match = re.match(r"Class ([ABC])\s+·", section["title"])
        if not match:
            continue
        letter = match.group(1)
        for row in section["rows"]:
            status = row["Status"].lower()
            control_display = row["Control applied"]
            if letter != "C" and status in {"not built", "not provisioned"}:
                control_display = f"{control_display} · {status}"
            projected.append({
                "id": row["ID"],
                "class": letter,
                "severity": row["Sev"],
                "claim": row["Claim"],
                "cost": row["What it costs if it’s wrong"],
                "control_display": None if letter == "C" else control_display,
                "control_active": status == "in force",
            })
    return projected


def emit(layer, frames):
    source = LAYER_FILES[layer]
    fm, sections, txt = CHECKER.parse(source)
    rows = [row for section in sections for row in section["rows"]]
    current = frames[source]
    if len(rows) != current["row_count"]:
        raise RuntimeError(
            f"{layer}: README says {current['row_count']} rows, parser found {len(rows)}"
        )
    if layer in {"instruction", "context", "authority-access", "recovery"}:
        shape = "row-register"
        projected = row_register_projection(layer, rows)
        exclusions = ["prevention", "residual", "severity", "runtime"]
        classes = None
    elif layer == "provenance":
        shape = "provenance"
        projected = provenance_projection(rows)
        exclusions = ["residual", "severity"]
        classes = None
    else:
        shape = "truth"
        projected = truth_projection(sections)
        exclusions = ["residual", "status_raw"]
        classes = truth_classes(txt, sections)
    payload = {
        "schema_version": 1,
        "generated_on": dt.date.today().isoformat(),
        "layer": layer,
        "source": f"registers/{source}.md",
        "figma_file": fm.get("figma-file"),
        "figma_node": current["node_id"],
        "shape": shape,
        "row_count": len(projected),
        # D-057 removes prevention and severity from the views; D-061 keeps
        # residual canon-only. Runtime labels were removed in the same view pass.
        "declared_exclusions": exclusions,
        "rows": projected,
    }
    if classes is not None:
        payload["classes"] = classes
    BUILD.mkdir(parents=True, exist_ok=True)
    path = BUILD / f"{layer}.rows.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("layers", nargs="*", choices=sorted(LAYER_FILES))
    args = parser.parse_args()
    selected = args.layers or list(LAYER_FILES)
    frames = read_current_frames()
    for layer in selected:
        print(emit(layer, frames))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

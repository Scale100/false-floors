// Run this script through Figma use_figma, never as standalone JavaScript.
// Replace __LAYER__ with one key below. Node IDs and counts were re-read from
// registers/README.md on 2026-08-09 before this baseline was extracted.

const TARGET_LAYER = "__LAYER__";
const CONFIG = {
  instruction: { nodeId: "1358:139", rows: 23, shape: "row-register", prefix: "IL" },
  context: { nodeId: "1386:139", rows: 23, shape: "row-register", prefix: "CL" },
  "authority-access": {
    nodeId: "1379:139", rows: 23, shape: "row-register", prefix: "AL",
    // Canon and the live view both have 11 unbypassable rows. The continuation
    // prompt's number 9 is the designed-marker count, not the authority count.
    authorityGreen: 11,
  },
  recovery: { nodeId: "1389:139", rows: 25, shape: "row-register", prefix: "RL" },
  provenance: { nodeId: "1395:139", rows: 24, shape: "provenance", prefix: "PL" },
  truth: { nodeId: "1392:139", rows: 15, shape: "truth", prefix: "TL" },
};

const cfg = CONFIG[TARGET_LAYER];
if (!cfg) throw new Error(`unknown layer: ${TARGET_LAYER}`);

const page = figma.root.children.find((p) => p.name === "Pathways");
if (!page) throw new Error("Pathways page not found");
await figma.setCurrentPageAsync(page);
const frame = await figma.getNodeByIdAsync(cfg.nodeId);
if (!frame || !("findAllWithCriteria" in frame)) {
  throw new Error(`${TARGET_LAYER}: frame ${cfg.nodeId} not found or not a container`);
}

const texts = frame.findAllWithCriteria({ types: ["TEXT"] });
const rects = frame.findAllWithCriteria({ types: ["RECTANGLE"] });
const approx = (a, b, tolerance = 1) => Math.abs(a - b) < tolerance;
const numericFont = (node) => typeof node.fontSize === "number" ? node.fontSize : null;
const clean = (value) => value.replace(/\s+/g, " ").trim();
const hexPaint = (paints) => {
  if (!Array.isArray(paints) || !paints.length || paints[0].type !== "SOLID") return null;
  const c = paints[0].color;
  return "#" + [c.r, c.g, c.b]
    .map((v) => Math.round(v * 255).toString(16).padStart(2, "0")).join("");
};
const rectAt = (x, rowY) => rects.find(
  (r) => approx(r.x, x, 0.6) && r.y >= rowY - 2 && r.y < rowY + 2
);
const textAt = (band, x, fontSize = null) => {
  const matches = band.filter((t) => approx(t.x, x, 1.1) &&
    (fontSize === null || (numericFont(t) !== null && approx(numericFont(t), fontSize, 0.25))));
  if (matches.length !== 1) {
    throw new Error(`${TARGET_LAYER}: expected one TEXT at x=${x}, font=${fontSize}; got ${matches.length}`);
  }
  return matches[0];
};
const intersects = (a, b) =>
  a.x < b.x + b.width && a.x + a.width > b.x &&
  a.y < b.y + b.height && a.y + a.height > b.y;
const assertNoOverlaps = (id, nodes) => {
  for (let i = 0; i < nodes.length; i += 1) {
    for (let j = i + 1; j < nodes.length; j += 1) {
      if (intersects(nodes[i], nodes[j])) {
        throw new Error(`${TARGET_LAYER} ${id}: TEXT overlap ${nodes[i].name} / ${nodes[j].name}`);
      }
    }
  }
};
const assertColumn = (id, node, right) => {
  if (node.x + node.width > right + 0.6) {
    throw new Error(`${TARGET_LAYER} ${id}: ${node.name} exceeds column edge ${right}`);
  }
};
const actionTypeFromFill = (rect) => {
  const fill = hexPaint(rect.fills);
  const values = { "#f0fdf4": "once", "#fefce8": "interval", "#fef2f2": "every_time" };
  if (!values[fill]) throw new Error(`${TARGET_LAYER}: unknown action fill ${fill}`);
  return values[fill];
};

function extractRowRegister() {
  const labelPattern = new RegExp(`^${cfg.prefix}-\\d+[A-Z] · `);
  const labels = texts.filter((t) => approx(t.x, 530, 1.1) &&
    numericFont(t) !== null && approx(numericFont(t), 11.5, 0.25) &&
    labelPattern.test(t.characters)).sort((a, b) => a.y - b.y);
  if (labels.length !== cfg.rows) {
    throw new Error(`${TARGET_LAYER}: expected ${cfg.rows} row labels, got ${labels.length}`);
  }
  const extracted = labels.map((label) => {
    const id = label.characters.split(" · ")[0];
    const rowY = label.y - 12;
    const band = texts.filter((t) => t.y >= rowY - 2 && t.y < rowY + 44);
    const symptom = textAt(band, 90);
    const catchPoint = textAt(band, 960, 8);
    const toolName = textAt(band, 1100);
    const mechanism = textAt(band, 1240);
    const outcomeText = textAt(band, 1560);
    const cadence = textAt(band, 1710, 8);
    const action = band.find((t) => approx(t.x, 1710, 1.1) && numericFont(t) > 8.25);
    if (!action) throw new Error(`${TARGET_LAYER} ${id}: action text missing`);
    const toolChip = rectAt(1090, rowY);
    const mechanismCell = rectAt(1230, rowY);
    const outcomeChip = rectAt(1550, rowY);
    const actionCell = rectAt(1700, rowY);
    if (!mechanismCell || !outcomeChip || !actionCell) {
      throw new Error(`${TARGET_LAYER} ${id}: declared rectangle missing`);
    }
    const toolTier = !toolChip ? "process" :
      hexPaint(toolChip.fills) === "#111827" ? "automatic" : "maintained";
    const outcomeFill = hexPaint(outcomeChip.fills);
    const outcomeByFill = TARGET_LAYER === "recovery"
      ? { "#dcfce7": "prevented", "#fef9c3": "recoverable", "#fee2e2": "irreversible" }
      : { "#dcfce7": "prevented", "#fef9c3": "detected", "#fee2e2": "survives" };
    const decodedOutcome = outcomeByFill[outcomeFill];
    if (!decodedOutcome || decodedOutcome !== clean(outcomeText.characters).toLowerCase()) {
      throw new Error(`${TARGET_LAYER} ${id}: outcome text/fill disagree (${outcomeText.characters}/${outcomeFill})`);
    }
    const marker = !!rectAt(68, rowY);
    let authorityEncoding = null;
    if (TARGET_LAYER === "authority-access") {
      const fill = hexPaint(mechanismCell.fills);
      authorityEncoding = fill === "#f0fdf4" ? "unbypassable" :
        fill === "#fee2e2" ? "bypassable_or_none" : null;
      if (!authorityEncoding) throw new Error(`${id}: unknown authority mechanism fill ${fill}`);
    }
    const rowTexts = [symptom, label, catchPoint, toolName, mechanism, outcomeText, cadence, action];
    assertNoOverlaps(id, rowTexts);
    for (const node of rowTexts) {
      // D-059 lengthened IL-1F's mechanism; it is the one deliberate two-line
      // row-register value and remains inside its 40px cell without overlap.
      const deliberateTwoLine = id === "IL-1F" && node === mechanism && node.height <= 26.1;
      if (node.height > 20.1 && !deliberateTwoLine) {
        throw new Error(`${TARGET_LAYER} ${id}: ${node.name} wrapped to ${node.height}px`);
      }
    }
    [[symptom, 490], [label, 920], [catchPoint, 1090], [toolName, 1200],
     [mechanism, 1520], [outcomeText, 1670], [cadence, 2010], [action, 2010]]
      .forEach(([node, right]) => assertColumn(id, node, right));
    return {
      id,
      failure: clean(label.characters.slice(id.length + 3)),
      symptom: clean(symptom.characters),
      catch: clean(catchPoint.characters).toLowerCase(),
      tool_name: clean(toolName.characters),
      tool_tier: toolTier,
      mechanism: clean(mechanism.characters),
      outcome: decodedOutcome,
      cadence: clean(cadence.characters),
      action: clean(action.characters),
      action_type: actionTypeFromFill(actionCell),
      marker,
      ...(authorityEncoding ? { authority_encoding: authorityEncoding } : {}),
    };
  });
  if (TARGET_LAYER === "authority-access") {
    const greens = extracted.filter((row) => row.authority_encoding === "unbypassable").length;
    if (greens !== cfg.authorityGreen) {
      throw new Error(`authority-access: expected ${cfg.authorityGreen} green mechanism cells, got ${greens}`);
    }
  }
  return { rows: extracted };
}

function extractProvenance() {
  const labels = texts.filter((t) => approx(t.x, 90, 1.1) &&
    numericFont(t) !== null && approx(numericFont(t), 11, 0.25) &&
    /^PL-\d+[A-Z] · /.test(t.characters)).sort((a, b) => a.y - b.y);
  if (labels.length !== cfg.rows) {
    throw new Error(`provenance: expected ${cfg.rows} row labels, got ${labels.length}`);
  }
  const decodeCell = (id, band, rowY, rectX, textX) => {
    const node = textAt(band, textX);
    const rect = rectAt(rectX, rowY);
    const value = clean(node.characters);
    if (!rect) {
      if (value.toLowerCase() !== "n/a" || !node.name.startsWith("na_")) {
        throw new Error(`provenance ${id}: missing rectangle at x=${rectX} without an na_ text`);
      }
      return { state: "n/a", text: "n/a" };
    }
    if (value.toLowerCase() === "n/a") {
      throw new Error(`provenance ${id}: n/a text unexpectedly has a rectangle`);
    }
    const state = { "#dcfce7": "closes", "#fef9c3": "partial", "#fee2e2": "nothing" }[hexPaint(rect.fills)];
    if (!state) throw new Error(`provenance ${id}: unknown control fill ${hexPaint(rect.fills)}`);
    return { state, text: value };
  };
  return { rows: labels.map((label) => {
    const id = label.characters.split(" · ")[0];
    const rowY = label.y - 12;
    const band = texts.filter((t) => t.y >= rowY - 2 && t.y < rowY + 44);
    const cost = textAt(band, 430);
    const harnessText = textAt(band, 750);
    const repoText = textAt(band, 1020);
    const controlText = textAt(band, 1290);
    const outcomeText = textAt(band, 1560);
    const cadence = textAt(band, 1710, 8);
    const action = band.find((t) => approx(t.x, 1710, 1.1) && numericFont(t) > 8.25);
    const outcomeChip = rectAt(1550, rowY);
    const actionCell = rectAt(1700, rowY);
    if (!action || !outcomeChip || !actionCell) throw new Error(`provenance ${id}: declared field missing`);
    const outcomeByFill = { "#dcfce7": "prevented", "#fef9c3": "detected", "#fee2e2": "survives" };
    const decodedOutcome = outcomeByFill[hexPaint(outcomeChip.fills)];
    if (decodedOutcome !== clean(outcomeText.characters).toLowerCase()) {
      throw new Error(`provenance ${id}: outcome text/fill disagree`);
    }
    const rowTexts = [label, cost, harnessText, repoText, controlText, outcomeText, cadence, action];
    assertNoOverlaps(id, rowTexts);
    for (const node of rowTexts) {
      if (node.height > 20.1 && !(id === "PL-1A" && node === cost)) {
        throw new Error(`provenance ${id}: ${node.name} wrapped to ${node.height}px`);
      }
    }
    [[label, 390], [cost, 710], [harnessText, 980], [repoText, 1250],
     [controlText, 1520], [outcomeText, 1670], [cadence, 2010], [action, 2010]]
      .forEach(([node, right]) => assertColumn(id, node, right));
    return {
      id,
      failure: clean(label.characters.slice(id.length + 3)),
      cost: clean(cost.characters),
      harness_gate: decodeCell(id, band, rowY, 740, 750),
      repo_artefact: decodeCell(id, band, rowY, 1010, 1020),
      control_plane_check: decodeCell(id, band, rowY, 1280, 1290),
      outcome: decodedOutcome,
      cadence: clean(cadence.characters),
      action: clean(action.characters),
      action_type: actionTypeFromFill(actionCell),
    };
  }) };
}

function extractTruth() {
  const labels = texts.filter((t) => numericFont(t) !== null && approx(numericFont(t), 12, 0.25) &&
    /^TL-\d{2} · /.test(t.characters)).sort((a, b) => a.y - b.y);
  if (labels.length !== cfg.rows) {
    throw new Error(`truth: expected ${cfg.rows} claim labels, got ${labels.length}`);
  }
  const classOf = (id) => {
    const number = Number(id.slice(3));
    return number <= 3 ? "A" : number <= 10 ? "B" : "C";
  };
  const severityByFill = { "#fef08a": "S1", "#f59e0b": "S2", "#cc0000": "S3", "#7f1d1d": "S4" };
  const extractedRows = labels.map((label) => {
    const id = label.characters.split(" · ")[0];
    const letter = classOf(id);
    const rowY = label.y - 13;
    const band = texts.filter((t) => t.y >= rowY - 2 && t.y < rowY + 44);
    const cost = textAt(band, 428);
    const costCell = rectAt(418, rowY);
    const claimCell = rectAt(80, rowY);
    if (!costCell || !claimCell) throw new Error(`truth ${id}: claim or cost rectangle missing`);
    const severity = severityByFill[hexPaint(costCell.fills)];
    if (!severity) throw new Error(`truth ${id}: unknown severity fill ${hexPaint(costCell.fills)}`);
    let controlCell = rectAt(756, rowY);
    if (!controlCell && letter === "C") {
      // All five Class C claims converge on one 60px control box centred in
      // the band; it does not geometrically span every claim row.
      controlCell = rects.find((r) => approx(r.x, 756, 0.6) && r.height > 40);
    }
    if (!controlCell) throw new Error(`truth ${id}: control rectangle missing`);
    const controlFill = hexPaint(controlCell.fills);
    const controlActive = controlFill === "#dbeafe";
    if (!["#dbeafe", "#fef3c7", "#fef2f2"].includes(controlFill)) {
      throw new Error(`truth ${id}: unknown control fill ${controlFill}`);
    }
    let controlDisplay = null;
    const rowControlTexts = band.filter((t) => t.x >= 756 && t.x + t.width <= 1006.6);
    if (letter !== "C") {
      if (rowControlTexts.length !== 1) throw new Error(`truth ${id}: expected one control text, got ${rowControlTexts.length}`);
      controlDisplay = clean(rowControlTexts[0].characters);
    }
    const rowTexts = [label, cost, ...rowControlTexts];
    assertNoOverlaps(id, rowTexts);
    for (const node of rowTexts) {
      if (node.height > 20.1) throw new Error(`truth ${id}: ${node.name} wrapped to ${node.height}px`);
    }
    assertColumn(id, label, 320);
    assertColumn(id, cost, 658);
    rowControlTexts.forEach((node) => assertColumn(id, node, 996));
    return {
      id,
      class: letter,
      severity,
      claim: clean(label.characters.slice(id.length + 3)),
      cost: clean(cost.characters),
      control_display: controlDisplay,
      control_active: controlActive,
      _rowY: rowY,
      _controlCell: controlCell,
    };
  });
  const classes = ["A", "B", "C"].map((letter) => {
    const classRows = extractedRows.filter((row) => row.class === letter);
    const top = Math.min(...classRows.map((row) => row._rowY));
    const bottom = Math.max(...classRows.map((row) => row._rowY + 40));
    const inBand = texts.filter((t) => t.y >= top - 2 && t.y < bottom + 2);
    const conversion = inBand.find((t) => t.x >= 1100 && t.x < 1300 &&
      numericFont(t) !== null && approx(numericFont(t), 14.5, 0.25));
    const outcome = inBand.find((t) => t.x >= 1400 && t.x < 1650 &&
      numericFont(t) !== null && approx(numericFont(t), 15, 0.25));
    const cadence = inBand.find((t) => approx(t.x, 1782, 1.1) &&
      numericFont(t) !== null && approx(numericFont(t), 8, 0.25));
    const action = inBand.find((t) => approx(t.x, 1782, 1.1) &&
      numericFont(t) !== null && approx(numericFont(t), 15, 0.25));
    const detail = inBand.find((t) => approx(t.x, 1782, 1.1) &&
      numericFont(t) !== null && approx(numericFont(t), 11, 0.25));
    if (!conversion || !outcome || !cadence || !action || !detail) {
      throw new Error(`truth Class ${letter}: class-level field missing`);
    }
    const actionCell = rects.find((r) => approx(r.x, 1770, 0.6) && r.y <= cadence.y && r.y + r.height >= detail.y + detail.height);
    if (!actionCell) throw new Error(`truth Class ${letter}: action rectangle missing`);
    let sharedControl = null;
    if (letter === "C") {
      const sharedRect = classRows[0]._controlCell;
      const sharedTexts = texts.filter((t) => t.x >= 756 && t.x + t.width <= 1006.6 &&
        t.y >= sharedRect.y && t.y + t.height <= sharedRect.y + sharedRect.height)
        .sort((a, b) => a.y - b.y);
      if (sharedTexts.length !== 2) throw new Error(`truth Class C: expected two shared-control texts, got ${sharedTexts.length}`);
      sharedControl = sharedTexts.map((t) => clean(t.characters)).join(" · ");
      assertNoOverlaps("Class C control", sharedTexts);
    }
    return {
      class: letter,
      conversion: clean(conversion.characters),
      outcome: clean(outcome.characters).toLowerCase(),
      cadence: clean(cadence.characters),
      action: clean(action.characters),
      action_detail: clean(detail.characters),
      action_type: actionTypeFromFill(actionCell),
      shared_control: sharedControl,
    };
  });
  return {
    rows: extractedRows.map(({ _rowY, _controlCell, ...row }) => row),
    classes,
  };
}

const data = cfg.shape === "row-register" ? extractRowRegister() :
  cfg.shape === "provenance" ? extractProvenance() : extractTruth();

return {
  schema_version: 1,
  extracted_on: "2026-08-09",
  layer: TARGET_LAYER,
  figma_file: figma.fileKey,
  page: { id: page.id, name: page.name },
  frame: { id: frame.id, name: frame.name, width: frame.width, height: frame.height },
  shape: cfg.shape,
  row_count: data.rows.length,
  assertions: {
    expected_rows: cfg.rows,
    no_text_overlaps: true,
    no_column_overflow: true,
    no_unexpected_wraps: true,
  },
  rows: data.rows,
  ...(data.classes ? { classes: data.classes } : {}),
};

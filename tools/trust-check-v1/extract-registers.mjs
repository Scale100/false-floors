#!/usr/bin/env node

import { spawnSync } from 'node:child_process';
import { existsSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const REGISTER_ROOT = 'projects/agent-trust-framework/registers';
const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const OUTPUT_PATH = join(SCRIPT_DIR, 'register-data.json');
const PAGE_PATH = join(SCRIPT_DIR, 'index.html');

const registerSpecs = [
  { file: 'instruction-layer.md', layer: 'instruction', prefix: 'IL', rows: 22, kind: 'standard' },
  { file: 'context-layer.md', layer: 'context', prefix: 'CL', rows: 22, kind: 'standard' },
  { file: 'authority-access-layer.md', layer: 'authority-access', prefix: 'AL', rows: 23, kind: 'authority' },
  { file: 'recovery-layer.md', layer: 'recovery', prefix: 'RL', rows: 24, kind: 'recovery' },
  { file: 'provenance-layer.md', layer: 'provenance', prefix: 'PL', rows: 22, kind: 'provenance' },
  { file: 'truth-layer.md', layer: 'truth', prefix: 'TL', rows: 15, kind: 'truth' },
];

function runGit(args, cwd = SCRIPT_DIR) {
  const result = spawnSync('git', args, { cwd, encoding: 'utf8' });
  if (result.status !== 0) {
    throw new Error(result.stderr.trim() || `git ${args.join(' ')} failed`);
  }
  return result.stdout;
}

function repositoryRoot() {
  return runGit(['rev-parse', '--show-toplevel']).trim();
}

function latestCanonCommit(root) {
  return runGit([
    'log', '-1', '--format=%H', '--', `:(glob)${REGISTER_ROOT}/*.md`,
  ], root).trim();
}

// The blob sha of every registers/*.md file at a commit, as { file: sha }.
//
// WHY THIS IS EMITTED ALONGSIDE generatedFrom, AND MATTERS MORE THAN IT.
// The C-25 check used to prove "which canon was read" by ancestry: canon had to be
// an ancestor of generatedFrom. That test has two failure modes that have both now
// been met in one day. A SQUASH merge replaces the branch commit, so the stamp goes
// "divergent history" and main reds on a change that was green on its own pull
// request — and the stamp can only be made correct AFTER the squash commit exists,
// so no pre-merge check can catch it. Worse, deleting the branch on merge makes the
// stamped commit UNRESOLVABLE in a fresh clone, so no amount of comparing at that
// commit can work either.
//
// Blob shas are content hashes, so this map settles the question directly and
// survives squash, rebase, branch deletion and history rewrites alike. It is also a
// STRONGER claim than the ancestry test: ancestry only proved the extractor ran at a
// commit that contained canon, while this proves the register bytes it read are the
// bytes present now, and names the file when they are not.
function registerBlobsAtCommit(root, commit) {
  const out = {};
  const listing = runGit(['ls-tree', commit, `${REGISTER_ROOT}/`], root);
  for (const line of listing.split('\n')) {
    if (!line.trim()) continue;
    const [meta, name] = line.split('\t');
    const [, type, sha] = meta.split(/\s+/);
    if (type !== 'blob' || !name.endsWith('.md')) continue;
    out[name.slice(REGISTER_ROOT.length + 1)] = sha;
  }
  return out;
}

// Must cover the SAME file set as registerBlobsAtCommit — every registers/*.md, not
// just the six the extractor parses — because the canon commit is defined by that
// glob. A narrower map here would silently compare fewer files than canon is made of.
function registerBlobsFromWorkingTree(root) {
  const out = {};
  const dir = join(root, REGISTER_ROOT);
  for (const name of readdirSync(dir).sort()) {
    if (!name.endsWith('.md')) continue;
    out[name] = runGit(['hash-object', join(dir, name)], root).trim();
  }
  return out;
}

function markdownAtCommit(root, commit, file) {
  return runGit(['show', `${commit}:${REGISTER_ROOT}/${file}`], root);
}

function markdownFromWorkingTree(root, file) {
  return readFileSync(join(root, REGISTER_ROOT, file), 'utf8');
}

function splitRow(line) {
  return line
    .trim()
    .replace(/^\|/, '')
    .replace(/\|$/, '')
    .split('|')
    .map((cell) => cell.trim());
}

function extractRows(markdown, prefix) {
  const lines = markdown.split(/\r?\n/);
  const rows = [];

  for (let index = 0; index < lines.length - 2; index += 1) {
    if (!/^\|\s*ID\s*\|/.test(lines[index])) continue;
    if (!/^\|(?:\s*:?-{3,}:?\s*\|)+$/.test(lines[index + 1].trim())) continue;

    const headers = splitRow(lines[index]);
    index += 2;
    while (index < lines.length && lines[index].trim().startsWith('|')) {
      const cells = splitRow(lines[index]);
      if (new RegExp(`^${prefix}-`).test(cells[0] ?? '')) {
        rows.push(Object.fromEntries(headers.map((header, cellIndex) => [header, cells[cellIndex] ?? ''])));
      }
      index += 1;
    }
  }

  return rows;
}

function parseNextAction(value) {
  const match = value.match(/^(.+?)\s+[—–]\s+(.+)$/);
  const triggerLabel = (match?.[1] ?? value).trim();
  return {
    trigger: triggerLabel.toLowerCase(),
    nextAction: value.trim(),
  };
}

function parseTool(value, hasRuntime = true) {
  const parts = value.split('·').map((part) => part.trim());
  if (hasRuntime) {
    const [tool = null, runtime = null, tier = null, builtState = null] = parts;
    return { tool, runtime, tier, builtState };
  }

  const [tool = null, tier = null, builtState = null] = parts;
  return { tool, runtime: 'any runtime', tier, builtState };
}

function parseControlCell(value) {
  if (value === 'n/a') return { strength: 'n/a', mechanism: null };
  const match = value.match(/^(closes|partial|nothing)\s+[—–]\s+(.+)$/);
  if (!match) throw new Error(`Unrecognised provenance control cell: ${value}`);
  return { strength: match[1], mechanism: match[2] };
}

function standardRow(row, spec) {
  const action = parseNextAction(row['Next action']);
  const tool = parseTool(row.Tool, spec.kind !== 'recovery');
  return {
    id: row.ID,
    layer: spec.layer,
    evidence: row.Evidence ?? null,
    severity: row.Sev,
    failure: row.Failure,
    showsUpAs: row['Shows up as'],
    prevention: row.Prevention,
    catchPoint: row.Catch,
    mechanism: row.Mechanism,
    ...tool,
    authority: row.Authority ?? null,
    outcome: row.Outcome,
    ...action,
  };
}

function provenanceRow(row, spec) {
  const action = parseNextAction(row['Next action']);
  return {
    id: row.ID,
    layer: spec.layer,
    evidence: row.Evidence ?? null,
    severity: row.Sev,
    failure: row['What breaks'],
    showsUpAs: row['What it costs'],
    prevention: null,
    catchPoint: null,
    mechanism: null,
    tool: null,
    runtime: null,
    tier: null,
    builtState: null,
    authority: null,
    harnessGate: parseControlCell(row['Harness gate']),
    repoArtefact: parseControlCell(row['Repo artefact']),
    controlPlaneCheck: parseControlCell(row['Control-plane check']),
    outcome: row.Outcome,
    ...action,
  };
}

function truthClass(id) {
  const number = Number(id.slice(3));
  if ([1, 2, 4, 5, 6, 7, 8, 9, 10].includes(number)) {
    return {
      class: 'B checkable',
      outcome: 'B detected',
      trigger: 'next build',
      nextAction: 'NEXT BUILD — Build or maintain the executable evidence',
    };
  }
  return {
    class: 'C judgement',
    outcome: 'C survives',
    trigger: 'every decision',
    nextAction: 'EVERY DECISION — Brief the judgement yourself',
  };
}

function truthRow(row, spec) {
  const classification = truthClass(row.ID);
  return {
    id: row.ID,
    layer: spec.layer,
    evidence: row.Evidence ?? null,
    severity: row.Sev,
    failure: row.Claim,
    showsUpAs: row["What it costs if it’s wrong"],
    prevention: null,
    catchPoint: null,
    mechanism: row['Control applied'],
    tool: null,
    runtime: null,
    tier: null,
    builtState: null,
    authority: null,
    claim: row.Claim,
    cost: row["What it costs if it’s wrong"],
    control: row['Control applied'],
    status: row.Status,
    ...classification,
  };
}

function parseRegister(markdown, spec) {
  const rows = extractRows(markdown, spec.prefix);
  if (rows.length !== spec.rows) {
    throw new Error(`${spec.file}: expected ${spec.rows} rows, parsed ${rows.length}`);
  }

  if (spec.kind === 'provenance') return rows.map((row) => provenanceRow(row, spec));
  if (spec.kind === 'truth') return rows.map((row) => truthRow(row, spec));
  return rows.map((row) => standardRow(row, spec));
}

function updateInlineFallback(payload) {
  if (!existsSync(PAGE_PATH)) return false;

  const open = '<script id="register-data-fallback" type="application/json">';
  const close = '</script>';
  const page = readFileSync(PAGE_PATH, 'utf8');
  const start = page.indexOf(open);
  const end = start === -1 ? -1 : page.indexOf(close, start + open.length);
  if (start === -1 || end === -1) {
    throw new Error('index.html is missing the register-data-fallback script block');
  }

  const inlineJson = JSON.stringify(payload).replaceAll('<', '\\u003c');
  const nextPage = `${page.slice(0, start + open.length)}${inlineJson}${page.slice(end)}`;
  writeFileSync(PAGE_PATH, nextPage, 'utf8');
  return true;
}

function main() {
  const root = repositoryRoot();
  const requestedSource = process.argv[2];
  const useWorkingTree = requestedSource === '--worktree';
  const source = requestedSource ?? latestCanonCommit(root);
  if (!source) {
    throw new Error(`No committed canon found under ${REGISTER_ROOT}/*.md`);
  }
  const rows = registerSpecs.flatMap((spec) => {
    const markdown = useWorkingTree
      ? markdownFromWorkingTree(root, spec.file)
      : markdownAtCommit(root, source, spec.file);
    return parseRegister(markdown, spec);
  });

  const ids = new Set(rows.map((row) => row.id));
  // 128 since the D-106 retirement pass of 2026-08-21 (was 134).
  if (rows.length !== 128 || ids.size !== 128) {
    throw new Error(`Expected 128 unique rows, got ${rows.length} rows and ${ids.size} unique IDs`);
  }

  const payload = {
    generatedFrom: useWorkingTree
      ? `working-tree@${runGit(['rev-parse', '--short=12', 'HEAD'], root).trim()}`
      : source,
    generatedBy: 'extract-registers.mjs',
    // Content identity of canon at generation time. check-registers.py compares this
    // to the blobs present now; see registerBlobsAtCommit above for why the commit
    // hash alone cannot carry this claim.
    canonBlobs: useWorkingTree
      ? registerBlobsFromWorkingTree(root)
      : registerBlobsAtCommit(root, source),
    rowCount: rows.length,
    rows,
  };
  writeFileSync(OUTPUT_PATH, `${JSON.stringify(payload, null, 2)}\n`, 'utf8');
  const updatedPage = updateInlineFallback(payload);
  process.stdout.write(`Wrote ${rows.length} rows to ${OUTPUT_PATH}${updatedPage ? ' and refreshed the inline fallback' : ''}\n`);
}

main();

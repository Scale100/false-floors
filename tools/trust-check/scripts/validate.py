#!/usr/bin/env python3
"""Hermetic installation calibration and end-to-end regression tests."""
import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('trust_check', Path(__file__).with_name('trust_check.py'))
tc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tc)
fx = tc.module('fixture_cases')


class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, cls.specs, cls.editorial, cls.counts = tc.load_assets()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='trust-check-calibration-')
        self.home = Path(self.tmp.name) / 'home'
        self.root = Path(self.tmp.name) / 'repo'
        self.home.mkdir()
        self.root.mkdir()
        self.env = patch.dict(os.environ, {'HOME': str(self.home), 'XDG_CONFIG_HOME': str(self.home), 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull})
        self.env.start()
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def invoke(self, *args, package=None):
        return subprocess.run([sys.executable, '-B', str((package or tc.BASE) / 'scripts/trust_check.py'), '--repo', str(self.root), *args], capture_output=True, text=True, timeout=20)

    def detect(self, rid, root=None):
        inv = tc.Inventory(root or self.root)
        return tc.detect(inv, rid, self.specs[rid])

    def test_full_non_class_c_library_and_bucket_identity(self):
        self.assertEqual(self.counts, tc.EXPECTED)
        inspected = {r['id'] for r in self.data['rows'] if r['catchPoint'] in tc.INSPECTABLE}
        self.assertEqual(set(self.specs), inspected)
        for row in self.data['rows']:
            if tc.bucket(row) == 'inspectable':
                self.assertEqual(self.specs[row['id']]['status'], 'active', row['id'])
        self.assertEqual(sum(s['status'] == 'active' for s in self.specs.values()), 66)
        for values in self.editorial.values():
            self.assertTrue({rid for v in values for rid in v['rowIds']} <= {r['id'] for r in self.data['rows']})

    def test_every_active_entry_refuses_bad_and_admits_good(self):
        seen = set()
        for rid, spec in self.specs.items():
            if spec['status'] != 'active':
                continue
            for good in (False, True):
                with self.subTest(row=rid, good=good), tempfile.TemporaryDirectory(dir=self.tmp.name) as tmp:
                    root = Path(tmp)
                    subprocess.run(['git', 'init', '-q', str(root)], check=True)
                    inv = tc.Inventory(root)
                    if spec['kind'] == 'remote':
                        inv.github_policy = fx.policy(good)
                        if rid == 'RL-2D':
                            fx.deploy(root)
                    else:
                        fx.local(root, rid, good)
                    found = tc.detect(inv, rid, spec)
                    self.assertEqual(found['state'], 'present' if good else 'absent', (rid, found))
                    if good:
                        self.assertTrue(found['evidence'], rid)
                        seen.add(rid)
        self.assertEqual(seen, {rid for rid, s in self.specs.items() if s['status'] == 'active'})

    def test_each_guard_rejects_disabled_missing_swallowing_and_stub(self):
        for rid in fx.GUARDS:
            for mode in ('disabled', 'missing', 'swallow', 'stub'):
                with self.subTest(row=rid, mode=mode), tempfile.TemporaryDirectory(dir=self.tmp.name) as tmp:
                    root = Path(tmp)
                    subprocess.run(['git', 'init', '-q', str(root)], check=True)
                    fx.connect(root, rid, mode)
                    self.assertNotEqual(self.detect(rid, root)['state'], 'present')

    def stub_git(self, trigger='--others'):
        """A git first on PATH that defers to the real one, delaying only the call under test.

        Same code path in both halves of the test; only $TRUST_CHECK_STUB_STALL differs,
        so a pass cannot come from the stub answering a different question. The trigger
        argument selects which call stalls: the working-set audit by default, or the
        repository-root call the scanner makes before it inspects anything.
        """
        real = shutil.which('git')
        self.assertTrue(real, 'a real git is required to back the stub')
        bindir = Path(self.tmp.name) / 'stub-bin'
        bindir.mkdir(exist_ok=True)
        stub = bindir / 'git'
        stub.write_text('#!/bin/sh\nfor a in "$@"; do\n  if [ "$a" = ' + shlex.quote(trigger) + ' ]; then sleep "${TRUST_CHECK_STUB_STALL:-0}" >/dev/null 2>&1; break; fi\ndone\nexec ' + shlex.quote(real) + ' "$@"\n')
        stub.chmod(0o755)
        return {'PATH': str(bindir) + os.pathsep + os.environ['PATH']}

    def test_slow_working_set_audit_is_named_and_visible_not_a_moved_count(self):
        # Regression for T-0125: on a large checkout the audit sometimes exceeded a
        # shared 4 s Git budget, and the detector reported a bare unknown, so the
        # observation counts moved with nothing changed in the repository.
        env = self.stub_git()
        fx.local(self.root, 'RL-1B', False)
        # The stalled audit is asserted first, so a pre-fix run fails on the reason it
        # actually gives rather than on the absence of a new attribute.
        with patch.dict(os.environ, {**env, 'TRUST_CHECK_STUB_STALL': '9'}):
            inv = tc.Inventory(self.root)
            inv.git_audit_timeout = 1
            found = tc.detect(inv, 'RL-1B', self.specs['RL-1B'])
            self.assertEqual(found['state'], 'unknown', found)
            for expected in ('git ls-files --others --directory --no-empty-directory --exclude-standard', '1 s'):
                self.assertIn(expected, found['reason'], found)
            self.assertEqual(len(inv.incomplete), 1, inv.incomplete)
            for expected in ('git ls-files --others', '1 s'):
                self.assertIn(expected, inv.incomplete[0])
            # A slow audit must not reach the shared error list; detectors branch on it.
            self.assertEqual(inv.errors, [])
            previous = {'status': 'skipped'}
            record = tc.make_record(inv, self.data, self.specs, self.editorial, self.counts, {}, previous, {})
            self.assertEqual(record['readBudget']['incompleteAudits'], inv.incomplete)
            self.assertIn('## Incomplete audits', tc.render(record, self.data))
            self.assertEqual(tc.compact_summary(record, self.data, previous, inv, tc.time.perf_counter())['incompleteAudits'], inv.incomplete)
            self.assertIn('ran out of budget', tc.terminal_report(inv, record, self.data, 0.0))
        # Known-good half: the same stub, no stall, still answers the real question.
        with patch.dict(os.environ, {**env, 'TRUST_CHECK_STUB_STALL': '0'}):
            quick = tc.Inventory(self.root)
            quick.git_audit_timeout = 1
            found = tc.detect(quick, 'RL-1B', self.specs['RL-1B'])
            self.assertEqual(found['state'], 'absent', found)
            self.assertEqual(quick.incomplete, [])

    def test_stalled_repository_root_call_is_named_as_a_timeout_not_a_missing_repository(self):
        # Regression for T-0128: main() asks Git for the repository root before it
        # inspects anything, and a Git that never answered was reported as the operator
        # having pointed at something that is not a repository root, which sends the
        # reader to look at their path instead of at the stalled command.
        # main() is called in-process so the module constant GIT_TIMEOUT is the seam;
        # the shipped script exposes no flag or variable that could shorten a real scan.
        env = self.stub_git('--show-toplevel')
        refusal = '--repo must be an existing Git repository root'

        def refused(root):
            with patch.object(sys, 'argv', ['trust_check.py', '--repo', str(root), '--offline']):
                with self.assertRaises(ValueError) as caught:
                    tc.main()
            return str(caught.exception)

        # The timeout message is asserted first, so a pre-fix run fails on the message
        # it actually gives rather than on anything the fix adds.
        with patch.dict(os.environ, {**env, 'TRUST_CHECK_STUB_STALL': '9'}), patch.object(tc, 'GIT_TIMEOUT', 1):
            stalled = refused(self.root)
        for expected in ('git rev-parse --show-toplevel', '1 s'):
            self.assertIn(expected, stalled)
        self.assertNotIn(refusal, stalled)
        self.assertFalse((self.root / tc.NAMES[0]).exists())
        # Known-good half: the same stub with no stall, and both genuine refusals stand.
        sub = self.root / 'sub'
        sub.mkdir()
        with patch.dict(os.environ, {**env, 'TRUST_CHECK_STUB_STALL': '0'}), patch.object(tc, 'GIT_TIMEOUT', 1):
            self.assertEqual(refused(self.home), refusal)
            self.assertEqual(refused(sub), refusal)

    def test_unrecognised_custom_guard_is_unknown(self):
        fx.connect(self.root, 'IL-1A')
        source = self.root / 'scripts/check-rule-budget.py'
        source.rename(source.with_name('bespoke-guard.py'))
        p = self.root / '.github/workflows/check.yml'
        p.write_text(p.read_text().replace('check-rule-budget.py', 'bespoke-guard.py'))
        found = self.detect('IL-1A')
        self.assertEqual(found['state'], 'unknown')
        self.assertIn('scripts/bespoke-guard.py', found['reason'])

    def test_aggregate_dispatcher_recognised_and_its_known_bads_refused(self):
        def hook(body):
            fx.write(self.root, 'scripts/check-banned-values.py', fx.guard_source('CL-4B'))
            fx.write(self.root, 'scripts/other.py', 'import sys\nsys.exit(0)\n')
            h = fx.write(self.root, '.githooks/pre-commit', body)
            h.chmod(0o755)
            subprocess.run(['git', '-C', str(self.root), 'config', 'core.hooksPath', '.githooks'], check=True)
            return self.detect('CL-4B')
        guard = 'python3 "${repo_root}/scripts/check-banned-values.py"'
        good = ('#!/usr/bin/env bash\nset -uo pipefail\nrepo_root="$(git rev-parse --show-toplevel)"\nfail=0\n'
                + guard + ' || fail=1\npython3 "${repo_root}/scripts/other.py" || fail=1\nexit "$fail"\n')
        found = hook(good)
        self.assertEqual(found['state'], 'present', found)
        self.assertEqual(found['how'], 'git config core.hooksPath -> .githooks/pre-commit -> scripts/check-banned-values.py')
        fallback = good.replace('--show-toplevel)"', '--show-toplevel 2>/dev/null || pwd)"')
        self.assertEqual(hook(fallback)['state'], 'present', 'root assignment with a pwd fallback')
        bads = {
            'root assignment with a foreign fallback': good.replace('--show-toplevel)"', '--show-toplevel || echo /elsewhere)"'),
            'exit 0 at the end': good.replace('exit "$fail"', 'exit 0'),
            'failure swallowed': good.replace(guard + ' || fail=1', guard + ' || true'),
            'no initialiser': good.replace('fail=0\n', ''),
            'reset after a guard': good.replace('exit "$fail"', 'fail=0\nexit "$fail"'),
            'unguarded line among guards': good.replace('exit "$fail"', 'python3 "${repo_root}/scripts/other.py"\nexit "$fail"'),
            'set +e': good.replace('set -uo pipefail', 'set +e'),
            'conditional guard': good.replace(guard + ' || fail=1', 'if [ -z "$SKIP" ]; then ' + guard + '; fi'),
            'exit of another variable': good.replace('exit "$fail"', 'exit "$rc"'),
            'stub guard': None,
        }
        for name, body in bads.items():
            with self.subTest(bad=name):
                if body is None:
                    hook(good)
                    fx.write(self.root, 'scripts/check-banned-values.py', '# banned forbidden value default\nprint("pass")\n')
                    found = self.detect('CL-4B')
                else:
                    found = hook(body)
                self.assertNotEqual(found['state'], 'present', (name, found))

    def repo(self):
        root = Path(tempfile.mkdtemp(dir=self.tmp.name))
        subprocess.run(['git', 'init', '-q', str(root)], check=True)
        return root

    def test_manifest_binds_a_declared_guard_the_pattern_does_not_name(self):
        root = self.repo()
        fx.write(root, fx.DECLARED_GUARD, fx.DECLARED_SOURCE)
        fx.dispatcher(root, [fx.DECLARED_GUARD])
        self.assertEqual(self.detect('CL-4B', root)['state'], 'unknown', 'unnamed guard earns nothing on its own')
        fx.manifest(root, {'CL-4B': [fx.DECLARED_GUARD]})
        found = self.detect('CL-4B', root)
        self.assertEqual(found['state'], 'present', found)
        self.assertTrue(found['manifest'])
        self.assertEqual(found['how'], 'git config core.hooksPath -> .githooks/pre-commit -> ' + fx.DECLARED_GUARD)
        self.assertIn('declared in .false-floors.json, not inferred', found['reason'])
        # The same file may implement two rows; each is decided on its own.
        fx.manifest(root, {'CL-4B': [fx.DECLARED_GUARD], 'IL-4A': [fx.DECLARED_GUARD]})
        for rid in ('CL-4B', 'IL-4A'):
            self.assertEqual(self.detect(rid, root)['state'], 'present', rid)

    def test_manifest_known_bads_are_refused(self):
        cases = {}

        root = self.repo()
        fx.write(root, fx.DECLARED_GUARD, fx.DECLARED_SOURCE)
        fx.manifest(root, {'CL-4B': [fx.DECLARED_GUARD]})
        cases['not connected on any listed surface'] = (root, 'absent', 'not connected on pre-commit')

        root = self.repo()
        fx.write(root, fx.DECLARED_GUARD, fx.DECLARED_STUB)
        fx.dispatcher(root, [fx.DECLARED_GUARD])
        fx.manifest(root, {'CL-4B': [fx.DECLARED_GUARD]})
        cases['stub with no input read and no rejection'] = (root, 'unknown', 'an input read and a rejection path')

        for name, joiner in (('failure swallowed by || true', ' || true'), ('conditional invocation', ' && [ -n "$RUN" ]')):
            root = self.repo()
            fx.write(root, fx.DECLARED_GUARD, fx.DECLARED_SOURCE)
            fx.dispatcher(root, [fx.DECLARED_GUARD], joiner)
            fx.manifest(root, {'CL-4B': [fx.DECLARED_GUARD]})
            cases[name] = (root, 'unknown', 'conditional, asynchronous, failure-swallowing or compound invocation')

        root = self.repo()
        fx.write(root, fx.DECLARED_GUARD, fx.DECLARED_SOURCE)
        (root / 'tools/linked.sh').symlink_to(fx.write(self.home, 'outside.sh', fx.DECLARED_SOURCE))
        fx.manifest(root, {'CL-4B': ['tools/linked.sh']})
        cases['symlinked declaration'] = (root, 'unknown', 'could not be read inside the repository')

        root = self.repo()
        fx.manifest(root, {'CL-4B': ['../outside.sh']})
        cases['declaration outside the repository'] = (root, 'unknown', 'could not be read inside the repository')

        for name, (root, state, phrase) in cases.items():
            with self.subTest(bad=name):
                found = self.detect('CL-4B', root)
                self.assertEqual(found['state'], state, (name, found))
                self.assertIn(phrase, found['reason'], (name, found))
                self.assertFalse(found['manifest'])

    def test_malformed_manifest_leaves_every_gate_row_unknown(self):
        for text in ('{bad', '{"gates": ["tools/my-banned-words.sh"]}', '[]'):
            with self.subTest(manifest=text):
                root = self.repo()
                fx.write(root, fx.DECLARED_GUARD, fx.DECLARED_SOURCE)
                fx.dispatcher(root, [fx.DECLARED_GUARD])
                fx.write(root, '.false-floors.json', text)
                for rid in ('CL-4B', 'IL-1A', 'IL-3A'):
                    found = self.detect(rid, root)
                    self.assertEqual(found['state'], 'unknown', (rid, found))
                    self.assertIn('.false-floors.json', found['reason'])

    def test_manifest_report_records_every_declaration_and_credits_none_it_may_not(self):
        root = self.repo()
        fx.write(root, fx.DECLARED_GUARD, fx.DECLARED_SOURCE)
        fx.write(root, 'tools/second-guard.sh', fx.DECLARED_SOURCE)
        fx.dispatcher(root, [fx.DECLARED_GUARD, 'tools/second-guard.sh'])
        fx.write(root, '.github/workflows/check.yml', json.dumps(
            {'on': {'pull_request': {}}, 'jobs': {'check': {'runs-on': 'ubuntu-latest', 'steps': [{'run': 'bash ' + fx.DECLARED_GUARD}]}}}))
        fx.manifest(root, {'CL-4B': [fx.DECLARED_GUARD, 'tools/second-guard.sh'], 'IL-4A': [fx.DECLARED_GUARD],
                           'IL-3A': [fx.DECLARED_GUARD], 'IL-2A': [fx.DECLARED_GUARD],
                           'IL-1D': [fx.DECLARED_GUARD], 'ZZ-99': [fx.DECLARED_GUARD]},
                    extra={'strayKey': 'ignored by the scanner'})
        inv = tc.Inventory(root)
        record = tc.make_record(inv, self.data, self.specs, self.editorial, self.counts, {}, {}, {})
        outcomes = {(e['rowId'], e['outcome']) for e in record['manifest']['entries']}
        self.assertEqual(outcomes, {('CL-4B', 'credited'), ('CL-4B', 'not evaluated'), ('IL-4A', 'credited'),
                                    ('IL-3A', 'declared, not creditable'), ('IL-2A', 'declared, not creditable'),
                                    ('IL-1D', 'declared, not creditable'), ('ZZ-99', 'unknown row, ignored')})
        self.assertTrue(any('Class C' in e['detail'] for e in record['manifest']['entries'] if e['rowId'] == 'IL-3A'))
        self.assertTrue(any('draft' in e['detail'] for e in record['manifest']['entries'] if e['rowId'] == 'IL-2A'))
        self.assertTrue(any('not a gate' in e['detail'] for e in record['manifest']['entries'] if e['rowId'] == 'IL-1D'))
        self.assertTrue(any('strayKey' in n for n in record['manifest']['notes']))
        # The keys this tool writes itself must not be reported as strays on every run.
        fx.manifest(root, {'CL-4B': [fx.DECLARED_GUARD]},
                    extra={'note': 'written by the tool', 'confirmedOn': {'CL-4B': '2026-09-09'},
                           'installed': {'RL-2C': {'path': 'tools/x.py'}}})
        quiet = tc.make_record(tc.Inventory(root), self.data, self.specs, self.editorial, self.counts, {}, {}, {})
        self.assertEqual([n for n in quiet['manifest']['notes'] if 'ignored' in n], [])
        self.assertEqual(record['rows']['CL-4B'], 'partially closed')
        self.assertEqual(record['rows']['IL-3A'], 'open')
        self.assertEqual(record['readBudget']['manifest'], 'read')
        report = tc.render(record, self.data, full=True)
        self.assertIn('## Repository manifest', report)
        for rid in ('CL-4B', 'IL-3A', 'ZZ-99'):
            self.assertIn('| ' + rid + ' | `' + fx.DECLARED_GUARD + '` |', report)

    def test_no_manifest_leaves_the_scan_unchanged(self):
        root = self.repo()
        fx.connect(root, 'IL-1A')
        before = tc.make_record(tc.Inventory(root), self.data, self.specs, self.editorial, self.counts, {}, {}, {})
        fx.manifest(root, {})
        after = tc.make_record(tc.Inventory(root), self.data, self.specs, self.editorial, self.counts, {}, {}, {})
        self.assertEqual({r: f['state'] for r, f in before['findings'].items()},
                         {r: f['state'] for r, f in after['findings'].items()})
        self.assertFalse(before['manifest']['declared'])
        self.assertEqual(before['readBudget']['manifest'], 'not present')
        self.assertIn('No `.false-floors.json`', tc.render(before, self.data, full=True))
    def test_claim_sources_dispatcher_scores_cl_4a_on_pre_commit(self):
        # The vault's own citation gate: a pre-commit dispatcher of the aggregate-then-fail shape
        # invoking tools/pre-commit-claim-sources.sh, which reads the staged diff and refuses.
        def hook(invocation):
            fx.write(self.root, 'tools/pre-commit-claim-sources.sh',
                     '#!/usr/bin/env bash\nset -uo pipefail\n'
                     'changed="$(git diff --cached --name-only)"\n'
                     'for document in ${changed}; do\n'
                     '  grep -q "source:" "${document}" || { echo "claim without a citation"; exit 1; }\n'
                     'done\n')
            h = fx.write(self.root, '.githooks/pre-commit',
                         '#!/usr/bin/env bash\nset -uo pipefail\n'
                         'repo_root="$(git rev-parse --show-toplevel)"\nfail=0\n' + invocation + '\nexit "$fail"\n')
            h.chmod(0o755)
            subprocess.run(['git', '-C', str(self.root), 'config', 'core.hooksPath', '.githooks'], check=True)
            return self.detect('CL-4A')
        guard = 'bash "${repo_root}/tools/pre-commit-claim-sources.sh"'
        found = hook(guard + ' || fail=1')
        self.assertEqual(found['state'], 'present', found)
        self.assertEqual(found['how'], 'git config core.hooksPath -> .githooks/pre-commit -> tools/pre-commit-claim-sources.sh')
        self.assertNotEqual(hook(guard + ' || true')['state'], 'present')

    def test_action_step_is_unknown_unless_it_is_a_known_setup_action(self):
        def workflow(*steps):
            fx.write(self.root, '.github/workflows/check.yml', json.dumps(
                {'on': {'pull_request': {}}, 'jobs': {'check': {'runs-on': 'ubuntu-latest', 'steps': list(steps)}}}))
        checkout = {'uses': 'actions/checkout@v4'}
        workflow(checkout, {'uses': 'actions/setup-python@v5'})
        self.assertEqual(self.detect('CL-4A')['state'], 'absent')
        self.assertEqual(self.detect('CL-4B')['state'], 'absent')
        workflow(checkout, {'uses': 'some-org/check-banned-values@v1'})
        found = self.detect('CL-4A')
        self.assertEqual(found['state'], 'unknown', found)
        self.assertIn('some-org/check-banned-values', found['reason'])
        self.assertIn('not inspected', found['reason'])
        self.assertNotIn('actions/checkout', found['reason'])
        # The allowlist matches the owner/name before the '@' exactly, so a lookalike is uninspected.
        workflow({'uses': 'actions/checkout-evil@v1'})
        self.assertIn('actions/checkout-evil', self.detect('CL-4A')['reason'])
        # A recorded CI action never makes a row uncertain on a surface it was not recorded on.
        self.assertEqual(self.detect('CL-4B')['state'], 'absent')
        # The reason names at most six actions.
        workflow(*[{'uses': f'some-org/guard-{n}@v1'} for n in range(7)])
        reason = self.detect('CL-4A')['reason']
        self.assertEqual(reason.count('some-org/guard-'), 6)
        self.assertIn(', ...', reason)
        # A recognised run: guard still scores, whatever else the job uses.
        fx.write(self.root, 'scripts/check-citations.py', fx.guard_source('CL-4A'))
        workflow({'uses': 'some-org/check-banned-values@v1'}, {'run': 'python3 scripts/check-citations.py'})
        self.assertEqual(self.detect('CL-4A')['state'], 'present')

    def test_surface_unknown_names_the_offending_configuration_line(self):
        # A read error elsewhere in the tree no longer turns an absent gate row into unknown.
        inv = tc.Inventory(self.root)
        inv.errors.append('docs/big.md: read budget exceeded')
        self.assertEqual(tc.detect(inv, 'RL-4C', self.specs['RL-4C'])['state'], 'absent')
        fx.connect(self.root, 'CL-4B')
        h = self.root / '.githooks/pre-commit'
        h.write_text('#!/bin/sh\nset -e\nhere=$(pwd)\npython3 "$here/scripts/check-banned-values.py"\n')
        found = self.detect('CL-4B')
        self.assertEqual(found['state'], 'unknown')
        self.assertIn('.githooks/pre-commit', found['reason'])
        self.assertIn('here=$(pwd)', found['reason'])
        fx.connect(self.root, 'IL-4C')
        p = self.root / '.claude/settings.json'
        doc = json.loads(p.read_text())
        doc['hooks']['PreToolUse'][0]['hooks'][0]['command'] = 'python3 "$(git rev-parse --show-toplevel)/scripts/read-before-write.py"'
        p.write_text(json.dumps(doc))
        found = self.detect('IL-4C')
        self.assertEqual(found['state'], 'unknown')
        self.assertIn('.claude/settings.json#/hooks/PreToolUse', found['reason'])
        self.assertIn('rev-parse', found['reason'])

    def test_yaml_real_format_comments_duplicates_aliases(self):
        fx.connect(self.root, 'IL-1A')
        p = self.root / '.github/workflows/check.yml'
        p.write_text('on: [pull_request]\njobs:\n  checks:\n    runs-on: ubuntu-latest\n    steps:\n      - name: Rule budget\n        run: |\n          python3 scripts/check-rule-budget.py\n')
        self.assertEqual(self.detect('IL-1A')['state'], 'present')
        p.write_text('on: [pull_request]\njobs:\n  checks:\n    runs-on: ubuntu-latest\n    steps:\n      - run: |\n          python3 scripts/check-rule-budget.py \\\n            --strict\n')
        self.assertEqual(self.detect('IL-1A')['state'], 'present', 'backslash continuation is one command')
        for text in ['# run: python3 scripts/check-rule-budget.py\n', 'on: [push]\non: [pull_request]\njobs: {}\n', 'on: &trigger [push]\njobs: *trigger\n', '!!python/object/apply:os.system ["touch EXECUTED"]\n']:
            p.write_text(text)
            self.assertNotEqual(self.detect('IL-1A')['state'], 'present')
            self.assertFalse((self.root / 'EXECUTED').exists())

    def test_npm_script_indirection_and_cycle(self):
        fx.connect(self.root, 'IL-1A')
        fx.write(self.root, 'package.json', json.dumps({'scripts': {'verify': 'python3 scripts/check-rule-budget.py'}}))
        p = self.root / '.github/workflows/check.yml'
        p.write_text(p.read_text().replace('python3 scripts/check-rule-budget.py', 'npm run verify'))
        self.assertEqual(self.detect('IL-1A')['state'], 'present')
        fx.write(self.root, 'package.json', json.dumps({'scripts': {'verify': 'npm run verify'}}))
        self.assertEqual(self.detect('IL-1A')['state'], 'unknown')

    def test_hook_wrong_event_matcher_local_disable_and_read_errors(self):
        fx.connect(self.root, 'IL-4C')
        p = self.root / '.claude/settings.json'
        good = p.read_text()
        for text in [good.replace('PreToolUse', 'PostToolUse'), good.replace('Write|Edit', 'Read')]:
            p.write_text(text)
            self.assertNotEqual(self.detect('IL-4C')['state'], 'present')
        p.write_text(good)
        fx.write(self.root, '.claude/settings.local.json', '{"disableAllHooks":true}')
        self.assertNotEqual(self.detect('IL-4C')['state'], 'present')
        p.write_text('{invalid')
        self.assertEqual(self.detect('IL-4C')['state'], 'unknown')

    def test_unreadable_guard_and_error_swallowing_shell(self):
        fx.connect(self.root, 'IL-4A')
        hook = self.root / '.githooks/pre-commit'
        hook.write_text(hook.read_text().replace('set -e', 'set +e') + 'exit 0\n')
        self.assertNotEqual(self.detect('IL-4A')['state'], 'present')
        fx.connect(self.root, 'IL-4A')
        script = self.root / 'scripts/check-eslint-rules.py'
        script.unlink()
        outside = fx.write(self.home, 'guard.py', fx.guard_source('IL-4A'))
        script.symlink_to(outside)
        self.assertEqual(self.detect('IL-4A')['state'], 'unknown')

    def test_primitive_disabled_wrong_type_and_oversized(self):
        for payload in [{'sandbox': {'enabled': False}}, {'sandbox': {'enabled': 'true'}}, {'permissions': {'deny': []}}, {'permissions': {'deny': 'Edit(*)'}}]:
            fx.write(self.root, '.claude/settings.json', json.dumps(payload))
            for rid in ('RL-2A', 'AL-1B'):
                self.assertNotEqual(self.detect(rid)['state'], 'present')
        fx.write(self.root, '.claude/settings.json', '{"sandbox":{"enabled":true}}')
        fx.write(self.root, '.claude/settings.local.json', '{"sandbox":{"enabled":false}}')
        self.assertEqual(self.detect('RL-2A')['state'], 'unknown')
        (self.root / '.claude/settings.local.json').unlink()
        fx.write(self.root, '.claude/settings.json', 'x' * (tc.MAX_FILE + 1))
        inv = tc.Inventory(self.root)
        for rid in ('RL-2A', 'AL-1B'):
            self.assertEqual(tc.detect(inv, rid, self.specs[rid])['state'], 'unknown')

    def test_remote_no_consent_missing_bypass_fields_and_inherited_rules(self):
        detector = tc.module('detectors')
        self.assertEqual(self.detect('AL-3B')['state'], 'unknown')
        for mutation in ('missing', 'evaluate', 'reviewers', 'checks'):
            inv = tc.Inventory(self.root)
            inv.github_policy = fx.policy()
            p = inv.github_policy
            if mutation == 'missing':
                del p['details'][42]['data']['bypass_actors']
                row = 'AL-3B'
            elif mutation == 'evaluate':
                p['details'][42]['data']['enforcement'] = 'evaluate'
                row = 'AL-3B'
            elif mutation == 'reviewers':
                p['effective']['data'][0]['parameters']['required_approving_review_count'] = 0
                row = 'AL-4E'
            else:
                p['effective']['data'][1]['parameters']['required_status_checks'] = []
                row = 'AL-4A'
            self.assertNotEqual(tc.detect(inv, row, self.specs[row])['state'], 'present')
        called = []
        def fetch(endpoint):
            called.append(endpoint)
            if '/rules/branches/' in endpoint:
                r = copy.deepcopy(fx.policy()['effective'])
                for rule in r['data']:
                    rule.update(ruleset_source_type='Organization', ruleset_source='fixture-org')
                return r
            if '/rulesets/' in endpoint:
                return fx.policy()['details'][42]
            return fx.policy()['legacy']
        inv = tc.Inventory(self.root)
        inv.github_policy = detector.fetch_policy('fixture/repo', 'release/test', fetch)
        self.assertTrue(any('orgs/fixture-org/rulesets/42' == x for x in called))
        self.assertTrue(any('release%2Ftest' in x for x in called))
        self.assertEqual(tc.detect(inv, 'AL-3B', self.specs['AL-3B'])['state'], 'present')
        inv.github_policy['effective']['data'][0]['parameters'] = None
        self.assertEqual(tc.detect(inv, 'AL-4E', self.specs['AL-4E'])['state'], 'unknown')

    def test_legacy_protection_and_deployment_route(self):
        inv = tc.Inventory(self.root)
        inv.github_policy = fx.policy(False)
        inv.github_policy['legacy']['data'] = {'enforce_admins': {'enabled': True}, 'allow_force_pushes': {'enabled': False}, 'required_status_checks': {'contexts': ['test']}, 'required_pull_request_reviews': {'required_approving_review_count': 1, 'bypass_pull_request_allowances': {'users': [], 'teams': [], 'apps': []}}}
        for row in ('AL-3B', 'AL-4A', 'AL-4E', 'RL-4B'):
            self.assertEqual(tc.detect(inv, row, self.specs[row])['state'], 'present')
        inv.github_policy['legacy']['data']['enforce_admins']['enabled'] = False
        self.assertNotEqual(tc.detect(inv, 'AL-3B', self.specs['AL-3B'])['state'], 'present')
        fx.deploy(self.root)
        p = self.root / '.github/workflows/deploy.yml'
        doc = json.loads(p.read_text()); doc['on']['workflow_dispatch'] = {}; p.write_text(json.dumps(doc))
        inv = tc.Inventory(self.root); inv.github_policy = fx.policy()
        self.assertEqual(tc.detect(inv, 'RL-2D', self.specs['RL-2D'])['state'], 'unknown')

    def test_freshness_public_tags_numeric_order_offline_and_failure(self):
        requests = []
        def tags(req, timeout):
            requests.append(req)
            return io.BytesIO(json.dumps([{'name': 'FF-2026.9'}, {'name': 'FF-2026.10'}, {'name': 'unrelated'}]).encode())
        self.assertEqual(tc.freshness('FF-2026.2', opener=tags)['latest'], 'FF-2026.10')
        self.assertEqual(tc.freshness('FF-2026.10', opener=tags)['status'], 'checked')
        self.assertEqual(tc.freshness('FF-2026.2', offline=True)['status'], 'skipped')
        self.assertTrue(all(r.full_url == tc.FEED and r.data is None and not r.has_header('Authorization') for r in requests))
        def unavailable(*a, **k): raise OSError('offline')
        self.assertEqual(tc.freshness('FF-2026.2', opener=unavailable)['status'], 'skipped')
        self.assertEqual(tc.freshness('FF-2026.2', opener=lambda *a, **k: io.BytesIO(b'{}'))['status'], 'skipped')

    def test_unavailable_history_has_no_stray_output(self):
        fx.write(self.root, 'tools/trust-check/scripts/diff-catalogue.py', "raise RuntimeError('must never execute target code')\n")
        prior = {'catalogueVersion': 'FF-2026.1', 'date': '2026-09-02', 'rows': {}}
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = tc.catalogue_diff(prior, self.data, self.root)
        self.assertEqual(result['status'], 'unavailable')
        self.assertEqual(out.getvalue(), '')

    def test_end_to_end_two_outputs_all_rows_no_target_execution(self):
        fx.local(self.root, 'AL-1B')
        fx.connect(self.root, 'IL-1A')
        # Marking a script executable never authorises the scanner to invoke it.
        guard = self.root / 'scripts/check-rule-budget.py'
        guard.write_text(guard.read_text() + "\nPath('EXECUTED').write_text('wrong')\n")
        before = {str(p.relative_to(self.root)) for p in self.root.rglob('*')}
        run = self.invoke('--offline')
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertLess(len(run.stdout), 2500)
        record = json.loads((self.root / tc.NAMES[0]).read_text())
        report = (self.root / tc.NAMES[1]).read_text()
        self.assertIn('False Floors trust check — Stage 1', report)
        self.assertIn('Controls identified for Stage 2 testing:', report)
        self.assertNotIn('Rows without a static answer are outside this Stage 1 report', report)
        self.assertIn('Our Stage 2 tool is due for release on 20 September.', report)
        self.assertIn('## Summary\n\nThe scan found', report)
        self.assertNotIn('**Summary:**', report)
        self.assertNotIn('In plain English:', report)
        self.assertIn('view of configuration coverage, not whether the checks work', report)
        self.assertIn('queued for Stage 2 testing.', report)
        self.assertIn('## Recommended next steps', report)
        self.assertIn('Here are three improvements you can add to your agent to make it more reliable.', report)
        self.assertEqual(report.count('**What to do:**'), tc.RECOMMENDATIONS_PER_PAGE)
        self.assertEqual(report.count('**Read more:**'), tc.RECOMMENDATIONS_PER_PAGE)
        self.assertIn('Canonical files', report)
        self.assertIn('Rule precedence', report)
        al_1b = next(row for row in self.data['rows'] if row['id'] == 'AL-1B')
        self.assertEqual(tc.improvement(al_1b)['title'], 'Enforced boundaries')
        self.assertIn('you might change your calendar rule from meetings until 5pm', report)
        self.assertIn('refunds over $100 need your approval', report)
        self.assertIn('production database', tc.improvement(al_1b)['explanation'])
        self.assertIn('ask whether the rule set has a precedence section', report)
        self.assertNotIn('- **What to look out for:**', report)
        self.assertNotIn('- **How to stop it:**', report)
        self.assertNotIn('- **Reference:**', report)
        self.assertNotIn('**Implementation pattern:**', report)
        self.assertNotIn('Catalogue reference:', report)
        self.assertIn('https://github.com/Scale100/false-floors/blob/main/registers/', report)
        self.assertIn('https://code.claude.com/docs/en/permissions',
                      tc.recommendation_references(al_1b))
        self.assertIn('After you have implemented these three improvements', report)
        self.assertIn('ask for the next three recommendations for the remaining', report)
        next_section = report.split('## Next', 1)[1]
        self.assertIn('. If you see one of these failures,', next_section)
        self.assertNotIn('\n\nIf you see one of these failures,', next_section)
        self.assertNotIn('\n\nNo score, badge, certification', next_section)
        report_before_more = report
        more = self.invoke('--offline', '--recommendations-page', '2')
        self.assertEqual(more.returncode, 0, more.stderr)
        self.assertRegex(more.stdout, r'Recommendations 4–6 of \d+')
        self.assertEqual(more.stdout.count('What to do:'), tc.RECOMMENDATIONS_PER_PAGE)
        self.assertEqual(more.stdout.count('Read more:'), tc.RECOMMENDATIONS_PER_PAGE)
        self.assertNotIn('What to look out for:', more.stdout)
        self.assertNotIn('How to stop it:', more.stdout)
        self.assertIn('https://', more.stdout)
        self.assertEqual((self.root / tc.NAMES[1]).read_text(), report_before_more)
        components = report.split('## Supported components found', 1)[1].split('## Stage 2 testing', 1)[0]
        self.assertEqual(components.count('\n- **'), 3)
        self.assertEqual(components.count('\n  - **Status:**'), 3)
        self.assertEqual(components.count('\n  - **Scope:**'), 3)
        self.assertEqual(components.count('\n  - **Inspected:**'), 3)
        self.assertEqual(components.count('\n  - **Evidence:**'), 3)
        self.assertEqual(components.count('\n\n- **'), 3)
        self.assertNotIn('\n\n### ', components)
        self.assertNotIn('<pre>', components)
        self.assertIn('Which False Floors failure is this, and what should I change?', report)
        for excluded in ('Unknown inspection results', 'Unhandled row shapes', 'Judgement required'):
            self.assertNotIn(excluded, report)
        self.assertEqual(json.loads(self.invoke('--offline', '--json-summary').stdout)['incompleteAudits'], [])
        self.assertNotIn('ran out of budget', run.stdout)
        self.assertEqual(record['readBudget']['incompleteAudits'], [])
        self.assertEqual(record['findings']['IL-1A']['state'], 'present')
        self.assertEqual(record['rows']['IL-1A'], 'partially closed')
        self.assertEqual(record['rows']['AL-1B'], 'open')
        self.assertEqual({f['state'] for f in record['findings'].values()}, {'present', 'absent', 'unknown'})
        branch_record = json.loads(json.dumps(record))
        for finding in branch_record['findings'].values():
            finding['state'] = 'unknown'
        branch_record['controlMap']['entries'] = []
        no_improvements = tc.render_stage1(branch_record, self.data)
        self.assertIn('No supported configuration improvement was identified', no_improvements)
        self.assertIn('Keep this assessment and rerun the trust check', no_improvements)
        self.assertIn('If you see an agent failure you want help with, paste what happened', no_improvements)
        branch_record['findings']['CL-1D']['state'] = 'absent'
        one_improvement = tc.render_stage1(branch_record, self.data)
        self.assertIn('Here is one improvement you can add', one_improvement)
        self.assertIn('After you have implemented this improvement', one_improvement)
        self.assertNotIn('ask for the next three recommendations', one_improvement)
        branch_record['findings']['IL-1D']['state'] = 'absent'
        two_improvements = tc.render_stage1(branch_record, self.data)
        self.assertIn('Here are two improvements you can add', two_improvements)
        self.assertIn('After you have implemented these two improvements', two_improvements)
        branch_record['findings']['AL-1B']['state'] = 'absent'
        final_three = tc.render_stage1(branch_record, self.data)
        self.assertIn('After you have implemented these three improvements', final_three)
        self.assertIn('rerun the trust check to see whether the configuration result changed', final_three)
        for row in self.data['rows']:
            self.assertIn(row['id'], record['rows'])
            if tc.judgement(row): self.assertEqual(record['rows'][row['id']], 'open')
        full = self.invoke('--offline', '--full')
        self.assertEqual(full.returncode, 0, full.stderr)
        full_report = (self.root / tc.NAMES[1]).read_text()
        for row in self.data['rows']:
            self.assertIn(row['id'], full_report)
            self.assertIn(row['failure'], full_report)
        after = {str(p.relative_to(self.root)) for p in self.root.rglob('*')}
        self.assertEqual(after - before, set(tc.NAMES))
        self.assertFalse((self.root / 'EXECUTED').exists())
        self.assertEqual(record['validation']['status'], 'pass')
        self.assertEqual(self.invoke('--offline').returncode, 0)
        second = json.loads((self.root / tc.NAMES[0]).read_text())
        self.assertEqual(second['catalogueDiff']['status'], 'checked')
        self.assertEqual(second['catalogueDiff']['result']['rowsAdded'], [])

    def test_interview_excludes_detector_unknown_and_judgement(self):
        inv = tc.Inventory(self.root)
        fs = {rid: tc.detect(inv, rid, s) for rid, s in self.specs.items()}
        qs = tc.questions(self.data, self.editorial, fs)
        rows = {r['id']: r for r in self.data['rows']}
        for q in qs:
            for rid in q['rowIds']:
                self.assertNotIn(rid, fs)
                self.assertFalse(tc.judgement(rows[rid]))
        record = tc.make_record(inv, self.data, self.specs, self.editorial, self.counts, {}, {}, {qs[0]['id']: True})
        for rid in qs[0]['rowIds']:
            self.assertEqual(record['selfReport'][rid]['evidenceClass'], 'self-reported')
            self.assertEqual(record['rows'][rid], 'open')
            self.assertIn('Verify the self-reported', record['nextAction'][rid])

    def test_stale_calibration_and_asset_tampering(self):
        package = Path(self.tmp.name) / 'package'
        shutil.copytree(tc.BASE, package)
        runner = package / 'scripts/detectors.py'
        runner.write_text(runner.read_text() + '\n# changed after calibration\n')
        fx.connect(self.root, 'IL-1A')
        p = self.invoke('--offline', package=package)
        self.assertEqual(p.returncode, 0, p.stderr)
        record = json.loads((self.root / tc.NAMES[0]).read_text())
        self.assertEqual(record['findings']['IL-1A']['state'], 'unknown')
        self.assertEqual(record['findings']['IL-1A']['detectorStatus'], 'draft')
        data = package / 'assets/register-data.json'
        payload = json.loads(data.read_text())
        payload['catalogueVersion'] = 'FF-2026.99'
        data.write_text(json.dumps(payload))
        altered = self.invoke('--offline', package=package)
        self.assertNotEqual(altered.returncode, 0)
        self.assertIn('Shipped asset changed; rebuild and revalidate: assets/register-data.json', altered.stderr)

    def test_integrity_lock_requires_the_exact_shipped_asset_set(self):
        for mutation in ('missing', 'extra'):
            with self.subTest(mutation=mutation):
                package = Path(self.tmp.name) / ('package-' + mutation)
                shutil.copytree(tc.BASE, package)
                lock_path = package / 'assets/integrity.json'
                lock = json.loads(lock_path.read_text())
                if mutation == 'missing':
                    del lock['sha256']['assets/editorial.json']
                else:
                    lock['sha256']['assets/not-shipped.json'] = '0' * 64
                lock_path.write_text(json.dumps(lock))
                altered = self.invoke('--offline', package=package)
                self.assertNotEqual(altered.returncode, 0)
                self.assertIn('integrity lock does not name the exact required file set', altered.stderr)

    def test_symlink_hardlink_output_and_invalid_prior_preserved(self):
        other = fx.write(self.home, 'other', 'preserve')
        out = self.root / tc.NAMES[1]
        for hard in (False, True):
            os.link(other, out) if hard else out.symlink_to(other)
            self.assertNotEqual(self.invoke('--offline').returncode, 0)
            self.assertEqual(other.read_text(), 'preserve')
            self.assertFalse((self.root / tc.NAMES[0]).exists())
            out.unlink()
        fx.write(self.root, tc.NAMES[0], '{bad')
        self.assertNotEqual(self.invoke('--offline').returncode, 0)
        self.assertEqual((self.root / tc.NAMES[0]).read_text(), '{bad')

    def test_projection_question_mode_and_consent_are_bounded(self):
        before = {str(p.relative_to(self.root)) for p in self.root.rglob('*')}
        p = self.invoke('--rows', 'IL-1A,RL-2A')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual({r['id'] for r in json.loads(p.stdout)}, {'IL-1A', 'RL-2A'})
        self.assertNotIn('canonBlobs', p.stdout)
        self.assertEqual(self.invoke('--questions').returncode, 0)
        self.assertEqual({str(p.relative_to(self.root)) for p in self.root.rglob('*')}, before)
        self.assertNotEqual(self.invoke('--offline', '--allow-github', 'fixture/repo', '--github-branch', 'main').returncode, 0)
        self.assertNotEqual(self.invoke('--allow-github', 'fixture/repo').returncode, 0)
        self.assertNotEqual(self.invoke('--allow-github', 'wrong/repo', '--github-branch', 'main').returncode, 0)
        self.assertNotEqual(self.invoke('--offline', '--answers', '[]').returncode, 0)

    # ---------------------------------------------------------------- D-272: map, confirm, install

    def test_control_map_describes_every_wired_control_and_names_no_row(self):
        """AC #4: the map is built from structure, carries no row, and assigns none."""
        # One guard the recogniser names on sight, and one it does not, on the same hook.
        fx.write(self.root, 'scripts/check-banned-values.py', fx.guard_source('CL-4B'))
        fx.write(self.root, 'tools/nobody-would-guess-this-name.sh',
                 '#!/usr/bin/env bash\n# refuse a commit that adds a forbidden value\n'
                 'set -uo pipefail\nstaged=$(git diff --cached --name-only)\n'
                 'grep -q nope $staged && { echo "BLOCKED: a forbidden value was added" >&2; exit 1; }\nexit 0\n')
        hook = fx.write(self.root, '.githooks/pre-commit',
                        '#!/usr/bin/env bash\nset -uo pipefail\nrepo_root="$(git rev-parse --show-toplevel)"\nfail=0\n'
                        'python3 "${repo_root}/scripts/check-banned-values.py" || fail=1\n'
                        'bash "${repo_root}/tools/nobody-would-guess-this-name.sh" || fail=1\nexit "$fail"\n')
        hook.chmod(0o755)
        subprocess.run(['git', '-C', str(self.root), 'config', 'core.hooksPath', '.githooks'], check=True)
        det = tc.module('detectors')
        inv = tc.Inventory(self.root)
        findings = {rid: tc.detect(inv, rid, spec) for rid, spec in self.specs.items()}
        control_map = det.control_map(inv, findings)
        by_path = {e['path']: e for e in control_map['entries']}
        self.assertIn('tools/nobody-would-guess-this-name.sh', by_path)
        mine = by_path['tools/nobody-would-guess-this-name.sh']
        # Structure, not vocabulary: where it is wired, what it reads, what it says on refusing.
        self.assertEqual(mine['surface'], 'pre-commit')
        self.assertTrue(mine['synchronousAndEnabled'])
        self.assertIn('staged diff', mine['reads'])
        self.assertIn('BLOCKED: a forbidden value was added', mine['refusalMessages'])
        self.assertIn('refuse a commit that adds a forbidden value', mine['header'])
        # The map never assigns a row, and never carries a key that could be mistaken for one.
        self.assertIsNone(mine['boundTo'])
        self.assertIsNone(mine['bindingSource'])
        self.assertNotIn('"row"', json.dumps(control_map))
        # A control a detector recognised on its own is marked verified, not confirmed.
        recognised = [e for e in control_map['entries'] if e['bindingSource'] == 'verified']
        self.assertTrue(recognised, 'the fixture guard should be recognised on its own name')
        self.assertTrue(all(e['boundTo'] for e in recognised))
        # Determinism: two builds of the same tree give the same map.
        self.assertEqual(control_map, det.control_map(tc.Inventory(self.root), findings))

    def unrecognised_guard(self):
        """A real refusing guard whose name no detector pattern admits."""
        fx.write(self.root, 'tools/house-style-please.sh',
                 '#!/usr/bin/env bash\n# house-style-please - refuse a commit that adds a banned default value\n'
                 'set -uo pipefail\nstaged=$(git diff --cached --name-only)\n'
                 'grep -q localhost:5432 $staged && { echo "BLOCKED: a banned value was added" >&2; exit 1; }\nexit 0\n')
        hook = fx.write(self.root, '.githooks/pre-commit',
                        '#!/usr/bin/env bash\nset -uo pipefail\nrepo_root="$(git rev-parse --show-toplevel)"\nfail=0\n'
                        'bash "${repo_root}/tools/house-style-please.sh" || fail=1\nexit "$fail"\n')
        hook.chmod(0o755)
        subprocess.run(['git', '-C', str(self.root), 'config', 'core.hooksPath', '.githooks'], check=True)
        det = tc.module('detectors')
        inv = tc.Inventory(self.root)
        findings = {rid: tc.detect(inv, rid, spec) for rid, spec in self.specs.items()}
        control_map = det.control_map(inv, findings)
        return next(e for e in control_map['entries'] if e['path'] == 'tools/house-style-please.sh')

    def proposals_file(self, entry, extra=()):
        path = self.root / 'proposals.json'
        path.write_text(json.dumps({'proposals': [
            {'controlId': entry['id'], 'row': 'CL-4B', 'confidence': 'high',
             'evidence': 'BLOCKED: a banned value was added', 'reason': 'it refuses a named wrong value'},
            *extra]}))
        return path

    def test_a_proposal_is_verified_before_credit_and_only_the_verified_are_written(self):
        """AC #5: propose writes nothing; confirm writes only what verification re-established."""
        entry = self.unrecognised_guard()
        bad = [
            {'controlId': entry['id'], 'row': 'IL-3A', 'confidence': 'low', 'evidence': '', 'reason': 'a Class C row'},
            {'controlId': 'invented::control', 'row': 'AL-1D', 'confidence': 'low', 'evidence': '', 'reason': 'no such control'},
            {'controlId': entry['id'], 'row': 'not-a-row', 'confidence': 'low', 'evidence': '', 'reason': 'malformed'},
            {'controlId': entry['id'], 'row': 'ZZ-99', 'confidence': 'low', 'evidence': '', 'reason': 'unknown row'},
        ]
        path = self.proposals_file(entry, bad)
        first = self.invoke('--offline', '--propose', str(path))
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn('WOULD BE CREDITED', first.stdout)
        self.assertIn('CL-4B', first.stdout)
        self.assertIn('Class C', first.stdout)
        self.assertIn('not a catalogue ID', first.stdout)
        self.assertIn('did not find wired', first.stdout)
        # Nothing at all is written by the propose step.
        self.assertFalse((self.root / tc.module('detectors').MANIFEST).exists())
        second = self.invoke('--offline', '--confirm', str(path))
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn('CONFIRMED AND WRITTEN', second.stdout)
        written = json.loads((self.root / tc.module('detectors').MANIFEST).read_text())
        self.assertEqual(written['gates'], {'CL-4B': ['tools/house-style-please.sh']})
        self.assertNotIn('IL-3A', written['gates'])
        self.assertNotIn('ZZ-99', written['gates'])
        self.assertIn('CL-4B', written['confirmedOn'])
        # The next run credits it as confirmed and has nothing left to read.
        run = self.invoke('--offline')
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertRegex(run.stdout, r'confirmed\s+CL-4B')
        record = json.loads((self.root / tc.NAMES[0]).read_text())
        self.assertEqual(record['findings']['CL-4B']['state'], 'present')
        self.assertTrue(record['findings']['CL-4B']['manifest'])
        entries = record['controlMap']['entries']
        self.assertEqual([e for e in entries if e['path'] == 'tools/house-style-please.sh'][0]['bindingSource'], 'confirmed')
        # Deterministic: a second run of the bound repository reads the same and writes the same.
        again = self.invoke('--offline')
        self.assertEqual(json.loads((self.root / tc.module('detectors').MANIFEST).read_text()), written)
        self.assertEqual(again.stdout, run.stdout.replace(run.stdout.split(' - ')[-1], again.stdout.split(' - ')[-1]))

    def test_a_proposal_the_scanner_cannot_verify_is_never_written(self):
        """The known-bad for the confirm step: a guard whose failure is swallowed."""
        entry = self.unrecognised_guard()
        hook = self.root / '.githooks/pre-commit'
        hook.write_text(hook.read_text().replace('|| fail=1', '|| true'))
        path = self.proposals_file(entry)
        run = self.invoke('--offline', '--confirm', str(path))
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn('REFUSED', run.stdout)
        self.assertIn('Nothing verified', run.stdout)
        self.assertFalse((self.root / tc.module('detectors').MANIFEST).exists())

    def test_the_terminal_report_is_v2_static_results_then_stage2_and_stays_on_one_screen(self):
        """V2 reports only established static results, then gives every control a next stage."""
        fx.connect(self.root, 'CL-4B')
        run = self.invoke('--offline')
        self.assertEqual(run.returncode, 0, run.stderr)
        out = run.stdout
        for part in ('trust check v2', 'STATIC RESULTS', 'RECOMMENDED NEXT STEPS',
                     'STAGE 2 TESTING', 'OPTIONAL CLASSIFICATION'):
            self.assertIn(part, out)
        self.assertLess(out.index('STATIC RESULTS'), out.index('STAGE 2 TESTING'))
        self.assertLess(out.index('STAGE 2 TESTING'), out.index('OPTIONAL CLASSIFICATION'))
        self.assertLessEqual(len(out), tc.TERMINAL_MAX)
        self.assertRegex(out, r'verified\s+CL-4B')
        self.assertRegex(out, r'\d+ wired controls identified for Stage 2 testing')
        self.assertIn('No score, badge or certification', out)
        self.assertIn('1. Canonical files', out)
        self.assertIn('2. Rule precedence', out)
        self.assertIn('3. Enforced boundaries', out)
        self.assertNotIn('Look out for:', out)
        self.assertNotIn('AVAILABLE RESPONSES', out)
        self.assertIn('the next three recommendations', out)
        self.assertIn('Instructions and links:', out)
        self.assertNotIn('Keep the assessment JSON. It is the handoff to Stage 2', out)
        self.assertNotIn('GAPS, most exposed first', out)
        self.assertNotRegex(out, r'\d+ unknown')
        # The full record is still the JSON, and it holds every row.
        record = json.loads((self.root / tc.NAMES[0]).read_text())
        self.assertEqual(len(record['findings']), len(self.specs))
        self.assertEqual(record['toolVersion'], '2')
        # The machine-readable summary is still available and is not the default.
        machine = self.invoke('--offline', '--json-summary')
        summary = json.loads(machine.stdout)
        self.assertEqual(set(summary) & {'staticResults', 'stage2ControlsIdentified', 'incompleteAudits'},
                         {'staticResults', 'stage2ControlsIdentified', 'incompleteAudits'})
        self.assertNotIn('observations', summary)

    def test_installing_a_gate_runs_its_self_test_and_the_next_scan_reports_the_result(self):
        """AC #7: an installed control is not a working one, so the receipt carries the test."""
        run = self.invoke('--offline', '--install', 'RL-2C')
        self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
        self.assertIn('SELF-TEST: PASSED', run.stdout)
        self.assertTrue((self.root / 'tools/destructive-git-guard.py').exists())
        receipt = json.loads((self.root / tc.module('detectors').MANIFEST).read_text())
        self.assertEqual(receipt['installed']['RL-2C']['selfTest']['passed'], True)
        # The receipt must carry the guard's own words, or a fabricated pass would be
        # indistinguishable from a real one. This is the mutation that survived on 2026-09-09.
        self.assertIn('destructive-git-guard self-test: PASS', receipt['installed']['RL-2C']['selfTest']['detail'])
        self.assertIn('7 known-bad refused', receipt['installed']['RL-2C']['selfTest']['detail'])
        # The next scan says what the self-test found, never that a file exists.
        scan = self.invoke('--offline')
        self.assertIn('installed ', scan.stdout)
        self.assertIn('its self-test caught the known-bad', scan.stdout)
        # Change the guard and the receipt must stop speaking for it.
        (self.root / 'tools/destructive-git-guard.py').write_text('# not the file that was tested\n')
        tampered = self.invoke('--offline')
        self.assertNotIn('caught the known-bad', tampered.stdout)
        self.assertIn('changed since its self-test ran', tampered.stdout)
        # A row with no template is refused rather than silently skipped.
        none = self.invoke('--offline', '--install', 'AL-2C')
        self.assertEqual(none.returncode, 1)
        self.assertIn('No installable gate for this row', none.stdout)

    def test_the_gate_library_passes_its_own_self_test(self):
        """The gate on the gate library: every template installs, wires and refuses its known-bad."""
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(tc.module('install').self_test(), 0)

    def test_unchanged_upstream_algorithms(self):
        for name in ('check-assessment', 'diff-catalogue'):
            with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(tc.module(name).self_test(), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)

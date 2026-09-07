---
type: reference
project: agent-trust-framework
title: Controls reference — what each named check asserts
status: published
date: 2026-09-06
last-updated: 2026-09-06
---

# Controls reference

**What this file is.** The registers name a control against each failure. This file says what each named control *asserts*, where it runs, and what it does not catch. It exists so a register row can state the control in plain terms — "regenerate-and-byte-diff on generated files" — while the reader can still see the concrete check behind it.

**What this file is not.** It is not the code, and it is not a recommendation to copy an implementation. Every entry describes a *check of a given shape*. The claim the registers make is that a check of that shape closes the failure — never that any particular script is the right way to write one. Build your own; the shape is the transferable part.

Scripts are named by their command, as they appear in the derivation project's package scripts. The scripts themselves are not published.

## Generated-artefact checks

The whole family works the same way: **regenerate the artefact from its source, then byte-diff the result against the committed copy.** A difference means the committed file is stale. This makes a generated file structurally impossible to commit in a stale state, which is why one pattern closes several rows at once ([IL-1F](instruction-layer.md), [IL-6B](instruction-layer.md), [TL-05](truth-layer.md)).

| Command | Asserts | Does not catch |
|---|---|---|
| `tokens:check` | The committed design tokens match what the token source regenerates | Whether the token source itself is correct |
| `agents:check` | The committed agent rule file matches what its inputs regenerate | Whether those inputs match the live control plane — CI cannot reach the vault ([instruction-layer](instruction-layer.md), reading notes) |
| `types:check` | The committed generated types match what the schema regenerates | A schema that is itself wrong |

## Test suites

| Command | Asserts | Does not catch |
|---|---|---|
| `test:flows` | End-to-end user flows execute and pass | That the flows encode the right requirement |
| `test:unit` | Unit behaviour is executed, not merely claimed | Whether the suite is meaningful — see [TL-09](truth-layer.md) |
| pgTAP suite | Database behaviour and row-level isolation hold against a real database | Application-layer paths that never reach the database |

pgTAP is a public open-source Postgres testing framework, not project code.

## Wording, architecture and interface checks

| Command | Asserts | Does not catch |
|---|---|---|
| `claims:check` | Published wording matches an approved-claims register | Whether the approved claim was true in the first place |
| `deps:check` | Module dependencies respect the declared architectural boundaries | Coupling that is expressed in something other than an import |
| `lint:i18n` | Interface strings are externalised rather than hard-coded | Whether the translation is correct |
| `a11y:check` | Automated accessibility rules pass, via axe-core | Everything automated accessibility testing cannot see, which is most of it |
| `verify:fast` | The fast pre-commit verification suite, into which individual gates are wired | Anything not wired into it — a gate that exists but is not called is C-34 |

axe-core is a public open-source accessibility engine, not project code.

## How to read an `available` row

A register row naming one of these controls says the control is the right shape for that failure, and the row's **availability** says whether a control of that shape exists at all. Neither says it is installed in your environment.

**This catalogue carries no install state.** Whether any control here is switched on somewhere is a fact about one environment on one date — an assessment, not a catalogue entry — and it is recorded as one. The register diagrams carry none either, because a figure travels without the paragraph that would say whose codebase it means.

That was not true until 2026-09-07, and the correction is worth stating rather than quietly applied: 84 cells across these registers used to carry the derivation codebase's install state, and this section used to tell you they did not. `TL-09` is what it cost — it published "not built" for mutation and property testing while both were running in that codebase's CI, and nothing announced the staleness, because a status column does not announce its own age.

---

*False Floors is a trade mark of Digital First Pty Ltd, trading as Scale100 (AU application AMCZ-2616155657). This content is CC BY 4.0; the name is not part of that licence. Citing, mapping to, or claiming conformance with the catalogue needs no permission – see `LICENSE-CONTENT`.*

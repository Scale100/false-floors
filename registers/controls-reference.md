---
type: reference
project: agent-trust-framework
title: Controls reference — what each named check asserts
status: published
date: 2026-09-06
last-updated: 2026-09-09
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

## Human-control checks

These controls apply only when an operator relies on human approval to constrain agent-produced software work. They are relevant to the **Regulated Delivery** applicability profile in D-271; a present control is not evidence that it is staffed, invoked or effective in a particular environment.

| Control shape | Asserts | Does not catch |
|---|---|---|
| Decision-specific qualification check | The assigned reviewer's documented qualification matches the decision's declared technical and risk scope | Whether the reviewer understood the evidence or exercised competent judgement in this decision |
| Decision-point evidence bundle | The reviewer received the declared change, test, risk and provenance evidence before the approval counts | Whether the supplied evidence is sufficient or correctly interpreted |
| Protected qualified-capacity gate | Admitted work stays within the declared qualified reviewers and minimum inspection time for its risk class | Whether a reviewer uses the reserved time well or becomes unavailable later |
| Override-authority check | The approval workflow affirmatively verifies that the assigned reviewer holds both reject and require-change permission | Whether another action route ignores that decision |
| Decision-enforcement gate | Every release or mutation route reads the human decision and refuses a rejected or unresolved change | Whether the reviewer identifies the defect or has the competence to judge it |

The same family enriches existing rows without duplicating them: code-labelling supports [PL-6D](provenance-layer.md); approval-policy completeness supports [IL-1E](instruction-layer.md); named reviewer availability supports [AL-4E](authority-access-layer.md); and decomposed confidence or oversight metrics support [TL-11](truth-layer.md). Four residual mechanisms are in the accepted row queue: decision-specific competence (TL-16 proposed), evidence at the decision point (PL-3G proposed), protected qualified capacity (AL-4H proposed) and effective override authority (AL-4I proposed). A fifth application, causal stop/change enforcement, is already covered by [IL-4E](instruction-layer.md) and [AL-4A](authority-access-layer.md): their destination-side gate is the mechanism that makes a recorded human decision bind every route.

## Execution and Capability control patterns

These controls are oracle-shaped. A named pattern is not evidence until it runs against the declared unit and conditions.

| EC rows | Control pattern | Receipt must show | Does not establish |
|---|---|---|---|
| EC-06, EC-07 | Time bound plus workflow enumeration | Declared bound, wedge result and enumerated job set | Functional correctness of a completed job |
| EC-08, EC-15 | Capability and configuration preflight | Required capability or configuration contract and refusal or hermetic-start result | The later functional postcondition |
| EC-09 | Environment-health sentinel | Dependency failure, invalid-run marker and refusal to emit a product result | Normal dependency health |
| EC-10, EC-11 | Executable postcondition and adversarial invariant tests | Requirement or invariant, test input and observed effect | Completeness of an unspecified requirement |
| EC-12 | Resource budget and load test | Budget, load shape and observed time, memory, quota and concurrency | Fleet allocation policy |
| EC-13, EC-14 | Contract and boundary-validation tests | Interface semantics or invalid inputs, version and effect result | Trustworthiness of an external source |
| EC-16 | Sequenced delivery test | Seed order, consumer observations and loss, duplicate and ordering verdict | Whether the delivery policy was complete |
| EC-17, EC-18 | Dependency-permutation and conflict tests | Dependency graph or isolation predicate and concurrent trace | A business-level postcondition not included in the predicate |
| EC-19 | Freshness or version fence | Observation version, delay or supersession fault and refusal or re-read | Freshness of a claim about a verifier report |
| EC-20 | Retry and amplification budget test | Injected fault, attempt and effect identifiers and bounded count | Ordinary single-attempt delivery ordering |

## How to read an `available` row

A register row naming one of these controls says the control is the right shape for that failure, and the row's **availability** says whether a control of that shape exists at all. Neither says it is installed in your environment.

**This catalogue carries no install state.** Whether any control here is switched on somewhere is a fact about one environment on one date — an assessment, not a catalogue entry — and it is recorded as one. The register diagrams carry none either, because a figure travels without the paragraph that would say whose codebase it means.

That was not true until 2026-09-07, and the correction is worth stating rather than quietly applied: 84 cells across these registers used to carry the derivation codebase's install state, and this section used to tell you they did not. `TL-09` is what it cost — it published "not built" for mutation and property testing while both were running in that codebase's CI, and nothing announced the staleness, because a status column does not announce its own age.

---

*False Floors is a trade mark of Digital First Pty Ltd, trading as Scale100 (AU application AMCZ-2616155657). This content is CC BY 4.0; the name is not part of that licence. Citing, mapping to, or claiming conformance with the catalogue needs no permission – see `LICENSE-CONTENT`.*

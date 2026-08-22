---
date: 2026-08-08
type: topic-brief
status: active
project: agent-trust-framework
covers: [six governance questions, seven diagnostic registers, Evidence, Truth, Provenance, Execution and Capability, public standard]
sources:
  - "[[my-work/ai-conversations/anatomy-of-an-agent-commercial-licensing-2026-08-08-raw]]"
  - "[[Insights Log]]"
  - "[[registers/README]]"
last-updated: 2026-08-19
---

# Six governance questions and seven diagnostic registers

> **Note added 2026-08-19 — the filename predates D-065 and is deliberately not being changed.** This file was written on 8 August 2026, when the model was five governance domains over six registers. On 9 August, D-064 rejected the pyramid but kept the scope finding under it, and **D-065 made Execution and Capability a seventh peer register and a governance question in its own right: "the public model becomes six governance questions / seven diagnostic registers."** D-070 repaired that register's headline question the same day. The body below has been brought to that architecture; `five-domain-six-register-architecture.md` is kept as the filename **only so the existing wikilinks to it keep resolving** — renaming it would break every reference. Treat the name as an address, never as a statement of the count.

## Current conclusion

The model has **six governance questions for communication and decision-making** and **seven diagnostic registers for professional analysis**.

| Governance domain | Executive question | Diagnostic register |
|---|---|---|
| Authority | What may the agent reach or cause? | Authority and Access |
| Context | Did it receive the right, current and permitted information? | Context |
| Instruction | Which rules governed it, and were they followed? | Instruction |
| Execution and Capability | Did the work it produced actually hold up? | Execution and Capability |
| Evidence | Can we reconstruct what happened and rely on the result? | Provenance + Truth |
| Recovery | Can failure be detected, contained and reversed? | Recovery |

**Execution and Capability is the question added by D-065, and its register is a decided stub with no rows** — [[execution-capability-layer]]. Its register-side question is the canonical one from that file: *for a declared unit of work, which required properties of the produced behaviour or available capability were violated or absent, and what was observed?* Nothing may quote a count, an outcome distribution or a built state for it, because none exists.

**One open item for the executive phrasing, flagged rather than settled here.** The executive question above is taken verbatim from [[cornerstone-content-strategy]] §5, corrected under C-51; the 2026-08-19 hub page draft phrases the same question as *"Was the work done correctly?"*. Two published wordings for one question is a drift risk, and picking between them is a content decision, not a correction — it is left open.

The governing sentence is:

> **We group by decision and split by failure mechanism.**

## Why six and seven are both necessary

The six-question view is not a simplified marketing version of a truer seven-part model. It is the executive decision architecture. Evidence is one governance decision because leaders ultimately need one answer: whether the account of the agent's work is defensible.

Professional analysis requires two non-substitutable tests:

1. **Provenance:** Can the organisation reconstruct the inputs, instructions, tools, actions, versions, reviewers and approvals?
2. **Truth:** Does independent evidence support the claims, outputs and conclusions?

Strong provenance can document the wrong test, an obsolete requirement or a false conclusion. A correct result can also be unauditable. The failure modes, evidence and remedies differ, so the registers remain separate.

## The Evidence rule

Evidence passes only when both Truth and Provenance pass.

| | Truth supported | Truth unsupported |
|---|---|---|
| Strong provenance | Defensible result | Auditable but wrong |
| Weak provenance | Possibly correct but unauditable | Opaque and unreliable |

No averaging is allowed. Strong traceability must not offset weak verification, and apparent correctness must not offset the absence of a defensible record.

## Why not use seven everywhere

Top-level domains are not intended to expose every analytically distinct mechanism. If they were, Authority would also split into identities, permissions, enforcement and delegation; Context would split into source authority, retrieval, freshness and isolation. The model would become a catalogue rather than a governance framework.

Six gives a stable set of decisions. Seven gives enough diagnostic resolution to identify control owners and remedies without losing the public model's coherence.

## Public and professional use

Public material may disclose the full architecture, including the fact that Evidence splits into Truth and Provenance. Commercial value must not depend on hiding one of the register headings.

The professional product consists of maintained register definitions, evidence requirements, scoring and escalation rules, calibration cases, platform adapters, report formats, benchmark data and authorised use—not secrecy about the taxonomy.

## Canon relationship

The seven register files under [[registers/README]] remain the analytical sources — six populated, and Execution and Capability a decided stub with no rows yet. This brief owns the relationship between the public six-question presentation and those seven registers. If a public description and a register disagree on analytical detail, the register wins; if a register is used to redefine the public domain structure, this brief must be revised explicitly.

## Validation still required

- Test whether independent reviewers classify the same cases consistently.
- Confirm that Evidence's worse-of-Truth-and-Provenance rule produces decision-useful outcomes.
- Test the architecture outside Claude Code using at least one enterprise agent platform and one materially different deployment.
- Confirm that public audiences understand the six/seven distinction without treating it as artificial product gating.

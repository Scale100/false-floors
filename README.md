# False Floors

**Every way your agent fails, and what catches it.**

False Floors is an agent assurance framework: a catalogue of the ways coding agents fail, and what actually catches each one.

A false floor is a board you put weight on because you believed something was holding it up – and nothing was. It is false **by construction, not by fraud** – nobody built the hollow board to deceive you. It looks solid from above because the finish of a board tells you nothing about the support beneath it. You find the hollow point by standing on it.

Three words carry the metaphor, and they mean the same thing everywhere in this catalogue. The **floor** is the business: the accumulated work everyone stands on, laid board by board, by people and now by agents. A **board** is one unit of work you put weight on: a report you act on, a fix you ship, a number you quote. The **support** under a board is whatever holds it up – the worker's competence at that task, and the control that is supposed to catch its absence. A board can be hollow from either side: the competence was never there, or the thing meant to catch the failure was itself the failure.

Every row is one failure mode. For each, the catalogue records where it can be caught inside the agent's turn, what mechanism catches it, whether that mechanism prevents the failure, merely detects it, or leaves it to survive – and what is left over that nothing covers. Every row also carries an evidence label: **evidenced** – a recorded incident, an independently coded finding, or a citable public case has been recorded against it – or **candidate** – named in advance, no receipt yet. Headline counts count evidenced rows only; the inclusion rule, the receipts and the prediction record are in `METHODOLOGY.md`.

The last part is the point. Most published guidance tells you what to do. This tells you what your controls still do not cover after you have done it.

## What is in here

| | |
|---|---|
| `registers/*-layer.md` | The catalogue itself, as markdown. Seven questions, one register each. Six are published; the seventh, execution and capability, is a stub with no rows yet and is marked as such. |
| `registers/README.md` | How to read a row: the columns, the class letters, the evidence labels, and the two registers that read their class words differently. |
| `METHODOLOGY.md` | How the rows were derived, what a row has to prove before it is counted, how the set has been tested, the prediction record, and what we already know is wrong with it. |

That is the whole of this release, on purpose. **This first cut is the catalogue and its method, and nothing else.** Clone it or download the zip and read the registers – that is what it is for today.

The tooling that surrounds the catalogue in our own work – the extraction script, the checker that fails a build when a page states counts the registers disagree with, and a single-page self-assessment tool – is real and in use, and it is not in here yet. It ships when it is ready to be read by other people, as its own release with its own note. Nothing has been removed to keep it back; it has simply not been published yet.

## Reporting a failure

If you have hit something, [open an incident](../../issues/new?template=incident.yml). One free-text box. Describe what happened in your own words.

**You do not have to work out which register it belongs to.** That is the maintainers' job, and getting it wrong is not a problem you can cause – two experienced coders working this catalogue independently agreed with each other only about six times in ten, so nobody is expecting a first-time reporter to out-perform that.

Every incident gets a public verdict on the thread:

| Verdict | What it means |
|---|---|
| `verdict: new row` | Nothing in the catalogue owned this. A row is being added, and you are credited on it. |
| `verdict: covered – fix exists` | Already catalogued, and there is a mechanism that catches it. The thread will point you at the row. |
| `verdict: covered – no fix` | Already catalogued, and nothing available catches it completely. The row says so. |
| `verdict: not an instance` | Reasoning given on the thread. Sometimes the answer is that the agent did what it was told. |

If your failure involves production details you cannot post in public, see [SECURITY.md](SECURITY.md) for the private channel.

## Contributing

Corrections to rows, new failure modes, and mechanisms that catch something a row currently leaves open are all welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). Contributors are credited on the rows they cause to change.

## Licence

Two licences, because code and catalogue get reused differently.

- **Register content**, and anything derived from it, is [CC BY 4.0](LICENSE-CONTENT). Use it, quote it, build on it, map your own framework onto it. Attribution is the only condition. This release is all content, so this is the licence that governs it.
- **Code** is [MIT](LICENSE) – embed it in your own pipeline without an attribution obligation in your interface. No code ships in this release; the licence is settled in advance so that it is not a question when it does.

## What this does not claim

- **It is not a security framework, and does not replace one.** It asks whether an agent's work can be trusted, not whether the agent is under attack. The two are different questions and you need both. Where it overlaps established security control sets, the mapping notes say so.
- **It is not a certification, a score, or a pass mark.** There is no badge that says you are safe.
- **The evidence base is stated per row, not asserted in general.** Rows record whether a failure has actually been seen and recorded, or is derived. Do not read an entry as a field-frequency claim.
- **Counts are in the registers, not in this file**, on purpose. Numbers copied by hand between documents go stale, and this catalogue has been bitten by exactly that. The registers are the source; a page that disagrees with them is a defect in the page.

---

*False Floors is a trade mark of Digital First Pty Ltd, trading as Scale100 (Australian trade mark application AMCZ-2616155657). Citing the catalogue, mapping to it, or claiming conformance with it needs no permission – see [LICENSE-CONTENT](LICENSE-CONTENT).*

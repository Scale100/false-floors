# False Floors

*an agent assurance framework*

**A catalogue of the ways coding agents fail, and what actually catches each one.**

A false floor is a control you are standing on that is not carrying your weight. It is false **by construction, not by fraud** – nobody is deceiving you. The rule really is in the file, the test really did run, the permission really was set. The floor is false because the mechanism does not do the job you believe it is doing, and nothing tells you that until you put weight on it.

Every row is one failure mode. For each, the catalogue records where it can be caught inside the agent's turn, what mechanism catches it, whether that mechanism prevents the failure, merely detects it, or leaves it to survive – and what is left over that nothing covers. Every row also carries an evidence label: **evidenced** – a recorded incident, an independently coded finding, or a citable public case has landed on it – or **candidate** – named in advance, no receipt yet. Headline counts count evidenced rows only; the inclusion rule, the receipts and the prediction record are in `registers/METHODOLOGY.md`.

The last part is the point. Most published guidance tells you what to do. This tells you what your controls still do not cover after you have done it.

## What is in here

| | |
|---|---|
| `registers/` | The catalogue itself, as markdown. Seven questions, one register each. Six are published; the seventh, execution and capability, is a stub with no rows yet and is marked as such. |
| `register-data.json` | The same rows as data, generated from the registers by `extract-registers.mjs`. Never hand-edited. |
| `trust-check/` | A single-page web tool. Answer some questions about your setup, get back the rows you are exposed on. |
| `tools/` | The checker scripts, including the one that fails a build when a page states counts the registers disagree with. |

## The tool runs locally and sends nothing

No accounts, no sign-up, no analytics, no submission, no telemetry. Open the page and it works offline. Read the source before you run it – that is the point of shipping it as one file with no dependencies.

If a future version ever collects anything, it will say so on the page, ask first, and be a separate decision made in the open. It will not be added quietly.

## Reporting a failure

If you have hit something, [open an incident](../../issues/new?template=incident.yml). One free-text box. Describe what happened in your own words.

**You do not have to work out which register it belongs to.** That is the maintainers' job, and getting it wrong is not a problem you can cause – two experienced coders working this catalogue independently agreed with each other only about six times in ten, so nobody is expecting a first-time reporter to out-perform that.

Every incident gets a public verdict on the thread:

| Verdict | What it means |
|---|---|
| `verdict: new row` | Nothing in the catalogue owned this. A row is being added, and you are credited on it. |
| `verdict: covered, fix exists` | Already catalogued, and there is a mechanism that catches it. The thread will point you at the row. |
| `verdict: covered, no fix` | Already catalogued, and nothing available catches it completely. The row says so. |
| `verdict: not an instance` | Reasoning given on the thread. Sometimes the answer is that the agent did what it was told. |

If your failure involves production details you cannot post in public, see [SECURITY.md](SECURITY.md) for the private channel.

## Contributing

Corrections to rows, new failure modes, and mechanisms that catch something a row currently leaves open are all welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). Contributors are credited on the rows they cause to change.

## Licence

Two licences, because code and catalogue get reused differently.

- **Register content**, and anything derived from it, is [CC BY 4.0](LICENSE-CONTENT). Use it, quote it, build on it, map your own framework onto it. Attribution is the only condition.
- **Code** – the checker scripts, the trust-check tool, the extraction script – is [MIT](LICENSE). Embed it in your own pipeline without an attribution obligation in your interface.

## What this does not claim

- **It is not a security framework, and does not replace one.** It asks whether an agent's work can be trusted, not whether the agent is under attack. The two are different questions and you need both. Where it overlaps established security control sets, the mapping notes say so.
- **It is not a certification, a score, or a pass mark.** There is no badge that says you are safe.
- **The evidence base is stated per row, not asserted in general.** Rows record whether a failure has actually been seen and recorded, or is derived. Do not read an entry as a field-frequency claim.
- **Counts are in the registers, not in this file**, on purpose. Numbers copied by hand between documents go stale, and this catalogue has been bitten by exactly that. The registers are the source; a page that disagrees with them is a defect in the page.

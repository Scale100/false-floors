# Contributing to False Floors

There are three useful things you can do here, in rough order of how much they help.

## 1. Report a failure you hit

[Open an incident.](../../issues/new?template=incident.yml) One free-text box, in your own words.

**Do not try to classify it.** You are not expected to know which register it belongs to, and you cannot get that wrong in a way that costs anything, because you are not asked. Mis-filing is the maintainers' problem by design.

An incident is worth reporting even if you think it is obvious, even if you suspect it is your own fault, and even if you already fixed it. "Obvious" failures that nobody wrote down are the most valuable rows in the catalogue.

## 2. Correct a row

If you have read a row and it is wrong, incomplete, or its mechanism does not do what it says, [open a correction](../../issues/new?template=register-correction.yml) citing the row ID. Disputing a specific published row is the one place naming a register is the right thing to do.

The strongest correction names a mechanism that catches something the row currently records as uncovered. That moves a row leftwards, which is the whole purpose of the catalogue.

## 3. Send a pull request

For typos, broken links, clearer wording and mechanism details, a pull request is faster than an issue. For anything that changes what a row *claims*, open an issue first – rows carry evidence rules that are easier to sort out in discussion than in review.

### Rules that apply to any change to a row

1. **Row IDs are stable and permanent.** `IL-3B` means the same failure for ever. A row can be reworded, re-mechanised or superseded, but never renumbered and never re-pointed at a different failure. Things outside this repository cite these IDs.
2. **A mechanism claim needs to say where it runs.** "Add a rule to your instructions file" is not a mechanism unless something checks the rule was followed. A control nobody invokes catches nothing, and the catalogue treats asserted wiring and absent wiring as the same thing.
3. **Say what is left over.** Every row states its gap – what it still does not cover. A change that improves a mechanism without updating the gap is incomplete.
4. **Do not state counts in prose.** Totals live in the registers, and a document that states a count the registers disagree with is wrong by definition – the registers are the source. We check this with a script on our side; it is not in this repository yet, so for now the rule is a rule rather than a build failure.

## Credit

**Every row created or materially changed by a report carries the reporter's handle.** If your incident becomes a row, your name is on the row, not just in a thread, and it stays there. If your correction changes what a row claims, the same applies.

This is not a courtesy. The catalogue is only worth anything if it reflects what happens to people other than its author, and the credit line is the honest record of that.

## What happens to your report

Every incident gets one of four public verdicts, as a label plus a closing comment:

| Verdict | Meaning |
|---|---|
| `verdict: new row` | Not covered. A row is being added; you are credited. |
| `verdict: covered – fix exists` | Already catalogued, with a mechanism that catches it. |
| `verdict: covered – no fix` | Already catalogued; nothing available catches it completely. |
| `verdict: not an instance` | Not a failure of the kind this catalogue tracks. Reasoning on the thread. |

Verdicts are public so the catalogue's coverage can be argued with. A closed issue with no verdict is a maintainer error – reopen it.

## Licensing your contribution

By contributing you agree that your contribution is licensed on the same terms as the rest of the repository: **register content and anything derived from it under [CC BY 4.0](LICENSE-CONTENT), and code under [MIT](LICENSE)**.

You keep the copyright in what you wrote. There is no copyright assignment and no contributor licence agreement to sign.

## What is out of scope

- **Vendor-supplied controls are baseline, not recommendations.** A mechanism your harness already ships and switches on by default belongs in the row's baseline, not in its list of things to install.
- **Prompt and instruction wording is not a mechanism.** Better-worded rules are welcome as advice elsewhere; they do not close a row, because prose decays under pressure and that is most of what this catalogue is about.
- **Security-only findings** – prompt injection, jailbreaks, adversarial attacks – are a different question with better-resourced homes. If an adversary is required for the failure, this is probably not the right catalogue. Report it anyway if you are unsure; sorting that out is not your job.

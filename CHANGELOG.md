# Changelog

## 0.2.2

- Sync the `RequirementsPack` generator version with the package version: 0.2.1 packs still wrote
  `generator.version: "0.2.0"`. `tests/version-sync.test.ts` now pins `src/version.ts` to
  `package.json`, so the next release cannot drift again. No rule or report change.

## 0.2.1

- Require `dsh-table-ingest` `^0.2.1`, which adds the ZIP entry-count, per-entry and cumulative output budgets requested in the dshopen review. No rule or report change.

## 0.2.0

Adds the `RequirementsPack` and the three queues — the producer half of the tender
spec. `mode=extract` keeps the 0.1.0 behaviour.

- **Three queues, not one list.** A 交付 (verified verbatim, in a binding section,
  no hedge), B 待确认 (quoted but structurally weak), C 必须处理 (not quotable, or
  hedged, or referenced elsewhere). A single merged list is what lets a tool report
  "no findings" when it actually found nothing it could quote.
- **Queue C is a gate.** While it is non-empty the pack reports `deliverable: false`
  and the report says the check is 未完成体检 — it must not be presented as a
  delivered list.
- **Coverage net over ten topics**, each reported as hit or explicitly
  "not found — this does not mean the document omits it".
- Clause families (`refuse` / `invalid` / `reject` / `disqualify` / `deviation` /
  `postAward`) rather than one keyword table, following the spec's probe where a
  result-word-only list hit 12/24 and a trigger-word-only list hit 15/24 with over
  half being the buyer's own obligations.
- Fixes the composition reader: numbering must now run consecutively, so a section
  heading like `3.7 投标文件的递交` is no longer appended as entry 7 of the previous
  chapter's list.
- Clause titles are anchored on the clause word, not on the first comma: the old
  rule titled 「原则上，投标有效期不足的按无效投标处理」 as 「原则上」.
- 27 tests.


## 0.1.0

First release. Extraction, not adjudication: every item is reported whether or not
it was found.

- Front-appendix values (deadline, opening, deposit, validity, ceiling, copies,
  sealing) read from two-column tables; body-text hits get a lower confidence and
  say why.
- Copy counts accept Chinese numerals and the comma-separated form
  (`正本一份，副本四份`), which the obvious `\d+` regex misses.
- **Recovers a requirement that the header detector consumed as the header row.**
  When the detected header's second cell looks like a date, amount or count, the
  pair is treated as data too — otherwise a plainly stated deadline went missing.
- Composition list read from a run of numbered entries after a lead-in sentence.
- 18 tests over a generated tender document.

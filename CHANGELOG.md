# Changelog

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

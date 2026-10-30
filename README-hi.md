# dsh-tender-requirements — Tender requirements (हिन्दी)

[English](README.md) · [简体中文](README-zh.md) · [Español](README-es.md) · [Português](README-pt.md) · [हिन्दी](README-hi.md)

[![dshfind](https://dshfind.com/api/badge/PerryLink/dsh-tender-requirements?metric=downloads)](https://dshfind.com/en/plugins/PerryLink/dsh-tender-requirements?ref=badge)

`dsh-tender-requirements` निविदा दस्तावेज़ पढ़कर बताता है कि क्या मिला: अग्र-परिशिष्ट की समय-सीमा, जमानत, वैधता और उच्चतम सीमा; निविदा की अपेक्षित संरचना; और मूल व प्रतियों की संख्या।

जो खोजा गया वह हर मद छपती है, मिले या न मिले। «नहीं मिला» और «दस्तावेज़ में नहीं है» दो अलग वाक्य हैं, और कीवर्ड निष्कर्षण केवल पहले को सहारा दे सकता है।

## Install

```sh
dsh plugin --profile <name> add dsh-tender-requirements
dsh --profile <name> --dump-config | grep 'dsh-tender-requirements'
```

## What it looks like

![Workflow diagram for dsh-tender-requirements: document → rule pack → findings.](docs/assets/dsh-tender-requirements-flow.svg)

*Workflow overview: document → rule pack → findings.*

**सीमा:** यह खोजक है, समीक्षक नहीं। यह नहीं आँकता कि दस्तावेज़ अनुरूप है या निविदा जीतेगी। यह **केवल मुख्य दस्तावेज़** पढ़ता है — स्पष्टीकरण, संशोधन और प्रश्नोत्तर क़ानूनन दस्तावेज़ का हिस्सा हैं और यहाँ नहीं जोड़े जाते, जो एक ज्ञात व्यवस्थागत कमी है।

## What it answers

- अग्र-परिशिष्ट कौन-सी समय-सीमा, जमानत, वैधता और उच्चतम सीमा बताता है?
- निविदा में क्या-क्या और किस क्रम में होना चाहिए?
- कितने मूल और कितनी प्रतियाँ चाहिए?
- कौन-सी मदें **नहीं** मिलीं और हाथ से पुष्टि करनी चाहिए?

## Standards it follows

पैक जाँच के आधार के रूप में कोई अनुच्छेद उद्धृत नहीं करता क्योंकि यह निष्कर्षण करता है, जाँच नहीं। यह उस संरचना को कूटबद्ध करता है जो अनुच्छेदों से निकलती है: आदेश 87 का अनुच्छेद 20 अनिवार्य 16 मदें गिनाता है, और निविदा विधि का अनुच्छेद 23 कहता है कि स्पष्टीकरण **दस्तावेज़ का भाग है** — ज्ञात कमी के रूप में दर्ज।

## Compatibility

| Surface | Status |
|---|---|
| Harness | peer range `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` |
| Node | `^22.19.0 || >=24.0.0` |
| Platforms | all (pure ESM; no native code, no network, no model call) |

## What it does

Recognition is per item, not one keyword table. Each item carries its own pattern and reports a confidence with a reason: 高 when found in a two-column front-appendix key, 中 in body text, 低 when not found. Copy counts accept Chinese numerals and the comma-separated form.

## Configuration

| Key | Default | Meaning |
|---|---|---|
| `rulesFile` | `rules/tender-requirements.yaml` | 规则库路径 |

## Material format

Input is a `.docx`. Tables are read through `dsh-table-ingest` one candidate at a time, because the front appendix is not necessarily the first table.

## Rule sources

No evidence directory: nothing here cites a clause as the basis of a finding. Known limits: only the main document is read; the front appendix must be a two-column table; the composition list must be a run of at least three numbered entries; and unusual wording is reported as not retrieved rather than guessed.

## Troubleshooting

- **The plugin installs but the tool never appears**: check that `main` resolves to `lib/index.mjs` and that `pnpm run build` produced it.
- **`dsh plugin add` rejects the package**: the peer range covers `0.1.x` and `0.2.x`; outside it, grant an explicit exemption.
- **A rule did not run**: read the `skipped` array.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-tender-requirements
```

## PerryLink DSH Plugin Family

Full family index: [choose a checker by material](https://perrylink.github.io/zh/checkers/choose/) and [all plugins](https://github.com/PerryLink). This repository is one of them.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-tender-requirements contributors.

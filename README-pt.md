# dsh-tender-requirements — Tender requirements (Português)

[English](README.md) · [简体中文](README-zh.md) · [Español](README-es.md) · [Português](README-pt.md) · [हिन्दी](README-hi.md)

[![dshfind](https://dshfind.com/api/badge/PerryLink/dsh-tender-requirements?metric=downloads)](https://dshfind.com/en/plugins/PerryLink/dsh-tender-requirements?ref=badge)

`dsh-tender-requirements` lê um caderno de encargos e reporta o que conseguiu encontrar: prazos, garantia, validade e teto do anexo inicial; a composição exigida da proposta; e o número de originais e cópias.

Cada item procurado é impresso, tenha sido encontrado ou não. «Não recuperado» e «o documento não o diz» são frases diferentes, e só a primeira um extrator por palavras-chave pode sustentar.

## Install

```sh
dsh plugin --profile <name> add dsh-tender-requirements
dsh --profile <name> --dump-config | grep 'dsh-tender-requirements'
```

## What it looks like

![Workflow diagram for dsh-tender-requirements: document → rule pack → findings.](docs/assets/dsh-tender-requirements-flow.svg)

*Workflow overview: document → rule pack → findings.*

**Limite:** é um localizador, não um revisor. Não julga se o caderno cumpre a norma nem se uma proposta ganhará. Lê **apenas o documento principal**: esclarecimentos, alterações e atas de perguntas são parte do caderno por lei e não são fundidos aqui, o que é uma lacuna sistemática conhecida.

## What it answers

- Que prazo, garantia, validade e teto indica o anexo inicial?
- O que deve conter uma proposta e em que ordem?
- Quantos originais e cópias são exigidos?
- Que itens **não** foram recuperados e devem ser confirmados à mão?

## Standards it follows

O pacote não cita cláusulas como base de verificação porque extrai, não verifica. Codifica a estrutura que as cláusulas implicam: o artigo 20.º da Portaria 87 enumera os 16 elementos obrigatórios, e o artigo 23.º da Lei das Empreitadas declara que um esclarecimento **é parte do caderno** — registado como lacuna conhecida.

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

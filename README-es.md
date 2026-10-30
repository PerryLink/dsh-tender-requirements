# dsh-tender-requirements — Tender requirements (Español)

[English](README.md) · [简体中文](README-zh.md) · [Español](README-es.md) · [Português](README-pt.md) · [हिन्दी](README-hi.md)

[![dshfind](https://dshfind.com/api/badge/PerryLink/dsh-tender-requirements?metric=downloads)](https://dshfind.com/en/plugins/PerryLink/dsh-tender-requirements?ref=badge)

`dsh-tender-requirements` lee un pliego de licitación e informa qué pudo encontrar: los plazos, la garantía, la validez y el techo del anexo inicial; la composición exigida de la oferta; y el número de originales y copias.

Se imprime cada elemento buscado, se haya encontrado o no. «No recuperado» y «el pliego no lo dice» son frases distintas, y solo la primera puede sostenerla un extractor por palabras clave.

## Install

```sh
dsh plugin --profile <name> add dsh-tender-requirements
dsh --profile <name> --dump-config | grep 'dsh-tender-requirements'
```

## What it looks like

![Workflow diagram for dsh-tender-requirements: document → rule pack → findings.](docs/assets/dsh-tender-requirements-flow.svg)

*Workflow overview: document → rule pack → findings.*

**Límite:** es un localizador, no un revisor. No juzga si el pliego cumple la normativa ni puede decir si una oferta ganará. Lee **solo el documento principal**: aclaraciones, modificaciones y actas de preguntas son parte del pliego por ley y no se fusionan aquí, lo que es una laguna sistemática conocida.

## What it answers

- ¿Qué plazo, garantía, validez y techo indica el anexo inicial?
- ¿Qué debe contener una oferta y en qué orden?
- ¿Cuántos originales y copias se exigen?
- ¿Qué elementos **no** se recuperaron y deben confirmarse a mano?

## Standards it follows

El paquete no cita cláusulas como base de una comprobación porque extrae, no comprueba. Codifica la estructura que las cláusulas implican: el artículo 20 de la Orden 87 enumera los 16 elementos que debe contener un pliego, y el artículo 23 de la Ley de Licitaciones declara que una aclaración **es parte del pliego** — recogido como laguna conocida.

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

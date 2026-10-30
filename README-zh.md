# dsh-tender-requirements — 招标文件要点抽取

[English](README.md) · [简体中文](README-zh.md) · [Español](README-es.md) · [Português](README-pt.md) · [हिन्दी](README-hi.md)

<!-- topblock:v1 -->
> **这是什么**　从一份招标文件里抽出时间、保证金、投标文件组成与份数，逐项告诉你有没有检索到。
> **给谁用**　投标专员、招标代理。
> **你交什么**　一份招标文件；抽取时间、保证金、投标文件组成与份数。
> **它不做什么**　不判合规、不认定责任、不替代审核人；只列材料内部能逐条指认的差异。
> **怎么开始**　命令行安装（暂未单独上架）：
> `dsh plugin --profile <name> add dsh-tender-requirements`
<!-- /topblock:v1 -->

[![dshfind](https://dshfind.com/api/badge/PerryLink/dsh-tender-requirements?metric=downloads)](https://dshfind.com/en/plugins/PerryLink/dsh-tender-requirements?ref=badge)

`dsh-tender-requirements` 读一份招标文件，报告能找到什么：前附表的截止时间、保证金、投标有效期、最高限价；投标文件组成清单；正本与副本份数。

每一项都会打印，不管找没找到。**「未检索到」和「文件里没写」是两句话**，关键词抽取只支撑得起前一句。

## Install

```sh
dsh plugin --profile <name> add dsh-tender-requirements
dsh --profile <name> --dump-config | grep 'dsh-tender-requirements'
```

## What it looks like

![Workflow diagram for dsh-tender-requirements: document → rule pack → findings.](docs/assets/dsh-tender-requirements-flow.svg)

*Workflow overview: document → rule pack → findings.*

**边界：** 这是抽取器，不是审阅器。它不判断招标文件是否合规，也不能判断能不能中标。它只读**主文件**——澄清、修改、补遗、答疑纪要依法都是招标文件的组成部分（招标投标法第23条），本工具不合并，这是已知的系统性漏检源，请人工合并。它也不会断言某条款不存在：措辞不同就是没匹配上。

## What it answers

- 前附表写的截止时间、保证金、有效期、最高限价各是什么？
- 投标文件要包含哪些内容、按什么顺序？
- 正本与副本各要几份？
- 哪几项**没检索到**，需要人工确认？

## Standards it follows

本包不引用条款作为判定依据，因为它是抽取不是检查。它编码的是条款隐含的结构：

- 政府采购货物和服务招标投标管理办法（87号令）第20条列出招标文件必须包含的 16 项，其中就有「评标方法、评标标准和投标无效情形」——这就是前附表是信息枢纽的原因。
- 招标投标法第23条：澄清或修改**是招标文件的组成部分**。本包把它列为已知缺口，因为那是最大的漏检来源。

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

完整清单（62 个核查器 + 通用插件）见 [按材料选核查器](https://perrylink.github.io/zh/checkers/choose/)；本仓只是其中一个。

## License

[Apache License 2.0](LICENSE) © 2026 dsh-tender-requirements contributors.

/**
 * Markdown report for a tender extraction.
 *
 * Every item is printed whether or not it was found, and a not-found item says
 * "not retrieved — please confirm" rather than "absent". A report that listed only
 * the hits would let a missing deposit clause look like a document that has none.
 */

import type { Extraction } from './model.ts'

const CONFIDENCE_LABEL: Record<string, string> = { high: '高', medium: '中', low: '低' }

/**
 * Render the extraction as markdown.
 *
 * @param extraction - the extraction result.
 * @param source - the document path.
 * @returns markdown text.
 */
export function renderMarkdown(extraction: Extraction, source: string): string {
  const lines: string[] = []
  const found = extraction.items.filter((item) => item.value !== '')
  const missing = extraction.items.filter((item) => item.value === '')

  lines.push('# 招标文件关键信息抽取')
  lines.push('')
  lines.push(`- 检查对象：${source}`)
  lines.push(`- 扫描范围：${extraction.coverage.paragraphs} 个段落、${extraction.coverage.tables} 张表`)
  lines.push(`- 结果：检索到 ${found.length} 项 · 未检索到 ${missing.length} 项（共查 ${extraction.items.length} 项）`)
  lines.push('')
  lines.push('## 检索到')
  lines.push('')
  if (found.length === 0) {
    lines.push('本次一项也没有检索到；请确认文件是否为招标文件正文，或前附表是否为两列表格。')
  } else {
    lines.push('| 项目 | 值 | 出处 | 置信度 | 为什么是这个置信度 |')
    lines.push('|---|---|---|---|---|')
    for (const item of found) {
      lines.push(`| ${item.label} | ${item.value.replace(/\|/gu, '\\|')} | ${item.source} | ${CONFIDENCE_LABEL[item.confidence] ?? item.confidence} | ${item.reason} |`)
    }
  }

  if (extraction.frontRows.length > 0) {
    lines.push('')
    lines.push('## 前附表（识别为两列表格）')
    lines.push('')
    lines.push('| 行 | 键 | 值 |')
    lines.push('|---|---|---|')
    for (const row of extraction.frontRows.slice(0, 40)) {
      lines.push(`| ${row.row} | ${row.key.replace(/\|/gu, '\\|')} | ${row.value.replace(/\|/gu, '\\|')} |`)
    }
    if (extraction.frontRows.length > 40) lines.push(`| … | 另有 ${extraction.frontRows.length - 40} 行 | |`)
  }

  if (extraction.composition.length > 0) {
    lines.push('')
    lines.push('## 投标文件组成清单')
    lines.push('')
    extraction.composition.forEach((entry, index) => lines.push(`${index + 1}. ${entry}`))
  }

  if (extraction.copies.raw !== '') {
    lines.push('')
    lines.push('## 份数')
    lines.push('')
    lines.push(`- 原文：${extraction.copies.raw}`)
    lines.push(`- 解析：正本 ${extraction.copies.original ?? '未解析'} 份 · 副本 ${extraction.copies.duplicate ?? '未解析'} 份`)
    if (extraction.copies.original === null && extraction.copies.duplicate === null) {
      lines.push('- ⚠️ 两种份数都没解析出来；中文数字与「正本一份，副本四份」这类句式都试过了，请人工核对')
    }
  }

  if (missing.length > 0) {
    lines.push('')
    lines.push('## 未检索到（请人工确认）')
    lines.push('')
    for (const item of missing) {
      lines.push(`- **${item.label}**：${item.reason}`)
    }
  }

  if (extraction.warnings.length > 0) {
    lines.push('')
    lines.push('## 提示')
    lines.push('')
    for (const warning of extraction.warnings) lines.push(`- ${warning}`)
  }

  lines.push('')
  lines.push('## 边界')
  lines.push('')
  lines.push('本报告只做信息抽取，不判断招标文件是否合规，也不判断投标人能否中标。')
  lines.push('「未检索到」不等于「文件里没有」：抽取基于关键词与结构，措辞不同就可能漏。请务必人工复核后再据此编制投标文件。')
  lines.push('只解析了主文件：澄清、修改、补遗、答疑纪要同样是招标文件的组成部分，本工具不覆盖，需人工合并。')
  lines.push('')
  return lines.join('\n')
}

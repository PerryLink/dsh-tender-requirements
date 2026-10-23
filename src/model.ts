/**
 * Extraction from a tender document.
 *
 * This is a *finder*, not an adjudicator. Every item it looks for is reported in
 * one of three states — found, not found, or found but ambiguous — and "not found"
 * is never rendered as "does not exist". A tender document that says nothing about
 * a deposit and one that says the deposit is zero are different documents, and a
 * report that collapses them would be worse than no report.
 *
 * Nothing here is automated on a language model. The spec's finding is that a
 * single keyword table is unusable (result-only words hit 12/24 on constructed
 * data, trigger-only words hit 15/24 and were mostly the buyer's own obligations),
 * so each item carries its own recogniser and its own confidence.
 */

import { ingestToTable, ingestDocx, type TableJson } from 'dsh-table-ingest/api'

/** How sure the extractor is about one item. */
export type Confidence = 'high' | 'medium' | 'low'

/** One thing we went looking for. */
export interface ExtractedItem {
  /** Stable key, e.g. `deadline`. */
  key: string
  /** Human label. */
  label: string
  /** What was found, or empty when nothing was. */
  value: string
  /** Where it came from: page, table and row, or a paragraph ordinal. */
  source: string
  /** How much to trust the value. */
  confidence: Confidence
  /** Why this confidence, in one sentence. */
  reason: string
}

/** The whole extraction. */
export interface Extraction {
  /** Items looked for, whether or not they were found. */
  items: ExtractedItem[]
  /** Front-appendix rows that were recognised as key-value pairs. */
  frontRows: { key: string; value: string; row: number }[]
  /** Composition list entries, in document order. */
  composition: string[]
  /** Copy counts, when stated. */
  copies: { original: number | null; duplicate: number | null; raw: string }
  /** Paragraph count and table count, for the coverage statement. */
  coverage: { paragraphs: number; tables: number; sections: string[] }
  warnings: string[]
}

/** Raised when the document cannot be read at all. */
export class TenderError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'TenderError'
  }
}

/** Chinese numeral table, enough for the counts that appear in tender documents. */
const CN_DIGITS: Record<string, number> = {
  零: 0, 〇: 0, 一: 1, 二: 2, 两: 2, 三: 3, 四: 4, 五: 5, 六: 6, 七: 7, 八: 8, 九: 9,
}

/**
 * Read a Chinese or Arabic numeral.
 *
 * @param text - e.g. `四`, `十`, `十二`, `4`.
 * @returns the value, or null when it is not a numeral.
 */
export function readCount(text: string): number | null {
  const trimmed = text.trim()
  if (/^\d+$/u.test(trimmed)) return Number.parseInt(trimmed, 10)
  if (trimmed === '') return null
  let total = 0
  let current = 0
  for (const character of trimmed) {
    if (character in CN_DIGITS) {
      current = CN_DIGITS[character] ?? 0
      continue
    }
    if (character === '十') {
      total += (current === 0 ? 1 : current) * 10
      current = 0
      continue
    }
    return null
  }
  return total + current
}

/**
 * Extract copy counts from a sentence.
 *
 * The spec's probe found that `正本一份，副本四份` is missed by the obvious regex,
 * so the pattern must accept Chinese numerals and the comma-separated form.
 *
 * @param text - the sentence to read.
 * @returns the counts and the raw text they came from.
 */
export function readCopies(text: string): { original: number | null; duplicate: number | null; raw: string } {
  const numeral = '([0-9]+|[零〇一二两三四五六七八九十]+)'
  const original = new RegExp(`正本\\s*${numeral}\\s*份`, 'u').exec(text)
  const duplicate = new RegExp(`副本\\s*${numeral}\\s*份`, 'u').exec(text)
  return {
    original: original === null ? null : readCount(original[1] ?? ''),
    duplicate: duplicate === null ? null : readCount(duplicate[1] ?? ''),
    raw: text.trim(),
  }
}

/** Key phrases for the front appendix, each with its label and recogniser. */
const ITEMS: { key: string; label: string; test: RegExp }[] = [
  { key: 'deadline', label: '投标截止时间', test: /投标截止时间|递交投标文件截止时间|投标文件递交的截止时间/u },
  { key: 'opening', label: '开标时间', test: /开标时间|开启时间/u },
  { key: 'deposit', label: '投标保证金', test: /投标保证金/u },
  { key: 'validity', label: '投标有效期', test: /投标有效期/u },
  { key: 'ceiling', label: '最高限价', test: /最高限价|招标控制价|预算金额/u },
  { key: 'copies', label: '份数（正本/副本）', test: /正本|副本/u },
  { key: 'sealing', label: '密封要求', test: /密封/u },
  { key: 'siteVisit', label: '踏勘现场', test: /踏勘|现场考察/u },
  { key: 'clarify', label: '澄清/答疑截止', test: /澄清|答疑/u },
]

/**
 * Whether a cell reads as a value rather than as a column label.
 *
 * A front appendix's header row is normally `条款号 | 编列内容` — two labels. When
 * the second cell carries a date, an amount or a count instead, the row is data
 * and the header detector has simply chosen the first data row of a table whose
 * title row it scored too low to use. Treating that pair as a label pair would
 * silently drop one requirement.
 *
 * @param text - the cell's text.
 * @returns true when the text looks like a value.
 */
export function looksLikeValue(text: string): boolean {
  const trimmed = text.trim()
  if (trimmed === '') return false
  if (/[0-9０-９]/u.test(trimmed)) return true
  if (/[¥￥]/u.test(trimmed)) return true
  if (/(?:年|月|日|时|分|天|份|元|万|个|套|册|页)/u.test(trimmed)) return true
  return trimmed.length > 12
}

/**
 * Turn one table into key-value rows when it looks like a front appendix.
 *
 * A front appendix is a two-column table whose left column is a label. Requiring
 * exactly two columns keeps an unrelated 4-column schedule from being read as one.
 *
 * @param table - the parsed table.
 * @returns key-value rows, or an empty array when the shape does not fit.
 */
export function frontRowsOf(table: TableJson): { key: string; value: string; row: number }[] {
  if (table.columns.length !== 2) return []
  const [left, right] = table.columns
  if (left === undefined || right === undefined) return []
  const rows: { key: string; value: string; row: number }[] = []
  // When the detected header is itself a data pair, it is a requirement too.
  if (looksLikeValue(right) && left !== '') rows.push({ key: left, value: right, row: 1 })
  table.rows.forEach((row, index) => {
    const key = (row[left] ?? '').trim()
    const value = (row[right] ?? '').trim()
    if (key === '' || value === '') return
    rows.push({ key, value, row: index + 1 })
  })
  return rows
}

/** Lists whose entries start with a numbered or bracketed marker. */
const LIST_MARKER = /^\s*(?:[（(]?\d+[)）.、]|[（(][一二三四五六七八九十]+[)）]|[一二三四五六七八九十]+[、.])\s*/u

/**
 * Extract the bid-document composition list from paragraphs.
 *
 * @param paragraphs - document paragraphs in order.
 * @returns the entries, in order, when a run of at least three is found.
 */
export function compositionOf(paragraphs: string[]): string[] {
  const entries: string[] = []
  let started = false
  for (const paragraph of paragraphs) {
    const trimmed = paragraph.trim()
    if (!started) {
      if (/投标文件(?:的)?(?:组成|构成|内容)|投标文件应包括|投标文件应由以下/u.test(trimmed)) {
        started = true
        continue
      }
      continue
    }
    if (trimmed === '') {
      if (entries.length >= 3) break
      continue
    }
    if (LIST_MARKER.test(trimmed)) {
      entries.push(trimmed.replace(LIST_MARKER, '').trim())
      continue
    }
    // A non-list paragraph after the list started ends it.
    if (entries.length >= 3) break
    entries.length = 0
    started = false
  }
  return entries.filter((entry) => entry !== '')
}

/**
 * Read every table in a document.
 *
 * The ingest layer selects one table for a checker; a tender document has several
 * and the front appendix is not necessarily the first, so each candidate is read
 * by index and the two-column ones are kept.
 *
 * @param buffer - the docx bytes.
 * @param filename - for the target and error messages.
 * @returns every table the reader could parse.
 */
export function allTablesOf(buffer: Buffer, filename: string): TableJson[] {
  const probe = ingestToTable(buffer, filename)
  const count = probe.candidates.length
  const tables: TableJson[] = []
  for (let index = 0; index < count; index++) {
    try {
      const one = ingestToTable(buffer, filename, { tableIndex: index })
      if (one.ok && one.table !== undefined) tables.push(one.table)
    } catch {
      // A table the reader refuses is reported in the coverage statement rather
      // than aborting the whole document.
    }
  }
  if (tables.length === 0 && probe.table !== undefined) tables.push(probe.table)
  return tables
}

/**
 * Extract the items this version looks for.
 *
 * @param buffer - the docx bytes.
 * @param filename - for the target and error messages.
 * @returns the extraction with a coverage statement.
 */
export function extract(buffer: Buffer, filename: string): Extraction {
  const tables = allTablesOf(buffer, filename)
  if (tables.length === 0) throw new TenderError(`${filename} 中没有可读的表格；前附表通常是两列表格`)

  let paragraphs: string[] = []
  try {
    paragraphs = ingestDocx(buffer, filename).paragraphs
  } catch {
    paragraphs = []
  }

  const frontRows: { key: string; value: string; row: number }[] = []
  const frontTableIndexes: number[] = []
  tables.forEach((table, index) => {
    const rows = frontRowsOf(table)
    if (rows.length > 0) {
      frontRows.push(...rows)
      frontTableIndexes.push(index)
    }
  })

  const joinedValues = frontRows.map((row) => `${row.key} ${row.value}`).join('\n')
  const joinedParagraphs = paragraphs.join('\n')
  const haystack = `${joinedValues}\n${joinedParagraphs}`

  const items: ExtractedItem[] = ITEMS.map((item) => {
    const fromFront = frontRows.find((row) => item.test.test(row.key))
    if (fromFront !== undefined) {
      return {
        key: item.key,
        label: item.label,
        value: fromFront.value,
        source: `前附表第 ${fromFront.row} 行`,
        confidence: 'high',
        reason: '在前附表（两列表格）的键里命中',
      }
    }
    const paragraph = paragraphs.find((text) => item.test.test(text))
    if (paragraph !== undefined) {
      return {
        key: item.key,
        label: item.label,
        value: paragraph.trim().slice(0, 200),
        source: '正文段落',
        confidence: 'medium',
        reason: '正文里命中关键词，但没有前附表的结构约束，可能不是最终口径',
      }
    }
    const anywhere = haystack.includes(item.label)
    return {
      key: item.key,
      label: item.label,
      value: '',
      source: '',
      confidence: 'low',
      reason: anywhere ? '只在一处出现，未能配对取值' : '本次未检索到，请人工确认；不表示文件里没有',
    }
  })

  const copiesText = frontRows.find((row) => /正本|副本|份数/u.test(row.key))?.value
    ?? paragraphs.find((text) => /正本|副本/u.test(text))
    ?? ''
  const copies = copiesText === '' ? { original: null, duplicate: null, raw: '' } : readCopies(copiesText)

  const composition = compositionOf(paragraphs)

  const warnings: string[] = []
  if (paragraphs.length === 0) warnings.push('没有读到正文段落，组成清单无法抽取；只做了表格抽取')
  if (frontRows.length === 0) warnings.push('没有识别出前附表（要求为两列表格）；关键值可能位于正文表格或正文中')
  if (composition.length === 0) warnings.push('没有识别出投标文件组成清单（要求为连续三条以上的编号条目）')

  const sections = tables.map((table, index) => `表${index}：${table.rows.length} 行 × ${table.columns.length} 列`)
  return {
    items,
    frontRows,
    composition,
    copies,
    coverage: { paragraphs: paragraphs.length, tables: tables.length, sections },
    warnings,
  }
}

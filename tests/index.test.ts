/**
 * Tender extraction.
 *
 * The load-bearing behaviour is not "does it find the deadline" but "does it say
 * when it did not". A report that printed only hits would let a missing deposit
 * clause read as a document that has none.
 */

import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import { compositionOf, extract, looksLikeValue, readCopies, readCount } from '../src/model.ts'
import { renderMarkdown } from '../src/report.ts'

const HERE = import.meta.dirname
const fixture = (name: string): Buffer => readFileSync(join(HERE, 'fixtures', name))

describe('numerals', () => {
  it('reads Chinese and Arabic counts', () => {
    expect(readCount('四')).toBe(4)
    expect(readCount('十二')).toBe(12)
    expect(readCount('4')).toBe(4)
    expect(readCount('四份')).toBeNull()
  })

  it('parses the form the obvious regex misses', () => {
    // The spec's probe: `正本一份，副本四份` is not matched by `(正本|副本)\s*(\d+)\s*份`.
    expect(readCopies('正本一份，副本四份')).toEqual({ original: 1, duplicate: 4, raw: '正本一份，副本四份' })
    expect(readCopies('正本 1 份，副本 3 份')).toEqual({ original: 1, duplicate: 3, raw: '正本 1 份，副本 3 份' })
  })

  it('reports both counts as null rather than guessing', () => {
    expect(readCopies('份数见附件')).toEqual({ original: null, duplicate: null, raw: '份数见附件' })
  })
})

describe('shape detection', () => {
  it('tells a value from a column label', () => {
    expect(looksLikeValue('2026年11月20日 9时30分')).toBe(true)
    expect(looksLikeValue('¥50,000.00')).toBe(true)
    expect(looksLikeValue('正本一份，副本四份')).toBe(true)
    expect(looksLikeValue('编列内容')).toBe(false)
    expect(looksLikeValue('条款号')).toBe(false)
  })
})

describe('composition', () => {
  it('reads a numbered list that follows the lead-in sentence', () => {
    const entries = compositionOf([
      '投标文件应由以下部分组成：',
      '1. 投标函',
      '2. 授权委托书',
      '3. 保证金凭证',
      '',
      '以上文件应按顺序装订。',
    ])
    expect(entries).toEqual(['投标函', '授权委托书', '保证金凭证'])
  })

  it('returns nothing when there is no such list', () => {
    expect(compositionOf(['本项目不接受联合体投标。'])).toEqual([])
  })
})

describe('extract', () => {
  const extraction = extract(fixture('tender-sample.docx'), 'tender-sample.docx')

  it('finds the front-appendix values', () => {
    const byKey = new Map(extraction.items.map((item) => [item.key, item]))
    expect(byKey.get('deadline')?.value).toContain('2026年11月20日')
    expect(byKey.get('deposit')?.value).toContain('50,000')
    expect(byKey.get('ceiling')?.value).toContain('贰佰万')
    expect(byKey.get('validity')?.value).toContain('90')
  })

  it('recovers a requirement that was consumed as the table header', () => {
    // The header detector picked the 投标截止时间 row; without recovering that pair
    // the deadline would be missing from a document that states it plainly.
    const deadline = extraction.items.find((item) => item.key === 'deadline')
    expect(deadline?.value).not.toBe('')
    expect(deadline?.confidence).toBe('high')
  })

  it('parses the copy counts from the front appendix', () => {
    expect(extraction.copies.original).toBe(1)
    expect(extraction.copies.duplicate).toBe(4)
  })

  it('reads the composition list', () => {
    expect(extraction.composition.length).toBe(6)
    expect(extraction.composition[0]).toContain('投标函')
  })

  it('marks every item it did not find, and says why', () => {
    const missing = extraction.items.filter((item) => item.value === '')
    expect(missing.length).toBeGreaterThan(0)
    for (const item of missing) {
      expect(item.reason).not.toBe('')
      expect(item.reason).toContain('未检索到')
    }
  })

  it('carries a coverage statement', () => {
    expect(extraction.coverage.tables).toBeGreaterThan(0)
    expect(extraction.coverage.paragraphs).toBeGreaterThan(0)
  })
})

describe('report', () => {
  it('lists what was not found, and says not-found is not absent', () => {
    const extraction = extract(fixture('tender-sample.docx'), 'tender-sample.docx')
    const markdown = renderMarkdown(extraction, 'tender-sample.docx')
    expect(markdown).toContain('未检索到（请人工确认）')
    expect(markdown).toContain('不等于')
    expect(markdown).toContain('只解析了主文件')
  })
})

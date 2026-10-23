/**
 * RequirementsPack: the machine-readable output a bid-health check consumes.
 *
 * The three queues are the point. Any single extraction can be paraphrased by a
 * language model; what a reader cannot do is tell, without being told, which
 * findings were verified verbatim, which need a human to look, and which could not
 * be extracted at all. Collapsing those into one list is how a tool ends up
 * claiming a document is clean when it is only unchecked.
 *
 *   A 交付    verified verbatim, structurally plausible, no hedge word
 *   B 待确认  quoted but the evidence is thinner — scattered, weak family, partly matched
 *   C 必须处理  not quotable, hedged, or referenced elsewhere — a human must supply it
 *
 * C is a gate: while it is non-empty the pack is marked 未完成体检 and must not be
 * presented as a delivered check.
 */

/** A queue a requirement falls into. */
export type Tier = 'A' | 'B' | 'C'

/** What kind of requirement it is. */
export type Category = 'reject-clause' | 'qualification' | 'composition' | 'timeline' | 'deposit' | 'scoring'

/** Which family of rejection wording the clause uses. */
export type Family = 'reject' | 'invalid' | 'refuse' | 'deviation' | 'disqualify' | 'postAward'

/** One extracted requirement. */
export interface PackItem {
  id: string
  category: Category
  /** Only reject clauses carry a family. */
  family?: Family
  title: string
  /** The sentence as it appears in the document. */
  quote: string
  source: { file: string; paragraph: number }
  verification: { matchMode: 'exact'; quoteVerified: boolean }
  tier: Tier
  reasons: string[]
  whoseRisk: 'bidder' | 'buyer'
  flags: string[]
  review: { state: 'pending' | 'confirmed' }
}

/** One topic the coverage net looked for. */
export interface CoverageTopic {
  id: string
  topic: string
  hit: boolean
  itemIds: string[]
  note: string
}

/** The whole pack. */
export interface RequirementsPack {
  packVersion: 1
  generator: { plugin: string; version: string; rulesVersion: string }
  source: { files: { path: string; role: string }[]; paragraphsTotal: number; hasAmendments: boolean }
  header: Record<string, unknown>
  items: PackItem[]
  coverage: { topics: CoverageTopic[] }
  queues: { a: number; b: number; c: number }
  /** False while queue C is non-empty; the report says so. */
  deliverable: boolean
  notes: string[]
}

/**
 * The rejection families, each with the wording that marks it.
 *
 * The spec's probe is the reason this is a list of families rather than one
 * keyword table: a result-word-only list hit 12 of 24 constructed clauses with two
 * false positives, and a trigger-word-only list (不得/应当/必须) hit 15 of 24 where
 * most were the buyer's own obligations. Splitting by family keeps `拒收` and
 * `否决` from being flattened into one undifferentiated "reject" bucket.
 */
const FAMILIES: { family: Family; words: string[] }[] = [
  { family: 'refuse', words: ['拒收', '不予受理', '拒绝接收'] },
  { family: 'invalid', words: ['无效投标', '投标无效', '按无效处理'] },
  { family: 'reject', words: ['否决其投标', '否决投标', '作废标处理', '废标'] },
  { family: 'disqualify', words: ['取消投标资格', '取消中标资格', '取消资格'] },
  { family: 'deviation', words: ['重大偏差', '实质性偏离', '重大偏离'] },
  { family: 'postAward', words: ['取消中标', '不予退还', '没收'] },
]

/** Words that make a clause conditional, and therefore queue B rather than A. */
const HEDGES = ['原则上', '一般', '可以', '视情况', '必要时', '酌情']

/** Sections where a reject clause is most likely to bind. */
const BINDING_SECTIONS = ['投标人须知', '评标办法', '资格', '废标', '无效']

/** The coverage net: topics a reader expects a tender document to address. */
const COVERAGE_TOPICS: { id: string; topic: string; test: RegExp }[] = [
  { id: 'COV-01', topic: '未盖章 / 未签字', test: /未(?:加盖|盖).{0,6}章|未(?:签字|签署)|漏签/u },
  { id: 'COV-02', topic: '密封不符合要求', test: /密封/u },
  { id: 'COV-03', topic: '逾期送达', test: /逾期(?:送达|递交)|截止时间后(?:送达|递交)/u },
  { id: 'COV-04', topic: '一标多投 / 联合体', test: /一标多投|联合体/u },
  { id: 'COV-05', topic: '投标保证金', test: /投标保证金/u },
  { id: 'COV-06', topic: '报价超过最高限价', test: /最高限价|招标控制价|超过预算/u },
  { id: 'COV-07', topic: '资格条件不符', test: /资格(?:条件|要求)/u },
  { id: 'COV-08', topic: '串通投标 / 弄虚作假', test: /串通|弄虚作假|提供虚假材料/u },
  { id: 'COV-09', topic: '投标有效期不足', test: /投标有效期/u },
  { id: 'COV-10', topic: '澄清与修改的效力', test: /澄清|修改|补遗|答疑/u },
]

/** Split a paragraph into sentence-like units. */
export function sentencesOf(paragraph: string): string[] {
  return paragraph
    .split(/(?<=[。！？；])/u)
    .map((part) => part.trim())
    .filter((part) => part.length >= 4)
}

/** Classify one sentence, or return null when it is not a reject clause. */
function clauseOf(sentence: string): { family: Family; word: string; index: number } | null {
  for (const entry of FAMILIES) {
    for (const word of entry.words) {
      const index = sentence.indexOf(word)
      if (index !== -1) return { family: entry.family, word, index }
    }
  }
  return null
}

/**
 * The title of a clause.
 *
 * The clause word is the anchor, not the first comma: taking the text before the
 * first comma turns 「原则上，投标有效期不足的按无效投标处理。」 into the title
 * 「原则上」, which says nothing about what the clause is about.
 *
 * @param sentence - the whole sentence.
 * @param anchor - index of the clause word inside it.
 * @returns the segment carrying the clause, trimmed to a readable length.
 */
function titleOf(sentence: string, anchor: number): string {
  const body = sentence.replace(/[。；]$/u, '')
  const segments: { text: string; start: number }[] = []
  let start = 0
  for (const part of body.split(/(?<=[，,])/u)) {
    segments.push({ text: part, start })
    start += part.length
  }
  const carrying = segments.find((segment) => anchor >= segment.start && anchor < segment.start + segment.text.length)
  const text = (carrying?.text ?? body).replace(/[，,]$/u, '').trim()
  return text.length > 40 ? `${text.slice(0, 40)}…` : text
}

/**
 * Build a RequirementsPack from the paragraphs of a tender document.
 *
 * @param paragraphs - document paragraphs in order.
 * @param header - the front-appendix values already extracted.
 * @param source - file name and role, for the pack's provenance.
 * @param generator - plugin name and versions.
 * @returns the pack, with the three queues already counted.
 */
export function buildPack(
  paragraphs: string[],
  header: Record<string, unknown>,
  source: { path: string; role: string },
  generator: { plugin: string; version: string; rulesVersion: string },
): RequirementsPack {
  const items: PackItem[] = []
  const notes: string[] = []
  let sequence = 0

  paragraphs.forEach((paragraph, paragraphIndex) => {
    // A section heading carries the structural signal for the sentences under it.
    const heading = BINDING_SECTIONS.some((marker) => paragraph.includes(marker))
    for (const sentence of sentencesOf(paragraph)) {
      const clause = clauseOf(sentence)
      if (clause === null) continue
      sequence++
      const hedged = HEDGES.filter((hedge) => sentence.includes(hedge))
      const inBindingSection = heading || BINDING_SECTIONS.some((marker) => sentence.includes(marker))
      const verified = paragraphs.some((text) => text.includes(sentence))
      const reasons: string[] = [`命中「${clause.word}」族（${clause.family}）`]
      if (inBindingSection) reasons.push('位于投标人须知/评标办法一类章节')
      else reasons.push('未在章节标题里找到定位线索')
      if (hedged.length > 0) reasons.push(`含修饰词「${hedged.join('、')}」，非绝对表述`)
      if (!verified) reasons.push('未能在正文中逐字定位')

      const tier: Tier = !verified || hedged.length > 0 ? 'C' : inBindingSection ? 'A' : 'B'
      items.push({
        id: `TRQ-REJ-${String(sequence).padStart(3, '0')}`,
        category: 'reject-clause',
        family: clause.family,
        title: titleOf(sentence, clause.index),
        quote: sentence,
        source: { file: source.path, paragraph: paragraphIndex + 1 },
        verification: { matchMode: 'exact', quoteVerified: verified },
        tier,
        reasons,
        whoseRisk: 'bidder',
        flags: hedged.length > 0 ? ['hedged'] : [],
        review: { state: 'pending' },
      })
    }
  })

  // Composition and timeline entries are quoted from the front appendix, so they
  // are verified by construction — but they are not reject clauses, and calling
  // them queue A would overstate what "verified" means here.
  for (const [key, value] of Object.entries(header)) {
    if (typeof value !== 'string' || value.trim() === '') continue
    sequence++
    items.push({
      id: `TRQ-HDR-${String(sequence).padStart(3, '0')}`,
      category: key.includes('保证金') ? 'deposit' : key.includes('时间') ? 'timeline' : 'composition',
      title: key,
      quote: `${key}：${value}`,
      source: { file: source.path, paragraph: 0 },
      verification: { matchMode: 'exact', quoteVerified: true },
      tier: 'A',
      reasons: ['前附表两列表格中的键值对，取值逐字来自表格'],
      whoseRisk: 'bidder',
      flags: [],
      review: { state: 'pending' },
    })
  }

  const fullText = paragraphs.join('\n')
  const coverage: CoverageTopic[] = COVERAGE_TOPICS.map((topic) => {
    const hit = topic.test.test(fullText)
    const itemIds = hit
      ? items.filter((item) => topic.test.test(item.quote)).map((item) => item.id)
      : []
    return {
      id: topic.id,
      topic: topic.topic,
      hit,
      itemIds,
      note: hit ? '' : '未检索到相关表述，请人工确认；这不表示文件里没有',
    }
  })

  const queues = {
    a: items.filter((item) => item.tier === 'A').length,
    b: items.filter((item) => item.tier === 'B').length,
    c: items.filter((item) => item.tier === 'C').length,
  }

  if (queues.c > 0) notes.push(`C 队列有 ${queues.c} 条：抽不出来的条款必须人工补录，在此之前本包不算完成体检`)
  const unhit = coverage.filter((topic) => !topic.hit)
  if (unhit.length > 0) notes.push(`覆盖网有 ${unhit.length} 个话题未命中，请在报告里逐条确认`)
  notes.push('只解析了主文件；澄清、补遗、答疑纪要是招标文件的组成部分，本包不合并')

  return {
    packVersion: 1,
    generator,
    source: { files: [source], paragraphsTotal: paragraphs.length, hasAmendments: /补遗|澄清|答疑/u.test(fullText) },
    header,
    items,
    coverage: { topics: coverage },
    queues,
    deliverable: queues.c === 0,
    notes,
  }
}

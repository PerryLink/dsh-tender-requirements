/**
 * Markdown for a RequirementsPack.
 *
 * The three queues are printed as three sections rather than one merged list, and
 * queue C is printed first. A reader who sees only the queue-A clauses would take
 * the pack for a complete list, when the whole point of the split is that it is
 * not one until C is empty.
 */

import type { RequirementsPack, Tier } from './requirements.ts'

const TIER_TITLE: Record<Tier, string> = {
  A: 'A 交付 · 逐字校验通过，可一键确认',
  B: 'B 待确认 · 引文在，但证据弱一些',
  C: 'C 必须处理 · 抽不出来或表述非绝对，必须人工补录',
}

/**
 * Render the pack as markdown.
 *
 * @param pack - the built pack.
 * @param source - the document path, for the header.
 * @returns markdown text.
 */
export function renderPack(pack: RequirementsPack, source: string): string {
  const lines: string[] = []
  lines.push('# 招标要求清单（RequirementsPack）')
  lines.push('')
  lines.push(`- 检查对象：${source}`)
  lines.push(`- 生成器：${pack.generator.plugin} v${pack.generator.version}｜规则库 ${pack.generator.rulesVersion}`)
  lines.push(`- 扫描：${pack.source.paragraphsTotal} 个段落`)
  lines.push(`- 队列：A 交付 ${pack.queues.a} · B 待确认 ${pack.queues.b} · C 必须处理 ${pack.queues.c}`)
  lines.push(`- 交付状态：${pack.deliverable ? '可交付' : '**未完成体检**（C 队列非空）'}`)
  lines.push('')

  if (!pack.deliverable) {
    lines.push('> ⚠️ **C 队列非空，本包不得作为正式交付物。**')
    lines.push('> 下面 C 队列里的每一条都是「工具没能给出可信引文」的条款，')
    lines.push('> 请人工补录或提供更清晰的版本后重新生成。在此之前，本清单不能当作完整的废标条款清单使用。')
    lines.push('')
  }

  for (const tier of ['C', 'A', 'B'] as Tier[]) {
    const items = pack.items.filter((item) => item.tier === tier)
    if (items.length === 0) continue
    lines.push(`## ${TIER_TITLE[tier]}`)
    lines.push('')
    for (const item of items) {
      lines.push(`- **${item.id}** ${item.title}${item.family === undefined ? '' : `（${item.family} 族）`}`)
      lines.push(`  - 原文：${item.quote}`)
      lines.push(`  - 出处：${item.source.file}${item.source.paragraph === 0 ? '（前附表）' : ` 第 ${item.source.paragraph} 段`}`)
      lines.push(`  - 判定理由：${item.reasons.join('；')}`)
    }
    lines.push('')
  }

  if (pack.items.length === 0) {
    lines.push('## 未检索到废标条款')
    lines.push('')
    lines.push('本版本没有在正文里检索到拒收/无效/否决/取消资格一类的表述。**这不表示招标文件没有废标条款**：')
    lines.push('措辞不同、写在表格里、或只在补遗里出现，都会检索不到。请人工核对。')
    lines.push('')
  }

  lines.push('## 覆盖网')
  lines.push('')
  lines.push('逐话题说明有没有在文件里找到对应表述。**未命中不等于文件没写**，只说明本工具没检索到。')
  lines.push('')
  lines.push('| 话题 | 结果 | 关联条款 |')
  lines.push('|---|---|---|')
  for (const topic of pack.coverage.topics) {
    lines.push(`| ${topic.topic} | ${topic.hit ? '命中' : `未检索到（${topic.note}）`} | ${topic.itemIds.join('、') || '—'} |`)
  }
  lines.push('')

  lines.push('## 边界')
  lines.push('')
  lines.push('本清单是**抽取结果**，不是法律意见：它说明「文件里这样写了」，不说明「法律上这样有效」。')
  lines.push('只解析了主文件 —— 澄清、修改、补遗、答疑纪要依法是招标文件的组成部分，本工具不合并。')
  for (const note of pack.notes) lines.push(`- ${note}`)
  lines.push('')
  return lines.join('\n')
}

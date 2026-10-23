import { readFile } from 'node:fs/promises'
import { resolve } from 'node:path'
import type { Context } from '@deepseek-ai/cordis'
import { defineTool } from '@deepseek-ai/dsh-tools'
import { Config } from './config.ts'
import type { Config as ConfigShape } from './config.ts'
import { extract } from './model.ts'
import { renderMarkdown } from './report.ts'

export const name = 'dsh-tender-requirements'
export const inject = ['tools']
export { Config }

/** Tool id exposed to the model, and the row id in `cordis.patch.yml`. */
export const TOOL_NAME = 'tender_requirements'

/**
 * Register the extraction tool.
 *
 * @param ctx - plugin context, with `tools` already available.
 * @param config - validated configuration.
 */
export function apply(ctx: Context, config: ConfigShape): () => void {
  return ctx.tools.register(
    defineTool({
      name: TOOL_NAME,
      description:
        '从招标文件（.docx）抽取关键信息：前附表的时间/保证金/有效期/最高限价、投标文件组成清单、正副本份数。' +
        '每项都报告「检索到 / 未检索到」以及置信度与理由；未检索到不等于文件里没有，需人工复核。' +
        '只解析主文件，不解析澄清与补遗。',
      parameters: {
        file: { type: 'string', description: '招标文件 .docx 的绝对路径。' },
      },
      output: {
        schema: {
          type: 'object',
          additionalProperties: false,
          properties: {
            plugin: { type: 'string' },
            target: { type: 'string' },
            foundCount: { type: 'integer' },
            missingCount: { type: 'integer' },
            compositionCount: { type: 'integer' },
            items: {
              type: 'array',
              items: {
                type: 'object',
                additionalProperties: false,
                properties: {
                  key: { type: 'string' },
                  label: { type: 'string' },
                  value: { type: 'string' },
                  confidence: { type: 'string' },
                },
              },
            },
            markdown: { type: 'string' },
            resultJson: { type: 'string' },
          },
        },
        render: (_args, value) => [{ type: 'text', text: (value as { markdown: string }).markdown }],
      },
      timeoutMs: config.timeoutMs,
      isConcurrencySafe: () => true,
      async execute(args, exec) {
        if (args.file === undefined || args.file.trim() === '') throw new Error('必须提供 file（招标文件 .docx 路径）')
        const path = resolve(args.file)
        exec.signal.throwIfAborted()
        const buffer = await readFile(path)
        exec.signal.throwIfAborted()
        const extraction = extract(buffer, path)
        const markdown = renderMarkdown(extraction, path)
        const found = extraction.items.filter((item) => item.value !== '')
        return {
          plugin: name,
          target: path,
          foundCount: found.length,
          missingCount: extraction.items.length - found.length,
          compositionCount: extraction.composition.length,
          items: found.map((item) => ({ key: item.key, label: item.label, value: item.value, confidence: item.confidence })),
          markdown,
          resultJson: JSON.stringify(extraction),
        }
      },
    }),
  )
}

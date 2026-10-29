import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import { VERSION } from '../src/version.ts'

describe('version', () => {
  it('mirrors package.json into the generator block', () => {
    const pkg = JSON.parse(readFileSync(join(import.meta.dirname, '..', 'package.json'), 'utf8'))
    expect(VERSION).toBe(pkg.version)
  })
})

import { describe, it, expect } from 'vitest'
import { formatCurrency, formatNumber, formatPercentage, formatBytes } from './utils'

describe('Formatting Utilities', () => {
  it('formats currency correctly', () => {
    expect(formatCurrency(1248950.45)).toBe('$1,248,950.45')
    expect(formatCurrency(0)).toBe('$0.00')
    expect(formatCurrency(null)).toBe('$0.00')
    expect(formatCurrency(undefined)).toBe('$0.00')
  })

  it('formats whole numbers with commas', () => {
    expect(formatNumber(5015)).toBe('5,015')
    expect(formatNumber(0)).toBe('0')
    expect(formatNumber(null)).toBe('0')
  })

  it('formats percentages with signs', () => {
    expect(formatPercentage(12.5)).toBe('+12.5%')
    expect(formatPercentage(-5.3)).toBe('-5.3%')
    expect(formatPercentage(0)).toBe('0.0%')
  })

  it('formats byte sizes into readable units', () => {
    expect(formatBytes(1024)).toBe('1 KB')
    expect(formatBytes(1048576)).toBe('1 MB')
    expect(formatBytes(52428800)).toBe('50 MB')
  })
})

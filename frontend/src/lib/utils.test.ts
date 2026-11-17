import { describe, it, expect } from 'vitest'
import {
  formatCurrency,
  formatNumber,
  formatPercentage,
  formatBytes,
  formatINR,
  formatIndianCompact,
  formatIndianDate,
} from './utils'

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

  it('formats Indian Rupees (INR) correctly using en-IN grouping', () => {
    expect(formatINR(1250)).toContain('1,250')
    expect(formatINR(125000)).toContain('1,25,000')
    expect(formatINR(1250000)).toContain('12,50,000')
    expect(formatINR(null)).toContain('0.00')
  })

  it('formats compact Indian currency (Lakhs and Crores)', () => {
    expect(formatIndianCompact(12500)).toBe('₹12,500')
    expect(formatIndianCompact(1250000)).toBe('₹12.50 Lakh')
    expect(formatIndianCompact(12500000)).toBe('₹1.25 Cr')
    expect(formatIndianCompact(0)).toBe('₹0.00')
  })

  it('formats dates into DD/MM/YYYY Indian format', () => {
    expect(formatIndianDate('2024-08-15')).toBe('15/08/2024')
    expect(formatIndianDate('2023-01-26T10:00:00')).toBe('26/01/2023')
  })
})

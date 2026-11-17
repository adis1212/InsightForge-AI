import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format a number with optional Indian or standard grouping.
 */
export function formatNumber(value?: number | null, locale: string = 'en-IN'): string {
  if (value === null || value === undefined || isNaN(value)) return '0'
  return new Intl.NumberFormat(locale, { maximumFractionDigits: 2 }).format(value)
}

/**
 * Format currency with currency symbol and locale.
 * Defaults to USD if not specified for test backwards-compatibility,
 * with first-class support for INR ('INR' / '₹').
 */
export function formatCurrency(
  value?: number | null,
  currency: 'USD' | 'INR' | string = 'USD'
): string {
  if (value === null || value === undefined || isNaN(value)) {
    return currency === 'INR' ? '₹0.00' : '$0.00'
  }

  const locale = currency === 'INR' ? 'en-IN' : 'en-US'
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency,
    maximumFractionDigits: 2,
  }).format(value)
}

/**
 * Dedicated Indian Rupee (INR) formatter following Indian numbering system
 * (e.g., ₹1,250, ₹12,500, ₹1,25,000, ₹12,50,000).
 */
export function formatINR(value?: number | null): string {
  if (value === null || value === undefined || isNaN(value)) return '₹0.00'
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2,
  }).format(value)
}

/**
 * Compact Indian currency formatting for executive dashboards:
 * - < 1 Lakh: ₹12,500
 * - 1 Lakh to 99.9 Lakh: ₹12.50 Lakh
 * - >= 1 Crore: ₹1.25 Cr
 */
export function formatIndianCompact(value?: number | null): string {
  if (value === null || value === undefined || isNaN(value)) return '₹0'
  const abs = Math.abs(value)
  const sign = value < 0 ? '-' : ''

  if (abs >= 10000000) {
    const crore = abs / 10000000
    return `${sign}₹${crore.toFixed(2)} Cr`
  }
  if (abs >= 100000) {
    const lakh = abs / 100000
    return `${sign}₹${lakh.toFixed(2)} Lakh`
  }
  if (abs >= 1000) {
    return `${sign}₹${new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(abs)}`
  }
  return `${sign}₹${abs.toFixed(2)}`
}

/**
 * Format percentages with explicit signs (+12.5%, -5.3%, 0.0%).
 */
export function formatPercentage(value?: number | null): string {
  if (value === null || value === undefined || isNaN(value)) return '0.0%'
  const formatted = Math.abs(value).toFixed(1)
  if (value > 0) return `+${formatted}%`
  if (value < 0) return `-${formatted}%`
  return '0.0%'
}

/**
 * Format bytes into human-readable memory/storage sizes.
 */
export function formatBytes(value?: number | null): string {
  if (!value || value === 0 || isNaN(value)) return '0 Bytes'

  const units = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const unitIndex = Math.min(
    Math.floor(Math.log(value) / Math.log(1024)),
    units.length - 1
  )
  const amount = value / 1024 ** unitIndex

  return `${Number(amount.toFixed(2))} ${units[unitIndex]}`
}

/**
 * Format date to standard Indian business format: DD/MM/YYYY.
 */
export function formatIndianDate(dateStringOrDate: string | Date): string {
  if (!dateStringOrDate) return 'N/A'
  const d = new Date(dateStringOrDate)
  if (isNaN(d.getTime())) return String(dateStringOrDate)
  const day = String(d.getDate()).padStart(2, '0')
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const year = d.getFullYear()
  return `${day}/${month}/${year}`
}

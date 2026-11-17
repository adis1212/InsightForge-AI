import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatNumber(value: number) {
  return new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(value)
}

export function formatCurrency(value: number) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 2,
  }).format(value)
}

export function formatPercentage(value: number) {
  return `${formatNumber(value)}%`
}

export function formatBytes(value: number) {
  if (value === 0) return '0 Bytes'

  const units = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const unitIndex = Math.floor(Math.log(value) / Math.log(1024))
  const amount = value / 1024 ** unitIndex

  return `${Number(amount.toFixed(2))} ${units[unitIndex]}`
}

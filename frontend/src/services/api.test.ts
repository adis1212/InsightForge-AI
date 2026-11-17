import { describe, it, expect } from 'vitest'
import { DEMO_ANALYTICS, DEMO_DATASET, DEMO_WORKSPACE, DEMO_PREVIEW } from './demoData'

describe('Demo Benchmark Data Integrity', () => {
  it('ensures demo analytics has complete summary KPIs', () => {
    const summary = DEMO_ANALYTICS.summary
    expect(summary.total_revenue.value).toBeGreaterThan(0)
    expect(summary.unique_orders.value).toBeGreaterThan(0)
    expect(summary.units_sold.value).toBeGreaterThan(0)
    expect(summary.average_order_value.value).toBeGreaterThan(0)
    expect(summary.unique_customers.value).toBeGreaterThan(0)
    expect(summary.cancellation_rate.value).toBeGreaterThanOrEqual(0)
  })

  it('ensures average order value equals total revenue divided by unique orders within tolerance', () => {
    const rev = DEMO_ANALYTICS.summary.total_revenue.value!
    const orders = DEMO_ANALYTICS.summary.unique_orders.value!
    const aov = DEMO_ANALYTICS.summary.average_order_value.value!
    const expected = rev / orders
    expect(Math.abs(aov - expected)).toBeLessThan(1.0)
  })

  it('ensures monthly revenue contains valid timeline and non-negative revenues', () => {
    expect(DEMO_ANALYTICS.monthly_revenue.length).toBe(12)
    for (const month of DEMO_ANALYTICS.monthly_revenue) {
      expect(month.revenue).toBeGreaterThan(0)
      expect(month.period).toMatch(/^\d{4}-\d{2}$/)
    }
    // Baseline month has null growth rate
    expect(DEMO_ANALYTICS.monthly_revenue[0].growth_rate).toBeNull()
  })

  it('ensures top products are sorted by revenue in descending order', () => {
    const prods = DEMO_ANALYTICS.top_products
    expect(prods.length).toBeGreaterThan(0)
    for (let i = 0; i < prods.length - 1; i++) {
      expect(prods[i].total_revenue).toBeGreaterThanOrEqual(prods[i + 1].total_revenue)
      expect(prods[i].rank).toBe(i + 1)
    }
  })

  it('verifies demo dataset schema matches canonical roles', () => {
    expect(DEMO_DATASET.column_mapping).toHaveProperty('invoice_no')
    expect(DEMO_DATASET.column_mapping).toHaveProperty('quantity')
    expect(DEMO_DATASET.column_mapping).toHaveProperty('unit_price')
    expect(DEMO_DATASET.column_mapping).toHaveProperty('date')
    expect(DEMO_DATASET.quality_report?.data_quality_score).toBeGreaterThanOrEqual(90)
  })

  it('verifies demo preview rows contain required tabular fields', () => {
    expect(DEMO_PREVIEW.rows.length).toBeGreaterThan(0)
    const first = DEMO_PREVIEW.rows[0]
    expect(first).toHaveProperty('InvoiceNo')
    expect(first).toHaveProperty('Quantity')
    expect(first).toHaveProperty('UnitPrice')
  })
})

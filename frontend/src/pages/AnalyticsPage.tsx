import React, { useState, useEffect } from 'react'
import {
  TrendingUp,
  Globe2,
  Package,
  AlertOctagon,
  Percent,
  DollarSign,
  ArrowUpRight,
  ArrowDownRight,
  Sparkles,
  Info,
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, LineChart, Line
} from 'recharts'
import { useWorkspace } from '../context/WorkspaceContext'
import { analyticsApi } from '../services/api'
import { DEMO_ANALYTICS } from '../services/demoData'
import type { AnalyticsResponse } from '../types'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { formatCurrency, formatNumber, formatPercentage } from '../lib/utils'

export function AnalyticsPage() {
  const { currentWorkspace, currentDataset, isDemoMode } = useWorkspace()
  const [data, setData] = useState<AnalyticsResponse>(DEMO_ANALYTICS)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    const fetchAnalytics = async () => {
      if (isDemoMode || !currentWorkspace || !currentDataset || currentDataset.id.startsWith('demo-')) {
        setData(DEMO_ANALYTICS)
        return
      }

      setIsLoading(true)
      try {
        const res = await analyticsApi.getFull(currentWorkspace.id, currentDataset.id)
        setData(res)
      } catch (e) {
        console.warn('Analytics fallback to demo:', e)
        setData(DEMO_ANALYTICS)
      } finally {
        setIsLoading(false)
      }
    }

    fetchAnalytics()
  }, [currentWorkspace, currentDataset, isDemoMode])

  const { monthly_revenue, top_products, geographic_performance, cancellation_stats, summary } = data

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <TrendingUp className="h-6 w-6 text-teal-600 dark:text-teal-400" />
            Deterministic Business Analytics
          </h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Vectorized Pandas mathematical breakdowns of revenue, product volume, and international geographic markets
          </p>
        </div>
        {isDemoMode && (
          <Badge variant="teal" className="self-start sm:self-auto text-xs">
            Benchmark Demo Data
          </Badge>
        )}
      </div>

      {/* Row 1: Geographic Distribution Bar Chart */}
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base font-bold flex items-center gap-2">
                <Globe2 className="h-5 w-5 text-teal-600 dark:text-teal-400" />
                Geographic Market Performance
              </CardTitle>
              <CardDescription className="text-xs">
                Total commercial transaction revenue by country
              </CardDescription>
            </div>
            <span className="text-xs text-muted-foreground font-mono">
              {geographic_performance.length} Territories
            </span>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-64 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={geographic_performance.slice(0, 8)}
                margin={{ top: 10, right: 10, left: 10, bottom: 20 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                <XAxis
                  dataKey="country"
                  stroke="hsl(var(--muted-foreground))"
                  fontSize={11}
                  angle={-15}
                  textAnchor="end"
                  tickLine={false}
                />
                <YAxis
                  stroke="hsl(var(--muted-foreground))"
                  fontSize={11}
                  tickLine={false}
                  tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--card))',
                    borderColor: 'hsl(var(--border))',
                    borderRadius: '0.5rem',
                    fontSize: '12px',
                  }}
                  formatter={(val: any) => [formatCurrency(Number(val)), 'Revenue']}
                />
                <Bar dataKey="revenue" fill="#199473" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Row 2: Top Products Table & Month-over-Month Growth */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Product Leaderboard */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-bold flex items-center gap-2">
              <Package className="h-5 w-5 text-navy-800 dark:text-slate-300" />
              Product Performance Rankings
            </CardTitle>
            <CardDescription className="text-xs">
              Top revenue-generating wholesale items
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto max-h-96">
              <table className="w-full text-xs text-left">
                <thead className="bg-muted text-muted-foreground text-[11px] uppercase tracking-wider sticky top-0">
                  <tr>
                    <th className="py-2.5 px-3">#</th>
                    <th className="py-2.5 px-3">Product Description</th>
                    <th className="py-2.5 px-3 text-right">Units</th>
                    <th className="py-2.5 px-3 text-right">Revenue</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {top_products.map((p) => (
                    <tr key={p.stock_code} className="hover:bg-muted/30 transition-colors">
                      <td className="py-2.5 px-3 font-bold text-muted-foreground">{p.rank}</td>
                      <td className="py-2.5 px-3">
                        <div className="font-semibold text-foreground">{p.description}</div>
                        <span className="font-mono text-[10px] text-muted-foreground">{p.stock_code}</span>
                      </td>
                      <td className="py-2.5 px-3 text-right font-mono">{formatNumber(p.units_sold)}</td>
                      <td className="py-2.5 px-3 text-right font-bold text-teal-600 dark:text-teal-400">
                        {formatCurrency(p.total_revenue)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Monthly Revenue & Growth Rate Breakdown */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-bold flex items-center gap-2">
              <Percent className="h-5 w-5 text-teal-600 dark:text-teal-400" />
              Period-over-Period Growth Rate
            </CardTitle>
            <CardDescription className="text-xs">
              Month-over-month percentage changes with zero-division protection
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto max-h-96">
              <table className="w-full text-xs text-left">
                <thead className="bg-muted text-muted-foreground text-[11px] uppercase tracking-wider sticky top-0">
                  <tr>
                    <th className="py-2.5 px-3">Period</th>
                    <th className="py-2.5 px-3 text-right">Gross Revenue</th>
                    <th className="py-2.5 px-3 text-right">MoM Growth</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {monthly_revenue.map((m) => {
                    const isPositive = m.growth_rate !== null && m.growth_rate !== undefined && m.growth_rate > 0
                    const isNegative = m.growth_rate !== null && m.growth_rate !== undefined && m.growth_rate < 0
                    return (
                      <tr key={m.period} className="hover:bg-muted/30 transition-colors">
                        <td className="py-2.5 px-3 font-mono font-medium">{m.period}</td>
                        <td className="py-2.5 px-3 text-right font-semibold">
                          {formatCurrency(m.revenue)}
                        </td>
                        <td className="py-2.5 px-3 text-right font-mono font-bold">
                          {m.growth_rate === null || m.growth_rate === undefined ? (
                            <span className="text-muted-foreground text-[10px] italic">Baseline</span>
                          ) : (
                            <span
                              className={`inline-flex items-center gap-0.5 ${
                                isPositive
                                  ? 'text-emerald-600 dark:text-emerald-400'
                                  : isNegative
                                  ? 'text-red-500'
                                  : 'text-muted-foreground'
                              }`}
                            >
                              {isPositive && <ArrowUpRight className="h-3 w-3" />}
                              {isNegative && <ArrowDownRight className="h-3 w-3" />}
                              {formatPercentage(m.growth_rate)}
                            </span>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Row 3: Cancellation Impact Callout */}
      {cancellation_stats && (
        <Card className="border-amber-500/20 bg-amber-500/5">
          <CardHeader className="pb-2">
            <div className="flex items-center gap-2">
              <AlertOctagon className="h-5 w-5 text-amber-500" />
              <CardTitle className="text-base font-bold text-amber-900 dark:text-amber-300">
                Cancellation & Return Adjustment Audit
              </CardTitle>
            </div>
            <CardDescription className="text-xs">
              Explicit handling of invoices starting with 'C' and negative quantities
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-xs">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
              <div className="p-3 rounded-lg bg-card border border-border">
                <span className="text-muted-foreground text-[11px]">Total Cancelled Orders</span>
                <p className="text-lg font-bold text-foreground mt-0.5">
                  {cancellation_stats.total_cancellations} Invoices
                </p>
                <p className="text-[10px] text-muted-foreground">Excluded from gross transaction totals</p>
              </div>

              <div className="p-3 rounded-lg bg-card border border-border">
                <span className="text-muted-foreground text-[11px]">Gross Revenue Impact</span>
                <p className="text-lg font-bold text-red-500 mt-0.5">
                  {formatCurrency(cancellation_stats.cancellation_revenue_impact)}
                </p>
                <p className="text-[10px] text-muted-foreground">Reversed / refunded merchandise value</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  DollarSign,
  ShoppingCart,
  Package,
  Users,
  Percent,
  TrendingUp,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
  FileSpreadsheet,
  Layers,
  Sparkles,
  Info,
  Calendar,
  Cpu,
} from 'lucide-react'
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import { useWorkspace } from '../context/WorkspaceContext'
import { analyticsApi } from '../services/api'
import { DEMO_ANALYTICS } from '../services/demoData'
import type { AnalyticsResponse } from '../types'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { formatCurrency, formatNumber } from '../lib/utils'

export function DashboardOverviewPage() {
  const { currentWorkspace, currentDataset, isDemoMode } = useWorkspace()
  const [data, setData] = useState<AnalyticsResponse>(DEMO_ANALYTICS)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchAnalytics = async () => {
      if (isDemoMode || !currentWorkspace || !currentDataset || currentDataset.id.startsWith('demo-')) {
        setData(DEMO_ANALYTICS)
        return
      }

      setIsLoading(true)
      setError(null)
      try {
        const res = await analyticsApi.getFull(currentWorkspace.id, currentDataset.id)
        setData(res)
      } catch (err: any) {
        console.warn('Backend analytics fetch fallback to demo:', err)
        setError(err.response?.data?.detail || 'Using verified benchmark demo dataset')
        setData(DEMO_ANALYTICS)
      } finally {
        setIsLoading(false)
      }
    }

    fetchAnalytics()
  }, [currentWorkspace, currentDataset, isDemoMode])

  const { summary, monthly_revenue, top_products, cancellation_stats } = data

  return (
    <div className="space-y-6">
      {/* Top Banner & Dataset Context */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-border pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-foreground">
              Commercial Analytics Overview
            </h1>
            {isDemoMode && (
              <Badge variant="teal" className="text-xs font-semibold">
                Benchmark Demo
              </Badge>
            )}
          </div>
          <p className="text-xs md:text-sm text-muted-foreground mt-0.5">
            Active Dataset:{' '}
            <span className="font-semibold text-foreground">
              {currentDataset ? currentDataset.name : 'Wholesale Transactions FY2023'}
            </span>
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Link to="/ml">
            <Button variant="teal" size="sm" className="gap-1.5 text-xs shadow-sm">
              <Cpu className="h-3.5 w-3.5 text-teal-200" />
              ML Intelligence (Stage 6)
            </Button>
          </Link>
          <Link to="/prompt-studio">
            <Button variant="outline" size="sm" className="gap-1.5 text-xs shadow-sm">
              <Sparkles className="h-3.5 w-3.5 text-teal-600 dark:text-teal-400" />
              Prompt Studio (Stage 5)
            </Button>
          </Link>
          <Link to="/datasets/upload">
            <Button variant="outline" size="sm" className="gap-1.5 text-xs">
              <FileSpreadsheet className="h-3.5 w-3.5" />
              Upload
            </Button>
          </Link>
          <Link to="/analytics">
            <Button variant="secondary" size="sm" className="gap-1.5 text-xs">
              <TrendingUp className="h-3.5 w-3.5" />
              Analytics
            </Button>
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3 md:gap-4">
        {/* Total Revenue */}
        <Card className="p-4 space-y-2">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-medium">Total Revenue</span>
            <DollarSign className="h-4 w-4 text-teal-600 dark:text-teal-400" />
          </div>
          <div className="text-lg md:text-2xl font-bold tracking-tight text-foreground">
            {summary.total_revenue.formatted}
          </div>
          <p className="text-[10px] text-muted-foreground leading-tight">
            Valid non-cancelled lines
          </p>
        </Card>

        {/* Unique Orders */}
        <Card className="p-4 space-y-2">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-medium">Unique Orders</span>
            <ShoppingCart className="h-4 w-4 text-navy-600 dark:text-slate-300" />
          </div>
          <div className="text-lg md:text-2xl font-bold tracking-tight text-foreground">
            {summary.unique_orders.formatted}
          </div>
          <p className="text-[10px] text-muted-foreground leading-tight">
            Distinct invoice IDs
          </p>
        </Card>

        {/* Units Sold */}
        <Card className="p-4 space-y-2">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-medium">Units Sold</span>
            <Package className="h-4 w-4 text-teal-600 dark:text-teal-400" />
          </div>
          <div className="text-lg md:text-2xl font-bold tracking-tight text-foreground">
            {summary.units_sold.formatted}
          </div>
          <p className="text-[10px] text-muted-foreground leading-tight">
            Gross quantities delivered
          </p>
        </Card>

        {/* Average Order Value */}
        <Card className="p-4 space-y-2">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-medium">Avg Order Value</span>
            <TrendingUp className="h-4 w-4 text-navy-600 dark:text-slate-300" />
          </div>
          <div className="text-lg md:text-2xl font-bold tracking-tight text-foreground">
            {summary.average_order_value.formatted}
          </div>
          <p className="text-[10px] text-muted-foreground leading-tight">
            Revenue / valid orders
          </p>
        </Card>

        {/* Unique Customers */}
        <Card className="p-4 space-y-2">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-medium">Unique Customers</span>
            <Users className="h-4 w-4 text-teal-600 dark:text-teal-400" />
          </div>
          <div className="text-lg md:text-2xl font-bold tracking-tight text-foreground">
            {summary.unique_customers.formatted}
          </div>
          <p className="text-[10px] text-muted-foreground leading-tight">
            Excludes null identifiers
          </p>
        </Card>

        {/* Cancellation Rate */}
        <Card className="p-4 space-y-2">
          <div className="flex items-center justify-between text-muted-foreground">
            <span className="text-xs font-medium">Cancellation Rate</span>
            <Percent className="h-4 w-4 text-amber-500" />
          </div>
          <div className="text-lg md:text-2xl font-bold tracking-tight text-foreground">
            {summary.cancellation_rate.formatted}
          </div>
          <p className="text-[10px] text-muted-foreground leading-tight">
            Flagged 'C' prefix invoices
          </p>
        </Card>
      </div>

      {/* Strict Requirement Notice: Margin & Profit Guard */}
      <div className="rounded-xl bg-muted/40 border border-border p-3.5 flex items-start gap-3 text-xs">
        <Info className="h-4 w-4 text-muted-foreground shrink-0 mt-0.5" />
        <div className="space-y-0.5">
          <span className="font-semibold text-foreground">Architectural Integrity Constraint:</span>
          <p className="text-muted-foreground leading-relaxed">
            Profit metrics and gross margin percentages remain strictly <strong>unavailable</strong> because unit cost of goods sold (COGS) is not present in standard wholesale transaction logs. InsightForge AI strictly prohibits estimating or fabricating commercial margins.
          </p>
        </div>
      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Monthly Revenue Trend (2 Columns) */}
        <Card className="lg:col-span-2">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-base font-bold">Monthly Revenue Trajectory</CardTitle>
                <CardDescription className="text-xs">
                  Deterministic monthly rollups with period-over-period growth rates
                </CardDescription>
              </div>
              <Badge variant="outline" className="text-[11px] gap-1 font-mono">
                <Calendar className="h-3 w-3" />
                FY2023 Timeline
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-72 w-full pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={monthly_revenue} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#199473" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#199473" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                  <XAxis
                    dataKey="period"
                    stroke="hsl(var(--muted-foreground))"
                    fontSize={11}
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
                    formatter={(value: any) => [formatCurrency(Number(value)), 'Net Revenue']}
                  />
                  <Area
                    type="monotone"
                    dataKey="revenue"
                    stroke="#199473"
                    strokeWidth={2.5}
                    fillOpacity={1}
                    fill="url(#revenueGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Top 5 Products by Revenue (1 Column) */}
        <Card className="flex flex-col">
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-bold">Top Performing Products</CardTitle>
            <CardDescription className="text-xs">
              Ranked by total net revenue delivered
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col justify-between pt-2">
            <div className="space-y-3">
              {top_products.slice(0, 5).map((prod) => (
                <div key={prod.stock_code} className="flex items-center justify-between text-xs border-b border-border/50 pb-2.5 last:border-0 last:pb-0">
                  <div className="space-y-0.5 max-w-[65%]">
                    <p className="font-semibold text-foreground truncate">{prod.description}</p>
                    <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
                      <span className="font-mono bg-muted px-1 rounded">{prod.stock_code}</span>
                      <span>{formatNumber(prod.units_sold)} units</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="font-bold text-foreground">
                      {formatCurrency(prod.total_revenue)}
                    </span>
                    <p className="text-[10px] text-teal-600 dark:text-teal-400">Rank #{prod.rank}</p>
                  </div>
                </div>
              ))}
            </div>

            <Link to="/analytics" className="pt-4">
              <Button variant="ghost" size="sm" className="w-full text-xs gap-1">
                View All Product Rankings
                <ArrowUpRight className="h-3.5 w-3.5" />
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

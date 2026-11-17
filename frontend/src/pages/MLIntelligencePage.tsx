import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Cpu,
  TrendingUp,
  AlertOctagon,
  ShieldAlert,
  Sparkles,
  RefreshCw,
  Search,
  Filter,
  CheckCircle2,
  AlertTriangle,
  Info,
  Calendar,
  Layers,
  BarChart3,
  ChevronRight,
  ExternalLink,
  ShieldCheck,
  Scale,
} from 'lucide-react'
import {
  AreaChart, Area, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import { useWorkspace } from '../context/WorkspaceContext'
import { mlApi } from '../services/api'
import type { ForecastResponse, AnomalyResponse, AnomalyRecord } from '../types'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { formatCurrency, formatNumber, formatPercentage } from '../lib/utils'

export function MLIntelligencePage() {
  const { currentWorkspace, currentDataset, datasets, isDemoMode } = useWorkspace()

  // State
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>(currentDataset?.id || 'benchmark-wholesale')
  const [activeTab, setActiveTab] = useState<'forecast' | 'anomalies' | 'methodology'>('forecast')
  const [forecastHorizon, setForecastHorizon] = useState<number>(6)
  const [contamination, setContamination] = useState<number>(0.03)

  // Data states
  const [forecastData, setForecastData] = useState<ForecastResponse | null>(null)
  const [anomalyData, setAnomalyData] = useState<AnomalyResponse | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  // Anomaly table filters
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [severityFilter, setSeverityFilter] = useState<string>('all')

  useEffect(() => {
    fetchMLData()
  }, [selectedDatasetId, forecastHorizon, contamination])

  const fetchMLData = async () => {
    setIsLoading(true)
    setError(null)
    const wsId = currentWorkspace?.id || 'demo-workspace-01'
    try {
      const [fRes, aRes] = await Promise.all([
        mlApi.getForecast(wsId, selectedDatasetId, forecastHorizon),
        mlApi.getAnomalies(wsId, selectedDatasetId, contamination),
      ])
      setForecastData(fRes)
      setAnomalyData(aRes)
    } catch (err: any) {
      console.warn('ML data fetch fallback:', err)
      setError(err.response?.data?.detail || 'Failed to load ML intelligence data.')
    } finally {
      setIsLoading(false)
    }
  }

  // Filter anomalies for display
  const filteredAnomalies = (anomalyData?.flagged_anomalies || []).filter((item: AnomalyRecord) => {
    const matchesSearch =
      searchQuery === '' ||
      item.invoice_no.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.stock_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.customer_id.toLowerCase().includes(searchQuery.toLowerCase())

    const matchesSeverity =
      severityFilter === 'all' || item.risk_severity.toLowerCase() === severityFilter.toLowerCase()

    return matchesSearch && matchesSeverity
  })

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-border pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
              <Cpu className="h-6 w-6 text-teal-600 dark:text-teal-400" />
              Machine Learning Intelligence
            </h1>
            <Badge variant="teal" className="text-xs font-semibold">
              Stage 6 Engine
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground mt-0.5">
            XGBoost Time-Series Revenue Forecasting & Isolation Forest Outlier Detection with Zero Data Leakage
          </p>
        </div>

        {/* View Switcher */}
        <div className="flex items-center gap-1 p-1 bg-muted rounded-lg text-xs font-medium self-start md:self-auto">
          <button
            onClick={() => setActiveTab('forecast')}
            className={`px-3 py-1.5 rounded-md transition-colors flex items-center gap-1.5 ${
              activeTab === 'forecast'
                ? 'bg-card text-foreground shadow-sm font-semibold'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <TrendingUp className="h-3.5 w-3.5 text-teal-600 dark:text-teal-400" />
            Model 1: XGBoost Forecast
          </button>
          <button
            onClick={() => setActiveTab('anomalies')}
            className={`px-3 py-1.5 rounded-md transition-colors flex items-center gap-1.5 ${
              activeTab === 'anomalies'
                ? 'bg-card text-foreground shadow-sm font-semibold'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <AlertOctagon className="h-3.5 w-3.5 text-rose-600 dark:text-rose-400" />
            Model 2: Isolation Forest
          </button>
          <button
            onClick={() => setActiveTab('methodology')}
            className={`px-3 py-1.5 rounded-md transition-colors flex items-center gap-1.5 ${
              activeTab === 'methodology'
                ? 'bg-card text-foreground shadow-sm font-semibold'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <ShieldCheck className="h-3.5 w-3.5 text-teal-600 dark:text-teal-400" />
            Evaluation & Limitations
          </button>
        </div>
      </div>

      {/* Control Toolbar */}
      <Card className="p-4 bg-card/60 backdrop-blur-sm border-border">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
          {/* Dataset Selector */}
          <div className="space-y-1">
            <label className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
              Input Dataset
            </label>
            <select
              value={selectedDatasetId}
              onChange={(e) => setSelectedDatasetId(e.target.value)}
              className="w-full px-3 py-2 text-xs rounded-lg border border-input bg-background focus:outline-none focus:ring-1 focus:ring-teal-500"
            >
              <option value="benchmark-wholesale">Synthetic Wholesale Benchmark (5,015 rows)</option>
              {datasets.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name} ({d.row_count || 0} rows)
                </option>
              ))}
            </select>
          </div>

          {/* Forecast Horizon Selector */}
          <div className="space-y-1">
            <label className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
              Forecast Horizon
            </label>
            <select
              value={forecastHorizon}
              onChange={(e) => setForecastHorizon(Number(e.target.value))}
              className="w-full px-3 py-2 text-xs rounded-lg border border-input bg-background focus:outline-none focus:ring-1 focus:ring-teal-500"
            >
              <option value={4}>4 Periods (1 Month Horizon)</option>
              <option value={6}>6 Periods (Standard Horizon)</option>
              <option value={8}>8 Periods (2 Month Horizon)</option>
              <option value={12}>12 Periods (Quarterly Horizon)</option>
            </select>
          </div>

          {/* Anomaly Contamination Selector */}
          <div className="space-y-1">
            <label className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
              Anomaly Contamination Rate
            </label>
            <select
              value={contamination}
              onChange={(e) => setContamination(Number(e.target.value))}
              className="w-full px-3 py-2 text-xs rounded-lg border border-input bg-background focus:outline-none focus:ring-1 focus:ring-teal-500"
            >
              <option value={0.01}>1.0% (Extreme Outliers Only)</option>
              <option value={0.03}>3.0% (Standard Commercial Screening)</option>
              <option value={0.05}>5.0% (Broad Suspicious Pattern Audit)</option>
            </select>
          </div>

          {/* Re-Train Action */}
          <div className="flex items-end gap-2 pt-1 md:pt-4">
            <Button
              variant="teal"
              className="w-full gap-2 text-xs h-9"
              onClick={fetchMLData}
              isLoading={isLoading}
            >
              <RefreshCw className="h-3.5 w-3.5" />
              Re-Train & Evaluate
            </Button>
          </div>
        </div>
      </Card>

      {/* Error Banner */}
      {error && (
        <div className="p-4 rounded-xl border border-destructive/30 bg-destructive/10 text-destructive text-xs flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
          <Button variant="outline" size="sm" onClick={fetchMLData} className="text-[11px] h-7 border-destructive/30">
            Retry
          </Button>
        </div>
      )}

      {/* VIEW 1: XGBOOST SALES FORECASTING */}
      {activeTab === 'forecast' && forecastData && (
        <div className="space-y-6">
          {/* Model 1 Metric Ribbon */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <Card className="p-3 bg-teal-500/5 border-teal-500/20">
              <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">
                XGBoost WAPE
              </span>
              <div className="text-xl font-extrabold text-teal-700 dark:text-teal-400 mt-0.5">
                {forecastData.evaluation?.xgboost_metrics.wape}%
              </div>
              <span className="text-[10px] text-muted-foreground">
                Weighted Absolute % Error
              </span>
            </Card>

            <Card className="p-3">
              <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">
                Seasonal Naive Baseline
              </span>
              <div className="text-xl font-bold text-foreground mt-0.5 font-mono">
                {forecastData.evaluation?.baseline_metrics.wape}%
              </div>
              <span className="text-[10px] text-muted-foreground">
                Lag-1 persistence baseline
              </span>
            </Card>

            <Card className="p-3">
              <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">
                Holdout Evaluation
              </span>
              <div className="text-base font-bold text-foreground mt-0.5">
                {forecastData.evaluation?.outperforms_baseline ? (
                  <Badge variant="success" className="text-[10px] py-0.5">
                    Outperforms Baseline (+{forecastData.evaluation.wape_improvement_pct}%)
                  </Badge>
                ) : (
                  <Badge variant="warning" className="text-[10px] py-0.5">
                    Baseline Competitive
                  </Badge>
                )}
              </div>
              <span className="text-[10px] text-muted-foreground font-mono">
                {forecastData.evaluation?.xgboost_metrics.test_periods_count} Holdout Periods
              </span>
            </Card>

            <Card className="p-3">
              <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">
                RMSE / MAE
              </span>
              <div className="text-sm font-bold text-foreground mt-1 font-mono">
                ${formatNumber(forecastData.evaluation?.xgboost_metrics.mae || 0)} MAE
              </div>
              <span className="text-[10px] text-muted-foreground font-mono">
                ${formatNumber(forecastData.evaluation?.xgboost_metrics.rmse || 0)} RMSE
              </span>
            </Card>
          </div>

          {/* Forecast Area / Line Chart with Confidence Interval */}
          <Card>
            <CardHeader className="pb-2">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <CardTitle className="text-base font-bold flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-teal-600 dark:text-teal-400" />
                    Revenue Trajectory & Recursive Multi-Step Forecast
                  </CardTitle>
                  <CardDescription className="text-xs">
                    Actual historical sales vs. XGBoost predicted trajectory with 95% residual confidence intervals
                  </CardDescription>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="inline-block w-3 h-3 rounded-full bg-teal-500" />
                  <span className="text-muted-foreground">Historical Actual</span>
                  <span className="inline-block w-3 h-3 rounded-full bg-emerald-500 ml-2" />
                  <span className="text-muted-foreground">XGBoost Forecast</span>
                  <span className="inline-block w-3 h-3 rounded-full bg-amber-500 ml-2" />
                  <span className="text-muted-foreground">Naive Baseline</span>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="h-80 w-full pt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart
                    data={forecastData.timeline}
                    margin={{ top: 10, right: 20, left: 20, bottom: 20 }}
                  >
                    <defs>
                      <linearGradient id="actualGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#0d9488" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#0d9488" stopOpacity={0.0} />
                      </linearGradient>
                      <linearGradient id="confidenceGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.25} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0.05} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                    <XAxis
                      dataKey="period"
                      stroke="hsl(var(--muted-foreground))"
                      fontSize={11}
                      tickLine={false}
                      interval={Math.ceil(forecastData.timeline.length / 10)}
                    />
                    <YAxis
                      stroke="hsl(var(--muted-foreground))"
                      fontSize={11}
                      tickLine={false}
                      tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`}
                    />
                    <Tooltip
                      content={({ active, payload, label }) => {
                        if (active && payload && payload.length) {
                          const pt = payload[0].payload
                          return (
                            <div className="p-3 bg-popover text-popover-foreground rounded-lg border border-border shadow-md text-xs space-y-1">
                              <p className="font-bold border-b pb-1 text-foreground">Period: {label}</p>
                              {pt.actual !== null && pt.actual !== undefined && (
                                <p className="text-teal-600 dark:text-teal-400 font-semibold">
                                  Actual: {formatCurrency(pt.actual)}
                                </p>
                              )}
                              {pt.forecast !== null && pt.forecast !== undefined && (
                                <p className="text-emerald-600 dark:text-emerald-400 font-semibold">
                                  XGBoost Forecast: {formatCurrency(pt.forecast)}
                                </p>
                              )}
                              {pt.baseline_forecast !== null && pt.baseline_forecast !== undefined && (
                                <p className="text-amber-600 dark:text-amber-400">
                                  Naive Baseline: {formatCurrency(pt.baseline_forecast)}
                                </p>
                              )}
                              {pt.lower_bound !== null && pt.upper_bound !== null && pt.lower_bound !== undefined && (
                                <p className="text-[10px] text-muted-foreground font-mono pt-1">
                                  95% CI: [{formatCurrency(pt.lower_bound)} &ndash; {formatCurrency(pt.upper_bound)}]
                                </p>
                              )}
                            </div>
                          )
                        }
                        return null
                      }}
                    />
                    {/* Confidence Band Area */}
                    <Area
                      type="monotone"
                      dataKey="upper_bound"
                      stroke="transparent"
                      fill="url(#confidenceGradient)"
                      name="Confidence Band"
                    />
                    {/* Actual Historical Revenue */}
                    <Line
                      type="monotone"
                      dataKey="actual"
                      stroke="#0d9488"
                      strokeWidth={2.5}
                      dot={false}
                      name="Historical Actual"
                    />
                    {/* Naive Baseline */}
                    <Line
                      type="monotone"
                      dataKey="baseline_forecast"
                      stroke="#f59e0b"
                      strokeWidth={1.5}
                      strokeDasharray="4 4"
                      dot={false}
                      name="Seasonal Naive"
                    />
                    {/* XGBoost Forecast Line */}
                    <Line
                      type="monotone"
                      dataKey="forecast"
                      stroke="#10b981"
                      strokeWidth={2.5}
                      dot={{ r: 3, fill: '#10b981' }}
                      name="XGBoost Forecast"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* Model Verdict & Disclosures */}
              <div className="mt-4 p-3 rounded-lg bg-muted/60 text-xs border border-border flex items-start gap-2.5">
                <Info className="h-4 w-4 text-teal-600 dark:text-teal-400 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <p className="font-semibold text-foreground">
                    Model Evaluation Verdict:
                  </p>
                  <p className="text-muted-foreground leading-relaxed">
                    {forecastData.evaluation?.evaluation_verdict}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Feature Importance Card */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-bold flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-teal-600 dark:text-teal-400" />
                XGBoost Feature Importance (Relative Gain)
              </CardTitle>
              <CardDescription className="text-xs">
                Influence of cyclical seasonality, trend, and shifted lag features on model predictions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 pt-2">
                {forecastData.feature_importances.slice(0, 6).map((feat, idx) => (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="font-mono text-foreground font-semibold">{feat.feature_name}</span>
                      <span className="text-muted-foreground font-mono">{(feat.importance_score * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-muted overflow-hidden">
                      <div
                        className="h-full bg-teal-500 rounded-full"
                        style={{ width: `${Math.min(feat.importance_score * 100 * 3, 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* VIEW 2: ISOLATION FOREST ANOMALIES */}
      {activeTab === 'anomalies' && anomalyData && (
        <div className="space-y-6">
          {/* Anomaly Ribbon */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <Card className="p-3 bg-rose-500/5 border-rose-500/20">
              <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">
                Total Anomalies Flagged
              </span>
              <div className="text-xl font-extrabold text-rose-700 dark:text-rose-400 mt-0.5">
                {anomalyData.anomaly_count}
              </div>
              <span className="text-[10px] text-muted-foreground">
                {(anomalyData.contamination_rate * 100).toFixed(1)}% contamination rate
              </span>
            </Card>

            <Card className="p-3">
              <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">
                Critical Severity
              </span>
              <div className="text-xl font-bold text-destructive mt-0.5 font-mono">
                {anomalyData.severity_breakdown['critical'] || 0}
              </div>
              <span className="text-[10px] text-muted-foreground">
                Score &ge; 0.85 or &ge; 3 risk factors
              </span>
            </Card>

            <Card className="p-3">
              <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">
                High Risk Tier
              </span>
              <div className="text-xl font-bold text-amber-600 dark:text-amber-400 mt-0.5 font-mono">
                {anomalyData.severity_breakdown['high'] || 0}
              </div>
              <span className="text-[10px] text-muted-foreground">
                Score 0.70 &ndash; 0.84
              </span>
            </Card>

            <Card className="p-3">
              <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">
                Isolation Cutoff Threshold
              </span>
              <div className="text-xl font-bold text-foreground mt-0.5 font-mono">
                {anomalyData.score_threshold}
              </div>
              <span className="text-[10px] text-muted-foreground">
                Normalized decision boundary
              </span>
            </Card>
          </div>

          {/* Anomaly Score Distribution Histogram */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base font-bold flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-rose-600 dark:text-rose-400" />
                Isolation Forest Score Distribution (Histogram)
              </CardTitle>
              <CardDescription className="text-xs">
                Distribution of normalized outlier scores across {formatNumber(anomalyData.total_records_analyzed)} transactions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-56 w-full pt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={anomalyData.distribution_buckets}
                    margin={{ top: 10, right: 20, left: 20, bottom: 10 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                    <XAxis
                      dataKey="score_range"
                      stroke="hsl(var(--muted-foreground))"
                      fontSize={11}
                      tickLine={false}
                    />
                    <YAxis
                      stroke="hsl(var(--muted-foreground))"
                      fontSize={11}
                      tickLine={false}
                    />
                    <Tooltip
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const d = payload[0].payload
                          return (
                            <div className="p-2.5 bg-popover text-popover-foreground rounded-lg border border-border shadow-md text-xs">
                              <p className="font-bold">Score Range: {d.score_range}</p>
                              <p className="text-rose-600 dark:text-rose-400 font-semibold">
                                Transactions: {formatNumber(d.count)}
                              </p>
                              <p className="text-[10px] text-muted-foreground">
                                {d.is_anomaly_zone ? 'Isolation Outlier Zone' : 'Standard Operating Inlier'}
                              </p>
                            </div>
                          )
                        }
                        return null
                      }}
                    />
                    <Bar
                      dataKey="count"
                      fill="#0d9488"
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Flagged Transactions Table */}
          <Card>
            <CardHeader className="pb-3 border-b border-border">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <CardTitle className="text-base font-bold flex items-center gap-2">
                    <ShieldAlert className="h-5 w-5 text-rose-600 dark:text-rose-400" />
                    Flagged Transaction Audit Table
                  </CardTitle>
                  <CardDescription className="text-xs">
                    Prioritized line items isolated by multi-dimensional price, volume, and cancellation deviations
                  </CardDescription>
                </div>

                {/* Search & Filter Controls */}
                <div className="flex items-center gap-2">
                  <div className="relative">
                    <Search className="h-3.5 w-3.5 absolute left-2.5 top-2.5 text-muted-foreground" />
                    <input
                      type="text"
                      placeholder="Search invoice, SKU..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-8 pr-3 py-1.5 text-xs rounded-lg border border-input bg-background focus:outline-none focus:ring-1 focus:ring-teal-500 w-44"
                    />
                  </div>
                  <select
                    value={severityFilter}
                    onChange={(e) => setSeverityFilter(e.target.value)}
                    className="px-2.5 py-1.5 text-xs rounded-lg border border-input bg-background focus:outline-none focus:ring-1 focus:ring-teal-500"
                  >
                    <option value="all">All Severities</option>
                    <option value="critical">Critical Only</option>
                    <option value="high">High Tier</option>
                    <option value="medium">Medium Tier</option>
                  </select>
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead className="bg-muted/70 text-muted-foreground uppercase text-[10px] tracking-wider border-b border-border">
                    <tr>
                      <th className="py-2.5 px-3">Invoice No</th>
                      <th className="py-2.5 px-3">Date</th>
                      <th className="py-2.5 px-3">SKU & Description</th>
                      <th className="py-2.5 px-3 text-right">Quantity</th>
                      <th className="py-2.5 px-3 text-right">Unit Price</th>
                      <th className="py-2.5 px-3 text-right">Total Amount</th>
                      <th className="py-2.5 px-3 text-center">Score</th>
                      <th className="py-2.5 px-3 text-center">Severity</th>
                      <th className="py-2.5 px-3">Pattern Indicators</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border font-mono text-[11px]">
                    {filteredAnomalies.slice(0, 25).map((anom, idx) => (
                      <tr key={idx} className="hover:bg-muted/30 transition-colors">
                        <td className="py-2 px-3 font-bold text-foreground">
                          {anom.invoice_no}
                          {anom.invoice_no.startsWith('C') && (
                            <span className="ml-1 text-[9px] px-1 rounded bg-rose-500/10 text-rose-600 dark:text-rose-400">
                              REV
                            </span>
                          )}
                        </td>
                        <td className="py-2 px-3 text-muted-foreground whitespace-nowrap">
                          {anom.invoice_date.split(' ')[0]}
                        </td>
                        <td className="py-2 px-3 max-w-[200px] truncate" title={anom.description}>
                          <span className="font-semibold text-foreground">{anom.stock_code}</span> &ndash; {anom.description}
                        </td>
                        <td className="py-2 px-3 text-right font-semibold">
                          {anom.quantity.toLocaleString()}
                        </td>
                        <td className="py-2 px-3 text-right">
                          ${anom.unit_price.toFixed(2)}
                        </td>
                        <td className="py-2 px-3 text-right font-bold text-foreground">
                          {formatCurrency(anom.total_amount)}
                        </td>
                        <td className="py-2 px-3 text-center">
                          <span className="font-bold text-rose-600 dark:text-rose-400">
                            {anom.anomaly_score.toFixed(3)}
                          </span>
                        </td>
                        <td className="py-2 px-3 text-center">
                          {anom.risk_severity === 'critical' ? (
                            <Badge variant="destructive" className="text-[9px] uppercase px-1.5 py-0">
                              Critical
                            </Badge>
                          ) : anom.risk_severity === 'high' ? (
                            <Badge variant="warning" className="text-[9px] uppercase px-1.5 py-0">
                              High
                            </Badge>
                          ) : (
                            <Badge variant="secondary" className="text-[9px] uppercase px-1.5 py-0">
                              Medium
                            </Badge>
                          )}
                        </td>
                        <td className="py-2 px-3">
                          <div className="flex flex-wrap gap-1">
                            {anom.suspicious_reasons.map((r, rIdx) => (
                              <span
                                key={rIdx}
                                className="text-[9px] px-1.5 py-0.5 rounded bg-muted text-muted-foreground border border-border"
                              >
                                {r.replace('_', ' ')}
                              </span>
                            ))}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="p-3 border-t border-border flex items-center justify-between text-xs text-muted-foreground">
                <span>Showing top {Math.min(filteredAnomalies.length, 25)} of {filteredAnomalies.length} flagged records</span>
                <span className="text-[10px] italic">
                  Preserved from source transaction logs
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* VIEW 3: METHODOLOGY & DISCLOSURES */}
      {activeTab === 'methodology' && (
        <div className="space-y-6 max-w-4xl">
          <Card>
            <CardHeader>
              <CardTitle className="text-base font-bold flex items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-teal-600 dark:text-teal-400" />
                Machine Learning Architectural Methodology & Disclosures
              </CardTitle>
              <CardDescription className="text-xs">
                Engineering standards, leakage prevention, and legal distinction between statistical outliers and fraud
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-5 text-xs text-muted-foreground leading-relaxed">
              <div className="p-4 rounded-xl border border-teal-500/30 bg-teal-500/5 space-y-2">
                <h4 className="font-bold text-foreground text-sm flex items-center gap-2">
                  <Scale className="h-4 w-4 text-teal-600 dark:text-teal-400" />
                  Mandatory Legal Disclaimer: Statistical Outlier vs. Confirmed Fraud
                </h4>
                <p>
                  InsightForge AI utilizes <strong>unsupervised Isolation Forests</strong> to measure high-dimensional mathematical distance from the operational centroid.
                  A flagged transaction represents a <em>statistically unusual data point</em> (e.g. extreme unit price relative to SKU median, bulk volume anomaly, or uncharacteristic cancellation magnitude).
                  <strong>Flags do NOT constitute proof of fraudulent activity, embezzlement, or operational misconduct</strong> without corroborating commercial auditing.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-3.5 rounded-lg border border-border bg-card space-y-2">
                  <h4 className="font-bold text-foreground flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-teal-600 dark:text-teal-400" />
                    XGBoost Sales Forecasting Protocol
                  </h4>
                  <ul className="list-disc list-inside space-y-1">
                    <li><strong>Chronological Holdout Validation:</strong> Strict temporal train/test split (last 20% of periods). Shuffled K-fold cross validation is strictly prohibited.</li>
                    <li><strong>Zero Target Leakage:</strong> All lag (t-1, t-2...) and rolling features are shifted by 1 period before feature creation.</li>
                    <li><strong>Baseline Discipline:</strong> Model performance is judged against a Seasonal Naive persistence benchmark. Outperformance is never claimed unless WAPE is measurably lower.</li>
                    <li><strong>Confidence Bounds:</strong> 95% interval calculated via holdout residual standard deviation scaled by sqrt(h) over forecast horizon h.</li>
                  </ul>
                </div>

                <div className="p-3.5 rounded-lg border border-border bg-card space-y-2">
                  <h4 className="font-bold text-foreground flex items-center gap-2">
                    <AlertOctagon className="h-4 w-4 text-rose-600 dark:text-rose-400" />
                    Isolation Forest Anomaly Protocol
                  </h4>
                  <ul className="list-disc list-inside space-y-1">
                    <li><strong>Relative SKU Deviation:</strong> Transactions are normalized against SKU median prices and order quantities to prevent high-value SKUs from dominating anomaly scores.</li>
                    <li><strong>Continuous Scoring:</strong> Raw path lengths are normalized into continuous $[0, 1]$ anomaly scores with an empirical percentile cutoff.</li>
                    <li><strong>Explainable Reason Tags:</strong> Every flagged record receives rule-backed causal indicator tags (EXTREME_UNIT_PRICE, BULK_QUANTITY, CANCELLATION_SPIKE).</li>
                    <li><strong>Audit Integrity:</strong> Source invoice numbers, customer IDs, and descriptions are preserved without synthetic masking.</li>
                  </ul>
                </div>
              </div>

              <div className="p-3.5 rounded-lg border border-border bg-muted/40 flex items-center justify-between">
                <div>
                  <p className="font-semibold text-foreground">Next: Stage 5 Prompt Engine Integration</p>
                  <p className="text-[11px] text-muted-foreground mt-0.5">
                    Verified ML forecast metrics and anomaly tallies are forwarded directly into Prompt Studio for evidence-grounded briefing.
                  </p>
                </div>
                <Link to="/prompt-studio">
                  <Button variant="teal" size="sm" className="gap-1.5 text-xs">
                    <Sparkles className="h-3.5 w-3.5" />
                    Prompt Studio
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}

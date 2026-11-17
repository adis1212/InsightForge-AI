import React, { useState, useEffect } from 'react'
import {
  FileSpreadsheet,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  RefreshCw,
  Sliders,
  ShieldCheck,
  Search,
  Check,
} from 'lucide-react'
import { useWorkspace } from '../context/WorkspaceContext'
import { datasetsApi } from '../services/api'
import { DEMO_PREVIEW, DEMO_DATASET } from '../services/demoData'
import type { DatasetPreview, QualityReport } from '../types'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { formatNumber } from '../lib/utils'

const STANDARD_ROLES = [
  { key: 'invoice_no', label: 'Invoice Number' },
  { key: 'stock_code', label: 'Stock Code / SKU' },
  { key: 'description', label: 'Description' },
  { key: 'quantity', label: 'Quantity' },
  { key: 'unit_price', label: 'Unit Price' },
  { key: 'customer_id', label: 'Customer ID' },
  { key: 'country', label: 'Country / Market' },
  { key: 'date', label: 'Transaction Date' },
]

export function DatasetPreviewPage() {
  const { currentWorkspace, currentDataset, isDemoMode } = useWorkspace()
  const [preview, setPreview] = useState<DatasetPreview>(DEMO_PREVIEW)
  const [quality, setQuality] = useState<QualityReport | null>(DEMO_DATASET.quality_report || null)
  const [activeTab, setActiveTab] = useState<'preview' | 'quality' | 'mapping'>('preview')
  const [mapping, setMapping] = useState<Record<string, string>>(
    currentDataset?.column_mapping || DEMO_DATASET.column_mapping || {}
  )
  const [isSavingMapping, setIsSavingMapping] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      if (isDemoMode || !currentWorkspace || !currentDataset || currentDataset.id.startsWith('demo-')) {
        setPreview(DEMO_PREVIEW)
        setQuality(DEMO_DATASET.quality_report || null)
        setMapping(DEMO_DATASET.column_mapping || {})
        return
      }

      setIsLoading(true)
      try {
        const [prevRes, qualRes] = await Promise.all([
          datasetsApi.preview(currentWorkspace.id, currentDataset.id, 50),
          datasetsApi.getQuality(currentWorkspace.id, currentDataset.id),
        ])
        setPreview(prevRes)
        setQuality(qualRes)
        if (currentDataset.column_mapping) {
          setMapping(currentDataset.column_mapping)
        }
      } catch (e) {
        console.warn('Fallback to demo preview:', e)
        setPreview(DEMO_PREVIEW)
        setQuality(DEMO_DATASET.quality_report || null)
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [currentWorkspace, currentDataset, isDemoMode])

  const handleSaveMapping = async () => {
    if (isDemoMode || !currentWorkspace || !currentDataset || currentDataset.id.startsWith('demo-')) {
      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(false), 2500)
      return
    }

    setIsSavingMapping(true)
    try {
      await datasetsApi.updateMapping(currentWorkspace.id, currentDataset.id, mapping)
      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(false), 2500)
    } catch (e) {
      console.error('Error saving mapping:', e)
    } finally {
      setIsSavingMapping(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <FileSpreadsheet className="h-6 w-6 text-teal-600 dark:text-teal-400" />
            Dataset Schema & Quality Audit
          </h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Active Dataset:{' '}
            <span className="font-semibold text-foreground">
              {currentDataset ? currentDataset.name : 'Wholesale Transactions FY2023'}
            </span>{' '}
            ({formatNumber(preview.total_rows)} rows)
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-1 p-1 bg-muted rounded-lg text-xs font-medium self-start sm:self-auto">
          <button
            onClick={() => setActiveTab('preview')}
            className={`px-3 py-1.5 rounded-md transition-colors ${
              activeTab === 'preview'
                ? 'bg-card text-foreground shadow-sm font-semibold'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Tabular Preview
          </button>
          <button
            onClick={() => setActiveTab('quality')}
            className={`px-3 py-1.5 rounded-md transition-colors ${
              activeTab === 'quality'
                ? 'bg-card text-foreground shadow-sm font-semibold'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Quality Audit
          </button>
          <button
            onClick={() => setActiveTab('mapping')}
            className={`px-3 py-1.5 rounded-md transition-colors ${
              activeTab === 'mapping'
                ? 'bg-card text-foreground shadow-sm font-semibold'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Column Mapping
          </button>
        </div>
      </div>

      {/* TAB 1: PREVIEW */}
      {activeTab === 'preview' && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-bold">First 50 Ingested Records</CardTitle>
            <CardDescription className="text-xs">
              Raw tabular schema verified and normalized for downstream deterministic KPI calculation
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto max-h-[550px] border-t border-border">
              <table className="w-full text-xs text-left border-collapse">
                <thead className="bg-muted/80 text-muted-foreground sticky top-0 backdrop-blur-sm z-10 font-semibold uppercase tracking-wider text-[11px]">
                  <tr>
                    <th className="py-2.5 px-3 border-b border-border">#</th>
                    {preview.columns.map((col) => (
                      <th key={col} className="py-2.5 px-3 border-b border-border whitespace-nowrap">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {preview.rows.map((row, idx) => {
                    const isCancellation = String(row['InvoiceNo'] || '').startsWith('C')
                    return (
                      <tr
                        key={idx}
                        className={`hover:bg-muted/40 transition-colors ${
                          isCancellation ? 'bg-amber-500/5' : ''
                        }`}
                      >
                        <td className="py-2 px-3 text-muted-foreground font-mono">{idx + 1}</td>
                        {preview.columns.map((col) => {
                          const val = row[col]
                          const isInvoice = col.toLowerCase().includes('invoice')
                          return (
                            <td key={col} className="py-2 px-3 whitespace-nowrap font-mono text-[11px]">
                              {isInvoice && isCancellation ? (
                                <span className="inline-flex items-center gap-1 text-amber-600 dark:text-amber-400 font-bold">
                                  {val}
                                  <Badge variant="warning" className="text-[9px] py-0 px-1">
                                    Cancelled
                                  </Badge>
                                </span>
                              ) : val !== null && val !== undefined ? (
                                String(val)
                              ) : (
                                <span className="text-muted-foreground/50 italic">null</span>
                              )}
                            </td>
                          )
                        })}
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* TAB 2: QUALITY AUDIT */}
      {activeTab === 'quality' && quality && (
        <div className="space-y-6">
          {/* Quality Score Hero Card */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="p-4 bg-teal-500/5 border-teal-500/30 flex items-center justify-between">
              <div>
                <span className="text-xs font-semibold text-teal-800 dark:text-teal-300">
                  Data Quality Score
                </span>
                <div className="text-3xl font-extrabold text-teal-700 dark:text-teal-400 mt-1">
                  {quality.data_quality_score}/100
                </div>
                <p className="text-[10px] text-muted-foreground mt-0.5">Reliable for KPI aggregation</p>
              </div>
              <ShieldCheck className="h-10 w-10 text-teal-600/40" />
            </Card>

            <Card className="p-4">
              <span className="text-xs text-muted-foreground">Duplicate Rows</span>
              <div className="text-2xl font-bold text-foreground mt-1">
                {quality.duplicate_rows}
              </div>
              <p className="text-[10px] text-muted-foreground mt-0.5">
                {quality.duplicate_percentage}% of total dataset
              </p>
            </Card>

            <Card className="p-4">
              <span className="text-xs text-muted-foreground">Cancellation Records</span>
              <div className="text-2xl font-bold text-amber-600 dark:text-amber-400 mt-1">
                {quality.cancellation_count}
              </div>
              <p className="text-[10px] text-muted-foreground mt-0.5">
                Auto-excluded from gross revenue
              </p>
            </Card>

            <Card className="p-4">
              <span className="text-xs text-muted-foreground">Negative Quantities</span>
              <div className="text-2xl font-bold text-foreground mt-1">
                {quality.negative_quantities}
              </div>
              <p className="text-[10px] text-muted-foreground mt-0.5">Tracked return lines</p>
            </Card>
          </div>

          {/* Missing Values Breakdown */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-bold">Missing Values by Column</CardTitle>
              <CardDescription className="text-xs">
                Audited null and NaN occurrence across transaction attributes
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(quality.missing_values).length === 0 ? (
                  <p className="text-xs text-muted-foreground">Zero missing values detected across all columns.</p>
                ) : (
                  Object.entries(quality.missing_values).map(([col, count]) => {
                    const pct = quality.missing_percentages[col] || 0
                    return (
                      <div key={col} className="space-y-1">
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-semibold text-foreground">{col}</span>
                          <span className="text-muted-foreground">
                            {count} missing ({pct}%)
                          </span>
                        </div>
                        <div className="w-full h-2 rounded-full bg-muted overflow-hidden">
                          <div
                            className="h-full bg-amber-500 rounded-full"
                            style={{ width: `${Math.min(pct * 2, 100)}%` }}
                          />
                        </div>
                      </div>
                    )
                  })
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* TAB 3: COLUMN MAPPING */}
      {activeTab === 'mapping' && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-bold">Canonical Role Mapping</CardTitle>
            <CardDescription className="text-xs">
              Map dataset headers to standard roles required by the deterministic KPI engine
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {saveSuccess && (
              <div className="p-3 text-xs rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-700 dark:text-emerald-400 flex items-center gap-2">
                <Check className="h-4 w-4" />
                <span>Column mapping saved successfully! KPIs updated.</span>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {STANDARD_ROLES.map((role) => (
                <div key={role.key} className="p-3 rounded-lg border border-border bg-card space-y-1.5">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-semibold text-foreground">{role.label}</label>
                    <span className="font-mono text-[10px] text-muted-foreground">{role.key}</span>
                  </div>
                  <select
                    value={mapping[role.key] || ''}
                    onChange={(e) => {
                      setMapping({ ...mapping, [role.key]: e.target.value })
                    }}
                    className="w-full px-3 py-1.5 text-xs rounded-md border border-input bg-background focus:outline-none focus:ring-1 focus:ring-teal-500"
                  >
                    <option value="">-- Unmapped --</option>
                    {preview.columns.map((col) => (
                      <option key={col} value={col}>
                        {col}
                      </option>
                    ))}
                  </select>
                </div>
              ))}
            </div>

            <div className="flex justify-end pt-2">
              <Button
                variant="teal"
                onClick={handleSaveMapping}
                isLoading={isSavingMapping}
                className="gap-2"
              >
                <Check className="h-4 w-4" />
                Save Column Mapping
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

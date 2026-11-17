import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  FileText, Download, Trash2, PlusCircle, CheckCircle2,
  AlertCircle, Clock, Sparkles, TrendingUp, Shield, BookOpen,
  Loader2, RefreshCw, Eye, Database, FileCheck, Layers,
} from 'lucide-react'
import { reportsApi } from '../services/api'
import type { ReportSummary, ReportDetail, ReportGenerateRequest } from '../types'

const DEMO_WORKSPACE = 'demo-workspace-01'
const BENCHMARK_DATASET = 'benchmark-wholesale'

export function ReportsPage() {
  const queryClient = useQueryClient()
  const [isGenerating, setIsGenerating] = useState(false)
  const [selectedReport, setSelectedReport] = useState<ReportDetail | null>(null)
  const [showGenModal, setShowGenModal] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Form State
  const [formData, setFormData] = useState<ReportGenerateRequest>({
    dataset_id: BENCHMARK_DATASET,
    prompt_version: 'v2',
    title: 'Boardroom Commercial Intelligence Briefing FY2023',
    include_forecast: true,
    include_anomalies: true,
    include_rag: true,
  })

  // Fetch reports list
  const { data: reports = [], isLoading, refetch } = useQuery({
    queryKey: ['reports', DEMO_WORKSPACE],
    queryFn: () => reportsApi.list(DEMO_WORKSPACE),
  })

  // Generate Report Mutation
  const generateMutation = useMutation({
    mutationFn: (data: ReportGenerateRequest) => reportsApi.generate(DEMO_WORKSPACE, data),
    onSuccess: (newReport) => {
      queryClient.invalidateQueries({ queryKey: ['reports', DEMO_WORKSPACE] })
      setIsGenerating(false)
      setShowGenModal(false)
      setSelectedReport(newReport)
      setError(null)
    },
    onError: (err: any) => {
      setIsGenerating(false)
      setError(err.response?.data?.detail || err.message || 'Report generation failed')
    },
  })

  // Delete Report Mutation
  const deleteMutation = useMutation({
    mutationFn: (reportId: string) => reportsApi.delete(DEMO_WORKSPACE, reportId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports', DEMO_WORKSPACE] })
      if (selectedReport) setSelectedReport(null)
    },
  })

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault()
    setIsGenerating(true)
    setError(null)
    generateMutation.mutate(formData)
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
  }

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-foreground">Executive Reports</h1>
            <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-teal-500/15 text-teal-700 dark:text-teal-400 border border-teal-500/30">
              Stage 9
            </span>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Audit-grade board briefings compiled from deterministic Pandas KPIs, XGBoost forecasts, and verified prompt summaries.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => refetch()}
            className="p-2 rounded-lg border border-border bg-card text-muted-foreground hover:text-foreground transition-colors"
            title="Refresh list"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
          <button
            onClick={() => setShowGenModal(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-teal-500 to-cyan-600 hover:from-teal-600 hover:to-cyan-700 text-white font-medium text-sm shadow-md transition-all"
          >
            <PlusCircle className="h-4 w-4" />
            <span>Generate Executive Report</span>
          </button>
        </div>
      </div>

      {/* Governance & Architecture Notice */}
      <div className="p-4 rounded-xl bg-card border border-border/70 space-y-2 text-xs">
        <div className="flex items-center gap-2 font-semibold text-foreground">
          <FileCheck className="h-4 w-4 text-teal-500" />
          <span>InsightForge Verification Guarantee</span>
        </div>
        <p className="text-muted-foreground leading-relaxed">
          Executive PDF reports are built with <b>100% deterministic numerical arithmetic</b>. The generative prompt pipeline
          explains findings and formats recommendations, but is strictly prohibited from calculating numbers.
          All cited metrics are verified within ±0.5% ground truth tolerance.
        </p>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Reports History List (2 cols on lg) */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-sm font-semibold text-foreground uppercase tracking-wider">Generated Reports History</h2>

          {isLoading ? (
            <div className="p-12 text-center text-muted-foreground bg-card border border-border rounded-xl">
              <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2 text-teal-500" />
              <p className="text-sm">Loading executive reports…</p>
            </div>
          ) : reports.length === 0 ? (
            <div className="p-12 text-center text-muted-foreground bg-card border border-border/60 rounded-xl space-y-3">
              <div className="w-12 h-12 rounded-2xl bg-teal-500/10 flex items-center justify-center mx-auto text-teal-500">
                <FileText className="h-6 w-6" />
              </div>
              <h3 className="text-base font-semibold text-foreground">No reports generated yet</h3>
              <p className="text-xs text-muted-foreground max-w-sm mx-auto">
                Generate your first comprehensive board-ready commercial report for the benchmark dataset.
              </p>
              <button
                onClick={() => setShowGenModal(true)}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-teal-500/15 text-teal-600 dark:text-teal-400 font-medium text-xs border border-teal-500/30 hover:bg-teal-500/25 transition-colors"
              >
                <PlusCircle className="h-3.5 w-3.5" /> Generate Benchmark Report
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {reports.map((r) => (
                <div
                  key={r.id}
                  className={`p-4 rounded-xl border transition-all cursor-pointer bg-card ${
                    selectedReport?.id === r.id
                      ? 'border-teal-500/60 shadow-md ring-1 ring-teal-500/30'
                      : 'border-border/60 hover:border-border hover:shadow-sm'
                  }`}
                  onClick={async () => {
                    const detail = await reportsApi.get(DEMO_WORKSPACE, r.id)
                    setSelectedReport(detail)
                  }}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3 min-w-0">
                      <div className="w-9 h-9 rounded-lg bg-teal-500/10 flex items-center justify-center shrink-0 mt-0.5">
                        <FileText className="h-5 w-5 text-teal-600 dark:text-teal-400" />
                      </div>
                      <div className="min-w-0">
                        <h4 className="text-sm font-semibold text-foreground truncate">{r.title}</h4>
                        <div className="flex flex-wrap items-center gap-2 text-[11px] text-muted-foreground mt-1">
                          <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-muted border border-border/50 uppercase">
                            {r.format}
                          </span>
                          <span>•</span>
                          <span>{formatBytes(r.file_size_bytes)}</span>
                          <span>•</span>
                          <span className="flex items-center gap-1 font-mono text-[10px]">
                            <Sparkles className="h-3 w-3 text-teal-500" />
                            {r.prompt_version.toUpperCase()} Grounded
                          </span>
                          <span>•</span>
                          <span>{new Date(r.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-1 shrink-0" onClick={(e) => e.stopPropagation()}>
                      <a
                        href={reportsApi.getDownloadUrl(DEMO_WORKSPACE, r.id)}
                        download
                        className="p-2 rounded-lg text-muted-foreground hover:text-teal-500 hover:bg-teal-500/10 transition-colors"
                        title="Download PDF"
                      >
                        <Download className="h-4 w-4" />
                      </a>
                      <button
                        onClick={() => deleteMutation.mutate(r.id)}
                        className="p-2 rounded-lg text-muted-foreground hover:text-red-500 hover:bg-red-500/10 transition-colors"
                        title="Delete report"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Report Detail Preview Sidebar */}
        <div className="space-y-4">
          <h2 className="text-sm font-semibold text-foreground uppercase tracking-wider">Report Audit Inspector</h2>

          {selectedReport ? (
            <div className="p-5 rounded-xl border border-border bg-card space-y-4 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-teal-500/15 text-teal-600 dark:text-teal-400 font-semibold border border-teal-500/20">
                  {selectedReport.status.toUpperCase()}
                </span>
                <span className="text-[10px] text-muted-foreground font-mono">
                  ID: {selectedReport.id.slice(0, 8)}
                </span>
              </div>

              <div>
                <h3 className="text-base font-bold text-foreground leading-tight">{selectedReport.title}</h3>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Generated {new Date(selectedReport.created_at).toLocaleString()}
                </p>
              </div>

              {selectedReport.report_metadata && (
                <div className="p-3.5 rounded-lg bg-muted/40 border border-border/60 space-y-2 text-xs">
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Audit Snapshot</p>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="text-muted-foreground text-[10px] block">Total Revenue</span>
                      <span className="font-bold text-foreground">
                        ${selectedReport.report_metadata.total_revenue?.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground text-[10px] block">Fulfilled Orders</span>
                      <span className="font-bold text-foreground">
                        {selectedReport.report_metadata.unique_orders?.toLocaleString()}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground text-[10px] block">Cancellation Rate</span>
                      <span className="font-bold text-foreground">
                        {selectedReport.report_metadata.cancellation_rate?.toFixed(1)}%
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground text-[10px] block">Verification</span>
                      <span className="font-bold text-emerald-600 dark:text-emerald-400">
                        {selectedReport.report_metadata.verification_status}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              <div className="space-y-2 text-xs text-muted-foreground">
                <div className="flex justify-between py-1 border-b border-border/50">
                  <span>File Size</span>
                  <span className="font-mono text-foreground">{formatBytes(selectedReport.file_size_bytes)}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-border/50">
                  <span>Prompt Version</span>
                  <span className="font-mono text-foreground">{selectedReport.prompt_version.toUpperCase()}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span>Format</span>
                  <span className="font-mono text-foreground uppercase">{selectedReport.format}</span>
                </div>
              </div>

              <a
                href={selectedReport.download_url}
                download
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-teal-500 hover:bg-teal-600 text-white font-medium text-xs shadow-md transition-colors"
              >
                <Download className="h-4 w-4" />
                <span>Download Executive PDF</span>
              </a>
            </div>
          ) : (
            <div className="p-8 text-center text-muted-foreground bg-card border border-border/60 rounded-xl text-xs space-y-2">
              <Eye className="h-6 w-6 mx-auto opacity-50" />
              <p>Select a report from the list to view its audit snapshot and download the binary document.</p>
            </div>
          )}
        </div>
      </div>

      {/* Generate Report Modal */}
      {showGenModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-card border border-border rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-teal-500" />
                <h3 className="text-lg font-bold text-foreground">Generate Executive PDF Report</h3>
              </div>
              <button
                onClick={() => setShowGenModal(false)}
                className="text-muted-foreground hover:text-foreground text-sm font-semibold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleGenerate} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-foreground block mb-1">Report Title</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg bg-background border border-border text-xs focus:outline-none focus:ring-2 focus:ring-teal-500/40"
                  required
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-foreground block mb-1">Target Dataset</label>
                <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-muted/40 border border-border text-xs text-muted-foreground font-mono">
                  <Database className="h-3.5 w-3.5 text-teal-500" />
                  <span>benchmark-wholesale (Wholesale FY2023)</span>
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-foreground block mb-1">Prompt Engine Version</label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setFormData({ ...formData, prompt_version: 'v2' })}
                    className={`p-2.5 rounded-lg border text-xs text-left transition-all ${
                      formData.prompt_version === 'v2'
                        ? 'border-teal-500 bg-teal-500/10 text-teal-600 dark:text-teal-400 font-semibold'
                        : 'border-border text-muted-foreground'
                    }`}
                  >
                    <div className="flex items-center gap-1 mb-0.5">
                      <Sparkles className="h-3 w-3" />
                      <span>v2 (Grounded)</span>
                    </div>
                    <p className="text-[10px] text-muted-foreground">Strict [METRIC] citations & zero math hallucination</p>
                  </button>
                  <button
                    type="button"
                    onClick={() => setFormData({ ...formData, prompt_version: 'v1' })}
                    className={`p-2.5 rounded-lg border text-xs text-left transition-all ${
                      formData.prompt_version === 'v1'
                        ? 'border-teal-500 bg-teal-500/10 text-teal-600 dark:text-teal-400 font-semibold'
                        : 'border-border text-muted-foreground'
                    }`}
                  >
                    <div className="flex items-center gap-1 mb-0.5">
                      <Layers className="h-3 w-3" />
                      <span>v1 (Baseline)</span>
                    </div>
                    <p className="text-[10px] text-muted-foreground">Unconstrained baseline for academic comparison</p>
                  </button>
                </div>
              </div>

              <div className="space-y-2 pt-2 border-t border-border/50">
                <p className="text-xs font-semibold text-foreground">Report Sections & Modules</p>
                <label className="flex items-center gap-2.5 text-xs text-muted-foreground cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.include_forecast}
                    onChange={(e) => setFormData({ ...formData, include_forecast: e.target.checked })}
                    className="rounded border-border text-teal-600 focus:ring-teal-500"
                  />
                  <TrendingUp className="h-3.5 w-3.5 text-purple-500" />
                  <span>Include XGBoost Sales Forecast & Naive Baseline Comparison</span>
                </label>
                <label className="flex items-center gap-2.5 text-xs text-muted-foreground cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.include_anomalies}
                    onChange={(e) => setFormData({ ...formData, include_anomalies: e.target.checked })}
                    className="rounded border-border text-teal-600 focus:ring-teal-500"
                  />
                  <Shield className="h-3.5 w-3.5 text-amber-500" />
                  <span>Include Isolation Forest Transaction Outlier Screening</span>
                </label>
                <label className="flex items-center gap-2.5 text-xs text-muted-foreground cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.include_rag}
                    onChange={(e) => setFormData({ ...formData, include_rag: e.target.checked })}
                    className="rounded border-border text-teal-600 focus:ring-teal-500"
                  />
                  <BookOpen className="h-3.5 w-3.5 text-teal-500" />
                  <span>Include Business Policy & Knowledge Base Citations</span>
                </label>
              </div>

              {error && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-xs text-red-600 dark:text-red-400 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <div className="flex items-center justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowGenModal(false)}
                  className="px-4 py-2 rounded-lg text-xs font-medium text-muted-foreground hover:bg-muted"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isGenerating}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-teal-500 hover:bg-teal-600 text-white text-xs font-semibold shadow-md disabled:opacity-50 transition-all"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>Compiling Analytics & PDF…</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4" />
                      <span>Compile Report</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

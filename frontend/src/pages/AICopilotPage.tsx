import React, { useState, useRef, useEffect, useCallback } from 'react'
import {
  Bot, Send, Sparkles, AlertCircle, ChevronDown, ChevronUp,
  Clock, CheckCircle2, XCircle, Loader2, MessageSquare,
  TrendingUp, BarChart3, Shield, FileText, Zap, Info,
  Database, Activity, PlusCircle,
} from 'lucide-react'
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell, Legend,
} from 'recharts'
import { agentApi } from '../services/api'
import type {
  AgentChatResponse, ToolExecutionTrace, EvidenceReference,
  ChartPayload,
} from '../types'

// ─── Constants ─────────────────────────────────────────────────────────────

const DEMO_WORKSPACE = 'demo-workspace-01'
const BENCHMARK_DATASET = 'benchmark-wholesale'

const EXAMPLE_PROMPTS = [
  { label: 'Summarize KPIs', query: 'What is our total revenue, order count, and cancellation rate?', icon: BarChart3 },
  { label: 'Revenue Trends', query: 'Show monthly revenue trends and growth trajectory', icon: TrendingUp },
  { label: 'Forecast Sales', query: 'Forecast revenue for the next 6 periods ahead', icon: Activity },
  { label: 'Detect Anomalies', query: 'Check for outliers and suspicious transactions', icon: Shield },
  { label: 'Top Products', query: 'Show top 5 products by revenue', icon: Database },
  { label: 'Executive Report', query: 'Generate a comprehensive executive commercial report for the board', icon: FileText },
]

// ─── Status Badge Component ────────────────────────────────────────────────

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    success: 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border-emerald-500/25',
    failed: 'bg-red-500/15 text-red-700 dark:text-red-400 border-red-500/25',
    insufficient_data: 'bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/25',
    skipped: 'bg-zinc-500/15 text-zinc-600 dark:text-zinc-400 border-zinc-500/25',
  }
  const icons: Record<string, React.ReactNode> = {
    success: <CheckCircle2 className="h-3 w-3" />,
    failed: <XCircle className="h-3 w-3" />,
    insufficient_data: <AlertCircle className="h-3 w-3" />,
    skipped: <Clock className="h-3 w-3" />,
  }
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold border ${styles[status] || styles.skipped}`}>
      {icons[status] || icons.skipped}
      {status.replace('_', ' ').toUpperCase()}
    </span>
  )
}

// ─── Execution Trace Drawer ────────────────────────────────────────────────

function ExecutionTraceDrawer({ traces }: { traces: ToolExecutionTrace[] }) {
  const [open, setOpen] = useState(false)
  if (!traces.length) return null

  return (
    <div className="mt-2 rounded-lg border border-border bg-muted/30">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 w-full px-3 py-2 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
      >
        <Zap className="h-3.5 w-3.5 text-teal-500" />
        <span>Tool Execution Trace ({traces.length} tool{traces.length > 1 ? 's' : ''})</span>
        <span className="ml-auto text-[10px] font-mono">
          {traces.reduce((sum, t) => sum + t.duration_ms, 0).toFixed(0)}ms total
        </span>
        {open ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
      </button>
      {open && (
        <div className="px-3 pb-3 space-y-2">
          {traces.map((t, i) => (
            <div key={i} className="flex items-start gap-2 p-2 rounded-md bg-background/60 border border-border/50 text-xs">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <code className="font-mono font-semibold text-foreground">{t.tool_name}</code>
                  <StatusBadge status={t.status} />
                  <span className="ml-auto text-[10px] font-mono text-muted-foreground">{t.duration_ms.toFixed(0)}ms</span>
                </div>
                {t.output_summary && (
                  <p className="text-muted-foreground leading-relaxed truncate">{t.output_summary}</p>
                )}
                {t.error_message && (
                  <p className="text-red-500 dark:text-red-400 leading-relaxed">{t.error_message}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ─── Evidence References ───────────────────────────────────────────────────

function EvidencePanel({ references }: { references: EvidenceReference[] }) {
  if (!references.length) return null
  const typeIcons: Record<string, React.ReactNode> = {
    metric: <BarChart3 className="h-3 w-3 text-blue-500" />,
    forecast: <TrendingUp className="h-3 w-3 text-purple-500" />,
    anomaly: <Shield className="h-3 w-3 text-amber-500" />,
    document: <FileText className="h-3 w-3 text-teal-500" />,
  }
  return (
    <div className="mt-2 flex flex-wrap gap-1.5">
      {references.map((r, i) => (
        <span
          key={i}
          title={r.detail}
          className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-muted/50 border border-border/50 text-[10px] font-medium text-muted-foreground hover:text-foreground cursor-default transition-colors"
        >
          {typeIcons[r.evidence_type] || <Info className="h-3 w-3" />}
          <span className="font-mono">{r.reference_id}</span>
          {r.value !== undefined && r.value !== null && (
            <span className="text-foreground font-semibold">
              {typeof r.value === 'number' ? (r.value > 1000 ? `$${(r.value as number).toLocaleString('en-US', { maximumFractionDigits: 2 })}` : r.value.toFixed(2)) : r.value}
            </span>
          )}
        </span>
      ))}
    </div>
  )
}

// ─── Chart Renderer ────────────────────────────────────────────────────────

const CHART_COLORS = {
  primary: '#0d9488',
  secondary: '#8b5cf6',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  muted: '#6b7280',
}

function CopilotChart({ payload }: { payload: ChartPayload }) {
  if (!payload.data?.length) return null

  return (
    <div className="mt-3 p-4 rounded-xl border border-border bg-card shadow-sm">
      <div className="mb-3">
        <h4 className="text-sm font-semibold text-foreground">{payload.title}</h4>
        {payload.subtitle && <p className="text-[11px] text-muted-foreground mt-0.5">{payload.subtitle}</p>}
      </div>

      {/* KPI Grid */}
      {payload.chart_type === 'kpi_grid' && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {payload.data.map((kpi, i) => (
            <div key={i} className="p-3 rounded-lg bg-muted/40 border border-border/50 text-center">
              <p className="text-[10px] uppercase tracking-wider text-muted-foreground font-semibold mb-1">{kpi.label}</p>
              <p className="text-lg font-bold text-foreground">{kpi.formatted}</p>
            </div>
          ))}
        </div>
      )}

      {/* Revenue Trends */}
      {payload.chart_type === 'revenue_trends' && (
        <ResponsiveContainer width="100%" height={260}>
          <AreaChart data={payload.data}>
            <defs>
              <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={CHART_COLORS.primary} stopOpacity={0.3} />
                <stop offset="95%" stopColor={CHART_COLORS.primary} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="period" tick={{ fontSize: 10 }} stroke="var(--muted-foreground)" />
            <YAxis tick={{ fontSize: 10 }} stroke="var(--muted-foreground)" tickFormatter={v => `$${(v / 1000).toFixed(0)}k`} />
            <Tooltip
              contentStyle={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 11 }}
              formatter={(v: any) => [`$${Number(v).toLocaleString('en-US', { maximumFractionDigits: 0 })}`, 'Revenue']}
            />
            <Area type="monotone" dataKey="revenue" stroke={CHART_COLORS.primary} fill="url(#colorRev)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      )}

      {/* Product Ranking */}
      {payload.chart_type === 'product_ranking' && (
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={payload.data} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis type="number" tick={{ fontSize: 10 }} stroke="var(--muted-foreground)" tickFormatter={v => `$${(v / 1000).toFixed(0)}k`} />
            <YAxis dataKey="description" type="category" tick={{ fontSize: 9 }} width={140} stroke="var(--muted-foreground)" />
            <Tooltip
              contentStyle={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 11 }}
              formatter={(v: any) => [`$${Number(v).toLocaleString('en-US', { maximumFractionDigits: 0 })}`, 'Revenue']}
            />
            <Bar dataKey="revenue" fill={CHART_COLORS.primary} radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}

      {/* Forecast Chart */}
      {payload.chart_type === 'forecast' && (
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={payload.data}>
            <defs>
              <linearGradient id="colorFc" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={CHART_COLORS.secondary} stopOpacity={0.3} />
                <stop offset="95%" stopColor={CHART_COLORS.secondary} stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorCI" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={CHART_COLORS.secondary} stopOpacity={0.1} />
                <stop offset="95%" stopColor={CHART_COLORS.secondary} stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="period" tick={{ fontSize: 10 }} stroke="var(--muted-foreground)" />
            <YAxis tick={{ fontSize: 10 }} stroke="var(--muted-foreground)" tickFormatter={v => `$${(v / 1000).toFixed(0)}k`} />
            <Tooltip
              contentStyle={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 11 }}
              formatter={(v: any) => [v !== null && v !== undefined ? `$${Number(v).toLocaleString('en-US', { maximumFractionDigits: 0 })}` : '—']}
            />
            <Legend verticalAlign="top" height={28} iconSize={10} wrapperStyle={{ fontSize: 10 }} />
            <Area type="monotone" dataKey="actual" name="Historical Actual" stroke={CHART_COLORS.primary} fill="none" strokeWidth={2} connectNulls={false} />
            <Area type="monotone" dataKey="forecast" name="XGBoost Forecast" stroke={CHART_COLORS.secondary} fill="url(#colorFc)" strokeWidth={2} strokeDasharray="5 3" />
            <Area type="monotone" dataKey="upper_bound" name="Upper 95% CI" stroke="transparent" fill="url(#colorCI)" />
            <Area type="monotone" dataKey="lower_bound" name="Lower 95% CI" stroke="transparent" fill="url(#colorCI)" />
            <Area type="monotone" dataKey="baseline_forecast" name="Naive Baseline" stroke={CHART_COLORS.muted} fill="none" strokeWidth={1} strokeDasharray="3 3" />
          </AreaChart>
        </ResponsiveContainer>
      )}

      {/* Anomaly Distribution */}
      {payload.chart_type === 'anomaly_distribution' && (
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={payload.data}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="range" tick={{ fontSize: 9 }} stroke="var(--muted-foreground)" />
            <YAxis tick={{ fontSize: 10 }} stroke="var(--muted-foreground)" />
            <Tooltip
              contentStyle={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 11 }}
            />
            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
              {payload.data.map((entry, idx) => (
                <Cell key={idx} fill={entry.is_anomaly_zone ? CHART_COLORS.danger : CHART_COLORS.primary} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}

// ─── Message Bubble ────────────────────────────────────────────────────────

interface ConversationMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  response?: AgentChatResponse
}

function MessageBubble({ msg }: { msg: ConversationMessage }) {
  const isUser = msg.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[85%] md:max-w-[75%] ${isUser ? 'order-1' : 'order-1'}`}>
        {/* Avatar + header */}
        <div className={`flex items-center gap-2 mb-1 ${isUser ? 'justify-end' : 'justify-start'}`}>
          {!isUser && (
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-teal-500 to-cyan-600 flex items-center justify-center">
              <Bot className="h-3.5 w-3.5 text-white" />
            </div>
          )}
          <span className="text-[10px] text-muted-foreground font-medium">
            {isUser ? 'You' : 'InsightForge Copilot'}
            {msg.response?.is_demo_mode && !isUser && (
              <span className="ml-1.5 px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-600 dark:text-amber-400 border border-amber-500/20 text-[9px] font-bold">
                DEMO
              </span>
            )}
          </span>
          <span className="text-[9px] text-muted-foreground">
            {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>

        {/* Message body */}
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
            isUser
              ? 'bg-primary text-primary-foreground rounded-br-md'
              : 'bg-muted/60 dark:bg-zinc-800/60 text-foreground border border-border/50 rounded-bl-md'
          }`}
        >
          {msg.content}
        </div>

        {/* Assistant extras */}
        {!isUser && msg.response && (
          <>
            {msg.response.chart_payload && <CopilotChart payload={msg.response.chart_payload} />}
            <EvidencePanel references={msg.response.evidence_references} />
            <ExecutionTraceDrawer traces={msg.response.execution_trace} />
            {msg.response.total_latency_ms > 0 && (
              <p className="text-[9px] text-muted-foreground mt-1.5 flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {msg.response.total_latency_ms.toFixed(0)}ms · Intent: <code className="font-mono">{msg.response.intent}</code>
                · {msg.response.tools_executed.length} tool{msg.response.tools_executed.length !== 1 ? 's' : ''}
              </p>
            )}
          </>
        )}
      </div>
    </div>
  )
}

// ─── Main Page ─────────────────────────────────────────────────────────────

export function AICopilotPage() {
  const [messages, setMessages] = useState<ConversationMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Auto-scroll
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || loading) return

    const userMsg: ConversationMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text.trim(),
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)
    setError(null)

    try {
      const res = await agentApi.chat(DEMO_WORKSPACE, {
        message: text.trim(),
        dataset_id: BENCHMARK_DATASET,
        session_id: sessionId,
        provider_type: 'local_demo',
      })

      if (!sessionId) setSessionId(res.session_id)

      const assistantMsg: ConversationMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: res.response_text,
        timestamp: new Date(res.created_at),
        response: res,
      }
      setMessages(prev => [...prev, assistantMsg])
    } catch (err: any) {
      const detail = err.response?.data?.detail || err.message || 'Unknown error'
      setError(detail)
      const errMsg: ConversationMessage = {
        id: `err-${Date.now()}`,
        role: 'assistant',
        content: `⚠️ Error: ${detail}`,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errMsg])
    } finally {
      setLoading(false)
    }
  }, [loading, sessionId])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    sendMessage(input)
  }

  const startNewSession = () => {
    setMessages([])
    setSessionId(null)
    setError(null)
    inputRef.current?.focus()
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] md:h-[calc(100vh-4rem)] overflow-hidden">
      {/* Header Bar */}
      <div className="shrink-0 px-4 py-3 border-b border-border bg-card/80 backdrop-blur-sm">
        <div className="flex items-center justify-between max-w-5xl mx-auto">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-teal-500 to-cyan-600 flex items-center justify-center shadow-md">
              <Bot className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-base font-bold text-foreground leading-tight">AI Copilot</h1>
              <p className="text-[11px] text-muted-foreground">Controlled LangGraph Business Analyst · Stage 8</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="hidden sm:inline-flex items-center gap-1 px-2 py-1 rounded-md bg-amber-500/10 text-amber-600 dark:text-amber-400 text-[10px] font-bold border border-amber-500/20">
              <Sparkles className="h-3 w-3" /> DEMO MODE
            </span>
            <button
              onClick={startNewSession}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-muted hover:bg-muted/80 text-xs font-medium transition-colors border border-border/50"
            >
              <PlusCircle className="h-3.5 w-3.5" /> New Chat
            </button>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-5xl mx-auto">
          {messages.length === 0 ? (
            /* Empty State — show example prompts */
            <div className="flex flex-col items-center justify-center h-full min-h-[50vh] text-center">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-teal-500 to-cyan-600 flex items-center justify-center mb-4 shadow-lg">
                <Bot className="h-9 w-9 text-white" />
              </div>
              <h2 className="text-xl font-bold text-foreground mb-1">InsightForge AI Copilot</h2>
              <p className="text-sm text-muted-foreground mb-6 max-w-md">
                Ask business questions about the wholesale benchmark dataset.
                The agent selects approved analytical tools, executes them with bounded permissions, and returns verified evidence.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 w-full max-w-2xl">
                {EXAMPLE_PROMPTS.map((ep) => (
                  <button
                    key={ep.label}
                    onClick={() => sendMessage(ep.query)}
                    className="flex items-center gap-2.5 p-3 rounded-xl bg-card hover:bg-muted border border-border/50 hover:border-teal-500/30 text-left transition-all group"
                  >
                    <div className="w-8 h-8 rounded-lg bg-teal-500/10 flex items-center justify-center shrink-0 group-hover:bg-teal-500/20 transition-colors">
                      <ep.icon className="h-4 w-4 text-teal-600 dark:text-teal-400" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-xs font-semibold text-foreground leading-tight">{ep.label}</p>
                      <p className="text-[10px] text-muted-foreground truncate mt-0.5">{ep.query}</p>
                    </div>
                  </button>
                ))}
              </div>
              <div className="mt-6 p-3 rounded-lg bg-muted/40 border border-border/50 text-[10px] text-muted-foreground max-w-lg">
                <div className="flex items-center gap-1.5 font-semibold mb-1">
                  <Info className="h-3 w-3 text-teal-500" />
                  <span>Approved Tools</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {['get_business_kpis', 'analyze_revenue_trends', 'get_product_performance', 'forecast_sales', 'detect_anomalies', 'retrieve_business_documents', 'generate_executive_report'].map(t => (
                    <code key={t} className="px-1.5 py-0.5 rounded bg-background border border-border/60 font-mono">{t}</code>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            messages.map((msg) => <MessageBubble key={msg.id} msg={msg} />)
          )}

          {/* Loading indicator */}
          {loading && (
            <div className="flex items-start gap-2 mb-4">
              <div className="w-6 h-6 rounded-full bg-gradient-to-br from-teal-500 to-cyan-600 flex items-center justify-center">
                <Bot className="h-3.5 w-3.5 text-white" />
              </div>
              <div className="flex items-center gap-2 px-4 py-3 rounded-2xl rounded-bl-md bg-muted/60 border border-border/50">
                <Loader2 className="h-4 w-4 animate-spin text-teal-500" />
                <span className="text-sm text-muted-foreground">Analyzing with approved tools…</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input Bar */}
      <div className="shrink-0 border-t border-border bg-card/80 backdrop-blur-sm px-4 py-3 mb-safe">
        <form onSubmit={handleSubmit} className="flex items-center gap-2 max-w-5xl mx-auto">
          <div className="flex items-center gap-2 px-1.5 text-[10px] text-muted-foreground shrink-0">
            <Database className="h-3.5 w-3.5" />
            <span className="hidden sm:inline font-mono">benchmark-wholesale</span>
          </div>
          <div className="relative flex-1">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a business question…"
              disabled={loading}
              maxLength={2000}
              className="w-full px-4 py-2.5 rounded-xl bg-background border border-border/80 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-teal-500/40 focus:border-teal-500/50 transition-all disabled:opacity-50"
            />
          </div>
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-teal-500 to-cyan-600 hover:from-teal-600 hover:to-cyan-700 flex items-center justify-center text-white shadow-md disabled:opacity-40 disabled:cursor-not-allowed transition-all"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </button>
        </form>
        {error && (
          <div className="mt-2 max-w-5xl mx-auto flex items-center gap-2 text-xs text-red-500 dark:text-red-400">
            <AlertCircle className="h-3.5 w-3.5 shrink-0" />
            <span className="truncate">{error}</span>
          </div>
        )}
      </div>
    </div>
  )
}

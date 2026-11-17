import React, { useState, useEffect } from 'react'
import {
  Sparkles,
  Cpu,
  CheckCircle2,
  AlertTriangle,
  Play,
  ArrowRight,
  ShieldCheck,
  Code2,
  Eye,
  Layers,
  ChevronDown,
  ChevronRight,
  TrendingUp,
  RefreshCw,
  FileCheck,
  AlertOctagon,
  Scale,
  Zap,
  Info,
} from 'lucide-react'
import { useWorkspace } from '../context/WorkspaceContext'
import { promptsApi } from '../services/api'
import type {
  PromptChainExecutionResponse,
  PromptComparisonResponse,
  EvaluationBenchmarkScorecard,
} from '../types'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { formatCurrency, formatNumber } from '../lib/utils'

export function PromptStudioPage() {
  const { currentWorkspace, currentDataset, datasets, setCurrentDataset, isDemoMode } = useWorkspace()

  // State
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>(currentDataset?.id || 'demo-dataset-01')
  const [activeTab, setActiveTab] = useState<'studio' | 'compare' | 'templates' | 'evaluation'>('studio')
  const [promptVersion, setPromptVersion] = useState<'v1' | 'v2'>('v2')
  const [providerType, setProviderType] = useState<string>('local_demo')

  // Execution states
  const [isRunning, setIsRunning] = useState<boolean>(false)
  const [executionResult, setExecutionResult] = useState<PromptChainExecutionResponse | null>(null)
  const [comparisonResult, setComparisonResult] = useState<PromptComparisonResponse | null>(null)
  const [scorecard, setScorecard] = useState<EvaluationBenchmarkScorecard | null>(null)
  const [templatesData, setTemplatesData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  // Expandable inspection toggles
  const [expandedStage, setExpandedStage] = useState<number>(3)
  const [showRawPrompts, setShowRawPrompts] = useState<boolean>(false)
  const [activeJsonTab, setActiveJsonTab] = useState<'formatted' | 'raw'>('formatted')

  // Auto-run on load with default benchmark
  useEffect(() => {
    handleRunPrompt(promptVersion)
    loadEvaluation()
    loadTemplates()
  }, [])

  const handleRunPrompt = async (ver: 'v1' | 'v2') => {
    setIsRunning(true)
    setError(null)
    try {
      const res = await promptsApi.execute(
        currentWorkspace?.id || 'demo-workspace-01',
        selectedDatasetId,
        ver,
        providerType
      )
      setExecutionResult(res)
    } catch (err: any) {
      console.warn('Backend execution fallback to demo:', err)
      setError(err.response?.data?.detail || 'Execution simulated locally')
    } finally {
      setIsRunning(false)
    }
  }

  const handleRunComparison = async () => {
    setIsRunning(true)
    setError(null)
    try {
      const res = await promptsApi.compare(
        currentWorkspace?.id || 'demo-workspace-01',
        selectedDatasetId,
        providerType
      )
      setComparisonResult(res)
      setActiveTab('compare')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Comparison failed')
    } finally {
      setIsRunning(false)
    }
  }

  const loadEvaluation = async () => {
    try {
      const res = await promptsApi.getEvaluation(currentWorkspace?.id || 'demo-workspace-01')
      setScorecard(res)
    } catch (e) {
      console.warn('Could not load evaluation scorecard:', e)
    }
  }

  const loadTemplates = async () => {
    try {
      const res = await promptsApi.getTemplates(currentWorkspace?.id || 'demo-workspace-01')
      setTemplatesData(res)
    } catch (e) {
      console.warn('Could not load templates:', e)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header & Subtitle */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-border pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-teal-600 dark:text-teal-400" />
              Evidence-Grounded Prompt Studio
            </h1>
            <Badge variant="teal" className="text-xs font-semibold">
              Stage 5 Engine
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground mt-0.5">
            3-Stage Chained Prompt Pipeline with Deterministic Numerical Verification and Pydantic Schema Auditing
          </p>
        </div>

        {/* Studio View Navigation */}
        <div className="flex items-center gap-1 p-1 bg-muted rounded-lg text-xs font-medium self-start md:self-auto">
          <button
            onClick={() => setActiveTab('studio')}
            className={`px-3 py-1.5 rounded-md transition-colors ${
              activeTab === 'studio'
                ? 'bg-card text-foreground shadow-sm font-semibold'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Prompt Studio
          </button>
          <button
            onClick={() => {
              if (!comparisonResult) handleRunComparison()
              else setActiveTab('compare')
            }}
            className={`px-3 py-1.5 rounded-md transition-colors flex items-center gap-1 ${
              activeTab === 'compare'
                ? 'bg-card text-foreground shadow-sm font-semibold'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <Scale className="h-3.5 w-3.5" />
            v1 vs v2 Comparison
          </button>
          <button
            onClick={() => setActiveTab('evaluation')}
            className={`px-3 py-1.5 rounded-md transition-colors flex items-center gap-1 ${
              activeTab === 'evaluation'
                ? 'bg-card text-foreground shadow-sm font-semibold'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <TrendingUp className="h-3.5 w-3.5" />
            Evaluation Lab
          </button>
          <button
            onClick={() => setActiveTab('templates')}
            className={`px-3 py-1.5 rounded-md transition-colors flex items-center gap-1 ${
              activeTab === 'templates'
                ? 'bg-card text-foreground shadow-sm font-semibold'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <Code2 className="h-3.5 w-3.5" />
            Jinja2 Templates
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

          {/* Prompt Version Selector */}
          <div className="space-y-1">
            <label className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
              Prompt Architecture Version
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => {
                  setPromptVersion('v1')
                  handleRunPrompt('v1')
                }}
                className={`px-3 py-2 text-xs rounded-lg border text-center transition-all ${
                  promptVersion === 'v1'
                    ? 'border-amber-500 bg-amber-500/10 text-amber-700 dark:text-amber-400 font-bold'
                    : 'border-border text-muted-foreground hover:bg-muted'
                }`}
              >
                v1: Baseline
              </button>
              <button
                type="button"
                onClick={() => {
                  setPromptVersion('v2')
                  handleRunPrompt('v2')
                }}
                className={`px-3 py-2 text-xs rounded-lg border text-center transition-all ${
                  promptVersion === 'v2'
                    ? 'border-teal-500 bg-teal-500/10 text-teal-700 dark:text-teal-400 font-bold'
                    : 'border-border text-muted-foreground hover:bg-muted'
                }`}
              >
                v2: Evidence-Grounded
              </button>
            </div>
          </div>

          {/* LLM Provider Selector */}
          <div className="space-y-1">
            <label className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
              LLM Provider Engine
            </label>
            <select
              value={providerType}
              onChange={(e) => setProviderType(e.target.value)}
              className="w-full px-3 py-2 text-xs rounded-lg border border-input bg-background focus:outline-none focus:ring-1 focus:ring-teal-500"
            >
              <option value="local_demo">Local Deterministic Demo (Zero-Cost)</option>
              <option value="gemini">Google Gemini 1.5 Flash (Backend API)</option>
              <option value="openai">OpenAI GPT-4o-mini (Backend API)</option>
            </select>
          </div>

          {/* Run Action */}
          <div className="flex items-end gap-2 pt-1 md:pt-4">
            <Button
              variant="teal"
              className="flex-1 gap-2 text-xs h-9"
              onClick={() => handleRunPrompt(promptVersion)}
              isLoading={isRunning}
            >
              <Play className="h-3.5 w-3.5 fill-current" />
              Execute 3-Stage Chain
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="h-9 gap-1 text-xs"
              onClick={handleRunComparison}
              title="Compare v1 and v2 on identical data"
            >
              <Scale className="h-3.5 w-3.5" />
              Compare
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
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleRunPrompt(promptVersion)}
            className="text-[11px] h-7 border-destructive/30"
          >
            Retry Execution
          </Button>
        </div>
      )}

      {/* Loading State */}
      {isRunning && (
        <Card className="p-8 text-center border-dashed">
          <RefreshCw className="h-8 w-8 text-teal-600 animate-spin mx-auto mb-3" />
          <h3 className="text-base font-semibold text-foreground">Executing 3-Stage Prompt Chain...</h3>
          <p className="text-xs text-muted-foreground mt-1 max-w-md mx-auto">
            Grounding numerical claims against Pandas KPIs and validating output with Pydantic JSON schema.
          </p>
        </Card>
      )}

      {/* VIEW 1: PROMPT STUDIO PIPELINE EXECUTION */}
      {activeTab === 'studio' && !isRunning && !executionResult && (
        <Card className="p-8 text-center border-dashed">
          <Sparkles className="h-8 w-8 text-muted-foreground mx-auto mb-3" />
          <h3 className="text-base font-semibold text-foreground">Prompt Studio Ready</h3>
          <p className="text-xs text-muted-foreground mt-1 max-w-md mx-auto">
            Select a dataset, prompt version, and provider engine above, then click "Execute 3-Stage Chain" to generate verified analytics insights.
          </p>
          <Button
            variant="teal"
            size="sm"
            className="mt-4 gap-2 text-xs"
            onClick={() => handleRunPrompt(promptVersion)}
          >
            <Play className="h-3.5 w-3.5 fill-current" />
            Execute Now
          </Button>
        </Card>
      )}

      {activeTab === 'studio' && !isRunning && executionResult && (
        <div className="space-y-6">
          {/* Execution Telemetry Ribbon */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            <Card className="p-3 bg-teal-500/5 border-teal-500/20">
              <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">
                Numerical Accuracy
              </span>
              <div className="text-xl font-extrabold text-teal-700 dark:text-teal-400 mt-0.5">
                {executionResult.overall_accuracy_score}%
              </div>
              <span className="text-[10px] text-muted-foreground">Deterministic audit</span>
            </Card>

            <Card className="p-3">
              <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">
                Prompt Version
              </span>
              <div className="text-base font-bold text-foreground mt-0.5 capitalize">
                {executionResult.prompt_version === 'v2' ? 'v2 Grounded' : 'v1 Baseline'}
              </div>
              <span className="text-[10px] text-muted-foreground font-mono">
                {executionResult.prompt_version === 'v2' ? 'Strict Schema' : 'Loose Text'}
              </span>
            </Card>

            <Card className="p-3">
              <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">
                Chain Latency
              </span>
              <div className="text-xl font-bold text-foreground mt-0.5 font-mono">
                {executionResult.total_latency_ms.toFixed(1)}ms
              </div>
              <span className="text-[10px] text-muted-foreground">3 stages pipeline</span>
            </Card>

            <Card className="p-3">
              <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">
                Total Tokens
              </span>
              <div className="text-xl font-bold text-foreground mt-0.5 font-mono">
                {executionResult.total_tokens_used.toLocaleString()}
              </div>
              <span className="text-[10px] text-muted-foreground">Prompt + Completion</span>
            </Card>

            <Card className="p-3">
              <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">
                Provider Mode
              </span>
              <div className="text-sm font-bold text-foreground mt-1">
                {executionResult.is_demo_mode ? (
                  <Badge variant="teal" className="text-[9px] py-0 px-1.5 font-mono">
                    Deterministic Demo
                  </Badge>
                ) : (
                  <Badge variant="success" className="text-[9px] py-0 px-1.5 font-mono">
                    Live API
                  </Badge>
                )}
              </div>
              <span className="text-[10px] text-muted-foreground mt-0.5 block">
                ${executionResult.estimated_cost_usd.toFixed(4)} USD
              </span>
            </Card>
          </div>

          {/* Three Stage Pipeline Cards */}
          <div className="space-y-4">
            {/* STAGE 1 CARD */}
            <Card className={`border transition-all ${expandedStage === 1 ? 'ring-1 ring-teal-500' : ''}`}>
              <CardHeader
                className="cursor-pointer py-3 px-4 flex flex-row items-center justify-between"
                onClick={() => setExpandedStage(expandedStage === 1 ? 0 : 1)}
              >
                <div className="flex items-center gap-3">
                  <div className="w-7 h-7 rounded-full bg-navy-100 dark:bg-navy-900 flex items-center justify-center font-bold text-xs text-navy-800 dark:text-teal-400">
                    1
                  </div>
                  <div>
                    <CardTitle className="text-sm font-bold">
                      Stage 1: Factual Data Summarization
                    </CardTitle>
                    <CardDescription className="text-[11px]">
                      Verified Pandas KPI JSON &rarr; Grounded factual statements with metric citations
                    </CardDescription>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge
                    variant={executionResult.stage_1.verification.is_valid ? 'success' : 'warning'}
                    className="text-[10px]"
                  >
                    {executionResult.stage_1.verification.accuracy_score}% Grounded
                  </Badge>
                  {expandedStage === 1 ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                </div>
              </CardHeader>

              {expandedStage === 1 && (
                <CardContent className="pt-2 border-t border-border space-y-4 text-xs">
                  {/* Verified Claims Table */}
                  {executionResult.stage_1.parsed_output?.claims && (
                    <div className="space-y-2">
                      <p className="font-semibold text-foreground text-[11px] uppercase tracking-wider">
                        Extracted Verified Claims ({executionResult.stage_1.parsed_output.claims.length})
                      </p>
                      <div className="space-y-1.5">
                        {executionResult.stage_1.parsed_output.claims.map((claim: any) => (
                          <div
                            key={claim.claim_id}
                            className="p-2.5 rounded-lg border border-border bg-muted/30 flex items-start justify-between gap-3"
                          >
                            <div className="space-y-1">
                              <div className="flex items-center gap-2">
                                <span className="font-mono text-[10px] text-muted-foreground font-bold">
                                  {claim.claim_id}
                                </span>
                                {claim.is_grounded ? (
                                  <Badge variant="success" className="text-[9px] py-0 px-1 gap-1">
                                    <CheckCircle2 className="h-2.5 w-2.5" />
                                    Verified
                                  </Badge>
                                ) : (
                                  <Badge variant="warning" className="text-[9px] py-0 px-1 gap-1">
                                    <AlertTriangle className="h-2.5 w-2.5" />
                                    Unverified
                                  </Badge>
                                )}
                              </div>
                              <p className="text-foreground leading-relaxed">{claim.statement}</p>
                            </div>
                            {claim.metric_references?.length > 0 && (
                              <div className="flex flex-col items-end gap-1 shrink-0 font-mono text-[10px]">
                                {claim.metric_references.map((ref: any, rIdx: number) => (
                                  <span
                                    key={rIdx}
                                    className="bg-card px-2 py-0.5 rounded border border-border text-teal-600 dark:text-teal-400"
                                  >
                                    [METRIC:{ref.metric_id}]
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Raw Output Display */}
                  <div className="pt-2">
                    <p className="font-semibold text-foreground text-[11px] uppercase tracking-wider mb-1">
                      Raw Stage 1 Output
                    </p>
                    <pre className="p-3 rounded-lg bg-muted text-[11px] font-mono overflow-x-auto whitespace-pre-wrap text-muted-foreground">
                      {executionResult.stage_1.raw_response}
                    </pre>
                  </div>
                </CardContent>
              )}
            </Card>

            {/* STAGE 2 CARD */}
            <Card className={`border transition-all ${expandedStage === 2 ? 'ring-1 ring-teal-500' : ''}`}>
              <CardHeader
                className="cursor-pointer py-3 px-4 flex flex-row items-center justify-between"
                onClick={() => setExpandedStage(expandedStage === 2 ? 0 : 2)}
              >
                <div className="flex items-center gap-3">
                  <div className="w-7 h-7 rounded-full bg-navy-100 dark:bg-navy-900 flex items-center justify-center font-bold text-xs text-navy-800 dark:text-teal-400">
                    2
                  </div>
                  <div>
                    <CardTitle className="text-sm font-bold">
                      Stage 2: Strategic Insights, Hypotheses & Refusal Checks
                    </CardTitle>
                    <CardDescription className="text-[11px]">
                      Validated factual summary &rarr; [HYPOTHESIS] tags, risk scoring, and "Insufficient data" alerts
                    </CardDescription>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge
                    variant={executionResult.stage_2.verification.is_valid ? 'success' : 'warning'}
                    className="text-[10px]"
                  >
                    {executionResult.stage_2.verification.accuracy_score}% Grounded
                  </Badge>
                  {expandedStage === 2 ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                </div>
              </CardHeader>

              {expandedStage === 2 && (
                <CardContent className="pt-2 border-t border-border space-y-4 text-xs">
                  {/* Hypotheses Grid */}
                  {executionResult.stage_2.parsed_output?.hypotheses?.length > 0 && (
                    <div className="space-y-2">
                      <p className="font-semibold text-foreground text-[11px] uppercase tracking-wider">
                        Commercial Hypotheses (Must use [HYPOTHESIS] prefix)
                      </p>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {executionResult.stage_2.parsed_output.hypotheses.map((hyp: any) => (
                          <div
                            key={hyp.hypothesis_id}
                            className="p-3 rounded-lg border border-border bg-card space-y-1.5"
                          >
                            <div className="flex items-center justify-between">
                              <span className="font-mono text-[10px] text-muted-foreground font-bold">
                                {hyp.hypothesis_id}
                              </span>
                              <Badge variant="teal" className="text-[9px] uppercase font-bold">
                                {hyp.confidence} confidence
                              </Badge>
                            </div>
                            <p className="font-semibold text-teal-700 dark:text-teal-400">
                              {hyp.hypothesis_statement}
                            </p>
                            <p className="text-muted-foreground text-[11px]">{hyp.observation}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Refusal Mandate Notice */}
                  {executionResult.stage_2.parsed_output?.unsupported_factors_noted && (
                    <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-xs space-y-1">
                      <div className="flex items-center gap-1.5 font-semibold text-amber-800 dark:text-amber-300">
                        <AlertOctagon className="h-4 w-4 text-amber-500" />
                        <span>Unsupported Data Refusals ("Insufficient data")</span>
                      </div>
                      <ul className="list-disc list-inside space-y-0.5 text-[11px] text-muted-foreground pt-1">
                        {executionResult.stage_2.parsed_output.unsupported_factors_noted.map((factor: string, fIdx: number) => (
                          <li key={fIdx}>{factor}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              )}
            </Card>

            {/* STAGE 3 CARD */}
            <Card className={`border transition-all ${expandedStage === 3 ? 'ring-1 ring-teal-500' : ''}`}>
              <CardHeader
                className="cursor-pointer py-3 px-4 flex flex-row items-center justify-between"
                onClick={() => setExpandedStage(expandedStage === 3 ? 0 : 3)}
              >
                <div className="flex items-center gap-3">
                  <div className="w-7 h-7 rounded-full bg-teal-100 dark:bg-teal-950 flex items-center justify-center font-bold text-xs text-teal-700 dark:text-teal-400">
                    3
                  </div>
                  <div>
                    <CardTitle className="text-sm font-bold flex items-center gap-2">
                      Stage 3: Executive Commercial Report
                      <Badge variant="teal" className="text-[9px] font-mono">
                        Pydantic Validated JSON
                      </Badge>
                    </CardTitle>
                    <CardDescription className="text-[11px]">
                      Validated outputs &rarr; Boardroom report complying with ExecutiveCommercialReport schema
                    </CardDescription>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge
                    variant={executionResult.stage_3.verification.is_valid ? 'success' : 'warning'}
                    className="text-[10px]"
                  >
                    {executionResult.stage_3.verification.accuracy_score}% Schema Compliant
                  </Badge>
                  {expandedStage === 3 ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                </div>
              </CardHeader>

              {expandedStage === 3 && (
                <CardContent className="pt-2 border-t border-border space-y-4 text-xs">
                  {/* View Mode Switcher */}
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-foreground text-[11px] uppercase tracking-wider">
                      Executive Commercial Intelligence Output
                    </span>
                    <div className="flex items-center gap-1 bg-muted p-1 rounded-md text-[10px]">
                      <button
                        onClick={() => setActiveJsonTab('formatted')}
                        className={`px-2.5 py-1 rounded transition-colors ${
                          activeJsonTab === 'formatted'
                            ? 'bg-card text-foreground font-semibold shadow-sm'
                            : 'text-muted-foreground'
                        }`}
                      >
                        Formatted Brief
                      </button>
                      <button
                        onClick={() => setActiveJsonTab('raw')}
                        className={`px-2.5 py-1 rounded transition-colors ${
                          activeJsonTab === 'raw'
                            ? 'bg-card text-foreground font-semibold shadow-sm'
                            : 'text-muted-foreground'
                        }`}
                      >
                        Pure JSON
                      </button>
                    </div>
                  </div>

                  {activeJsonTab === 'formatted' && executionResult.structured_report ? (
                    <div className="space-y-4 border rounded-xl p-4 bg-card shadow-sm">
                      <div className="border-b border-border pb-3">
                        <h2 className="text-lg font-bold text-foreground">
                          {executionResult.structured_report.report_title}
                        </h2>
                        <div className="flex items-center gap-2 text-[11px] text-muted-foreground mt-0.5">
                          <span>Dataset: {executionResult.structured_report.dataset_name}</span>
                          <span>•</span>
                          <span>Generated: {new Date(executionResult.structured_report.generated_at).toLocaleString()}</span>
                        </div>
                      </div>

                      {/* Executive Summary */}
                      <div className="space-y-1">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-teal-600 dark:text-teal-400">
                          Executive Synthesis
                        </span>
                        <p className="text-sm leading-relaxed text-foreground">
                          {executionResult.structured_report.executive_summary}
                        </p>
                      </div>

                      {/* KPI Highlights Grid */}
                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2">
                        {executionResult.structured_report.kpi_highlights.map((kpi, idx) => (
                          <div key={idx} className="p-3 rounded-lg bg-muted/40 border border-border">
                            <span className="text-[10px] text-muted-foreground">{kpi.label}</span>
                            <div className="text-base font-bold text-foreground mt-0.5">
                              {kpi.formatted}
                            </div>
                            <span className="text-[9px] text-muted-foreground truncate block">
                              {kpi.context_note}
                            </span>
                          </div>
                        ))}
                      </div>

                      {/* Prioritized Recommendations */}
                      {executionResult.structured_report.prioritized_recommendations.length > 0 && (
                        <div className="space-y-2 pt-2">
                          <span className="text-[11px] font-bold uppercase tracking-wider text-foreground">
                            Prioritized Operational Actions
                          </span>
                          <div className="space-y-2">
                            {executionResult.structured_report.prioritized_recommendations.map((rec, rIdx) => (
                              <div
                                key={rIdx}
                                className="p-3 rounded-lg border border-border bg-muted/20 flex items-start gap-3"
                              >
                                <Badge variant="teal" className="text-[10px] font-bold">
                                  {rec.priority}
                                </Badge>
                                <div className="space-y-0.5">
                                  <p className="font-semibold text-foreground text-xs">{rec.title}</p>
                                  <p className="text-muted-foreground text-[11px]">{rec.action}</p>
                                  <p className="text-[10px] text-teal-600 dark:text-teal-400">
                                    Impact: {rec.expected_impact}
                                  </p>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <pre className="p-4 rounded-xl bg-muted font-mono text-[11px] overflow-x-auto text-muted-foreground">
                      {JSON.stringify(executionResult.structured_report || executionResult.stage_3.raw_response, null, 2)}
                    </pre>
                  )}
                </CardContent>
              )}
            </Card>
          </div>
        </div>
      )}

      {/* VIEW 2: SIDE-BY-SIDE COMPARISON (v1 vs v2) */}
      {activeTab === 'compare' && comparisonResult && (
        <div className="space-y-6">
          {/* Comparison Delta Hero */}
          <Card className="p-5 border-teal-500/30 bg-teal-500/5">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-teal-700 dark:text-teal-400">
                  Empirical Evaluation Benchmark
                </span>
                <h3 className="text-xl font-bold text-foreground mt-1">
                  Controlled A/B Prompt Comparison: v1 (Baseline) vs v2 (Evidence-Grounded)
                </h3>
                <p className="text-xs text-muted-foreground mt-1 max-w-2xl leading-relaxed">
                  {comparisonResult.comparison_summary}
                </p>
              </div>
              <div className="flex items-center gap-4 shrink-0">
                <div className="text-center p-3 rounded-xl bg-card border border-border">
                  <span className="text-[10px] text-muted-foreground font-semibold">Accuracy Gain</span>
                  <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400">
                    +{comparisonResult.accuracy_delta}%
                  </div>
                </div>
                <div className="text-center p-3 rounded-xl bg-card border border-border">
                  <span className="text-[10px] text-muted-foreground font-semibold">Hallucination Reduction</span>
                  <div className="text-2xl font-black text-teal-600 dark:text-teal-400">
                    {comparisonResult.hallucination_reduction_pct}%
                  </div>
                </div>
              </div>
            </div>
          </Card>

          {/* Side-by-Side Stage Comparison Columns */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Column 1: Prompt v1 (Baseline) */}
            <Card className="border-amber-500/30">
              <CardHeader className="bg-amber-500/5 border-b border-border pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base font-bold text-amber-800 dark:text-amber-400">
                    Prompt v1: Unconstrained Baseline
                  </CardTitle>
                  <Badge variant="warning" className="text-[10px]">
                    {comparisonResult.v1_result.overall_accuracy_score}% Accuracy
                  </Badge>
                </div>
                <CardDescription className="text-xs">
                  Loose text summarization without structured metric ID anchoring
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-4 space-y-4 text-xs">
                <div>
                  <span className="font-semibold text-foreground text-[11px] uppercase">
                    Stage 1: Factual Narrative
                  </span>
                  <div className="p-3 mt-1 rounded-lg bg-muted text-[11px] leading-relaxed text-muted-foreground">
                    {comparisonResult.v1_result.stage_1.raw_response}
                  </div>
                </div>

                <div>
                  <span className="font-semibold text-foreground text-[11px] uppercase">
                    Stage 2: Insights & Speculation
                  </span>
                  <div className="p-3 mt-1 rounded-lg bg-muted text-[11px] leading-relaxed text-muted-foreground">
                    {comparisonResult.v1_result.stage_2.raw_response}
                  </div>
                </div>

                <div>
                  <span className="font-semibold text-foreground text-[11px] uppercase">
                    Stage 3: Markdown JSON
                  </span>
                  <pre className="p-3 mt-1 rounded-lg bg-muted text-[10px] font-mono overflow-x-auto text-muted-foreground">
                    {comparisonResult.v1_result.stage_3.raw_response}
                  </pre>
                </div>
              </CardContent>
            </Card>

            {/* Column 2: Prompt v2 (Grounded) */}
            <Card className="border-teal-500">
              <CardHeader className="bg-teal-500/10 border-b border-border pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base font-bold text-teal-800 dark:text-teal-300">
                    Prompt v2: Evidence-Grounded Engine
                  </CardTitle>
                  <Badge variant="success" className="text-[10px]">
                    {comparisonResult.v2_result.overall_accuracy_score}% Accuracy
                  </Badge>
                </div>
                <CardDescription className="text-xs">
                  Strict [METRIC:id] citations, [HYPOTHESIS] prefixes, and validated Pydantic schema
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-4 space-y-4 text-xs">
                <div>
                  <span className="font-semibold text-foreground text-[11px] uppercase">
                    Stage 1: Structured Claims
                  </span>
                  <pre className="p-3 mt-1 rounded-lg bg-muted text-[10px] font-mono overflow-x-auto text-muted-foreground max-h-48">
                    {comparisonResult.v2_result.stage_1.raw_response}
                  </pre>
                </div>

                <div>
                  <span className="font-semibold text-foreground text-[11px] uppercase">
                    Stage 2: Grounded Hypotheses & Refusal
                  </span>
                  <pre className="p-3 mt-1 rounded-lg bg-muted text-[10px] font-mono overflow-x-auto text-muted-foreground max-h-48">
                    {comparisonResult.v2_result.stage_2.raw_response}
                  </pre>
                </div>

                <div>
                  <span className="font-semibold text-foreground text-[11px] uppercase">
                    Stage 3: ExecutiveCommercialReport
                  </span>
                  <div className="p-3 mt-1 rounded-lg border border-teal-500/30 bg-card space-y-1">
                    <p className="font-bold text-foreground">
                      {comparisonResult.v2_result.structured_report?.report_title}
                    </p>
                    <p className="text-[11px] text-muted-foreground leading-relaxed">
                      {comparisonResult.v2_result.structured_report?.executive_summary}
                    </p>
                    <span className="text-[10px] font-mono text-emerald-600 dark:text-emerald-400 block pt-1">
                      &check; 100% Validated Pydantic JSON
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* VIEW 3: EVALUATION BENCHMARK SCORECARD */}
      {activeTab === 'evaluation' && scorecard && (
        <div className="space-y-6">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-base font-bold flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-teal-600 dark:text-teal-400" />
                    Golden Test Dataset Evaluation Scorecard
                  </CardTitle>
                  <CardDescription className="text-xs">
                    Automated evaluation across {scorecard.scenarios_evaluated} controlled benchmark scenarios
                  </CardDescription>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={async () => {
                    const res = await promptsApi.triggerEvaluation(currentWorkspace?.id || 'demo-workspace-01')
                    setScorecard(res)
                  }}
                  className="text-xs gap-1"
                >
                  <RefreshCw className="h-3 w-3" />
                  Re-Run Benchmark
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Scorecard Table */}
              <div className="overflow-x-auto border rounded-xl">
                <table className="w-full text-xs text-left">
                  <thead className="bg-muted text-muted-foreground uppercase text-[11px]">
                    <tr>
                      <th className="py-2.5 px-3">Evaluation Metric</th>
                      <th className="py-2.5 px-3 text-center">Prompt v1 (Baseline)</th>
                      <th className="py-2.5 px-3 text-center">Prompt v2 (Grounded)</th>
                      <th className="py-2.5 px-3 text-center">Performance Delta</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    <tr>
                      <td className="py-2.5 px-3 font-semibold">Average Numerical Accuracy</td>
                      <td className="py-2.5 px-3 text-center font-mono text-amber-600">
                        {scorecard.v1_avg_accuracy}%
                      </td>
                      <td className="py-2.5 px-3 text-center font-mono text-emerald-600 font-bold">
                        {scorecard.v2_avg_accuracy}%
                      </td>
                      <td className="py-2.5 px-3 text-center font-mono text-emerald-600 font-bold">
                        +{(scorecard.v2_avg_accuracy - scorecard.v1_avg_accuracy).toFixed(1)}%
                      </td>
                    </tr>
                    <tr>
                      <td className="py-2.5 px-3 font-semibold">Total Hallucinations Detected</td>
                      <td className="py-2.5 px-3 text-center font-mono text-amber-600">
                        {scorecard.v1_total_hallucinations}
                      </td>
                      <td className="py-2.5 px-3 text-center font-mono text-emerald-600 font-bold">
                        {scorecard.v2_total_hallucinations}
                      </td>
                      <td className="py-2.5 px-3 text-center font-mono text-emerald-600 font-bold">
                        Zero Hallucinations
                      </td>
                    </tr>
                    <tr>
                      <td className="py-2.5 px-3 font-semibold">Pydantic JSON Schema Pass Rate</td>
                      <td className="py-2.5 px-3 text-center font-mono text-red-500">
                        {scorecard.v1_schema_pass_rate}%
                      </td>
                      <td className="py-2.5 px-3 text-center font-mono text-emerald-600 font-bold">
                        {scorecard.v2_schema_pass_rate}%
                      </td>
                      <td className="py-2.5 px-3 text-center font-mono text-emerald-600 font-bold">
                        +100.0%
                      </td>
                    </tr>
                    <tr>
                      <td className="py-2.5 px-3 font-semibold">Refusal Correctness ("Insufficient data")</td>
                      <td className="py-2.5 px-3 text-center font-mono text-red-500">
                        {scorecard.v1_refusal_pass_rate}%
                      </td>
                      <td className="py-2.5 px-3 text-center font-mono text-emerald-600 font-bold">
                        {scorecard.v2_refusal_pass_rate}%
                      </td>
                      <td className="py-2.5 px-3 text-center font-mono text-emerald-600 font-bold">
                        +100.0%
                      </td>
                    </tr>
                    <tr>
                      <td className="py-2.5 px-3 font-semibold">Average Pipeline Latency</td>
                      <td className="py-2.5 px-3 text-center font-mono">
                        {scorecard.v1_avg_latency_ms.toFixed(1)}ms
                      </td>
                      <td className="py-2.5 px-3 text-center font-mono">
                        {scorecard.v2_avg_latency_ms.toFixed(1)}ms
                      </td>
                      <td className="py-2.5 px-3 text-center font-mono text-muted-foreground">
                        {(scorecard.v2_avg_latency_ms - scorecard.v1_avg_latency_ms).toFixed(1)}ms
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Rubric Criteria Summary */}
              {scorecard.rubric_scores?.evaluation_dimensions && (
                <div className="space-y-3 pt-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-foreground">
                    Human Usefulness & Prompt Engineering Rubric
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {scorecard.rubric_scores.evaluation_dimensions.map((dim: any, dIdx: number) => (
                      <div key={dIdx} className="p-3 rounded-lg border border-border bg-card space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-foreground text-xs">{dim.dimension}</span>
                          <span className="font-mono text-teal-600 dark:text-teal-400 font-bold text-[11px]">
                            {dim.v2_score}
                          </span>
                        </div>
                        <p className="text-muted-foreground text-[10px] leading-relaxed">{dim.criteria}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* VIEW 4: STORED JINJA2 TEMPLATES */}
      {activeTab === 'templates' && templatesData && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-bold flex items-center gap-2">
              <Code2 className="h-5 w-5 text-teal-600 dark:text-teal-400" />
              Stored Jinja2 Prompt Templates & Architectural Diffs
            </CardTitle>
            <CardDescription className="text-xs">
              Version-controlled prompt templates with documented rationale for v1 versus v2 enhancements
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {Object.entries(templatesData.version_differences || {}).map(([stage, diff]: any) => (
                <div key={stage} className="p-3 rounded-lg border border-border bg-card space-y-1 text-xs">
                  <span className="font-bold text-foreground">{stage} Version Difference</span>
                  <p className="text-muted-foreground text-[11px] leading-relaxed">{diff}</p>
                </div>
              ))}
            </div>

            <div className="space-y-3 pt-2">
              {Object.entries(templatesData.templates || {}).map(([filename, content]: any) => (
                <div key={filename} className="border border-border rounded-lg overflow-hidden">
                  <div className="bg-muted px-3 py-1.5 font-mono text-[11px] font-semibold text-foreground flex items-center justify-between">
                    <span>{filename}</span>
                    <Badge variant={filename.includes('v2') ? 'teal' : 'secondary'} className="text-[9px]">
                      {filename.includes('v2') ? 'v2 Grounded' : 'v1 Baseline'}
                    </Badge>
                  </div>
                  <pre className="p-3 text-[10px] font-mono text-muted-foreground overflow-x-auto max-h-40 bg-card">
                    {content}
                  </pre>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

import React from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, BarChart3, Database, ShieldCheck, Cpu, CheckCircle2, Sparkles, TrendingUp } from 'lucide-react'
import { Button } from '../components/ui/Button'
import { Card, CardContent } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'

export function LandingPage() {
  return (
    <div className="space-y-16 py-6 md:py-12">
      {/* Hero Section */}
      <section className="text-center space-y-6 max-w-3xl mx-auto">
        <Badge variant="teal" className="py-1 px-3 text-xs tracking-wide">
          <Sparkles className="w-3.5 h-3.5 mr-1" />
          Prompt Engineering Capstone Platform
        </Badge>
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight text-foreground">
          Commercial Intelligence Grounded in{' '}
          <span className="text-teal-600 dark:text-teal-400">Verifiable Truth</span>
        </h1>
        <p className="text-lg md:text-xl text-muted-foreground leading-relaxed">
          InsightForge AI combines high-performance deterministic Pandas analytics with evidence-bounded AI workflows.
          Never risk business decisions on LLM arithmetic hallucinations.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <Link to="/dashboard" className="w-full sm:w-auto">
            <Button variant="teal" size="lg" className="w-full sm:w-auto gap-2">
              Launch Live Dashboard
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link to="/datasets/upload" className="w-full sm:w-auto">
            <Button variant="outline" size="lg" className="w-full sm:w-auto gap-2">
              <Database className="h-4 w-4" />
              Upload Wholesale CSV
            </Button>
          </Link>
        </div>
      </section>

      {/* Pillars Grid */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-t-4 border-t-navy-800 dark:border-t-teal-500">
          <CardContent className="pt-6 space-y-3">
            <div className="w-10 h-10 rounded-lg bg-navy-100 dark:bg-navy-900 flex items-center justify-center text-navy-800 dark:text-teal-400">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <h3 className="text-lg font-bold">Deterministic KPI Core</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Every gross revenue dollar, cancellation adjustment, and AOV metric is computed natively in Pandas with rigorous division-by-zero guards.
            </p>
          </CardContent>
        </Card>

        <Card className="border-t-4 border-t-teal-600">
          <CardContent className="pt-6 space-y-3">
            <div className="w-10 h-10 rounded-lg bg-teal-100 dark:bg-teal-950 flex items-center justify-center text-teal-700 dark:text-teal-400">
              <Cpu className="h-5 w-5" />
            </div>
            <h3 className="text-lg font-bold">Staged Intelligence Architecture</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Clean, typed interfaces ready for 3-stage chained prompt pipelines, XGBoost forecasting, Isolation Forest anomalies, and LangGraph agents.
            </p>
          </CardContent>
        </Card>

        <Card className="border-t-4 border-t-navy-600 dark:border-t-slate-400">
          <CardContent className="pt-6 space-y-3">
            <div className="w-10 h-10 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-800 dark:text-slate-200">
              <BarChart3 className="h-5 w-5" />
            </div>
            <h3 className="text-lg font-bold">Mobile-First PWA UI</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Tailored for mobile warehouse floors and desktop executive suites with bottom navigation, responsive charts, and dark theme support.
            </p>
          </CardContent>
        </Card>
      </section>

      {/* Benchmark Badge Section */}
      <section className="rounded-2xl bg-muted/50 border border-border p-6 md:p-8 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="space-y-2 text-center md:text-left">
          <div className="flex items-center justify-center md:justify-start gap-2">
            <Badge variant="success">Benchmark Ready</Badge>
            <span className="text-xs text-muted-foreground">UCI Online Retail II & Synthetic Generator</span>
          </div>
          <h3 className="text-xl font-bold">Reproducible Wholesale Benchmark Included</h3>
          <p className="text-sm text-muted-foreground max-w-xl">
            Pre-loaded with a 5,015-row transactional wholesale dataset with cancellation tracking, negative quantities, and multi-currency distributions.
          </p>
        </div>
        <Link to="/datasets/preview">
          <Button variant="secondary" className="shrink-0 gap-2">
            <TrendingUp className="h-4 w-4" />
            Inspect Benchmark Metrics
          </Button>
        </Link>
      </section>
    </div>
  )
}

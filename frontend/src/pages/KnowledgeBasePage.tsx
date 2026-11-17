import React, { useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  FileText, Upload, Trash2, Search, BookOpen, AlertTriangle,
  CheckCircle, Loader2, FileSearch, ChevronDown, ChevronUp,
  Shield, Info, ExternalLink, Database, Sparkles, Clock
} from 'lucide-react'
import { knowledgeApi } from '../services/api'
import { useWorkspace } from '../context/WorkspaceContext'
import type { KnowledgeDocument, ChunkResult } from '../types'

// ─── helpers ────────────────────────────────────────────────────────────────

function fmtBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

function fmtDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
}

function statusBadge(status: KnowledgeDocument['status']) {
  const map = {
    ready: 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-900/20 dark:text-emerald-400 dark:border-emerald-800',
    processing: 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-900/20 dark:text-amber-400 dark:border-amber-800',
    error: 'bg-red-50 text-red-700 border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800',
  } as const
  const icon = {
    ready: <CheckCircle className="h-3 w-3" />,
    processing: <Loader2 className="h-3 w-3 animate-spin" />,
    error: <AlertTriangle className="h-3 w-3" />,
  }
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded border text-[11px] font-semibold ${map[status]}`}>
      {icon[status]} {status}
    </span>
  )
}

// ─── similarity score bar ───────────────────────────────────────────────────

function SimilarityBar({ score }: { score: number }) {
  const pct = Math.round(score * 100)
  const colour = pct >= 70 ? 'bg-emerald-500' : pct >= 45 ? 'bg-teal-500' : 'bg-amber-400'
  return (
    <div className="flex items-center gap-2 mt-1">
      <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${colour}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-[11px] font-mono text-muted-foreground w-8 text-right">{pct}%</span>
    </div>
  )
}

// ─── chunk card ─────────────────────────────────────────────────────────────

function ChunkCard({ chunk, rank }: { chunk: ChunkResult; rank: number }) {
  const [expanded, setExpanded] = useState(false)
  return (
    <div className="border border-border rounded-lg p-3.5 bg-card hover:border-teal-300 dark:hover:border-teal-700 transition-colors">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <span className="shrink-0 inline-flex items-center justify-center h-5 w-5 rounded-full bg-teal-100 dark:bg-teal-900/40 text-teal-700 dark:text-teal-400 text-[10px] font-bold">
            {rank}
          </span>
          <div className="min-w-0">
            <p className="text-sm font-medium text-foreground truncate">{chunk.document_title}</p>
            <p className="text-[11px] text-muted-foreground">{chunk.source_reference ?? '—'}</p>
          </div>
        </div>
        <button
          onClick={() => setExpanded(v => !v)}
          className="shrink-0 p-1 rounded hover:bg-muted text-muted-foreground"
          aria-label="Toggle excerpt"
        >
          {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </button>
      </div>
      <SimilarityBar score={chunk.similarity_score} />
      {expanded && (
        <blockquote className="mt-3 pl-3 border-l-2 border-teal-400 dark:border-teal-600 text-sm text-muted-foreground leading-relaxed">
          {chunk.chunk_text}
        </blockquote>
      )}
    </div>
  )
}

// ─── main page ──────────────────────────────────────────────────────────────

export function KnowledgeBasePage() {
  const { currentWorkspace } = useWorkspace()
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [uploadTitle, setUploadTitle] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'documents' | 'search' | 'info'>('documents')

  const workspaceId = currentWorkspace?.id ?? 'demo-workspace-01'

  // ── queries ─────────────────────────────────────────────────────────────
  const { data: documents = [], isLoading: docsLoading } = useQuery({
    queryKey: ['knowledge', workspaceId],
    queryFn: () => knowledgeApi.list(workspaceId),
    refetchInterval: (query) => {
      const docs = query.state.data as KnowledgeDocument[] | undefined
      return docs?.some(d => d.status === 'processing') ? 3000 : false
    },
  })

  const { data: searchResult, isPending: searching, mutate: runSearch } = useMutation({
    mutationFn: ({ q, k }: { q: string; k: number }) =>
      knowledgeApi.search(workspaceId, q, k),
  })

  // ── upload mutation ──────────────────────────────────────────────────────
  const uploadMutation = useMutation({
    mutationFn: ({ file, title }: { file: File; title?: string }) =>
      knowledgeApi.upload(workspaceId, file, title),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['knowledge', workspaceId] })
      setUploadTitle('')
      if (fileInputRef.current) fileInputRef.current.value = ''
    },
  })

  // ── delete mutation ──────────────────────────────────────────────────────
  const deleteMutation = useMutation({
    mutationFn: (docId: string) => knowledgeApi.delete(workspaceId, docId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['knowledge', workspaceId] })
      setDeleteConfirm(null)
    },
  })

  // ── handlers ─────────────────────────────────────────────────────────────
  const handleFiles = (files: FileList | null) => {
    if (!files || files.length === 0) return
    const file = files[0]
    uploadMutation.mutate({ file, title: uploadTitle || file.name })
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    handleFiles(e.dataTransfer.files)
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchInput.trim().length < 3) return
    setSearchQuery(searchInput.trim())
    runSearch({ q: searchInput.trim(), k: 5 })
  }

  const readyCount = documents.filter(d => d.status === 'ready').length
  const totalChunks = documents.filter(d => d.status === 'ready').reduce((s, d) => s + d.chunk_count, 0)

  return (
    <div className="max-w-5xl mx-auto px-4 py-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <BookOpen className="h-6 w-6 text-teal-600 dark:text-teal-400" />
            <h1 className="text-2xl font-bold text-foreground">Knowledge Base</h1>
            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-teal-500/15 text-teal-700 dark:text-teal-400 border border-teal-500/20">
              Stage 7
            </span>
          </div>
          <p className="text-sm text-muted-foreground">
            Upload business documents (vendor contracts, shipping SLAs, return policies) to ground AI insights in real evidence.
          </p>
        </div>
        {/* Stats ribbon */}
        <div className="flex gap-3 text-center shrink-0">
          {[
            { label: 'Documents', value: readyCount },
            { label: 'Passages', value: totalChunks.toLocaleString() },
          ].map(s => (
            <div key={s.label} className="px-4 py-2 rounded-lg bg-muted border border-border text-center min-w-[72px]">
              <div className="text-lg font-bold text-foreground">{s.value}</div>
              <div className="text-[11px] text-muted-foreground">{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-muted rounded-lg w-fit">
        {(['documents', 'search', 'info'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors capitalize ${
              activeTab === tab
                ? 'bg-card text-foreground shadow-sm border border-border'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            {tab === 'documents' && <FileText className="inline h-3.5 w-3.5 mr-1.5 -mt-0.5" />}
            {tab === 'search' && <Search className="inline h-3.5 w-3.5 mr-1.5 -mt-0.5" />}
            {tab === 'info' && <Shield className="inline h-3.5 w-3.5 mr-1.5 -mt-0.5" />}
            {tab}
          </button>
        ))}
      </div>

      {/* ── TAB: Documents ────────────────────────────────────────────────── */}
      {activeTab === 'documents' && (
        <div className="space-y-5">
          {/* Upload card */}
          <div className="rounded-xl border border-border bg-card p-5">
            <h2 className="text-base font-semibold text-foreground mb-3 flex items-center gap-2">
              <Upload className="h-4 w-4 text-teal-600" /> Upload Business Document
            </h2>
            <input
              className="w-full mb-3 px-3 py-2 rounded-lg border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/40"
              placeholder="Document title (optional — defaults to filename)"
              value={uploadTitle}
              onChange={e => setUploadTitle(e.target.value)}
            />
            {/* Drop zone */}
            <div
              onDragOver={e => { e.preventDefault(); setDragOver(true) }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`relative flex flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed p-8 cursor-pointer transition-colors ${
                dragOver
                  ? 'border-teal-500 bg-teal-50 dark:bg-teal-900/20'
                  : 'border-border hover:border-teal-400 hover:bg-muted/50'
              }`}
            >
              {uploadMutation.isPending ? (
                <>
                  <Loader2 className="h-8 w-8 text-teal-500 animate-spin" />
                  <p className="text-sm text-muted-foreground">Processing document…</p>
                  <p className="text-xs text-muted-foreground">Extracting text, chunking, and generating embeddings</p>
                </>
              ) : (
                <>
                  <Upload className="h-8 w-8 text-muted-foreground" />
                  <p className="text-sm font-medium text-foreground">Drop PDF or TXT here, or click to browse</p>
                  <p className="text-xs text-muted-foreground">Supported: .pdf .txt · Max 25 MB</p>
                </>
              )}
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.txt"
                className="hidden"
                onChange={e => handleFiles(e.target.files)}
              />
            </div>
            {uploadMutation.isError && (
              <div className="mt-3 flex items-start gap-2 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-sm text-red-700 dark:text-red-400">
                <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
                <span>{String((uploadMutation.error as any)?.response?.data?.detail ?? 'Upload failed')}</span>
              </div>
            )}
            {uploadMutation.isSuccess && (
              <div className="mt-3 flex items-center gap-2 p-3 rounded-lg bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 text-sm text-emerald-700 dark:text-emerald-400">
                <CheckCircle className="h-4 w-4 shrink-0" />
                Document uploaded and indexed — {uploadMutation.data.chunk_count} passages ready.
              </div>
            )}
          </div>

          {/* Document list */}
          <div className="rounded-xl border border-border bg-card overflow-hidden">
            <div className="px-5 py-3 border-b border-border flex items-center justify-between">
              <h2 className="text-base font-semibold text-foreground flex items-center gap-2">
                <Database className="h-4 w-4 text-teal-600" /> Indexed Documents
              </h2>
              <span className="text-xs text-muted-foreground">{documents.length} total</span>
            </div>
            {docsLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-6 w-6 animate-spin text-teal-500" />
              </div>
            ) : documents.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <BookOpen className="h-10 w-10 text-muted-foreground/40 mb-3" />
                <p className="text-sm font-medium text-muted-foreground">No documents yet</p>
                <p className="text-xs text-muted-foreground mt-1">Upload a vendor contract or business policy to get started</p>
              </div>
            ) : (
              <div className="divide-y divide-border">
                {documents.map(doc => (
                  <div key={doc.id} className="px-5 py-3.5 flex items-center gap-3 hover:bg-muted/30 transition-colors group">
                    <div className="shrink-0">
                      <FileText className="h-8 w-8 text-teal-600/70 dark:text-teal-500/70" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-sm font-medium text-foreground truncate max-w-[260px]">{doc.title}</span>
                        {statusBadge(doc.status)}
                        <span className="text-[11px] px-1.5 py-0.5 rounded bg-muted border border-border text-muted-foreground font-mono uppercase">
                          {doc.file_type}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 mt-0.5 text-[11px] text-muted-foreground">
                        <span>{fmtBytes(doc.file_size)}</span>
                        {doc.status === 'ready' && <span>{doc.chunk_count} passages</span>}
                        <span className="flex items-center gap-1"><Clock className="h-3 w-3" />{fmtDate(doc.created_at)}</span>
                      </div>
                      {doc.status === 'error' && doc.error_message && (
                        <p className="text-[11px] text-red-600 dark:text-red-400 mt-0.5 truncate">{doc.error_message}</p>
                      )}
                    </div>
                    {/* Delete */}
                    <div className="shrink-0">
                      {deleteConfirm === doc.id ? (
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-red-600 dark:text-red-400 font-medium">Delete?</span>
                          <button
                            onClick={() => deleteMutation.mutate(doc.id)}
                            disabled={deleteMutation.isPending}
                            className="px-2 py-1 rounded bg-red-500 text-white text-xs font-semibold hover:bg-red-600 disabled:opacity-50"
                          >
                            {deleteMutation.isPending ? '…' : 'Yes'}
                          </button>
                          <button
                            onClick={() => setDeleteConfirm(null)}
                            className="px-2 py-1 rounded bg-muted text-muted-foreground text-xs font-semibold hover:bg-muted/80"
                          >
                            No
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setDeleteConfirm(doc.id)}
                          className="p-1.5 rounded opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20"
                          title="Delete document"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── TAB: Search ───────────────────────────────────────────────────── */}
      {activeTab === 'search' && (
        <div className="space-y-5">
          {readyCount === 0 && (
            <div className="flex items-start gap-3 p-4 rounded-xl bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800">
              <Info className="h-5 w-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
              <p className="text-sm text-amber-700 dark:text-amber-300">
                No indexed documents yet. Upload business documents in the Documents tab first.
              </p>
            </div>
          )}
          {/* Search form */}
          <form onSubmit={handleSearch} className="rounded-xl border border-border bg-card p-5">
            <label className="block text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
              <FileSearch className="h-4 w-4 text-teal-600" /> Search Business Knowledge
            </label>
            <div className="flex gap-2">
              <input
                className="flex-1 px-3 py-2 rounded-lg border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/40"
                placeholder="e.g. payment terms late fee, return policy restocking, delivery SLA"
                value={searchInput}
                onChange={e => setSearchInput(e.target.value)}
                minLength={3}
              />
              <button
                type="submit"
                disabled={searchInput.trim().length < 3 || searching}
                className="px-4 py-2 rounded-lg bg-teal-600 hover:bg-teal-700 text-white text-sm font-semibold disabled:opacity-50 transition-colors flex items-center gap-2"
              >
                {searching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                Search
              </button>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Semantic search over all indexed documents in this workspace using cosine similarity (min. threshold: 0.25).
            </p>
          </form>

          {/* Results */}
          {searchResult && (
            <div className="rounded-xl border border-border bg-card overflow-hidden">
              <div className="px-5 py-3 border-b border-border bg-muted/40">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div>
                    <span className="text-sm font-semibold text-foreground">
                      {searchResult.chunks_found} passage{searchResult.chunks_found !== 1 ? 's' : ''} found
                    </span>
                    <span className="text-muted-foreground text-xs ml-2">for "{searchQuery}"</span>
                  </div>
                  <span className="text-xs text-muted-foreground flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {searchResult.retrieval_latency_ms.toFixed(0)} ms
                  </span>
                </div>
              </div>

              {searchResult.chunks_found === 0 ? (
                <div className="flex flex-col items-center justify-center py-10 text-center">
                  <FileSearch className="h-9 w-9 text-muted-foreground/40 mb-3" />
                  <p className="text-sm font-medium text-muted-foreground">No relevant passages found</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Try a different query or upload more related documents
                  </p>
                </div>
              ) : (
                <div className="p-4 space-y-3">
                  {/* Citation summary */}
                  <div className="flex items-start gap-2 p-3 rounded-lg bg-teal-50 dark:bg-teal-900/20 border border-teal-200 dark:border-teal-800">
                    <Sparkles className="h-4 w-4 text-teal-600 dark:text-teal-400 shrink-0 mt-0.5" />
                    <p className="text-xs text-teal-700 dark:text-teal-300 leading-relaxed">{searchResult.evidence_summary}</p>
                  </div>
                  {searchResult.retrieved_chunks.map((chunk, i) => (
                    <ChunkCard key={chunk.chunk_id} chunk={chunk} rank={i + 1} />
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ── TAB: Info (RAG rules & methodology) ──────────────────────────── */}
      {activeTab === 'info' && (
        <div className="space-y-4">
          <div className="rounded-xl border border-border bg-card p-5 space-y-4">
            <h2 className="text-base font-semibold text-foreground flex items-center gap-2">
              <Shield className="h-4 w-4 text-teal-600" /> RAG Design Rules &amp; Security
            </h2>
            {[
              {
                title: 'Evidence only — no calculations',
                body: 'Retrieved document passages are injected into the AI prompt as contextual evidence. The RAG system never performs financial calculations. All numerical KPIs are computed exclusively by the deterministic Pandas engine.',
              },
              {
                title: 'Prompt injection sanitization',
                body: 'Document content is scanned at ingestion time for known injection patterns (e.g. "IGNORE PREVIOUS INSTRUCTIONS", "You are now…"). Matching lines are replaced with a neutral placeholder before embedding or storage.',
              },
              {
                title: 'Workspace isolation',
                body: 'Every document and chunk is scoped to its workspace_id. The retrieval engine filters exclusively by workspace — it is architecturally impossible to retrieve passages from another workspace.',
              },
              {
                title: 'Citation honesty',
                body: 'Only passages that genuinely exist in the database are returned as citations. The system never fabricates or paraphrases sources. Chunk IDs, document titles, and page references are always preserved.',
              },
              {
                title: '"Insufficient data" policy',
                body: 'When fewer than the minimum similarity threshold (0.25 cosine) chunks are found, the response explicitly states "No relevant business documents found" rather than hallucinating context.',
              },
            ].map(item => (
              <div key={item.title} className="flex gap-3">
                <CheckCircle className="h-4 w-4 text-teal-500 shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-foreground">{item.title}</p>
                  <p className="text-xs text-muted-foreground mt-0.5 leading-relaxed">{item.body}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="rounded-xl border border-border bg-card p-5">
            <h2 className="text-base font-semibold text-foreground mb-3 flex items-center gap-2">
              <Info className="h-4 w-4 text-teal-600" /> Technical Architecture
            </h2>
            <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3 text-sm">
              {[
                ['Embedding Model', 'all-MiniLM-L6-v2 (sentence-transformers, 384-dim)'],
                ['Similarity Metric', 'Cosine similarity with 0.25 minimum threshold'],
                ['Chunking Strategy', 'Sliding-window (400 words, 60-word overlap)'],
                ['PDF Extraction', 'pypdf — page-by-page text extraction'],
                ['Storage', 'JSON embedding arrays in SQLite (dev) / PostgreSQL (prod)'],
                ['Max Document Size', '25 MB per file'],
                ['Supported Formats', '.pdf · .txt'],
                ['Workspace Isolation', 'workspace_id filter on every DB query'],
              ].map(([k, v]) => (
                <div key={k}>
                  <dt className="text-xs text-muted-foreground font-medium">{k}</dt>
                  <dd className="text-sm text-foreground">{v}</dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      )}
    </div>
  )
}

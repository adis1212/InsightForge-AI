import React, { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  UploadCloud,
  FileSpreadsheet,
  CheckCircle2,
  AlertCircle,
  FileCheck,
  ArrowRight,
  Info,
} from 'lucide-react'
import { useWorkspace } from '../context/WorkspaceContext'
import { datasetsApi } from '../services/api'
import { Button } from '../components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { formatBytes } from '../lib/utils'

export function DatasetUploadPage() {
  const { currentWorkspace, setCurrentDataset, refreshDatasets, setDemoMode } = useWorkspace()
  const [file, setFile] = useState<File | null>(null)
  const [datasetName, setDatasetName] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()

  const handleFileSelect = (selectedFile: File) => {
    setError(null)
    setSuccess(null)

    const validExtensions = ['.csv', '.xlsx', '.xls']
    const ext = '.' + selectedFile.name.split('.').pop()?.toLowerCase()

    if (!validExtensions.includes(ext)) {
      setError(`Invalid file format '${ext}'. Please upload CSV or Excel (.xlsx, .xls) files.`)
      return
    }

    if (selectedFile.size > 50 * 1024 * 1024) {
      setError(`File size (${formatBytes(selectedFile.size)}) exceeds the maximum allowed 50 MB.`)
      return
    }

    setFile(selectedFile)
    if (!datasetName) {
      setDatasetName(selectedFile.name.replace(/\.[^/.]+$/, ''))
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0])
    }
  }

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file || !currentWorkspace) return

    setIsUploading(true)
    setError(null)

    try {
      const dataset = await datasetsApi.upload(currentWorkspace.id, file, datasetName)
      setCurrentDataset(dataset)
      setDemoMode(false)
      await refreshDatasets()
      setSuccess(`Dataset '${dataset.name}' successfully parsed and validated!`)
      setTimeout(() => {
        navigate('/datasets/preview')
      }, 1200)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload dataset. Check backend connection.')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
          <UploadCloud className="h-6 w-6 text-teal-600 dark:text-teal-400" />
          Dataset Ingestion Engine
        </h1>
        <p className="text-sm text-muted-foreground mt-0.5">
          Upload commercial transaction logs in CSV or Excel formats for automated schema parsing & KPI indexing
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base font-bold">Upload Wholesale Dataset</CardTitle>
          <CardDescription className="text-xs">
            Supports CSV, XLSX, and XLS formats up to 50 MB
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleUpload} className="space-y-6">
            {error && (
              <div className="p-3 text-xs rounded-lg bg-destructive/10 border border-destructive/20 text-destructive flex items-center gap-2">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {success && (
              <div className="p-3 text-xs rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-700 dark:text-emerald-400 flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 shrink-0" />
                <span>{success}</span>
              </div>
            )}

            {/* Drag & Drop Area */}
            <div
              onDragOver={(e) => {
                e.preventDefault()
                setIsDragging(true)
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                isDragging
                  ? 'border-teal-500 bg-teal-500/5'
                  : 'border-border hover:border-teal-500/50 hover:bg-muted/30'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv,.xlsx,.xls"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    handleFileSelect(e.target.files[0])
                  }
                }}
              />
              <div className="flex flex-col items-center justify-center space-y-3">
                <div className="p-3 rounded-full bg-muted text-muted-foreground">
                  <FileSpreadsheet className="h-8 w-8 text-teal-600 dark:text-teal-400" />
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-semibold text-foreground">
                    {file ? file.name : 'Click to browse or drag and drop your file'}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {file ? `${formatBytes(file.size)} • Ready for ingestion` : 'CSV, XLSX, or XLS (Maximum 50 MB)'}
                  </p>
                </div>
              </div>
            </div>

            {/* Dataset Name Input */}
            <div className="space-y-1">
              <label className="text-xs font-medium text-foreground">Dataset Title</label>
              <input
                type="text"
                placeholder="e.g., Wholesale Transactions FY2023"
                value={datasetName}
                onChange={(e) => setDatasetName(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-lg border border-input bg-background focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>

            {/* Ingestion Info Box */}
            <div className="p-3.5 rounded-xl bg-muted/40 border border-border text-xs space-y-1.5">
              <div className="flex items-center gap-1.5 font-semibold text-foreground">
                <Info className="h-3.5 w-3.5 text-teal-600" />
                <span>Automatic Column Role Identification</span>
              </div>
              <p className="text-muted-foreground text-[11px] leading-relaxed">
                InsightForge automatically detects canonical column roles including Invoice Number, Stock Code, Item Description, Quantity, Unit Price, Customer ID, Date, and Country based on fuzzy pattern matching.
              </p>
            </div>

            <Button
              type="submit"
              variant="teal"
              size="lg"
              className="w-full gap-2"
              disabled={!file}
              isLoading={isUploading}
            >
              <UploadCloud className="h-4 w-4" />
              Process & Ingest Dataset
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

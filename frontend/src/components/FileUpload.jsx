import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileSpreadsheet, FileJson, FileText, File, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { api } from '../utils/api'

const fileIcons = {
  'csv': FileSpreadsheet,
  'xlsx': FileSpreadsheet,
  'json': FileJson,
  'pdf': FileText,
}

const fileColors = {
  'csv': 'text-green-400',
  'xlsx': 'text-green-400',
  'json': 'text-yellow-400',
  'pdf': 'text-red-400',
}

export default function FileUpload({ onUploadComplete, setLoading }) {
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const [uploadResult, setUploadResult] = useState(null)

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0]
    if (!file) return

    setUploading(true)
    setError(null)
    setLoading(true)

    try {
      const result = await api.upload(file)
      setUploadResult(result)
      setLoading(false)
      setTimeout(() => {
        onUploadComplete(result.session_id, {
          file_name: result.file_name,
          file_type: result.file_type,
          summary: result.summary,
        })
      }, 1500)
    } catch (err) {
      setError(err.message)
      setUploading(false)
      setLoading(false)
    }
  }, [onUploadComplete, setLoading])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/json': ['.json'],
      'application/pdf': ['.pdf'],
    },
    maxFiles: 1,
    maxSize: 500 * 1024 * 1024,
    disabled: uploading,
  })

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-white mb-2">Upload Your Dataset</h2>
        <p className="text-gray-400">Drag & drop or click to upload CSV, Excel, JSON, or PDF files</p>
      </div>

      <div className="grid grid-cols-4 gap-4 max-w-2xl mx-auto mb-8">
        {[
          { ext: 'CSV', icon: FileSpreadsheet, color: 'text-green-400' },
          { ext: 'Excel', icon: FileSpreadsheet, color: 'text-green-400' },
          { ext: 'JSON', icon: FileJson, color: 'text-yellow-400' },
          { ext: 'PDF', icon: FileText, color: 'text-red-400' },
        ].map(({ ext, icon: Icon, color }) => (
          <div key={ext} className="card flex flex-col items-center gap-2 py-4">
            <Icon size={28} className={color} />
            <span className="text-sm text-gray-400">{ext}</span>
          </div>
        ))}
      </div>

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
          isDragActive
            ? 'border-blue-500 bg-blue-500/10'
            : 'border-gray-700 hover:border-gray-500 hover:bg-gray-900/50'
        } ${uploading ? 'opacity-50 pointer-events-none' : ''}`}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <div className="flex flex-col items-center gap-3">
            <Loader2 size={40} className="text-blue-400 animate-spin" />
            <p className="text-blue-400 font-medium">Analyzing your dataset...</p>
            <p className="text-gray-500 text-sm">Detecting columns, inferring schema</p>
          </div>
        ) : uploadResult ? (
          <div className="flex flex-col items-center gap-3">
            <CheckCircle size={40} className="text-green-400" />
            <p className="text-green-400 font-medium">Upload successful!</p>
            <p className="text-gray-400 text-sm">{uploadResult.file_name} — {uploadResult.summary.total_rows} rows</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <Upload size={40} className={`${isDragActive ? 'text-blue-400' : 'text-gray-500'}`} />
            <p className={`font-medium ${isDragActive ? 'text-blue-400' : 'text-gray-300'}`}>
              {isDragActive ? 'Drop your file here' : 'Drag & drop your dataset here'}
            </p>
            <p className="text-gray-500 text-sm">or click to browse — CSV, Excel, JSON, PDF (up to 500MB)</p>
          </div>
        )}
      </div>

      {error && (
        <div className="card border-red-800 bg-red-900/20 flex items-center gap-3">
          <AlertCircle size={20} className="text-red-400 shrink-0" />
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      )}

      <div className="card">
        <h3 className="text-sm font-semibold text-gray-300 mb-3">Supported Features Per Format</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs text-gray-400">
          <div><span className="text-green-400">✓</span> CSV — Full support</div>
          <div><span className="text-green-400">✓</span> Excel — Full support</div>
          <div><span className="text-green-400">✓</span> JSON — Structured + API</div>
          <div><span className="text-green-400">✓</span> PDF — Text extraction</div>
        </div>
      </div>
    </div>
  )
}

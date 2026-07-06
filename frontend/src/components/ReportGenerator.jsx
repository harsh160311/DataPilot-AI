import React, { useState } from 'react'
import { api } from '../utils/api'
import { FileText, Download, Loader2, AlertCircle, CheckCircle, AlertTriangle } from 'lucide-react'

export default function ReportGenerator({ sessionId }) {
  const [report, setReport] = useState(null)
  const [textReport, setTextReport] = useState(null)
  const [loading, setLoading] = useState(false)
  const [loadingText, setLoadingText] = useState(false)
  const [error, setError] = useState(null)

  const handleGenerateReport = async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await api.getReport(sessionId)
      setReport(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateText = async () => {
    setLoadingText(true)
    setError(null)
    try {
      const result = await api.getTextReport(sessionId)
      setTextReport(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoadingText(false)
    }
  }

  const handleDownloadText = () => {
    if (!textReport) return
    const blob = new Blob([textReport], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `datapilot-report-${Date.now()}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">AI Report Generation</h2>
          <p className="text-sm text-gray-400 mt-1">Auto-generated summary reports with insights and recommendations</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleGenerateReport}
            disabled={loading}
            className="btn-primary flex items-center gap-2"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : <FileText size={16} />}
            {loading ? 'Generating...' : 'Generate Summary'}
          </button>
          <button
            onClick={handleGenerateText}
            disabled={loadingText}
            className="btn-secondary flex items-center gap-2"
          >
            {loadingText ? <Loader2 size={16} className="animate-spin" /> : <Download size={16} />}
            {loadingText ? 'Generating...' : 'Text Report'}
          </button>
        </div>
      </div>

      {error && (
        <div className="card border-red-800 bg-red-900/20 flex items-center gap-3">
          <AlertCircle size={20} className="text-red-400" />
          <p className="text-red-300">{error}</p>
        </div>
      )}

      {textReport && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="card-header mb-0">Text Report</h3>
            <button onClick={handleDownloadText} className="btn-secondary flex items-center gap-2 text-xs">
              <Download size={14} />
              Download .txt
            </button>
          </div>
          <pre className="text-sm text-gray-300 font-mono whitespace-pre-wrap bg-gray-950 rounded-lg p-4 max-h-[500px] overflow-y-auto">
            {textReport}
          </pre>
        </div>
      )}

      {report && (
        <div className="space-y-4">
          <div className="card">
            <h3 className="card-header">Dataset Quality Score</h3>
            {report.quality_score && (
              <div className="flex items-center gap-6">
                <div className="relative w-24 h-24">
                  <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 36 36">
                    <circle cx="18" cy="18" r="16" fill="none" stroke="#374151" strokeWidth="3" />
                    <circle
                      cx="18" cy="18" r="16" fill="none"
                      stroke={report.quality_score.score >= 80 ? '#22c55e' : report.quality_score.score >= 60 ? '#f59e0b' : '#ef4444'}
                      strokeWidth="3"
                      strokeDasharray={`${report.quality_score.score * 1.005} 100.5`}
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-2xl font-bold text-white">{report.quality_score.score}</span>
                  </div>
                </div>
                <div>
                  <p className="text-lg font-bold">
                    Grade: <span className={
                      report.quality_score.grade === 'A' ? 'text-green-400' :
                      report.quality_score.grade === 'B' ? 'text-blue-400' :
                      report.quality_score.grade === 'C' ? 'text-yellow-400' :
                      'text-red-400'
                    }>{report.quality_score.grade}</span>
                  </p>
                  <p className="text-sm text-gray-400 mt-1">out of 100</p>
                </div>
              </div>
            )}
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {report.dataset_summary && (
              <>
                <div className="card text-center">
                  <p className="text-2xl font-bold text-blue-400">{report.dataset_summary.total_rows?.toLocaleString()}</p>
                  <p className="text-xs text-gray-400 mt-1">Total Rows</p>
                </div>
                <div className="card text-center">
                  <p className="text-2xl font-bold text-green-400">{report.dataset_summary.total_columns}</p>
                  <p className="text-xs text-gray-400 mt-1">Total Columns</p>
                </div>
                <div className="card text-center">
                  <p className="text-2xl font-bold text-yellow-400">{report.dataset_summary.missing_values?.toLocaleString()}</p>
                  <p className="text-xs text-gray-400 mt-1">Missing Values</p>
                </div>
                <div className="card text-center">
                  <p className="text-2xl font-bold text-red-400">{report.dataset_summary.duplicate_rows}</p>
                  <p className="text-xs text-gray-400 mt-1">Duplicates</p>
                </div>
              </>
            )}
          </div>

          {report.top_insights?.length > 0 && (
            <div className="card">
              <h3 className="card-header">Top Insights</h3>
              <div className="space-y-3">
                {report.top_insights.map((insight, idx) => (
                  <div key={idx} className="flex items-start gap-3 p-3 bg-gray-800/50 rounded-lg">
                    <CheckCircle size={16} className="text-blue-400 mt-0.5 shrink-0" />
                    <div>
                      <p className="text-sm font-medium text-gray-200">{insight.title}</p>
                      <p className="text-xs text-gray-400 mt-1">{insight.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {report.critical_alerts?.length > 0 && (
            <div className="card">
              <h3 className="card-header">Alerts</h3>
              <div className="space-y-3">
                {report.critical_alerts.map((alert, idx) => (
                  <div key={idx} className="flex items-start gap-3 p-3 bg-red-900/10 rounded-lg">
                    <AlertTriangle size={16} className="text-red-400 mt-0.5 shrink-0" />
                    <div>
                      <p className="text-sm text-gray-200">{alert.message}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {report.recommendations?.length > 0 && (
            <div className="card">
              <h3 className="card-header">Recommendations</h3>
              <ol className="space-y-2 list-decimal list-inside">
                {report.recommendations.map((rec, idx) => (
                  <li key={idx} className="text-sm text-gray-300">{rec}</li>
                ))}
              </ol>
            </div>
          )}
        </div>
      )}

      {!report && !textReport && !error && (
        <div className="card text-center py-12">
          <FileText size={48} className="text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">Generate a report to see insights, quality scores, and recommendations</p>
          <p className="text-gray-500 text-sm mt-2">Reports include data quality assessment, key findings, and actionable recommendations</p>
        </div>
      )}
    </div>
  )
}

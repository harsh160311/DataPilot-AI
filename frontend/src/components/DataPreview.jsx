import React, { useEffect, useState } from 'react'
import { api } from '../utils/api'
import { Table, Loader2, AlertCircle } from 'lucide-react'

export default function DataPreview({ sessionId, fileInfo }) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    setError(null)
    Promise.all([
      api.getSummary(sessionId),
      api.getColumns(sessionId),
    ])
      .then(([summary, columns]) => setData({ summary, columns }))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [sessionId])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 size={32} className="text-blue-400 animate-spin" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="card border-red-800 bg-red-900/20 flex items-center gap-3">
        <AlertCircle size={20} className="text-red-400" />
        <p className="text-red-300">{error}</p>
      </div>
    )
  }

  if (!data) return null

  const { summary, columns } = data

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card text-center">
          <p className="text-2xl font-bold text-blue-400">{summary.total_rows?.toLocaleString() || 0}</p>
          <p className="text-xs text-gray-400 mt-1">Total Rows</p>
        </div>
        <div className="card text-center">
          <p className="text-2xl font-bold text-green-400">{summary.total_columns || 0}</p>
          <p className="text-xs text-gray-400 mt-1">Total Columns</p>
        </div>
        <div className="card text-center">
          <p className="text-2xl font-bold text-yellow-400">{summary.numeric_columns || 0}</p>
          <p className="text-xs text-gray-400 mt-1">Numeric Columns</p>
        </div>
        <div className="card text-center">
          <p className="text-2xl font-bold text-purple-400">{summary.categorical_columns || 0}</p>
          <p className="text-xs text-gray-400 mt-1">Categorical Columns</p>
        </div>
      </div>

      <div className="card">
        <h3 className="card-header flex items-center gap-2">
          <Table size={18} /> Column Details
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800">
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Column Name</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Data Type</th>
                <th className="text-right py-3 px-4 text-gray-400 font-medium">Non-Null</th>
                <th className="text-right py-3 px-4 text-gray-400 font-medium">Nulls</th>
                <th className="text-right py-3 px-4 text-gray-400 font-medium">Unique</th>
                <th className="text-right py-3 px-4 text-gray-400 font-medium">Null %</th>
              </tr>
            </thead>
            <tbody>
              {columns.columns?.map((col) => (
                <tr key={col.name} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                  <td className="py-3 px-4 text-gray-200 font-medium">{col.name}</td>
                  <td className="py-3 px-4">
                    <span className="badge bg-gray-800 text-gray-300 text-xs">{col.dtype}</span>
                  </td>
                  <td className="py-3 px-4 text-right text-gray-300">{col.nulls !== undefined ? (col.non_null_count || 0).toLocaleString() : '-'}</td>
                  <td className="py-3 px-4 text-right text-gray-300">{col.nulls?.toLocaleString() || '0'}</td>
                  <td className="py-3 px-4 text-right text-gray-300">{col.unique?.toLocaleString() || '0'}</td>
                  <td className="py-3 px-4 text-right">
                    {col.nulls && summary.total_rows
                      ? <span className={col.nulls / summary.total_rows > 0.1 ? 'text-red-400' : 'text-gray-400'}>
                          {((col.nulls / summary.total_rows) * 100).toFixed(1)}%
                        </span>
                      : <span className="text-gray-500">0%</span>
                    }
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {summary.memory_usage && (
        <div className="card text-sm text-gray-400">
          Memory usage: <span className="text-gray-200 font-medium">{summary.memory_usage}</span>
        </div>
      )}
    </div>
  )
}

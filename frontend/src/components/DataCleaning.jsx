import React, { useState } from 'react'
import { api } from '../utils/api'
import { Sparkles, AlertCircle, CheckCircle, Loader2 } from 'lucide-react'

export default function DataCleaning({ sessionId }) {
  const [cleaning, setCleaning] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleClean = async () => {
    setCleaning(true)
    setError(null)
    try {
      const res = await api.cleanData(sessionId)
      setResult(res)
    } catch (err) {
      setError(err.message)
    } finally {
      setCleaning(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Auto Data Cleaning</h2>
          <p className="text-sm text-gray-400 mt-1">Remove duplicates, fill missing values, detect outliers</p>
        </div>
        <button
          onClick={handleClean}
          disabled={cleaning}
          className="btn-primary flex items-center gap-2"
        >
          {cleaning ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Sparkles size={16} />
          )}
          {cleaning ? 'Cleaning...' : 'Run Auto Clean'}
        </button>
      </div>

      {error && (
        <div className="card border-red-800 bg-red-900/20 flex items-center gap-3">
          <AlertCircle size={20} className="text-red-400" />
          <p className="text-red-300">{error}</p>
        </div>
      )}

      {result && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="card text-center border-green-800">
              <CheckCircle size={24} className="text-green-400 mx-auto mb-2" />
              <p className="text-2xl font-bold text-green-400">{result.original_rows?.toLocaleString()}</p>
              <p className="text-xs text-gray-400">Original Rows</p>
            </div>
            <div className="card text-center border-blue-800">
              <CheckCircle size={24} className="text-blue-400 mx-auto mb-2" />
              <p className="text-2xl font-bold text-blue-400">{result.cleaned_rows?.toLocaleString()}</p>
              <p className="text-xs text-gray-400">Cleaned Rows</p>
            </div>
            <div className="card text-center border-yellow-800">
              <AlertCircle size={24} className="text-yellow-400 mx-auto mb-2" />
              <p className="text-2xl font-bold text-yellow-400">{result.duplicates_removed || 0}</p>
              <p className="text-xs text-gray-400">Duplicates Removed</p>
            </div>
            <div className="card text-center border-purple-800">
              <AlertCircle size={24} className="text-purple-400 mx-auto mb-2" />
              <p className="text-2xl font-bold text-purple-400">{result.nulls_filled || 0}</p>
              <p className="text-xs text-gray-400">Nulls Filled</p>
            </div>
          </div>

          <div className="card">
            <h3 className="card-header">Corrections Applied</h3>
            {result.corrections_applied?.length > 0 ? (
              <ul className="space-y-2">
                {result.corrections_applied.map((correction, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                    <CheckCircle size={16} className="text-green-400 mt-0.5 shrink-0" />
                    <span>{correction}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-500">No corrections were needed.</p>
            )}
          </div>
        </div>
      )}

      {!result && !error && (
        <div className="card text-center py-12">
          <Sparkles size={48} className="text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">Click "Run Auto Clean" to automatically clean your dataset</p>
          <p className="text-gray-500 text-sm mt-2">The system will handle missing values, duplicates, and outliers</p>
        </div>
      )}
    </div>
  )
}

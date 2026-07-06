import React, { useEffect, useState } from 'react'
import { api } from '../utils/api'
import { Lightbulb, TrendingUp, TrendingDown, Loader2, AlertCircle, Target, BarChart3 } from 'lucide-react'

const severityIcons = {
  critical: AlertCircle,
  warning: TrendingDown,
  info: Lightbulb,
}

const severityColors = {
  critical: 'border-red-800 bg-red-900/10',
  warning: 'border-yellow-800 bg-yellow-900/10',
  info: 'border-blue-800 bg-blue-900/10',
}

const severityBadge = {
  critical: 'badge-critical',
  warning: 'badge-warning',
  info: 'badge-info',
}

const typeIcons = {
  correlation: BarChart3,
  distribution: TrendingUp,
  outlier: AlertCircle,
  temporal: TrendingUp,
  data_quality: AlertCircle,
  variance: BarChart3,
  dominance: Target,
}

export default function Insights({ sessionId }) {
  const [insights, setInsights] = useState([])
  const [trends, setTrends] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    Promise.all([
      api.getInsights(sessionId),
      api.getTrends(sessionId),
    ])
      .then(([insightsData, trendsData]) => {
        setInsights(insightsData.insights || [])
        setTrends(trendsData.trends || [])
      })
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

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white">Auto-Generated Insights</h2>
        <p className="text-sm text-gray-400 mt-1">AI-discovered patterns, trends, and anomalies in your data</p>
      </div>

      {trends.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {trends.map((trend, idx) => (
            <div key={idx} className={`card border ${trend.direction === 'up' ? 'border-green-800' : 'border-red-800'}`}>
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-400">{trend.column}</p>
                {trend.direction === 'up' ? (
                  <TrendingUp size={18} className="text-green-400" />
                ) : (
                  <TrendingDown size={18} className="text-red-400" />
                )}
              </div>
              <p className={`text-2xl font-bold ${trend.direction === 'up' ? 'text-green-400' : 'text-red-400'}`}>
                {trend.change_percent > 0 ? '+' : ''}{trend.change_percent}%
              </p>
              <p className="text-xs text-gray-500 mt-1">
                From {trend.first_value?.toFixed(2)} to {trend.last_value?.toFixed(2)}
              </p>
            </div>
          ))}
        </div>
      )}

      <div className="space-y-4">
        {insights.length === 0 ? (
          <div className="card text-center py-12">
            <Lightbulb size={48} className="text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">No significant insights detected</p>
            <p className="text-gray-500 text-sm mt-2">Try cleaning your data first to reveal more patterns</p>
          </div>
        ) : (
          insights.map((insight, idx) => {
            const Icon = typeIcons[insight.type] || Lightbulb
            return (
              <div key={idx} className={`card border ${severityColors[insight.severity] || severityColors.info}`}>
                <div className="flex items-start gap-4">
                  <div className="mt-1">
                    <Icon size={20} className="text-blue-400" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="font-semibold text-gray-200">{insight.title}</h3>
                      <span className={`shrink-0 ${severityBadge[insight.severity] || 'badge-info'}`}>
                        {insight.severity}
                      </span>
                    </div>
                    <p className="text-sm text-gray-400 mt-2">{insight.description}</p>
                    {insight.recommendation && (
                      <div className="mt-3 flex items-start gap-2 text-sm">
                        <Target size={14} className="text-blue-400 mt-0.5 shrink-0" />
                        <span className="text-blue-300">{insight.recommendation}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}

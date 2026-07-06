import React, { useEffect, useState } from 'react'
import { api } from '../utils/api'
import { AlertTriangle, TrendingUp, TrendingDown, Link2, Loader2, AlertCircle } from 'lucide-react'

const alertIcons = {
  anomaly: AlertTriangle,
  trend_change: TrendingUp,
  correlation_alert: Link2,
}

const alertSeverity = {
  critical: 'border-red-800 bg-red-900/10',
  warning: 'border-yellow-800 bg-yellow-900/10',
  info: 'border-blue-800 bg-blue-900/10',
}

const alertBadge = {
  critical: 'badge-critical',
  warning: 'badge-warning',
  info: 'badge-info',
}

export default function AlertsPanel({ sessionId }) {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    api.getAlerts(sessionId)
      .then((data) => setAlerts(data.alerts || []))
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
        <h2 className="text-xl font-bold text-white">Real-Time Alerts</h2>
        <p className="text-sm text-gray-400 mt-1">Automatically detected anomalies, spikes, drops, and correlations</p>
      </div>

      {alerts.length === 0 ? (
        <div className="card text-center py-12">
          <AlertTriangle size={48} className="text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No alerts detected</p>
          <p className="text-gray-500 text-sm mt-2">Your data looks clean — no significant anomalies found</p>
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert, idx) => {
            const Icon = alertIcons[alert.type] || AlertTriangle
            return (
              <div key={idx} className={`card border ${alertSeverity[alert.severity] || alertSeverity.info}`}>
                <div className="flex items-start gap-4">
                  <div className={`mt-1 ${alert.severity === 'critical' ? 'text-red-400' : alert.severity === 'warning' ? 'text-yellow-400' : 'text-blue-400'}`}>
                    <Icon size={20} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="font-semibold text-gray-200">{alert.message}</h3>
                      <span className={`shrink-0 ${alertBadge[alert.severity] || 'badge-info'}`}>
                        {alert.severity}
                      </span>
                    </div>
                    <div className="flex gap-4 mt-2 text-xs text-gray-400">
                      {alert.column && <span>Column: <span className="text-gray-300">{alert.column}</span></span>}
                      {alert.value !== undefined && <span>Value: <span className="text-gray-300">{typeof alert.value === 'number' ? alert.value.toFixed(2) : alert.value}</span></span>}
                      {alert.threshold !== undefined && <span>Threshold: <span className="text-gray-300">{typeof alert.threshold === 'number' ? alert.threshold.toFixed(2) : alert.threshold}</span></span>}
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

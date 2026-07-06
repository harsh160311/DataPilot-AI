import React, { useEffect, useState } from 'react'
import { api } from '../utils/api'
import { Loader2, AlertCircle, TrendingUp, TrendingDown } from 'lucide-react'
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  ScatterChart, Scatter,
} from 'recharts'

const COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316']

export default function Dashboard({ sessionId }) {
  const [dashboard, setDashboard] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    api.getDashboard(sessionId)
      .then(setDashboard)
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

  if (!dashboard) return null

  const renderChart = (chart, idx) => {
    if (!chart.data || (Array.isArray(chart.data) && chart.data.length === 0) || (chart.data.values && chart.data.values.length === 0)) {
      return null
    }

    switch (chart.type) {
      case 'line':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={Array.isArray(chart.data) ? chart.data : []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey={Object.keys(Array.isArray(chart.data) && chart.data.length > 0 ? chart.data[0] : {})[0]} stroke="#6b7280" tick={{ fontSize: 12 }} />
              <YAxis stroke="#6b7280" tick={{ fontSize: 12 }} />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', color: '#e5e7eb' }} />
              {chart.series ? (
                chart.series.map((s, i) => (
                  <Line key={s} type="monotone" dataKey={s} stroke={COLORS[i % COLORS.length]} strokeWidth={2} dot={false} />
                ))
              ) : (
                <Line type="monotone" dataKey={Object.keys(Array.isArray(chart.data) && chart.data.length > 0 ? chart.data[0] : {})[1]} stroke="#3b82f6" strokeWidth={2} dot={false} />
              )}
            </LineChart>
          </ResponsiveContainer>
        )

      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={Array.isArray(chart.data) ? chart.data : []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey={Object.keys(Array.isArray(chart.data) && chart.data.length > 0 ? chart.data[0] : {})[0]} stroke="#6b7280" tick={{ fontSize: 12 }} />
              <YAxis stroke="#6b7280" tick={{ fontSize: 12 }} />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', color: '#e5e7eb' }} />
              <Bar dataKey={Object.keys(Array.isArray(chart.data) && chart.data.length > 0 ? chart.data[0] : {})[1]} fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )

      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={Array.isArray(chart.data) ? chart.data : []}
                dataKey="value"
                nameKey="label"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={({ label, percent }) => `${label} (${(percent * 100).toFixed(0)}%)`}
              >
                {(Array.isArray(chart.data) ? chart.data : []).map((_, idx) => (
                  <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', color: '#e5e7eb' }} />
            </PieChart>
          </ResponsiveContainer>
        )

      case 'scatter':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey={Object.keys(Array.isArray(chart.data) && chart.data.length > 0 ? chart.data[0] : {})[0]} stroke="#6b7280" />
              <YAxis dataKey={Object.keys(Array.isArray(chart.data) && chart.data.length > 0 ? chart.data[0] : {})[1]} stroke="#6b7280" />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', color: '#e5e7eb' }} />
              <Scatter data={Array.isArray(chart.data) ? chart.data : []} fill="#3b82f6" />
            </ScatterChart>
          </ResponsiveContainer>
        )

      case 'histogram':
        return (
          <div className="flex items-center justify-center h-[300px] text-gray-500">
            <p>Histogram: {chart.title}</p>
          </div>
        )

      default:
        return (
          <div className="flex items-center justify-center h-[300px] text-gray-500">
            <p>Chart type: {chart.type}</p>
          </div>
        )
    }
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {dashboard.kpis?.map((kpi, idx) => (
          <div key={idx} className="card">
            <p className="text-xs text-gray-400 mb-1">{kpi.label}</p>
            <p className="text-2xl font-bold text-white">
              {typeof kpi.value === 'number' ? kpi.value.toLocaleString() : kpi.value}
            </p>
            {kpi.change && kpi.change !== 0 && (
              <div className={`flex items-center gap-1 text-xs mt-1 ${kpi.change > 0 ? 'text-green-400' : 'text-red-400'}`}>
                {kpi.change > 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                <span>{Math.abs(kpi.change).toFixed(1)}%</span>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {dashboard.charts?.map((chart, idx) => (
          <div key={idx} className="card">
            <h3 className="text-sm font-semibold text-gray-300 mb-4">{chart.title}</h3>
            {renderChart(chart, idx)}
          </div>
        ))}
      </div>
    </div>
  )
}

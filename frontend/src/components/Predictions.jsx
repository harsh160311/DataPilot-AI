import React, { useState, useEffect } from 'react'
import { api } from '../utils/api'
import { Brain, Loader2, AlertCircle, TrendingUp, ArrowRight } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function Predictions({ sessionId }) {
  const [target, setTarget] = useState('')
  const [periods, setPeriods] = useState(5)
  const [training, setTraining] = useState(false)
  const [predicting, setPredicting] = useState(false)
  const [trainResult, setTrainResult] = useState(null)
  const [forecast, setForecast] = useState(null)
  const [error, setError] = useState(null)
  const [columns, setColumns] = useState([])

  const handleTrain = async () => {
    if (!target) return
    setTraining(true)
    setError(null)
    try {
      const result = await api.trainModel(sessionId, target)
      setTrainResult(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setTraining(false)
    }
  }

  const handleForecast = async () => {
    if (!target) return
    setPredicting(true)
    setError(null)
    try {
      const result = await api.forecast(sessionId, target, periods)
      setForecast(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setPredicting(false)
    }
  }

  const loadColumns = async () => {
    try {
      const cols = await api.getColumns(sessionId)
      setColumns(cols.columns?.filter((c) => c.dtype.includes('int') || c.dtype.includes('float')) || [])
    } catch (err) {
      setColumns([])
    }
  }

  useEffect(() => { loadColumns() }, [])

  const chartData = forecast?.forecasts?.map((f) => ({
    period: `Period ${f.period}`,
    value: f.predicted_value,
  })) || []

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white">Prediction Engine</h2>
        <p className="text-sm text-gray-400 mt-1">Train ML models and forecast future trends</p>
      </div>

      <div className="card">
        <h3 className="card-header">Select Target Column</h3>
        <div className="flex gap-3">
          <select
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            className="input-field flex-1"
          >
            <option value="">Choose a numeric column to predict...</option>
            {columns.map((col) => (
              <option key={col.name} value={col.name}>{col.name}</option>
            ))}
          </select>
          <input
            type="number"
            value={periods}
            onChange={(e) => setPeriods(Math.max(1, Math.min(30, parseInt(e.target.value) || 1)))}
            className="input-field w-24 text-center"
            min="1"
            max="30"
            title="Forecast periods"
          />
        </div>
        <div className="flex gap-3 mt-4">
          <button
            onClick={handleTrain}
            disabled={!target || training}
            className="btn-primary flex items-center gap-2"
          >
            {training ? <Loader2 size={16} className="animate-spin" /> : <Brain size={16} />}
            {training ? 'Training...' : 'Train Model'}
          </button>
          <button
            onClick={handleForecast}
            disabled={!target || predicting}
            className="btn-secondary flex items-center gap-2"
          >
            {predicting ? <Loader2 size={16} className="animate-spin" /> : <TrendingUp size={16} />}
            {predicting ? 'Predicting...' : 'Generate Forecast'}
          </button>
        </div>
      </div>

      {error && (
        <div className="card border-red-800 bg-red-900/20 flex items-center gap-3">
          <AlertCircle size={20} className="text-red-400" />
          <p className="text-red-300">{error}</p>
        </div>
      )}

      {trainResult && !trainResult.error && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {trainResult.metrics?.type === 'regression' ? (
            <>
              <div className="card text-center">
                <p className="text-xs text-gray-400 mb-1">R² Score</p>
                <p className="text-2xl font-bold text-blue-400">{trainResult.metrics.r2?.toFixed(3)}</p>
              </div>
              <div className="card text-center">
                <p className="text-xs text-gray-400 mb-1">MAE</p>
                <p className="text-2xl font-bold text-green-400">{trainResult.metrics.mae?.toFixed(2)}</p>
              </div>
              <div className="card text-center">
                <p className="text-xs text-gray-400 mb-1">RMSE</p>
                <p className="text-2xl font-bold text-yellow-400">{trainResult.metrics.rmse?.toFixed(2)}</p>
              </div>
              <div className="card text-center">
                <p className="text-xs text-gray-400 mb-1">Training Samples</p>
                <p className="text-2xl font-bold text-purple-400">{trainResult.training_samples}</p>
              </div>
            </>
          ) : trainResult.metrics?.type === 'classification' ? (
            <div className="card text-center col-span-2">
              <p className="text-xs text-gray-400 mb-1">Accuracy</p>
              <p className="text-2xl font-bold text-blue-400">{(trainResult.metrics.accuracy * 100).toFixed(1)}%</p>
            </div>
          ) : null}

          {trainResult.feature_importance?.length > 0 && (
            <div className="card col-span-full">
              <h3 className="card-header">Feature Importance</h3>
              <div className="space-y-2">
                {trainResult.feature_importance.slice(0, 10).map((feat, idx) => (
                  <div key={idx} className="flex items-center gap-3">
                    <span className="text-sm text-gray-300 w-40 truncate">{feat.feature}</span>
                    <div className="flex-1 bg-gray-800 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full"
                        style={{ width: `${feat.importance * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-400 w-12 text-right">
                      {(feat.importance * 100).toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {forecast && forecast.forecasts?.length > 0 && (
        <div className="card">
          <h3 className="card-header flex items-center gap-2">
            <TrendingUp size={18} className="text-blue-400" />
            Forecast: {forecast.target}
          </h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="period" stroke="#6b7280" />
                <YAxis stroke="#6b7280" />
                <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', color: '#e5e7eb' }} />
                <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} dot={{ fill: '#3b82f6' }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-5 gap-2 mt-4">
            {forecast.forecasts.map((f, idx) => (
              <div key={idx} className="text-center p-2 bg-gray-800 rounded-lg">
                <p className="text-xs text-gray-400">Period {f.period}</p>
                <p className="text-sm font-bold text-blue-400">{f.predicted_value?.toFixed(2)}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

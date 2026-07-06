import React, { useEffect, useState } from 'react'
import { api } from '../utils/api'
import { Trophy, Medal, Loader2, AlertCircle, TrendingUp, TrendingDown } from 'lucide-react'

const rankMedals = {
  1: 'text-yellow-400',
  2: 'text-gray-300',
  3: 'text-amber-600',
}

export default function Rankings({ sessionId }) {
  const [rankings, setRankings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    api.getRankings(sessionId)
      .then((data) => setRankings(data.rankings || []))
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

  if (rankings.length === 0) {
    return (
      <div className="card text-center py-12">
        <Trophy size={48} className="text-gray-600 mx-auto mb-4" />
        <p className="text-gray-400">No rankings available</p>
        <p className="text-gray-500 text-sm mt-2">Upload data with categorical and numeric columns to see rankings</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white">Rankings</h2>
        <p className="text-sm text-gray-400 mt-1">Top performers, contributors, and categories ranked by key metrics</p>
      </div>

      {rankings.map((ranking, idx) => (
        <div key={idx} className="card">
          <h3 className="card-header">
            {ranking.metric} by {ranking.category}
          </h3>
          <div className="space-y-2">
            {ranking.rankings?.map((item, i) => (
              <div
                key={i}
                className="flex items-center gap-4 p-3 rounded-lg hover:bg-gray-800/50 transition-colors"
              >
                <div className="w-8 text-center">
                  {i < 3 ? (
                    <Medal size={20} className={rankMedals[i + 1] || 'text-gray-500'} />
                  ) : (
                    <span className="text-sm text-gray-500">#{item.rank}</span>
                  )}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-200">{item.label}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold text-blue-400">
                    {item.value?.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                  </p>
                  {item.change !== undefined && item.change !== null && (
                    <div className={`flex items-center gap-1 text-xs ${item.change > 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {item.change > 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                      <span>{Math.abs(item.change).toFixed(1)}%</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

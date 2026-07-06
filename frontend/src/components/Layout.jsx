import React from 'react'
import { Database, Trash2, Cpu } from 'lucide-react'

export default function Layout({ tabs, activeTab, onTabChange, sessionId, fileInfo, onReset, children }) {
  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      <header className="bg-gray-900 border-b border-gray-800 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Database size={20} className="text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">DataPilot AI</h1>
              <p className="text-xs text-gray-400">Data Intelligence Platform</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <Cpu size={14} />
              <span>GPU-Accelerated</span>
            </div>

            {sessionId && (
              <div className="flex items-center gap-3">
                <div className="text-xs text-gray-400">
                  <span className="text-green-400">●</span> {fileInfo?.file_name || 'Active'}
                </div>
                <button
                  onClick={onReset}
                  className="flex items-center gap-1.5 text-xs text-red-400 hover:text-red-300 transition-colors"
                >
                  <Trash2 size={14} />
                  <span>Clear & Upload New</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      <nav className="bg-gray-900/50 border-b border-gray-800 px-6">
        <div className="max-w-7xl mx-auto flex gap-1 overflow-x-auto py-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => !tab.disabled && onTabChange(tab.id)}
              disabled={tab.disabled}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white'
                  : tab.disabled
                  ? 'text-gray-600 cursor-not-allowed'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </nav>

      <main className="flex-1 px-6 py-6">
        <div className="max-w-7xl mx-auto">
          {children}
        </div>
      </main>

      <footer className="bg-gray-900 border-t border-gray-800 px-6 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between text-xs text-gray-500">
          <span>DataPilot AI v1.0.0</span>
          <span>Zero Data Storage | Privacy-First | GPU-Accelerated</span>
          <span>Powered by AI & NVIDIA RAPIDS</span>
        </div>
      </footer>
    </div>
  )
}

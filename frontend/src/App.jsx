import React, { useState } from 'react'
import Layout from './components/Layout'
import FileUpload from './components/FileUpload'
import DataPreview from './components/DataPreview'
import DataCleaning from './components/DataCleaning'
import Dashboard from './components/Dashboard'
import Insights from './components/Insights'
import Predictions from './components/Predictions'
import ChatAssistant from './components/ChatAssistant'
import AlertsPanel from './components/AlertsPanel'
import Rankings from './components/Rankings'
import ReportGenerator from './components/ReportGenerator'

export default function App() {
  const [sessionId, setSessionId] = useState(null)
  const [activeTab, setActiveTab] = useState('upload')
  const [fileInfo, setFileInfo] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleUploadComplete = (id, info) => {
    setSessionId(id)
    setFileInfo(info)
    setActiveTab('preview')
  }

  const handleReset = () => {
    setSessionId(null)
    setFileInfo(null)
    setActiveTab('upload')
  }

  const tabs = [
    { id: 'upload', label: 'Upload', icon: '📤', disabled: false },
    { id: 'preview', label: 'Preview', icon: '👁️', disabled: !sessionId },
    { id: 'cleaning', label: 'Cleaning', icon: '🧹', disabled: !sessionId },
    { id: 'dashboard', label: 'Dashboard', icon: '📊', disabled: !sessionId },
    { id: 'insights', label: 'Insights', icon: '🧠', disabled: !sessionId },
    { id: 'predictions', label: 'Predictions', icon: '🔮', disabled: !sessionId },
    { id: 'chat', label: 'AI Chat', icon: '💬', disabled: !sessionId },
    { id: 'alerts', label: 'Alerts', icon: '⚠️', disabled: !sessionId },
    { id: 'rankings', label: 'Rankings', icon: '🏆', disabled: !sessionId },
    { id: 'reports', label: 'Reports', icon: '📋', disabled: !sessionId },
  ]

  return (
    <Layout
      tabs={tabs}
      activeTab={activeTab}
      onTabChange={setActiveTab}
      sessionId={sessionId}
      fileInfo={fileInfo}
      onReset={handleReset}
    >
      {loading && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-900 rounded-xl p-8 flex flex-col items-center gap-4">
            <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-gray-400">Processing...</p>
          </div>
        </div>
      )}

      {activeTab === 'upload' && (
        <FileUpload onUploadComplete={handleUploadComplete} setLoading={setLoading} />
      )}
      {activeTab === 'preview' && sessionId && (
        <DataPreview sessionId={sessionId} fileInfo={fileInfo} />
      )}
      {activeTab === 'cleaning' && sessionId && (
        <DataCleaning sessionId={sessionId} />
      )}
      {activeTab === 'dashboard' && sessionId && (
        <Dashboard sessionId={sessionId} />
      )}
      {activeTab === 'insights' && sessionId && (
        <Insights sessionId={sessionId} />
      )}
      {activeTab === 'predictions' && sessionId && (
        <Predictions sessionId={sessionId} />
      )}
      {activeTab === 'chat' && sessionId && (
        <ChatAssistant sessionId={sessionId} />
      )}
      {activeTab === 'alerts' && sessionId && (
        <AlertsPanel sessionId={sessionId} />
      )}
      {activeTab === 'rankings' && sessionId && (
        <Rankings sessionId={sessionId} />
      )}
      {activeTab === 'reports' && sessionId && (
        <ReportGenerator sessionId={sessionId} />
      )}
    </Layout>
  )
}

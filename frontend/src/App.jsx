import { useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import QueryPanel from './components/QueryPanel';
import ResultsPanel from './components/ResultsPanel';
import FeedbackPanel from './components/FeedbackPanel';
import RiskHeatmap from './components/RiskHeatmap';
import { Database, Upload, BookOpen } from 'lucide-react';

function App() {
  const [activeView, setActiveView] = useState('query');
  const [queryResult, setQueryResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const renderView = () => {
    switch (activeView) {
      case 'query':
        return (
          <div className="page-container">
            <QueryPanel
              onResult={(result) => setQueryResult(result)}
              onLoading={setIsLoading}
            />
            {queryResult && (
              <>
                <FeedbackPanel sessionId={queryResult.session_id} />
                <ResultsPanel result={queryResult} />
              </>
            )}
          </div>
        );

      case 'analytics':
        return (
          <div className="page-container">
            <RiskHeatmap />
          </div>
        );

      case 'knowledge':
        return (
          <div className="page-container">
            <div className="card">
              <div className="card-header">
                <div className="card-title">
                  <Database size={18} />
                  Knowledge Base Overview
                </div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                  gap: 16
                }}>
                  <div className="stat-card">
                    <div className="stat-card-icon purple"><Database size={24} /></div>
                    <div className="stat-card-info">
                      <span className="stat-card-value">Qdrant</span>
                      <span className="stat-card-label">Vector Database</span>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-card-icon cyan"><Upload size={24} /></div>
                    <div className="stat-card-info">
                      <span className="stat-card-value">Hybrid</span>
                      <span className="stat-card-label">Semantic + Metadata Search</span>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-card-icon emerald"><BookOpen size={24} /></div>
                    <div className="stat-card-info">
                      <span className="stat-card-value">384D</span>
                      <span className="stat-card-label">Embedding Dimension</span>
                    </div>
                  </div>
                </div>

                <div className="recommendation-box" style={{ borderColor: 'var(--border-subtle)' }}>
                  <strong>How the Knowledge Base Works:</strong>{'\n\n'}
                  <strong>1. Data Ingestion (Step 1):</strong> Defect records are embedded using all-MiniLM-L6-v2 and stored in Qdrant with structured metadata (severity, module, root cause, version).{'\n\n'}
                  <strong>2. Hybrid Search:</strong> Queries combine semantic similarity (vector search) with metadata filters (module, severity) for precise retrieval.{'\n\n'}
                  <strong>3. Pattern Recognition (Step 2):</strong> The LLM analyzes retrieved defects to identify commonalities and trends.{'\n\n'}
                  <strong>4. Self-Learning (Step 3):</strong> When you rate a recommendation as "incorrect" and provide a correction, that knowledge is saved back as a High-Confidence Reference point — the system learns from your feedback.{'\n\n'}
                  <strong>5. Predictive Guidance (Step 4):</strong> When code changes are provided, the system predicts high-risk modules and generates BDD Gherkin scenarios for mitigation.
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="app-layout">
      <Sidebar activeView={activeView} onNavigate={setActiveView} />
      <Header activeView={activeView} />
      <main className="main-content">
        {renderView()}
      </main>
    </div>
  );
}

export default App;

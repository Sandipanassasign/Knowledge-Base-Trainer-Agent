import { History, Lightbulb, Target, BookOpen } from 'lucide-react';

export default function ResultsPanel({ result }) {
    if (!result) return null;

    const { historical_matches, patterns, recommendation, predictive_risks } = result;

    return (
        <div className="results-panel">
            {/* Historical Matches */}
            <div className="card" style={{ marginBottom: 24 }}>
                <div className="card-header">
                    <div className="card-title">
                        <History size={18} />
                        Historical Matches ({historical_matches?.length || 0})
                    </div>
                </div>
                <div className="match-list">
                    {historical_matches?.length > 0 ? (
                        historical_matches.map((match, i) => (
                            <div className="match-item" key={i}>
                                <div className="match-item-header">
                                    <span className="match-item-title">{match.title}</span>
                                    <span
                                        className="match-item-score"
                                        style={{
                                            background: match.similarity_score > 0.7
                                                ? 'rgba(16,185,129,0.15)' : 'rgba(234,179,8,0.15)',
                                            color: match.similarity_score > 0.7
                                                ? 'var(--accent-emerald)' : 'var(--severity-medium)',
                                        }}
                                    >
                                        {(match.similarity_score * 100).toFixed(0)}% match
                                    </span>
                                </div>
                                <div className="match-item-body">{match.description}</div>
                                {match.resolution && (
                                    <div className="match-item-body" style={{ color: 'var(--accent-emerald)', fontSize: 12 }}>
                                        ✅ Resolution: {match.resolution}
                                    </div>
                                )}
                                <div className="match-item-meta">
                                    <span className={`meta-tag severity-${match.severity}`}>{match.severity}</span>
                                    <span className="meta-tag module">{match.module_id}</span>
                                    <span className="meta-tag root-cause">{match.root_cause_category}</span>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="empty-state">
                            <BookOpen size={36} />
                            <div className="empty-state-title">No matches found</div>
                            <div className="empty-state-desc">
                                Try seeding the database with sample data first.
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Patterns */}
            {patterns?.length > 0 && (
                <div className="card" style={{ marginBottom: 24 }}>
                    <div className="card-header">
                        <div className="card-title">
                            <Lightbulb size={18} />
                            Identified Patterns
                        </div>
                    </div>
                    <div className="pattern-list">
                        {patterns.map((pattern, i) => (
                            <div className="pattern-item" key={i}>
                                <div className="pattern-item-bullet" />
                                <span>{pattern}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Recommendation */}
            {recommendation && (
                <div className="card" style={{ marginBottom: 24 }}>
                    <div className="card-header">
                        <div className="card-title">
                            <Target size={18} />
                            Strategic Recommendation
                        </div>
                    </div>
                    <div className="recommendation-box">{recommendation}</div>
                </div>
            )}

            {/* Predictive Risks / BDD Scenarios */}
            {predictive_risks?.length > 0 && (
                <div className="card" style={{ marginBottom: 24 }}>
                    <div className="card-header">
                        <div className="card-title">
                            <Target size={18} style={{ color: 'var(--accent-rose)' }} />
                            Predictive Risk Analysis & BDD Scenarios
                        </div>
                    </div>
                    {predictive_risks.map((risk, i) => (
                        <div className="bdd-scenario" key={i}>
                            <div className="bdd-scenario-header">
                                <span className="bdd-scenario-module">{risk.module}</span>
                                <span
                                    className="bdd-scenario-risk"
                                    style={{
                                        background: risk.risk_score > 0.7
                                            ? 'rgba(239,68,68,0.15)' : risk.risk_score > 0.4
                                                ? 'rgba(234,179,8,0.15)' : 'rgba(34,197,94,0.15)',
                                        color: risk.risk_score > 0.7
                                            ? 'var(--severity-critical)' : risk.risk_score > 0.4
                                                ? 'var(--severity-medium)' : 'var(--severity-low)',
                                    }}
                                >
                                    Risk: {(risk.risk_score * 100).toFixed(0)}%
                                </span>
                            </div>
                            <div className="match-item-body">{risk.reason}</div>
                            {risk.suggested_bdd_scenario && (
                                <pre>{risk.suggested_bdd_scenario}</pre>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

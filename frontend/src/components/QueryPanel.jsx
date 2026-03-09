import { useState } from 'react';
import { Search, Send, Code, Filter } from 'lucide-react';
import { queryAgent } from '../api/client';

export default function QueryPanel({ onResult, onLoading }) {
    const [query, setQuery] = useState('');
    const [moduleFilter, setModuleFilter] = useState('');
    const [severityFilter, setSeverityFilter] = useState('');
    const [codeChanges, setCodeChanges] = useState('');
    const [showAdvanced, setShowAdvanced] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        setError('');
        onLoading?.(true);

        try {
            const result = await queryAgent({
                query: query.trim(),
                moduleFilter: moduleFilter || null,
                severityFilter: severityFilter || null,
                codeChanges: codeChanges || null,
            });
            onResult?.(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
            onLoading?.(false);
        }
    };

    return (
        <div className="card query-panel">
            <div className="card-header">
                <div className="card-title">
                    <Search size={18} />
                    Ask the DKI Agent
                </div>
                <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => setShowAdvanced(!showAdvanced)}
                >
                    <Filter size={14} />
                    {showAdvanced ? 'Hide Filters' : 'Filters & Code'}
                </button>
            </div>

            <form className="query-form" onSubmit={handleSubmit}>
                <div className="input-group">
                    <label className="input-label">Your Testing Problem</label>
                    <textarea
                        className="textarea"
                        placeholder="e.g., We're seeing intermittent failures in the login flow after deploying the new session handler. What should we focus testing on?"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        rows={3}
                    />
                </div>

                {showAdvanced && (
                    <>
                        <div className="query-filters">
                            <div className="input-group">
                                <label className="input-label">Module Filter</label>
                                <select
                                    className="select"
                                    value={moduleFilter}
                                    onChange={(e) => setModuleFilter(e.target.value)}
                                >
                                    <option value="">All Modules</option>
                                    <option value="authentication">Authentication</option>
                                    <option value="payment">Payment</option>
                                    <option value="search">Search</option>
                                    <option value="cart">Cart</option>
                                    <option value="database">Database</option>
                                    <option value="notifications">Notifications</option>
                                    <option value="user_profile">User Profile</option>
                                    <option value="api_gateway">API Gateway</option>
                                    <option value="real_time">Real Time</option>
                                    <option value="reporting">Reporting</option>
                                    <option value="inventory">Inventory</option>
                                    <option value="dashboard">Dashboard</option>
                                    <option value="file_service">File Service</option>
                                </select>
                            </div>
                            <div className="input-group">
                                <label className="input-label">Severity Filter</label>
                                <select
                                    className="select"
                                    value={severityFilter}
                                    onChange={(e) => setSeverityFilter(e.target.value)}
                                >
                                    <option value="">All Severities</option>
                                    <option value="critical">Critical</option>
                                    <option value="high">High</option>
                                    <option value="medium">Medium</option>
                                    <option value="low">Low</option>
                                </select>
                            </div>
                        </div>

                        <div className="input-group">
                            <label className="input-label">
                                <Code size={14} style={{ verticalAlign: 'middle', marginRight: 6 }} />
                                Current Code Changes (for Predictive Analysis)
                            </label>
                            <textarea
                                className="textarea"
                                placeholder="Paste a summary of your current code changes for the agent to predict high-risk modules and generate BDD scenarios..."
                                value={codeChanges}
                                onChange={(e) => setCodeChanges(e.target.value)}
                                rows={4}
                            />
                        </div>
                    </>
                )}

                {error && (
                    <div
                        className="feedback-message"
                        style={{ background: 'rgba(244,63,94,0.1)', borderColor: 'rgba(244,63,94,0.3)', color: 'var(--accent-rose)' }}
                    >
                        {error}
                    </div>
                )}

                <div className="query-actions">
                    <button className="btn btn-primary" type="submit" disabled={loading || !query.trim()}>
                        {loading ? (
                            <>
                                <div className="loading-spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
                                Analyzing…
                            </>
                        ) : (
                            <>
                                <Send size={16} />
                                Query Agent
                            </>
                        )}
                    </button>
                </div>
            </form>
        </div>
    );
}

import { useState, useEffect } from 'react';
import {
    BarChart3,
    Bug,
    ShieldAlert,
    MessageSquareDot,
    TrendingUp,
    AlertTriangle,
} from 'lucide-react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    Legend,
} from 'recharts';
import { getAnalytics } from '../api/client';

const SEVERITY_COLORS = {
    critical: '#ef4444',
    high: '#f97316',
    medium: '#eab308',
    low: '#22c55e',
};

const getRiskClass = (score) => {
    if (score >= 0.7) return 'risk-extreme';
    if (score >= 0.45) return 'risk-high';
    if (score >= 0.2) return 'risk-medium';
    return 'risk-low';
};

export default function RiskHeatmap() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        loadAnalytics();
    }, []);

    const loadAnalytics = async () => {
        setLoading(true);
        setError('');
        try {
            const res = await getAnalytics();
            setData(res);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="loading-state">
                <div className="loading-spinner" />
                <div className="loading-text">Loading analytics…</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="card">
                <div className="empty-state">
                    <AlertTriangle size={36} />
                    <div className="empty-state-title">Error loading analytics</div>
                    <div className="empty-state-desc">{error}</div>
                    <button className="btn btn-primary btn-sm" onClick={loadAnalytics}>Retry</button>
                </div>
            </div>
        );
    }

    if (!data || data.total_defects === 0) {
        return (
            <div className="card">
                <div className="empty-state">
                    <BarChart3 size={48} />
                    <div className="empty-state-title">No data available</div>
                    <div className="empty-state-desc">
                        Seed the database with sample defect data to see the risk analytics dashboard.
                    </div>
                </div>
            </div>
        );
    }

    // Prepare chart data
    const severityData = Object.entries(data.severity_distribution).map(([key, value]) => ({
        name: key.charAt(0).toUpperCase() + key.slice(1),
        value,
        fill: SEVERITY_COLORS[key] || '#6366f1',
    }));

    const moduleBarData = data.modules.slice(0, 8).map((m) => ({
        name: m.module_id.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()),
        risk: Math.round(m.risk_score * 100),
        defects: m.defect_count,
    }));

    return (
        <>
            {/* Stat Cards */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-card-icon purple"><Bug size={24} /></div>
                    <div className="stat-card-info">
                        <span className="stat-card-value">{data.total_defects}</span>
                        <span className="stat-card-label">Total Defects</span>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-card-icon cyan"><ShieldAlert size={24} /></div>
                    <div className="stat-card-info">
                        <span className="stat-card-value">{data.modules?.length || 0}</span>
                        <span className="stat-card-label">Modules Tracked</span>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-card-icon amber"><TrendingUp size={24} /></div>
                    <div className="stat-card-info">
                        <span className="stat-card-value">
                            {data.modules?.[0] ? (data.modules[0].risk_score * 100).toFixed(0) + '%' : '—'}
                        </span>
                        <span className="stat-card-label">Highest Risk</span>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-card-icon emerald"><MessageSquareDot size={24} /></div>
                    <div className="stat-card-info">
                        <span className="stat-card-value">{data.feedback_stats?.total_feedback || 0}</span>
                        <span className="stat-card-label">Feedback Entries</span>
                    </div>
                </div>
            </div>

            {/* Risk Heatmap */}
            <div className="card" style={{ marginBottom: 24 }}>
                <div className="card-header">
                    <div className="card-title">
                        <ShieldAlert size={18} />
                        Module Risk Heatmap
                    </div>
                    <button className="btn btn-secondary btn-sm" onClick={loadAnalytics}>Refresh</button>
                </div>
                <div className="heatmap-grid">
                    {data.modules.map((mod) => (
                        <div className={`heatmap-cell ${getRiskClass(mod.risk_score)}`} key={mod.module_id}>
                            <div className="heatmap-cell-title">
                                {mod.module_id.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                            </div>
                            <div className="heatmap-cell-score">
                                {(mod.risk_score * 100).toFixed(0)}%
                            </div>
                            <div className="heatmap-cell-count">{mod.defect_count} defect(s)</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Charts */}
            <div className="content-grid">
                {/* Severity Pie */}
                <div className="card">
                    <div className="card-header">
                        <div className="card-title">
                            <BarChart3 size={18} />
                            Severity Distribution
                        </div>
                    </div>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={severityData}
                                    cx="50%"
                                    cy="50%"
                                    outerRadius={100}
                                    innerRadius={55}
                                    paddingAngle={3}
                                    dataKey="value"
                                    stroke="none"
                                >
                                    {severityData.map((entry, index) => (
                                        <Cell key={index} fill={entry.fill} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{
                                        background: '#111827',
                                        border: '1px solid rgba(99,115,255,0.3)',
                                        borderRadius: 12,
                                    }}
                                />
                                <Legend
                                    wrapperStyle={{ fontSize: 12, color: '#94a3b8' }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Module Risk Bar */}
                <div className="card">
                    <div className="card-header">
                        <div className="card-title">
                            <TrendingUp size={18} />
                            Module Risk Scores
                        </div>
                    </div>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={moduleBarData} layout="vertical" margin={{ left: 20 }}>
                                <XAxis type="number" domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 11 }} />
                                <YAxis
                                    dataKey="name"
                                    type="category"
                                    width={110}
                                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                                />
                                <Tooltip
                                    contentStyle={{
                                        background: '#111827',
                                        border: '1px solid rgba(99,115,255,0.3)',
                                        borderRadius: 12,
                                    }}
                                    formatter={(value) => [`${value}%`, 'Risk Score']}
                                />
                                <Bar
                                    dataKey="risk"
                                    fill="#6366f1"
                                    radius={[0, 6, 6, 0]}
                                    barSize={20}
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </>
    );
}

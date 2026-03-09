import { Brain } from 'lucide-react';
import {
    Search,
    BarChart3,
    Database,
    MessageSquare,
    ShieldCheck,
    Zap,
} from 'lucide-react';

const navItems = [
    { id: 'query', label: 'AI Query', icon: Search },
    { id: 'analytics', label: 'Risk Dashboard', icon: BarChart3 },
    { id: 'knowledge', label: 'Knowledge Base', icon: Database },
];

export default function Sidebar({ activeView, onNavigate }) {
    return (
        <aside className="sidebar">
            <div className="sidebar-logo">
                <div className="sidebar-logo-icon">
                    <Brain />
                </div>
                <div className="sidebar-logo-text">
                    <span className="sidebar-logo-title">DKI Platform</span>
                    <span className="sidebar-logo-subtitle">AI Assurance</span>
                </div>
            </div>

            <nav className="sidebar-nav">
                {navItems.map((item) => (
                    <div
                        key={item.id}
                        className={`sidebar-nav-item ${activeView === item.id ? 'active' : ''}`}
                        onClick={() => onNavigate(item.id)}
                    >
                        <item.icon />
                        <span>{item.label}</span>
                    </div>
                ))}
            </nav>

            <div className="sidebar-footer">
                <div className="sidebar-status">
                    <div className="sidebar-status-dot" />
                    <span>Agent Online — v1.0</span>
                </div>
            </div>
        </aside>
    );
}

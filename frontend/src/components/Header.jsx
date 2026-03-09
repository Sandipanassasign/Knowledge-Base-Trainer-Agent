import { Sparkles, Database } from 'lucide-react';
import { seedDatabase } from '../api/client';
import { useState } from 'react';

const viewTitles = {
    query: '🧠 AI-Powered Query',
    analytics: '📊 Risk Analytics Dashboard',
    knowledge: '💾 Knowledge Base Management',
};

export default function Header({ activeView }) {
    const [seeding, setSeeding] = useState(false);
    const [seedMsg, setSeedMsg] = useState('');

    const handleSeed = async () => {
        setSeeding(true);
        setSeedMsg('');
        try {
            const res = await seedDatabase();
            setSeedMsg(res.message);
        } catch (err) {
            setSeedMsg('❌ ' + err.message);
        } finally {
            setSeeding(false);
            setTimeout(() => setSeedMsg(''), 4000);
        }
    };

    return (
        <header className="header">
            <div className="header-title">
                <Sparkles size={20} />
                {viewTitles[activeView] || 'DKI Assurance Platform'}
            </div>
            <div className="header-actions">
                {seedMsg && (
                    <span style={{ fontSize: '13px', color: 'var(--accent-emerald)' }}>{seedMsg}</span>
                )}
                <button className="btn btn-secondary btn-sm" onClick={handleSeed} disabled={seeding}>
                    <Database size={14} />
                    {seeding ? 'Seeding…' : 'Seed Sample Data'}
                </button>
            </div>
        </header>
    );
}

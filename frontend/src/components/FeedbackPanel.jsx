import { useState } from 'react';
import { ThumbsUp, ThumbsDown, MessageCircle } from 'lucide-react';
import { submitFeedback } from '../api/client';

export default function FeedbackPanel({ sessionId }) {
    const [feedbackGiven, setFeedbackGiven] = useState(false);
    const [showCorrection, setShowCorrection] = useState(false);
    const [correction, setCorrection] = useState('');
    const [context, setContext] = useState('');
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);

    if (!sessionId) return null;

    const handleFeedback = async (type) => {
        if (type === 'incorrect') {
            setShowCorrection(true);
            return;
        }

        setLoading(true);
        try {
            const res = await submitFeedback({ sessionId, feedbackType: 'correct' });
            setMessage(res.message);
            setFeedbackGiven(true);
        } catch (err) {
            setMessage('❌ ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmitCorrection = async () => {
        if (!correction.trim()) return;
        setLoading(true);
        try {
            const res = await submitFeedback({
                sessionId,
                feedbackType: 'incorrect',
                correction: correction.trim(),
                additionalContext: context.trim() || null,
            });
            setMessage(res.message);
            setFeedbackGiven(true);
            setShowCorrection(false);
        } catch (err) {
            setMessage('❌ ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="card" style={{ marginBottom: 24 }}>
            <div className="card-header">
                <div className="card-title">
                    <MessageCircle size={18} />
                    Rate This Recommendation
                </div>
            </div>

            <div className="feedback-panel">
                {!feedbackGiven && !showCorrection && (
                    <div className="feedback-buttons">
                        <button
                            className="btn btn-success"
                            onClick={() => handleFeedback('correct')}
                            disabled={loading}
                        >
                            <ThumbsUp size={16} />
                            Helpful
                        </button>
                        <button
                            className="btn btn-danger"
                            onClick={() => handleFeedback('incorrect')}
                            disabled={loading}
                        >
                            <ThumbsDown size={16} />
                            Not Helpful
                        </button>
                    </div>
                )}

                {showCorrection && !feedbackGiven && (
                    <>
                        <div className="input-group">
                            <label className="input-label">What's the correct approach?</label>
                            <textarea
                                className="textarea"
                                placeholder="Provide the correct testing strategy or approach..."
                                value={correction}
                                onChange={(e) => setCorrection(e.target.value)}
                                rows={3}
                            />
                        </div>
                        <div className="input-group">
                            <label className="input-label">Additional Context (optional)</label>
                            <input
                                className="input"
                                placeholder="Any extra context..."
                                value={context}
                                onChange={(e) => setContext(e.target.value)}
                            />
                        </div>
                        <div style={{ display: 'flex', gap: 12 }}>
                            <button
                                className="btn btn-primary btn-sm"
                                onClick={handleSubmitCorrection}
                                disabled={loading || !correction.trim()}
                            >
                                {loading ? 'Saving…' : 'Submit Correction'}
                            </button>
                            <button
                                className="btn btn-secondary btn-sm"
                                onClick={() => setShowCorrection(false)}
                            >
                                Cancel
                            </button>
                        </div>
                    </>
                )}

                {message && (
                    <div className={`feedback-message ${feedbackGiven ? 'success' : 'info'}`}>
                        {message}
                    </div>
                )}
            </div>
        </div>
    );
}

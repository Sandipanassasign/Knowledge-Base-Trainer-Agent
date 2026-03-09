/**
 * API Client for the DKI Assurance Platform backend.
 */
const API_BASE = 'http://localhost:8000/api';

async function request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
        headers: { 'Content-Type': 'application/json' },
        ...options,
    };

    try {
        const response = await fetch(url, config);
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }
        return await response.json();
    } catch (err) {
        if (err.message === 'Failed to fetch') {
            throw new Error('Backend unavailable. Ensure the FastAPI server is running on port 8000.');
        }
        throw err;
    }
}

/** Submit a query to the DKI agent */
export async function queryAgent({ query, moduleFilter, severityFilter, codeChanges }) {
    return request('/query', {
        method: 'POST',
        body: JSON.stringify({
            query,
            module_filter: moduleFilter || null,
            severity_filter: severityFilter || null,
            code_changes: codeChanges || null,
        }),
    });
}

/** Submit feedback on a recommendation */
export async function submitFeedback({ sessionId, feedbackType, correction, additionalContext }) {
    return request('/feedback', {
        method: 'POST',
        body: JSON.stringify({
            session_id: sessionId,
            feedback_type: feedbackType,
            correction: correction || null,
            additional_context: additionalContext || null,
        }),
    });
}

/** Fetch analytics data for the dashboard */
export async function getAnalytics() {
    return request('/analytics');
}

/** Seed the database with sample data */
export async function seedDatabase() {
    return request('/seed', { method: 'POST' });
}

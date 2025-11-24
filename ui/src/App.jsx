import { useState } from 'react';
import Layout from './components/Layout';
import ProfilerForm from './components/ProfilerForm';
import Dashboard from './components/Dashboard';
import ComparisonView from './components/ComparisonView';
import './App.css';

function App() {
    const [activeTab, setActiveTab] = useState('profile');
    const [results, setResults] = useState(null);

    const handleProfileComplete = (data) => {
        setResults(data);
        setActiveTab('dashboard');
    };

    return (
        <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
            {activeTab === 'profile' && (
                <div className="profile-view">
                    <h1>Start Profiling</h1>
                    <p className="subtitle">Analyze your Python code for performance, memory, and complexity.</p>
                    <ProfilerForm onProfileComplete={handleProfileComplete} />
                </div>
            )}

            {activeTab === 'dashboard' && (
                <div className="dashboard-view">
                    {results ? (
                        <Dashboard data={results} />
                    ) : (
                        <div className="empty-state">
                            <p>No profiling data available. Start a new profile.</p>
                            <button onClick={() => setActiveTab('profile')}>Go to Profiler</button>
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'compare' && <ComparisonView />}
            {activeTab === 'history' && <div>History Placeholder</div>}
            {activeTab === 'settings' && <div>Settings Placeholder</div>}
        </Layout>
    );
}

export default App;

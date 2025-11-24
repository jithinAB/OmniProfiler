import React, { useState } from 'react';
import axios from 'axios';
import { Code, FileUp, GitBranch, Play } from 'lucide-react';
import { API_ENDPOINTS } from '../config';
import './ProfilerForm.css';

const ProfilerForm = ({ onProfileComplete }) => {
    const [mode, setMode] = useState('code'); // code, file, repo
    const [input, setInput] = useState('');
    const [entryPoint, setEntryPoint] = useState('');
    const [file, setFile] = useState(null);
    const [warmupRuns, setWarmupRuns] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            let response;
            if (mode === 'code') {
                response = await axios.post(API_ENDPOINTS.profileCode, {
                    code: input,
                    warmup_runs: warmupRuns
                });
            } else if (mode === 'file') {
                const formData = new FormData();
                formData.append('file', file);
                response = await axios.post(API_ENDPOINTS.profileFile, formData);
            } else if (mode === 'repo') {
                response = await axios.post(API_ENDPOINTS.profileRepo, {
                    url: input,
                    entry_point: entryPoint || null
                });
            }
            onProfileComplete(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="profiler-form-container">
            <div className="mode-selector">
                <button className={mode === 'code' ? 'active' : ''} onClick={() => setMode('code')}>
                    <Code size={16} /> Code Snippet
                </button>
                <button className={mode === 'file' ? 'active' : ''} onClick={() => setMode('file')}>
                    <FileUp size={16} /> Upload File
                </button>
                <button className={mode === 'repo' ? 'active' : ''} onClick={() => setMode('repo')}>
                    <GitBranch size={16} /> Repository
                </button>
            </div>

            <form onSubmit={handleSubmit} className="profiler-form">
                {mode === 'code' && (
                    <textarea
                        placeholder="Paste your Python code here..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        className="code-input"
                    />
                )}

                {mode === 'file' && (
                    <div className="file-input-wrapper">
                        <input
                            type="file"
                            onChange={(e) => setFile(e.target.files[0])}
                            className="file-input"
                        />
                        <div className="file-drop-zone">
                            <FileUp size={32} />
                            <p>{file ? file.name : "Drag & drop or click to upload"}</p>
                        </div>
                    </div>
                )}

                {mode === 'repo' && (
                    <div className="repo-inputs">
                        <input
                            type="text"
                            placeholder="https://github.com/username/repo.git"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            className="repo-input"
                        />
                        <input
                            type="text"
                            placeholder="Entry Point (e.g., main.py) - Optional"
                            value={entryPoint}
                            onChange={(e) => setEntryPoint(e.target.value)}
                            className="repo-input entry-point"
                            title="Specify the main python file to execute for dynamic profiling"
                        />
                    </div>
                )}

                {mode === 'code' && (
                    <div className="advanced-options">
                        <details>
                            <summary>Advanced Options</summary>
                            <div className="option-group">
                                <label htmlFor="warmup-runs">
                                    Warm-up Runs
                                    <span className="info-tooltip" title="Execute code N times before profiling to stabilize caches and JIT. WARNING: Side effects will happen multiple times.">ℹ️</span>
                                </label>
                                <input
                                    id="warmup-runs"
                                    type="number"
                                    min="0"
                                    max="10"
                                    value={warmupRuns}
                                    onChange={(e) => setWarmupRuns(parseInt(e.target.value) || 0)}
                                    className="number-input"
                                />
                            </div>
                        </details>
                    </div>
                )}

                {error && <div className="error-message">{error}</div>}

                <button type="submit" className="run-btn" disabled={loading}>
                    {loading ? 'Profiling...' : <><Play size={16} /> Run Profiler</>}
                </button>
            </form>
        </div>
    );
};

export default ProfilerForm;

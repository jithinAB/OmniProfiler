import React, { useState } from 'react';
import { Upload, ArrowRight, ArrowDown, ArrowUp, Minus } from 'lucide-react';
import { formatBytes, formatTime } from '../utils/formatters';
import './ComparisonView.css';

const ComparisonView = () => {
    const [fileA, setFileA] = useState(null);
    const [fileB, setFileB] = useState(null);
    const [reportA, setReportA] = useState(null);
    const [reportB, setReportB] = useState(null);
    const [comparison, setComparison] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleFileChange = (e, setFile, setReport) => {
        const file = e.target.files[0];
        if (file) {
            setFile(file);
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const json = JSON.parse(event.target.result);
                    setReport(json);
                } catch (err) {
                    setError(`Error parsing ${file.name}: ${err.message}`);
                }
            };
            reader.readAsText(file);
        }
    };

    const handleCompare = async () => {
        if (!reportA || !reportB) return;

        setLoading(true);
        setError(null);

        try {
            const response = await fetch('/api/compare', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    report_a: reportA,
                    report_b: reportB
                }),
            });

            if (!response.ok) {
                throw new Error('Comparison failed');
            }

            const data = await response.json();
            setComparison(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const MetricDiff = ({ label, data, formatter = (v) => v }) => {
        if (!data) return null;
        const { baseline, comparison, diff, pct, status } = data;

        let colorClass = 'neutral';
        let Icon = Minus;

        if (status === 'improved') {
            colorClass = 'improved';
            Icon = ArrowDown; // Assuming lower is better for most metrics
        } else if (status === 'degraded') {
            colorClass = 'degraded';
            Icon = ArrowUp;
        }

        return (
            <div className={`diff-card ${colorClass}`}>
                <h4>{label}</h4>
                <div className="diff-values">
                    <div className="value-box">
                        <span className="label">Baseline</span>
                        <span className="value">{formatter(baseline)}</span>
                    </div>
                    <div className="diff-arrow">
                        <ArrowRight size={16} />
                    </div>
                    <div className="value-box">
                        <span className="label">Comparison</span>
                        <span className="value">{formatter(comparison)}</span>
                    </div>
                </div>
                <div className="diff-stat">
                    <Icon size={16} />
                    <span className="pct">{Math.abs(pct).toFixed(1)}%</span>
                    <span className="abs">({diff > 0 ? '+' : ''}{formatter(diff)})</span>
                </div>
            </div>
        );
    };

    return (
        <div className="comparison-view">
            <h2>Profiler Comparison Tool</h2>

            <div className="upload-section">
                <div className="upload-box">
                    <h3>Baseline Report (A)</h3>
                    <input
                        type="file"
                        accept=".json"
                        onChange={(e) => handleFileChange(e, setFileA, setReportA)}
                    />
                    {fileA && <p className="file-name">{fileA.name}</p>}
                </div>

                <div className="vs-badge">VS</div>

                <div className="upload-box">
                    <h3>Comparison Report (B)</h3>
                    <input
                        type="file"
                        accept=".json"
                        onChange={(e) => handleFileChange(e, setFileB, setReportB)}
                    />
                    {fileB && <p className="file-name">{fileB.name}</p>}
                </div>
            </div>

            <div className="actions">
                <button
                    className="compare-btn"
                    onClick={handleCompare}
                    disabled={!reportA || !reportB || loading}
                >
                    {loading ? 'Comparing...' : 'Compare Reports'}
                </button>
            </div>

            {error && <div className="error-message">{error}</div>}

            {comparison && (
                <div className="results-section">
                    <h3>Performance Delta</h3>

                    <div className="diff-grid">
                        <MetricDiff
                            label="Execution Time"
                            data={comparison.time?.wall_time}
                            formatter={formatTime}
                        />
                        <MetricDiff
                            label="CPU Time"
                            data={comparison.time?.cpu_time}
                            formatter={formatTime}
                        />
                        <MetricDiff
                            label="Peak Memory"
                            data={comparison.memory?.peak_memory}
                            formatter={formatBytes}
                        />
                        <MetricDiff
                            label="Total Allocations"
                            data={comparison.allocations?.total_allocations}
                            formatter={(v) => v.toLocaleString()}
                        />
                        <MetricDiff
                            label="GC Collections"
                            data={comparison.gc?.total_collections}
                            formatter={(v) => v.toLocaleString()}
                        />
                        <MetricDiff
                            label="GC Objects"
                            data={comparison.gc?.total_objects}
                            formatter={(v) => v.toLocaleString()}
                        />
                    </div>
                </div>
            )}
        </div>
    );
};

export default ComparisonView;

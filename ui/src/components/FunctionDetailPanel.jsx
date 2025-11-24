import React from 'react';
import { X, Clock, Hash, Zap } from 'lucide-react';
import './FunctionDetailPanel.css';

const FunctionDetailPanel = ({ functionName, data, onClose }) => {
    if (!functionName || !data) return null;

    const complexity = data.static_analysis?.complexity?.[functionName] || 0;
    const callGraph = data.static_analysis?.call_graph?.[functionName] || [];
    const lineProfiles = data.dynamic_analysis?.line_profiles?.[functionName];

    // Extract calls from hotspots if available
    const hotspots = data.dynamic_analysis?.hotspots || [];
    let calls = 0;
    let totalTime = 0;

    // Parse hotspots to find this function's stats
    hotspots.forEach(line => {
        if (line.includes(functionName)) {
            const match = line.match(/(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)/);
            if (match) {
                calls = parseInt(match[1]);
                totalTime = parseFloat(match[4]);
            }
        }
    });

    const complexityLevel = complexity <= 5 ? 'low' : complexity <= 10 ? 'medium' : 'high';
    const complexityColor = complexityLevel === 'low' ? '#00ff88' : complexityLevel === 'medium' ? '#ffaa00' : '#ff0055';

    return (
        <div className="function-detail-panel">
            <div className="panel-header">
                <h3>{functionName}()</h3>
                <button className="close-btn" onClick={onClose}>
                    <X size={20} />
                </button>
            </div>

            <div className="panel-content">
                {/* Summary Metrics */}
                <div className="metrics-summary">
                    <div className="metric-item">
                        <div className="metric-icon"><Hash color={complexityColor} /></div>
                        <div className="metric-details">
                            <span className="metric-label">Complexity</span>
                            <span className="metric-value" style={{ color: complexityColor }}>{complexity}</span>
                        </div>
                    </div>

                    {calls > 0 && (
                        <div className="metric-item">
                            <div className="metric-icon"><Zap color="#00f2ff" /></div>
                            <div className="metric-details">
                                <span className="metric-label">Total Calls</span>
                                <span className="metric-value">{calls.toLocaleString()}</span>
                            </div>
                        </div>
                    )}

                    {totalTime > 0 && (
                        <div className="metric-item">
                            <div className="metric-icon"><Clock color="#d946ef" /></div>
                            <div className="metric-details">
                                <span className="metric-label">Total Time</span>
                                <span className="metric-value">{(totalTime * 1000).toFixed(2)} ms</span>
                            </div>
                        </div>
                    )}
                </div>

                {/* Call Relationships */}
                {callGraph.length > 0 && (
                    <div className="section">
                        <h4>Calls To:</h4>
                        <div className="call-list">
                            {callGraph.map((callee, idx) => (
                                <div key={idx} className="call-item">
                                    <span className="call-arrow">→</span>
                                    <span className="call-name">{callee}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Line-level data if available */}
                {lineProfiles && lineProfiles.lines && Object.keys(lineProfiles.lines).length > 0 && (
                    <div className="section">
                        <h4>Line-Level Performance:</h4>

                        {/* Source code with metrics */}
                        {lineProfiles.source && (
                            <div className="source-viewer">
                                <table className="source-table">
                                    <thead>
                                        <tr>
                                            <th className="line-no-header">Line</th>
                                            <th className="hits-header">Hits</th>
                                            <th className="time-header">Time</th>
                                            <th className="code-header">Code</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {lineProfiles.source.split('\n').map((line, idx) => {
                                            const lineNo = (lineProfiles.start_line || 1) + idx;
                                            const stats = lineProfiles.lines[lineNo.toString()];
                                            const hasStats = !!stats;
                                            const heat = hasStats && stats.time_ms > 1 ? 'hot' : hasStats && stats.time_ms > 0.1 ? 'warm' : 'cool';

                                            return (
                                                <tr key={idx} className={hasStats ? `has-stats ${heat}` : ''}>
                                                    <td className="line-no">{lineNo}</td>
                                                    <td className="hits">{hasStats ? stats.hits.toLocaleString() : ''}</td>
                                                    <td className="time">{hasStats ? `${stats.time_ms}ms` : ''}</td>
                                                    <td className="code">
                                                        <code>{line || ' '}</code>
                                                    </td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                </table>
                            </div>
                        )}

                        {/* Fallback to table view if no source */}
                        {!lineProfiles.source && (
                            <div className="line-stats">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Line</th>
                                            <th>Hits</th>
                                            <th>Time (ms)</th>
                                            <th>Per Hit (μs)</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {Object.entries(lineProfiles.lines)
                                            .sort(([a], [b]) => parseInt(a) - parseInt(b))
                                            .map(([lineNo, stats]) => (
                                                <tr key={lineNo}>
                                                    <td>{lineNo}</td>
                                                    <td>{stats.hits.toLocaleString()}</td>
                                                    <td>{stats.time_ms}</td>
                                                    <td>{stats.time_per_hit_us}</td>
                                                </tr>
                                            ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                )}

                {/* Placeholder for future enhancements */}
                {!lineProfiles || !lineProfiles.lines || Object.keys(lineProfiles.lines).length === 0 && (
                    <div className="section placeholder">
                        <p>Analyzing line-by-line metrics...</p>
                        <small>Line profiling running in background</small>
                    </div>
                )}
            </div>
        </div>
    );
};

export default FunctionDetailPanel;

import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { Cpu, Gauge, HelpCircle } from 'lucide-react';
import { formatTime, formatNumber } from '../utils/formatters';
import './CPUMetrics.css';

const CPUMetrics = ({ cpuData, timeData }) => {
    if (!cpuData) {
        return null;
    }

    const { user_time, system_time, cpu_percent, context_switches } = cpuData;

    // Prepare data for pie chart
    const cpuTimeData = [
        { name: 'User Time', value: user_time || 0, color: '#00f2ff' },
        { name: 'System Time', value: system_time || 0, color: '#ffaa00' }
    ];

    const totalTime = user_time + system_time;
    const userPercent = totalTime > 0 ? ((user_time / totalTime) * 100).toFixed(1) : 0;
    const systemPercent = totalTime > 0 ? ((system_time / totalTime) * 100).toFixed(1) : 0;

    return (
        <div className="cpu-metrics">
            <div className="cpu-header">
                <Cpu color="#00f2ff" size={20} />
                <h4>CPU Performance</h4>
                <HelpCircle
                    size={14}
                    className="help-icon"
                    title="CPU metrics show how your code uses processing resources. Lower values are better."
                />
            </div>

            <div className="cpu-grid">
                {/* CPU Utilization Gauge */}
                <div className="cpu-utilization" title="Percentage of CPU used during execution. Lower is better.">
                    <div className="cpu-gauge">
                        <Gauge size={48} color="#00f2ff" />
                        <div className="cpu-percent-display">
                            <span className="cpu-percent-value">{formatNumber(cpu_percent || 0)}</span>
                            <span className="cpu-percent-label">%</span>
                        </div>
                    </div>
                    <span className="cpu-gauge-label">CPU Utilization</span>
                </div>

                {/* Time Breakdown Pie Chart */}
                <div className="cpu-breakdown" title="User time is your code, System time is OS/kernel calls. Lower is better for both.">
                    <h5>Time Breakdown</h5>
                    <ResponsiveContainer width="100%" height={150}>
                        <PieChart>
                            <Pie
                                data={cpuTimeData}
                                cx="50%"
                                cy="50%"
                                innerRadius={40}
                                outerRadius={60}
                                paddingAngle={2}
                                dataKey="value"
                            >
                                {cpuTimeData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{ backgroundColor: '#111', border: '1px solid #333' }}
                                formatter={(value) => formatTime(value)}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                    <div className="cpu-time-stats">
                        <div className="cpu-time-stat">
                            <span className="cpu-time-dot" style={{ backgroundColor: '#00f2ff' }}></span>
                            <span>User: {formatTime(user_time || 0)} ({userPercent}%)</span>
                        </div>
                        <div className="cpu-time-stat">
                            <span className="cpu-time-dot" style={{ backgroundColor: '#ffaa00' }}></span>
                            <span>System: {formatTime(system_time || 0)} ({systemPercent}%)</span>
                        </div>
                    </div>
                </div>

                {/* Context Switches */}
                {context_switches && (
                    <div className="cpu-context-switches" title="Context switches indicate how often the process was interrupted. Lower is better.">
                        <h5>Context Switches</h5>
                        <div className="cpu-ctx-stats">
                            <div className="cpu-ctx-stat">
                                <span className="cpu-ctx-label">Voluntary</span>
                                <span className="cpu-ctx-value" title="Process yielded CPU (e.g., waiting for I/O)">{formatNumber(context_switches.voluntary)}</span>
                            </div>
                            <div className="cpu-ctx-stat">
                                <span className="cpu-ctx-label">Involuntary</span>
                                <span className="cpu-ctx-value" title="Process was preempted by OS (indicates contention)">{formatNumber(context_switches.involuntary)}</span>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default CPUMetrics;

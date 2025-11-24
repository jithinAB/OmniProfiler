import React from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { Cpu, Zap, Copy, AlertTriangle } from 'lucide-react';
import { formatBytes } from '../utils/formatters';
import './ScaleneDashboard.css';

const MetricCard = ({ icon, title, value, subtitle, tooltip, isWarning }) => (
    <div className={`metric-card ${isWarning ? 'warning' : ''}`} title={tooltip}>
        <div className="metric-icon">{icon}</div>
        <div className="metric-info">
            <div className="metric-header">
                <h3>{title}</h3>
            </div>
            <p>{value}</p>
            {subtitle && <span>{subtitle}</span>}
        </div>
    </div>
);

const ScaleneDashboard = ({ data }) => {
    if (!data || !data.files) return null;

    // Aggregate metrics across all files
    let totalPythonCpu = 0;
    let totalNativeCpu = 0;
    let totalSystemCpu = 0;
    let totalCopyVolume = 0;
    let maxPeakMem = 0;
    let leaks = [];

    // Iterate through files to aggregate data
    Object.entries(data.files).forEach(([filename, fileData]) => {
        // CPU aggregation (using function level summaries if available, or just summing up)
        // Scalene provides percentages, so we might need to look at samples or just average percentages
        // Actually, Scalene's JSON has `percent_cpu_time` per file.
        // And inside functions/lines it has `n_cpu_percent_python`, `n_cpu_percent_c`, `n_sys_percent`.

        // Let's look at the first file's summary for simplicity or iterate lines
        if (fileData.functions) {
            fileData.functions.forEach(func => {
                totalPythonCpu += func.n_cpu_percent_python;
                totalNativeCpu += func.n_cpu_percent_c;
                totalSystemCpu += func.n_sys_percent;
                totalCopyVolume += func.n_copy_mb_s;
            });
        }

        // Leaks
        if (fileData.leaks && Object.keys(fileData.leaks).length > 0) {
            Object.entries(fileData.leaks).forEach(([lineno, leakData]) => {
                leaks.push({
                    file: filename,
                    line: lineno,
                    ...leakData
                });
            });
        }
    });

    // Normalize CPU percentages to 100% for the chart
    const totalCpu = totalPythonCpu + totalNativeCpu + totalSystemCpu;
    const cpuData = [
        { name: 'Python', value: totalCpu ? (totalPythonCpu / totalCpu) * 100 : 0 },
        { name: 'Native', value: totalCpu ? (totalNativeCpu / totalCpu) * 100 : 0 },
        { name: 'System', value: totalCpu ? (totalSystemCpu / totalCpu) * 100 : 0 },
    ].filter(d => d.value > 0);

    const COLORS = ['#3b82f6', '#10b981', '#f59e0b'];

    return (
        <div className="scalene-dashboard">
            <div className="dashboard-header">
                <h2>Scalene Advanced Profiling</h2>
                <div className="badge">High Precision</div>
            </div>

            <div className="metrics-grid">
                <MetricCard
                    icon={<Cpu color="#3b82f6" />}
                    title="Python vs Native"
                    value={`${(cpuData.find(d => d.name === 'Python')?.value || 0).toFixed(1)}% Python`}
                    subtitle={`${(cpuData.find(d => d.name === 'Native')?.value || 0).toFixed(1)}% Native`}
                    tooltip="Breakdown of execution time between Python code and Native C extensions."
                />
                <MetricCard
                    icon={<Copy color="#f59e0b" />}
                    title="Memory Copy"
                    value={`${totalCopyVolume.toFixed(2)} MB/s`}
                    subtitle="Copy Volume"
                    tooltip="Rate of memory copying. High values indicate inefficient data handling (e.g. non-zero-copy NumPy operations)."
                    isWarning={totalCopyVolume > 100}
                />
                <MetricCard
                    icon={<AlertTriangle color="#ef4444" />}
                    title="Memory Leaks"
                    value={leaks.length}
                    subtitle="Potential Leaks"
                    tooltip="Number of lines with potential memory leaks detected."
                    isWarning={leaks.length > 0}
                />
            </div>

            <div className="charts-grid">
                <div className="chart-card">
                    <h3>CPU Time Breakdown</h3>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={cpuData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {cpuData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip contentStyle={{ backgroundColor: '#111', border: '1px solid #333' }} />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Placeholder for Memory Breakdown or other charts */}
                <div className="chart-card">
                    <h3>Memory Efficiency</h3>
                    <div className="chart-container flex-center">
                        <p className="no-data">Detailed memory breakdown coming soon</p>
                    </div>
                </div>
            </div>

            {leaks.length > 0 && (
                <div className="leaks-section">
                    <h3>Detected Memory Leaks</h3>
                    <div className="table-container">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>File</th>
                                    <th>Line</th>
                                    <th>Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                {leaks.map((leak, idx) => (
                                    <tr key={idx}>
                                        <td className="monospace">{leak.file}</td>
                                        <td className="monospace">{leak.line}</td>
                                        <td>{JSON.stringify(leak)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ScaleneDashboard;

import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Clock, Cpu, HardDrive, Zap, HelpCircle, Download, FileUp, Code, Copy, AlertTriangle } from 'lucide-react';
import CallGraph from './CallGraph';
import HotspotsTable from './HotspotsTable';
import CallTreeViewer from './CallTreeViewer';
import GCMetrics from './GCMetrics';
import CPUMetrics from './CPUMetrics';
import HardwareDetails from './HardwareDetails';
import ExecutionGraph from './ExecutionGraph';
import ScaleneDashboard from './ScaleneDashboard';
import { formatBytes, formatTime } from '../utils/formatters';
import './Dashboard.css';

const MetricCard = ({ icon, title, value, subtitle, tooltip, isGood }) => (
    <div className="metric-card" title={tooltip}>
        <div className="metric-icon">{icon}</div>
        <div className="metric-info">
            <div className="metric-header">
                <h3>{title}</h3>
                {tooltip && <HelpCircle size={14} className="help-icon" />}
            </div>
            <p className={isGood ? 'metric-good' : ''}>{value}</p>
            {subtitle && <span>{subtitle}</span>}
        </div>
    </div>
);

const RepoDashboard = ({ data }) => {
    // Safety checks
    if (!data || !data.files || !data.summary) {
        return <div className="dashboard"><p>Error: Invalid repository data</p></div>;
    }

    const { summary, files, dynamic_analysis, hardware, scalene_analysis } = data;

    // Helper to calculate total complexity from complexity dict
    const getComplexity = (complexityObj) => {
        if (!complexityObj || typeof complexityObj !== 'object') return 0;
        const values = Object.values(complexityObj);
        if (values.length === 0) return 0;
        // Handle both old (int) and new ({complexity: int}) formats
        return values.reduce((sum, val) => {
            const score = typeof val === 'number' ? val : (val?.complexity || 0);
            return sum + score;
        }, 0);
    };

    // Calculate Repo Aggregates (with safety checks)
    const totalLoc = Array.isArray(files) ? files.reduce((acc, f) => acc + (f.raw_metrics?.loc || 0), 0) : 0;
    const totalSloc = Array.isArray(files) ? files.reduce((acc, f) => acc + (f.raw_metrics?.sloc || 0), 0) : 0;
    const avgMaintainability = (Array.isArray(files) && files.length > 0)
        ? files.reduce((acc, f) => acc + (f.maintainability || 0), 0) / files.length
        : 0;

    // Prepare complexity data for chart
    const complexityData = files
        .map(f => ({
            name: f.path.split('/').pop(), // Just filename
            complexity: getComplexity(f.complexity),
            path: f.path
        }))
        .filter(f => f.complexity > 0)
        .sort((a, b) => b.complexity - a.complexity)
        .slice(0, 15);

    // Dynamic Metrics (if available)
    const timeMetrics = dynamic_analysis?.time || {};
    const memMetrics = dynamic_analysis?.memory || {};
    const ioMetrics = dynamic_analysis?.io || {};

    const wallTime = Number(timeMetrics.wall_time) || 0;
    const cpuTime = Number(timeMetrics.cpu_time) || 0;
    const currentMem = Number(memMetrics.current_memory) || 0;
    const peakMem = Number(memMetrics.peak_memory) || 0;

    // Helper to get all functions
    const getAllFunctions = () => {
        const allFuncs = [];
        files.forEach(file => {
            if (file.complexity) {
                Object.entries(file.complexity).forEach(([funcName, details]) => {
                    // Handle both old and new formats
                    const complexity = typeof details === 'number' ? details : details.complexity;
                    const loc = typeof details === 'object' ? details.loc : 'N/A';
                    const lineno = typeof details === 'object' ? details.lineno : 'N/A';

                    allFuncs.push({
                        name: funcName,
                        file: file.path,
                        complexity: complexity,
                        big_o: file.big_o?.[funcName] || 'N/A',
                        loc: loc,
                        lineno: lineno
                    });
                });
            }
        });
        return allFuncs.sort((a, b) => b.complexity - a.complexity);
    };

    const allFunctions = getAllFunctions();

    return (
        <div className="dashboard">
            <div className="dashboard-header">
                <h2>Repository Analysis</h2>
                <div className="repo-path">{data.repo_path}</div>
            </div>

            {/* Scalene Analysis Section (if available) */}
            {scalene_analysis && (
                <div className="dynamic-section">
                    <ScaleneDashboard data={scalene_analysis} />
                    <div className="divider" style={{ margin: '2rem 0', borderBottom: '1px solid #333' }}></div>
                </div>
            )}

            {/* Dynamic Analysis Section (if available) */}
            {dynamic_analysis && (
                <div className="dynamic-section">
                    <h3>Dynamic Profiling Results</h3>
                    <div className="metrics-grid">
                        <MetricCard
                            icon={<Clock color="#00f2ff" />}
                            title="Execution Time"
                            value={formatTime(wallTime)}
                            subtitle={`CPU: ${formatTime(cpuTime)}`}
                            tooltip="Total elapsed time (wall clock). Lower is better. CPU time shows actual processing time."
                            isGood={wallTime < 1}
                        />
                        <MetricCard
                            icon={<Zap color="#d946ef" />}
                            title="Peak Memory"
                            value={formatBytes(peakMem)}
                            subtitle={`Current: ${formatBytes(currentMem)}`}
                            tooltip="Maximum memory allocated during execution. Lower is better for efficiency."
                            isGood={peakMem < 10 * 1024 * 1024} // < 10MB is good
                        />
                        <MetricCard
                            icon={<HardDrive color="#f59e0b" />}
                            title="I/O Operations"
                            value={`${ioMetrics.read_count || 0} Reads`}
                            subtitle={`${ioMetrics.write_count || 0} Writes`}
                            tooltip="Number of disk read/write operations. Lower is better for performance."
                        />
                        <MetricCard
                            icon={<Cpu color="#10b981" />}
                            title="Hardware"
                            value={`${hardware?.cpu_brand || 'Unknown CPU'}`}
                            subtitle={`${hardware?.cpu_physical_cores || 0} cores (${hardware?.cpu_logical_cores || 0} threads) • ${formatBytes(hardware?.ram_total || 0)} RAM`}
                            tooltip="System hardware information detected during profiling."
                        />
                    </div>

                    {/* GC Metrics */}
                    {dynamic_analysis?.gc && <GCMetrics gcData={dynamic_analysis.gc} />}

                    {/* CPU Metrics */}
                    {dynamic_analysis?.cpu && <CPUMetrics cpuData={dynamic_analysis.cpu} timeData={timeMetrics} />}

                    <div className="divider" style={{ margin: '2rem 0', borderBottom: '1px solid #333' }}></div>
                </div>
            )}

            <h3>Static Analysis Results</h3>
            <div className="metrics-grid">
                <MetricCard
                    icon={<FileUp color="#00f2ff" />}
                    title="Total Files"
                    value={summary.total_files}
                    subtitle={`${summary.analyzed_files} analyzed`}
                />
                <MetricCard
                    icon={<Code color="#10b981" />}
                    title="Lines of Code"
                    value={totalLoc.toLocaleString()}
                    subtitle={`${totalSloc.toLocaleString()} SLOC`}
                    tooltip="Total Lines of Code (LOC) and Source Lines of Code (SLOC - excluding comments/blanks)."
                />
                <MetricCard
                    icon={<Zap color="#d946ef" />}
                    title="Avg Complexity"
                    value={(files.reduce((acc, f) => acc + getComplexity(f.complexity), 0) / (files.length || 1)).toFixed(1)}
                    tooltip="Average Cyclomatic Complexity across all analyzed files."
                />
                <MetricCard
                    icon={<HelpCircle color="#f59e0b" />}
                    title="Maintainability"
                    value={avgMaintainability.toFixed(1)}
                    subtitle={avgMaintainability > 85 ? "High" : avgMaintainability > 65 ? "Medium" : "Low"}
                    isGood={avgMaintainability > 65}
                    tooltip="Average Maintainability Index (0-100). Higher is better. >85 is good, <65 is hard to maintain."
                />
            </div>

            <div className="charts-grid">
                <div className="chart-card" style={{ gridColumn: '1 / -1' }}>
                    <h3>Top Complex Files</h3>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={complexityData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                                <XAxis dataKey="name" stroke="#888" />
                                <YAxis stroke="#888" />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#111', border: '1px solid #333' }}
                                    formatter={(value, name, props) => [value, `Complexity (${props.payload.path})`]}
                                />
                                <Bar dataKey="complexity" fill="#00f2ff" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            <div className="repo-visualizations">
                <div className="chart-card full-width">
                    <h3>Execution Flow Graph</h3>
                    <div className="chart-container" style={{ height: '600px' }}>
                        <ExecutionGraph files={files} />
                    </div>
                </div>
            </div>

            <div className="repo-files-list">
                <h3>Function Metrics</h3>
                <div className="table-container" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Function</th>
                                <th>File</th>
                                <th>Complexity</th>
                                <th>Big O</th>
                                <th>LOC</th>
                                <th>Line</th>
                            </tr>
                        </thead>
                        <tbody>
                            {allFunctions.map((func, index) => (
                                <tr key={index}>
                                    <td className="monospace">{func.name}</td>
                                    <td className="monospace" style={{ fontSize: '0.9em', color: '#888' }}>{func.file}</td>
                                    <td>
                                        <span className={`complexity-badge ${func.complexity > 5 ? 'high' : 'low'}`}>
                                            {func.complexity}
                                        </span>
                                    </td>
                                    <td className="monospace">{func.big_o}</td>
                                    <td className="monospace">{func.loc}</td>
                                    <td className="monospace">{func.lineno}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            <div className="repo-files-list">
                <h3>File Details</h3>
                <div className="table-container">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>File Path</th>
                                <th>Total Complexity</th>
                                <th>LOC / SLOC</th>
                                <th>Comments</th>
                                <th>Maintainability</th>
                            </tr>
                        </thead>
                        <tbody>
                            {files.map((file, index) => {
                                const totalComplexity = getComplexity(file.complexity);
                                return (
                                    <tr key={index}>
                                        <td className="monospace">{file.path}</td>
                                        <td>
                                            <span className={`complexity-badge ${totalComplexity > 10 ? 'high' : 'low'}`}>
                                                {totalComplexity}
                                            </span>
                                        </td>
                                        <td>{file.raw_metrics?.loc || 'N/A'} / {file.raw_metrics?.sloc || 'N/A'}</td>
                                        <td>{file.raw_metrics?.comments || 0}</td>
                                        <td>
                                            <span style={{
                                                color: (file.maintainability || 0) > 85 ? '#10b981' : (file.maintainability || 0) > 65 ? '#f59e0b' : '#ef4444',
                                                fontWeight: 'bold'
                                            }}>
                                                {(file.maintainability || 0).toFixed(1)}
                                            </span>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};


const Dashboard = ({ data }) => {
    if (!data) return null;

    // Check if this is a repo analysis result
    if (data.files && data.summary) {
        return <RepoDashboard data={data} />;
    }

    const handleExport = () => {
        const jsonString = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `profile_report_${Date.now()}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    };

    const { hardware, dynamic_analysis, static_analysis, scalene_analysis } = data;
    const timeMetrics = dynamic_analysis?.time || {};
    const memMetrics = dynamic_analysis?.memory || {};
    const ioMetrics = dynamic_analysis?.io || {};
    const complexity = static_analysis?.complexity || {};
    const callGraph = static_analysis?.call_graph || {};
    const hotspots = dynamic_analysis?.hotspots || [];

    // Prepare data for charts
    const complexityData = Object.entries(complexity).map(([name, value]) => ({
        name,
        complexity: value
    })).slice(0, 10); // Top 10

    const currentMem = Number(memMetrics.current_memory) || 0;
    const peakMem = Number(memMetrics.peak_memory) || 0;

    const memoryData = [
        { name: 'Current', value: currentMem },
        { name: 'Peak', value: peakMem },
    ].filter(item => item.value > 0);

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

    // Determine if metrics are "good" (low values are better for most metrics)
    const wallTime = Number(timeMetrics.wall_time) || 0;
    const cpuTime = Number(timeMetrics.cpu_time) || 0;

    return (
        <div className="dashboard">
            <div className="dashboard-header">
                <h2>Profiling Results</h2>
                <button className="export-btn" onClick={handleExport}>
                    <Download size={16} />
                    Export JSON
                </button>
            </div>

            {scalene_analysis && (
                <div style={{ marginBottom: '2rem' }}>
                    <ScaleneDashboard data={scalene_analysis} />
                </div>
            )}

            <div className="metrics-grid">
                <MetricCard
                    icon={<Clock color="#00f2ff" />}
                    title="Execution Time"
                    value={formatTime(wallTime)}
                    subtitle={`CPU: ${formatTime(cpuTime)}`}
                    tooltip="Total elapsed time (wall clock). Lower is better. CPU time shows actual processing time."
                    isGood={wallTime < 1}
                />
                <MetricCard
                    icon={<Zap color="#d946ef" />}
                    title="Peak Memory"
                    value={formatBytes(peakMem)}
                    subtitle={`Current: ${formatBytes(currentMem)}`}
                    tooltip="Maximum memory allocated during execution. Lower is better for efficiency."
                    isGood={peakMem < 10 * 1024 * 1024} // < 10MB is good
                />
                <MetricCard
                    icon={<HardDrive color="#f59e0b" />}
                    title="I/O Operations"
                    value={`${ioMetrics.read_count || 0} Reads`}
                    subtitle={`${ioMetrics.write_count || 0} Writes`}
                    tooltip="Number of disk read/write operations. Lower is better for performance."
                />
                <MetricCard
                    icon={<Cpu color="#10b981" />}
                    title="Hardware"
                    value={`${hardware?.cpu_brand || 'Unknown CPU'}`}
                    subtitle={`${hardware?.cpu_physical_cores || 0} cores (${hardware?.cpu_logical_cores || 0} threads) • ${formatBytes(hardware?.ram_total || 0)} RAM`}
                    tooltip="System hardware information detected during profiling. Click 'Hardware Specifications' below for full details."
                />
            </div>

            {/* Scalene Metrics Section (if available) */}
            {dynamic_analysis?.scalene && (
                <div className="scalene-metrics-section" style={{ marginTop: '2rem' }}>
                    <h3>High-Precision Profiling (Scalene)</h3>
                    <div className="metrics-grid">
                        <MetricCard
                            icon={<Cpu color="#3b82f6" />}
                            title="Python vs Native"
                            value={`${dynamic_analysis.scalene.cpu_breakdown.python.toFixed(1)}% Python`}
                            subtitle={`${dynamic_analysis.scalene.cpu_breakdown.native.toFixed(1)}% Native • ${dynamic_analysis.scalene.cpu_breakdown.system.toFixed(1)}% System`}
                            tooltip="Breakdown of execution time between Python code, Native C extensions, and System calls."
                        />
                        <MetricCard
                            icon={<Copy color="#f59e0b" />}
                            title="Memory Copy"
                            value={`${dynamic_analysis.scalene.memory_copy_mb_s.toFixed(2)} MB/s`}
                            subtitle="Copy Volume"
                            tooltip="Rate of memory copying. High values indicate inefficient data handling."
                            isGood={dynamic_analysis.scalene.memory_copy_mb_s < 100}
                        />
                        {dynamic_analysis.scalene.leaks.length > 0 && (
                            <MetricCard
                                icon={<AlertTriangle color="#ef4444" />}
                                title="Memory Leaks"
                                value={dynamic_analysis.scalene.leaks.length}
                                subtitle="Potential Leaks Detected"
                                tooltip="Number of lines with potential memory leaks detected by Scalene."
                                isGood={false}
                            />
                        )}
                    </div>

                    {/* CPU Breakdown Chart */}
                    <div className="charts-grid" style={{ marginTop: '1rem' }}>
                        <div className="chart-card">
                            <h3>CPU Time Breakdown</h3>
                            <div className="chart-container">
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie
                                            data={[
                                                { name: 'Python', value: dynamic_analysis.scalene.cpu_breakdown.python },
                                                { name: 'Native', value: dynamic_analysis.scalene.cpu_breakdown.native },
                                                { name: 'System', value: dynamic_analysis.scalene.cpu_breakdown.system }
                                            ].filter(d => d.value > 0)}
                                            cx="50%"
                                            cy="50%"
                                            innerRadius={60}
                                            outerRadius={80}
                                            paddingAngle={5}
                                            dataKey="value"
                                        >
                                            {[
                                                { name: 'Python', value: dynamic_analysis.scalene.cpu_breakdown.python },
                                                { name: 'Native', value: dynamic_analysis.scalene.cpu_breakdown.native },
                                                { name: 'System', value: dynamic_analysis.scalene.cpu_breakdown.system }
                                            ].filter(d => d.value > 0).map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={['#3b82f6', '#10b981', '#f59e0b'][index % 3]} />
                                            ))}
                                        </Pie>
                                        <Tooltip contentStyle={{ backgroundColor: '#111', border: '1px solid #333' }} />
                                        <Legend />
                                    </PieChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>

                    {/* Memory Leaks Table */}
                    {dynamic_analysis.scalene.leaks.length > 0 && (
                        <div style={{ marginTop: '1rem' }}>
                            <h3 style={{ color: '#ef4444' }}>Detected Memory Leaks</h3>
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
                                        {dynamic_analysis.scalene.leaks.map((leak, idx) => (
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
            )}

            {/* Hardware Details - Expandable */}
            <HardwareDetails hardware={hardware} />

            <div className="charts-grid">
                <div className="chart-container">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={complexityData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                            <XAxis dataKey="name" stroke="#888" />
                            <YAxis stroke="#888" />
                            <Tooltip contentStyle={{ backgroundColor: '#111', border: '1px solid #333' }} />
                            <Bar dataKey="complexity" fill="#00f2ff" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            <div className="chart-card">
                <h3>Memory Usage</h3>
                <div className="chart-container">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={memoryData}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                fill="#8884d8"
                                paddingAngle={5}
                                dataKey="value"
                            >
                                {memoryData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip contentStyle={{ backgroundColor: '#111', border: '1px solid #333' }} />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Call Graph Visualization */}
            <div className="call-graph-section">
                <h3>Execution Flow Graph</h3>
                <CallGraph callGraph={callGraph} complexity={complexity} data={data} />
            </div>

            {/* GC Metrics */}
            {dynamic_analysis?.gc && <GCMetrics gcData={dynamic_analysis.gc} />}

            {/* CPU Metrics */}
            {dynamic_analysis?.cpu && <CPUMetrics cpuData={dynamic_analysis.cpu} timeData={timeMetrics} />}

            {/* Hotspots Table */}
            {hotspots && hotspots.length > 0 && <HotspotsTable hotspots={hotspots} />}

            {/* Call Tree Viewer */}
            {dynamic_analysis?.call_tree && (
                <CallTreeViewer
                    callTree={dynamic_analysis.call_tree}
                    complexityMap={static_analysis?.complexity}
                    bigOMap={static_analysis?.big_o}
                />
            )}
        </div>
    );
};

export default Dashboard;

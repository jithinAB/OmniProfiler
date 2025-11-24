import React, { useState, useMemo } from 'react';
import { ArrowUpDown, Flame } from 'lucide-react';
import './HotspotsTable.css';

const HotspotsTable = ({ hotspots }) => {
    const [sortBy, setSortBy] = useState('cumulative');
    const [sortDirection, setSortDirection] = useState('desc');

    const parsedHotspots = useMemo(() => {
        if (!hotspots || hotspots.length === 0) return [];

        const data = [];
        hotspots.forEach(line => {
            // Parse cProfile output format: ncalls tottime percall cumtime percall filename:lineno(function)
            const match = line.match(/(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(.+):(\d+)\((.+)\)/);
            if (match) {
                data.push({
                    ncalls: parseInt(match[1]),
                    tottime: parseFloat(match[2]),
                    percall_tot: parseFloat(match[3]),
                    cumtime: parseFloat(match[4]),
                    percall_cum: parseFloat(match[5]),
                    filename: match[6],
                    lineno: parseInt(match[7]),
                    function: match[8]
                });
            }
        });
        return data;
    }, [hotspots]);

    const sortedData = useMemo(() => {
        const sorted = [...parsedHotspots];
        sorted.sort((a, b) => {
            let aVal = a[sortBy];
            let bVal = b[sortBy];

            if (sortBy === 'function' || sortBy === 'filename') {
                aVal = aVal.toLowerCase();
                bVal = bVal.toLowerCase();
                return sortDirection === 'asc'
                    ? aVal.localeCompare(bVal)
                    : bVal.localeCompare(aVal);
            }

            return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
        });
        return sorted;
    }, [parsedHotspots, sortBy, sortDirection]);

    const handleSort = (column) => {
        if (sortBy === column) {
            setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
        } else {
            setSortBy(column);
            setSortDirection('desc');
        }
    };

    const getHeatColor = (value, max) => {
        const intensity = value / max;
        if (intensity > 0.7) return '#ff0055';
        if (intensity > 0.4) return '#ffaa00';
        return '#00ff88';
    };

    if (parsedHotspots.length === 0) {
        return (
            <div className="hotspots-empty">
                <p>No hotspot data available</p>
            </div>
        );
    }

    const maxCumtime = Math.max(...parsedHotspots.map(h => h.cumtime));
    const maxTottime = Math.max(...parsedHotspots.map(h => h.tottime));

    return (
        <div className="hotspots-container">
            <div className="hotspots-header">
                <div className="header-icon">
                    <Flame color="#ff0055" size={20} />
                </div>
                <h4>Performance Hotspots</h4>
                <span className="hotspots-count" title="Functions consuming the most time. Red = high time consumption (needs optimization), Green = low time consumption (efficient).">{parsedHotspots.length} functions</span>
            </div>

            <div className="hotspots-table-wrapper">
                <table className="hotspots-table">
                    <thead>
                        <tr>
                            <th onClick={() => handleSort('function')} className="sortable" title="Function name and location in code">
                                <span>Function</span>
                                <ArrowUpDown size={14} />
                            </th>
                            <th onClick={() => handleSort('ncalls')} className="sortable" title="Number of times this function was called. Higher = more frequently called.">
                                <span>Calls</span>
                                <ArrowUpDown size={14} />
                            </th>
                            <th onClick={() => handleSort('tottime')} className="sortable" title="Total time spent in this function (excluding sub-functions). Lower is better. Red = hotspot needing optimization.">
                                <span>Total Time</span>
                                <ArrowUpDown size={14} />
                            </th>
                            <th onClick={() => handleSort('cumtime')} className="sortable" title="Cumulative time including all sub-functions called. Lower is better. This shows the total impact of calling this function.">
                                <span>Cumulative</span>
                                <ArrowUpDown size={14} />
                            </th>
                            <th onClick={() => handleSort('percall_cum')} className="sortable" title="Average time per call (cumulative / calls). Lower is better. Shows efficiency per invocation.">
                                <span>Per Call</span>
                                <ArrowUpDown size={14} />
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {sortedData.map((row, idx) => (
                            <tr key={idx}>
                                <td className="function-cell">
                                    <span className="function-name">{row.function}</span>
                                    <span className="function-location">
                                        {row.filename.split('/').pop()}:{row.lineno}
                                    </span>
                                </td>
                                <td className="number-cell">{row.ncalls.toLocaleString()}</td>
                                <td className="number-cell">
                                    <span style={{ color: getHeatColor(row.tottime, maxTottime) }}>
                                        {row.tottime.toFixed(4)}s
                                    </span>
                                </td>
                                <td className="number-cell">
                                    <span style={{ color: getHeatColor(row.cumtime, maxCumtime) }}>
                                        {row.cumtime.toFixed(4)}s
                                    </span>
                                    <div
                                        className="heat-bar"
                                        style={{
                                            width: `${(row.cumtime / maxCumtime) * 100}%`,
                                            backgroundColor: getHeatColor(row.cumtime, maxCumtime)
                                        }}
                                    />
                                </td>
                                <td className="number-cell">{row.percall_cum.toFixed(6)}s</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default HotspotsTable;

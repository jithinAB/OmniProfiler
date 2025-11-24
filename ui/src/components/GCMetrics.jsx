import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Trash2, HelpCircle } from 'lucide-react';
import './GCMetrics.css';

const GCMetrics = ({ gcData }) => {
    if (!gcData || !gcData.collections) {
        return null;
    }

    const { collections, objects_per_gen, thresholds, total_objects } = gcData;

    // Prepare data for chart
    const chartData = [
        { gen: 'Gen 0', collections: collections.gen0, objects: objects_per_gen.gen0, threshold: thresholds.gen0 },
        { gen: 'Gen 1', collections: collections.gen1, objects: objects_per_gen.gen1, threshold: thresholds.gen1 },
        { gen: 'Gen 2', collections: collections.gen2, objects: objects_per_gen.gen2, threshold: thresholds.gen2 }
    ];

    const totalCollections = collections.gen0 + collections.gen1 + collections.gen2;

    return (
        <div className="gc-metrics">
            <div className="gc-header">
                <Trash2 color="#ff0055" size={20} />
                <h4>Garbage Collector Activity</h4>
                <HelpCircle
                    size={14}
                    className="help-icon"
                    title="Garbage collection metrics show memory cleanup activity. Lower collection counts are better. Gen 0 = young objects, Gen 2 = old objects."
                />
            </div>

            <div className="gc-summary">
                <div className="gc-stat" title="Total number of garbage collection cycles. Lower is better - means less memory cleanup needed.">
                    <span className="gc-label">Total Collections</span>
                    <span className="gc-value">{totalCollections}</span>
                </div>
                <div className="gc-stat" title="Number of objects currently being tracked by the garbage collector. This is normal and expected.">
                    <span className="gc-label">Tracked Objects</span>
                    <span className="gc-value">{total_objects?.toLocaleString() || 'N/A'}</span>
                </div>
            </div>

            <div className="gc-chart">
                <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                        <XAxis dataKey="gen" stroke="#888" />
                        <YAxis stroke="#888" />
                        <Tooltip
                            contentStyle={{ backgroundColor: '#111', border: '1px solid #333' }}
                            labelStyle={{ color: '#00f2ff' }}
                        />
                        <Bar dataKey="collections" fill="#ff0055" name="Collections" />
                    </BarChart>
                </ResponsiveContainer>
            </div>

            <div className="gc-details">
                {chartData.map((gen, idx) => (
                    <div key={idx} className="gc-gen-info" title={
                        idx === 0 ? "Gen 0: Young objects, collected most frequently. High count is normal." :
                            idx === 1 ? "Gen 1: Medium-aged objects. Moderate collection count is normal." :
                                "Gen 2: Old, long-lived objects. Low collection count is best."
                    }>
                        <h5>{gen.gen}</h5>
                        <div className="gc-gen-stats">
                            <span title="Number of times this generation was collected. Gen 0 should be highest.">Collections: <strong>{gen.collections}</strong></span>
                            <span title="Current number of objects in this generation.">Objects: <strong>{gen.objects}</strong></span>
                            <span title="Threshold: when object count exceeds this, collection is triggered.">Threshold: <strong>{gen.threshold}</strong></span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default GCMetrics;

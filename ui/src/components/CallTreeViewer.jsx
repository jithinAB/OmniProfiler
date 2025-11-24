import React, { useState } from 'react';
import { ChevronRight, ChevronDown, Clock, Activity } from 'lucide-react';
import './CallTreeViewer.css';

const CallTreeViewer = ({ callTree, complexityMap = {}, bigOMap = {} }) => {
    const [expanded, setExpanded] = useState(new Set(['root']));

    // Parse pyinstrument call tree JSON into structured data
    const parseCallTree = (jsonString) => {
        if (!jsonString) return null;

        try {
            const data = JSON.parse(jsonString);

            // Recursive function to map pyinstrument JSON to our tree format
            const mapNode = (node) => {
                if (!node) return null;

                return {
                    name: node.function || 'root',
                    location: node.file_path_short ? `${node.file_path_short}:${node.line_no}` : '',
                    time: node.time,
                    id: `${node.function}-${Math.random()}`,
                    children: (node.children || []).map(mapNode).filter(n => n !== null)
                };
            };

            // pyinstrument JSON root might be the session object or the root node
            // usually it has a 'root_frame'
            const rootFrame = data.root_frame || data;
            return mapNode(rootFrame);
        } catch (e) {
            console.error("Failed to parse call tree JSON:", e);
            return null;
        }
    };

    const parsedTree = parseCallTree(callTree);

    const toggleNode = (nodeId) => {
        const newExpanded = new Set(expanded);
        if (newExpanded.has(nodeId)) {
            newExpanded.delete(nodeId);
        } else {
            newExpanded.add(nodeId);
        }
        setExpanded(newExpanded);
    };

    const getComplexityColor = (cc) => {
        if (!cc) return '#888';
        if (cc <= 5) return '#00ff88'; // Low complexity - Green
        if (cc <= 10) return '#ffaa00'; // Medium complexity - Orange
        return '#ff0055'; // High complexity - Red
    };

    const lookupComplexity = (name, map) => {
        if (!map) return null;
        // 1. Exact match
        if (map[name]) return map[name];
        // 2. Class method match (e.g. "MyClass.method" matches "method")
        // We look for a key that ends with ".name"
        const key = Object.keys(map).find(k => k.endsWith(`.${name}`));
        return key ? map[key] : null;
    };

    const renderNode = (node, depth = 0) => {
        const hasChildren = node.children && node.children.length > 0;
        const isExpanded = expanded.has(node.id);
        const timeColor = node.time > 0.01 ? '#ff0055' : node.time > 0.001 ? '#ffaa00' : '#00ff88';

        // Get complexity metrics with fuzzy lookup
        const cc = lookupComplexity(node.name, complexityMap);
        const bigO = lookupComplexity(node.name, bigOMap);
        const ccColor = getComplexityColor(cc);

        return (
            <div key={node.id} className="tree-node">
                <div
                    className="tree-node-content"
                    style={{ paddingLeft: `${depth * 20 + 8}px` }}
                >
                    {hasChildren && (
                        <button
                            className="expand-btn"
                            onClick={() => toggleNode(node.id)}
                        >
                            {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                        </button>
                    )}
                    {!hasChildren && <span className="leaf-spacer" />}

                    <div className="node-info">
                        <span className="node-name">{node.name}</span>
                        {node.location && (
                            <span className="node-location">{node.location}</span>
                        )}

                        {/* Complexity Badges */}
                        {(cc || bigO) && (
                            <div className="complexity-badges">
                                {bigO && (
                                    <span className="badge big-o" title="Estimated Big O Complexity">
                                        {bigO}
                                    </span>
                                )}
                                {cc && (
                                    <span
                                        className="badge cc"
                                        style={{ borderColor: ccColor, color: ccColor }}
                                        title={`Cyclomatic Complexity: ${cc} (Lower is better)`}
                                    >
                                        CC: {cc}
                                    </span>
                                )}
                            </div>
                        )}
                    </div>

                    <span className="node-time" style={{ color: timeColor }}>
                        {node.time > 0 ? `${node.time.toFixed(3)}s` : ''}
                    </span>
                </div>

                {hasChildren && isExpanded && (
                    <div className="tree-children">
                        {node.children.map(child => renderNode(child, depth + 1))}
                    </div>
                )}
            </div>
        );
    };

    if (!parsedTree) {
        return (
            <div className="call-tree-viewer">
                <div className="tree-header">
                    <Activity color="#00f2ff" size={20} />
                    <h4>Call Tree</h4>
                </div>
                <div className="tree-empty">
                    <p>No call tree data available</p>
                </div>
            </div>
        );
    }

    return (
        <div className="call-tree-viewer">
            <div className="tree-header">
                <Activity color="#00f2ff" size={20} />
                <h4>Execution Call Tree</h4>
                <div className="tree-legend">
                    <span className="legend-item">
                        <span className="legend-dot" style={{ backgroundColor: '#00ff88' }} />
                        Simple
                    </span>
                    <span className="legend-item">
                        <span className="legend-dot" style={{ backgroundColor: '#ffaa00' }} />
                        Moderate
                    </span>
                    <span className="legend-item">
                        <span className="legend-dot" style={{ backgroundColor: '#ff0055' }} />
                        Complex
                    </span>
                </div>
            </div>

            <div className="tree-content">
                {parsedTree.children.map(node => renderNode(node, 0))}
            </div>
        </div>
    );
};

export default CallTreeViewer;

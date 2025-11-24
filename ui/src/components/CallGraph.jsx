import React, { useMemo, useState } from 'react';
import ReactFlow, {
    Background,
    Controls,
    MiniMap,
    useNodesState,
    useEdgesState
} from 'reactflow';
import 'reactflow/dist/style.css';
import FunctionDetailPanel from './FunctionDetailPanel';
import './CallGraph.css';

const CallGraph = ({ callGraph, complexity, data }) => {
    const [selectedFunction, setSelectedFunction] = useState(null);

    // Transform call graph data to ReactFlow format
    const { nodes: initialNodes, edges: initialEdges } = useMemo(() => {
        if (!callGraph || Object.keys(callGraph).length === 0) {
            return { nodes: [], edges: [] };
        }

        const nodes = [];
        const edges = [];
        const addedNodes = new Set();
        let nodeY = 0;

        // Helper to get complexity level for coloring
        const getComplexityLevel = (funcName) => {
            const c = complexity?.[funcName] || 0;
            if (c <= 5) return 'low';
            if (c <= 10) return 'medium';
            return 'high';
        };

        // Create nodes and edges
        Object.entries(callGraph).forEach(([source, targets], idx) => {
            // Add source node if not already added
            if (!addedNodes.has(source)) {
                nodes.push({
                    id: source,
                    data: {
                        label: source,
                        complexity: complexity?.[source] || 0,
                        level: getComplexityLevel(source)
                    },
                    position: { x: 250, y: nodeY },
                    type: 'default',
                    className: `node-${getComplexityLevel(source)}`
                });
                addedNodes.add(source);
                nodeY += 100;
            }

            // Add target nodes and edges
            targets.forEach((target, targetIdx) => {
                if (!addedNodes.has(target)) {
                    nodes.push({
                        id: target,
                        data: {
                            label: target,
                            complexity: complexity?.[target] || 0,
                            level: getComplexityLevel(target)
                        },
                        position: { x: 500 + (targetIdx * 150), y: nodeY },
                        type: 'default',
                        className: `node-${getComplexityLevel(target)}`
                    });
                    addedNodes.add(target);
                }

                // Create edge
                edges.push({
                    id: `${source}-${target}-${targetIdx}`,
                    source: source,
                    target: target,
                    animated: true,
                    style: { stroke: '#00ffff', strokeWidth: 2 }
                });
            });
        });

        return { nodes, edges };
    }, [callGraph, complexity]);

    const [nodes, , onNodesChange] = useNodesState(initialNodes);
    const [edges, , onEdgesChange] = useEdgesState(initialEdges);

    const onNodeClick = (event, node) => {
        setSelectedFunction(node.id);
    };

    if (!callGraph || Object.keys(callGraph).length === 0) {
        return (
            <div className="call-graph-empty">
                <p>No call graph data available</p>
            </div>
        );
    }

    return (
        <>
            <div className="call-graph-container">
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onNodeClick={onNodeClick}
                    fitView
                    attributionPosition="bottom-left"
                >
                    <Background color="#1a1a2e" gap={16} />
                    <Controls />
                    <MiniMap
                        nodeColor={(node) => {
                            if (node.className?.includes('low')) return '#00ff88';
                            if (node.className?.includes('medium')) return '#ffaa00';
                            return '#ff0055';
                        }}
                        maskColor="rgba(0, 255, 255, 0.1)"
                    />
                </ReactFlow>
            </div>

            {selectedFunction && (
                <FunctionDetailPanel
                    functionName={selectedFunction}
                    data={data}
                    onClose={() => setSelectedFunction(null)}
                />
            )}
        </>
    );
};

export default CallGraph;

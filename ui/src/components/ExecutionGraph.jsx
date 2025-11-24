import React, { useMemo } from 'react';
import ReactFlow, {
    Background,
    Controls,
    MiniMap,
    Position,
    MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';
import './ExecutionGraph.css';

const ExecutionGraph = ({ files }) => {
    const { nodes, edges } = useMemo(() => {
        const nodes = [];
        const edges = [];
        const functionNodeMap = new Map(); // Map of "file:function" -> node id

        // Color palette for file groups
        const fileColors = [
            '#00f2ff', '#d946ef', '#f59e0b', '#10b981',
            '#ec4899', '#8b5cf6', '#06b6d4'
        ];

        let nodeId = 0;
        let yOffset = 0;

        // Create nodes for each file and its functions
        files.forEach((file, fileIndex) => {
            const fileColor = fileColors[fileIndex % fileColors.length];
            const fileName = file.path.split('/').pop();
            const filePath = file.path;

            // Create file header node
            const fileNodeId = `file-${nodeId++}`;
            nodes.push({
                id: fileNodeId,
                type: 'group',
                data: {
                    label: fileName,
                    path: filePath
                },
                position: { x: 50, y: yOffset },
                style: {
                    backgroundColor: 'rgba(17, 17, 17, 0.95)',
                    border: `2px solid ${fileColor}`,
                    borderRadius: '12px',
                    padding: '10px',
                    width: 300,
                    minHeight: 100
                },
                className: 'file-node'
            });

            let funcYOffset = 50; // Start below file header

            // Create function nodes within this file
            if (file.complexity) {
                Object.entries(file.complexity).forEach(([funcName, details]) => {
                    const complexity = typeof details === 'number' ? details : details.complexity;
                    const funcNodeId = `func-${nodeId++}`;
                    const funcKey = `${filePath}:${funcName}`;

                    functionNodeMap.set(funcKey, funcNodeId);

                    nodes.push({
                        id: funcNodeId,
                        parentNode: fileNodeId,
                        extent: 'parent',
                        data: {
                            label: funcName,
                            complexity: complexity,
                            big_o: file.big_o?.[funcName] || 'N/A',
                            loc: typeof details === 'object' ? details.loc : 'N/A'
                        },
                        position: { x: 10, y: funcYOffset },
                        targetPosition: Position.Left,
                        sourcePosition: Position.Right,
                        style: {
                            backgroundColor: complexity > 5 ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)',
                            border: `1px solid ${complexity > 5 ? '#ef4444' : '#10b981'}`,
                            borderRadius: '8px',
                            padding: '8px 12px',
                            fontSize: '12px',
                            color: '#fff',
                            width: 260
                        },
                        className: 'function-node'
                    });

                    funcYOffset += 70;
                });
            }

            yOffset += Math.max(funcYOffset + 30, 150);
        });

        // Create edges based on call graph
        files.forEach(file => {
            if (file.call_graph) {
                Object.entries(file.call_graph).forEach(([caller, callees]) => {
                    const sourceKey = `${file.path}:${caller}`;
                    const sourceNodeId = functionNodeMap.get(sourceKey);

                    if (!sourceNodeId) return;

                    callees.forEach(callee => {
                        // Try to find callee in the same file first
                        let targetKey = `${file.path}:${callee}`;
                        let targetNodeId = functionNodeMap.get(targetKey);

                        // If not found, search in other files
                        if (!targetNodeId) {
                            for (const [key, id] of functionNodeMap.entries()) {
                                if (key.endsWith(`:${callee}`)) {
                                    targetNodeId = id;
                                    break;
                                }
                            }
                        }

                        if (targetNodeId && sourceNodeId !== targetNodeId) {
                            edges.push({
                                id: `edge-${sourceNodeId}-${targetNodeId}`,
                                source: sourceNodeId,
                                target: targetNodeId,
                                type: 'smoothstep',
                                animated: true,
                                style: { stroke: '#555', strokeWidth: 2 },
                                markerEnd: {
                                    type: MarkerType.ArrowClosed,
                                    color: '#555',
                                    width: 20,
                                    height: 20
                                }
                            });
                        }
                    });
                });
            }
        });

        return { nodes, edges };
    }, [files]);

    if (nodes.length === 0) {
        return (
            <div style={{
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#888'
            }}>
                No functions found to visualize
            </div>
        );
    }

    return (
        <div style={{ height: '100%', width: '100%' }}>
            <ReactFlow
                nodes={nodes}
                edges={edges}
                fitView
                attributionPosition="bottom-right"
                minZoom={0.1}
                maxZoom={1.5}
                defaultEdgeOptions={{
                    type: 'smoothstep',
                    animated: true
                }}
            >
                <Background color="#333" gap={16} />
                <Controls />
                <MiniMap
                    nodeColor={(node) => {
                        if (node.type === 'group') return '#00f2ff';
                        return node.data.complexity > 5 ? '#ef4444' : '#10b981';
                    }}
                    maskColor="rgba(0, 0, 0, 0.8)"
                />
            </ReactFlow>
        </div>
    );
};

export default ExecutionGraph;

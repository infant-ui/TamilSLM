import React, { useMemo, useEffect } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Panel
} from 'reactflow';
import 'reactflow/dist/style.css';
import dagre from 'dagre';

const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

const nodeWidth = 172;
const nodeHeight = 36;

const getLayoutedElements = (nodes, edges, direction = 'TB') => {
  const isHorizontal = direction === 'LR';
  dagreGraph.setGraph({ rankdir: direction });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      ...node,
      targetPosition: isHorizontal ? 'left' : 'top',
      sourcePosition: isHorizontal ? 'right' : 'bottom',
      position: {
        x: nodeWithPosition.x - nodeWidth / 2,
        y: nodeWithPosition.y - nodeHeight / 2,
      },
    };
  });

  return { nodes: layoutedNodes, edges };
};

export default function MindmapGraph({ data }) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    if (data && data.nodes && data.edges) {
      const formattedNodes = data.nodes.map((n) => ({
        id: String(n.id),
        data: { label: n.label || n.id },
        position: { x: 0, y: 0 },
        style: { 
          background: 'var(--card-bg)', 
          color: 'var(--text-color)',
          border: '1px solid var(--border)',
          borderRadius: '8px',
          padding: '10px',
          fontSize: '14px',
          fontWeight: '500'
        }
      }));

      const formattedEdges = data.edges.map((e) => ({
        id: String(e.id),
        source: String(e.source),
        target: String(e.target),
        label: e.label || '',
        animated: true,
        style: { stroke: 'var(--cyan)', strokeWidth: 2 }
      }));

      const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
        formattedNodes,
        formattedEdges
      );

      setNodes(layoutedNodes);
      setEdges(layoutedEdges);
    }
  }, [data, setNodes, setEdges]);

  if (!data) return null;

  return (
    <div style={{ width: '100%', height: '500px', background: 'var(--bg-color)', borderRadius: '12px', overflow: 'hidden', border: '1px solid var(--border)' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Background color="var(--border)" gap={16} />
        <Controls />
        <MiniMap nodeColor="var(--cyan)" maskColor="rgba(0,0,0,0.1)" />
        <Panel position="top-right" style={{ background: 'var(--card-bg)', padding: '5px 10px', borderRadius: '5px', border: '1px solid var(--border)', fontSize: '12px' }}>
          Interactive Map
        </Panel>
      </ReactFlow>
    </div>
  );
}

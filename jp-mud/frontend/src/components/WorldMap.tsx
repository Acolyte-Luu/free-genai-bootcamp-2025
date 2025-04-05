import React, { useState, useEffect, useMemo, useCallback } from 'react';
// import { Direction } from '../types'; // Temporarily remove this import
// import 'aframe'; // No longer needed
// import { Simulation, forceSimulation, forceManyBody, forceLink, forceCenter } from 'd3-force'; // No longer needed
import ReactFlow, { MiniMap, Controls, Background, Node, Edge, Position } from 'reactflow';
import 'reactflow/dist/style.css'; // Import React Flow styles
import LocationNode from './LocationNode'; // Import the custom node

interface LocationData {
  name: string;
  japanese_name?: string;
  characterCount: number;
  itemCount: number;
  visited: boolean;
  isCurrent: boolean;
}

// Replace old NodeObject interface
// interface NodeObject {
//   id: string;
//   name: string;
//   japanese_name?: string;
//   visited: boolean;
//   isCurrent: boolean;
//   hidden?: boolean;
//   x?: number;
//   y?: number;
//   characterCount?: number; 
//   itemCount?: number;      
// }

// Replace old GraphData interface
// interface GraphData {
//   nodes: NodeObject[];
//   links: LinkObject[];
// }

// Replace old LinkObject interface
// interface LinkObject {
//   source: string;
//   target: string;
//   direction?: string; 
// }

interface WorldMapProps {
  worldData: any;
  currentLocation: string;
  visitedLocations: string[];
  className?: string;
}

const WorldMap: React.FC<WorldMapProps> = ({ 
  worldData, 
  currentLocation, 
  visitedLocations = [],
  className = ''
}) => {
  // Remove state related to react-force-graph loading and fallback
  // const [ForceGraph2DComponent, setForceGraph2DComponent] = useState<any>(null);
  // const [fallbackView, setFallbackView] = useState<boolean>(false);
  
  const [nodes, setNodes] = useState<Node<LocationData>[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  // Remove useEffect hooks related to react-force-graph loading and fallback timeout
  // useEffect(() => { ... }); 
  // useEffect(() => { ... }); 

  // Recalculate nodes and edges when world data changes
  useEffect(() => {
    if (!worldData || !worldData.locations) {
      setNodes([]);
      setEdges([]);
      return;
    }

    const initialNodes: Node<LocationData>[] = [];
    const initialEdges: Edge[] = [];
    const nodeMap = new Map<string, Node<LocationData>>();
    const edgeSet = new Set<string>(); // To prevent duplicate edges

    // Create nodes
    Object.entries(worldData.locations).forEach(([id, location]: [string, any], index) => {
      if (!location) return; // Skip if location data is invalid
      
      const isHidden = location.hidden || false;
      const visited = visitedLocations.includes(id);

      // Only add node if not hidden or if visited
      if (!isHidden || visited) {
        const node: Node<LocationData> = {
          id,
          type: 'locationNode', // Use custom node type
          position: { x: (index % 5) * 200, y: Math.floor(index / 5) * 150 }, // Basic grid layout
          data: {
            name: location.name || `Location ${id}`,
            japanese_name: location.japanese_name,
            characterCount: Array.isArray(location.characters) ? location.characters.length : 0,
            itemCount: Array.isArray(location.items) ? location.items.length : 0,
            visited: visited,
            isCurrent: id === currentLocation,
          },
          sourcePosition: Position.Right,
          targetPosition: Position.Left,
        };
        initialNodes.push(node);
        nodeMap.set(id, node);
      }
    });

    // Create edges
    initialNodes.forEach(node => {
      const sourceId = node.id;
      const location = worldData.locations[sourceId];

      if (location && location.connections) {
        Object.entries(location.connections).forEach(([direction, targetId]: [string, any]) => {
          // Ensure target node exists in our processed nodes
          if (nodeMap.has(targetId)) {
            const edgeIdForward = `${sourceId}-${targetId}`;
            const edgeIdBackward = `${targetId}-${sourceId}`;

            // Add edge only if it (or its reverse) hasn't been added
            if (!edgeSet.has(edgeIdForward) && !edgeSet.has(edgeIdBackward)) {
              initialEdges.push({
                id: edgeIdForward,
                source: sourceId,
                target: targetId,
                // label: direction, // Optional: label edges with direction
                animated: sourceId === currentLocation || targetId === currentLocation, // Animate edges connected to current location
                style: { strokeWidth: 2 },
              });
              edgeSet.add(edgeIdForward);
            }
          }
        });
      }
    });

    setNodes(initialNodes);
    setEdges(initialEdges);

  }, [worldData, currentLocation, visitedLocations]);

  // Remove old graphData calculation
  // const graphData = useMemo(() => { ... });
  
  // Remove old height calculation and fallback view rendering
  // const graphHeight = Math.max(500, Math.min(800, graphData.nodes.length * 50));
  // const renderFallbackView = () => { ... };

  // Define node types if we create custom nodes later
  const nodeTypes = useMemo(() => ({ locationNode: LocationNode }), []);

  return (
    <div className={`world-map border border-gray-300 dark:border-gray-700 rounded-md overflow-hidden shadow-md ${className}`} style={{ height: '700px' }}>
      <h3 className="px-4 py-2 bg-gray-100 dark:bg-gray-800 font-medium border-b border-gray-300 dark:border-gray-700">World Map (世界地図)</h3>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes} // Use the defined custom node type
        fitView // Automatically fit the view to the nodes
        attributionPosition="bottom-left"
      >
        <MiniMap />
        <Controls />
        <Background />
      </ReactFlow>
       {/* Remove old map legend */}
       {/* <div className="p-2 text-xs bg-gray-50 dark:bg-gray-800 border-t border-gray-300 dark:border-gray-700"> ... </div> */}
    </div>
  );
};

export default WorldMap; 
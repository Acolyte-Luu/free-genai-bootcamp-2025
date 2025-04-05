import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';

// Define the expected structure of the data passed to this node
// This should match the 'data' object created in WorldMap.tsx
interface LocationNodeData {
  name: string;
  japanese_name?: string;
  characterCount: number;
  itemCount: number;
  visited: boolean;
  isCurrent: boolean;
}

const LocationNode: React.FC<NodeProps<LocationNodeData>> = ({ data }) => {
  // Destructure with default values just in case
  const {
    name = 'Unknown',
    japanese_name = '',
    characterCount = 0,
    itemCount = 0,
    visited = false,
    isCurrent = false,
  } = data;

  const nodeStyle: React.CSSProperties = {
    background: isCurrent ? '#ff6b6b' : visited ? '#4dabf7' : '#f1f3f5',
    color: isCurrent || visited ? 'white' : '#212529', // Use white text for current/visited
    border: `1px solid ${
      isCurrent ? '#fa5252' : visited ? '#339af0' : '#ced4da'
    }`,
    padding: '10px 15px',
    borderRadius: '5px',
    minWidth: '160px',
    textAlign: 'center',
    fontSize: '12px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  };

  return (
    <div style={nodeStyle}>
      {/* Handles for connections (ensure these match source/target positions in WorldMap) */}
      <Handle
        type="target"
        position={Position.Left}
        style={{ background: '#555', width: '8px', height: '8px' }}
        isConnectable={true}
      />
      <Handle
        type="source"
        position={Position.Right}
        style={{ background: '#555', width: '8px', height: '8px' }}
        isConnectable={true}
      />

      {/* Content */}
      <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>{name}</div>
      {japanese_name && (
        <div
          style={{
            fontSize: '10px',
            marginBottom: '6px',
            opacity: 0.8,
          }}
        >
          {japanese_name}
        </div>
      )}

      {/* Icons */}
      {(characterCount > 0 || itemCount > 0) && ( // Only show icon container if there's something to show
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '8px',
            marginTop: '5px',
            borderTop: '1px solid rgba(0,0,0,0.05)', // Separator line
            paddingTop: '5px',
          }}
        >
          {characterCount > 0 && (
            <div
              title={`${characterCount} character(s)`}
              style={{ display: 'flex', alignItems: 'center', gap: '2px' }}
            >
              <span style={{ fontSize: '14px' }}>👤</span>
              <span style={{ fontSize: '11px' }}>{characterCount}</span>
            </div>
          )}
          {itemCount > 0 && (
            <div
              title={`${itemCount} item(s)`}
              style={{ display: 'flex', alignItems: 'center', gap: '2px' }}
            >
              <span style={{ fontSize: '14px' }}>📦</span>
              <span style={{ fontSize: '11px' }}>{itemCount}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default LocationNode;

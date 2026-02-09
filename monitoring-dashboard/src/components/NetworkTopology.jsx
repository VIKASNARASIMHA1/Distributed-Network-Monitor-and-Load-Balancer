import React, { useState, useEffect, useRef } from 'react';
import './NetworkTopology.css';

const NetworkTopology = ({ servers = [] }) => {
  const containerRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const [traffic, setTraffic] = useState([]);

  // Update dimensions on resize
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight,
        });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Generate traffic animation
  useEffect(() => {
    const interval = setInterval(() => {
      if (servers.length > 0) {
        const from = 'lb';
        const to = servers[Math.floor(Math.random() * servers.length)].name;
        const id = Date.now();
        
        setTraffic(prev => [...prev, { id, from, to }]);
        
        // Remove traffic after animation
        setTimeout(() => {
          setTraffic(prev => prev.filter(t => t.id !== id));
        }, 2000);
      }
    }, 500);

    return () => clearInterval(interval);
  }, [servers]);

  // Calculate node positions
  const calculatePositions = () => {
    const positions = {};
    const centerX = dimensions.width / 2;
    const centerY = dimensions.height / 2;
    
    // Load balancer position (center)
    positions.lb = { x: centerX, y: centerY, type: 'lb' };
    
    // Server positions (circle around center)
    servers.forEach((server, index) => {
      const angle = (index * 2 * Math.PI) / servers.length;
      const radius = Math.min(dimensions.width, dimensions.height) * 0.3;
      positions[server.name] = {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
        type: 'server',
        ...server,
      };
    });
    
    return positions;
  };

  const positions = calculatePositions();
  const nodes = Object.entries(positions);

  return (
    <div className="topology-container" ref={containerRef}>
      {/* Connections */}
      {nodes.map(([name, node]) => {
        if (node.type === 'server') {
          return (
            <div
              key={`conn-${name}`}
              className="connection"
              style={{
                left: positions.lb.x,
                top: positions.lb.y,
                width: Math.sqrt(
                  Math.pow(node.x - positions.lb.x, 2) + 
                  Math.pow(node.y - positions.lb.y, 2)
                ),
                transform: `rotate(${Math.atan2(
                  node.y - positions.lb.y,
                  node.x - positions.lb.x
                )}rad)`,
              }}
            />
          );
        }
        return null;
      })}

      {/* Traffic animation */}
      {traffic.map(({ id, from, to }) => {
        if (!positions[from] || !positions[to]) return null;
        
        const distance = Math.sqrt(
          Math.pow(positions[to].x - positions[from].x, 2) + 
          Math.pow(positions[to].y - positions[from].y, 2)
        );
        const angle = Math.atan2(
          positions[to].y - positions[from].y,
          positions[to].x - positions[from].x
        );
        
        return (
          <div
            key={id}
            className="traffic-flow"
            style={{
              left: positions[from].x,
              top: positions[from].y,
              '--distance': `${distance}px`,
              transform: `rotate(${angle}rad)`,
            }}
          />
        );
      })}

      {/* Nodes */}
      {nodes.map(([name, node]) => (
        <div
          key={name}
          className={`node ${node.type} ${node.healthy === false ? 'unhealthy' : ''}`}
          style={{
            left: node.x - 30,
            top: node.y - 30,
            backgroundColor: node.type === 'lb' 
              ? 'rgba(147, 51, 234, 0.2)' 
              : node.healthy === false
                ? 'rgba(248, 113, 113, 0.2)'
                : 'rgba(59, 130, 246, 0.2)',
            borderColor: node.type === 'lb' 
              ? '#9333ea' 
              : node.healthy === false
                ? '#f87171'
                : '#3b82f6',
          }}
          title={`${name}\n${node.type === 'server' ? `Connections: ${node.connections || 0}\nCPU: ${node.cpu_usage || 0}%\nMemory: ${node.memory_usage || 0}%` : 'Load Balancer'}`}
        >
          {node.type === 'lb' ? 'LB' : name.split('-').pop()}
          {node.type === 'server' && node.healthy === false && (
            <div className="error-badge">!</div>
          )}
        </div>
      ))}

      {/* Legend */}
      <div className="topology-legend">
        <div className="legend-item">
          <div className="legend-color lb"></div>
          <span>Load Balancer</span>
        </div>
        <div className="legend-item">
          <div className="legend-color server healthy"></div>
          <span>Healthy Server</span>
        </div>
        <div className="legend-item">
          <div className="legend-color server unhealthy"></div>
          <span>Unhealthy Server</span>
        </div>
        <div className="legend-item">
          <div className="traffic-dot"></div>
          <span>Live Traffic</span>
        </div>
      </div>
    </div>
  );
};

export default NetworkTopology;
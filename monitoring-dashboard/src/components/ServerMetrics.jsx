import React, { useState, useEffect } from 'react';
import { 
  FiServer, 
  FiCpu, 
  FiHardDrive, 
  FiActivity,
  FiCheckCircle,
  FiXCircle,
  FiClock,
  FiUsers
} from 'react-icons/fi';
import './ServerMetrics.css';

const ServerMetrics = ({ servers = [] }) => {
  const [selectedServer, setSelectedServer] = useState(null);
  const [metricsHistory, setMetricsHistory] = useState({});

  // Update metrics history
  useEffect(() => {
    servers.forEach(server => {
      if (!server.name) return;
      
      setMetricsHistory(prev => {
        const history = prev[server.name] || [];
        const newEntry = {
          timestamp: Date.now(),
          cpu: server.cpu_usage || 0,
          memory: server.memory_usage || 0,
          connections: server.connections || 0,
        };
        
        const updatedHistory = [...history.slice(-19), newEntry];
        return {
          ...prev,
          [server.name]: updatedHistory,
        };
      });
    });
  }, [servers]);

  const getServerStatus = (server) => {
    if (server.healthy === false) return 'unhealthy';
    if (server.cpu_usage > 80 || server.memory_usage > 85) return 'warning';
    return 'healthy';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return '#4ade80';
      case 'warning': return '#fbbf24';
      case 'unhealthy': return '#f87171';
      default: return '#9ca3af';
    }
  };

  const formatUptime = (seconds) => {
    if (!seconds) return 'N/A';
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (days > 0) return `${days}d ${hours}h`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  const calculateTrend = (serverName, metric) => {
    const history = metricsHistory[serverName];
    if (!history || history.length < 2) return 0;
    
    const recent = history.slice(-2);
    const diff = recent[1][metric] - recent[0][metric];
    return diff;
  };

  if (servers.length === 0) {
    return (
      <div className="server-metrics-empty">
        <FiServer size={48} />
        <p>No servers available</p>
        <small>Start the server nodes to see metrics</small>
      </div>
    );
  }

  return (
    <div className="server-metrics">
      <div className="server-list">
        {servers.map(server => {
          const status = getServerStatus(server);
          const trendCpu = calculateTrend(server.name, 'cpu');
          const trendMemory = calculateTrend(server.name, 'memory');
          
          return (
            <div
              key={server.name || server.id}
              className={`server-card ${selectedServer?.name === server.name ? 'selected' : ''}`}
              onClick={() => setSelectedServer(server)}
            >
              <div className="server-header">
                <div className="server-title">
                  <div 
                    className="server-status-indicator"
                    style={{ backgroundColor: getStatusColor(status) }}
                  ></div>
                  <div className="server-name">
                    <FiServer size={14} />
                    <span>{server.name || `Server ${server.id}`}</span>
                  </div>
                </div>
                <div className="server-status">
                  {status === 'healthy' ? (
                    <FiCheckCircle color="#4ade80" />
                  ) : status === 'warning' ? (
                    <FiActivity color="#fbbf24" />
                  ) : (
                    <FiXCircle color="#f87171" />
                  )}
                  <span className={`status-text ${status}`}>
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </span>
                </div>
              </div>
              
              <div className="server-metrics-grid">
                <div className="metric-item">
                  <div className="metric-header">
                    <FiCpu size={12} />
                    <span>CPU</span>
                    {trendCpu !== 0 && (
                      <span className={`trend ${trendCpu > 0 ? 'up' : 'down'}`}>
                        {trendCpu > 0 ? '↗' : '↘'}
                      </span>
                    )}
                  </div>
                  <div className="metric-value">
                    {server.cpu_usage?.toFixed(1) || '0'}%
                  </div>
                  <div className="metric-bar">
                    <div 
                      className="metric-bar-fill"
                      style={{
                        width: `${Math.min(server.cpu_usage || 0, 100)}%`,
                        backgroundColor: getStatusColor(
                          (server.cpu_usage || 0) > 80 ? 'warning' : 'healthy'
                        ),
                      }}
                    ></div>
                  </div>
                </div>
                
                <div className="metric-item">
                  <div className="metric-header">
                    <FiHardDrive size={12} />
                    <span>Memory</span>
                    {trendMemory !== 0 && (
                      <span className={`trend ${trendMemory > 0 ? 'up' : 'down'}`}>
                        {trendMemory > 0 ? '↗' : '↘'}
                      </span>
                    )}
                  </div>
                  <div className="metric-value">
                    {server.memory_usage?.toFixed(1) || '0'}%
                  </div>
                  <div className="metric-bar">
                    <div 
                      className="metric-bar-fill"
                      style={{
                        width: `${Math.min(server.memory_usage || 0, 100)}%`,
                        backgroundColor: getStatusColor(
                          (server.memory_usage || 0) > 85 ? 'warning' : 'healthy'
                        ),
                      }}
                    ></div>
                  </div>
                </div>
                
                <div className="metric-item">
                  <div className="metric-header">
                    <FiUsers size={12} />
                    <span>Connections</span>
                  </div>
                  <div className="metric-value">
                    {server.connections || 0}
                  </div>
                </div>
                
                <div className="metric-item">
                  <div className="metric-header">
                    <FiClock size={12} />
                    <span>Uptime</span>
                  </div>
                  <div className="metric-value">
                    {formatUptime(server.uptime)}
                  </div>
                </div>
              </div>
              
              <div className="server-footer">
                <div className="response-time">
                  <span>Response:</span>
                  <span className="value">
                    {server.avg_response_time?.toFixed(1) || '0'}ms
                  </span>
                </div>
                <div className="requests-count">
                  <span>Requests:</span>
                  <span className="value">
                    {server.total_requests || 0}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      {selectedServer && (
        <div className="server-details">
          <div className="details-header">
            <h3>{selectedServer.name} Details</h3>
            <button 
              className="close-details"
              onClick={() => setSelectedServer(null)}
            >
              ×
            </button>
          </div>
          
          <div className="details-grid">
            <div className="detail-item">
              <label>Hostname</label>
              <span>{selectedServer.hostname || 'N/A'}</span>
            </div>
            <div className="detail-item">
              <label>Last Check</label>
              <span>
                {selectedServer.last_check 
                  ? new Date(selectedServer.last_check).toLocaleTimeString()
                  : 'N/A'}
              </span>
            </div>
            <div className="detail-item">
              <label>Response Time Trend</label>
              <span>
                {calculateTrend(selectedServer.name, 'avg_response_time')?.toFixed(1) || '0'}ms
              </span>
            </div>
            <div className="detail-item">
              <label>Weight</label>
              <span>{selectedServer.weight || 1}</span>
            </div>
          </div>
          
          {metricsHistory[selectedServer.name] && (
            <div className="metrics-chart">
              <h4>CPU Usage History</h4>
              <div className="chart-container">
                {metricsHistory[selectedServer.name].map((entry, index, arr) => {
                  const prevEntry = arr[index - 1];
                  if (!prevEntry) return null;
                  
                  return (
                    <div
                      key={entry.timestamp}
                      className="chart-line"
                      style={{
                        height: `${Math.min(entry.cpu, 100)}%`,
                        left: `${(index / (arr.length - 1)) * 100}%`,
                      }}
                      title={`CPU: ${entry.cpu.toFixed(1)}% at ${new Date(entry.timestamp).toLocaleTimeString()}`}
                    ></div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ServerMetrics;
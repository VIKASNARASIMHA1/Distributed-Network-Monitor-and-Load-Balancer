import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import NetworkTopology from './components/NetworkTopology';
import ServerMetrics from './components/ServerMetrics';
import TrafficFlow from './components/TrafficFlow';
import LoadBalancerStats from './components/LoadBalancerStats';

function App() {
  const [stats, setStats] = useState(null);
  const [servers, setServers] = useState([]);
  const [algorithm, setAlgorithm] = useState('round_robin');
  const [trafficData, setTrafficData] = useState([]);
  const [isSimulating, setIsSimulating] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    // Fetch initial data
    fetchStats();
    fetchServers();

    // Set up WebSocket for real-time updates
    const ws = new WebSocket('ws://localhost:5000/ws');
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'stats_update') {
        setStats(data.payload);
      } else if (data.type === 'traffic_update') {
        setTrafficData(prev => [...prev.slice(-50), data.payload]);
      }
    };

    // Poll for updates every 5 seconds
    const interval = setInterval(fetchStats, 5000);

    return () => {
      clearInterval(interval);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:5000/stats');
      const data = await response.json();
      setStats(data);
      setServers(data.server_stats || []);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchServers = async () => {
    try {
      const response = await fetch('http://localhost:5000/servers');
      const data = await response.json();
      setServers(data.servers || []);
    } catch (error) {
      console.error('Error fetching servers:', error);
    }
  };

  const changeAlgorithm = async (newAlgo) => {
    try {
      const response = await fetch(`http://localhost:5000/algorithm/${newAlgo}`);
      const data = await response.json();
      if (data.success) {
        setAlgorithm(newAlgo);
        fetchStats();
      }
    } catch (error) {
      console.error('Error changing algorithm:', error);
    }
  };

  const sendTestRequest = async () => {
    try {
      const response = await fetch('http://localhost:5000/request');
      const data = await response.json();
      console.log('Request result:', data);
      fetchStats(); // Refresh stats
    } catch (error) {
      console.error('Error sending request:', error);
    }
  };

  const startTrafficSimulation = async () => {
    setIsSimulating(true);
    // Simulate traffic by sending multiple requests
    for (let i = 0; i < 10; i++) {
      await sendTestRequest();
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    setIsSimulating(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🌐 Distributed Network Monitor</h1>
        <div className="status-indicator">
          <span className={`status-dot ${stats ? 'online' : 'offline'}`}></span>
          {stats ? 'System Online' : 'System Offline'}
        </div>
      </header>

      <div className="main-content">
        <div className="control-panel">
          <h2>Controls</h2>
          <div className="algorithm-selector">
            <label>Load Balancing Algorithm:</label>
            <select 
              value={algorithm} 
              onChange={(e) => changeAlgorithm(e.target.value)}
            >
              <option value="round_robin">Round Robin</option>
              <option value="least_connections">Least Connections</option>
              <option value="least_response_time">Least Response Time</option>
              <option value="weighted_round_robin">Weighted Round Robin</option>
              <option value="ip_hash">IP Hash</option>
            </select>
          </div>
          
          <div className="button-group">
            <button onClick={sendTestRequest} disabled={isSimulating}>
              Send Test Request
            </button>
            <button onClick={startTrafficSimulation} disabled={isSimulating}>
              {isSimulating ? 'Simulating...' : 'Simulate Traffic'}
            </button>
            <button onClick={fetchStats}>
              Refresh Stats
            </button>
          </div>
        </div>

        <div className="dashboard-grid">
          <div className="card full-width">
            <NetworkTopology servers={servers} />
          </div>

          <div className="card">
            <h2>Load Balancer Stats</h2>
            {stats && <LoadBalancerStats stats={stats} />}
          </div>

          <div className="card">
            <h2>Server Health</h2>
            <ServerMetrics servers={servers} />
          </div>

          <div className="card">
            <h2>Traffic Flow</h2>
            <TrafficFlow data={trafficData} />
          </div>

          <div className="card full-width">
            <h2>Real-time Metrics</h2>
            {stats && (
              <div className="metrics-grid">
                <div className="metric">
                  <div className="metric-label">Total Requests</div>
                  <div className="metric-value">{stats.total_requests}</div>
                </div>
                <div className="metric">
                  <div className="metric-label">Healthy Servers</div>
                  <div className="metric-value">
                    {stats.healthy_servers}/{stats.total_servers}
                  </div>
                </div>
                <div className="metric">
                  <div className="metric-label">Algorithm</div>
                  <div className="metric-value">{stats.algorithm}</div>
                </div>
                <div className="metric">
                  <div className="metric-label">Active Connections</div>
                  <div className="metric-value">
                    {servers.reduce((sum, s) => sum + s.connections, 0)}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
import React, { useState, useEffect, useRef } from 'react';
import { 
  FiTrendingUp, 
  FiTrendingDown, 
  FiActivity,
  FiPieChart,
  FiBarChart2
} from 'react-icons/fi';
import './TrafficFlow.css';

const TrafficFlow = ({ data = [] }) => {
  const [trafficData, setTrafficData] = useState([]);
  const [timeRange, setTimeRange] = useState('5m');
  const [selectedMetric, setSelectedMetric] = useState('requests');
  const chartRef = useRef(null);

  // Process incoming data
  useEffect(() => {
    if (data.length > 0) {
      const newEntry = data[data.length - 1];
      setTrafficData(prev => {
        const updated = [...prev, {
          timestamp: Date.now(),
          ...newEntry,
        }].slice(-100); // Keep last 100 entries
        
        return updated;
      });
    }
  }, [data]);

  // Simulate traffic if no data
  useEffect(() => {
    if (trafficData.length === 0) {
      const interval = setInterval(() => {
        const mockData = {
          requests: Math.floor(Math.random() * 100),
          bytes: Math.floor(Math.random() * 1000000),
          responseTime: Math.random() * 100 + 50,
          successRate: 95 + Math.random() * 5,
        };
        
        setTrafficData(prev => {
          const updated = [...prev, {
            timestamp: Date.now(),
            ...mockData,
          }].slice(-100);
          
          return updated;
        });
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [trafficData.length]);

  const calculateStats = () => {
    if (trafficData.length === 0) {
      return {
        totalRequests: 0,
        avgResponseTime: 0,
        successRate: 100,
        throughput: 0,
        peakRequests: 0,
        errorRate: 0,
      };
    }

    const recentData = trafficData.slice(-30); // Last 30 seconds
    const requests = recentData.map(d => d.requests || 0);
    const responseTimes = recentData.map(d => d.responseTime || 0);
    const successRates = recentData.map(d => d.successRate || 100);

    return {
      totalRequests: requests.reduce((a, b) => a + b, 0),
      avgResponseTime: responseTimes.length > 0 
        ? responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length 
        : 0,
      successRate: successRates.length > 0 
        ? successRates.reduce((a, b) => a + b, 0) / successRates.length 
        : 100,
      throughput: requests.length > 0 
        ? requests.reduce((a, b) => a + b, 0) / requests.length 
        : 0,
      peakRequests: Math.max(...requests, 0),
      errorRate: 100 - (successRates.length > 0 
        ? successRates.reduce((a, b) => a + b, 0) / successRates.length 
        : 100),
    };
  };

  const getProtocolDistribution = () => {
    // Mock protocol distribution
    return [
      { protocol: 'HTTP', percentage: 45, color: '#3b82f6' },
      { protocol: 'HTTPS', percentage: 30, color: '#10b981' },
      { protocol: 'WebSocket', percentage: 15, color: '#8b5cf6' },
      { protocol: 'API', percentage: 10, color: '#f59e0b' },
    ];
  };

  const getGeographicDistribution = () => {
    // Mock geographic distribution
    return [
      { region: 'North America', percentage: 40, color: '#3b82f6' },
      { region: 'Europe', percentage: 35, color: '#10b981' },
      { region: 'Asia', percentage: 20, color: '#8b5cf6' },
      { region: 'Other', percentage: 5, color: '#f59e0b' },
    ];
  };

  const stats = calculateStats();
  const protocolDistribution = getProtocolDistribution();
  const geoDistribution = getGeographicDistribution();

  const renderChart = () => {
    if (trafficData.length < 2) {
      return (
        <div className="chart-placeholder">
          <FiActivity size={48} />
          <p>Collecting traffic data...</p>
        </div>
      );
    }

    const chartData = trafficData.slice(-20); // Last 20 data points
    const maxValue = Math.max(...chartData.map(d => d[selectedMetric] || 0));
    const chartHeight = 200;

    return (
      <div className="line-chart" ref={chartRef}>
        {chartData.map((point, index) => {
          const value = point[selectedMetric] || 0;
          const percentage = maxValue > 0 ? (value / maxValue) * 100 : 0;
          const x = (index / (chartData.length - 1)) * 100;
          const y = chartHeight - (percentage / 100) * chartHeight;

          return (
            <React.Fragment key={index}>
              <div
                className="chart-point"
                style={{
                  left: `${x}%`,
                  bottom: `${(percentage / 100) * chartHeight}px`,
                  backgroundColor: selectedMetric === 'requests' 
                    ? '#3b82f6' 
                    : selectedMetric === 'responseTime'
                    ? '#10b981'
                    : '#8b5cf6',
                }}
                title={`${selectedMetric}: ${value.toFixed(1)}`}
              />
              
              {index > 0 && (
                <svg className="chart-line" style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}>
                  <line
                    x1={`${((index - 1) / (chartData.length - 1)) * 100}%`}
                    y1={chartHeight - ((chartData[index - 1][selectedMetric] || 0) / maxValue) * chartHeight}
                    x2={`${x}%`}
                    y2={y}
                    stroke={selectedMetric === 'requests' ? '#3b82f6' : selectedMetric === 'responseTime' ? '#10b981' : '#8b5cf6'}
                    strokeWidth="2"
                    strokeLinecap="round"
                  />
                </svg>
              )}
            </React.Fragment>
          );
        })}
        
        <div className="chart-grid">
          {[0, 25, 50, 75, 100].map(percent => (
            <div
              key={percent}
              className="grid-line"
              style={{ bottom: `${(percent / 100) * chartHeight}px` }}
            >
              <span className="grid-label">
                {Math.round((percent / 100) * maxValue)}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="traffic-flow">
      <div className="traffic-header">
        <h3>Traffic Analytics</h3>
        <div className="traffic-controls">
          <select 
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="time-range-select"
          >
            <option value="1m">Last 1 minute</option>
            <option value="5m">Last 5 minutes</option>
            <option value="15m">Last 15 minutes</option>
            <option value="1h">Last hour</option>
          </select>
          
          <div className="metric-selector">
            <button
              className={`metric-btn ${selectedMetric === 'requests' ? 'active' : ''}`}
              onClick={() => setSelectedMetric('requests')}
              title="Requests per second"
            >
              <FiTrendingUp />
              <span>Requests</span>
            </button>
            <button
              className={`metric-btn ${selectedMetric === 'responseTime' ? 'active' : ''}`}
              onClick={() => setSelectedMetric('responseTime')}
              title="Response time"
            >
              <FiActivity />
              <span>Response Time</span>
            </button>
            <button
              className={`metric-btn ${selectedMetric === 'successRate' ? 'active' : ''}`}
              onClick={() => setSelectedMetric('successRate')}
              title="Success rate"
            >
              <FiTrendingUp />
              <span>Success Rate</span>
            </button>
          </div>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-header">
            <FiTrendingUp />
            <span>Requests/sec</span>
          </div>
          <div className="stat-value">
            {stats.throughput.toFixed(1)}
          </div>
          <div className="stat-trend">
            <span className="trend-up">+12%</span>
            <span>from last period</span>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-header">
            <FiActivity />
            <span>Avg Response</span>
          </div>
          <div className="stat-value">
            {stats.avgResponseTime.toFixed(1)}ms
          </div>
          <div className="stat-trend">
            <span className="trend-down">-5%</span>
            <span>from last period</span>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-header">
            <FiTrendingUp />
            <span>Success Rate</span>
          </div>
          <div className="stat-value">
            {stats.successRate.toFixed(1)}%
          </div>
          <div className="stat-trend">
            <span className="trend-up">+0.5%</span>
            <span>from last period</span>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-header">
            <FiBarChart2 />
            <span>Peak Load</span>
          </div>
          <div className="stat-value">
            {stats.peakRequests}
          </div>
          <div className="stat-trend">
            <span className="trend-neutral">±0%</span>
            <span>from last period</span>
          </div>
        </div>
      </div>

      <div className="chart-container">
        <div className="chart-header">
          <h4>{selectedMetric.charAt(0).toUpperCase() + selectedMetric.slice(1)} Over Time</h4>
          <span className="chart-subtitle">
            Last {timeRange === '1m' ? 'minute' : timeRange === '5m' ? '5 minutes' : timeRange === '15m' ? '15 minutes' : 'hour'}
          </span>
        </div>
        {renderChart()}
      </div>

      <div className="distribution-grid">
        <div className="distribution-card">
          <div className="distribution-header">
            <FiPieChart />
            <h4>Protocol Distribution</h4>
          </div>
          <div className="distribution-chart">
            <div className="pie-chart">
              {protocolDistribution.reduce((acc, protocol, index) => {
                const prevPercentage = acc;
                const percentage = protocol.percentage;
                
                return (
                  <React.Fragment key={protocol.protocol}>
                    <div
                      className="pie-segment"
                      style={{
                        '--percentage': `${percentage}%`,
                        '--start': `${prevPercentage}%`,
                        '--color': protocol.color,
                      }}
                      title={`${protocol.protocol}: ${percentage}%`}
                    ></div>
                    {prevPercentage + percentage}
                  </React.Fragment>
                );
              }, 0)}
            </div>
            <div className="distribution-legend">
              {protocolDistribution.map(protocol => (
                <div key={protocol.protocol} className="legend-item">
                  <div 
                    className="legend-color" 
                    style={{ backgroundColor: protocol.color }}
                  ></div>
                  <span className="legend-label">{protocol.protocol}</span>
                  <span className="legend-value">{protocol.percentage}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="distribution-card">
          <div className="distribution-header">
            <FiPieChart />
            <h4>Geographic Distribution</h4>
          </div>
          <div className="distribution-bars">
            {geoDistribution.map(item => (
              <div key={item.region} className="bar-item">
                <div className="bar-label">
                  <span>{item.region}</span>
                  <span>{item.percentage}%</span>
                </div>
                <div className="bar-container">
                  <div
                    className="bar-fill"
                    style={{
                      width: `${item.percentage}%`,
                      backgroundColor: item.color,
                    }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="traffic-alerts">
        <h4>Recent Traffic Events</h4>
        <div className="alerts-list">
          <div className="alert-item info">
            <div className="alert-icon">i</div>
            <div className="alert-content">
              <strong>Traffic spike detected</strong>
              <small>2 minutes ago - Requests increased by 150%</small>
            </div>
          </div>
          <div className="alert-item warning">
            <div className="alert-icon">⚠</div>
            <div className="alert-content">
              <strong>High response times</strong>
              <small>5 minutes ago - Average response time above 200ms</small>
            </div>
          </div>
          <div className="alert-item success">
            <div className="alert-icon">✓</div>
            <div className="alert-content">
              <strong>Traffic normalized</strong>
              <small>10 minutes ago - System returned to normal load</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrafficFlow;
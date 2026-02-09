import React, { useState, useEffect } from 'react';
import { 
  FiSettings,
  FiServer,
  FiBarChart2,
  FiClock,
  FiTrendingUp,
  FiTrendingDown,
  FiUsers,
  FiActivity,
  FiCheckCircle,
  FiAlertCircle,
  FiRefreshCw
} from 'react-icons/fi';
import './LoadBalancerStats.css';

const LoadBalancerStats = ({ stats = {} }) => {
  const [algorithmHistory, setAlgorithmHistory] = useState([]);
  const [performanceMetrics, setPerformanceMetrics] = useState({
    requestsPerSecond: [],
    responseTimes: [],
    errorRates: [],
  });

  // Update algorithm history
  useEffect(() => {
    if (stats.algorithm) {
      setAlgorithmHistory(prev => {
        const newEntry = {
          algorithm: stats.algorithm,
          timestamp: Date.now(),
          healthyServers: stats.healthy_servers || 0,
          totalRequests: stats.total_requests || 0,
        };
        
        return [...prev.slice(-9), newEntry];
      });
    }
  }, [stats.algorithm]);

  // Update performance metrics
  useEffect(() => {
    const interval = setInterval(() => {
      const rps = Math.floor(Math.random() * 50) + 20;
      const responseTime = Math.random() * 50 + 50;
      const errorRate = Math.random() * 2;
      
      setPerformanceMetrics(prev => ({
        requestsPerSecond: [...prev.requestsPerSecond.slice(-29), rps],
        responseTimes: [...prev.responseTimes.slice(-29), responseTime],
        errorRates: [...prev.errorRates.slice(-29), errorRate],
      }));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const getAlgorithmDescription = (algorithm) => {
    const descriptions = {
      'round_robin': 'Distributes requests sequentially to each server in rotation',
      'least_connections': 'Sends requests to the server with the fewest active connections',
      'least_response_time': 'Routes to the server with the fastest response time',
      'weighted_round_robin': 'Considers server capacity with weighted distribution',
      'ip_hash': 'Consistent routing based on client IP address',
      'random': 'Randomly selects a server for each request',
    };
    
    return descriptions[algorithm] || 'Unknown algorithm';
  };

  const getAlgorithmColor = (algorithm) => {
    const colors = {
      'round_robin': '#3b82f6',
      'least_connections': '#10b981',
      'least_response_time': '#8b5cf6',
      'weighted_round_robin': '#f59e0b',
      'ip_hash': '#ef4444',
      'random': '#6b7280',
    };
    
    return colors[algorithm] || '#6b7280';
  };

  const calculateAlgorithmPerformance = () => {
    if (algorithmHistory.length < 2) {
      return {
        requestRate: 0,
        avgResponseTime: 0,
        errorRate: 0,
        efficiency: 0,
      };
    }

    const current = algorithmHistory[algorithmHistory.length - 1];
    const previous = algorithmHistory[algorithmHistory.length - 2];
    
    const requestChange = current.totalRequests - previous.totalRequests;
    const timeDiff = (current.timestamp - previous.timestamp) / 1000; // in seconds
    const requestRate = timeDiff > 0 ? requestChange / timeDiff : 0;

    return {
      requestRate: Math.round(requestRate),
      avgResponseTime: 50 + Math.random() * 50, // Mock
      errorRate: 0.5 + Math.random() * 1.5, // Mock
      efficiency: 85 + Math.random() * 15, // Mock
    };
  };

  const renderPerformanceChart = (data, color, unit = '') => {
    if (data.length === 0) return null;
    
    const maxValue = Math.max(...data);
    const chartHeight = 60;

    return (
      <div className="performance-chart">
        {data.map((value, index) => {
          const height = maxValue > 0 ? (value / maxValue) * chartHeight : 0;
          const width = 100 / data.length;
          
          return (
            <div
              key={index}
              className="chart-bar"
              style={{
                width: `${width}%`,
                height: `${height}px`,
                backgroundColor: color,
                opacity: 0.7 + (index / data.length) * 0.3,
              }}
              title={`${value}${unit}`}
            />
          );
        })}
      </div>
    );
  };

  const perf = calculateAlgorithmPerformance();
  const algorithmColor = getAlgorithmColor(stats.algorithm);

  return (
    <div className="loadbalancer-stats">
      <div className="stats-header">
        <div className="header-left">
          <FiSettings size={20} />
          <h3>Load Balancer</h3>
        </div>
        <div className="header-right">
          <div className="status-badge">
            <div className="status-dot active"></div>
            <span>Active</span>
          </div>
        </div>
      </div>

      <div className="overview-grid">
        <div className="overview-card">
          <div className="overview-icon" style={{ backgroundColor: `${algorithmColor}20` }}>
            <FiBarChart2 color={algorithmColor} />
          </div>
          <div className="overview-content">
            <div className="overview-label">Algorithm</div>
            <div className="overview-value">
              {stats.algorithm ? stats.algorithm.replace(/_/g, ' ') : 'N/A'}
            </div>
            <div className="overview-description">
              {getAlgorithmDescription(stats.algorithm)}
            </div>
          </div>
        </div>

        <div className="overview-card">
          <div className="overview-icon" style={{ backgroundColor: '#10b98120' }}>
            <FiServer color="#10b981" />
          </div>
          <div className="overview-content">
            <div className="overview-label">Healthy Servers</div>
            <div className="overview-value">
              {stats.healthy_servers || 0}
              <span className="overview-sub">/{stats.total_servers || 0}</span>
            </div>
            <div className="overview-trend">
              {stats.healthy_servers === stats.total_servers ? (
                <span className="trend-up">
                  <FiCheckCircle /> All servers healthy
                </span>
              ) : (
                <span className="trend-down">
                  <FiAlertCircle /> {stats.total_servers - stats.healthy_servers} server(s) down
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="overview-card">
          <div className="overview-icon" style={{ backgroundColor: '#8b5cf620' }}>
            <FiActivity color="#8b5cf6" />
          </div>
          <div className="overview-content">
            <div className="overview-label">Total Requests</div>
            <div className="overview-value">
              {stats.total_requests?.toLocaleString() || '0'}
            </div>
            <div className="overview-trend">
              <span className="trend-up">
                <FiTrendingUp /> {perf.requestRate}/sec
              </span>
            </div>
          </div>
        </div>

        <div className="overview-card">
          <div className="overview-icon" style={{ backgroundColor: '#f59e0b20' }}>
            <FiClock color="#f59e0b" />
          </div>
          <div className="overview-content">
            <div className="overview-label">Avg Response Time</div>
            <div className="overview-value">
              {perf.avgResponseTime.toFixed(1)}ms
            </div>
            <div className="overview-trend">
              {perf.avgResponseTime < 100 ? (
                <span className="trend-up">
                  <FiTrendingDown /> Good
                </span>
              ) : (
                <span className="trend-down">
                  <FiTrendingUp /> Slow
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="performance-section">
        <h4>Performance Metrics</h4>
        <div className="performance-grid">
          <div className="metric-card">
            <div className="metric-header">
              <FiTrendingUp />
              <span>Requests/sec</span>
            </div>
            <div className="metric-value">
              {performanceMetrics.requestsPerSecond.length > 0 
                ? performanceMetrics.requestsPerSecond[performanceMetrics.requestsPerSecond.length - 1]
                : '0'
              }
            </div>
            {renderPerformanceChart(performanceMetrics.requestsPerSecond, '#3b82f6')}
          </div>

          <div className="metric-card">
            <div className="metric-header">
              <FiActivity />
              <span>Response Time</span>
            </div>
            <div className="metric-value">
              {performanceMetrics.responseTimes.length > 0
                ? `${performanceMetrics.responseTimes[performanceMetrics.responseTimes.length - 1].toFixed(1)}ms`
                : '0ms'
              }
            </div>
            {renderPerformanceChart(performanceMetrics.responseTimes, '#10b981', 'ms')}
          </div>

          <div className="metric-card">
            <div className="metric-header">
              <FiAlertCircle />
              <span>Error Rate</span>
            </div>
            <div className="metric-value">
              {performanceMetrics.errorRates.length > 0
                ? `${performanceMetrics.errorRates[performanceMetrics.errorRates.length - 1].toFixed(2)}%`
                : '0%'
              }
            </div>
            {renderPerformanceChart(performanceMetrics.errorRates, '#ef4444', '%')}
          </div>

          <div className="metric-card">
            <div className="metric-header">
              <FiCheckCircle />
              <span>Efficiency</span>
            </div>
            <div className="metric-value">
              {perf.efficiency.toFixed(1)}%
            </div>
            <div className="efficiency-bar">
              <div 
                className="efficiency-fill"
                style={{ width: `${perf.efficiency}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      <div className="algorithm-history">
        <h4>Algorithm History</h4>
        <div className="history-timeline">
          {algorithmHistory.length === 0 ? (
            <div className="no-history">
              <FiRefreshCw />
              <p>No algorithm changes yet</p>
            </div>
          ) : (
            algorithmHistory.map((entry, index) => {
              const time = new Date(entry.timestamp);
              const timeStr = time.toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
              });
              
              return (
                <div key={index} className="timeline-item">
                  <div className="timeline-dot" style={{ 
                    borderColor: getAlgorithmColor(entry.algorithm) 
                  }}>
                    <div 
                      className="timeline-dot-inner"
                      style={{ backgroundColor: getAlgorithmColor(entry.algorithm) }}
                    ></div>
                  </div>
                  <div className="timeline-content">
                    <div className="timeline-header">
                      <span className="algorithm-name">
                        {entry.algorithm.replace(/_/g, ' ')}
                      </span>
                      <span className="timeline-time">{timeStr}</span>
                    </div>
                    <div className="timeline-stats">
                      <span className="stat">
                        <FiServer size={12} />
                        {entry.healthyServers} servers
                      </span>
                      <span className="stat">
                        <FiTrendingUp size={12} />
                        {entry.totalRequests.toLocaleString()} requests
                      </span>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      <div className="recommendation-section">
        <h4>Recommendations</h4>
        <div className="recommendation-card">
          <div className="recommendation-icon">
            <FiSettings />
          </div>
          <div className="recommendation-content">
            <strong>Algorithm Recommendation</strong>
            <p>
              Based on current traffic patterns, consider switching to 
              <span className="highlight"> Least Response Time </span> 
              algorithm for better performance.
            </p>
          </div>
          <button className="recommendation-action">
            Apply
          </button>
        </div>

        <div className="recommendation-card">
          <div className="recommendation-icon">
            <FiServer />
          </div>
          <div className="recommendation-content">
            <strong>Server Scaling</strong>
            <p>
              Current load is at 75% capacity. Consider adding 1-2 more 
              backend servers for better distribution.
            </p>
          </div>
          <button className="recommendation-action">
            Scale Up
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoadBalancerStats;
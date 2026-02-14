# Distributed Network Monitor & Load Balancer
A comprehensive, production-ready system demonstrating intelligent load balancing, real-time health monitoring, and interactive network visualization. Built with modern microservices architecture and container orchestration.

## Code Structure

```
distributed-network-monitor/
├── load-balancer/          # Core load balancing logic
│   ├── main.py            # Flask application
│   ├── algorithms.py      # All load balancing algorithms
│   ├── health_check.py    # Server health monitoring
│   └── config.py          # Configuration management
├── server-nodes/          # Simulated backend servers
│   ├── shared/            # Common server code
│   └── node[1-3]/         # Individual server instances
├── monitoring-dashboard/  # React frontend
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── store/         # Redux state management
│   │   └── utils/         # API and helper functions
├── metrics-collector/     # Metrics aggregation
├── config/                # Service configurations
├── scripts/               # Utility scripts
└── docs/                  # Documentation
```

## Quick Start

```
# Clone and run
git clone https://github.com/yourusername/distributed-network-monitor.git
cd distributed-network-monitor
docker-compose up --build

# Access services:
# Dashboard:      http://localhost:3000
# Load Balancer:  http://localhost:5000
# Grafana:        http://localhost:3001  (admin/admin)
# Prometheus:     http://localhost:9090
```
## Features

###  Intelligent Load Balancing

***Multiple Algorithms***: Round Robin, Least Connections, Least Response Time, Weighted, IP Hash

***Real-time Health Checks***: Automatic server health monitoring

***Adaptive Routing***: Dynamic algorithm switching based on performance

### Real-time Monitoring

***Interactive Dashboard***: Live network topology visualization

***Server Metrics***: CPU, memory, connections, response times

***Traffic Analytics***: Requests/sec, error rates, protocol distribution

### Production-Ready Architecture

***Microservices***: Docker containers with isolated concerns

***Monitoring Stack***: Prometheus + Grafana integration

***High Availability***: Auto-failover and health recovery

###  Developer Experience

***Hot Reloading***: Automatic code reloading during development

***Comprehensive Logging***: Structured logs for debugging and auditing

***API Documentation***: Well-documented REST endpoints

***Test Utilities***: Traffic generation and load testing scripts

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Requests                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                ┌───────▼───────┐
                │   Load        │  ←─ Distributes traffic using
                │   Balancer    │     selected algorithm
                └───────┬───────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
    ┌───▼───┐       ┌───▼───┐       ┌───▼───┐
    │Server │       │Server │       │Server │  ←─ Simulated web
    │  1    │       │  2    │       │  3    │     servers with
    └───────┘       └───────┘       └───────┘     varying loads
        │               │               │
        └───────────────┼───────────────┘
                        │
                ┌───────▼───────┐
                │   Metrics     │  ←─ Collects performance data
                │   Collector   │     from all components
                └───────┬───────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
    ┌───▼───┐       ┌───▼───┐       ┌───▼───┐
    │React  │       │Prom-  │       │Grafana│  ←─ Visualization
    │Dash-  │       │etheus │       │       │     and monitoring
    │board  │       └───────┘       └───────┘
    └───────┘
```

## Tech Stack

1. Load Balancer -	Python (Flask), Redis
2. Web Servers	- Python (Flask), Gunicorn
3. Dashboard -	React, Redux, Socket.io
4. Monitoring - Prometheus, Grafana
5. Orchestration -	Docker, Docker Compose
6. Visualization -	Recharts, D3.js

## Data Flow

***Request Ingestion***: Client requests hit the load balancer

***Algorithm Selection***: LB selects server based on current algorithm

***Health Verification***: LB checks server health before forwarding

***Request Processing***: Server processes request and returns response

***Metrics Collection***: All components emit Prometheus metrics

***Visualization***: Dashboard updates in real-time via WebSocket

***Alerting***: System triggers alerts for anomalies

## Monitoring & Analytics

### Available Metrics

***Request Rate***: Requests per second across all servers

***Response Times***: 50th, 95th, 99th percentile latencies

***Error Rates***: HTTP error percentages by server

***Resource Usage***: CPU, memory, and connection counts

***Algorithm Performance***: Comparison of different strategies

***Traffic Patterns***: Geographic and protocol distributions

### Grafana Dashboards

***Network Overview***: High-level system health

***Server Performance***: Individual server metrics

***Load Balancer Analytics***: Algorithm effectiveness

***Traffic Analysis***: Request patterns and distributions

## API Endpoints

### Load Balancer (:5000)

GET / - API info

GET /request - Forward request through load balancer

GET /stats - Get load balancer statistics

GET /algorithm/{algo} - Change load balancing algorithm

GET /metrics - Prometheus metrics

### Web Servers (:5001-5003)

GET / - Hello endpoint

GET /health - Health check

GET /metrics - Server metrics

GET /api/data - Sample data API

## Testing

```
# Manual testing
curl http://localhost:5000/request
curl http://localhost:5000/stats
curl http://localhost:5000/algorithm/least_connections

# Generate test traffic
python scripts/generate_traffic.py --requests 1000 --concurrent 10
```

## Performance Metrics

***Requests/sec***: Throughput monitoring

***Response Time***: 95th percentile tracking

***Error Rate***: HTTP error percentage

***Server Health***: CPU, memory, connection counts

***Algorithm Efficiency***: Load distribution quality

## Troubleshooting

```
# Check logs
docker-compose logs -f

# Restart services
docker-compose restart

# Rebuild from scratch
docker-compose down -v
docker-compose up --build

# Check service health
curl http://localhost:5000/
curl http://localhost:5001/health
```

## Alerting & Notifications

### Built-in Alerts

***Server Unhealthy***: When a server fails health checks

***High Latency***: Response time > 200ms

***High CPU/Memory***: Resource usage above thresholds

***Traffic Spike***: Sudden increase in request rate

***Algorithm Inefficiency***: Poor load distribution detected

### Alert Integration

***Dashboard Alerts***: Real-time notifications in the React UI

***Grafana Alerts***: Configurable alert rules with notifications

***Prometheus Alerts***: Rule-based alerting for critical issues

## Performance Benchmarks

### Results

***Throughput***: ~800 RPS per server instance

***Latency***: < 50ms 95th percentile

***Memory Usage***: < 512MB per service

***CPU Usage***: < 30% under normal load

## Concepts Demonstrated

***Load Balancing Algorithms***: Theory and practical implementation

***Microservices Architecture***: Service decomposition and communication

***Container Orchestration***: Docker Compose for multi-service apps

***Monitoring & Observability***: Metrics collection and visualization

***Real-time Web Applications***: WebSocket communication

***Production Best Practices***: Health checks, logging, error handling

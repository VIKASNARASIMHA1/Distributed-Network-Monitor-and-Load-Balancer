#!/usr/bin/env python3
"""
Metrics Collector - Collects metrics from load balancer and servers
"""
import asyncio
import aiohttp
import time
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
from prometheus_client import start_http_server, Gauge, Counter, Histogram

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ServerConfig:
    name: str
    url: str
    port: int

class MetricsCollector:
    def __init__(self, servers: List[ServerConfig], lb_url: str = "http://localhost:5000"):
        self.servers = servers
        self.lb_url = lb_url
        self.metrics = {}
        self.setup_prometheus_metrics()
        
    def setup_prometheus_metrics(self):
        """Setup Prometheus metrics"""
        # Load Balancer metrics
        self.lb_requests = Counter(
            'loadbalancer_requests_total',
            'Total requests processed by load balancer',
            ['algorithm']
        )
        
        self.lb_healthy_servers = Gauge(
            'loadbalancer_healthy_servers',
            'Number of healthy servers'
        )
        
        self.lb_response_time = Histogram(
            'loadbalancer_response_time_seconds',
            'Load balancer response time',
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0]
        )
        
        # Server metrics
        self.server_cpu = Gauge(
            'server_cpu_usage_percent',
            'Server CPU usage percentage',
            ['server']
        )
        
        self.server_memory = Gauge(
            'server_memory_usage_percent',
            'Server memory usage percentage',
            ['server']
        )
        
        self.server_connections = Gauge(
            'server_active_connections',
            'Server active connections',
            ['server']
        )
        
        self.server_uptime = Gauge(
            'server_uptime_seconds',
            'Server uptime in seconds',
            ['server']
        )
        
        self.server_response_time = Histogram(
            'server_response_time_seconds',
            'Server response time in seconds',
            ['server'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0]
        )
        
    async def collect_server_metrics(self, session: aiohttp.ClientSession, server: ServerConfig):
        """Collect metrics from a single server"""
        try:
            # Get health metrics
            start_time = time.time()
            async with session.get(f"{server.url}:{server.port}/metrics", timeout=5) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    metrics_text = await response.text()
                    
                    # Parse Prometheus metrics
                    for line in metrics_text.split('\n'):
                        if line.startswith('#') or not line.strip():
                            continue
                        
                        # Simple parsing of Prometheus metrics
                        if 'server_cpu_usage' in line:
                            value = self._extract_metric_value(line)
                            self.server_cpu.labels(server=server.name).set(value)
                        elif 'server_memory_usage' in line:
                            value = self._extract_metric_value(line)
                            self.server_memory.labels(server=server.name).set(value)
                        elif 'server_active_connections' in line:
                            value = self._extract_metric_value(line)
                            self.server_connections.labels(server=server.name).set(value)
                        elif 'server_uptime' in line:
                            value = self._extract_metric_value(line)
                            self.server_uptime.labels(server=server.name).set(value)
                    
                    # Record response time
                    self.server_response_time.labels(server=server.name).observe(response_time)
                    
                    return {
                        'server': server.name,
                        'status': 'healthy',
                        'response_time': response_time
                    }
                else:
                    logger.warning(f"Server {server.name} returned status {response.status}")
                    return {
                        'server': server.name,
                        'status': 'unhealthy',
                        'response_time': None
                    }
                    
        except Exception as e:
            logger.error(f"Error collecting metrics from {server.name}: {e}")
            return {
                'server': server.name,
                'status': 'error',
                'error': str(e)
            }
    
    async def collect_load_balancer_metrics(self, session: aiohttp.ClientSession):
        """Collect metrics from load balancer"""
        try:
            start_time = time.time()
            async with session.get(f"{self.lb_url}/stats", timeout=5) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Update Prometheus metrics
                    self.lb_healthy_servers.set(data.get('healthy_servers', 0))
                    
                    # Record response time
                    self.lb_response_time.observe(response_time)
                    
                    return {
                        'status': 'success',
                        'data': data,
                        'response_time': response_time
                    }
                else:
                    logger.warning(f"Load balancer returned status {response.status}")
                    return {
                        'status': 'error',
                        'error': f"HTTP {response.status}"
                    }
                    
        except Exception as e:
            logger.error(f"Error collecting load balancer metrics: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _extract_metric_value(self, metric_line: str) -> float:
        """Extract value from Prometheus metric line"""
        try:
            # Format: metric_name{label="value"} 123.45
            parts = metric_line.split()
            if len(parts) >= 2:
                return float(parts[1])
        except:
            pass
        return 0.0
    
    async def collect_all_metrics(self):
        """Collect metrics from all sources"""
        async with aiohttp.ClientSession() as session:
            # Collect server metrics concurrently
            server_tasks = [
                self.collect_server_metrics(session, server)
                for server in self.servers
            ]
            
            server_results = await asyncio.gather(*server_tasks)
            
            # Collect load balancer metrics
            lb_result = await self.collect_load_balancer_metrics(session)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'servers': server_results,
                'load_balancer': lb_result
            }
    
    async def run_continuous_collection(self, interval: int = 10):
        """Run continuous metrics collection"""
        logger.info(f"Starting metrics collection every {interval} seconds")
        
        while True:
            try:
                metrics = await self.collect_all_metrics()
                
                # Log summary
                healthy_servers = sum(1 for s in metrics['servers'] if s['status'] == 'healthy')
                logger.info(f"Collected metrics: {healthy_servers}/{len(self.servers)} servers healthy")
                
                # Store metrics (could be saved to database)
                self.metrics[metrics['timestamp']] = metrics
                
                # Keep only last hour of metrics
                cutoff_time = time.time() - 3600
                self.metrics = {
                    k: v for k, v in self.metrics.items()
                    if datetime.fromisoformat(k).timestamp() > cutoff_time
                }
                
            except Exception as e:
                logger.error(f"Error in metrics collection cycle: {e}")
            
            await asyncio.sleep(interval)

def main():
    """Main function"""
    # Configure servers
    servers = [
        ServerConfig("web-server-1", "http://localhost", 5001),
        ServerConfig("web-server-2", "http://localhost", 5002),
        ServerConfig("web-server-3", "http://localhost", 5003),
    ]
    
    # Create collector
    collector = MetricsCollector(servers)
    
    # Start Prometheus metrics server
    start_http_server(8000)
    logger.info("Prometheus metrics server started on port 8000")
    
    # Run collection
    asyncio.run(collector.run_continuous_collection(interval=10))

if __name__ == "__main__":
    main()
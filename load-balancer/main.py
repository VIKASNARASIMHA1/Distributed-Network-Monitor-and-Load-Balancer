#!/usr/bin/env python3
"""
Intelligent Load Balancer with multiple algorithms
"""
from flask import Flask, request, jsonify
import threading
import time
import random
import json
from dataclasses import dataclass
from typing import List, Dict
from enum import Enum
import requests
from collections import deque
import statistics

app = Flask(__name__)

class LoadBalancingAlgorithm(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    IP_HASH = "ip_hash"
    LEAST_RESPONSE_TIME = "least_response_time"

@dataclass
class ServerNode:
    id: int
    name: str
    ip: str
    port: int
    weight: int = 1
    health_check_url: str = "/health"
    is_healthy: bool = True
    active_connections: int = 0
    response_times: deque = None
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    
    def __post_init__(self):
        self.response_times = deque(maxlen=100)
        self.last_check = time.time()
    
    @property
    def avg_response_time(self):
        if self.response_times:
            return statistics.mean(self.response_times)
        return 1000  # High default if no data
    
    @property
    def url(self):
        return f"http://{self.ip}:{self.port}"
    
    def check_health(self):
        try:
            start = time.time()
            response = requests.get(f"{self.url}{self.health_check_url}", timeout=2)
            response_time = (time.time() - start) * 1000  # Convert to ms
            
            self.response_times.append(response_time)
            self.is_healthy = response.status_code == 200
            
            # Extract metrics from response if available
            if response.headers.get('Content-Type') == 'application/json':
                data = response.json()
                self.cpu_usage = data.get('cpu_usage', 0)
                self.memory_usage = data.get('memory_usage', 0)
                self.active_connections = data.get('active_connections', 0)
            
            self.last_check = time.time()
            return True
        except:
            self.is_healthy = False
            return False

class LoadBalancer:
    def __init__(self, algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN):
        self.algorithm = algorithm
        self.servers: List[ServerNode] = []
        self.current_index = 0
        self.request_count = 0
        self.health_check_interval = 10  # seconds
        self.routing_history = []
        
        # Start health check thread
        self.health_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self.health_thread.start()
    
    def add_server(self, server: ServerNode):
        self.servers.append(server)
        print(f"Added server: {server.name} ({server.ip}:{server.port})")
    
    def get_healthy_servers(self):
        return [s for s in self.servers if s.is_healthy]
    
    def select_server(self, client_ip: str = None) -> ServerNode:
        """Select server based on chosen algorithm"""
        healthy_servers = self.get_healthy_servers()
        
        if not healthy_servers:
            raise Exception("No healthy servers available")
        
        if self.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            server = healthy_servers[self.current_index % len(healthy_servers)]
            self.current_index += 1
        
        elif self.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            server = min(healthy_servers, key=lambda s: s.active_connections)
        
        elif self.algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
            server = min(healthy_servers, key=lambda s: s.avg_response_time)
        
        elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            # Weighted selection
            total_weight = sum(s.weight for s in healthy_servers)
            selection = random.uniform(0, total_weight)
            cumulative = 0
            for s in healthy_servers:
                cumulative += s.weight
                if selection <= cumulative:
                    server = s
                    break
        
        elif self.algorithm == LoadBalancingAlgorithm.IP_HASH:
            # Deterministic based on client IP
            if client_ip:
                ip_hash = hash(client_ip) % len(healthy_servers)
                server = healthy_servers[ip_hash]
            else:
                server = healthy_servers[0]
        
        # Track routing
        self.routing_history.append({
            'timestamp': time.time(),
            'server': server.id,
            'client_ip': client_ip,
            'algorithm': self.algorithm.value
        })
        
        # Keep only last 1000 entries
        if len(self.routing_history) > 1000:
            self.routing_history = self.routing_history[-1000:]
        
        server.active_connections += 1
        self.request_count += 1
        
        return server
    
    def forward_request(self, client_ip: str = None):
        """Forward request to selected server"""
        server = self.select_server(client_ip)
        
        try:
            # Simulate request forwarding
            print(f"Forwarding request to {server.name}")
            
            # Simulate some processing time
            time.sleep(random.uniform(0.01, 0.1))
            
            # Return server info (in real implementation, would proxy actual request)
            return {
                'server_id': server.id,
                'server_name': server.name,
                'server_url': server.url,
                'algorithm_used': self.algorithm.value,
                'active_connections': server.active_connections,
                'response_time': server.avg_response_time
            }
            
        finally:
            server.active_connections -= 1
    
    def _health_check_loop(self):
        """Background thread for health checks"""
        while True:
            time.sleep(self.health_check_interval)
            for server in self.servers:
                server.check_health()
    
    def get_stats(self):
        """Get load balancer statistics"""
        healthy = self.get_healthy_servers()
        
        return {
            'total_servers': len(self.servers),
            'healthy_servers': len(healthy),
            'total_requests': self.request_count,
            'algorithm': self.algorithm.value,
            'server_stats': [
                {
                    'id': s.id,
                    'name': s.name,
                    'healthy': s.is_healthy,
                    'connections': s.active_connections,
                    'avg_response_time': s.avg_response_time,
                    'cpu_usage': s.cpu_usage,
                    'memory_usage': s.memory_usage,
                    'last_check': s.last_check
                }
                for s in self.servers
            ]
        }

# Initialize load balancer
lb = LoadBalancer(algorithm=LoadBalancingAlgorithm.ROUND_ROBIN)

# Add sample servers
lb.add_server(ServerNode(1, "web-server-1", "localhost", 5001))
lb.add_server(ServerNode(2, "web-server-2", "localhost", 5002))
lb.add_server(ServerNode(3, "web-server-3", "localhost", 5003))

@app.route('/')
def index():
    return jsonify({
        'message': 'Load Balancer API',
        'status': 'running',
        'endpoints': [
            '/request - Forward a request',
            '/stats - Get load balancer statistics',
            '/servers - List all servers',
            '/algorithm/<algo> - Change algorithm'
        ]
    })

@app.route('/request')
def handle_request():
    """Handle incoming request"""
    client_ip = request.remote_addr
    try:
        result = lb.forward_request(client_ip)
        return jsonify({'success': True, **result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 503

@app.route('/stats')
def get_stats():
    """Get load balancer statistics"""
    return jsonify(lb.get_stats())

@app.route('/servers')
def list_servers():
    """List all servers"""
    servers = [
        {
            'id': s.id,
            'name': s.name,
            'url': s.url,
            'healthy': s.is_healthy,
            'weight': s.weight,
            'connections': s.active_connections
        }
        for s in lb.servers
    ]
    return jsonify({'servers': servers})

@app.route('/algorithm/<algo>')
def change_algorithm(algo):
    """Change load balancing algorithm"""
    try:
        lb.algorithm = LoadBalancingAlgorithm(algo)
        return jsonify({
            'success': True,
            'message': f'Algorithm changed to {algo}',
            'current_algorithm': lb.algorithm.value
        })
    except ValueError:
        valid_algorithms = [a.value for a in LoadBalancingAlgorithm]
        return jsonify({
            'success': False,
            'error': f'Invalid algorithm. Valid options: {valid_algorithms}'
        }), 400

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    stats = lb.get_stats()
    metrics_output = []
    
    # Server metrics
    for server in stats['server_stats']:
        metrics_output.append(f'loadbalancer_server_healthy{{server="{server["name"]}"}} {1 if server["healthy"] else 0}')
        metrics_output.append(f'loadbalancer_server_connections{{server="{server["name"]}"}} {server["connections"]}')
        metrics_output.append(f'loadbalancer_server_response_time{{server="{server["name"]}"}} {server["avg_response_time"]}')
    
    # Global metrics
    metrics_output.append(f'loadbalancer_total_requests {lb.request_count}')
    metrics_output.append(f'loadbalancer_healthy_servers {stats["healthy_servers"]}')
    
    return '\n'.join(metrics_output), 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    print("Starting Load Balancer on http://localhost:5000")
    print("Available servers:")
    for server in lb.servers:
        print(f"  - {server.name}: {server.url}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
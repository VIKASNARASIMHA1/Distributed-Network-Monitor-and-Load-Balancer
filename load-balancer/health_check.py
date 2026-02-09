"""
Health checking service for backend servers
"""
import threading
import time
import requests
from typing import List, Dict, Callable
from dataclasses import dataclass
from datetime import datetime
import json
import socket


@dataclass
class HealthCheckConfig:
    """Health check configuration"""
    interval: int = 10  # seconds
    timeout: int = 5  # seconds
    success_threshold: int = 2
    failure_threshold: int = 3
    endpoint: str = "/health"
    expected_status: int = 200
    tcp_check: bool = True
    tcp_port: int = None


@dataclass
class ServerHealth:
    """Server health status"""
    server_id: str
    url: str
    is_healthy: bool = False
    last_check: datetime = None
    consecutive_successes: int = 0
    consecutive_failures: int = 0
    response_time: float = 0.0
    last_error: str = None
    metrics: Dict = None
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}


class HealthChecker:
    """Health checking service"""
    
    def __init__(self, config: HealthCheckConfig = None):
        self.config = config or HealthCheckConfig()
        self.servers: Dict[str, ServerHealth] = {}
        self.callbacks: List[Callable] = []
        self.running = False
        self.thread = None
        
    def add_server(self, server_id: str, url: str):
        """Add a server to health check"""
        self.servers[server_id] = ServerHealth(
            server_id=server_id,
            url=url
        )
    
    def remove_server(self, server_id: str):
        """Remove a server from health check"""
        if server_id in self.servers:
            del self.servers[server_id]
    
    def check_server(self, server: ServerHealth) -> bool:
        """Check health of a single server"""
        try:
            start_time = time.time()
            
            # First try TCP connection
            if self.config.tcp_check:
                parsed_url = server.url.replace("http://", "").replace("https://", "")
                hostname = parsed_url.split(":")[0] if ":" in parsed_url else parsed_url
                port = self.config.tcp_port or 80
                
                # Try TCP connection
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.config.timeout)
                result = sock.connect_ex((hostname, port))
                sock.close()
                
                if result != 0:
                    raise ConnectionError(f"TCP connection failed: {result}")
            
            # Then try HTTP health endpoint
            response = requests.get(
                f"{server.url}{self.config.endpoint}",
                timeout=self.config.timeout,
                headers={'User-Agent': 'HealthChecker/1.0'}
            )
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            if response.status_code == self.config.expected_status:
                server.consecutive_successes += 1
                server.consecutive_failures = 0
                server.response_time = response_time
                server.last_error = None
                server.last_check = datetime.now()
                
                # Parse metrics if available
                try:
                    if response.headers.get('Content-Type', '').startswith('application/json'):
                        server.metrics = response.json()
                except:
                    server.metrics = {}
                
                # Check if server is considered healthy
                if server.consecutive_successes >= self.config.success_threshold:
                    if not server.is_healthy:
                        server.is_healthy = True
                        self._notify_status_change(server, True)
                    return True
            else:
                raise Exception(f"Unexpected status code: {response.status_code}")
                
        except Exception as e:
            server.consecutive_failures += 1
            server.consecutive_successes = 0
            server.response_time = 0
            server.last_error = str(e)
            server.last_check = datetime.now()
            
            if server.consecutive_failures >= self.config.failure_threshold:
                if server.is_healthy:
                    server.is_healthy = False
                    self._notify_status_change(server, False)
            
            return False
        
        return server.is_healthy
    
    def check_all_servers(self):
        """Check health of all servers"""
        for server_id, server in list(self.servers.items()):
            try:
                self.check_server(server)
            except Exception as e:
                print(f"Error checking server {server_id}: {e}")
    
    def start(self):
        """Start health checking thread"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print(f"Health checker started with {len(self.servers)} servers")
    
    def stop(self):
        """Stop health checking"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def _run(self):
        """Main health checking loop"""
        while self.running:
            try:
                self.check_all_servers()
            except Exception as e:
                print(f"Health check loop error: {e}")
            
            # Sleep until next check
            for _ in range(self.config.interval):
                if not self.running:
                    break
                time.sleep(1)
    
    def register_callback(self, callback: Callable):
        """Register callback for status changes"""
        self.callbacks.append(callback)
    
    def _notify_status_change(self, server: ServerHealth, is_healthy: bool):
        """Notify all callbacks of status change"""
        for callback in self.callbacks:
            try:
                callback(server, is_healthy)
            except Exception as e:
                print(f"Error in health check callback: {e}")
    
    def get_healthy_servers(self) -> List[str]:
        """Get list of healthy server IDs"""
        return [
            server_id for server_id, server in self.servers.items()
            if server.is_healthy
        ]
    
    def get_status(self) -> Dict:
        """Get current health status of all servers"""
        status = {
            'total_servers': len(self.servers),
            'healthy_servers': len(self.get_healthy_servers()),
            'servers': {}
        }
        
        for server_id, server in self.servers.items():
            status['servers'][server_id] = {
                'url': server.url,
                'healthy': server.is_healthy,
                'last_check': server.last_check.isoformat() if server.last_check else None,
                'response_time': server.response_time,
                'consecutive_successes': server.consecutive_successes,
                'consecutive_failures': server.consecutive_failures,
                'last_error': server.last_error,
                'metrics': server.metrics
            }
        
        return status


# Singleton instance
health_checker = HealthChecker()


if __name__ == "__main__":
    # Example usage
    checker = HealthChecker(HealthCheckConfig(interval=5))
    
    # Add test servers
    checker.add_server("server1", "http://localhost:5001")
    checker.add_server("server2", "http://localhost:5002")
    
    # Register callback
    def on_status_change(server, is_healthy):
        status = "healthy" if is_healthy else "unhealthy"
        print(f"Server {server.server_id} is now {status}")
    
    checker.register_callback(on_status_change)
    
    # Start checking
    checker.start()
    
    try:
        # Run for 30 seconds
        time.sleep(30)
    finally:
        checker.stop()
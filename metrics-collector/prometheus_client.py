"""
Prometheus client utilities
"""
from prometheus_client import (
    Counter, Gauge, Histogram, Summary,
    generate_latest, CONTENT_TYPE_LATEST,
    REGISTRY
)
from typing import Dict, Any, Optional
import time

class PrometheusMetrics:
    """Prometheus metrics manager"""
    
    def __init__(self):
        self.metrics = {}
        self.setup_default_metrics()
    
    def setup_default_metrics(self):
        """Setup default metrics"""
        # Request metrics
        self.metrics['requests_total'] = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status']
        )
        
        # Response time metrics
        self.metrics['request_duration'] = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
        )
        
        # Error metrics
        self.metrics['errors_total'] = Counter(
            'http_errors_total',
            'Total HTTP errors',
            ['method', 'endpoint', 'error_type']
        )
        
        # System metrics
        self.metrics['active_connections'] = Gauge(
            'active_connections',
            'Number of active connections'
        )
        
        self.metrics['memory_usage'] = Gauge(
            'memory_usage_bytes',
            'Memory usage in bytes'
        )
        
        self.metrics['cpu_usage'] = Gauge(
            'cpu_usage_percent',
            'CPU usage percentage'
        )
    
    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request metrics"""
        self.metrics['requests_total'].labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()
        
        self.metrics['request_duration'].labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def record_error(self, method: str, endpoint: str, error_type: str):
        """Record error metrics"""
        self.metrics['errors_total'].labels(
            method=method,
            endpoint=endpoint,
            error_type=error_type
        ).inc()
    
    def update_system_metrics(self, connections: int, memory: int, cpu: float):
        """Update system metrics"""
        self.metrics['active_connections'].set(connections)
        self.metrics['memory_usage'].set(memory)
        self.metrics['cpu_usage'].set(cpu)
    
    def get_metrics(self) -> bytes:
        """Get all metrics in Prometheus format"""
        return generate_latest(REGISTRY)
    
    def create_custom_gauge(self, name: str, description: str, labels: list = None):
        """Create a custom gauge metric"""
        if name in self.metrics:
            return self.metrics[name]
        
        if labels:
            gauge = Gauge(name, description, labels)
        else:
            gauge = Gauge(name, description)
        
        self.metrics[name] = gauge
        return gauge
    
    def create_custom_counter(self, name: str, description: str, labels: list = None):
        """Create a custom counter metric"""
        if name in self.metrics:
            return self.metrics[name]
        
        if labels:
            counter = Counter(name, description, labels)
        else:
            counter = Counter(name, description)
        
        self.metrics[name] = counter
        return counter

# Global instance
metrics = PrometheusMetrics()

# Decorators for easy metric collection
def track_request(endpoint: str = None):
    """Decorator to track request metrics"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Extract request info if available
                request = None
                for arg in args:
                    if hasattr(arg, 'method') and hasattr(arg, 'path'):
                        request = arg
                        break
                
                method = request.method if request else 'UNKNOWN'
                path = endpoint or (request.path if request else 'unknown')
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Record success
                status = 200
                if hasattr(result, 'status_code'):
                    status = result.status_code
                
                duration = time.time() - start_time
                metrics.record_request(method, path, status, duration)
                
                return result
                
            except Exception as e:
                # Record error
                method = 'UNKNOWN'
                path = endpoint or 'unknown'
                
                metrics.record_error(method, path, type(e).__name__)
                metrics.record_request(method, path, 500, time.time() - start_time)
                
                raise e
        
        return wrapper
    return decorator

def expose_metrics():
    """Expose metrics endpoint for Prometheus"""
    from flask import Response
    
    def metrics_endpoint():
        return Response(
            metrics.get_metrics(),
            mimetype=CONTENT_TYPE_LATEST
        )
    
    return metrics_endpoint
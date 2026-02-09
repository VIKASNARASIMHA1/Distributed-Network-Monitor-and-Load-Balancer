"""
Shared web server implementation for all nodes
"""
import os
import random
import time
import threading
from datetime import datetime
from flask import Flask, request, jsonify
import psutil
import socket

def create_app():
    app = Flask(__name__)

    # Configuration from environment
    SERVER_ID = int(os.getenv('SERVER_ID', 1))
    SERVER_NAME = os.getenv('SERVER_NAME', f'web-server-{SERVER_ID}')
    PORT = int(os.getenv('PORT', 5000 + SERVER_ID))

    # Server characteristics
    CPU_LOAD_FACTOR = random.uniform(0.8, 1.2)
    MEMORY_BASE = random.uniform(25, 40)
    FAILURE_RATE = 0.005  # 0.5% chance of failure

    # State
    active_connections = 0
    connection_lock = threading.Lock()
    request_count = 0
    start_time = time.time()
    hostname = socket.gethostname()

    @app.before_request
    def track_request():
        nonlocal active_connections, request_count
        with connection_lock:
            active_connections += 1
            request_count += 1

    @app.after_request
    def after_request(response):
        nonlocal active_connections
        with connection_lock:
            active_connections -= 1
        return response

    @app.route('/')
    def home():
        """Main endpoint"""
        # Simulate processing delay
        delay = random.expovariate(1.0) * CPU_LOAD_FACTOR * 0.05
        time.sleep(delay)
        
        # Simulate occasional failure
        if random.random() < FAILURE_RATE:
            return jsonify({'error': 'Simulated server failure'}), 500
        
        return jsonify({
            'server': SERVER_NAME,
            'hostname': hostname,
            'message': f'Hello from {SERVER_NAME}!',
            'timestamp': datetime.now().isoformat(),
            'active_connections': active_connections,
            'total_requests': request_count,
            'uptime': int(time.time() - start_time)
        })

    @app.route('/health')
    def health():
        """Health check endpoint"""
        if random.random() < FAILURE_RATE * 0.5:
            return jsonify({'status': 'unhealthy'}), 503
        
        cpu = get_cpu_usage()
        memory = get_memory_usage()
        
        return jsonify({
            'status': 'healthy',
            'server': SERVER_NAME,
            'timestamp': datetime.now().isoformat(),
            'cpu_usage': cpu,
            'memory_usage': memory,
            'active_connections': active_connections,
            'total_requests': request_count,
            'uptime': int(time.time() - start_time),
            'hostname': hostname
        })

    @app.route('/metrics')
    def metrics():
        """Prometheus metrics endpoint"""
        cpu = get_cpu_usage()
        memory = get_memory_usage()
        
        metrics_data = f"""# HELP server_info Server information
# TYPE server_info gauge
server_info{{server="{SERVER_NAME}", hostname="{hostname}"}} 1

# HELP server_cpu_usage CPU usage percentage
# TYPE server_cpu_usage gauge
server_cpu_usage{{server="{SERVER_NAME}"}} {cpu}

# HELP server_memory_usage Memory usage percentage
# TYPE server_memory_usage gauge
server_memory_usage{{server="{SERVER_NAME}"}} {memory}

# HELP server_active_connections Active connections
# TYPE server_active_connections gauge
server_active_connections{{server="{SERVER_NAME}"}} {active_connections}

# HELP server_total_requests Total requests served
# TYPE server_total_requests counter
server_total_requests{{server="{SERVER_NAME}"}} {request_count}

# HELP server_uptime Server uptime in seconds
# TYPE server_uptime gauge
server_uptime{{server="{SERVER_NAME}"}} {int(time.time() - start_time)}
"""
        
        return metrics_data, 200, {'Content-Type': 'text/plain'}

    @app.route('/api/data')
    def get_data():
        """Sample data API"""
        time.sleep(random.uniform(0.02, 0.1))
        
        items = [
            {'id': i, 'name': f'Product {i}', 'price': round(random.uniform(10, 1000), 2)}
            for i in range(random.randint(5, 15))
        ]
        
        return jsonify({
            'server': SERVER_NAME,
            'data': items,
            'count': len(items),
            'generated_at': datetime.now().isoformat()
        })

    @app.route('/api/process', methods=['POST'])
    def process():
        """CPU-intensive processing"""
        data = request.get_json() or {}
        iterations = min(data.get('iterations', 1000), 10000)
        
        start = time.time()
        result = sum(i * 0.00001 for i in range(iterations))
        processing_time = time.time() - start
        
        return jsonify({
            'result': result,
            'iterations': iterations,
            'processing_time': processing_time,
            'server': SERVER_NAME
        })

    @app.route('/info')
    def info():
        """Server information"""
        return jsonify({
            'server': SERVER_NAME,
            'version': '1.0.0',
            'hostname': hostname,
            'port': PORT,
            'start_time': datetime.fromtimestamp(start_time).isoformat(),
            'characteristics': {
                'cpu_load_factor': CPU_LOAD_FACTOR,
                'memory_base': MEMORY_BASE,
                'failure_rate': FAILURE_RATE
            }
        })

    def get_cpu_usage():
        """Get CPU usage with simulated load"""
        real_usage = psutil.cpu_percent(interval=0.1)
        load = active_connections * 0.3
        simulated = min(100, real_usage * CPU_LOAD_FACTOR + load)
        return round(simulated, 2)

    def get_memory_usage():
        """Get memory usage with simulated load"""
        real_usage = psutil.virtual_memory().percent
        load = active_connections * 0.1
        simulated = min(100, MEMORY_BASE + load + (real_usage * 0.1))
        return round(simulated, 2)

    return app
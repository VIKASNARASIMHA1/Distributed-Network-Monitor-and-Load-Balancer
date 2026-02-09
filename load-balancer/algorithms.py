"""
Load balancing algorithms implementation
"""
import random
import hashlib
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum
import statistics


class LoadBalancingAlgorithm(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    IP_HASH = "ip_hash"
    LEAST_RESPONSE_TIME = "least_response_time"
    RANDOM = "random"


@dataclass
class ServerStats:
    """Server statistics for load balancing decisions"""
    active_connections: int = 0
    response_times: list = None
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    weight: int = 1
    is_healthy: bool = True
    
    def __post_init__(self):
        if self.response_times is None:
            self.response_times = []
    
    @property
    def avg_response_time(self) -> float:
        if self.response_times:
            return statistics.mean(self.response_times[:10])  # Last 10 responses
        return 1000.0  # High default
    
    @property
    def score(self) -> float:
        """Calculate a score for weighted algorithms"""
        if not self.is_healthy:
            return float('inf')
        
        # Lower score is better
        score = (
            self.active_connections * 0.5 +
            self.avg_response_time * 0.01 +
            self.cpu_usage * 0.3 +
            self.memory_usage * 0.2
        )
        
        # Adjust by weight (higher weight = better)
        score = score / max(self.weight, 1)
        
        return score


class LoadBalancerAlgorithms:
    """Collection of load balancing algorithms"""
    
    @staticmethod
    def round_robin(servers: List[ServerStats], last_index: int) -> int:
        """Round Robin algorithm"""
        healthy_servers = [i for i, s in enumerate(servers) if s.is_healthy]
        if not healthy_servers:
            raise ValueError("No healthy servers available")
        
        current_index = (last_index + 1) % len(healthy_servers)
        return healthy_servers[current_index]
    
    @staticmethod
    def least_connections(servers: List[ServerStats]) -> int:
        """Least Connections algorithm"""
        healthy_servers = [(i, s) for i, s in enumerate(servers) if s.is_healthy]
        if not healthy_servers:
            raise ValueError("No healthy servers available")
        
        # Find server with minimum connections
        min_connections = float('inf')
        selected_index = 0
        
        for i, server in healthy_servers:
            if server.active_connections < min_connections:
                min_connections = server.active_connections
                selected_index = i
            elif server.active_connections == min_connections:
                # Tie-breaker: lower response time
                if server.avg_response_time < servers[selected_index].avg_response_time:
                    selected_index = i
        
        return selected_index
    
    @staticmethod
    def weighted_round_robin(servers: List[ServerStats]) -> int:
        """Weighted Round Robin algorithm"""
        healthy_servers = [(i, s) for i, s in enumerate(servers) if s.is_healthy]
        if not healthy_servers:
            raise ValueError("No healthy servers available")
        
        # Calculate total weight
        total_weight = sum(server.weight for _, server in healthy_servers)
        
        # Generate random number in range [0, total_weight)
        r = random.uniform(0, total_weight)
        
        # Find server based on weight
        cumulative = 0
        for i, server in healthy_servers:
            cumulative += server.weight
            if r <= cumulative:
                return i
        
        # Fallback to first server
        return healthy_servers[0][0]
    
    @staticmethod
    def least_response_time(servers: List[ServerStats]) -> int:
        """Least Response Time algorithm"""
        healthy_servers = [(i, s) for i, s in enumerate(servers) if s.is_healthy]
        if not healthy_servers:
            raise ValueError("No healthy servers available")
        
        # Find server with minimum response time
        min_response_time = float('inf')
        selected_index = 0
        
        for i, server in healthy_servers:
            if server.avg_response_time < min_response_time:
                min_response_time = server.avg_response_time
                selected_index = i
            elif server.avg_response_time == min_response_time:
                # Tie-breaker: fewer connections
                if server.active_connections < servers[selected_index].active_connections:
                    selected_index = i
        
        return selected_index
    
    @staticmethod
    def ip_hash(servers: List[ServerStats], client_ip: str) -> int:
        """IP Hash algorithm"""
        healthy_servers = [i for i, s in enumerate(servers) if s.is_healthy]
        if not healthy_servers:
            raise ValueError("No healthy servers available")
        
        # Create hash from IP address
        ip_hash = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        
        # Select server based on hash
        return healthy_servers[ip_hash % len(healthy_servers)]
    
    @staticmethod
    def random_selection(servers: List[ServerStats]) -> int:
        """Random selection algorithm"""
        healthy_servers = [i for i, s in enumerate(servers) if s.is_healthy]
        if not healthy_servers:
            raise ValueError("No healthy servers available")
        
        return random.choice(healthy_servers)
    
    @staticmethod
    def get_algorithm(algo: LoadBalancingAlgorithm):
        """Get algorithm function by name"""
        algorithms = {
            LoadBalancingAlgorithm.ROUND_ROBIN: LoadBalancerAlgorithms.round_robin,
            LoadBalancingAlgorithm.LEAST_CONNECTIONS: LoadBalancerAlgorithms.least_connections,
            LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN: LoadBalancerAlgorithms.weighted_round_robin,
            LoadBalancingAlgorithm.LEAST_RESPONSE_TIME: LoadBalancerAlgorithms.least_response_time,
            LoadBalancingAlgorithm.IP_HASH: LoadBalancerAlgorithms.ip_hash,
            LoadBalancingAlgorithm.RANDOM: LoadBalancerAlgorithms.random_selection,
        }
        return algorithms.get(algo, LoadBalancerAlgorithms.round_robin)


class AdaptiveLoadBalancer:
    """Adaptive load balancer that switches algorithms based on conditions"""
    
    def __init__(self):
        self.current_algorithm = LoadBalancingAlgorithm.ROUND_ROBIN
        self.performance_metrics = {
            'response_times': [],
            'error_rates': [],
            'throughput': []
        }
    
    def evaluate_performance(self, servers: List[ServerStats]) -> LoadBalancingAlgorithm:
        """Evaluate performance and switch algorithm if needed"""
        if len(servers) < 2:
            return LoadBalancingAlgorithm.ROUND_ROBIN
        
        # Check if servers have similar performance
        response_times = [s.avg_response_time for s in servers if s.is_healthy]
        if len(response_times) < 2:
            return self.current_algorithm
        
        # Calculate coefficient of variation
        mean_rt = statistics.mean(response_times)
        if mean_rt > 0:
            std_rt = statistics.stdev(response_times)
            cv = std_rt / mean_rt
            
            # If response times vary significantly, use least response time
            if cv > 0.3:
                return LoadBalancingAlgorithm.LEAST_RESPONSE_TIME
        
        # Check connection distribution
        connections = [s.active_connections for s in servers if s.is_healthy]
        if connections:
            max_conn = max(connections)
            min_conn = min(connections)
            
            # If connection distribution is uneven, use least connections
            if max_conn > min_conn * 2:
                return LoadBalancingAlgorithm.LEAST_CONNECTIONS
        
        # Default to round robin
        return LoadBalancingAlgorithm.ROUND_ROBIN
    
    def select_server(self, servers: List[ServerStats], client_ip: str = None) -> int:
        """Select server using adaptive algorithm"""
        # Update algorithm if needed
        new_algo = self.evaluate_performance(servers)
        if new_algo != self.current_algorithm:
            print(f"Switching algorithm from {self.current_algorithm} to {new_algo}")
            self.current_algorithm = new_algo
        
        # Get the algorithm function
        algo_func = LoadBalancerAlgorithms.get_algorithm(self.current_algorithm)
        
        # Special handling for algorithms that need additional parameters
        if self.current_algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            # Need to track round robin index (simplified)
            return algo_func(servers, 0)
        elif self.current_algorithm == LoadBalancingAlgorithm.IP_HASH:
            if not client_ip:
                client_ip = "0.0.0.0"
            return algo_func(servers, client_ip)
        else:
            return algo_func(servers)
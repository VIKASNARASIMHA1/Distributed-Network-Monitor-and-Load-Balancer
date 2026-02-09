"""
Configuration management for load balancer
"""
import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json
import yaml


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class ServerConfig:
    """Individual server configuration"""
    id: str
    name: str
    host: str
    port: int
    weight: int = 1
    health_check_endpoint: str = "/health"
    protocol: str = "http"
    enabled: bool = True
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    @property
    def url(self) -> str:
        return f"{self.protocol}://{self.host}:{self.port}"
    
    @property
    def health_check_url(self) -> str:
        return f"{self.url}{self.health_check_endpoint}"


@dataclass
class HealthCheckConfig:
    """Health check configuration"""
    enabled: bool = True
    interval_seconds: int = 10
    timeout_seconds: int = 5
    success_threshold: int = 2
    failure_threshold: int = 3
    tcp_check: bool = True
    http_check: bool = True
    expected_status_codes: List[int] = None
    
    def __post_init__(self):
        if self.expected_status_codes is None:
            self.expected_status_codes = [200]


@dataclass
class LoadBalancerConfig:
    """Main load balancer configuration"""
    # Network
    host: str = "0.0.0.0"
    port: int = 5000
    workers: int = 4
    backlog: int = 2048
    
    # Algorithm
    algorithm: str = "round_robin"
    sticky_sessions: bool = False
    session_timeout: int = 1800  # seconds
    
    # Health checking
    health_check: HealthCheckConfig = None
    
    # Servers
    servers: List[ServerConfig] = None
    
    # Logging
    log_level: LogLevel = LogLevel.INFO
    log_file: Optional[str] = None
    access_log: bool = True
    
    # Monitoring
    metrics_enabled: bool = True
    metrics_port: int = 5001
    metrics_path: str = "/metrics"
    
    # Security
    rate_limit_enabled: bool = False
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    trusted_proxies: List[str] = None
    
    # Advanced
    connection_timeout: int = 30
    keepalive_timeout: int = 5
    max_body_size: int = 10485760  # 10MB
    
    def __post_init__(self):
        if self.health_check is None:
            self.health_check = HealthCheckConfig()
        if self.servers is None:
            self.servers = []
        if self.trusted_proxies is None:
            self.trusted_proxies = ["127.0.0.1"]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LoadBalancerConfig':
        """Create config from dictionary"""
        # Handle nested dataclasses
        if 'health_check' in data and isinstance(data['health_check'], dict):
            data['health_check'] = HealthCheckConfig(**data['health_check'])
        
        if 'servers' in data and isinstance(data['servers'], list):
            servers = []
            for server_data in data['servers']:
                servers.append(ServerConfig(**server_data))
            data['servers'] = servers
        
        return cls(**data)
    
    @classmethod
    def from_file(cls, filepath: str) -> 'LoadBalancerConfig':
        """Load configuration from file"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Config file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            if filepath.endswith('.yaml') or filepath.endswith('.yml'):
                data = yaml.safe_load(f)
            elif filepath.endswith('.json'):
                data = json.load(f)
            else:
                raise ValueError("Unsupported config file format")
        
        return cls.from_dict(data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        """Convert config to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, default=str)
    
    def to_yaml(self) -> str:
        """Convert config to YAML string"""
        return yaml.dump(self.to_dict(), default_flow_style=False)
    
    def save(self, filepath: str):
        """Save configuration to file"""
        data = self.to_dict()
        
        with open(filepath, 'w') as f:
            if filepath.endswith('.yaml') or filepath.endswith('.yml'):
                yaml.dump(data, f, default_flow_style=False)
            elif filepath.endswith('.json'):
                json.dump(data, f, indent=2)
            else:
                raise ValueError("Unsupported config file format")
    
    def validate(self):
        """Validate configuration"""
        errors = []
        
        # Validate algorithm
        valid_algorithms = [
            "round_robin", "least_connections", "weighted_round_robin",
            "least_response_time", "ip_hash", "random"
        ]
        if self.algorithm not in valid_algorithms:
            errors.append(f"Invalid algorithm: {self.algorithm}")
        
        # Validate port ranges
        if not (1 <= self.port <= 65535):
            errors.append(f"Invalid port: {self.port}")
        
        if not (1 <= self.metrics_port <= 65535):
            errors.append(f"Invalid metrics port: {self.metrics_port}")
        
        # Validate workers
        if self.workers < 1:
            errors.append(f"Invalid worker count: {self.workers}")
        
        # Validate servers
        if not self.servers:
            errors.append("No servers configured")
        else:
            for i, server in enumerate(self.servers):
                if not server.host or not server.port:
                    errors.append(f"Server {i}: missing host or port")
                if server.weight < 1:
                    errors.append(f"Server {i}: weight must be >= 1")
        
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))


def load_config(config_path: Optional[str] = None) -> LoadBalancerConfig:
    """Load configuration from file or environment"""
    
    # Default config
    config = LoadBalancerConfig()
    
    # Try to load from file
    if config_path and os.path.exists(config_path):
        config = LoadBalancerConfig.from_file(config_path)
    
    # Override from environment variables
    env_mapping = {
        'LB_HOST': 'host',
        'LB_PORT': 'port',
        'LB_ALGORITHM': 'algorithm',
        'LB_WORKERS': 'workers',
        'LB_LOG_LEVEL': 'log_level',
    }
    
    for env_var, config_attr in env_mapping.items():
        if env_var in os.environ:
            setattr(config, config_attr, os.environ[env_var])
    
    # Parse port as integer
    if 'LB_PORT' in os.environ:
        config.port = int(os.environ['LB_PORT'])
    
    if 'LB_WORKERS' in os.environ:
        config.workers = int(os.environ['LB_WORKERS'])
    
    # Add default servers if none configured
    if not config.servers:
        config.servers = [
            ServerConfig("server1", "web-server-1", "localhost", 5001, weight=1),
            ServerConfig("server2", "web-server-2", "localhost", 5002, weight=1),
            ServerConfig("server3", "web-server-3", "localhost", 5003, weight=2),
        ]
    
    # Validate configuration
    config.validate()
    
    return config


# Global configuration instance
config = load_config()
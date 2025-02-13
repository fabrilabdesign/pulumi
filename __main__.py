"""A Python Pulumi program for Addi-Aire Infrastructure"""

import pulumi
from src.networking import NetworkingStack
from src.compute import ContainerStack
from src.monitoring import MonitoringStack
from src.storage import StorageStack
from pulumi import Output
from src.security.vault import VaultStack, AutoVault
from src.registry import Registry
from src.registry.certs import generate_registry_certs
from src.registry.auth import generate_htpasswd
from pathlib import Path

# Get configuration
config = pulumi.Config()
environment = config.get("environment", "dev")

# Registry configuration
registry_config = {
    "server": config.require_secret("registryServer"),
    "username": config.require_secret("registryUsername"),
    "password": config.require_secret("registryPassword")
}

# Set up registry
registry_config_dir = Path('config/registry')
hostname = '192.168.3.26'

# Generate certificates
key_path, cert_path = generate_registry_certs(registry_config_dir / 'certs', hostname)

# Generate auth credentials
registry_password = generate_htpasswd(registry_config_dir / 'auth', 'admin')

# Create networking stack
network = NetworkingStack("main")

# Create registry instance
registry = Registry('registry', network_id=network.mgmt_network.id)

# Store registry credentials securely
pulumi.export('registry_username', 'admin')
pulumi.export('registry_password', registry_password)
pulumi.export('registry_url', f'https://{hostname}:5000')

# Create container stack with appropriate network
containers = ContainerStack("main",
    network_ids={
        "prod": network.prod_network.id,
        "dev": network.dev_network.id,
        "mgmt": network.mgmt_network.id
    },
    registry_config=registry_config,
    environment=environment
)

# Create monitoring stack
monitoring = MonitoringStack("main",
    network_ids={
        "prod": network.prod_network.id,
        "dev": network.dev_network.id,
        "mgmt": network.mgmt_network.id
    }
)

# Create storage stack
storage = StorageStack("main",
    network_ids={
        "prod": network.prod_network.id,
        "dev": network.dev_network.id,
        "mgmt": network.mgmt_network.id
    }
)

# Create Vault stack
vault = AutoVault("main", network.mgmt_network.id)

# Export outputs
pulumi.export("networks", {
    "prod": network.prod_network.name,
    "dev": network.dev_network.name,
    "mgmt": network.mgmt_network.name
})

# External endpoints (for browser/user access)
pulumi.export("external_endpoints", {
    "app": "http://192.168.3.26:3000",
    "jenkins": "http://192.168.3.26:8080",
    "kibana": "http://192.168.3.26:5601",
    "grafana": "http://192.168.3.26:3001",
    "elasticsearch": "http://192.168.3.26:9200",
    "vault": "http://192.168.3.26:8200"
})

# Internal endpoints (for container communication)
pulumi.export("internal_endpoints", {
    "app": "http://app:3000",
    "jenkins": "http://jenkins:8080",
    "kibana": "http://kibana:5601",
    "grafana": "http://grafana:3000",
    "elasticsearch": "http://elasticsearch:9200",
    "vault": "http://vault:8200"
})

# Export vault token
pulumi.export("vault_token", "addi-aire-now")

"""A Python Pulumi program for Addi-Aire Infrastructure"""

import pulumi
from src.networking import NetworkingStack
from src.compute import ContainerStack
from src.monitoring import MonitoringStack
from src.storage import StorageStack
from pulumi import Output
from src.security.vault import VaultStack, AutoVault

# Get configuration
config = pulumi.Config()
environment = config.get("environment", "dev")

# Registry configuration
registry_config = {
    "server": config.require_secret("registryServer"),
    "username": config.require_secret("registryUsername"),
    "password": config.require_secret("registryPassword")
}

# Create networking stack
network = NetworkingStack("main")

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

pulumi.export("endpoints", {
    "app": f"http://192.168.3.26:3000",
    "jenkins": "http://192.168.3.26:8080/jenkins",
    "nginx": "http://192.168.3.26",
    "kibana": "http://192.168.3.26:5601",
    "grafana": "http://192.168.3.26:3001",
    "elasticsearch": "http://192.168.3.26:9200"
})

# Export UI access
pulumi.export("vault_url", "http://192.168.3.26:8200")
pulumi.export("vault_token", "addi-aire-now")

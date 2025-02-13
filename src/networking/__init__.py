from pulumi import ComponentResource, ResourceOptions, Output
from pulumi_docker import Network
from typing import Dict, List

class NetworkingStack(ComponentResource):
    def __init__(self, name: str, opts: ResourceOptions = None):
        super().__init__("addi-aire:networking:NetworkingStack", name, None, opts)

        # Production network - isolated
        self.prod_network = Network("prod-network",
            name="addi-aire-prod",
            driver="bridge",
            internal=True,  # No external connectivity
            ipv6=False,
            attachable=True,  # Allow external containers to connect
            ipam_configs=[{
                "subnet": "172.18.0.0/16",
                "gateway": "172.18.0.1"
            }],
            opts=ResourceOptions(parent=self)
        )

        # Development network - isolated
        self.dev_network = Network("dev-network",
            name="addi-aire-dev",
            driver="bridge",
            internal=True,
            ipv6=False,
            attachable=True,
            ipam_configs=[{
                "subnet": "172.19.0.0/16",
                "gateway": "172.19.0.1"
            }],
            opts=ResourceOptions(parent=self)
        )

        # Management network - external access
        self.mgmt_network = Network("mgmt-network",
            name="addi-aire-mgmt",
            driver="bridge",
            internal=False,  # Allow external connectivity
            ipv6=False,
            attachable=True,
            ipam_configs=[{
                "subnet": "172.20.0.0/16",
                "gateway": "172.20.0.1"
            }],
            opts=ResourceOptions(parent=self)
        )

        self.register_outputs({
            "networks": {
                "prod": {
                    "id": self.prod_network.id,
                    "name": self.prod_network.name,
                    "subnet": "172.18.0.0/16",
                    "gateway": "172.18.0.1"
                },
                "dev": {
                    "id": self.dev_network.id,
                    "name": self.dev_network.name,
                    "subnet": "172.19.0.0/16",
                    "gateway": "172.19.0.1"
                },
                "mgmt": {
                    "id": self.mgmt_network.id,
                    "name": self.mgmt_network.name,
                    "subnet": "172.20.0.0/16",
                    "gateway": "172.20.0.1"
                }
            }
        }) 
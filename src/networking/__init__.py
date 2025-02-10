from pulumi import ComponentResource, ResourceOptions, Output
from pulumi_docker import Network
from typing import Dict, List

class NetworkingStack(ComponentResource):
    def __init__(self, name: str, opts: ResourceOptions = None):
        super().__init__("addi-aire:networking:NetworkingStack", name, None, opts)

        # Production network (172.18.0.0/16)
        self.prod_network = Network("prod-network",
            name="addi-aire-prod",
            driver="bridge",
            ipam_configs=[{
                "subnet": "172.18.0.0/16",
                "gateway": "172.18.0.1"
            }],
            opts=ResourceOptions(parent=self)
        )

        # Development network (172.19.0.0/16)
        self.dev_network = Network("dev-network",
            name="addi-aire-dev",
            driver="bridge",
            ipam_configs=[{
                "subnet": "172.19.0.0/16",
                "gateway": "172.19.0.1"
            }],
            opts=ResourceOptions(parent=self)
        )

        # Management network (172.20.0.0/16)
        self.mgmt_network = Network("mgmt-network",
            name="addi-aire-mgmt",
            driver="bridge",
            ipam_configs=[{
                "subnet": "172.20.0.0/16",
                "gateway": "172.20.0.1"
            }],
            opts=ResourceOptions(parent=self)
        )

        self.register_outputs({
            "prod_network_id": self.prod_network.id,
            "dev_network_id": self.dev_network.id,
            "mgmt_network_id": self.mgmt_network.id,
            "prod_network_name": self.prod_network.name,
            "dev_network_name": self.dev_network.name,
            "mgmt_network_name": self.mgmt_network.name
        }) 
from pulumi import ComponentResource, ResourceOptions, Output
from pulumi_vault import AuthBackend, Mount
from pulumi_docker import Container, Volume, ContainerCapabilitiesArgs

class BasicVault(ComponentResource):
    def __init__(self, network_id: str):
        self.vault = Container("vault",
            image="hashicorp/vault:1.15.6",
            ports=[{"internal": 8200, "external": 8200}],
            command=["vault", "server", "-dev"],
            network_id=network_id,
            envs={
                "VAULT_DEV_ROOT_TOKEN_ID": "addi-aire-temp",
                "VAULT_DEV_LISTEN_ADDRESS": "0.0.0.0:8200"
            }
        )

class AutoVault(ComponentResource):
    def __init__(self, name: str, network_id: str, opts: ResourceOptions = None):
        super().__init__("addi-aire:vault:AutoVault", name, None, opts)
        
        # Self-contained vault with auto-unseal
        self.vault = Container("vault",
            image="hashicorp/vault:1.15.6",
            ports=[{"internal": 8200, "external": 8200}],
            networks_advanced=[{"name": network_id}],
            envs=[
                "VAULT_DEV_ROOT_TOKEN_ID=addi-aire-now",
                "VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200"
            ],
            command=[
                "vault", "server",
                "-dev",
                "-dev-root-token-id=addi-aire-now",
                "-dev-listen-address=0.0.0.0:8200"
            ],
            capabilities=ContainerCapabilitiesArgs(
                adds=["IPC_LOCK"]
            ),
            opts=ResourceOptions(parent=self)
        )
        
        self.register_outputs({
            "vault_address": "http://localhost:8200",
            "vault_token": "addi-aire-now"
        }) 
from pulumi import ComponentResource, ResourceOptions, Output
from pulumi_vault import AuthBackend, Mount
from pulumi_docker import Container, Volume, ContainerCapabilitiesArgs, ContainerNetworksAdvancedArgs

class BasicVault(ComponentResource):
    def __init__(self, network_id: str):
        self.vault = Container("vault",
            image="hashicorp/vault:1.15.6",
            ports=[{"internal": "8200", "external": "8200"}],
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
        
        # Create persistent volume for Vault data
        self.volume = Volume(
            f"{name}-data",
            name="vault_data",
            opts=ResourceOptions(parent=self, protect=True)  # protect=True prevents accidental deletion
        )
        
        # Self-contained vault with auto-unseal
        self.vault = Container("vault",
            image="hashicorp/vault:1.15.6",
            ports=[{"internal": "8200", "external": "8220"}],
            volumes=[{
                "volume_name": self.volume.name,
                "container_path": "/vault/data"
            }],
            networks_advanced=[ContainerNetworksAdvancedArgs(
                name=network_id,
                aliases=["vault"]
            )],
            envs=[
                "VAULT_DEV_ROOT_TOKEN_ID=addi-aire-now",
                "VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200",
                "VAULT_LOCAL_CONFIG={\"storage\": {\"file\": {\"path\": \"/vault/data\"}}}"
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
            "vault_address": "http://192.168.3.26:8220",
            "vault_token": "addi-aire-now"
        }) 
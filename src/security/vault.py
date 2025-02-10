from pulumi import ResourceOptions, ComponentResource
from pulumi_vault import AuthBackend, Mount
from pulumi_docker import Container, Volume, ContainerCapabilitiesArgs
import json
import pulumi
from pulumi_aws import kms

class VaultStack(ComponentResource):
    def __init__(self, name: str, network_id: str, opts: ResourceOptions = None):
        super().__init__("addi-aire:security:VaultStack", name, None, opts)
        
        # Enable Kubernetes auth
        self.kubernetes_auth = AuthBackend("kubernetes",
            type="kubernetes",
            path="kubernetes",
            opts=ResourceOptions(parent=self)
        )

        # KV secrets engine
        self.kv_secrets = Mount("kv",
            path="kv",
            type="kv",
            options={
                "version": "2"
            },
            opts=ResourceOptions(parent=self)
        )

        # PKI engine for certificates
        self.pki = Mount("pki",
            path="pki",
            type="pki",
            default_lease_ttl_seconds=86400,
            max_lease_ttl_seconds=315360000,
            opts=ResourceOptions(parent=self)
        )

        # Persistent storage
        self.storage = Volume("vault-data", 
            name="vault_data",
            opts=ResourceOptions(parent=self)
        )

        # Vault server container
        self.vault = Container("vault-server",
            image="vault:1.15.0",
            ports=[
                {"internal": 8200, "external": 8200},
                {"internal": 8201, "external": 8201, "protocol": "tcp"}
            ],
            volumes=[{
                "volume_name": self.storage.name,
                "container_path": "/vault/data"
            }],
            command=["vault", "server", "-config=/vault/config/config.hcl"],
            network_id=network_id,
            envs={
                "VAULT_API_ADDR": "http://vault.addi-aire:8200",
                "VAULT_CLUSTER_ADDR": "https://vault.addi-aire:8201"
            },
            opts=ResourceOptions(parent=self)
        )

        # Initialization and unsealing
        self._init_vault()

        self.register_outputs({
            "vault_address": "http://vault.addi-aire:8200"
        })

    def _init_vault(self):
        """Automated initialization and unsealing process"""
        from pulumi_command import Command
        
        # Initialize Vault
        init_cmd = Command("vault-init",
            create="vault operator init -key-shares=5 -key-threshold=3 -format=json",
            environment={
                "VAULT_ADDR": "http://localhost:8200"
            },
            opts=ResourceOptions(
                parent=self,
                depends_on=[self.vault]
            )
        )
        
        # Store unseal keys and root token
        pulumi.export("vault_unseal_keys", init_cmd.stdout.apply(lambda x: json.loads(x)["unseal_keys_b64"]))
        pulumi.export("vault_root_token", init_cmd.stdout.apply(lambda x: json.loads(x)["root_token"]))

    def _configure_auto_unseal(self):
        """AWS KMS auto-unseal configuration"""
        # Create KMS key
        kms_key = kms.Key("vault-auto-unseal",
            description="Vault auto-unseal key",
            key_usage="ENCRYPT_DECRYPT",
            deletion_window_in_days=30
        )
        
        # Update Vault config
        self.vault.command.apply(lambda _: 
            "vault server -config=/vault/config/auto-unseal.hcl"
        )
        
        # Generate auto-unseal config
        pulumi.Output.all(kms_key.arn).apply(lambda args:
            open("/vault/config/auto-unseal.hcl", "w").write(f"""
                seal "awskms" {{
                  region     = "us-west-2"
                  kms_key_id = "{args[0]}"
                }}
            """)
        )

class BasicVault(ComponentResource):
    def __init__(self, network_id: str):
        self.vault = Container("vault",
            image="vault:1.15.0",
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
            ports=[{"internal": 8200, "external": 8220}],
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
            "vault_address": "http://localhost:8220",
            "vault_token": "addi-aire-now"
        }) 
from pulumi import ComponentResource, ResourceOptions, Config, Output
import pulumi_docker as docker
import os
from pathlib import Path
from typing import Optional, Dict, Any

class RegistryArgs:
    def __init__(self,
                 host: str = "192.168.3.26",
                 port: str = "5000",
                 config_path: Optional[str] = None) -> None:
        self.host = host
        self.port = port
        self.config_path = config_path or "config/registry"

class Registry(ComponentResource):
    def __init__(self,
                 name: str,
                 network_id: str,
                 args: RegistryArgs = None,
                 opts: Optional[ResourceOptions] = None):
        super().__init__('custom:registry:Registry', name, None, opts)

        args = args or RegistryArgs()
        config = Config()

        # Resource naming convention
        def make_name(resource_name: str) -> str:
            return f"{name}-{resource_name}"

        # Ensure config directories exist
        config_dir = Path(os.path.abspath(args.config_path))
        certs_dir = config_dir / 'certs'
        auth_dir = config_dir / 'auth'
        
        for dir_path in [config_dir, certs_dir, auth_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Create registry volume
        self.volume = docker.Volume(
            make_name("volume"),
            name=make_name("volume"),
            opts=ResourceOptions(parent=self)
        )

        # Container configuration
        container_config = {
            'name': name,
            'image': 'registry:2',
            'ports': [{
                'internal': str(args.port),
                'external': str(args.port),
                'protocol': 'tcp'
            }],
            'volumes': [
                docker.ContainerVolumeArgs(
                    volume_name=self.volume.name,
                    container_path='/var/lib/registry'
                ),
                docker.ContainerVolumeArgs(
                    host_path=str(config_dir / 'config.yml'),
                    container_path='/etc/docker/registry/config.yml'
                ),
                docker.ContainerVolumeArgs(
                    host_path=str(certs_dir),
                    container_path='/certs'
                ),
                docker.ContainerVolumeArgs(
                    host_path=str(auth_dir),
                    container_path='/auth'
                )
            ],
            'restart': 'always',
            'networks_advanced': [
                docker.ContainerNetworksAdvancedArgs(
                    name=network_id,
                    aliases=["registry"]
                )
            ],
            'envs': [
                f"REGISTRY_HTTP_ADDR=0.0.0.0:{args.port}",
                f"REGISTRY_HTTP_TLS_CERTIFICATE=/certs/registry.crt",
                f"REGISTRY_HTTP_TLS_KEY=/certs/registry.key"
            ],
            'healthcheck': {
                'test': ["CMD", "curl", "-f", f"https://localhost:{args.port}/v2/ || exit 1"],
                'interval': "30s",
                'timeout': "10s",
                'retries': "3",
                'start_period': "10s"
            }
        }

        # Create registry container
        self.container = docker.Container(
            name,
            opts=ResourceOptions(
                parent=self,
                depends_on=[self.volume],
                custom_timeouts={"create": "10m", "update": "10m", "delete": "10m"}
            ),
            **container_config
        )

        # Prometheus monitoring configuration
        self.monitoring_config = {
            'job_name': 'registry',
            'metrics_path': '/metrics',
            'scheme': 'https',
            'tls_config': {
                'ca_file': '/etc/docker/certs.d/{args.host}:{args.port}/ca.crt',
                'insecure_skip_verify': "true"
            },
            'static_configs': [{
                'targets': [f'{args.host}:{args.port}']
            }]
        }

        # Register component outputs
        self.register_outputs({
            'volume_name': self.volume.name,
            'container_id': self.container.id,
            'registry_url': Output.concat("https://", args.host, ":", Output.from_input(args.port)),
            'monitoring_config': self.monitoring_config
        }) 
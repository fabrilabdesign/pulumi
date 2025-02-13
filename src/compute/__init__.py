from pulumi import ComponentResource, ResourceOptions, Output
from pulumi_docker import Image, Container, Volume, ContainerCapabilitiesArgs, ContainerNetworksAdvancedArgs
from typing import Dict, List, Union

class ContainerStack(ComponentResource):
    def __init__(self, 
                 name: str,
                 network_ids: Dict[str, Union[str, Output[str]]],
                 registry_config: Dict[str, str] = None,
                 environment: str = "dev",
                 opts: ResourceOptions = None):
        super().__init__("addi-aire:compute:ContainerStack", name, None, opts)

        # Create volumes
        self.jenkins_volume = Volume("jenkins-data",
            name="jenkins_home",
            opts=ResourceOptions(parent=self)
        )

        # Create Jenkins container
        self.jenkins = Container("jenkins",
            image="jenkins/jenkins:lts-jdk17",
            name="jenkins",
            ports=[
                {"internal": "8080", "external": "8080"},
                {"internal": "50000", "external": "50000"}
            ],
            volumes=[
                {"volume_name": self.jenkins_volume.name, "container_path": "/var/jenkins_home"},
                {"host_path": "/var/run/docker.sock", "container_path": "/var/run/docker.sock"}
            ],
            envs=[
                f"JENKINS_OPTS=--prefix=/jenkins",
                f"REGISTRY_USERNAME={registry_config['username']}",
                f"REGISTRY_PASSWORD={registry_config['password']}",
                f"DOCKER_HOST=unix:///var/run/docker.sock",
                f"DOCKER_CERT_PATH=/certs/client",
                f"DOCKER_TLS_VERIFY=1"
            ],
            networks_advanced=[ContainerNetworksAdvancedArgs(
                name=network_ids["mgmt"],
                aliases=["jenkins"]
            )],
            healthcheck={
                "test": ["CMD", "curl", "-f", "http://localhost:8080 || exit 1"],
                "interval": "30s",
                "timeout": "10s",
                "retries": "3",
                "start_period": "60s"
            },
            restart="unless-stopped",
            opts=ResourceOptions(parent=self)
        )

        self.register_outputs({
            "external_url": "http://192.168.3.26:8080",
            "internal_url": "http://jenkins:8080",
            "container_id": self.jenkins.id
        }) 
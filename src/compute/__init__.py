from pulumi import ComponentResource, ResourceOptions, Output
from pulumi_docker import Image, Container, Volume, ContainerCapabilitiesArgs
from typing import Dict, List

class ContainerStack(ComponentResource):
    def __init__(self, 
                 name: str,
                 network_ids: Dict[str, Output[str]],
                 registry_config: Dict[str, str] = None,
                 environment: str = "dev",
                 opts: ResourceOptions = None):
        super().__init__("addi-aire:compute:ContainerStack", name, None, opts)

        # Create volumes
        self.jenkins_volume = Volume("jenkins-data",
            name="jenkins_home",
            opts=ResourceOptions(parent=self)
        )

        # Jenkins container with plugins and configuration
        self.jenkins = Container("jenkins",
            image="jenkins/jenkins:lts-jdk17",
            name="jenkins",
            ports=[{
                "internal": 8080,
                "external": 8080
            }, {
                "internal": 50000,
                "external": 50000
            }],
            volumes=[{
                "volume_name": self.jenkins_volume.name,
                "container_path": "/var/jenkins_home"
            }],
            networks_advanced=[{
                "name": network_ids["mgmt"]
            }],
            envs=[
                "JAVA_OPTS=-Xmx2g -Djava.awt.headless=true",
                "TZ=UTC"
            ],
            healthcheck={
                "test": ["CMD", "curl", "-f", "http://localhost:8080 || exit 1"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "60s"
            },
            restart="unless-stopped",
            opts=ResourceOptions(parent=self)
        )

        self.register_outputs({
            "external_url": "http://192.168.3.26:8080",
            "internal_url": "http://jenkins:8080",
            "container_ips": {
                "jenkins": self.jenkins.networks_advanced.apply(
                    lambda networks: networks[0].get("ip_address", "pending") if networks else None
                )
            }
        }) 
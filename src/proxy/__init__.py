from pulumi import ComponentResource, ResourceOptions
from pulumi_docker import Container, Volume, ContainerPortArgs, ContainerMountArgs
from typing import Dict, List
import os

class NginxProxy(ComponentResource):
    def __init__(self, 
                 name: str,
                 network_id: str,
                 config_dir: str = "/home/james/pulumi/config/nginx",
                 opts: ResourceOptions = None):
        super().__init__("addi-aire:proxy:NginxProxy", name, None, opts)
        
        # Create volumes for Nginx
        self.config_volume = Volume(f"{name}-config",
            name="nginx_config",
            opts=ResourceOptions(parent=self)
        )
        
        self.logs_volume = Volume(f"{name}-logs",
            name="nginx_logs",
            opts=ResourceOptions(parent=self)
        )

        # Ensure SSL directory exists
        os.makedirs(f"{config_dir}/ssl", exist_ok=True)
        os.makedirs(f"{config_dir}/cloudflare", exist_ok=True)

        # Nginx container
        self.nginx = Container("nginx",
            image="nginx:mainline",
            ports=[
                ContainerPortArgs(
                    internal=80,
                    external=80
                ),
                ContainerPortArgs(
                    internal=443,
                    external=443
                )
            ],
            volumes=[
                # Main nginx config
                ContainerMountArgs(
                    host_path=f"{config_dir}/nginx.conf",
                    container_path="/etc/nginx/nginx.conf",
                    read_only=True
                ),
                # App configurations
                ContainerMountArgs(
                    host_path=f"{config_dir}/conf.d",
                    container_path="/etc/nginx/conf.d",
                    read_only=True
                ),
                # SSL certificates
                ContainerMountArgs(
                    host_path=f"{config_dir}/ssl",
                    container_path="/etc/nginx/ssl",
                    read_only=True
                ),
                # Cloudflare configuration
                ContainerMountArgs(
                    host_path=f"{config_dir}/cloudflare",
                    container_path="/etc/nginx/cloudflare",
                    read_only=True
                ),
                # MIME types
                ContainerMountArgs(
                    host_path=f"{config_dir}/mime.types",
                    container_path="/etc/nginx/mime.types",
                    read_only=True
                ),
                # Logs
                ContainerMountArgs(
                    volume_name=self.logs_volume.name,
                    container_path="/var/log/nginx"
                )
            ],
            envs=[
                "NGINX_ENVSUBST_TEMPLATE_DIR=/etc/nginx/templates",
                "NGINX_ENVSUBST_TEMPLATE_SUFFIX=.template",
                "NGINX_ENVSUBST_OUTPUT_DIR=/etc/nginx/conf.d/apps",
                "TZ=UTC"
            ],
            network_id=network_id,
            restart="unless-stopped",
            healthcheck={
                "test": ["CMD", "curl", "-f", "http://localhost/health"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3
            },
            capabilities={
                "add": ["NET_ADMIN"]
            },
            command=[
                "sh", "-c",
                """
                # Wait for Cloudflare config
                while [ ! -f /etc/nginx/cloudflare/cloudflare.conf ]; do
                    echo "Waiting for Cloudflare configuration..."
                    sleep 5
                done
                
                # Start Nginx
                nginx -g 'daemon off;'
                """
            ],
            opts=ResourceOptions(parent=self)
        )
        
        self.register_outputs({
            "container_id": self.nginx.id,
            "config_volume": self.config_volume.name,
            "logs_volume": self.logs_volume.name
        }) 
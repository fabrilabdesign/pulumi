from pulumi import ComponentResource, ResourceOptions
from pulumi_docker import Container, Volume

class DnsStack(ComponentResource):
    def __init__(self, name: str, network_id: str, opts: ResourceOptions = None):
        super().__init__("addi-aire:dns:DnsStack", name, None, opts)
        
        # Zone files volume
        self.zone_volume = Volume("bind-zones", 
            name="bind9_zones",
            opts=ResourceOptions(parent=self)
        )

        # Bind9 container
        self.bind = Container("bind9",
            image="ubuntu/bind9:latest",
            ports=[{"internal": "53", "external": "53", "protocol": "tcp"},
                   {"internal": "53", "external": "53", "protocol": "udp"}],
            volumes=[{
                "volume_name": self.zone_volume.name,
                "container_path": "/etc/bind/zones"
            }],
            command=[
                "named", "-g", "-c", "/etc/bind/named.conf",
                "-u", "bind"
            ],
            network_id=network_id,
            opts=ResourceOptions(parent=self)
        )

        self.register_outputs({
            "dns_server_ip": self.bind.network_settings.ip_address
        }) 
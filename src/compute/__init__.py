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

        self.nginx_volume = Volume("nginx-data",
            name="nginx_data",
            opts=ResourceOptions(parent=self)
        )

        # Nginx configuration
        nginx_config = """
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    multi_accept on;
}

http {
    include mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log main;

    # Basic Settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;

    # Gzip Settings
    gzip on;
    gzip_disable "msie6";
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Jenkins upstream
    upstream jenkins {
        server 192.168.3.26:8080;
        keepalive 32;
    }

    # HTTP Server
    server {
        listen 80;
        server_name _;
        
        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\\n";
        }

        # Redirect root to Jenkins
        location = / {
            return 301 /jenkins/;
        }

        # Jenkins proxy
        location /jenkins {
            proxy_pass http://jenkins;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Connection "";
            proxy_http_version 1.1;
            proxy_buffering off;
            proxy_request_buffering off;
            proxy_max_temp_file_size 0;
            client_max_body_size 0;
            
            # Remove any existing Connection header
            proxy_set_header Connection "";
            
            # Required for Jenkins websocket agents
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }

    # HTTPS Server
    server {
        listen 443 ssl;
        server_name _;
        
        ssl_certificate ssl/server.crt;
        ssl_certificate_key ssl/server.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_timeout 1d;
        ssl_session_cache shared:SSL:50m;
        ssl_session_tickets off;
        
        location /jenkins {
            proxy_pass http://jenkins;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_buffering off;
            proxy_request_buffering off;
            proxy_max_temp_file_size 0;
            client_max_body_size 0;
            
            # Required for Jenkins websocket agents
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}"""

        # Create nginx config file
        self.nginx_config = Container("nginx-config",
            image="alpine",
            command=[
                "/bin/sh", "-c",
                f"""
                mkdir -p /config/nginx/ssl /config/nginx/conf.d
                # Generate self-signed cert for dev
                apk add --no-cache openssl curl
                openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                    -keyout /config/nginx/ssl/server.key \
                    -out /config/nginx/ssl/server.crt \
                    -subj "/C=US/ST=CA/L=SanFrancisco/O=Addi-Aire/CN=localhost"
                
                # Copy mime.types from nginx image
                wget -O /config/nginx/mime.types https://raw.githubusercontent.com/nginx/nginx/master/conf/mime.types
                
                cat > /config/nginx/nginx.conf << 'EOL'
                {nginx_config}
                EOL

                chmod 644 /config/nginx/nginx.conf
                chmod 644 /config/nginx/mime.types
                chmod 600 /config/nginx/ssl/server.key
                chmod 644 /config/nginx/ssl/server.crt
                """
            ],
            volumes=[{
                "host_path": "/home/james/pulumi/config/nginx",
                "container_path": "/config/nginx"
            }],
            networks_advanced=[{
                "name": network_ids["mgmt"]
            }],
            opts=ResourceOptions(parent=self)
        )

        # Create nginx runtime directories
        self.nginx_dirs = Container("nginx-dirs",
            image="alpine",
            command=[
                "/bin/sh", "-c",
                """
                mkdir -p /tmp/nginx/{cache,run,logs}
                chmod -R 777 /tmp/nginx
                """
            ],
            volumes=[{
                "host_path": "/tmp/nginx",
                "container_path": "/tmp/nginx"
            }],
            networks_advanced=[{
                "name": network_ids["mgmt"]
            }],
            opts=ResourceOptions(parent=self)
        )

        # Jenkins container with plugins and configuration
        self.jenkins = Container("jenkins",
            image="jenkins/jenkins:lts-jdk17",
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
            networks_advanced=[
                {"name": network_ids["mgmt"]},
                {"name": network_ids["prod"]}
            ],
            envs=[
                "JENKINS_OPTS=--prefix=/jenkins",
                "JAVA_OPTS=-Djenkins.install.runSetupWizard=false -Dhudson.model.DirectoryBrowserSupport.CSP=\"\"",
                "JENKINS_URL=http://192.168.3.26:8080/jenkins",
                "TZ=UTC"
            ],
            healthcheck={
                "test": ["CMD", "curl", "-f", "http://localhost:8080/jenkins/prometheus || exit 1"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "60s"
            },
            command=["/bin/sh", "-c", "chown -R jenkins:jenkins /var/jenkins_home && /usr/local/bin/jenkins.sh"],
            capabilities=ContainerCapabilitiesArgs(
                adds=["IPC_LOCK"]
            ),
            restart="unless-stopped",
            opts=ResourceOptions(depends_on=[self.nginx_config], parent=self)
        )

        # Nginx container with reverse proxy config
        self.nginx = Container("nginx",
            image="nginx:latest",
            ports=[{
                "internal": 80,
                "external": 80
            }, {
                "internal": 443,
                "external": 443
            }],
            volumes=[{
                "host_path": "/home/james/pulumi/config/nginx",
                "container_path": "/etc/nginx",
                "read_only": False
            }, {
                "container_path": "/var/cache/nginx",
                "host_path": "/tmp/nginx/cache"
            }, {
                "container_path": "/var/run",
                "host_path": "/tmp/nginx/run"
            }, {
                "container_path": "/var/log/nginx",
                "host_path": "/tmp/nginx/logs"
            }],
            networks_advanced=[{
                "name": network_ids["prod"]
            }],
            healthcheck={
                "test": ["CMD", "curl", "-f", "http://localhost/health || exit 1"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "30s"
            },
            envs=[
                "NGINX_ENVSUBST_TEMPLATE_DIR=/etc/nginx/conf.d",
                "NGINX_ENVSUBST_TEMPLATE_SUFFIX=.conf",
                "NGINX_ENVSUBST_OUTPUT_DIR=/etc/nginx/conf.d"
            ],
            command=["/bin/sh", "-c", "nginx -g 'daemon off;'"],
            opts=ResourceOptions(depends_on=[self.nginx_config, self.nginx_dirs, self.jenkins], parent=self)
        )

        self.register_outputs({
            "jenkins_url": "http://localhost:8080/jenkins",
            "nginx_url": "http://localhost",
            "container_ips": {
                "jenkins": self.jenkins.networks_advanced.apply(
                    lambda networks: networks[0].get("ip_address", "pending") if networks else None
                ),
                "nginx": self.nginx.networks_advanced.apply(
                    lambda networks: networks[0].get("ip_address", "pending") if networks else None
                )
            }
        }) 
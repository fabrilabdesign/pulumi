from pulumi import ComponentResource, ResourceOptions, Output
from pulumi_docker import Container, Volume
from typing import Dict

class MonitoringStack(ComponentResource):
    def __init__(self, 
                 name: str,
                 network_ids: Dict[str, Output[str]],
                 opts: ResourceOptions = None):
        super().__init__("addi-aire:monitoring:MonitoringStack", name, None, opts)

        # Create volumes
        volumes = {
            "elasticsearch": Volume("elasticsearch-data", name="elasticsearch_data", opts=ResourceOptions(parent=self)),
            "grafana": Volume("grafana-data", name="grafana_data", opts=ResourceOptions(parent=self)),
            "prometheus": Volume("prometheus-data", name="prometheus_data", opts=ResourceOptions(parent=self)),
            "alertmanager": Volume("alertmanager-data", name="alertmanager_data", opts=ResourceOptions(parent=self))
        }

        # Prometheus
        self.prometheus = Container("prometheus",
            image="prom/prometheus:latest",
            ports=[{"internal": 9090, "external": 9090}],
            volumes=[{
                "volume_name": volumes["prometheus"].name,
                "container_path": "/prometheus",
                "read_only": False
            }, {
                "container_path": "/etc/prometheus",
                "host_path": "/home/james/pulumi/config/prometheus",
                "read_only": True
            }],
            networks_advanced=[{
                "name": network_ids["mgmt"]
            }],
            command=[
                "--config.file=/etc/prometheus/prometheus.yml",
                "--storage.tsdb.path=/prometheus",
                "--web.console.libraries=/usr/share/prometheus/console_libraries",
                "--web.console.templates=/usr/share/prometheus/consoles",
                "--web.enable-lifecycle",
                "--web.enable-admin-api",
                "--web.external-url=http://192.168.3.26:9090",
                "--storage.tsdb.retention.time=15d",
                "--web.listen-address=0.0.0.0:9090"
            ],
            healthcheck={
                "test": ["CMD", "curl", "-f", "http://prometheus:9090/-/healthy", "-O", "/dev/null"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3
            },
            envs=["TZ=UTC"],
            restart="unless-stopped",
            opts=ResourceOptions(parent=self)
        )

        # Alertmanager
        self.alertmanager = Container("alertmanager",
            image="prom/alertmanager:latest",
            ports=[{"internal": 9093, "external": 9093}],
            volumes=[{
                "volume_name": volumes["alertmanager"].name,
                "container_path": "/alertmanager"
            }],
            networks_advanced=[{
                "name": network_ids["mgmt"]
            }],
            command=[
                "--config.file=/etc/alertmanager/alertmanager.yml",
                "--storage.path=/alertmanager"
            ],
            healthcheck={
                "test": ["CMD", "curl", "-f", "http://alertmanager:9093/-/healthy"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3
            },
            restart="unless-stopped",
            opts=ResourceOptions(parent=self)
        )

        # Node Exporter
        self.node_exporter = Container("node-exporter",
            image="prom/node-exporter:latest",
            ports=[{"internal": 9100, "external": 9100}],
            networks_advanced=[{
                "name": network_ids["mgmt"]
            }],
            volumes=[
                {"host_path": "/proc", "container_path": "/host/proc", "read_only": True},
                {"host_path": "/sys", "container_path": "/host/sys", "read_only": True},
                {"host_path": "/", "container_path": "/rootfs", "read_only": True}
            ],
            command=[
                "--path.procfs=/host/proc",
                "--path.sysfs=/host/sys",
                "--path.rootfs=/rootfs",
                "--collector.filesystem.ignored-mount-points=^/(sys|proc|dev|host|etc)($|/)",
                "--web.listen-address=:9100"
            ],
            healthcheck={
                "test": ["CMD", "wget", "-q", "http://node-exporter:9100/metrics"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3
            },
            restart="unless-stopped",
            opts=ResourceOptions(parent=self)
        )

        # Elasticsearch
        self.elasticsearch = Container("elasticsearch",
            image="elasticsearch:8.12.1",
            name="elasticsearch",
            ports=[{
                "internal": 9200,
                "external": 9200
            }],
            volumes=[{
                "volume_name": volumes["elasticsearch"].name,
                "container_path": "/usr/share/elasticsearch/data"
            }],
            networks_advanced=[{
                "name": network_ids["mgmt"]
            }],
            envs=[
                "discovery.type=single-node",
                "xpack.security.enabled=false",
                "ES_JAVA_OPTS=-Xms512m -Xmx512m",
                "network.host=0.0.0.0",
                "http.port=9200"
            ],
            healthcheck={
                "test": ["CMD", "curl", "-f", "http://localhost:9200/_cluster/health || exit 1"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "60s"
            },
            restart="unless-stopped",
            opts=ResourceOptions(parent=self)
        )

        # Kibana
        self.kibana = Container("kibana",
            image="kibana:8.12.1",
            name="kibana",
            ports=[{
                "internal": 5601,
                "external": 5601
            }],
            networks_advanced=[{
                "name": network_ids["mgmt"]
            }],
            envs=[
                "ELASTICSEARCH_HOSTS=http://elasticsearch:9200",
                "SERVER_NAME=kibana",
                "SERVER_HOST=0.0.0.0"
            ],
            healthcheck={
                "test": ["CMD", "curl", "-f", "http://localhost:5601/api/status || exit 1"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "60s"
            },
            restart="unless-stopped",
            opts=ResourceOptions(parent=self)
        )

        # Logstash
        self.logstash = Container("logstash",
            image="docker.elastic.co/logstash/logstash:8.12.1",
            ports=[
                {"internal": 5044, "external": 5044},
                {"internal": 9600, "external": 9600}
            ],
            networks_advanced=[{
                "name": network_ids["mgmt"]
            }],
            envs=[
                "ELASTICSEARCH_URL=http://elasticsearch:9200",
                "XPACK_MONITORING_ELASTICSEARCH_HOSTS=http://elasticsearch:9200"
            ],
            healthcheck={
                "test": ["CMD", "curl", "-f", "http://logstash:9600"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3
            },
            restart="unless-stopped",
            opts=ResourceOptions(parent=self)
        )

        # Grafana with pre-configured datasources and dashboards
        self.grafana = Container("grafana",
            image="grafana/grafana:latest",
            ports=[{"internal": 3000, "external": 3001}],
            volumes=[{
                "volume_name": volumes["grafana"].name,
                "container_path": "/var/lib/grafana"
            }, {
                "container_path": "/etc/grafana/provisioning/datasources",
                "host_path": "/home/james/pulumi/config/grafana/provisioning/datasources"
            }, {
                "container_path": "/etc/grafana/provisioning/dashboards",
                "host_path": "/home/james/pulumi/config/grafana/provisioning/dashboards"
            }],
            networks_advanced=[{
                "name": network_ids["mgmt"]
            }],
            envs=[
                "GF_SECURITY_ADMIN_PASSWORD=admin",
                "GF_USERS_ALLOW_SIGN_UP=false",
                "GF_INSTALL_PLUGINS=grafana-piechart-panel,grafana-worldmap-panel,grafana-clock-panel,grafana-simple-json-datasource",
                "GF_AUTH_ANONYMOUS_ENABLED=true",
                "GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer",
                "GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH=/etc/grafana/provisioning/dashboards/overview.json",
                "GF_PATHS_PROVISIONING=/etc/grafana/provisioning",
                "GF_FEATURE_TOGGLES_ENABLE=publicDashboards traceqlEditor",
                "GF_UNIFIED_ALERTING_ENABLED=true",
                "GF_SERVER_HTTP_PORT=3000",
                "GF_SERVER_DOMAIN=192.168.3.26",
                "GF_SERVER_ROOT_URL=http://192.168.3.26:3001"
            ],
            healthcheck={
                "test": ["CMD", "wget", "-q", "http://grafana:3000/api/health"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "30s"
            },
            command=["/bin/sh", "-c", """
                chown -R grafana:grafana /var/lib/grafana
                chmod -R 755 /var/lib/grafana
                /run.sh
            """],
            user="root",
            restart="unless-stopped",
            opts=ResourceOptions(parent=self)
        )

        # Comprehensive health check container
        self.health_check = Container("health-check",
            image="alpine/curl",
            command=[
                "sh", "-c",
                """
                while true; do
                    # Infrastructure checks
                    curl -f http://jenkins:8080/jenkins || exit 1
                    curl -f http://nginx/health || exit 1
                    
                    # Monitoring stack checks
                    curl -f http://elasticsearch:9200/_cluster/health || exit 1
                    curl -f http://kibana:5601/api/status || exit 1
                    curl -f http://grafana:3000/api/health || exit 1
                    wget -q http://prometheus:9090/-/healthy || exit 1
                    wget -q http://alertmanager:9093/-/healthy || exit 1
                    wget -q http://node-exporter:9100/metrics || exit 1
                    curl -f http://logstash:9600 || exit 1
                    
                    # Log successful check
                    echo "[$(date)] All services healthy"
                    
                    # Resource checks
                    free -m
                    df -h
                    top -b -n 1
                    
                    sleep 30
                done
                """
            ],
            networks_advanced=[
                {"name": network_ids["mgmt"]},
                {"name": network_ids["prod"]},
                {"name": network_ids["dev"]}
            ],
            restart="always",
            opts=ResourceOptions(parent=self)
        )

        # cAdvisor for container metrics
        self.cadvisor = Container("cadvisor",
            image="gcr.io/cadvisor/cadvisor:v0.47.2",
            ports=[{"internal": 8080, "external": 8082}],
            networks_advanced=[{
                "name": network_ids["mgmt"]
            }],
            volumes=[
                {"host_path": "/", "container_path": "/rootfs", "read_only": True},
                {"host_path": "/var/run", "container_path": "/var/run", "read_only": True},
                {"host_path": "/sys", "container_path": "/sys", "read_only": True},
                {"host_path": "/var/lib/docker", "container_path": "/var/lib/docker", "read_only": True},
                {"host_path": "/dev/disk", "container_path": "/dev/disk", "read_only": True}
            ],
            healthcheck={
                "test": ["CMD", "wget", "-q", "http://cadvisor:8080/healthz"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3
            },
            privileged=True,
            opts=ResourceOptions(parent=self)
        )

        # Loki for log aggregation
        self.loki = Container("loki",
            image="grafana/loki:2.9.3",
            ports=[{"internal": 3100, "external": 3100}],
            volumes=[{
                "volume_name": volumes["grafana"].name,
                "container_path": "/loki"
            }, {
                "container_path": "/etc/loki",
                "host_path": "/home/james/pulumi/config/loki",
                "read_only": True
            }],
            networks_advanced=[{
                "name": network_ids["mgmt"]
            }],
            command=[
                "-config.file=/etc/loki/local-config.yaml",
                "-target=all"
            ],
            healthcheck={
                "test": ["CMD", "wget", "-q", "http://loki:3100/ready"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3
            },
            restart="unless-stopped",
            opts=ResourceOptions(parent=self)
        )

        # Promtail to ship logs to Loki
        self.promtail = Container("promtail",
            image="grafana/promtail:2.9.3",
            volumes=[
                {"host_path": "/var/log", "container_path": "/var/log", "read_only": True},
                {"host_path": "/var/lib/docker/containers", "container_path": "/var/lib/docker/containers", "read_only": True},
                {"host_path": "/home/james/pulumi/config/promtail", "container_path": "/etc/promtail", "read_only": True}
            ],
            networks_advanced=[{
                "name": network_ids["mgmt"]
            }],
            command=[
                "-config.file=/etc/promtail/config.yml",
                f"-client.url=http://loki:3100/loki/api/v1/push"
            ],
            healthcheck={
                "test": ["CMD", "wget", "-q", "http://promtail:9080/ready"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3
            },
            restart="unless-stopped",
            privileged=True,
            opts=ResourceOptions(parent=self)
        )

        # Tempo for distributed tracing
        self.tempo = Container("tempo",
            image="grafana/tempo:2.3.1",
            ports=[
                {"internal": 3200, "external": 3200},  # HTTP
                {"internal": 4317, "external": 4317},  # OTLP gRPC
                {"internal": 4318, "external": 4318}   # OTLP HTTP
            ],
            volumes=[{
                "volume_name": volumes["grafana"].name,
                "container_path": "/tmp/tempo"
            }, {
                "container_path": "/etc/tempo",
                "host_path": "/home/james/pulumi/config/tempo",
                "read_only": True
            }],
            networks_advanced=[{
                "name": network_ids["mgmt"]
            }],
            command=[
                "-config.file=/etc/tempo/tempo.yaml",
                "-target=all"
            ],
            healthcheck={
                "test": ["CMD", "wget", "-q", "http://tempo:3200/ready"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3
            },
            restart="unless-stopped",
            opts=ResourceOptions(parent=self)
        )

        self.register_outputs({
            "urls": {
                "elasticsearch": "http://192.168.3.26:9200",
                "kibana": "http://192.168.3.26:5601",
                "grafana": "http://192.168.3.26:3001",
                "prometheus": "http://192.168.3.26:9090",
                "alertmanager": "http://192.168.3.26:9093",
                "node_exporter": "http://192.168.3.26:9100"
            },
            "ports": {
                "logstash": 5044,
                "logstash_monitoring": 9600
            },
            "health_check_id": self.health_check.id
        }) 
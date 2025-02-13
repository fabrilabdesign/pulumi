from pulumi import ComponentResource, ResourceOptions, Output
from pulumi_docker import Volume, Container
from typing import Dict, Union

class StorageStack(ComponentResource):
    def __init__(self, 
                 name: str,
                 network_ids: Dict[str, Union[str, Output[str]]],
                 opts: ResourceOptions = None):
        super().__init__("addi-aire:storage:StorageStack", name, None, opts)

        # Create volumes
        volumes = {
            "backup": Volume("backup-data", name="backup_data", opts=ResourceOptions(parent=self)),
            "archive": Volume("archive-data", name="archive_data", opts=ResourceOptions(parent=self))
        }

        # # Backup service with enhanced features
        # self.backup_service = Container("backup-service",
        #     image="alpine",
        #     command=["/bin/sh", "-c", "apk add --no-cache tar gzip curl jq pigz && while true; do echo \"[$(date)] Starting backup process...\"; BACKUP_DATE=$(date +%Y%m%d_%H%M%S); BACKUP_DIR=\"/backup/$BACKUP_DATE\"; mkdir -p $BACKUP_DIR; echo \"Backing up Jenkins...\"; pigz -c /jenkins_home > $BACKUP_DIR/jenkins.tar.gz; echo \"Backing up Nginx configs...\"; tar czf $BACKUP_DIR/nginx.tar.gz /nginx_data; echo \"Creating Elasticsearch snapshot...\"; curl -X PUT \"http://elasticsearch:9200/_snapshot/backup\" -H \"Content-Type: application/json\" -d '{\"type\":\"fs\",\"settings\":{\"location\":\"/backup/elasticsearch\"}}'; curl -X PUT \"http://elasticsearch:9200/_snapshot/backup/$BACKUP_DATE?wait_for_completion=true\"; echo \"Backing up Grafana...\"; tar czf $BACKUP_DIR/grafana.tar.gz /grafana_data; echo \"Backing up Prometheus data...\"; tar czf $BACKUP_DIR/prometheus.tar.gz /prometheus_data; echo \"Creating backup manifest...\"; echo \"{\\\"timestamp\\\":\\\"$(date -Iseconds)\\\",\\\"components\\\":{\\\"jenkins\\\":{\\\"size\\\":\\\"$(du -sh $BACKUP_DIR/jenkins.tar.gz | cut -f1)\\\"},\\\"nginx\\\":{\\\"size\\\":\\\"$(du -sh $BACKUP_DIR/nginx.tar.gz | cut -f1)\\\"},\\\"elasticsearch\\\":{\\\"size\\\":\\\"$(du -sh /backup/elasticsearch | cut -f1)\\\"},\\\"grafana\\\":{\\\"size\\\":\\\"$(du -sh $BACKUP_DIR/grafana.tar.gz | cut -f1)\\\"},\\\"prometheus\\\":{\\\"size\\\":\\\"$(du -sh $BACKUP_DIR/prometheus.tar.gz | cut -f1)\\\"}}}\" > $BACKUP_DIR/manifest.json; echo \"Archiving old backups...\"; find /backup -maxdepth 1 -type d -mtime +7 -exec mv {} /archive/ \\;; echo \"Cleaning up old archives...\"; find /archive -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \\;; echo \"[$(date)] Backup completed successfully\"; echo \"Next backup in 24 hours...\"; sleep 86400; done"],
        #     volumes=[
        #         {
        #             "volume_name": volumes["backup"].name,
        #             "container_path": "/backup"
        #         },
        #         {
        #             "volume_name": volumes["archive"].name,
        #             "container_path": "/archive"
        #         },
        #         {
        #             "volume_name": "jenkins_home",
        #             "container_path": "/jenkins_home"
        #         },
        #         {
        #             "volume_name": "nginx_data",
        #             "container_path": "/nginx_data"
        #         },
        #         {
        #             "volume_name": "elasticsearch_data",
        #             "container_path": "/elasticsearch_data"
        #         },
        #         {
        #             "volume_name": "grafana_data",
        #             "container_path": "/grafana_data"
        #         },
        #         {
        #             "volume_name": "prometheus_data",
        #             "container_path": "/prometheus_data"
        #         }
        #     ],
        #     networks_advanced=[{
        #         "name": network_ids["mgmt"]
        #     }],
        #     restart="always",
        #     envs=[
        #         "TZ=UTC",
        #         "BACKUP_RETENTION_DAYS=7",
        #         "ARCHIVE_RETENTION_DAYS=30"
        #     ],
        #     opts=ResourceOptions(parent=self)
        # )

        # # Recovery service for disaster recovery
        # self.recovery_service = Container("recovery-service",
        #     image="alpine",
        #     command=[
        #         "sh", "-c",
        #         """
        #         # Install required tools
        #         apk add --no-cache tar gzip curl jq pigz

        #         # Start a simple recovery API server
        #         while true; do
        #             nc -l -p 8080 | while read line; do
        #                 if echo "$line" | grep -q "GET /backups"; then
        #                     # List available backups
        #                     echo -e "HTTP/1.1 200 OK\\n"
        #                     find /backup -maxdepth 1 -type d -name "2*" | jq -R -s 'split("\\n")[:-1]'
        #                 elif echo "$line" | grep -q "POST /recover/"; then
        #                     # Extract backup ID from request
        #                     BACKUP_ID=$(echo "$line" | sed 's/.*\\/recover\\/\\([^\\/ ]\\+\\).*/\\1/')
        #                     if [ -d "/backup/$BACKUP_ID" ]; then
        #                         echo "Starting recovery from backup $BACKUP_ID..."
                                
        #                         # Stop services (via Docker API)
        #                         curl --unix-socket /var/run/docker.sock http://v1.41/containers/jenkins/stop
        #                         curl --unix-socket /var/run/docker.sock http://v1.41/containers/nginx/stop
        #                         curl --unix-socket /var/run/docker.sock http://v1.41/containers/elasticsearch/stop
        #                         curl --unix-socket /var/run/docker.sock http://v1.41/containers/grafana/stop
                                
        #                         # Restore data
        #                         cd /backup/$BACKUP_ID
        #                         pigz -dc jenkins.tar.gz > /jenkins_home
        #                         tar xzf nginx.tar.gz -C /
        #                         tar xzf grafana.tar.gz -C /
        #                         tar xzf prometheus.tar.gz -C /
                                
        #                         # Restore Elasticsearch snapshot
        #                         curl -X POST "http://elasticsearch:9200/_snapshot/backup/$BACKUP_ID/_restore"
                                
        #                         # Start services
        #                         curl --unix-socket /var/run/docker.sock http://v1.41/containers/jenkins/start
        #                         curl --unix-socket /var/run/docker.sock http://v1.41/containers/nginx/start
        #                         curl --unix-socket /var/run/docker.sock http://v1.41/containers/elasticsearch/start
        #                         curl --unix-socket /var/run/docker.sock http://v1.41/containers/grafana/start
                                
        #                         echo -e "HTTP/1.1 200 OK\\n\\nRecovery completed successfully"
        #                     else
        #                         echo -e "HTTP/1.1 404 Not Found\\n\\nBackup not found"
        #                     fi
        #                 else
        #                     echo -e "HTTP/1.1 400 Bad Request\\n\\nInvalid request"
        #                 fi
        #             done
        #         done
        #         """
        #     ],
        #     volumes=[
        #         {
        #             "volume_name": volumes["backup"].name,
        #             "container_path": "/backup"
        #         },
        #         {
        #             "volume_name": volumes["archive"].name,
        #             "container_path": "/archive"
        #         },
        #         {
        #             "host_path": "/var/run/docker.sock",
        #             "container_path": "/var/run/docker.sock"
        #         }
        #     ],
        #     networks_advanced=[{
        #         "name": network_ids["mgmt"]
        #     }],
        #     ports=[{
        #         "internal": 8080,
        #         "external": 8081
        #     }],
        #     restart="always",
        #     opts=ResourceOptions(parent=self)
        # )

        self.register_outputs({
            "volumes": {
                "backup": volumes["backup"].name,
                "archive": volumes["archive"].name
            }
            # "services": {
            #     "backup": self.backup_service.id,
            #     "recovery": self.recovery_service.id
            # },
            # "recovery_api": "http://192.168.3.26:8081"
        }) 
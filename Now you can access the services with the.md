Now you can access the services with these credentials:
Elasticsearch (http://192.168.3.26:9200)
Username: elastic
Password: addi-aire-elastic
Kibana (http://192.168.3.26:5601)
Username: elastic
Password: addi-aire-elastic
You don't need to run the enrollment token command since we've configured the connection between Kibana and Elasticsearch using environment variables. The services should be able to communicate with each other automatically.
Let me know if you need help setting up any indices or visualizations in Kibana, or if you'd like to configure any other services.

I'll help you with the login credentials and setup for each service. Here's how to access them:
Jenkins (http://192.168.3.26:8080/jenkins)
Since we disabled the setup wizard (jenkins.install.runSetupWizard=false), you can log in with:
Username: admin
Password: Check the initial password in Jenkins logs:
Grafana (http://192.168.3.26:3001)
Default credentials:
Username: admin
Password: admin
You'll be prompted to change the password on first login
Kibana (http://192.168.3.26:5601)
No authentication required (we disabled xpack security)
Direct access to the UI
Vault (http://192.168.3.26:8200)
Token: addi-aire-now (set in the code)
Prometheus (http://192.168.3.26:9090)
No authentication required
Direct access to the UI
Alertmanager (http://192.168.3.26:9093)
No authentication required
Direct access to the UI
Would you like me to help you set up any specific service or configure additional security? We should probably:
Enable proper authentication for Prometheus/Alertmanager
Set up proper SSL certificates
Configure Grafana datasources for Prometheus
Set up Elasticsearch indices in Kibana
Let me know which area you'd like to tackle first.

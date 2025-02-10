storage "raft" {
  path = "/vault/data"
  node_id = "node1"
}

listener "tcp" {
  address = "0.0.0.0:8200"
  tls_disable = 1  # Enable TLS in production
}

api_addr = "http://vault.addi-aire:8200"
cluster_addr = "https://vault.addi-aire:8201"
ui = true 
# Network Engineer Cheat Sheet - Addi-Aire Infrastructure

## Core Network
- Router: Ubiquiti UDM Pro (192.168.2.1)
- Primary Network: 192.168.3.0/24
- Management Network: 192.168.2.0/24

## Key Server IPs
- Primary App Server: 192.168.3.26
- Development Server: 192.168.3.147
- ESXi Host: 192.168.2.236
- APC UPS: 192.168.2.165

## IP Ranges
- Production Servers: 192.168.3.11 - 192.168.3.20
- Virtual Machines: 192.168.3.100 - 192.168.3.150
- Dev Workstations: 192.168.3.200 - 192.168.3.250
- Network Devices: 192.168.3.251 - 192.168.3.254

## Critical Ports
- Nginx: 80, 443
- Jenkins Master: 8080
- Jenkins Agents: 50000-51000
- React Dev: 3000
- SSH: 22 (or custom)
- Docker API: 2375/2376 (localhost only)

## Security Checklist
1. SSH Configuration
   - Key-based auth only
   - IP whitelisting
   - Custom port recommended

2. Firewall Rules
   - Allow 80/443 inbound
   - Restrict SSH access
   - Container network isolation
   - Stateful inspection enabled

3. Network Segmentation
   - Production VLAN
   - Development VLAN
   - Management VLAN

## Monitoring Points
- Router health: 192.168.2.1
- ESXi status: 192.168.2.236
- UPS monitoring: 192.168.2.165
- Server metrics: Deploy on each host
- Container health: Docker stats

## Quick Commands
```bash
# Network Diagnostics
ip addr show                    # Show IP addresses
ip route show                   # Show routing table
ss -tuln                       # List open ports
ping -c 4 192.168.2.1          # Test router connectivity
traceroute 192.168.3.26        # Trace route to app server

# Docker Network
docker network ls              # List networks
docker network inspect bridge  # Inspect default network
docker container stats        # Monitor container resources

# Nginx
nginx -t                      # Test configuration
systemctl status nginx        # Check service status
nginx -s reload              # Reload configuration

# Security
ufw status                    # Check firewall status
iptables -L                  # List firewall rules
fail2ban-client status       # Check intrusion prevention
```

## Emergency Procedures
1. Network Down
   - Check UPS status (192.168.2.165)
   - Verify router power (192.168.2.1)
   - Check physical connections
   - Review router logs

2. Server Unreachable
   - Ping gateway (192.168.2.1)
   - Check server power state
   - Verify network config
   - Review system logs

3. Service Disruption
   - Check container status
   - Verify Nginx config
   - Review application logs
   - Monitor resource usage
# Linux Systems Administration & DevOps Cheat Sheet

## System Information & Monitoring

### System Stats
```bash
# System Overview
uname -a                    # Kernel & system info
lsb_release -a             # Distribution info
hostnamectl                # System hostname info
uptime                     # System uptime

# Hardware Info
lscpu                      # CPU info
free -h                    # Memory usage
df -h                      # Disk usage
lsblk                      # Block devices
lspci                      # PCI devices
dmidecode                  # Hardware info
```

### Resource Monitoring
```bash
# Real-time Monitoring
top                        # Process overview
htop                       # Enhanced top
iotop                      # I/O monitoring
iftop                      # Network monitoring
nethogs                    # Per-process network

# System Load
vmstat 1                   # Virtual memory stats
mpstat 1                   # CPU stats
iostat -xz 1              # I/O stats
```

## Storage Management

### Disk Operations
```bash
# Disk Partitioning
fdisk -l                   # List partitions
parted -l                  # List partitions (GPT)
gdisk /dev/sda            # GPT partitioning

# LVM Operations
pvdisplay                  # Physical volumes
vgdisplay                  # Volume groups
lvdisplay                  # Logical volumes
lvextend -L +10G /dev/vg/lv  # Extend LV
resize2fs /dev/vg/lv      # Resize filesystem
```

### File System
```bash
# File System Operations
df -h                      # Disk space usage
du -sh /*                  # Directory sizes
ncdu                       # Interactive disk usage
lsof                      # List open files
fuser -m /mnt             # Who's using mount

# File Search
find / -name "pattern"    # Find files
locate filename           # Quick file search
updatedb                  # Update locate db
```

## Network Administration

### Network Configuration
```bash
# Interface Management
ip addr                    # Show IP addresses
ip link                    # Link status
ip route                   # Routing table
ss -tulpn                 # Active connections
netstat -tulpn            # Active ports

# Network Tools
ping -c 4 hostname        # Test connectivity
traceroute hostname       # Trace route
mtr hostname              # Better traceroute
dig domain.com            # DNS lookup
nslookup domain.com       # DNS lookup
```

### Firewall Management
```bash
# UFW (Uncomplicated Firewall)
ufw status                # Show status
ufw allow 80/tcp         # Allow port
ufw deny from 1.2.3.4    # Block IP
ufw enable/disable       # Toggle firewall

# iptables
iptables -L              # List rules
iptables -A INPUT -p tcp --dport 80 -j ACCEPT  # Allow port
iptables-save > rules   # Save rules
iptables-restore < rules # Restore rules
```

## Process Management

### Service Control
```bash
# Systemd
systemctl status service     # Service status
systemctl start service     # Start service
systemctl enable service    # Enable on boot
systemctl list-units       # List services
journalctl -u service      # Service logs

# Process Control
ps aux                     # List processes
pgrep process_name        # Find process ID
pkill process_name        # Kill process
nice -n 19 command        # Run with low priority
renice 19 -p pid          # Change priority
```

## User Management

### User Operations
```bash
# User Administration
useradd -m username       # Create user
usermod -aG group user    # Add to group
passwd username           # Set password
who                       # Show logged in
w                        # Show who + what

# Permission Management
chmod 755 file           # Change permissions
chown user:group file    # Change ownership
setfacl -m u:user:rwx file # ACL
getfacl file            # Show ACL
```

## Package Management

### APT (Debian/Ubuntu)
```bash
# Package Operations
apt update               # Update repos
apt upgrade              # Upgrade packages
apt install package      # Install package
apt remove package       # Remove package
apt autoremove          # Clean unused

# Package Info
apt search keyword       # Search packages
apt show package        # Package info
dpkg -l                 # List installed
apt list --upgradable   # Show upgradable
```

## Log Management

### System Logs
```bash
# Log Viewing
tail -f /var/log/syslog  # Follow syslog
grep -i error /var/log/* # Find errors
journalctl -f           # Follow systemd logs
journalctl -b          # Boot logs
last                   # Login history

# Log Rotation
logrotate -f /etc/logrotate.conf  # Force rotation
cat /etc/logrotate.d/nginx       # Config example
```

## Container Management

### Docker Operations
```bash
# Container Management
docker ps                # List containers
docker stats            # Container stats
docker logs container   # Container logs
docker exec -it container bash  # Enter container
docker inspect container # Container details

# Image Management
docker images           # List images
docker pull image      # Pull image
docker build -t name . # Build image
docker prune          # Clean unused
```

## Backup & Recovery

### Backup Commands
```bash
# File Backup
tar -czf backup.tar.gz /path  # Create archive
tar -xzf backup.tar.gz       # Extract archive
rsync -avz src/ dest/       # Sync files
dd if=/dev/sda of=disk.img  # Disk image

# Database Backup
pg_dump dbname > backup.sql  # PostgreSQL
mysqldump dbname > backup.sql # MySQL
```

## Performance Tuning

### System Tuning
```bash
# Kernel Parameters
sysctl -a                # Show all params
sysctl vm.swappiness=10 # Set param
echo 1 > /proc/sys/net/ipv4/ip_forward # Enable IP forwarding

# Resource Limits
ulimit -a               # Show limits
ulimit -n 65535        # Set file limit
```

## Security

### Security Checks
```bash
# System Security
fail2ban-client status  # Show banned IPs
ausearch -k sudo       # Audit sudo use
chkrootkit             # Check for rootkits
lynis audit system    # Security audit

# SSL/Certificates
openssl x509 -text -noout -in cert.pem  # Show cert
certbot renew         # Renew Let's Encrypt
```

## Troubleshooting

### Common Issues
```bash
# System Issues
dmesg | tail           # Kernel messages
journalctl -p err     # Error messages
strace command        # Trace system calls
ltrace command       # Trace library calls

# Network Issues
tcpdump -i eth0      # Packet capture
nmap -p- localhost   # Port scan
curl -v website.com  # HTTP debug
```

## Automation & Scripting

### Bash Scripting
```bash
# Script Template
#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# Error handling
trap 'echo "Error on line $LINENO"' ERR

# Common patterns
for i in $(seq 1 10); do
    echo $i
done

if [ -f file.txt ]; then
    echo "File exists"
fi
```

## Maintenance Tasks

### Daily Checks
```bash
# System Health
check_disk_space() {
    df -h | awk '{ if($5 > "80%") print $0 }'
}

check_load() {
    uptime | awk -F'load average:' '{ print $2 }'
}

check_memory() {
    free -h | grep Mem
}

check_zombie_processes() {
    ps aux | grep Z
}
```

### Monthly Tasks
```bash
# System Updates
apt update && apt upgrade -y
needrestart            # Check for restarts
update-grub           # Update GRUB

# Cleanup
find /var/log -type f -delete  # Clear logs
apt autoremove        # Remove unused
journalctl --vacuum-time=30d  # Clear old journals
```
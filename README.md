# Addi-Aire Infrastructure

This repository contains the Pulumi infrastructure code for the Addi-Aire platform. The infrastructure is designed following the best practices outlined in the platform engineering documentation.

## Architecture Overview

The infrastructure is organized into several key components:

- **Networking**: Docker bridge network setup for container communication
- **Compute**: Container management including registry, images, and running containers
- **Monitoring**: Prometheus-based monitoring with service discovery

## Prerequisites

- Python 3.7+
- Pulumi CLI
- Docker
- Docker Registry credentials

## Directory Structure

```
addi-aire/
├── Pulumi.yaml              # Project config
├── Pulumi.dev.yaml          # Dev stack config
├── Pulumi.prod.yaml         # Prod stack config
├── __main__.py             # Main entry point
├── requirements.txt        # Python dependencies
└── src/
    ├── networking/        # Network resources
    ├── compute/          # Container resources
    ├── storage/         # Storage resources
    └── monitoring/      # Monitoring setup
```

## Configuration

The following configuration values need to be set:

```bash
# Set environment
pulumi config set environment dev  # or prod

# Set registry credentials (as secrets)
pulumi config set --secret registryServer registry.addi-aire.com
pulumi config set --secret registryUsername <username>
pulumi config set --secret registryPassword <password>
```

## Components

### Networking Stack
- Docker bridge network
- Network isolation
- Custom naming

### Container Stack
- Docker registry integration
- Application container deployment
- Environment-based configuration
- Port mapping (3000:3000)

### Monitoring Stack
- Prometheus service monitoring
- Metrics endpoint configuration
- Container label-based discovery

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Initialize Pulumi stack:
   ```bash
   pulumi stack init dev
   ```

3. Configure the stack:
   ```bash
   # Set required configuration values
   pulumi config set ...
   ```

4. Deploy the infrastructure:
   ```bash
   pulumi up
   ```

## Outputs

After deployment, the following outputs are available:
- `network_id`: ID of the created Docker network
- `app_url`: URL to access the application
- `container_ip`: IP address of the application container

## Monitoring

The infrastructure includes built-in monitoring with:
- Prometheus metrics collection
- Service discovery via labels
- `/metrics` endpoint exposure

## Security

- Secrets management via Pulumi configuration
- Network isolation
- Registry authentication
- Environment-based configuration

## Development

To contribute to this infrastructure:

1. Create a new branch
2. Make your changes
3. Test using `pulumi preview`
4. Submit a pull request

## Testing

```bash
# Install test dependencies
pip install -r requirements.txt

# Run tests
pytest tests/
``` 
# Pulumi Subject Matter Expert Cheat Sheet - Addi-Aire

## Project Structure
```
addi-aire/
├── Pulumi.yaml              # Project config
├── Pulumi.dev.yaml          # Dev stack config
├── Pulumi.prod.yaml         # Prod stack config
├── index.ts                 # Main entry
├── tsconfig.json            # TypeScript config
├── package.json             # Dependencies
└── src/
    ├── networking/         # Network resources
    ├── compute/           # VM and container resources
    ├── storage/          # Storage resources
    └── monitoring/       # Monitoring resources
```

## Core Components Setup

### Base Infrastructure
```typescript
import * as pulumi from "@pulumi/pulumi";
import * as docker from "@pulumi/docker";
import * as nginx from "@pulumi/nginx";

// Resource configuration
const config = new pulumi.Config();
const environment = config.require("environment");

// Network setup
const network = new docker.Network("addi-aire-network", {
    name: `addi-aire-${environment}`,
    driver: "bridge",
    options: {
        "com.docker.network.bridge.name": "addi-aire-bridge"
    }
});

// Container registry
const registry = new docker.Registry("registry", {
    server: "registry.addi-aire.com",
    username: config.requireSecret("registryUsername"),
    password: config.requireSecret("registryPassword")
});
```

### Application Deployment
```typescript
// Docker image
const appImage = new docker.Image("app", {
    build: {
        context: "../app",
        dockerfile: "Dockerfile"
    },
    imageName: "addi-aire/app:latest",
    registry: registry
});

// Application service
const app = new docker.Container("app", {
    image: appImage.imageName,
    ports: [{
        internal: 3000,
        external: 3000
    }],
    networkId: network.id,
    envs: [
        `NODE_ENV=${environment}`,
        pulumi.interpolate`DB_HOST=${dbHost}`
    ]
});
```

## Resource Management

### State Management
```bash
# Stack operations
pulumi stack init dev
pulumi stack select prod
pulumi stack output
pulumi stack export > stack.json
pulumi stack import < stack.json

# State inspection
pulumi refresh
pulumi state delete <resource>
pulumi state unprotect <resource>
```

### Configuration Management
```yaml
# Pulumi.dev.yaml
config:
  addi-aire:environment: dev
  addi-aire:instanceType: t2.micro
  addi-aire:dockerRegistry: registry.addi-aire.com
secretConfig:
  addi-aire:dbPassword:
    secure: AAABANKBj6seK8LN...
```

## Advanced Patterns

### Component Resources
```typescript
class AppService extends pulumi.ComponentResource {
    constructor(name: string, args: AppServiceArgs, opts?: pulumi.ComponentResourceOptions) {
        super("addi-aire:app:Service", name, {}, opts);

        // Container
        const container = new docker.Container(`${name}-container`, {
            image: args.image,
            ports: args.ports,
            networkId: args.networkId,
            envs: args.environment
        }, { parent: this });

        // Nginx config
        const nginx = new nginx.Config(`${name}-nginx`, {
            upstream: {
                name: name,
                servers: [{
                    address: pulumi.interpolate`${container.networkSettings.ipAddress}:${args.ports[0].internal}`
                }]
            }
        }, { parent: this });

        this.registerOutputs({
            containerIp: container.networkSettings.ipAddress,
            nginxConfig: nginx.file
        });
    }
}
```

### Dynamic Providers
```typescript
class DockerVolumeProvider implements pulumi.dynamic.ResourceProvider {
    async create(inputs: any) {
        // Custom volume creation logic
        return { id: volumeId, outs: { ... } };
    }

    async delete(id: string, inputs: any) {
        // Custom volume deletion logic
    }
}

class DockerVolume extends pulumi.dynamic.Resource {
    constructor(name: string, args: VolumeArgs, opts?: pulumi.CustomResourceOptions) {
        super(new DockerVolumeProvider(), name, args, opts);
    }
}
```

## CI/CD Integration

### GitHub Actions
```yaml
name: Infrastructure Deployment
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: pulumi/actions@v3
        with:
          command: up
          stack-name: dev
          work-dir: infrastructure
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
```

### Jenkins Pipeline
```groovy
pipeline {
    agent any
    environment {
        PULUMI_ACCESS_TOKEN = credentials('pulumi-token')
    }
    stages {
        stage('Deploy Infrastructure') {
            steps {
                sh '''
                    pulumi stack select dev
                    pulumi preview
                    pulumi up --yes
                '''
            }
        }
    }
}
```

## Testing Strategies

### Unit Testing
```typescript
import * as testing from "@pulumi/testing";

describe("Infrastructure", () => {
    const pulumiProgram = async () => {
        // Your Pulumi program
    };

    it("creates required resources", async () => {
        const resources = await testing.run(pulumiProgram);
        expect(resources).toHaveResource("docker:Container", {
            name: "app",
            image: "addi-aire/app:latest"
        });
    });
});
```

### Integration Testing
```typescript
import * as docker from "@pulumi/docker";
import * as automation from "@pulumi/pulumi/automation";

describe("Infrastructure Integration", () => {
    it("deploys and validates app", async () => {
        const stack = await automation.LocalWorkspace.createOrSelectStack({
            stackName: "integration",
            workDir: "./integration"
        });

        await stack.up();
        // Validation logic
        await stack.destroy();
    });
});
```

## Monitoring & Observability

### Resource Tracking
```typescript
// Custom resource tracker
const tracker = new pulumi.ResourceTracker("resource-tracker", {
    onResourceCreated: async (resource) => {
        console.log(`Created: ${resource.urn}`);
    },
    onResourceModified: async (resource) => {
        console.log(`Modified: ${resource.urn}`);
    }
});

// Apply to resources
const app = new docker.Container("app", {
    // ... config
}, { resourceTracker: tracker });
```

### Metrics Export
```typescript
// Export metrics to Prometheus
const metrics = new prometheus.ServiceMonitor("app-monitor", {
    selector: {
        matchLabels: app.labels
    },
    endpoints: [{
        port: "metrics",
        path: "/metrics"
    }]
});
```

## Security Best Practices

### Secret Management
```typescript
// Using secret manager
const secrets = new SecretManager("app-secrets", {
    items: {
        "db-password": config.requireSecret("dbPassword"),
        "api-key": config.requireSecret("apiKey")
    }
});

// Applying secrets
const app = new docker.Container("app", {
    // ... other config
    envs: pulumi.all([secrets.items]).apply(([items]) => [
        `DB_PASSWORD=${items["db-password"]}`,
        `API_KEY=${items["api-key"]}`
    ])
});
```

### Network Policies
```typescript
const policy = new NetworkPolicy("app-policy", {
    spec: {
        podSelector: {
            matchLabels: app.labels
        },
        ingress: [{
            from: [{
                namespaceSelector: {
                    matchLabels: {
                        name: "default"
                    }
                }
            }]
        }]
    }
});
```

## Troubleshooting Guide

### Common Issues
1. State Conflicts
```bash
# Reset state
pulumi refresh
# Force unlock state
pulumi stack export | pulumi stack import
```

2. Resource Dependencies
```typescript
// Explicit dependencies
const app = new docker.Container("app", {
    // ... config
}, { dependsOn: [database, cache] });
```

3. Network Issues
```typescript
// Debug network
new docker.Container("debug", {
    image: "nicolaka/netshoot",
    networkId: network.id,
    command: ["sleep", "infinity"]
});
```

### Debug Commands
```bash
# Stack debugging
pulumi stack --show-urls
pulumi logs --follow
pulumi history

# Resource inspection
pulumi query resource <URN>
pulumi watch
```
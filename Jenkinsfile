pipeline {
    agent any
    
    environment {
        // App Configuration
        APP_NAME = 'addi-aire-nextjs'
        CONTAINER_PORT = '3000'
        REGISTRY = 'localhost:5000'
        ENVIRONMENT = "${env.BRANCH_NAME == 'main' ? 'prod' : 'dev'}"
        
        // Vault Configuration
        VAULT_ADDR = 'http://192.168.3.26:8220'
        VAULT_TOKEN = credentials('vault-token')
    }
    
    stages {
        stage('Load Secrets') {
            steps {
                withVault(configuration: [
                    timeout: 60, 
                    vaultCredentialId: 'vault-token', 
                    engineVersion: 2,
                    vaultUrl: env.VAULT_ADDR
                ], vaultSecrets: [
                    [path: 'kv/data/secret/addi-aire/stripe', secretValues: [
                        [envVar: 'STRIPE_SECRET', vaultKey: 'secret_key'],
                        [envVar: 'STRIPE_PUBLISHABLE', vaultKey: 'publishable_key'],
                        [envVar: 'STRIPE_WEBHOOK', vaultKey: 'webhook_secret'],
                        [envVar: 'STRIPE_API', vaultKey: 'api_version']
                    ]]
                ]) {
                    sh 'echo "Secrets loaded successfully"'
                }
            }
        }
        
        stage('Build Next.js') {
            steps {
                sh '''
                    npm install --legacy-peer-deps
                    npm run build
                '''
            }
        }
        
        stage('Build & Push Image') {
            steps {
                sh """
                    # Build new image
                    docker build -t ${APP_NAME}:${BUILD_NUMBER} \
                    --build-arg STRIPE_SECRET_KEY=${STRIPE_SECRET} \
                    --build-arg NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE} \
                    --build-arg STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK} \
                    --build-arg STRIPE_API_VERSION=${STRIPE_API} \
                    .

                    # Tag and push to registry
                    docker tag ${APP_NAME}:${BUILD_NUMBER} ${REGISTRY}/${APP_NAME}:${BUILD_NUMBER}
                    docker push ${REGISTRY}/${APP_NAME}:${BUILD_NUMBER}
                """
            }
        }
        
        stage('Deploy') {
            steps {
                script {
                    // Stop and remove existing container
                    sh """
                        if docker ps -a | grep -q ${APP_NAME}_${ENVIRONMENT}; then
                            docker stop ${APP_NAME}_${ENVIRONMENT}
                            docker rm ${APP_NAME}_${ENVIRONMENT}
                        fi
                    """
                    
                    // Run new container in the correct network
                    sh """
                        docker run -d \
                        --name ${APP_NAME}_${ENVIRONMENT} \
                        --network addi-aire-${ENVIRONMENT} \
                        --health-cmd="curl -f http://localhost:${CONTAINER_PORT}/api/health || exit 1" \
                        --health-interval=30s \
                        --health-timeout=10s \
                        --health-retries=3 \
                        -e NODE_ENV=${ENVIRONMENT} \
                        -e STRIPE_SECRET_KEY=${STRIPE_SECRET} \
                        -e NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLISHABLE} \
                        -e STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK} \
                        -e STRIPE_API_VERSION=${STRIPE_API} \
                        ${REGISTRY}/${APP_NAME}:${BUILD_NUMBER}
                    """
                    
                    // Wait for container health check
                    sh '''
                        attempt=1
                        max_attempts=30
                        until docker inspect ${APP_NAME}_${ENVIRONMENT} --format='{{.State.Health.Status}}' | grep -q healthy; do
                            if [ $attempt -eq $max_attempts ]; then
                                echo "Container failed to become healthy"
                                exit 1
                            fi
                            echo "Waiting for container to become healthy (attempt $attempt/$max_attempts)..."
                            sleep 2
                            attempt=$((attempt + 1))
                        done
                    '''
                    
                    // Update Nginx config using our template system
                    sh '''
                        export APP_NAME=${APP_NAME}
                        export ENVIRONMENT=${ENVIRONMENT}
                        export CONTAINER_PORT=${CONTAINER_PORT}
                        envsubst '${APP_NAME} ${ENVIRONMENT} ${CONTAINER_PORT}' < /etc/nginx/templates/app.conf.template > /etc/nginx/conf.d/apps/${ENVIRONMENT}/${APP_NAME}.conf
                        nginx -s reload
                    '''
                }
            }
        }
    }
    
    post {
        failure {
            sh """
                if docker ps -a | grep -q ${APP_NAME}_${ENVIRONMENT}; then
                    docker stop ${APP_NAME}_${ENVIRONMENT}
                    docker rm ${APP_NAME}_${ENVIRONMENT}
                fi
                if [ -f "/etc/nginx/conf.d/apps/${ENVIRONMENT}/${APP_NAME}.conf" ]; then
                    rm /etc/nginx/conf.d/apps/${ENVIRONMENT}/${APP_NAME}.conf
                fi
                nginx -s reload
            """
        }
    }
} 
pipeline {
    agent {
        label 'docker'
    }
    
    environment {
        DOCKER_CREDENTIALS_ID = 'docker'
        BUILD_TAG = "${BUILD_NUMBER}"
        FE_IMAGE = "razielrey/domain-monitor-fe"
        BE_IMAGE = "razielrey/domain-monitor-be"
    }
    
    stages {
        stage('Clean Workspace') {
            steps {
                cleanWs()
                echo 'Workspace cleaned'
                script {
                    sh"""
                        if [ \$(sudo docker ps -aq) ]; then
                            sudo docker rm -f \$(sudo docker ps -aq)
                        else
                            echo "No containers to remove"
                        fi
                        # Remove old images
                        sudo docker image prune -f
                    """
                }
                echo 'Docker containers removed'
            }
        }
        
        stage('Clone Repository') {
            steps {
                dir('MonitoringApp') {
                    script {
                        git branch: 'FE-BE_Exercise', url: 'https://github.com/RazielRey/DevOpsCourse.git'
                        COMMIT_ID = sh(script: 'git rev-parse HEAD', returnStdout: true).trim().take(5)
                    }
                }
            }
        }
        
        stage('Build Docker Images') {
            parallel {
                stage('Build Frontend') {
                    steps {
                        dir('MonitoringApp/DevOpsCourse/app/FE') {
                            script {
                                sh """
                                    sudo docker build -t ${FE_IMAGE}:${BUILD_TAG} .
                                    sudo docker tag ${FE_IMAGE}:${BUILD_TAG} ${FE_IMAGE}:latest
                                """
                            }
                        }
                    }
                }
                
                stage('Build Backend') {
                    steps {
                        dir('MonitoringApp/DevOpsCourse/app/BE') {
                            script {
                                sh """
                                    sudo docker build -t ${BE_IMAGE}:${BUILD_TAG} .
                                    sudo docker tag ${BE_IMAGE}:${BUILD_TAG} ${BE_IMAGE}:latest
                                """
                            }
                        }
                    }
                }
            }
        }
        
        stage('Start Application Stack') {
            steps {
                script {
                    sh """
                        # Start Backend with host network
                        sudo docker run -d --network host \
                            --name be-app-${BUILD_TAG} \
                            ${BE_IMAGE}:${BUILD_TAG}
                        
                        sleep 5
                        
                        # Start Frontend with host network
                        sudo docker run -d --network host \
                            --name fe-app-${BUILD_TAG} \
                            -e BACKEND_URL=http://localhost:5001 \
                            ${FE_IMAGE}:${BUILD_TAG}
                        
                        # Wait for services to be ready
                        sleep 10
                        
                        # Print container logs for debugging
                        echo "Frontend logs:"
                        sudo docker logs fe-app-${BUILD_TAG}
                        echo "Backend logs:"
                        sudo docker logs be-app-${BUILD_TAG}
                    """
                }
            }
        }
        
        stage('Service Check') {
            steps {
                script {
                    sh """
                        # Check if containers are running
                        echo "Checking container status:"
                        sudo docker ps
                        
                        # Simple connection test
                        for i in \$(seq 1 6); do
                            if curl -s http://localhost:8080 > /dev/null; then
                                echo "Frontend is responding"
                                break
                            fi
                            if [ \$i -eq 6 ]; then
                                echo "Frontend not responding"
                                exit 1
                            fi
                            sleep 5
                        done
                    """
                }
            }
        }
        
        stage('Selenium Test') {
            steps {
                script {
                    sh """
                        # Start Selenium container with host network
                        sudo docker run --network host \
                            -d \
                            --name selenium-test \
                            -e APP_URL=http://localhost:8080 \
                            -e WAIT_TIMEOUT=30 \
                            -e PYTHONUNBUFFERED=1 \
                            razielrey/selenium-tests:latest
                        
                        sleep 10
                        
                        # Run tests with output
                        if ! sudo docker exec selenium-test python3 -u run_tests.py; then
                            echo "Selenium tests failed - collecting debug info"
                            sudo docker logs selenium-test
                            sudo docker logs fe-app-${BUILD_TAG}
                            sudo docker logs be-app-${BUILD_TAG}
                            exit 1
                        fi
                    """
                }
            }
        }
    }
    
    post {
        success {
            script {
                withCredentials([usernamePassword(credentialsId: 'docker', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh """
                        echo ${DOCKER_PASS} | sudo docker login -u ${DOCKER_USER} --password-stdin
                        
                        # Push Frontend images
                        sudo docker push ${FE_IMAGE}:${BUILD_TAG}
                        sudo docker push ${FE_IMAGE}:latest
                        
                        # Push Backend images
                        sudo docker push ${BE_IMAGE}:${BUILD_TAG}
                        sudo docker push ${BE_IMAGE}:latest
                    """
                }
                build job: 'ansible-domain-monitor-pipeline', wait: true
            }
        }
        
        always {
            sh """
                # Clean up containers
                sudo docker rm -f be-app-${BUILD_TAG} fe-app-${BUILD_TAG} selenium-test || true
                
                # Clean up dangling images
                sudo docker image prune -f
            """
        }
    }
}

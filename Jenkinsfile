pipeline {
    agent any

    parameters {
        booleanParam(name: 'RUN_TRIVY', defaultValue: false, description: 'Quet bao mat image bang Trivy (tuy chon, lan dau tai CSDL kha lau)')
        booleanParam(name: 'ENFORCE_QUALITY_GATE', defaultValue: false, description: 'Fail pipeline neu SonarQube Quality Gate khong dat')
    }

    environment {
        // File kubeconfig da copy vao Jenkins
        KUBECONFIG     = '/var/jenkins_home/.kube/config'
        // Scanner chay trong container rieng nen goi SonarQube qua may host
        SONAR_HOST_URL = 'http://host.docker.internal:9000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test user-service (Java 17)') {
            steps {
                sh '''
                    docker run --rm --volumes-from $(hostname) -v m2-cache:/root/.m2 -w "$WORKSPACE/user-service" maven:3.9-eclipse-temurin-17 mvn -B test
                '''
            }
        }

        stage('Test frontend (Java 17)') {
            steps {
                sh '''
                    docker run --rm --volumes-from $(hostname) -v m2-cache:/root/.m2 -w "$WORKSPACE/frontend" maven:3.9-eclipse-temurin-17 mvn -B test
                '''
            }
        }

        stage('Test product-service (Python)') {
            steps {
                sh '''
                    docker run --rm --volumes-from $(hostname) -w "$WORKSPACE/product-service" python:3.12-slim sh -c "pip install --no-cache-dir -r requirements.txt && python -m pytest -q --junitxml=report.xml"
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    sh '''
                        docker run --rm --volumes-from $(hostname) -w "$WORKSPACE" -e SONAR_HOST_URL -e SONAR_TOKEN sonarsource/sonar-scanner-cli:latest -Dsonar.qualitygate.wait=$ENFORCE_QUALITY_GATE
                    '''
                }
            }
        }

        stage('Build Docker images') {
            steps {
                sh '''
                    docker build -t user-service:$BUILD_NUMBER -t user-service:latest ./user-service
                    docker build -t product-service:$BUILD_NUMBER -t product-service:latest ./product-service
                    docker build -t frontend:$BUILD_NUMBER -t frontend:latest ./frontend
                '''
            }
        }

        stage('Trivy Scan (optional)') {
            when {
                expression { params.RUN_TRIVY }
            }
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    sh '''
                        for img in user-service product-service frontend; do
                            docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v trivy-cache:/root/.cache/ aquasec/trivy:latest image --timeout 30m --scanners vuln --severity HIGH,CRITICAL --exit-code 0 --no-progress $img:$BUILD_NUMBER
                        done
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    # Thay tag :latest bang tag theo so build roi apply
                    for f in k8s/*.yaml; do
                        sed "s#:latest#:$BUILD_NUMBER#" "$f" | kubectl apply -f -
                    done
                    kubectl rollout status deployment/postgres --timeout=180s
                    kubectl rollout status deployment/user-service --timeout=300s
                    kubectl rollout status deployment/product-service --timeout=300s
                    kubectl rollout status deployment/frontend --timeout=300s
                '''
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: '**/target/surefire-reports/*.xml,product-service/report.xml'
            sh 'kubectl get pods,svc || true'
        }
        success {
            echo 'Pipeline OK - truy cap frontend bang: kubectl port-forward svc/frontend 8000:8000'
        }
        failure {
            echo 'Pipeline FAILED - xem log stage bi do'
        }
    }
}
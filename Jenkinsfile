pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "attendance-system"
        DOCKER_TAG   = "${env.BUILD_NUMBER}"
        PYTHON       = "python"
    }

    stages {

        stage('Clone Repository') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '''
                    %PYTHON% -m venv venv
                    venv\\Scripts\\pip install --upgrade pip
                    venv\\Scripts\\pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                bat 'venv\\Scripts\\python -m pytest test_app.py -v --junitxml=test-results.xml'
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        // Docker stage commented out — add back once Dockerfile is ready
        /*
        stage('Build Docker Image') {
            steps {
                bat 'docker info > nul 2>&1 || (echo Docker is not running && exit 1)'
                bat "docker build -t %DOCKER_IMAGE%:%DOCKER_TAG% ."
                bat "docker tag %DOCKER_IMAGE%:%DOCKER_TAG% %DOCKER_IMAGE%:latest"
            }
        }
        */
    }

    post {
        always {
            archiveArtifacts artifacts: 'test-results.xml', allowEmptyArchive: true
            cleanWs()
        }
        success {
            echo "Build #${env.BUILD_NUMBER} succeeded!"
        }
        failure {
            echo "Build #${env.BUILD_NUMBER} failed. Check console output."
        }
    }
}

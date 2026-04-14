pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "attendance-system"
        DOCKER_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Clone Repository') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                // Using a virtual environment to keep the Jenkins node clean
                sh '''
                    python3 -m venv venv
                    ./venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                // Running the test file shown in your repo structure
                sh './venv/bin/python -m pytest test_app.py'
            }
        }

        stage('Build Docker Image') {
            steps {
                // Building the image that will eventually be deployed to Blue or Green
                sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
            }
        }
    }

    post {
        always {
            // Clean up workspace to save disk space
            cleanWs()
        }
        failure {
            echo 'Pipeline failed! Check the console output for errors.'
        }
    }
}
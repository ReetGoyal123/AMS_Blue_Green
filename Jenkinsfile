pipeline {
    agent any
    environment {
        DOCKER_IMAGE = "attendance-system"
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        PYTHON = 'C:\Users\shash\AppData\Local\Programs\Python\Python313\python.exe'
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
                    "%PYTHON%" -m venv venv
                    call venv\\Scripts\\activate
                    venv\\Scripts\\pip install -r requirements.txt
                '''
            }
        }
        stage('Run Tests') {
            steps {
                bat 'venv\\Scripts\\python -m pytest test_app.py -v'
            }
        }
        stage('Build Docker Image') {
            steps {
                bat "docker build -t %DOCKER_IMAGE%:%DOCKER_TAG% ."
                bat "docker tag %DOCKER_IMAGE%:%DOCKER_TAG% %DOCKER_IMAGE%:latest"
            }
        }
    }
    post {
        always {
            cleanWs()
        }
        failure {
            echo 'Pipeline failed! Check the console output for errors.'
        }
    }
}

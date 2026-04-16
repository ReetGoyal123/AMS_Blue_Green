pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "attendance-system"
        DOCKER_TAG   = "${env.BUILD_NUMBER}"
        PYTHON       = 'C:/Users/shash/AppData/Local/Programs/Python/Python313/python.exe'
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
                bat 'venv\\Scripts\\python test_app.py'
            }
        }
    }

    post {
        always {
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

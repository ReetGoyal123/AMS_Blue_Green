pipeline {
    agent any
    environment {
        PYTHON      = 'C:/Users/shash/AppData/Local/Programs/Python/Python313/python.exe'
        PYTHONUTF8  = "1"
        IMAGE_NAME  = "attendance-system"
        BLUE_PORT   = "8501"
        GREEN_PORT  = "8502"
        BLUE_NAME   = "attendance-blue"
        GREEN_NAME  = "attendance-green"
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

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %IMAGE_NAME%:%BUILD_NUMBER% .'
            }
        }

        stage('Deploy Green') {
            steps {
                bat '''
                    FOR /F "tokens=*" %%i IN ('docker ps -q -f name=%GREEN_NAME%') DO docker stop %%i
                    FOR /F "tokens=*" %%i IN ('docker ps -aq -f name=%GREEN_NAME%') DO docker rm %%i
                    docker run -d --name %GREEN_NAME% -p %GREEN_PORT%:8501 %IMAGE_NAME%:%BUILD_NUMBER%
                '''
            }
        }

        stage('Health Check') {
            steps {
                bat '''
                    echo Waiting for green container to start...
                    ping -n 15 127.0.0.1 > nul
                    curl -f http://localhost:%GREEN_PORT%/_stcore/health || exit 1
                    echo Green container is healthy!
                '''
            }
        }

        stage('Switch Blue-Green') {
            steps {
                bat '''
                    FOR /F "tokens=*" %%i IN ('docker ps -q -f name=%BLUE_NAME%') DO docker stop %%i
                    FOR /F "tokens=*" %%i IN ('docker ps -aq -f name=%BLUE_NAME%') DO docker rm %%i
                    docker stop %GREEN_NAME%
                    docker rm %GREEN_NAME%
                    docker run -d --name %BLUE_NAME% -p %BLUE_PORT%:8501 %IMAGE_NAME%:%BUILD_NUMBER%
                    echo Switched! App now live on port %BLUE_PORT%
                '''
            }
        }

    }
    post {
        always {
            cleanWs()
        }
        success {
            echo "Build #${env.BUILD_NUMBER} succeeded! App live at http://localhost:8501"
        }
        failure {
            echo "Build #${env.BUILD_NUMBER} failed. Check console output."
        }
    }
}

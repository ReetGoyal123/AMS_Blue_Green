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
                   FOR /F "tokens=*" %%i IN ('docker ps -q --filter "name=^%GREEN_NAME%$"') DO docker stop %%i
                   FOR /F "tokens=*" %%i IN ('docker ps -aq --filter "name=^%GREEN_NAME%$"') DO docker rm %%i
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

        stage('Switch Traffic to Green') {
            steps {
                powershell """
                \$conf = Get-Content C:\\Users\\shash\\Downloads\\nginx-1.30.0\\nginx-1.30.0\\conf\\nginx.conf
                \$conf = \$conf -replace 'server localhost:\\d+;', 'server localhost:%GREEN_PORT%;'
                \$conf | Set-Content C:\\Users\\shash\\Downloads\\nginx-1.30.0\\nginx-1.30.0\\conf\\nginx.conf
                """
                bat 'C:\\Users\\shash\\Downloads\\nginx-1.30.0\\nginx-1.30.0\\nginx.exe -p C:\\Users\\shash\\Downloads\\nginx-1.30.0\\nginx-1.30.0 -s reload'
            }
        }
        stage('Stop Blue') {
            steps {
        bat '''
            docker stop %BLUE_NAME% 2>nul || echo No blue to stop
            docker rm %BLUE_NAME% 2>nul || echo No blue to remove
            docker rename %GREEN_NAME% %BLUE_NAME%
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

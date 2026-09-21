pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out Construction-AI source code'
            }
        }

        stage('Python Version') {
            steps {
                bat 'python --version'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'python -m pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                bat 'python -m pytest tests -v'
            }
        }
    }

    post {
        success {
            echo 'Construction-AI CI pipeline completed successfully.'
        }

        failure {
            echo 'Construction-AI CI pipeline failed. Check the console output.'
        }
    }
}
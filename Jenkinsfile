pipeline {
    agent any
    stages {
        stage('Environment Check') {
            steps {
                sh '''
                    python3 -m site
                    pwd
                    ls
                '''
            }
        }
    }
}

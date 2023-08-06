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
        
        stage('Compile Python') {
            steps {
                sh 'python3 -m py_compile src/data_collection/api_request.py'
                stash(name: 'compiled-results', includes: 'src/**/*.py*')
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    echo "Running pytest in tests/data_collection/"
                    pytest tests/data_collection/
                '''
            }
        }
    }
}

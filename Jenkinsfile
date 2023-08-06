pipeline {
    agent any
    stages {
        stage('Setup Environment') {
            steps {
                sh '''#!/bin/bash
                    echo "Creating virtual environment..."
                    python3 -m venv .NYT

                    echo "Activating virtual environment..."
                    source .NYT/bin/activate

                    echo "Installing dependencies..."
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Environment Check') {
            steps {
                sh '''#!/bin/bash
                    source .NYT/bin/activate
                    python -m site
                    pwd
                    ls
                '''
            }
        }

        stage('Compile Python') {
            steps {
                sh '''#!/bin/bash
                    source .NYT/bin/activate
                    python -m py_compile src/data_collection/api_request.py
                '''
                stash(name: 'compiled-results', includes: 'src/**/*.py*')
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''#!/bin/bash
                    source .NYT/bin/activate
                    echo "Running pytest in tests/data_collection/"
                    pytest tests/data_collection/
                '''
            }
        }
    }
}



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
                    python -m py_compile src/data_main/main.py
                '''
                stash(name: 'compiled-results', includes: 'src/**/*.py*')
            }
        }

        stage('Unit Tests') {
            steps {
                script {
                    def imageName = "nyt-app:test"
                    def composeFile = "docker-compose.yml"

                    sh "docker-compose -f ${composeFile} down -v"
                    sh "docker rmi -f ${imageName} || true"
                    sh "docker-compose -f ${composeFile} build app"
                    
                    sh """
                        docker-compose -f ${composeFile} run --rm app \
                            pytest -vv --junitxml=/app/tests/test-results.xml /app/tests/data_collection/
                    """
                    
                    sh "cp ./tests/test-results.xml ./test-results.xml"
                }
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('Docker Build and Compose') {
            steps {
                script {
                    def imageName = "nyt-app"
                    def imageTag = "latest"
                    def composeFile = "docker-compose.yml"

                    sh "docker rmi -f ${imageName}:${imageTag} || true"
                    
                    sh """
                        echo "Building Docker image using docker-compose..."
                        docker-compose -f ${composeFile} build app
                    """
                }
            }
        }
    }
}



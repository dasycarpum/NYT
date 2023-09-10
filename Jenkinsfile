pipeline {
    agent any
    environment {
        DB_PASS = credentials('db-pass')
    }
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

        stage('Compile Python for Data') {
            steps {
                sh '''#!/bin/bash
                    source .NYT/bin/activate
                    python -m py_compile src/data_main/main.py
                '''
                stash(name: 'compiled-results', includes: 'src/**/*.py*')
            }
        }

        stage('Unit Tests for Data') {
            steps {
                script {
                    def imageName = "nyt-app-data:test"
                    def composeFile = "docker-compose.data.yml"

                    sh "docker-compose -f ${composeFile} down -v"
                    sh "docker rmi -f ${imageName} || true"
                    sh "docker-compose -f ${composeFile} build app"
                    
                    sh """
                        docker-compose -f ${composeFile} run --rm -e DB_PASS=${DB_PASS} app pytest -vv --junitxml=/usr/src/app/tests/test-results-data-collection.xml /usr/src/app/tests/data_collection/
                    """
                    sh "cp ./tests/test-results-data-collection.xml ./test-results-data-collection.xml"

                    sh """
                        docker-compose -f ${composeFile} run --rm -e DB_PASS=${DB_PASS} app pytest -vv --junitxml=/usr/src/app/tests/test-results-data-ingestion.xml /usr/src/app/tests/data_ingestion/
                    """
                    sh "cp ./tests/test-results-data-ingestion.xml ./test-results-data-ingestion.xml"

                    sh """
                        docker-compose -f ${composeFile} run --rm -e DB_PASS=${DB_PASS} app pytest -vv --junitxml=/usr/src/app/tests/test-results-data-main.xml /usr/src/app/tests/data_main/
                    """
                    sh "cp ./tests/test-results-data-main.xml ./test-results-data-main.xml"
                }
            }
            post {
                always {
                    junit '**/test-results-*.xml'
                }
            }
        }


        stage('Docker Build and Compose for Data') {
            steps {
                script {
                    def imageName = "nyt-app-data"
                    def composeFile = "docker-compose.data.yml"

                    sh "docker rmi -f ${imageName} || true"
                    
                    sh """
                        echo "Building Docker image using docker-compose..."
                        docker-compose -f ${composeFile} build app
                    """
                }
            }
        }

        stage('Compile Python for ML') {
            steps {
                sh '''#!/bin/bash
                    source .NYT/bin/activate
                    python -m py_compile src/machine_learning/main.py
                '''
                stash(name: 'compiled-results-ml', includes: 'src/machine_learning/*.py*')
            }
        }

        stage('Unit Tests for ML') {
            steps {
                script {
                    def imageName = "nyt-app-ml:test"
                    def composeFile = "docker-compose.data.yml"

                    sh "docker-compose -f ${composeFile} down -v"
                    sh "docker rmi -f ${imageName} || true"
                    sh "docker-compose -f ${composeFile} build app"
        
                    sh """
                        docker-compose -f docker-compose.ml.yml run --rm -e DB_PASS=${DB_PASS} app pytest -vv --junitxml=/usr/src/app/tests/test-results-ml.xml /usr/src/app/tests/machine_learning/
                    """
                    sh "cp ./tests/test-results-ml.xml ./test-results-ml.xml"
                }
            }
            post {
                always {
                    junit '**/test-results-ml.xml'
                }
            }
        }

        stage('Docker Build and Compose for ML') {
            steps {
                script {
                    def imageName = "nyt-app-ml"
                    def composeFile = "docker-compose.ml.yml"

                    sh "docker rmi -f ${imageName} || true"
                    
                    sh """
                        echo "Building Docker image for ML using docker-compose..."
                        docker-compose -f ${composeFile} build app
                    """
                }
            }
        }

        stage('Compile Python for API') {
            steps {
                sh '''#!/bin/bash
                    source .NYT/bin/activate
                    python -m py_compile src/api/main.py
                '''
                stash(name: 'compiled-results-api', includes: 'src/api/*.py*')
            }
        }

        stage('Unit Tests for API') {
            steps {
                script {
                    def imageName = "nyt-app-api:test"
                    def composeFile = "docker-compose.api.yml"

                    sh "docker-compose -f ${composeFile} down -v"
                    sh "docker rmi -f ${imageName} || true"
                    sh "docker-compose -f ${composeFile} build app"
        
                    sh """
                        docker-compose -f docker-compose.api.yml run --rm -e DB_PASS=${DB_PASS} app pytest -vv --junitxml=/usr/src/app/tests/test-results-api.xml /usr/src/app/tests/api/
                    """
                    sh "cp ./tests/test-results-api.xml ./test-results-api.xml"
                }
            }
            post {
                always {
                    junit '**/test-results-api.xml'
                }
            }
        }
    }
}

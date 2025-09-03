pipeline {
    agent any

    stages {
        // === Stage 1: Clone the GitHub repository ===
        stage('Clone repository') {
            steps {
                // This clones the Git repo from the 'development' branch
                git branch: 'main', url: 'https://github.com/qxzjy/housing-prices-ml.git'
            }
        }

         // === Stage 2: Build a Docker image ===
        stage('Build Docker Image') {
            steps {
                script {
                    // This builds a Docker image from the Dockerfile in the repo
                    docker.build("ml-pipeline-test:latest")
                }
            }
        }

        // === Stage 3: Run tests inside the Docker container ===
        stage('Run Tests') {
            steps {
                script {
                    // Run a command inside the Docker container built earlier
                    // This uses pytest to run tests and outputs results to results.xml
                    docker.image("ml-pipeline-test:latest").inside {
                        sh 'python -m pytest --junitxml=results.xml'
                    }
                }
            }
        }

        // === Stage 4: Archive test results ===
        stage('Archive Results') {
            steps {
                // This tells Jenkins to store the test result file so it can be displayed in the UI
                junit 'results.xml'
            }
        }
    }

    post {
        always {
            // Clean up workspace and remove dangling Docker images
            sh 'docker system prune -f'
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check logs for errors.'
        }
    }
}
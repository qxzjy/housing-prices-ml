pipeline {
    agent any

    environment {
        DB_URI = credentials('db-uri')
    }

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
                    sh 'docker build -t ml-pipeline-test .'
                }
            }
        }

        // === Stage 3: Run tests inside the Docker container ===
        stage('Run Tests') {
            steps {
                // Write environment variables to a temporary file
                // KEEP SINGLE QUOTE FOR SECURITY PURPOSES (MORE INFO HERE: https://www.jenkins.io/doc/book/pipeline/jenkinsfile/#handling-credentials)
                script {
                    writeFile file: 'env.list', text: "DB_URI=$DB_URI"
                }

                // Run a temporary Docker container and pass env variables securely via --env-file
                sh '''
                docker run --rm --env-file env.list \
                ml-pipeline-test \
                bash -c "pytest --maxfail=1 --disable-warnings --junitxml=results.xml"
                '''
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
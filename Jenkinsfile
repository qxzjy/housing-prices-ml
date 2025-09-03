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
                    docker.build("${DOCKER_IMAGE}:latest")
                }
            }
        }

        // === Stage 3: Run tests inside the Docker container ===
        stage('Run Tests') {
            steps {
                script {
                    // Run a command inside the Docker container built earlier
                    // This uses pytest to run tests and outputs results to results.xml
                    docker.image("${DOCKER_IMAGE}:latest").inside {
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

        // stage('Run Tests Inside Docker Container') {
        //     steps {
        //         withCredentials([
        //             string(credentialsId: 'mlflow-tracking-uri', variable: 'MLFLOW_TRACKING_URI'),
        //             string(credentialsId: 'aws-access-key', variable: 'AWS_ACCESS_KEY_ID'),
        //             string(credentialsId: 'aws-secret-key', variable: 'AWS_SECRET_ACCESS_KEY'),
        //             string(credentialsId: 'backend-store-uri', variable: 'BACKEND_STORE_URI'),
        //             string(credentialsId: 'artifact-root', variable: 'ARTIFACT_ROOT'),
        //             string(credentialsId: 'mlflow-experiment-name', variable: 'MLFLOW_EXPERIMENT_NAME')
        //         ]) {
        //             // Write environment variables to a temporary file
        //             // KEEP SINGLE QUOTE FOR SECURITY PURPOSES (MORE INFO HERE: https://www.jenkins.io/doc/book/pipeline/jenkinsfile/#handling-credentials)
        //             script {
        //                 writeFile file: 'env.list', text: '''
        //                 MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI
        //                 AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
        //                 AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
        //                 BACKEND_STORE_URI=$BACKEND_STORE_URI
        //                 ARTIFACT_ROOT=$ARTIFACT_ROOT
        //                 MLFLOW_EXPERIMENT_NAME=$MLFLOW_EXPERIMENT_NAME
        //                 '''
        //             }

        //             // Run a temporary Docker container and pass env variables securely via --env-file
        //             sh '''
        //             docker run --rm --env-file env.list \
        //             ml-pipeline-image \
        //             bash -c "pytest --maxfail=1 --disable-warnings"
        //             '''
        //         }
        //     }
        // }
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
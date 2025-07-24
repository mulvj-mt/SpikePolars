# Spike Polars

## Purpose
To demonstrate the feasibility of replacing existing ETL tasks in the Skills For Care Data Platform.

## Prerequisites
- Access to an AWS account, with permissions to create resources in ECS, IAM, ECR, S3 and Step Functions
- Docker
- The project is built using the [uv](https://docs.astral.sh/uv/) build tool, along with [PoeThePoet](https://poethepoet.natn.io/index.html).
You will need to have both these tools installed prior to development.
- Terraform

## Local Build and Deployment

### Project Set Up
1. Fork and clone the repository to your local machine.
2. Run `poe check` - this will build the project and run all tests (there are no unit tests but linting, security and type safety are tested)

### AWS Setup
1. Authenticate to the AWS account on the command line, using your usual method (e.g. AWS-Vault).
2. On the AWS console, create an S3 bucket. The code is currently configured to work with a bucket called `spike-polars-data`, but you can
change this in the Terraform configuration (see `variables.tf`) if need be. 
3. Run: `uv run makedata.py` - this will create a large data file called `fake_data.csv` and an associated `schema.json`.
4. Copy the data file and the schema to S3:
    ```bash
      aws s3 cp fake_data.csv s3://spike-polars-data/source/fake_data.csv
      aws s3 cp schema.json  s3://spike-polars-data/schema/schema.json 
    ```
   Change the S3 bucket name if needed.
3. Create an ECR repository. The code is configured to use a repository called `spike/spikepolars`, but again this can be changed in the
Terraform configuration.
4. Use the standard AWS CLI command to log in to ECR, replacing the region and account number as required:
    ```bash
      aws ecr get-login-password --region <REGION> | docker login --username AWS --password-stdin <ACCOUNT NUMBER>.dkr.ecr.<REGION>.amazonaws.com
    ```

### Docker Setup (assuming MacBook)
1. Make sure the Docker daemon (Desktop) is running.
2. Check that you have `buildx` installed: `docker buildx version`. If not, you will need to upgrade Docker.
3. Create a builder: `docker buildx create --name mybuilder --use` (replacing "mybuilder" with any name you want).
4. Check that the builder includes `linux/amd64` - you should see it mentioned if you run: `docker buildx inspect --bootstrap`
5. Then, build, tag and push the Docker image:
    ```bash
      docker buildx build --platform linux/amd64 -t spikepolars . --load 
      docker tag spikepolars:latest <ECR REPO URL>:latest
      docker push <ECR REPO URL>:latest 
    ```

### Terraform Setup
1. Change to the `terraform` directory.
2. Run `terraform init`.
3. Then:
    ```bash
      terraform plan
      terraform apply
    ```

## Execution
Go to the `Step Functions` page in the AWS console, select `SpikePolars-ecs-task-runner-sfn`, and hit the `Start execution` button. After about a minute,
you should see a successful run. You should be able to verify that your S3 bucket has a new file called `destination/fake_data.parquet`.

## Cleanup
1. In the `terraform` directory, run `terraform destroy`.
2. Delete the ECR repository.
3. Empty and delete the S3 bucket.


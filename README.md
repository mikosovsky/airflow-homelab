# airflow-homelab
Generating fernetkey and JWT secret:
```py
from cryptography.fernet import Fernet
import secrets; import base64
print(f'AIRFLOW__CORE__FERNET_KEY={Fernet.generate_key().decode()}')
print(f'AIRFLOW__API_AUTH__JWT_SECRET={base64.urlsafe_b64encode(secrets.token_bytes(64)).decode()}')
```
Building image from Dockerfile:
```zsh
docker build -t my-airflow:local -f Dockerfile .
```
Starting docker compose with new image of airflow:
```zsh
AIRFLOW_IMAGE_NAME=my-airflow:local docker compose up -d
```
Shutting down docker compose:
```zsh
docker compose down --volumes --rmi all 
```
content of seaweedfs/s3_config.json:
```json
{
    "identities": [
        {
            "name": "airflow-local",
            "credentials": [
                {
                    "accessKey": "<access_key>",
                    "secretKey": "<secret_access_key>"
                }
            ],
            "actions": [
                "Admin",
                "Read",
                "Write",
                "List",
                "Tagging"
            ]
        }
    ]
}
```
Additional config for secret in airflow to get access to local s3:
```json
{
  "aws_access_key_id": "<access_key>",
  "aws_secret_access_key": "<secret_access_key>",
  "endpoint_url": "http://seaweedfs:8333",
  "region_name": "us-east-1"
}
```

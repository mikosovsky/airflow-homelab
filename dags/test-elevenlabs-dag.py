from datetime import datetime
import base64

from airflow.decorators import dag, task
from airflow.providers.elevenlabs.hooks.elevenlabs import ElevenLabsHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook


@dag(start_date=datetime(2024, 1, 1), schedule=None, catchup=False)
def elevenlabs_hook_example():
    @task
    def generate():
        elevenlabs_hook = ElevenLabsHook("elevenlabs_default")
        s3_hook = S3Hook(aws_conn_id="local_s3")
        bucket_name = "demo-bucket"
        if not s3_hook.check_for_bucket(bucket_name):
            s3_hook.create_bucket(bucket_name=bucket_name)
        audio = elevenlabs_hook.text_to_speech("Cześć, to test z Airflow i ElevenLabs.")
        s3_hook = S3Hook(aws_conn_id="local_s3")
        bucket_name = "demo-bucket"
        if not s3_hook.check_for_bucket(bucket_name):
            s3_hook.create_bucket(bucket_name=bucket_name)
        audio_data = base64.b64decode(audio.audio_base_64)
        s3_hook.load_bytes(
            bytes_data=audio_data,
            key="elevenlabs/audio.mp3",
            bucket_name=bucket_name,
            replace=True,
        )

    generate()


dag = elevenlabs_hook_example()

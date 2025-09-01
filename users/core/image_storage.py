from minio import Minio

from users.config import config


def s3_storage_initialize():
    """Initialize S3 storage using minio client."""
    client = Minio(
        endpoint=f"{config.MINIO.HOST}:{config.MINIO.PORT}",
        access_key=config.MINIO.USER,
        secret_key=config.MINIO.PASSWORD,
        # Change in the future before production launch.
        secure=False
    )
    bucket_name = config.MINIO.BUCKET
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
    return client

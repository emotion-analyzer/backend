import io
import json

from minio import Minio

from users.config import config


def s3_storage_initialize():
    """Initialize S3 storage using minio client."""
    client = Minio(
        endpoint=f"{config.MINIO.HOST}:{config.MINIO.PORT}",
        access_key=config.MINIO.USER,
        secret_key=config.MINIO.PASSWORD,
        # HTTPS, change in the future before production launch.
        secure=False
    )
    if not client.bucket_exists(config.MINIO.BUCKET):
        client.make_bucket(config.MINIO.BUCKET)

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{config.MINIO.BUCKET}/*"]
            }
        ]
    }

    client.set_bucket_policy(config.MINIO.BUCKET, json.dumps(policy))
    return client


def s3_store(user_id, avatar, extension, minio_client):
    """Store image in S3 using minio client."""
    image_stream = io.BytesIO(avatar)
    content_type = f"image/{extension}"
    minio_client.put_object(
        bucket_name=config.MINIO.BUCKET,
        object_name=f"{user_id}.{extension}",
        data=image_stream,
        length=len(image_stream.getvalue()),
        content_type=content_type
    )
    return s3_get_image_url(user_id, extension)


def s3_get_image_url(user_id, extension):
    """Get a presigned URL for the image (temporary access)."""
    url =  (f"{config.MINIO.ADDRESS}:{config.MINIO.PORT}/"
            f"{config.MINIO.BUCKET}/{user_id}.{extension}")
    return url

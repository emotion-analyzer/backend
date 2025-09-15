import base64


def decode_b64(data_uri: str):
    """Decode dataURI and store it in S3 storage."""
    header, b64_data = data_uri.split(",", 1)
    extension = header.split("/")[1].split(";")[0]
    return extension, base64.b64decode(b64_data)

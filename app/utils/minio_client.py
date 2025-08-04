import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException
from minio import Minio
from minio.error import S3Error
from ..core.config import settings
import logging
import json

logger = logging.getLogger(__name__)

class MinIOClient:
    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket {self.bucket_name}")
                self._set_bucket_public()
                logger.info(f"Created bucket {self.bucket_name}")
            else:
                # Ensure existing bucket is public
                self._set_bucket_public()
        except S3Error as e:
            logger.error(f"Error creating bucket: {e}")
            raise HTTPException(status_code=500, detail="Storage service error")
    
    def _set_bucket_public(self):
        """Set bucket policy to allow public read access"""
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"]
                }
            ]
        }
        
        try:
            self.client.set_bucket_policy(self.bucket_name, json.dumps(policy))
            logger.info(f"Set public read policy for bucket {self.bucket_name}")
        except S3Error as e:
            logger.warning(f"Could not set bucket policy (might already be set): {e}")

    def upload_file(self, file: UploadFile) -> str:
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Only image files are allowed")
        
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        file_name = f"{uuid.uuid4()}.{file_extension}"
        
        try:
            file.file.seek(0)
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=file_name,
                data=file.file,
                length=file.size,
                content_type=file.content_type
            )
            
            return file_name
        except S3Error as e:
            logger.error(f"Error uploading file: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload file")
        except Exception as e:
            logger.error(f"Unexpected error uploading file: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload file")

    def build_file_url(self, object_name: str) -> str:
        if settings.IS_PRODUCTION:
            protocol = "https"
        else:
            protocol = "http"
        # Use public URL
        # url = self.client.presigned_get_object(self.bucket_name, object_name)
        url = f"{protocol}://{settings.CDN_ENDPOINT}/{self.bucket_name}/{object_name}"
        # return url.replace("minio:9000", f"{settings.CDN_ENDPOINT}")
        return url

    def delete_file(self, object_name: str) -> bool:
        try:
            object_name = object_name.split('/')[-1]
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            logger.error(f"Error deleting file: {e}")
            return False

minio_client = MinIOClient()
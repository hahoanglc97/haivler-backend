import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException
from minio import Minio
from minio.error import S3Error
from ..core.config import settings
import logging

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
        except S3Error as e:
            logger.error(f"Error creating bucket: {e}")
            raise HTTPException(status_code=500, detail="Storage service error")
    
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
            
            file_url = self.get_file_url(file_name)
            return file_url
        except S3Error as e:
            logger.error(f"Error uploading file: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload file")
        except Exception as e:
            logger.error(f"Unexpected error uploading file: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload file")
    
    def get_file_url(self, object_name: str) -> str:
        if settings.MINIO_SECURE:
            protocol = "https"
        else:
            protocol = "http"
        # Use public URL
        url = self.client.presigned_get_object(self.bucket_name, object_name)
        # url = f"{protocol}://{settings.MINIO_ENDPOINT}/{self.bucket_name}/{object_name}"
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
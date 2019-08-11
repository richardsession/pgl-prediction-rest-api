import os
import logging
import boto3
import magic
from boto3.s3.transfer import TransferConfig
from botocore.exceptions import ClientError
from datetime import datetime
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

class FileManager:

    def __init__(self, bucket, valid_mime_types):
        self.bucket = bucket
        self.valid_mime_types = valid_mime_types
        self.dir = 'uploads'
        self.s3_client = boto3.client(
            's3', 
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'), 
            aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
            region_name=os.getenv('AWS_REGION')
        )

    def upload(self, file):
        try:
            new_filename = self.change_filename(file)

            file.save(new_filename)

            if not self.is_valid_type(new_filename):
                return False

            with open(new_filename, 'rb') as f:
                self.s3_client.put_object(
                    Body=f.read(), 
                    Bucket=self.bucket,
                    Key=new_filename
                )
                
                return new_filename


            return False
        except ClientError as e:
            logging.error(e)
            return False

    def upload_new_version(self, file, filename=None):
        try:
            if filename is None:
                filename = file.filename

            save_path = os.path.join('uploads', secure_filename(filename))

            os.remove(save_path)

            with open(save_path, 'ab') as f:
                f.write(file.stream.read())

            # if not self.is_valid_type('uploads/' + filename):
            #     return False

            # Upload setup for large files
            config = TransferConfig(
                multipart_threshold=1024 * 25, 
                max_concurrency=10,
                multipart_chunksize=1024 * 25, 
                use_threads=True
            )
            
            self.s3_client.upload_file(
                save_path,
                self.bucket,
                filename,
                Config=config
            )

            return filename
        except ClientError as e:
            logging.error('Unable to update file version')
            logging.error(e)
            return False
        
    def is_valid_type(self, filename):
        mime_type = magic.from_file(filename, mime=True)

        return mime_type in self.valid_mime_types

    def change_filename(self, file):
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        filename = str(timestamp) + '_' + secure_filename(file.filename)

        return filename

    def get_file(self, key):
        try:
            file_object = self.s3_client.Object(self.bucket, key)

            return file_object
        except ClientError as e:
            logging.error(e)
            return False

    def download_file(self, key):
        try:
            file_object = self.get_file(key)
            file_object.download_file()

            return True
        except ClientError as e:
            logging.error(e)
            return False        
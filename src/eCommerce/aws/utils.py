import boto3

StaticRootS3BotoStorage = None #lambda: S3Boto3Storage(location='static')
MediaRootS3BotoStorage  = None #lambda: S3Boto3Storage(location='media')
ProtectedS3Storage  = None #lambda: S3Boto3Storage(location='protected')

import datetime
import os
import dotenv
dotenv.read_dotenv()

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", None)
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", None)
AWS_FILE_EXPIRE = 200
AWS_PRELOAD_METADATA = True
AWS_QUERYSTRING_AUTH = False
DEFAULT_FILE_STORAGE = os.environ.get("DEFAULT_FILE_STORAGE")
STATICFILES_STORAGE = os.environ.get("STATICFILES_STORAGE")
AWS_STORAGE_BUCKET_NAME = str(os.environ.get("AWS_STORAGE_BUCKET_NAME", None))
S3DIRECT_REGION = os.environ.get("S3DIRECT_REGION", None)
S3_URL = '//%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
MEDIA_URL = '//%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
MEDIA_ROOT = MEDIA_URL
PROTECTED_ROOT_URL = '//%s.s3.amazonaws.com/protected/' % AWS_STORAGE_BUCKET_NAME
PROTECTED_ROOT = PROTECTED_ROOT_URL
STATIC_URL = S3_URL + 'static/'
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
two_months = datetime.timedelta(days=61)
date_two_months_later = datetime.date.today() + two_months
expires = date_two_months_later.strftime("%A, %d %B %Y 20:00:00 GMT")
AWS_HEADERS = { 
    'Expires': expires,
    'Cache-Control': 'max-age=%d' % (int(two_months.total_seconds()), ),
}
AWS_GROUP_NAME = os.environ.get("AWS_GROUP_NAME", None)
AWS_USERNAME = os.environ.get("AWS_USERNAME", None)

PROTECTED_DIR_NAME = 'protected'
PROTECTED_MEDIA_URL = '//%s.s3.amazonaws.com/%s/' %( AWS_STORAGE_BUCKET_NAME, PROTECTED_DIR_NAME)

AWS_DOWNLOAD_EXPIRE = 5000 #(0ptional, in milliseconds)

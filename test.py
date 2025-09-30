import boto3

# 🔑 Replace with your lease credentials
ACCESS_KEY = "AKIA56YMFI767W2XKV4A"
SECRET_KEY = "9WGJgHRKyYVxhI56kcuSr+SYcHk2XipSuUM+hl9J"
# SESSION_TOKEN = "YOUR_SESSION_TOKEN"

# 🔧 Replace with your bucket + region
BUCKET = "lease-test-bucket-20250928"
REGION = "eu-north-1"

s3 = boto3.client(
    "s3",
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    # aws_session_token=SESSION_TOKEN,
    region_name=REGION
)

res = s3.list_objects_v2(Bucket=BUCKET)
for obj in res.get("Contents", []):
    print(obj["Key"])

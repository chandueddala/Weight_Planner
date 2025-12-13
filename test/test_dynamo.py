import os
from dotenv import load_dotenv
import boto3

load_dotenv()

AWS_PROFILE = os.getenv("AWS_PROFILE", "default")
AWS_REGION  = os.getenv("AWS_REGION", "us-east-1")

print("Using AWS_PROFILE =", AWS_PROFILE)
print("Using AWS_REGION  =", AWS_REGION)

# Force boto3 to use your CLI profile + region
session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)

# Prove account
sts = session.client("sts")
print("STS:", sts.get_caller_identity())

# Prove DynamoDB tables exist in THIS region/account
ddb = session.client("dynamodb")
tables = ddb.list_tables()["TableNames"]
print("Tables:", tables)

# Must contain these:
assert "Users" in tables and "UserSessions" in tables, "Tables not found in this region/profile"

# Now do put_item
users = session.resource("dynamodb").Table("Users")
users.put_item(Item={
    "user_id": "test-user-1",
    "email": "test@example.com",
    "credits_remaining": 10,
    "plan": "free"
})
print("✅ put_item OK")

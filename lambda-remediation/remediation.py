import boto3
import json

s3 = boto3.client("s3")

def lambda_handler(event, context):
    detail = event.get("detail", {})
    resource_id = detail.get("resourceId")

    if not resource_id:
        print("No resourceId found in event, skipping.")
        return {"statusCode": 400, "body": "Missing resourceId"}

    print(f"Remediating bucket: {resource_id}")

    # Remove the public-read bucket policy
    try:
        s3.delete_bucket_policy(Bucket=resource_id)
        print(f"Removed public bucket policy from {resource_id}")
    except Exception as e:
        print(f"Could not delete bucket policy: {e}")

    # Re-block public access at the bucket level, belt and braces
    s3.put_public_access_block(
        Bucket=resource_id,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True,
        },
    )
    print(f"Re-enabled public access block on {resource_id}")

    return {"statusCode": 200, "body": json.dumps({"remediated": resource_id})}
# AWS Healthcare Compliance & Automated Remediation Platform

A serverless AWS pipeline that continuously monitors cloud resources for security misconfigurations, automatically alerts on violations, self-heals the problem, and keeps a full audit trail — built solo, from the ground up, as a technical demonstration inspired by HIPAA-style compliance requirements.

> **Note:** This project demonstrates AWS security/compliance engineering concepts. It is **not** a certified HIPAA-compliant environment and makes no claim of regulatory compliance.

---

## Architecture

```
AWS Config → EventBridge → SNS (alert) + Lambda (auto-remediate) → CloudTrail (audit)
```

1. **AWS Config** continuously evaluates S3 buckets against a public-access rule.
2. **EventBridge** listens for compliance state changes and fires the moment a resource goes `NON_COMPLIANT`.
3. **SNS** emails a real-time alert with the violation details.
4. **Lambda** automatically removes the offending public bucket policy and re-locks public access.
5. **CloudTrail** logs every API call involved, providing a full audit trail of both the violation and the fix.

---

## Why the rule changed from the original plan

The project was originally scoped around an S3 **encryption** rule. During the build, AWS's current default behavior (auto-encrypting new S3 buckets) made that rule unable to produce a real violation — every new bucket came back `COMPLIANT` immediately. Rather than fake the finding, the project pivoted to a rule AWS does *not* auto-remediate: **S3 public read access** — arguably a more realistic and higher-impact real-world scenario, since accidental public buckets are a common cause of real cloud data breaches.

---

## AWS Resources Built

| Component | Resource | Region |
|---|---|---|
| Config recorder | `default` | eu-central-1 |
| Config rules | `s3-bucket-server-side-encryption-enabled`, `s3-bucket-public-read-prohibited` | eu-central-1 |
| Config delivery bucket | `aws-config-bucket-900429455393` | eu-central-1 |
| Test resource | `compliance-test-bucket-900429455393` | eu-central-1 |
| EventBridge rule | `config-noncompliant-rule` | eu-central-1 |
| SNS topic | `compliance-alerts` | eu-central-1 |
| Lambda function | `s3-public-access-remediation` (Python 3.12) | eu-central-1 |
| IAM role | `lambda-remediation-role` | — |
| CloudTrail trail | `compliance-trail` → `compliance-cloudtrail-logs-900429455393` | eu-central-1 |

---

## How Remediation Works

`lambda-remediation/remediation.py` is triggered by EventBridge whenever Config reports a `NON_COMPLIANT` public-access violation. It:
1. Deletes the offending bucket policy (`s3:DeleteBucketPolicy`)
2. Re-applies a full public access block (`s3:PutBucketPublicAccessBlock`) as a belt-and-braces safeguard
3. Logs its actions to CloudWatch Logs for traceability

IAM permissions for the Lambda execution role are scoped to only the actions it needs — no wildcard admin access.

---

## End-to-End Test Results

The full pipeline was validated running unattended — the test bucket was made public via `put-bucket-policy`, and every downstream step fired automatically with no manual intervention:

1. ✅ Config detected the bucket transition from `COMPLIANT` → `NON_COMPLIANT`
2. ✅ EventBridge caught the compliance change event
3. ✅ SNS delivered a real-time email alert containing the violation annotation ("The S3 bucket policy allows public read access.")
4. ✅ Lambda executed automatically and removed the public policy (`NoSuchBucketPolicy` confirmed on lookup — no manual Lambda invocation)
5. ✅ Config re-evaluated the bucket and confirmed `COMPLIANT` on its own
6. ✅ CloudTrail recorded the underlying API activity throughout

Screenshots of each stage are in `/screenshots`.

---

## Running the Demo Yourself

```bash
# 1. Make the test bucket public (recreates the violation)
aws s3api put-public-access-block --bucket compliance-test-bucket-900429455393 \
  --public-access-block-configuration BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false

aws s3api put-bucket-policy --bucket compliance-test-bucket-900429455393 --policy file://public-policy.json

# 2. Force Config to notice
aws configservice start-config-rules-evaluation --config-rule-names s3-bucket-public-read-prohibited

# 3. Wait ~1-2 minutes, then watch:
#    - your inbox for the SNS alert
#    - aws s3api get-bucket-policy --bucket compliance-test-bucket-900429455393  (should error NoSuchBucketPolicy once fixed)
#    - aws configservice get-compliance-details-by-config-rule --config-rule-name s3-bucket-public-read-prohibited  (should show COMPLIANT again)
```

---

## Cost Control

This project uses only S3, Config, EventBridge, SNS, Lambda, and CloudTrail — no EC2, RDS, or NAT Gateway. To avoid ongoing charges when not actively demoing:

```bash
aws configservice stop-configuration-recorder --configuration-recorder-name default
aws cloudtrail stop-logging --name compliance-trail --region eu-central-1
```

Both can be restarted at any time (`start-configuration-recorder` / `start-logging`) without losing any of the built infrastructure.

---

## What I Learned

This was my first hands-on cloud infrastructure project, built entirely from the command line with no prior AWS or terminal experience. Along the way I worked through:
- IAM roles, trust policies, and least-privilege permission scoping
- Event-driven architecture (EventBridge pattern matching on state *changes*, not just states)
- S3 bucket policies vs. account/bucket-level public access blocks, and how they interact
- Debugging real AWS errors (delivery channel ordering, S3 bucket policy propagation, IAM role propagation delays)
- Writing and deploying a Python Lambda function with a scoped IAM execution role

---

## Portfolio Summary

**AWS Healthcare Compliance & Automated Remediation Platform**
Designed and implemented a serverless AWS compliance platform using AWS Config, EventBridge, Lambda, SNS, CloudTrail and IAM to continuously evaluate cloud resources against security policies, generate real-time compliance alerts, and automatically remediate public-access misconfigurations. Implemented least-privilege IAM and validated a full unattended end-to-end detection, notification, remediation, and audit workflow.

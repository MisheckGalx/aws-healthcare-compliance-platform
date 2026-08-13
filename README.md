# AWS Healthcare Compliance & Automated Remediation Platform

A serverless AWS pipeline that continuously monitors cloud resources for security misconfigurations, automatically alerts on violations, self-heals the problem, and keeps a full audit trail.

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

## Portfolio Summary

**AWS Healthcare Compliance & Automated Remediation Platform**
Designed and implemented a serverless AWS compliance platform using AWS Config, EventBridge, Lambda, SNS, CloudTrail and IAM to continuously evaluate cloud resources against security policies, generate real-time compliance alerts, and automatically remediate public-access misconfigurations. Implemented least-privilege IAM and validated a full unattended end-to-end detection, notification, remediation, and audit workflow.

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

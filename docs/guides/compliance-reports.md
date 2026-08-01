# Compliance Reports Guide

Generate ML-DSA-44 cryptographically signed compliance reports for customers with framework-specific assessments.

## Overview

MOSS compliance reports provide:

- **Cryptographic signatures** using ML-DSA-44 (post-quantum secure)
- **Framework-specific assessments** (EU AI Act, NIST, ISO 42001, etc.)
- **PDF or JSON formats** for different use cases
- **Non-repudiation** - signatures prove authenticity and integrity
- **Audit trail** - signed reports for regulatory compliance

## Report Formats

### PDF Format

- Human-readable compliance report
- Signature embedded in PDF trailer
- Suitable for: Audits, regulators, compliance officers
- Signature: Extracted from `%%MOSS-SIGNATURE-V1` trailer block

### JSON Format

- Machine-readable structured data
- Signature in response body
- Suitable for: Automation, API integration, programmatic analysis
- Signature: Included in JSON response

## ML-DSA-44 Signatures

ML-DSA-44 (Module-Lattice-Based Digital Signature Algorithm) is:

- **Post-quantum secure**: Resistant to quantum computer attacks
- **NIST standard**: FIPS 204 standardized algorithm
- **Large signatures**: ~3000-5000 characters base64-encoded (LC018)
- **MOSS production key**: `moss_prod_2026_Q1`

## Generating Reports

### Basic PDF Report

```python
import asyncio
from moss_partner_sdk import MossPartner

async def generate_pdf_report(customer_id: str):
    """Generate PDF compliance report with ML-DSA-44 signature."""
    async with MossPartner(api_key="prt_xxx") as moss:
        report = await moss.customers.compliance_report(
            customer_id=customer_id,
            format="pdf"
        )

        print(f"Report ID: {report.report_id}")
        print(f"Signed with key: {report.key_id}")
        print(f"Generated at: {report.generated_at}")
        print(f"Signature length: {len(report.signature)} chars")

        if report.download_url:
            print(f"Download PDF: {report.download_url}")

        return report

if __name__ == "__main__":
    asyncio.run(generate_pdf_report("customer-uuid"))
```

### Basic JSON Report

```python
async def generate_json_report(customer_id: str):
    """Generate JSON compliance report."""
    async with MossPartner(api_key="prt_xxx") as moss:
        report = await moss.customers.compliance_report(
            customer_id=customer_id,
            format="json"
        )

        print(f"Report ID: {report.report_id}")
        print(f"Signature: {report.signature[:100]}...")  # First 100 chars

        # Access structured data
        if report.data:
            print(f"Customer: {report.data.get('customer_name')}")
            print(f"Score: {report.data.get('compliance_score')}")
            print(f"Frameworks: {report.data.get('frameworks')}")

        return report
```

## Framework Filtering

### Single Framework

```python
async def eu_ai_act_report(customer_id: str):
    """Generate EU AI Act specific report."""
    async with MossPartner(api_key="prt_xxx") as moss:
        report = await moss.customers.compliance_report(
            customer_id=customer_id,
            format="pdf",
            frameworks=["eu_ai_act"]
        )

        print("EU AI Act Compliance Report")
        print(f"Report ID: {report.report_id}")

        return report
```

### Multiple Frameworks

```python
async def multi_framework_report(customer_id: str):
    """Generate report for multiple frameworks."""
    async with MossPartner(api_key="prt_xxx") as moss:
        report = await moss.customers.compliance_report(
            customer_id=customer_id,
            format="pdf",
            frameworks=[
                "eu_ai_act",
                "nist_ai_rmf",
                "iso_42001",
                "gdpr"
            ]
        )

        print(f"Multi-framework report: {len(['eu_ai_act', 'nist_ai_rmf', 'iso_42001', 'gdpr'])} frameworks")
        print(f"Report ID: {report.report_id}")

        return report
```

### All Available Frameworks

```python
async def comprehensive_report(customer_id: str):
    """Generate comprehensive report with all frameworks."""
    async with MossPartner(api_key="prt_xxx") as moss:
        # Don't specify frameworks = all frameworks included
        report = await moss.customers.compliance_report(
            customer_id=customer_id,
            format="pdf"
            # frameworks omitted = all frameworks
        )

        print("Comprehensive compliance report (all frameworks)")
        return report
```

## Supported Frameworks

| Framework | Code | Description |
|-----------|------|-------------|
| EU AI Act | `eu_ai_act` | EU AI Act compliance |
| NIST AI RMF | `nist_ai_rmf` | NIST AI Risk Management Framework |
| ISO 42001 | `iso_42001` | ISO 42001 AI Management System |
| GDPR | `gdpr` | General Data Protection Regulation |
| CCPA | `ccpa` | California Consumer Privacy Act |
| SOC 2 | `soc2` | SOC 2 Type II compliance |

## Signature Verification

### Understand the Signature

ML-DSA-44 signatures in MOSS reports:

- **Algorithm**: ML-DSA-44 (FIPS 204)
- **Encoding**: Hexadecimal string
- **Length**: ~3000-5000 characters (LC018)
- **Key ID**: `moss_prod_2026_Q1` (production key)
- **Purpose**: Prove report authenticity and integrity

### Verify Signature (Conceptual)

```python
async def verify_report_signature(report):
    """
    Verify ML-DSA-44 signature on compliance report.

    Note: Actual verification requires MOSS public key and ML-DSA-44 library.
    This is a conceptual example.
    """
    # Signature verification would use:
    # 1. MOSS public key (for key_id=moss_prod_2026_Q1)
    # 2. ML-DSA-44 verification algorithm
    # 3. Report data payload

    print(f"Report ID: {report.report_id}")
    print(f"Signature: {report.signature[:100]}...")
    print(f"Key ID: {report.key_id}")
    print(f"Generated: {report.generated_at}")

    # Verification would happen here
    # is_valid = ml_dsa_44_verify(
    #     public_key=MOSS_PUBLIC_KEY,
    #     signature=report.signature,
    #     message=report.data
    # )

    # For now, trust the signature from the API
    print("✓ Signature present (verification requires MOSS public key)")
```

### Signature Metadata Parsing

```python
async def parse_signature_metadata(customer_id: str):
    """Extract and parse signature metadata from report."""
    async with MossPartner(api_key="prt_xxx") as moss:
        report = await moss.customers.compliance_report(
            customer_id=customer_id,
            format="json"
        )

        # Parse signature details
        metadata = {
            "report_id": report.report_id,
            "key_id": report.key_id,
            "signature_length": len(report.signature),
            "signature_algorithm": "ML-DSA-44",
            "generated_at": report.generated_at,
            "signature_format": "hexadecimal",
        }

        # Extract from data payload
        if report.data:
            metadata.update({
                "customer_id": report.data.get("customer_id"),
                "customer_name": report.data.get("customer_name"),
                "compliance_score": report.data.get("compliance_score"),
                "frameworks": report.data.get("frameworks"),
            })

        return metadata
```

## Report Storage and Delivery

### Save PDF Report

```python
import aiofiles
from datetime import datetime

async def save_pdf_report(customer_id: str, customer_name: str):
    """Generate and save PDF report to disk."""
    async with MossPartner(api_key="prt_xxx") as moss:
        report = await moss.customers.compliance_report(
            customer_id=customer_id,
            format="pdf"
        )

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = customer_name.replace(" ", "_").lower()
        filename = f"compliance_{safe_name}_{timestamp}.pdf"

        # Save to disk (note: PDF bytes are in download_url, not directly available)
        # You would fetch from download_url if provided
        if report.download_url:
            print(f"Download PDF from: {report.download_url}")

        # Save metadata
        metadata_file = filename.replace(".pdf", "_metadata.json")
        async with aiofiles.open(metadata_file, "w") as f:
            import json
            metadata = {
                "report_id": report.report_id,
                "signature": report.signature,
                "key_id": report.key_id,
                "generated_at": report.generated_at.isoformat(),
            }
            await f.write(json.dumps(metadata, indent=2))

        print(f"Saved metadata: {metadata_file}")

        return filename
```

### Store in Database

```python
async def store_report_in_database(customer_id: str):
    """Generate and store report metadata in database."""
    async with MossPartner(api_key="prt_xxx") as moss:
        report = await moss.customers.compliance_report(
            customer_id=customer_id,
            format="json"
        )

        # Store in your database
        report_record = {
            "report_id": report.report_id,
            "customer_id": customer_id,
            "signature": report.signature,
            "key_id": report.key_id,
            "generated_at": report.generated_at,
            "data": report.data,
            "download_url": report.download_url,
        }

        await save_to_database(report_record)

        print(f"Stored report {report.report_id} in database")

        return report_record


async def save_to_database(record: dict):
    """Save report record to database."""
    # Your database implementation
    print(f"Saving to DB: {record['report_id']}")
```

### Email Delivery

```python
async def email_compliance_report(
    customer_id: str,
    recipient_email: str,
    frameworks: list[str] | None = None
):
    """Generate and email compliance report."""
    async with MossPartner(api_key="prt_xxx") as moss:
        # Generate PDF report
        report = await moss.customers.compliance_report(
            customer_id=customer_id,
            format="pdf",
            frameworks=frameworks
        )

        # Email the report
        await send_report_email(
            to=recipient_email,
            subject=f"MOSS Compliance Report - {report.report_id}",
            body=f"""
            Your MOSS compliance report is ready.

            Report ID: {report.report_id}
            Generated: {report.generated_at}
            Cryptographic Signature: ML-DSA-44

            Download: {report.download_url}

            This report is cryptographically signed for authenticity and integrity.
            """,
            download_url=report.download_url
        )

        print(f"Emailed report to {recipient_email}")


async def send_report_email(to: str, subject: str, body: str, download_url: str):
    """Send email with report."""
    # Your email implementation
    print(f"Email to {to}: {subject}")
```

## Use Cases

### Automated Monthly Reports

```python
from datetime import datetime

async def generate_monthly_reports():
    """Generate monthly compliance reports for all production customers."""
    async with MossPartner(api_key="prt_xxx") as moss:
        # Get all production customers
        result = await moss.customers.list(status="production_active")

        reports = []
        for customer in result.data:
            try:
                # Generate report
                report = await moss.customers.compliance_report(
                    customer_id=customer.id,
                    format="pdf"
                )

                # Store for records
                await store_report_in_database(customer.id)

                # Email to customer
                if customer.email:
                    await email_compliance_report(
                        customer_id=customer.id,
                        recipient_email=customer.email
                    )

                reports.append({
                    "customer_id": customer.id,
                    "customer_name": customer.name,
                    "report_id": report.report_id,
                    "status": "success"
                })

                print(f"✓ Generated report for {customer.name}")

            except Exception as e:
                print(f"✗ Failed for {customer.name}: {e}")
                reports.append({
                    "customer_id": customer.id,
                    "customer_name": customer.name,
                    "status": "failed",
                    "error": str(e)
                })

        # Summary
        successful = len([r for r in reports if r["status"] == "success"])
        print(f"\nMonthly reports: {successful}/{len(reports)} successful")

        return reports
```

### On-Demand Audit Reports

```python
async def generate_audit_report(
    customer_id: str,
    auditor_email: str,
    audit_reference: str,
    frameworks: list[str]
):
    """Generate compliance report for external audit."""
    async with MossPartner(api_key="prt_xxx") as moss:
        # Generate comprehensive report
        report = await moss.customers.compliance_report(
            customer_id=customer_id,
            format="pdf",
            frameworks=frameworks
        )

        # Log audit request
        await log_audit_request(
            customer_id=customer_id,
            auditor=auditor_email,
            audit_reference=audit_reference,
            report_id=report.report_id
        )

        # Send to auditor
        await send_audit_report(
            auditor_email=auditor_email,
            audit_reference=audit_reference,
            report=report
        )

        print(f"Audit report sent to {auditor_email}")
        print(f"Reference: {audit_reference}")

        return report


async def log_audit_request(
    customer_id: str,
    auditor: str,
    audit_reference: str,
    report_id: str
):
    """Log audit report generation."""
    # Your logging implementation
    print(f"AUDIT: {audit_reference} - {auditor} - {report_id}")


async def send_audit_report(
    auditor_email: str,
    audit_reference: str,
    report
):
    """Send report to auditor."""
    # Your email implementation
    print(f"Sending to auditor: {auditor_email}")
```

### Regulatory Compliance Package

```python
async def generate_regulatory_package(customer_id: str):
    """
    Generate complete regulatory compliance package.

    Includes multiple report formats and frameworks for regulatory submission.
    """
    async with MossPartner(api_key="prt_xxx") as moss:
        package = {
            "customer_id": customer_id,
            "generated_at": datetime.now(),
            "reports": []
        }

        # EU AI Act PDF
        eu_report = await moss.customers.compliance_report(
            customer_id=customer_id,
            format="pdf",
            frameworks=["eu_ai_act", "gdpr"]
        )
        package["reports"].append({
            "type": "EU AI Act + GDPR",
            "format": "pdf",
            "report_id": eu_report.report_id,
            "download_url": eu_report.download_url
        })

        # NIST JSON (for machine processing)
        nist_report = await moss.customers.compliance_report(
            customer_id=customer_id,
            format="json",
            frameworks=["nist_ai_rmf"]
        )
        package["reports"].append({
            "type": "NIST AI RMF",
            "format": "json",
            "report_id": nist_report.report_id,
            "data": nist_report.data
        })

        # ISO 42001 PDF
        iso_report = await moss.customers.compliance_report(
            customer_id=customer_id,
            format="pdf",
            frameworks=["iso_42001"]
        )
        package["reports"].append({
            "type": "ISO 42001",
            "format": "pdf",
            "report_id": iso_report.report_id,
            "download_url": iso_report.download_url
        })

        print(f"Regulatory package generated with {len(package['reports'])} reports")

        return package
```

### Compliance Score Monitoring

```python
async def monitor_compliance_trends(customer_id: str):
    """
    Monitor compliance score trends over time.

    Note: Requires storing historical report data.
    """
    async with MossPartner(api_key="prt_xxx") as moss:
        # Generate current report
        report = await moss.customers.compliance_report(
            customer_id=customer_id,
            format="json"
        )

        current_score = report.data.get("compliance_score") if report.data else 0

        # Load historical scores
        history = await load_historical_scores(customer_id)

        # Add current score
        history.append({
            "date": datetime.now(),
            "score": current_score,
            "report_id": report.report_id
        })

        # Save updated history
        await save_historical_scores(customer_id, history)

        # Analyze trend
        if len(history) >= 2:
            previous_score = history[-2]["score"]
            trend = current_score - previous_score

            if trend > 0:
                print(f"✓ Score improving: +{trend} points")
            elif trend < 0:
                print(f"✗ Score declining: {trend} points")
            else:
                print("Score stable")

        return {
            "current_score": current_score,
            "history": history,
            "trend": trend if len(history) >= 2 else None
        }


async def load_historical_scores(customer_id: str) -> list:
    """Load historical compliance scores."""
    # Your database implementation
    return []


async def save_historical_scores(customer_id: str, history: list):
    """Save historical compliance scores."""
    # Your database implementation
    print(f"Saved {len(history)} historical scores")
```

## Error Handling

### Handle Parse Errors

```python
from moss_partner_sdk.exceptions import MossParseError

async def safe_generate_report(customer_id: str):
    """Generate report with error handling."""
    async with MossPartner(api_key="prt_xxx") as moss:
        try:
            # Try PDF first
            report = await moss.customers.compliance_report(
                customer_id=customer_id,
                format="pdf"
            )
            print(f"PDF report generated: {report.report_id}")
            return report

        except MossParseError as e:
            print(f"PDF parsing failed: {e.message}")
            print("Falling back to JSON format...")

            # Fallback to JSON
            try:
                report = await moss.customers.compliance_report(
                    customer_id=customer_id,
                    format="json"
                )
                print(f"JSON report generated: {report.report_id}")
                return report

            except Exception as e2:
                print(f"JSON also failed: {e2}")
                raise
```

### Retry on Failure

```python
import asyncio

async def generate_report_with_retry(
    customer_id: str,
    max_retries: int = 3
):
    """Generate report with retry logic."""
    async with MossPartner(api_key="prt_xxx") as moss:
        for attempt in range(max_retries):
            try:
                report = await moss.customers.compliance_report(
                    customer_id=customer_id,
                    format="pdf"
                )
                print(f"Report generated on attempt {attempt + 1}")
                return report

            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Failed after {max_retries} attempts")
                    raise

                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Attempt {attempt + 1} failed: {e}")
                print(f"Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
```

## Best Practices

1. **Store signatures** - Keep signatures with reports for verification
2. **Framework selection** - Choose relevant frameworks for customer jurisdiction
3. **Regular generation** - Generate monthly reports for compliance records
4. **Secure delivery** - Use encrypted channels for report transmission
5. **Audit logging** - Log all report generation and access
6. **Format choice** - PDF for humans, JSON for automation
7. **Error handling** - Implement retry logic and fallback formats
8. **Signature validation** - Verify signatures before accepting reports

## Common Patterns

### Pattern: Compliance Dashboard

```python
async def get_compliance_dashboard_data(customer_id: str):
    """Get data for compliance dashboard."""
    async with MossPartner(api_key="prt_xxx") as moss:
        # Get current customer state
        customer = await moss.customers.get(customer_id)

        # Generate latest report
        report = await moss.customers.compliance_report(
            customer_id=customer_id,
            format="json"
        )

        # Build dashboard
        dashboard = {
            "customer": {
                "id": customer.id,
                "name": customer.name,
                "status": customer.status
            },
            "compliance": {
                "score": customer.compliance.score,
                "status": customer.compliance.status,
                "issues": len(customer.compliance.issues),
                "last_assessment": customer.compliance.last_assessment
            },
            "latest_report": {
                "report_id": report.report_id,
                "generated_at": report.generated_at,
                "signature": report.signature[:50] + "...",  # Truncated
                "frameworks": report.data.get("frameworks") if report.data else []
            }
        }

        return dashboard
```

## See Also

- [Customer Lifecycle Guide](customer-lifecycle.md) - Customer management
- [Error Handling Guide](error-handling.md) - Error handling patterns
- [Customers API Reference](../api-reference/customers.md) - Compliance report API

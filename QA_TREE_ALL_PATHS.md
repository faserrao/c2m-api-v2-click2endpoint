# Complete Q&A Decision Tree - All Possible Paths

This document lists all possible paths through the 4-question UI and their resulting endpoints.

## Question Flow Overview

1. **Q1: What type of document submission do you need?**
   - single / multi / merge / pdfSplit

2. **Q2: Will you use a saved job template?** (Shown for: single, multi, merge)
   - true / false

3. **Q3: How will recipient addresses be provided?** (Shown for all types)
   - explicit / template / addressCapture

4. **Q4: Is each document personalized for its recipient?** (Shown for: multi, merge)
   - true / false

## Endpoint Mapping (Updated)

Based on the hardcoded implementation in `app_hardcoded_v1.py`:

1. **`/jobs/single-doc-job-template`** - Single document with job template
2. **`/jobs/single-doc`** - Single document without job template
3. **`/jobs/multi-docs-job-template`** - Multiple documents with job template
4. **`/jobs/multi-doc`** - Multiple documents without job template
5. **`/jobs/multi-doc-merge-job-template`** - Merge multiple documents (always uses template)
6. **`/jobs/single-pdf-split`** - Split PDF (no template support)

## Level 2 Parameters (After Endpoint Selection)

### Document Specification (All 5 EBNF Methods)
When document is required from API call, users can specify via:
1. **Document ID** - Simple string reference (e.g., "doc_12345")
2. **External URL** - URL to fetch document (e.g., "https://example.com/doc.pdf")
3. **Upload Request + Name** - Combination of uploadRequestId + documentName
4. **Zip + Document Name** - Reference within a zip file (zipId + documentName)
5. **Upload Request + Zip + Name** - Reference within a zip in an upload request

### Template Logic (Use Cases 1 and 3)
For endpoints with templates, the template may provide:
- **Job Options** - ALWAYS provided by template
- **Document** OR **Recipients** - May provide one, the other, or neither (NEVER both)

When recipient style is "template":
- Only asks about document source (template or API call)
- No address inputs needed

When recipient style is "explicit":
- Asks about document source
- Shows address input section with options for:
  - Address List ID
  - Single Address ID
  - New Address (full form)

### Payment Types (All 6 from EBNF)
1. **CREDIT_CARD** - Requires card details (number, type, expiration, CVV)
2. **INVOICE** - Requires invoice number
3. **ACH** - Requires routing and account numbers
4. **USER_CREDIT** - Requires credit amount
5. **APPLE_PAY** - Handled by mobile wallet
6. **GOOGLE_PAY** - Handled by mobile wallet

### Job Template
- **Job Template ID** - Primary identifier (e.g., "template_12345")
- **Job Template Name** - Optional human-readable name (e.g., "My Template")
- API uses ID if provided, otherwise falls back to name

### Additional Parameters
- **Tags** - Comma-separated list for job categorization
- **Job Options** - For non-template endpoints (document class, layout, mail class, etc.)

## All Possible Paths and Endpoints

### Path 1: Single Document → Template → Explicit
- Q1: **single** (Single document)
- Q2: **true** (Use saved template)
- Q3: **explicit** (Provided in API call)
- **Endpoint: /jobs/single-doc-job-template**

### Path 2: Single Document → Template → From Template
- Q1: **single** (Single document)
- Q2: **true** (Use saved template)
- Q3: **template** (From template/mailing list)
- **Endpoint: /jobs/single-doc-job-template**

### Path 3: Single Document → Template → Address Capture
- Q1: **single** (Single document)
- Q2: **true** (Use saved template)
- Q3: **addressCapture** (Extract from document)
- **Endpoint: /jobs/single-doc-job-template**

### Path 4: Single Document → No Template → Explicit
- Q1: **single** (Single document)
- Q2: **false** (Configure manually)
- Q3: **explicit** (Provided in API call)
- **Endpoint: /jobs/single-doc**

### Path 5: Single Document → No Template → From Template
- Q1: **single** (Single document)
- Q2: **false** (Configure manually)
- Q3: **template** (From template/mailing list)
- **Endpoint: /jobs/single-doc**

### Path 6: Single Document → No Template → Address Capture
- Q1: **single** (Single document)
- Q2: **false** (Configure manually)
- Q3: **addressCapture** (Extract from document)
- **Endpoint: /jobs/single-doc**

### Path 7: Multiple Documents → Template → Explicit → Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **true** (Use saved template)
- Q3: **explicit** (Provided in API call)
- Q4: **true** (Unique per recipient)
- **Endpoint: /jobs/multi-docs-job-template**

### Path 8: Multiple Documents → Template → Explicit → Not Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **true** (Use saved template)
- Q3: **explicit** (Provided in API call)
- Q4: **false** (Same for all)
- **Endpoint: /jobs/multi-docs-job-template**

### Path 9: Multiple Documents → Template → From Template → Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **true** (Use saved template)
- Q3: **template** (From template/mailing list)
- Q4: **true** (Unique per recipient)
- **Endpoint: /jobs/multi-docs-job-template**

### Path 10: Multiple Documents → Template → From Template → Not Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **true** (Use saved template)
- Q3: **template** (From template/mailing list)
- Q4: **false** (Same for all)
- **Endpoint: /jobs/multi-docs-job-template**

### Path 11: Multiple Documents → Template → Address Capture → Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **true** (Use saved template)
- Q3: **addressCapture** (Extract from document)
- Q4: **true** (Unique per recipient)
- **Endpoint: /jobs/multi-docs-job-template**

### Path 12: Multiple Documents → Template → Address Capture → Not Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **true** (Use saved template)
- Q3: **addressCapture** (Extract from document)
- Q4: **false** (Same for all)
- **Endpoint: /jobs/multi-docs-job-template**

### Path 13: Multiple Documents → No Template → Explicit → Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **false** (Configure manually)
- Q3: **explicit** (Provided in API call)
- Q4: **true** (Unique per recipient)
- **Endpoint: /jobs/multi-doc**

### Path 14: Multiple Documents → No Template → Explicit → Not Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **false** (Configure manually)
- Q3: **explicit** (Provided in API call)
- Q4: **false** (Same for all)
- **Endpoint: /jobs/multi-doc**

### Path 15: Multiple Documents → No Template → From Template → Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **false** (Configure manually)
- Q3: **template** (From template/mailing list)
- Q4: **true** (Unique per recipient)
- **Endpoint: /jobs/multi-doc**

### Path 16: Multiple Documents → No Template → From Template → Not Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **false** (Configure manually)
- Q3: **template** (From template/mailing list)
- Q4: **false** (Same for all)
- **Endpoint: /jobs/multi-doc**

### Path 17: Multiple Documents → No Template → Address Capture → Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **false** (Configure manually)
- Q3: **addressCapture** (Extract from document)
- Q4: **true** (Unique per recipient)
- **Endpoint: /jobs/multi-doc**

### Path 18: Multiple Documents → No Template → Address Capture → Not Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **false** (Configure manually)
- Q3: **addressCapture** (Extract from document)
- Q4: **false** (Same for all)
- **Endpoint: /jobs/multi-doc**

### Path 19: Merge Documents → Template → Explicit → Personalized
- Q1: **merge** (Multiple documents to merge)
- Q2: **true** (Use saved template)
- Q3: **explicit** (Provided in API call)
- Q4: **true** (Unique per recipient)
- **Endpoint: /jobs/multi-doc-merge-job-template**

### Path 20: Merge Documents → Template → Explicit → Not Personalized
- Q1: **merge** (Multiple documents to merge)
- Q2: **true** (Use saved template)
- Q3: **explicit** (Provided in API call)
- Q4: **false** (Same for all)
- **Endpoint: /jobs/multi-doc-merge-job-template**

### Path 21: Merge Documents → Template → From Template → Personalized
- Q1: **merge** (Multiple documents to merge)
- Q2: **true** (Use saved template)
- Q3: **template** (From template/mailing list)
- Q4: **true** (Unique per recipient)
- **Endpoint: /jobs/multi-doc-merge-job-template**

### Path 22: Merge Documents → Template → From Template → Not Personalized
- Q1: **merge** (Multiple documents to merge)
- Q2: **true** (Use saved template)
- Q3: **template** (From template/mailing list)
- Q4: **false** (Same for all)
- **Endpoint: /jobs/multi-doc-merge-job-template**

### Path 23: Merge Documents → Template → Address Capture → Personalized
- Q1: **merge** (Multiple documents to merge)
- Q2: **true** (Use saved template)
- Q3: **addressCapture** (Extract from document)
- Q4: **true** (Unique per recipient)
- **Endpoint: /jobs/multi-doc-merge-job-template**

### Path 24: Merge Documents → Template → Address Capture → Not Personalized
- Q1: **merge** (Multiple documents to merge)
- Q2: **true** (Use saved template)
- Q3: **addressCapture** (Extract from document)
- Q4: **false** (Same for all)
- **Endpoint: /jobs/multi-doc-merge-job-template**

### Path 25: PDF Split → Explicit Addresses
- Q1: **pdfSplit** (Split a combined PDF)
- Q2: (Not shown for pdfSplit)
- Q3: **explicit** (Provided in API call)
- **Endpoint: /jobs/single-pdf-split**

### Path 26: PDF Split → From Template
- Q1: **pdfSplit** (Split a combined PDF)
- Q2: (Not shown for pdfSplit)
- Q3: **template** (From template/mailing list)
- **Endpoint: /jobs/single-pdf-split**

### Path 27: PDF Split → Address Capture
- Q1: **pdfSplit** (Split a combined PDF)
- Q2: (Not shown for pdfSplit)
- Q3: **addressCapture** (Extract from document)
- **Endpoint: /jobs/single-pdf-split**

## Summary of Endpoints

Based on the hardcoded implementation, there are **6 unique endpoints**:

1. **`/jobs/single-doc-job-template`** - Single document with job template
2. **`/jobs/single-doc`** - Single document without job template
3. **`/jobs/multi-docs-job-template`** - Multiple documents with job template
4. **`/jobs/multi-doc`** - Multiple documents without job template
5. **`/jobs/multi-doc-merge-job-template`** - Merge multiple documents (always with template)
6. **`/jobs/single-pdf-split`** - Split PDF (no template support)

## Key Implementation Details

1. **Document Specification**: All endpoints support the 5 EBNF-defined methods
2. **Template Logic**: Templates provide job options + either document OR recipients (never both)
3. **Payment Types**: All 6 payment types from EBNF are supported
4. **Address Input**: Dynamic forms for Address List ID, Single Address ID, or New Address
5. **API Generation**: Complete JSON body with all required and optional parameters

## Total Number of Paths: 27
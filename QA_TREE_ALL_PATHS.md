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

## All Possible Paths and Endpoints

### Path 1: Single Document → Template
- Q1: **single** (Single document)
- Q2: **true** (Use saved template)
- Q3: **explicit** (Provided in API call)
- **Endpoint: submitSingleDocTemplate**

### Path 2: Single Document → Template → From Template
- Q1: **single** (Single document)
- Q2: **true** (Use saved template)
- Q3: **template** (From template/mailing list)
- **Endpoint: submitSingleDocTemplate**

### Path 3: Single Document → Template → Address Capture
- Q1: **single** (Single document)
- Q2: **true** (Use saved template)
- Q3: **addressCapture** (Extract from document)
- **Endpoint: submitSingleDocTemplate**

### Path 4: Single Document → No Template
- Q1: **single** (Single document)
- Q2: **false** (Configure manually)
- Q3: **explicit** (Provided in API call)
- **Endpoint: submitSingleDoc**

### Path 5: Single Document → No Template → From Template
- Q1: **single** (Single document)
- Q2: **false** (Configure manually)
- Q3: **template** (From template/mailing list)
- **Endpoint: submitSingleDoc**

### Path 6: Single Document → No Template → Address Capture
- Q1: **single** (Single document)
- Q2: **false** (Configure manually)
- Q3: **addressCapture** (Extract from document)
- **Endpoint: submitSingleDoc**

### Path 7: Multiple Documents → Template → Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **true** (Use saved template)
- Q3: **explicit** (Provided in API call)
- Q4: **true** (Unique per recipient)
- **Endpoint: submitMultiDocTemplate**

### Path 8: Multiple Documents → Template → Not Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **true** (Use saved template)
- Q3: **explicit** (Provided in API call)
- Q4: **false** (Same for all)
- **Endpoint: submitMultiDocTemplate**

### Path 9: Multiple Documents → Template → From Template → Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **true** (Use saved template)
- Q3: **template** (From template/mailing list)
- Q4: **true** (Unique per recipient)
- **Endpoint: submitMultiDocTemplate**

### Path 10: Multiple Documents → Template → From Template → Not Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **true** (Use saved template)
- Q3: **template** (From template/mailing list)
- Q4: **false** (Same for all)
- **Endpoint: submitMultiDocTemplate**

### Path 11: Multiple Documents → Template → Address Capture → Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **true** (Use saved template)
- Q3: **addressCapture** (Extract from document)
- Q4: **true** (Unique per recipient)
- **Endpoint: submitMultiDocTemplate**

### Path 12: Multiple Documents → Template → Address Capture → Not Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **true** (Use saved template)
- Q3: **addressCapture** (Extract from document)
- Q4: **false** (Same for all)
- **Endpoint: submitMultiDocTemplate**

### Path 13: Multiple Documents → No Template → Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **false** (Configure manually)
- Q3: **explicit** (Provided in API call)
- Q4: **true** (Unique per recipient)
- **Endpoint: submitMultiDoc**

### Path 14: Multiple Documents → No Template → Not Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **false** (Configure manually)
- Q3: **explicit** (Provided in API call)
- Q4: **false** (Same for all)
- **Endpoint: submitMultiDoc**

### Path 15: Multiple Documents → No Template → From Template → Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **false** (Configure manually)
- Q3: **template** (From template/mailing list)
- Q4: **true** (Unique per recipient)
- **Endpoint: submitMultiDoc**

### Path 16: Multiple Documents → No Template → From Template → Not Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **false** (Configure manually)
- Q3: **template** (From template/mailing list)
- Q4: **false** (Same for all)
- **Endpoint: submitMultiDoc**

### Path 17: Multiple Documents → No Template → Address Capture → Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **false** (Configure manually)
- Q3: **addressCapture** (Extract from document)
- Q4: **true** (Unique per recipient)
- **Endpoint: submitMultiDoc**

### Path 18: Multiple Documents → No Template → Address Capture → Not Personalized
- Q1: **multi** (Multiple separate documents)
- Q2: **false** (Configure manually)
- Q3: **addressCapture** (Extract from document)
- Q4: **false** (Same for all)
- **Endpoint: submitMultiDoc**

### Path 19: Merge Documents → Personalized
- Q1: **merge** (Multiple documents to merge)
- Q2: **true/false** (Template choice - doesn't affect merge endpoint)
- Q3: **explicit** (Provided in API call)
- Q4: **true** (Unique per recipient)
- **Endpoint: submitMultiDocMerge**

### Path 20: Merge Documents → Not Personalized
- Q1: **merge** (Multiple documents to merge)
- Q2: **true/false** (Template choice - doesn't affect merge endpoint)
- Q3: **explicit** (Provided in API call)
- Q4: **false** (Same for all)
- **Endpoint: submitMultiDocMerge**

### Path 21: Merge Documents → From Template → Personalized
- Q1: **merge** (Multiple documents to merge)
- Q2: **true/false** (Template choice - doesn't affect merge endpoint)
- Q3: **template** (From template/mailing list)
- Q4: **true** (Unique per recipient)
- **Endpoint: submitMultiDocMerge**

### Path 22: Merge Documents → From Template → Not Personalized
- Q1: **merge** (Multiple documents to merge)
- Q2: **true/false** (Template choice - doesn't affect merge endpoint)
- Q3: **template** (From template/mailing list)
- Q4: **false** (Same for all)
- **Endpoint: submitMultiDocMerge**

### Path 23: Merge Documents → Address Capture → Personalized
- Q1: **merge** (Multiple documents to merge)
- Q2: **true/false** (Template choice - doesn't affect merge endpoint)
- Q3: **addressCapture** (Extract from document)
- Q4: **true** (Unique per recipient)
- **Endpoint: submitMultiDocMerge**

### Path 24: Merge Documents → Address Capture → Not Personalized
- Q1: **merge** (Multiple documents to merge)
- Q2: **true/false** (Template choice - doesn't affect merge endpoint)
- Q3: **addressCapture** (Extract from document)
- Q4: **false** (Same for all)
- **Endpoint: submitMultiDocMerge**

### Path 25: PDF Split → Explicit Addresses
- Q1: **pdfSplit** (Split a combined PDF)
- Q2: (Not shown for pdfSplit)
- Q3: **explicit** (Provided in API call)
- **Endpoint: submitPdfSplit**

### Path 26: PDF Split → From Template
- Q1: **pdfSplit** (Split a combined PDF)
- Q2: (Not shown for pdfSplit)
- Q3: **template** (From template/mailing list)
- **Endpoint: submitPdfSplit**

### Path 27: PDF Split → Address Capture
- Q1: **pdfSplit** (Split a combined PDF)
- Q2: (Not shown for pdfSplit)
- Q3: **addressCapture** (Extract from document)
- **Endpoint: submitPdfSplit**

## Summary of Endpoints

Based on the qa_tree.yaml file, there are **6 unique endpoints**:

1. **submitSingleDocTemplate** - Single document with job template
2. **submitSingleDoc** - Single document without job template
3. **submitMultiDocTemplate** - Multiple documents with job template
4. **submitMultiDoc** - Multiple documents without job template
5. **submitMultiDocMerge** - Merge multiple documents (template question shown but doesn't affect endpoint)
6. **submitPdfSplit** - Split PDF (no template question)

## Key Observations

1. **Q2 (Template Usage)** is only shown for single, multi, and merge document types
2. **Q3 (Recipient Style)** is shown for ALL document types
3. **Q4 (Personalized)** is only shown for multi and merge types
4. For **merge** documents, the template question (Q2) is shown but doesn't affect the endpoint selection
5. **pdfSplit** skips Q2 entirely and goes straight to Q3

## Total Number of Paths: 27
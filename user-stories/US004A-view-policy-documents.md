# US004A: View Policy Document Details and Preview

## User Story

**As a** policy researcher
**I need** to view policy document details and preview content
**So that** I can review documents before downloading and assess their relevance

## Description

Users should be able to view detailed information about policy documents and preview their content directly in the application. The system should support various document formats (PDF, HTML, DOCX) and provide relevant metadata and context about each document.

## Acceptance Criteria

### Scenario 1: View document details

**Given** I have found a policy document in search results
**When** I click on the document title
**Then** I should see a detailed view with:
- Full document title
- Source (DSO, Gemeenteblad, custom source)
- Publication date
- Municipality (if applicable)
- Document type
- Original URL
- Summary or description (if available)
**And** I should see a preview or "View Document" button

### Scenario 2: Preview PDF documents

**Given** I am viewing a PDF policy document
**When** I click "Preview" or "View Document"
**Then** the PDF should open in an embedded viewer within the application
**And** I should be able to navigate through pages
**And** I should be able to zoom in and out
**And** the original formatting should be preserved

### Scenario 3: View HTML documents

**Given** I am viewing an HTML policy document
**When** I click "View Document"
**Then** the HTML content should be displayed in a clean, readable format
**And** links within the document should be functional
**And** images should load properly
**And** styling should be preserved but sanitized for security

### Scenario 4: Handle unavailable documents

**Given** I try to view a document whose source is no longer available
**When** I click "View Document"
**Then** I should see an error message indicating the document is unavailable
**And** I should still see the cached metadata
**And** I should see the last known access date

### Scenario 5: Copy document link

**Given** I am viewing a policy document
**When** I click "Copy Link to Document"
**Then** the original source URL should be copied to my clipboard
**And** I should see a confirmation message
**And** the link should open the original document when pasted in a browser

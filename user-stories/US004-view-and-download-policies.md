# US004: View and Download Policy Documents

## User Story

**As a** policy researcher
**I need** to view and download scanned policy documents
**So that** I can review the full content and save documents for offline analysis

## Description

Users should be able to preview policy documents directly in the application and download them for offline use. The system should support various document formats (PDF, HTML, DOCX) and provide relevant metadata and context about each document.

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

### Scenario 4: Download documents

**Given** I am viewing a policy document
**When** I click the "Download" button
**Then** the document should download to my local machine
**And** the filename should include the document title and source
**And** the original format should be preserved (PDF, HTML, DOCX)

### Scenario 5: Download multiple documents

**Given** I have selected multiple documents from search results
**When** I click "Download Selected"
**Then** all selected documents should be downloaded
**And** they should be packaged in a ZIP file if more than 5 documents
**And** the ZIP should include a manifest file with metadata

### Scenario 6: Copy document link

**Given** I am viewing a policy document
**When** I click "Copy Link to Document"
**Then** the original source URL should be copied to my clipboard
**And** I should see a confirmation message
**And** the link should open the original document when pasted in a browser

### Scenario 7: Handle unavailable documents

**Given** I try to view a document whose source is no longer available
**When** I click "View Document"
**Then** I should see an error message indicating the document is unavailable
**And** I should still see the cached metadata
**And** I should see the last known access date

### Scenario 8: Track document views

**Given** I am logged in as a user
**When** I view or download a document
**Then** the system should record this action
**And** I should be able to see my recently viewed documents
**And** I should be able to access my download history

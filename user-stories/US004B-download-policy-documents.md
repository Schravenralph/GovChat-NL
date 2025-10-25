# US004B: Download Policy Documents

## User Story

**As a** policy researcher
**I need** to download policy documents for offline use
**So that** I can analyze documents without internet access and save them for future reference

## Description

Users should be able to download individual or multiple policy documents to their local machine. The system should preserve original formats and provide convenient batch download capabilities for multiple documents.

## Acceptance Criteria

### Scenario 1: Download a single document

**Given** I am viewing a policy document
**When** I click the "Download" button
**Then** the document should download to my local machine
**And** the filename should include the document title and source
**And** the original format should be preserved (PDF, HTML, DOCX)

### Scenario 2: Download multiple documents

**Given** I have selected multiple documents from search results
**When** I click "Download Selected"
**Then** all selected documents should be downloaded
**And** they should be packaged in a ZIP file if more than 5 documents
**And** the ZIP should include a manifest file with metadata

### Scenario 3: Select documents for batch download

**Given** I am viewing search results
**When** I use checkboxes to select multiple documents
**Then** I should see a counter showing how many documents are selected
**And** I should see a "Download Selected" button
**And** I should be able to select/deselect all documents at once

### Scenario 4: Download large document collections

**Given** I am downloading more than 20 documents
**When** the download is initiated
**Then** I should see a progress indicator
**And** I should be able to cancel the download if needed
**And** completed documents should be available even if I cancel partway through

### Scenario 5: Handle download errors

**Given** a document fails to download due to network issues
**When** the download error occurs
**Then** I should see a clear error message
**And** I should be offered the option to retry the download
**And** successfully downloaded documents should still be available

# US001: Scan Gemeentebladen for Policy Documents

## User Story

**As a** policy researcher
**I need** to scan Gemeentebladen for policy documents
**So that** I can discover and access municipal policies that are not available in the DSO system

## Description

The system should be able to automatically scan and index policy documents from Gemeentebladen (municipal gazettes) across different municipalities. This allows users to find policy documents that may not be related to environmental or spatial planning but are still relevant for policy research.

## Acceptance Criteria

### Scenario 1: Successfully scan a Gemeenteblad source

**Given** the policy scanner is configured with a valid Gemeenteblad URL
**When** I initiate a scan of the Gemeenteblad source
**Then** the system should retrieve all available policy documents
**And** the documents should be indexed with metadata (title, publication date, municipality, document type)
**And** I should see a confirmation message with the number of documents found

### Scenario 2: Handle multiple municipalities

**Given** I have configured multiple Gemeenteblad sources from different municipalities
**When** I run a batch scan across all configured sources
**Then** each municipality's documents should be scanned separately
**And** documents should be tagged with the corresponding municipality name
**And** I should receive a summary report showing results per municipality

### Scenario 3: Handle scan errors gracefully

**Given** one or more Gemeenteblad sources are temporarily unavailable
**When** the scanning process encounters an error
**Then** the system should log the error with details
**And** continue scanning other available sources
**And** notify me of which sources failed and which succeeded

### Scenario 4: Avoid duplicate documents

**Given** a document has already been scanned and indexed previously
**When** a rescan is performed on the same Gemeenteblad source
**Then** the system should detect duplicate documents
**And** only update the document if changes are detected
**And** skip indexing if the document is unchanged

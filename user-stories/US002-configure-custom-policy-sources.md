# US002: Configure Custom Policy Sources

## User Story

**As a** system administrator
**I need** to configure custom website sources for policy scanning
**So that** I can extend the scanner to include additional policy repositories beyond DSO and Gemeentebladen

## Description

The system should allow administrators to add, configure, and manage custom policy sources from various websites. This enables the policy scanner to be flexible and extensible, supporting different types of policy repositories with varying structures and formats.

## Acceptance Criteria

### Scenario 1: Add a new custom policy source

**Given** I am logged in as an administrator
**When** I navigate to the policy sources configuration page
**And** I provide a source name, URL, and source type
**And** I submit the new source configuration
**Then** the new source should be added to the list of active sources
**And** I should see a confirmation message
**And** the source should be available for scanning

### Scenario 2: Configure source-specific settings

**Given** I am adding a new custom policy source
**When** I configure the source settings
**Then** I should be able to specify:
- Document selector patterns (CSS selectors or XPath)
- Metadata extraction rules (title, date, category)
- Scan frequency (daily, weekly, monthly)
- Document type filters (PDF, HTML, DOCX)
**And** the system should validate the configuration before saving

### Scenario 3: Test a policy source configuration

**Given** I have configured a new custom policy source
**When** I click the "Test Configuration" button
**Then** the system should attempt to scan the source
**And** return a preview of found documents (max 10)
**And** display any configuration errors or warnings
**And** show the extracted metadata for validation

### Scenario 4: Deactivate a policy source

**Given** I have an active policy source that is no longer relevant
**When** I deactivate the source from the configuration page
**Then** the source should remain in the system but marked as inactive
**And** it should be excluded from future scans
**And** existing indexed documents from that source should remain accessible

### Scenario 5: Validate URL accessibility

**Given** I am configuring a new policy source with a URL
**When** I submit the configuration
**Then** the system should verify the URL is accessible
**And** return an error if the URL returns 404 or connection timeout
**And** warn me if the URL requires authentication

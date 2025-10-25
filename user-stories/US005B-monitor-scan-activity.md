# US005B: Monitor Active Scans and History

## User Story

**As a** system administrator
**I need** to monitor active scans and view scan history
**So that** I can track scanning progress and troubleshoot issues when they occur

## Description

Administrators should be able to view real-time status of active scans and access historical scan data. This enables proactive monitoring and helps identify patterns or recurring issues with specific sources.

## Acceptance Criteria

### Scenario 1: View active scan jobs

**Given** I am on the scan management dashboard
**When** I view the list of active scans
**Then** I should see all currently running scans with:
- Source name
- Start time
- Progress percentage (if available)
- Number of documents processed
- Estimated time remaining
**And** I should be able to cancel a running scan if needed

### Scenario 2: View scan history

**Given** I want to review past scanning activity
**When** I access the scan history page
**Then** I should see a list of completed scans with:
- Source name
- Start and end time
- Status (success, partial success, failed)
- Number of documents found
- Number of new documents added
- Number of updated documents
- Any errors or warnings
**And** I should be able to filter by source, date range, and status

### Scenario 3: View detailed scan logs

**Given** I want to investigate a specific scan
**When** I click on a scan entry in the history
**Then** I should see detailed logs for that scan
**And** logs should include timestamps for each major action
**And** any errors should be highlighted with details
**And** I should be able to export the logs

### Scenario 4: Monitor scan performance metrics

**Given** I want to understand scanning efficiency
**When** I view scan performance metrics
**Then** I should see:
- Average scan duration per source
- Documents scanned per hour
- Success rate percentage
- Most common errors
**And** I should be able to view metrics for a specific time period
**And** I should be able to compare performance across different sources

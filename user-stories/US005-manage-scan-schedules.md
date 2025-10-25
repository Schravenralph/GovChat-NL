# US005: Manage Policy Scan Schedules

## User Story

**As a** system administrator
**I need** to manage and monitor automated policy scanning schedules
**So that** the system stays up-to-date with the latest policy documents without manual intervention

## Description

The system should support automated, scheduled scanning of all configured policy sources. Administrators should be able to configure scan frequencies, monitor scan status, and view scan history to ensure the policy database remains current.

## Acceptance Criteria

### Scenario 1: Configure scan schedule for a source

**Given** I am managing a policy source
**When** I configure the scan schedule settings
**Then** I should be able to set:
- Scan frequency (hourly, daily, weekly, monthly)
- Specific time of day for scans
- Days of the week (for weekly scans)
- Date of month (for monthly scans)
**And** the schedule should be validated before saving
**And** I should see the next scheduled scan time

### Scenario 2: View active scan jobs

**Given** I am on the scan management dashboard
**When** I view the list of active scans
**Then** I should see all currently running scans with:
- Source name
- Start time
- Progress percentage (if available)
- Number of documents processed
- Estimated time remaining
**And** I should be able to cancel a running scan if needed

### Scenario 3: View scan history

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

### Scenario 4: Handle scan failures

**Given** a scheduled scan has failed
**When** I check the scan status
**Then** I should see a clear error message explaining the failure
**And** the system should automatically retry failed scans (up to 3 attempts)
**And** I should receive a notification if all retry attempts fail
**And** I should be able to manually trigger a rescan

### Scenario 5: Pause and resume scanning

**Given** I need to perform system maintenance
**When** I pause all scanning activities
**Then** all active scans should complete their current document
**And** no new scans should start
**And** scheduled scans should be queued for later
**And** I should be able to resume scanning when ready

### Scenario 6: Monitor scan performance

**Given** I want to optimize scanning efficiency
**When** I view scan performance metrics
**Then** I should see:
- Average scan duration per source
- Documents scanned per hour
- Success rate percentage
- Most common errors
- Resource usage (CPU, memory, network)
**And** I should be able to export metrics as CSV or JSON

### Scenario 7: Configure scan priorities

**Given** I have multiple policy sources configured
**When** I set scan priorities for different sources
**Then** high-priority sources should be scanned first
**And** I should be able to assign priority levels (high, medium, low)
**And** priority should affect queue ordering when multiple scans are scheduled

### Scenario 8: Receive scan notifications

**Given** I have configured notification preferences
**When** a scan completes or fails
**Then** I should receive a notification via:
- Email
- In-app notification
- Webhook (optional)
**And** I should be able to configure which events trigger notifications
**And** I should be able to customize notification recipients

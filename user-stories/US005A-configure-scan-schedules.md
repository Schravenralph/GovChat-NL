# US005A: Configure and Execute Scan Schedules

## User Story

**As a** system administrator
**I need** to configure automated scan schedules for policy sources
**So that** policy documents are automatically updated without manual intervention

## Description

The system should allow administrators to set up automated scanning schedules for each policy source. Administrators should be able to define when and how often scans occur, and manually trigger scans when needed.

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

### Scenario 2: Manually trigger a scan

**Given** I want to immediately update a policy source
**When** I click "Run Scan Now" for a specific source
**Then** the scan should start immediately
**And** I should see a confirmation that the scan has started
**And** the scan should not interfere with the regular schedule

### Scenario 3: Pause and resume scanning

**Given** I need to perform system maintenance
**When** I pause all scanning activities
**Then** all active scans should complete their current document
**And** no new scans should start
**And** scheduled scans should be queued for later
**And** I should be able to resume scanning when ready

### Scenario 4: Configure scan priorities

**Given** I have multiple policy sources configured
**When** I set scan priorities for different sources
**Then** high-priority sources should be scanned first
**And** I should be able to assign priority levels (high, medium, low)
**And** priority should affect queue ordering when multiple scans are scheduled

### Scenario 5: Edit existing scan schedules

**Given** I have an existing scan schedule
**When** I modify the schedule settings
**Then** the changes should be saved immediately
**And** the next scheduled scan time should be recalculated
**And** I should see a confirmation of the updated schedule

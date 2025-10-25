# US003B: Filter Policy Search Results

## User Story

**As a** policy researcher
**I need** to filter search results by various criteria
**So that** I can narrow down results to find the most relevant policy documents

## Description

Users should be able to apply multiple filters to search results to refine their query. Filters should include source, date range, municipality, and document type, and should be combinable to create precise search criteria.

## Acceptance Criteria

### Scenario 1: Filter by policy source

**Given** I have performed a search that returns documents from multiple sources
**When** I apply a filter to show only documents from "Gemeentebladen"
**Then** the results should update to show only Gemeenteblad documents
**And** I should see the number of results for each available source
**And** I should be able to select multiple sources simultaneously

### Scenario 2: Filter by date range

**Given** I am viewing search results
**When** I set a date range filter (e.g., "Last 6 months" or custom dates)
**Then** only documents published within that date range should be displayed
**And** the result count should update accordingly
**And** I should be able to clear the date filter to see all results again

### Scenario 3: Filter by municipality

**Given** I am searching for policy documents
**When** I apply a municipality filter (e.g., "Amsterdam", "Rotterdam")
**Then** only documents from the selected municipality should be shown
**And** I should see a list of all available municipalities with document counts
**And** I should be able to select multiple municipalities

### Scenario 4: Filter by document type

**Given** I have search results containing different document types (PDF, HTML, DOCX)
**When** I apply a document type filter
**Then** only documents of the selected type should be displayed
**And** the filter should show the count of documents for each type
**And** I should be able to combine this with other filters

### Scenario 5: Combine multiple filters

**Given** I have applied a source filter
**When** I add a date range filter and a municipality filter
**Then** the results should show only documents matching ALL filter criteria
**And** I should see the total number of active filters
**And** I should be able to remove individual filters without clearing all

### Scenario 6: Clear all filters

**Given** I have multiple filters applied
**When** I click "Clear All Filters"
**Then** all filters should be removed
**And** the search should show all results again
**And** I should see a confirmation that filters were cleared

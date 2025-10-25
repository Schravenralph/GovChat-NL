# US003: Search and Filter Scanned Policies

## User Story

**As a** policy researcher
**I need** to search and filter scanned policies by various criteria
**So that** I can quickly find relevant policy documents from multiple sources

## Description

Users should be able to search through all indexed policy documents using keywords and apply filters to narrow down results. The search should work across documents from DSO, Gemeentebladen, and custom policy sources, providing a unified search experience.

## Acceptance Criteria

### Scenario 1: Perform basic keyword search

**Given** the system has indexed policy documents from multiple sources
**When** I enter a search term in the search box
**And** I click the search button
**Then** I should see a list of documents containing that keyword
**And** the results should show document title, source, publication date, and a snippet
**And** the search term should be highlighted in the snippets

### Scenario 2: Filter by policy source

**Given** I have performed a search that returns documents from multiple sources
**When** I apply a filter to show only documents from "Gemeentebladen"
**Then** the results should update to show only Gemeenteblad documents
**And** I should see the number of results for each available source
**And** I should be able to select multiple sources simultaneously

### Scenario 3: Filter by date range

**Given** I am viewing search results
**When** I set a date range filter (e.g., "Last 6 months" or custom dates)
**Then** only documents published within that date range should be displayed
**And** the result count should update accordingly
**And** I should be able to clear the date filter to see all results again

### Scenario 4: Filter by municipality

**Given** I am searching for policy documents
**When** I apply a municipality filter (e.g., "Amsterdam", "Rotterdam")
**Then** only documents from the selected municipality should be shown
**And** I should see a list of all available municipalities with document counts
**And** I should be able to select multiple municipalities

### Scenario 5: Filter by document type

**Given** I have search results containing different document types (PDF, HTML, DOCX)
**When** I apply a document type filter
**Then** only documents of the selected type should be displayed
**And** the filter should show the count of documents for each type
**And** I should be able to combine this with other filters

### Scenario 6: Sort search results

**Given** I have search results displayed
**When** I select a sort option (relevance, date newest first, date oldest first, alphabetical)
**Then** the results should reorder according to the selected sort method
**And** the sort selection should persist when applying filters

### Scenario 7: Handle no results

**Given** I perform a search
**When** no documents match my search criteria
**Then** I should see a "No results found" message
**And** I should see suggestions to broaden my search (remove filters, try different keywords)
**And** I should still be able to modify my search and filters

### Scenario 8: Save search filters

**Given** I have applied multiple filters to my search
**When** I click "Save Search"
**Then** I should be able to name and save this filter combination
**And** access it later from a "Saved Searches" menu
**And** receive notifications when new documents match my saved search

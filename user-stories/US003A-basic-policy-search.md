# US003A: Basic Policy Search

## User Story

**As a** policy researcher
**I need** to perform basic keyword searches across scanned policies
**So that** I can quickly find documents containing specific terms

## Description

Users should be able to search through all indexed policy documents using keywords. The search should work across documents from DSO, Gemeentebladen, and custom policy sources, providing a unified search experience with highlighted results.

## Acceptance Criteria

### Scenario 1: Perform basic keyword search

**Given** the system has indexed policy documents from multiple sources
**When** I enter a search term in the search box
**And** I click the search button
**Then** I should see a list of documents containing that keyword
**And** the results should show document title, source, publication date, and a snippet
**And** the search term should be highlighted in the snippets

### Scenario 2: Handle no results

**Given** I perform a search
**When** no documents match my search criteria
**Then** I should see a "No results found" message
**And** I should see suggestions to broaden my search (try different keywords)
**And** I should still be able to modify my search

### Scenario 3: Sort search results

**Given** I have search results displayed
**When** I select a sort option (relevance, date newest first, date oldest first, alphabetical)
**Then** the results should reorder according to the selected sort method
**And** the sort selection should persist when I navigate

### Scenario 4: View result count

**Given** I have performed a search
**When** the results are displayed
**Then** I should see the total number of matching documents
**And** the count should be clearly visible at the top of the results

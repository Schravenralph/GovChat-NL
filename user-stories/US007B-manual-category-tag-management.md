# US007B: Manual Category and Tag Management

## User Story

**As a** policy researcher
**I need** to manually add, edit, and remove categories and tags
**So that** I can correct automatic assignments and add domain-specific classifications

## Description

Users should be able to manually manage categories and tags for policy documents. This allows for corrections to automatic assignments and enables users to add specialized classifications that may not be captured automatically.

## Acceptance Criteria

### Scenario 1: Manual tag management

**Given** I am viewing a policy document
**When** I want to add or modify tags
**Then** I should be able to add custom tags manually
**And** I should be able to remove auto-generated tags
**And** the system should suggest tags based on similar documents
**And** tags should be saved and immediately searchable

### Scenario 2: Edit document categories

**Given** I am viewing a document's categorization
**When** I want to change the assigned categories
**Then** I should be able to add or remove categories
**And** I should be able to change the primary category designation
**And** changes should be tracked with timestamp and user ID
**And** I should see a confirmation when changes are saved

### Scenario 3: Bulk edit categories and tags

**Given** I have selected multiple documents
**When** I want to apply categories or tags to all of them
**Then** I should be able to add categories/tags to all selected documents
**And** I should be able to remove categories/tags from all selected documents
**And** I should see a summary of how many documents will be affected
**And** I should be able to confirm or cancel the bulk operation

### Scenario 4: Tag suggestions based on content

**Given** I am adding tags to a document
**When** I start typing a tag
**Then** the system should suggest existing tags that match
**And** show how many other documents use each suggested tag
**And** allow me to create a new tag if none match
**And** warn me if the new tag is very similar to an existing one

### Scenario 5: View tag and category usage statistics

**Given** I want to understand which tags and categories are most common
**When** I access the tag/category statistics page
**Then** I should see a list of all tags with usage counts
**And** I should see all categories with document counts
**And** I should be able to merge similar or duplicate tags
**And** I should be able to delete unused tags

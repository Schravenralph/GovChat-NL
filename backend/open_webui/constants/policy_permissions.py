"""
Policy Scanner Permission Constants

Defines all permissions for the Policy Scanner module.
"""

class PolicyPermissions:
    """Policy Scanner permission constants"""

    # User permissions (all authenticated users)
    SEARCH = "policy:search"           # Can search documents
    VIEW = "policy:view"               # Can view document details
    DOWNLOAD = "policy:download"       # Can download documents
    SAVE_SEARCH = "policy:save_search" # Can save searches
    FAVORITE = "policy:favorite"       # Can favorite documents

    # Admin permissions
    ADMIN = "policy:admin"             # Full admin access
    MANAGE_SOURCES = "policy:manage_sources"  # Can manage sources
    TRIGGER_SCAN = "policy:trigger_scan"      # Can trigger scans
    CATEGORIZE = "policy:categorize"   # Can categorize documents
    DELETE = "policy:delete"           # Can delete documents

    # Permission groups
    USER_PERMISSIONS = [
        SEARCH, VIEW, DOWNLOAD, SAVE_SEARCH, FAVORITE
    ]

    ADMIN_PERMISSIONS = [
        ADMIN, MANAGE_SOURCES, TRIGGER_SCAN, CATEGORIZE, DELETE
    ]

    ALL_PERMISSIONS = USER_PERMISSIONS + ADMIN_PERMISSIONS

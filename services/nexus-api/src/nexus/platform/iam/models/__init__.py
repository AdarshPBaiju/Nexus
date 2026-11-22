"""
nexus.platform.iam.models - Identity, Workspace, and OAuth models barrel.
"""

from nexus.platform.iam.models.favourite import UserFavourite
from nexus.platform.iam.models.oauth_client import OAuthClientApp
from nexus.platform.iam.models.oauth_grant import OAuthConsentGrant
from nexus.platform.iam.models.staff_profile import StaffProfile
from nexus.platform.iam.models.staff_role_assignment import StaffRoleAssignment
from nexus.platform.iam.models.user import User
from nexus.platform.iam.models.workspace_membership import UserWorkspaceMembership

__all__ = [
    "OAuthClientApp",
    "OAuthConsentGrant",
    "StaffProfile",
    "StaffRoleAssignment",
    "User",
    "UserFavourite",
    "UserWorkspaceMembership",
]

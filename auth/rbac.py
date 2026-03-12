from fastapi import Depends, HTTPException, status

from auth.jwt import get_current_user

ROLE_PERMISSIONS = {
    "super_admin": ["read", "write", "delete", "manage_users", "view_analytics"],
    "district_officer": ["read", "write", "view_analytics"],
    "field_agent": ["read", "write_distribution"],
    "auditor": ["read", "view_analytics"],
}


def require_permission(permission: str):
    def dependency(current_user=Depends(get_current_user)):
        role = current_user.role.value if hasattr(current_user.role, "value") else current_user.role
        allowed = ROLE_PERMISSIONS.get(role, [])
        if permission not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: insufficient permissions"
            )
        return current_user
    return dependency

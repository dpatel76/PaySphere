"""
GPS CDM - Auth Dependencies
FastAPI dependencies for authentication and authorization
"""

from typing import List, Optional
from functools import wraps

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .security import decode_token, TokenData
from .models import User

# OAuth2 scheme for token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_db_connection():
    """Get database connection."""
    import psycopg2
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="gps_cdm",
    )


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[User]:
    """
    Get the current user from the JWT token.

    Returns None if no token or invalid token (for optional auth).
    Raises HTTPException for invalid tokens when token is provided.
    """
    if token is None:
        return None

    token_data = decode_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if token_data.token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch full user data from database
    db = get_db_connection()
    try:
        cursor = db.cursor()
        cursor.execute("""
            SELECT u.user_id, u.email, u.username, u.first_name, u.last_name,
                   u.is_active, u.is_superuser, u.last_login, u.created_at
            FROM auth.users u
            WHERE u.user_id = %s::uuid
        """, (token_data.user_id,))

        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user roles
        cursor.execute("""
            SELECT r.name
            FROM auth.user_roles ur
            JOIN auth.roles r ON ur.role_id = r.role_id
            WHERE ur.user_id = %s::uuid
        """, (token_data.user_id,))
        roles = [r[0] for r in cursor.fetchall()]

        # Get user permissions
        cursor.execute("""
            SELECT permission_name FROM auth.get_user_permissions(%s::uuid)
        """, (token_data.user_id,))
        permissions = [p[0] for p in cursor.fetchall()]

        return User(
            user_id=str(row[0]),
            email=row[1],
            username=row[2],
            first_name=row[3],
            last_name=row[4],
            is_active=row[5],
            is_superuser=row[6],
            last_login=row[7],
            created_at=row[8],
            roles=[],  # Simplified - just names in permissions
            permissions=permissions,
        )
    finally:
        db.close()


async def get_current_active_user(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """
    Get the current active user. Raises exception if not authenticated or inactive.
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    return current_user


def require_permission(permission: str):
    """
    Dependency that requires a specific permission.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_permission("admin:write"))])
    """
    async def permission_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.is_superuser:
            return current_user

        if permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission} required",
            )
        return current_user

    return permission_checker


def require_any_permission(permissions: List[str]):
    """
    Dependency that requires any of the specified permissions.

    Usage:
        @router.get("/data", dependencies=[Depends(require_any_permission(["data:read", "admin:read"]))])
    """
    async def permission_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.is_superuser:
            return current_user

        if not any(p in current_user.permissions for p in permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: one of {permissions} required",
            )
        return current_user

    return permission_checker


def require_roles(roles: List[str]):
    """
    Dependency that requires one of the specified roles.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_roles(["admin", "operator"]))])
    """
    async def role_checker(
        token: str = Depends(oauth2_scheme)
    ) -> TokenData:
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_data = decode_token(token)
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if token_data.is_superuser:
            return token_data

        if not any(r in token_data.roles for r in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role denied: one of {roles} required",
            )
        return token_data

    return role_checker


# Convenience dependencies for common permission patterns
RequireAdmin = Depends(require_any_permission(["users:admin", "pipeline:admin"]))
RequireOperator = Depends(require_any_permission(["pipeline:write", "exceptions:write"]))
RequireAnalyst = Depends(require_any_permission(["pipeline:read", "dq:read"]))
RequireViewer = Depends(require_permission("pipeline:read"))

"""
GPS CDM API - Authentication Routes
"""

from typing import List
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from gps_cdm.api.auth.security import (
    verify_password,
    get_password_hash,
    create_token_pair,
    decode_token,
)
from gps_cdm.api.auth.models import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserCreate,
    UserResponse,
    UserUpdate,
    UserPasswordUpdate,
)
from gps_cdm.api.auth.dependencies import (
    get_current_active_user,
    require_permission,
)

router = APIRouter()


def get_db_connection():
    """Get database connection."""
    import psycopg2
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="gps_cdm",
    )


def get_user_with_permissions(cursor, user_id: str) -> dict:
    """Fetch user with roles and permissions."""
    cursor.execute("""
        SELECT u.user_id, u.email, u.username, u.first_name, u.last_name,
               u.is_active, u.is_superuser
        FROM auth.users u
        WHERE u.user_id = %s::uuid
    """, (user_id,))
    row = cursor.fetchone()
    if not row:
        return None

    # Get roles
    cursor.execute("""
        SELECT r.name FROM auth.user_roles ur
        JOIN auth.roles r ON ur.role_id = r.role_id
        WHERE ur.user_id = %s::uuid
    """, (user_id,))
    roles = [r[0] for r in cursor.fetchall()]

    # Get permissions
    cursor.execute("""
        SELECT permission_name FROM auth.get_user_permissions(%s::uuid)
    """, (user_id,))
    permissions = [p[0] for p in cursor.fetchall()]

    return {
        "user_id": str(row[0]),
        "email": row[1],
        "username": row[2],
        "first_name": row[3],
        "last_name": row[4],
        "is_active": row[5],
        "is_superuser": row[6],
        "roles": roles,
        "permissions": permissions,
    }


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login with username and password.

    Returns access and refresh tokens.
    """
    db = get_db_connection()
    try:
        cursor = db.cursor()

        # Find user by username or email
        cursor.execute("""
            SELECT user_id, username, email, password_hash, is_active, is_superuser
            FROM auth.users
            WHERE username = %s OR email = %s
        """, (form_data.username, form_data.username))

        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id, username, email, password_hash, is_active, is_superuser = row

        if not is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled",
            )

        if not verify_password(form_data.password, password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user permissions
        user_data = get_user_with_permissions(cursor, str(user_id))

        # Update last login
        cursor.execute("""
            UPDATE auth.users SET last_login = %s WHERE user_id = %s
        """, (datetime.now(timezone.utc), user_id))
        db.commit()

        # Create tokens
        token_data = {
            "sub": str(user_id),
            "username": username,
            "email": email,
            "is_superuser": is_superuser,
            "roles": user_data["roles"],
            "permissions": user_data["permissions"],
        }

        tokens = create_token_pair(token_data)
        return TokenResponse(**tokens)

    finally:
        db.close()


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    """
    token_data = decode_token(request.refresh_token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if token_data.token_type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    db = get_db_connection()
    try:
        cursor = db.cursor()
        user_data = get_user_with_permissions(cursor, token_data.user_id)

        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        if not user_data["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled",
            )

        token_payload = {
            "sub": user_data["user_id"],
            "username": user_data["username"],
            "email": user_data["email"],
            "is_superuser": user_data["is_superuser"],
            "roles": user_data["roles"],
            "permissions": user_data["permissions"],
        }

        tokens = create_token_pair(token_payload)
        return TokenResponse(**tokens)

    finally:
        db.close()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_active_user)
):
    """Get current authenticated user's information."""
    db = get_db_connection()
    try:
        cursor = db.cursor()
        user_data = get_user_with_permissions(cursor, current_user.user_id)
        return UserResponse(**user_data)
    finally:
        db.close()


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    updates: UserUpdate,
    current_user = Depends(get_current_active_user)
):
    """Update current user's profile."""
    db = get_db_connection()
    try:
        cursor = db.cursor()

        update_fields = []
        params = []

        if updates.email is not None:
            update_fields.append("email = %s")
            params.append(updates.email)
        if updates.first_name is not None:
            update_fields.append("first_name = %s")
            params.append(updates.first_name)
        if updates.last_name is not None:
            update_fields.append("last_name = %s")
            params.append(updates.last_name)

        if update_fields:
            update_fields.append("updated_at = %s")
            params.append(datetime.now(timezone.utc))
            params.append(current_user.user_id)

            cursor.execute(f"""
                UPDATE auth.users
                SET {', '.join(update_fields)}
                WHERE user_id = %s::uuid
            """, params)
            db.commit()

        user_data = get_user_with_permissions(cursor, current_user.user_id)
        return UserResponse(**user_data)

    finally:
        db.close()


@router.post("/me/password")
async def change_password(
    password_update: UserPasswordUpdate,
    current_user = Depends(get_current_active_user)
):
    """Change current user's password."""
    db = get_db_connection()
    try:
        cursor = db.cursor()

        # Verify current password
        cursor.execute("""
            SELECT password_hash FROM auth.users WHERE user_id = %s::uuid
        """, (current_user.user_id,))
        row = cursor.fetchone()

        if not verify_password(password_update.current_password, row[0]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        # Update password
        new_hash = get_password_hash(password_update.new_password)
        cursor.execute("""
            UPDATE auth.users
            SET password_hash = %s, updated_at = %s
            WHERE user_id = %s::uuid
        """, (new_hash, datetime.now(timezone.utc), current_user.user_id))
        db.commit()

        return {"message": "Password updated successfully"}

    finally:
        db.close()


# ============================================================================
# User Management (Admin endpoints)
# ============================================================================

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user = Depends(require_permission("users:read"))
):
    """List all users (admin only)."""
    db = get_db_connection()
    try:
        cursor = db.cursor()
        cursor.execute("""
            SELECT user_id FROM auth.users ORDER BY created_at DESC
        """)
        users = []
        for row in cursor.fetchall():
            user_data = get_user_with_permissions(cursor, str(row[0]))
            if user_data:
                users.append(UserResponse(**user_data))
        return users
    finally:
        db.close()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    current_user = Depends(require_permission("users:write"))
):
    """Create a new user (admin only)."""
    db = get_db_connection()
    try:
        cursor = db.cursor()

        # Check if username or email already exists
        cursor.execute("""
            SELECT 1 FROM auth.users WHERE username = %s OR email = %s
        """, (user.username, user.email))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists",
            )

        # Create user
        password_hash = get_password_hash(user.password)
        cursor.execute("""
            INSERT INTO auth.users (email, username, password_hash, first_name, last_name)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING user_id
        """, (user.email, user.username, password_hash, user.first_name, user.last_name))

        user_id = str(cursor.fetchone()[0])

        # Assign roles
        for role_id in user.role_ids:
            cursor.execute("""
                INSERT INTO auth.user_roles (user_id, role_id, assigned_by)
                VALUES (%s::uuid, %s::uuid, %s::uuid)
                ON CONFLICT DO NOTHING
            """, (user_id, role_id, current_user.user_id))

        db.commit()

        user_data = get_user_with_permissions(cursor, user_id)
        return UserResponse(**user_data)

    finally:
        db.close()


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user = Depends(require_permission("users:read"))
):
    """Get a specific user (admin only)."""
    db = get_db_connection()
    try:
        cursor = db.cursor()
        user_data = get_user_with_permissions(cursor, user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse(**user_data)
    finally:
        db.close()


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user = Depends(require_permission("users:admin"))
):
    """Delete a user (admin only)."""
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    db = get_db_connection()
    try:
        cursor = db.cursor()
        cursor.execute("""
            DELETE FROM auth.users WHERE user_id = %s::uuid
        """, (user_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        db.commit()
    finally:
        db.close()


# ============================================================================
# Roles and Permissions
# ============================================================================

@router.get("/roles")
async def list_roles(current_user = Depends(get_current_active_user)):
    """List all roles."""
    db = get_db_connection()
    try:
        cursor = db.cursor()
        cursor.execute("""
            SELECT role_id, name, description, is_system_role
            FROM auth.roles
            ORDER BY name
        """)
        return [
            {
                "role_id": str(row[0]),
                "name": row[1],
                "description": row[2],
                "is_system_role": row[3],
            }
            for row in cursor.fetchall()
        ]
    finally:
        db.close()


@router.get("/permissions")
async def list_permissions(current_user = Depends(get_current_active_user)):
    """List all permissions."""
    db = get_db_connection()
    try:
        cursor = db.cursor()
        cursor.execute("""
            SELECT permission_id, name, description, resource, action
            FROM auth.permissions
            ORDER BY resource, action
        """)
        return [
            {
                "permission_id": str(row[0]),
                "name": row[1],
                "description": row[2],
                "resource": row[3],
                "action": row[4],
            }
            for row in cursor.fetchall()
        ]
    finally:
        db.close()

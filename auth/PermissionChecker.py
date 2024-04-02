from fastapi import Depends, HTTPException
from functions import token_in_header
from models import Role


class PermissionChecker:
    def __init__(self, permissions_required: list):
        self.permissions_required = permissions_required

    def __call__(self, user:dict = Depends(token_in_header)):
        for permission_required in self.permissions_required:
            print(Role.get_role_permissions(user['role']))
            if permission_required not in Role.get_role_permissions(user['role']):
                raise HTTPException(
                    status_code=403,
                    detail="Not enough permissions to access this resource")
        return user

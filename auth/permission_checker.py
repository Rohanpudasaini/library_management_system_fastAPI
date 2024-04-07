from fastapi import Depends, HTTPException
from utils.helper_function import token_in_header
from models import Role

# from fastapi.security import OAuth2PasswordBearer
# token_in_header = OAuth2PasswordBearer(tokenUrl="/login")

class PermissionChecker:
    def __init__(self, permissions_required: list):
        self.permissions_required = permissions_required

    def __call__(self, user:dict = Depends(token_in_header)):
        for permission_required in self.permissions_required:
            print(permission_required)
            # print(Role.get_role_permissions(user['role']))
            is_permitted = Role.role_got_permission(permission_required,user['role'])
            # if permission_required not in Role.get_role_permissions(user['role']):
            if not is_permitted:
                raise HTTPException(
                    status_code=403,
                    detail="Not enough permissions to access this resource")
        return user

class ContainPermission:
    def __init__(self, permissions_required: list):
        self.permissions_required = permissions_required

    def __call__(self, user:dict = Depends(token_in_header)):
        for permission_required in self.permissions_required:
            print(permission_required)
            # print(Role.get_role_permissions(user['role']))
            is_permitted = Role.role_got_permission(permission_required,user['role'])            
            # if permission_required not in Role.get_role_permissions(user['role']):
            if not is_permitted:
                # raise HTTPException(
                #     status_code=403,
                #     detail="Not enough permissions to access this resource")
                return False
        return True
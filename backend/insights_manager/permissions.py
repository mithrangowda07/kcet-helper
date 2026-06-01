from rest_framework.permissions import BasePermission

from insights_manager.models import AdminAccount


class IsAdminAccount(BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, AdminAccount) and request.user.is_active

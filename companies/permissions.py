from rest_framework.permissions import BasePermission


class IsCompanyOwner(BasePermission):
    message = "Only the owner of this company can modify it."

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.owner_id == request.user.pk


class IsCompanyOwnerOrAdmin(BasePermission):
    message = "Only the company owner or an admin can delete this company."

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        return obj.owner_id == request.user.pk or request.user.role == "ADMIN"

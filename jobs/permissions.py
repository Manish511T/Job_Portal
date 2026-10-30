from rest_framework.permissions import BasePermission


class IsJobOwner(BasePermission):
    message = "You can only modify your own jobs."

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.company.owner_id == request.user.id


class IsJobOwnerOrAdmin(BasePermission):
    message = "Only the job owner or an admin can delete this job."

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        return (
            obj.company.owner_id == request.user.id
            or request.user.role == "ADMIN"
        )
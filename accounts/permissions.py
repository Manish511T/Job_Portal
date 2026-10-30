from rest_framework.permissions import BasePermission

from accounts.models import User


class IsCandidate(BasePermission):
    message = "Only candidates can access this resource."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "CANDIDATE"

class IsEmployer(BasePermission):
    message = "Only employers can access this resource."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == User.Role.EMPLOYER
        )

class IsAdminRole(BasePermission):
    message = "Only users with the ADMIN role can access this resource."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "ADMIN"

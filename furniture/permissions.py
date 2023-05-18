from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsCommentAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return request.user.is_staff or obj.user == request.user
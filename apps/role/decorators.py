from django.http import HttpResponseForbidden


def role_required(required_role):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.userprofile.role.name == required_role:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden(
                    "You don't have permission to view this page."
                )

        return _wrapped_view

    return decorator

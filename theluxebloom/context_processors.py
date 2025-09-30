def staff_or_superuser(request):
    return {
        "is_admin": request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
    }
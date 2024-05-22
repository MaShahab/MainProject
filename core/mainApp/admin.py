from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from mainApp.models import User, Profile

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'is_superuser', 'is_active', 'is_verified')
    list_filter = ('email', 'is_superuser', 'is_active', 'is_verified')
    search_fields = ('email',)
    ordering = ('email',)
    readonly_fields = ["date_joined"]
    fieldsets = (
        ('Authentication', {
            "fields": (
                'email', 'password'
            ),
        }),
        ('Permissions', {
            "fields": (
                'is_staff', 'is_active', 'is_superuser', 'is_verified'
            ),
        }),
        ('group permissions', {
            "fields": (
                'groups', 'user_permissions',
            ),
        }),
        ('dates', {
            "fields": (
                'last_login',
            ),
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions", "is_verified"
            )}
         ),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile)
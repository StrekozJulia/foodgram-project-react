from django.contrib import admin
from .models import CustomUser, Follow


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', ]
    list_filter = ['email', 'username', ]


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Follow)

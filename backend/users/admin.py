from django.contrib import admin

from .models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'email', 'first_name')
    search_fields = ('username', 'email', )
    empty_value_display = '-no-data-'


admin.site.register(CustomUser, CustomUserAdmin)

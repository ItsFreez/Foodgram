from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from users.models import Follow, User

admin.site.empty_value_display = 'Не задано'


class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = ('username', 'email',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')
    list_filter = ('following',)


admin.site.unregister(Group)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Follow, FollowAdmin)

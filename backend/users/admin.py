from django.contrib import admin

from users.models import Follow, User

admin.site.empty_value_display = 'Не задано'


class UserAdmin(admin.ModelAdmin):
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


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)

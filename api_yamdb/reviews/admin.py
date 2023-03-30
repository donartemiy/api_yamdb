from django.contrib import admin

from reviews.models import Category, Genre, Review, Title, User


@admin.register(User)
class UsersAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'role',
        'bio',
        'first_name',
        'last_name',
    )
    search_fields = ('username', 'role',)
    list_filter = ('username',)
    empty_value_display = '-пусто-'


admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Title)
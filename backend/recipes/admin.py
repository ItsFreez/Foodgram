from django.contrib import admin

from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredientsRelated, Tag, ShoppingCart)


admin.site.empty_value_display = 'Не задано'


class IngredientInline(admin.TabularInline):
    model = RecipeIngredientsRelated


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    search_fields = ('name', 'slug',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'pub_date', 'count_in_favorites')
    readonly_fields = ('count_in_favorites',)
    search_fields = ('name',)
    list_filter = ('tags', 'author',)
    filter_horizontal = ('tags',)
    inlines = (IngredientInline,)

    @admin.display(description='Количество добавлений в избранное')
    def count_in_favorites(self, obj):
        return obj.favorites.count()


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    list_filter = ('recipe',)
    search_fields = ('user',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    list_filter = ('recipe',)
    search_fields = ('user',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)

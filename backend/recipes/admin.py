from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Subscription, Tag, TagRecipe, Unit)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags',)
    fields = (
        'name',
        'text',
        'author',
        'image',
        'cooking_time',
        'count_favorite',
    )
    readonly_fields = ('count_favorite',)

    def count_favorite(self, obj):
        return obj.choosing.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    empty_value_display = '-no-data-'


admin.site.register(Favorite)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientRecipe)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart)
admin.site.register(Subscription)
admin.site.register(Tag)
admin.site.register(TagRecipe)
admin.site.register(Unit)

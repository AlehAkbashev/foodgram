from typing import Any

from django.contrib import admin
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import HttpRequest

from .models import (Ingredient, IngredientRecipe, IsFavorited,
                     IsInShoppingCart, Recipe, Subscription, Tag)


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "color", "slug")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )

    list_filter = ("name",)

    search_fields = ("name",)


class IngredientRecipeInLine(admin.TabularInline):
    model = IngredientRecipe
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientRecipeInLine,)
    list_display = ("id", "name", "author", "get_likes_for_recipe",)

    list_filter = ("name", "author", "tags__name")

    search_fields = ("name",)

    list_display_links = ('name', )
    filter_horizontal = ('ingredients',)

    @admin.display(description="Likes")
    def get_likes_for_recipe(self, obj):
        return obj.likes

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        current_qs = super().get_queryset(request)
        return current_qs.annotate(likes=Count("isfavorited"))


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "author")


@admin.register(IsFavorited)
class IsFavoritedAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")


@admin.register(IsInShoppingCart)
class IsInShoopingCartAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")

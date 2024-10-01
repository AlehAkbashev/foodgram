from django_filters import rest_framework as filters

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    """
    Фильтр для модели Recipe.
    Фильтрует по полям: tags, author, is_favorited, is_in_shopping_cart.
    """

    tags = filters.AllValuesMultipleFilter(
        field_name="tags__slug",
    )
    is_favorited = filters.BooleanFilter(
        field_name="isfavorited", method="is_favorited_queryset"
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name="isinshoppingcart", method="is_in_shopping_cart_queryset"
    )

    class Meta:
        fields = ("is_favorited", "is_in_shopping_cart", "author", "tags")
        model = Recipe

    def is_favorited_queryset(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(isfavorited__user=self.request.user)
        return queryset

    def is_in_shopping_cart_queryset(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(isinshoppingcart__user=self.request.user)
        return queryset

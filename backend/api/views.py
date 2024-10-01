from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (Ingredient, IngredientRecipe, IsFavorited,
                            IsInShoppingCart, Recipe, Subscription, Tag, User)

from .custom_filters import RecipeFilter
from .pagination import CustomPagination
from .permissions import RecipePermissions
from .search import CustomSearch
from .serializers import (IngredientSerializer, IsFavoriteSerializer,
                          IsInShoppingCartSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, SubscriptionReadSerializer,
                          SubscriptionWriteSerializer, TagSerializer)
from .utils import delete_favor_shopp_subscr, post_favor_shopp_subscr


class TagViewSet(ReadOnlyModelViewSet):
    """
    Представление, обрабатывающее эндпоинт api/tags/
    """

    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)


class IngredientViewSet(ReadOnlyModelViewSet):
    """
    Представление, обрабатывающее эндпоинт api/ingredients/
    """

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (CustomSearch,)
    search_fields = ("^name",)


class CustomUserViewSet(UserViewSet):
    """
    Представление, обрабатывающее следующие действия:
    - регистрация пользователя
    - получение токена пользователем
    - информация для пользователя о самом себе
    - все подписки пользователя
    - возможность подписаться на другого пользователя
    - возможность удалить подписку на другого пользователя
    """

    pagination_class = CustomPagination

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
        pagination_class=CustomPagination,
    )
    def subscriptions(self, request):
        """
        Все подписки пользователя.
        """
        subscriptions = request.user.subscriptions.all()
        limit = request.GET.get("recipes_limit", None)
        paginator = self.paginate_queryset(subscriptions)
        serializer = SubscriptionReadSerializer(
            paginator, many=True, context={"recipes_limit": limit}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=["post", "delete"],
        serializer_class=SubscriptionWriteSerializer,
        permission_classes=(IsAuthenticated,),
        detail=True,
        url_path="subscribe",
        queryset=Subscription.objects.all(),
    )
    def post_and_delete_subscribe(self, request, id):
        """
        Подписаться на пользователя.
        Удалить подписку на пользователя.
        """
        author = get_object_or_404(User, id=self.kwargs.get("id"))
        limit = request.GET.get("recipes_limit")
        if request.method == "POST":
            return post_favor_shopp_subscr(
                self,
                request,
                serializer=SubscriptionWriteSerializer,
                data_field="author",
                pk="id",
                limit=limit,
            )
        return delete_favor_shopp_subscr(
            request,
            data_field="author",
            income_object=author,
            model=Subscription,
        )

    def activation(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def resend_activation(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def reset_password(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def reset_password_confirm(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def set_username(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def reset_username(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def reset_username_confirm(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)


class RecipesViewSet(ModelViewSet):
    """
    Представление, обратывающее следующие действия:
    - информация о рецепте
    - список всех рецептов
    - создание своего рецепта
    - изменение своего рецепта
    - удаление своего рецепта
    - добавить рецепт в избранное
    - удалить рецепт из избранного
    - добавить рецепт в список покупок
    - удалить рецепт из списка покупок
    - скачать список покупок одним файлом
    """

    pagination_class = CustomPagination
    queryset = Recipe.objects.all()
    permission_classes = (RecipePermissions,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        methods=["delete", "post"],
        url_path="favorite",
        detail=True,
        permission_classes=[
            IsAuthenticated,
        ],
        queryset=IsFavorited.objects.all(),
        serializer_class=IsFavoriteSerializer,
    )
    def post_and_del_favorite(self, request, pk):
        if request.method == "POST":
            return post_favor_shopp_subscr(
                self,
                request,
                serializer=IsFavoriteSerializer,
                data_field="recipe",
                pk="pk",
            )
        recipe = get_object_or_404(Recipe, id=self.kwargs.get("pk"))
        return delete_favor_shopp_subscr(
            request,
            data_field="recipe",
            income_object=recipe,
            model=IsFavorited,
        )

    @action(
        methods=["delete", "post"],
        url_path="shopping_cart",
        detail=True,
        permission_classes=[
            IsAuthenticated,
        ],
        serializer_class=IsInShoppingCartSerializer,
        queryset=IsInShoppingCart.objects.all(),
    )
    def post_and_delete_shopping_cart(self, request, pk):

        if request.method == "POST":
            try:
                Recipe.objects.get(id=self.kwargs.get("pk"))
            except Recipe.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return post_favor_shopp_subscr(
                self,
                request,
                serializer=IsInShoppingCartSerializer,
                data_field="recipe",
                pk="pk",
            )
        recipe = get_object_or_404(Recipe, id=self.kwargs.get("pk"))
        return delete_favor_shopp_subscr(
            request,
            data_field="recipe",
            income_object=recipe,
            model=IsInShoppingCart,
        )

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def download_shopping_cart(self, request):
        all_recipes = Recipe.objects.filter(
            isinshoppingcart__user=request.user
        )
        shopping_list = IngredientRecipe.objects.filter(
            recipe__in=all_recipes
        ).values(
            "ingredient__name",
            "ingredient__measurement_unit"
        ).annotate(total=Sum("amount"))

        with open("shopping_list.txt", "w") as file:
            for item in shopping_list:
                file.write(
                    f'{item["ingredient__name"]} - {item["total"]} '
                    f'{item["ingredient__measurement_unit"]}\n'
                )

        file = open("shopping_list.txt")
        response = HttpResponse(file, content_type="text/plain")
        return response

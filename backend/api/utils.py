from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Ingredient, IngredientRecipe


def get_status_for_favor_or_shopp_subsribe(self, model, object, obj_field):
    """
    Возвращает статус подписки или присутствие в списке покупок
    """
    if self.context.get("request").user.is_anonymous:
        return False
    dict_fields = {obj_field: object}
    return model.objects.filter(
        user=self.context.get("request").user, **dict_fields
    ).exists()


def post_favor_shopp_subscr(
    self, request, serializer, data_field, pk, limit=None
):
    """
    Обрабатывает Post запрос на добавление рецепта в избранное,
    в список покупок или подписку на автора.
    """
    context = {"request": request}
    if limit:
        context["recipes_limit"] = limit
        serializer = serializer(
            data={data_field: self.kwargs.get(pk)}, context=context
        )
    else:
        serializer = serializer(
            data={data_field: self.kwargs.get(pk)}, context=context
        )
    serializer.is_valid(raise_exception=True)
    save_objects = {
        "user": request.user,
    }
    serializer.save(**save_objects)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_favor_shopp_subscr(request, data_field, income_object, model):
    """
    Удаляет рецепт из избранного или из списка покупок
    иди удаляет подписку на автора.
    """
    try:
        delete_fields = {"user": request.user, data_field: income_object}
        instance = model.objects.get(**delete_fields)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except model.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def create_update_ingredient(new_ingredients, instance):
    """
    Создает или обновляет ингредиенты в рецепте.
    """
    objects = []
    for item in new_ingredients:
        item = dict(**item)
        current_ingredient = get_object_or_404(
            Ingredient, id=item["ingredient"]
        )
        objects.append(
            IngredientRecipe(
                recipe=instance,
                ingredient=current_ingredient,
                amount=item["amount"],
            )
        )
    IngredientRecipe.objects.bulk_create(objects)

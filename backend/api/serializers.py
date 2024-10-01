from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Ingredient, IngredientRecipe, IsFavorited,
                            IsInShoppingCart, Recipe, Subscription, Tag,
                            TagRecipes, User)

from .utils import (create_update_ingredient,
                    get_status_for_favor_or_shopp_subsribe)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "color", "slug"]

    def validate_id(self, value):
        if not Tag.objects.filter(id=value).exists():
            raise serializers.ValidationError("Такого тега не существует.")
        return value


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name", "measurement_unit"]


class RecipeForSubscription(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class IsInShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
        slug_field="username",
    )

    class Meta:
        model = IsInShoppingCart
        fields = ("recipe", "user")
        validators = [
            UniqueTogetherValidator(
                queryset=IsInShoppingCart.objects.all(),
                fields=("user", "recipe"),
                message=(
                    "Нельзя еще раз добавлять в список покупок "
                    "этот рецепт."
                ),
            )
        ]

    def to_representation(self, instance):
        instance = RecipeForSubscription(instance.recipe)
        return instance.data


class IsFavoriteSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
        slug_field="username",
    )

    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = IsFavorited
        fields = (
            "user",
            "recipe",
        )
        validators = [
            UniqueTogetherValidator(
                queryset=IsFavorited.objects.all(),
                fields=("user", "recipe"),
                message="Нельзя еще раз добавлять в избранное этот рецепт.",
            )
        ]

    def to_representation(self, instance):
        instance = RecipeForSubscription(instance.recipe)
        return instance.data


class SubscriptionReadSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="author.email")
    id = serializers.IntegerField(source="author.id")
    username = serializers.SlugField(source="author.username")
    first_name = serializers.CharField(source="author.first_name")
    last_name = serializers.CharField(source="author.last_name")
    is_subscribed = serializers.BooleanField(default=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source="author.recipes.count")

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.author)
        recipes_limit = self.context.get("recipes_limit")
        try:
            if recipes_limit:
                recipes = recipes[:int(recipes_limit)]
        except ValueError:
            raise serializers.ValidationError(
                "recipe_limit это число, а не текстовая строка"
            )
        return RecipeForSubscription(recipes, many=True).data


class SubscriptionWriteSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
        slug_field="username",
    )

    class Meta:
        model = Subscription
        fields = ("user", "author")
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=("user", "author"),
                message="Можно только один раз подписаться на пользователя",
            )
        ]

    def to_representation(self, instance):
        user = SubscriptionReadSerializer(
            instance,
            context={"recipes_limit": self.context.get("recipes_limit")},
        )
        return user.data

    def validate_author(self, value):
        if self.context.get("request").user.id == value.id:
            raise serializers.ValidationError(
                "Нельзя подписаться на самого себя"
            )
        return value


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
            "id",
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        return get_status_for_favor_or_shopp_subsribe(
            self, Subscription, obj, obj_field="author"
        )


class IngredientRecipeReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name")
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeReadSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = IngredientRecipeReadSerializer(
        many=True, source="rec_ingredients"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        return get_status_for_favor_or_shopp_subsribe(
            self, IsFavorited, obj, obj_field="recipe"
        )

    def get_is_in_shopping_cart(self, obj):
        return get_status_for_favor_or_shopp_subsribe(
            self, IsInShoppingCart, obj, obj_field="recipe"
        )


class IngredientRecipeWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient")

    class Meta:
        model = IngredientRecipe
        fields = ("id", "amount")

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Количество ингредиента не может быть меньше 1."
            )
        return value

    def validate_id(self, value):
        if not Ingredient.objects.filter(id=value):
            raise serializers.ValidationError(
                "Такого ингредиента не существует"
            )
        return value


class RecipeWriteSerializer(serializers.ModelSerializer):

    image = Base64ImageField()
    tags = serializers.SlugRelatedField(
        queryset=Tag.objects.all(), slug_field="id", many=True
    )
    ingredients = IngredientRecipeWriteSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = ("author",)

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        create_update_ingredient(ingredients, recipe)
        tags_list = []
        for tag in tags:
            tags_list.append(
                TagRecipes(
                    recipe=recipe,
                    tag=tag
                )
            )
        TagRecipes.objects.bulk_create(tags_list)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        new_ingredients = validated_data.pop("ingredients")
        instance.rec_ingredients.all().delete()
        create_update_ingredient(new_ingredients, instance)
        new_tags = validated_data.pop("tags")
        instance.tags.set(new_tags)
        return super().update(instance, validated_data)

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                {"Список ингредиентов не может быть пустым."}
            )
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                "Поле тег не может быть пустым."
            )
        tags_set = set()
        for item in value:
            if item in tags_set:
                raise serializers.ValidationError(
                    {
                        "tags": (
                            "В рецепте есть повторяющиеся теги. "
                            "Необходимо удалить повторы."
                        )
                    }
                )
            tags_set.add(item)
        return value

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                {"Необходимо добавить фотографию."}
            )
        return value

    def validate(self, attrs):
        items = dict(**attrs)
        REQUIRED_FIELDS = (
            "ingredients",
            "tags",
        )
        for field in REQUIRED_FIELDS:
            if field not in items:
                raise serializers.ValidationError(
                    {
                        field: f"Не хватает поля {field}"
                    }
                )
        ingred_set = set()
        ingredients = items.get("ingredients")
        if ingredients:
            for item in ingredients:
                id = dict(**item)["ingredient"]
                if id in ingred_set:
                    raise serializers.ValidationError(
                        {
                            "ingredient": (
                                "В рецепте есть повторяющийся ингредиент. "
                                "Необходимо удалить повторы."
                            )
                        }
                    )
                ingred_set.add(id)
        return attrs

    def to_representation(self, instance):
        recipe = RecipeReadSerializer(
            instance,
            context={
                "request": self.context.get("request"),
            },
        )
        return recipe.data

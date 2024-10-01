from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from .const import COLOR_MAX_LEN, COMMON_MAX_LEN, TEXT_MAX_LEN

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=COMMON_MAX_LEN,
        verbose_name="Название тега",
        unique=True
    )

    color = ColorField(
        max_length=COLOR_MAX_LEN,
        verbose_name="Цвет тега",
        unique=True,
    )

    slug = models.SlugField(
        max_length=COMMON_MAX_LEN,
        unique=True,
        verbose_name="Слаг тега",
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=COMMON_MAX_LEN, blank=False, verbose_name="Название"
    )
    measurement_unit = models.CharField(
        max_length=COMMON_MAX_LEN,
        blank=False,
        verbose_name="Единица измерения",
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_name_measurement_unit",
            )
        ]

    def __str__(self) -> str:
        return self.name


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscriptions"
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_user_author"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} подписан на {self.author}"

    def clean(self) -> None:
        if self.user == self.author:
            raise ValidationError("Нельзя подписаться на самого себя")


class Recipe(models.Model):
    name = models.CharField(max_length=COMMON_MAX_LEN)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipes"
    )
    image = models.ImageField(upload_to="recipes_image/")
    text = models.CharField(max_length=TEXT_MAX_LEN)
    ingredients = models.ManyToManyField(
        Ingredient, through="IngredientRecipe"
    )
    tags = models.ManyToManyField(Tag, through="TagRecipes", null=False)
    cooking_time = models.IntegerField(validators=[MinValueValidator(1)])
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)

    def __str__(self) -> str:
        return self.name


class AbstractRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class IsFavorited(AbstractRecipe):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="is_favorited"
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "user"), name="unique_recipe_user_favorite"
            )
        ]

    def __str__(self) -> str:
        return f"Рецепт {self.recipe} нравится {self.user}"


class IsInShoppingCart(AbstractRecipe):

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="is_in_shopping_cart"
    )

    class Meta:
        verbose_name = "Рецепт в списке покупок"
        verbose_name_plural = "Рецепты в списке покупок"
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "user"),
                name="unique_recipe_user_in_shopping",
            )
        ]

    def __str__(self) -> str:
        return f"{self.recipe} в списке покупок у пользователя {self.user}"


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="ingr_recipes"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="rec_ingredients"
    )

    amount = models.PositiveIntegerField()

    class Meta:
        verbose_name = ("Ингредиент в рецепте",)
        verbose_name_plural = "Ингредиенты в рецепте"
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "ingredient"),
                name="unique_recipe_ingredient",
            )
        ]


class TagRecipes(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="tag_recipes"
    )
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

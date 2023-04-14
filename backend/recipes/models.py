from django.core import validators
from django.db import models
from users.models import CustomUser


class Tag(models.Model):
    """Теги"""
    name = models.CharField(
        'Имя',
        unique=True,
        max_length=200,
        help_text='Название тега',
        validators=[
            validators.RegexValidator(
                r'[-+\w\s]+',
                'Недопустимые символы в имени!'
            )
        ]
    )
    color = models.CharField(
        'Цвет',
        max_length=7,
        help_text='Цвет тега',
        validators=[
            validators.RegexValidator(
                r'#[a-fA-F0–9]{6}',
                'Недопустимые символы в коде цвета!'
            )
        ]
    )
    slug = models.SlugField(
        'Путь',
        max_length=200,
        unique=True,
        help_text='Путь тега',
        validators=[
            validators.RegexValidator(
                r'[-\w]+',
                'Недопустимые символы в пути!'
            )
        ]
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('slug', )

    def __str__(self):
        return self.name


class Unit(models.Model):
    """Единицы измерения"""
    name = models.CharField(
        'Имя',
        max_length=200,
        help_text='Название единицы измерения',
    )

    class Meta:
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'
        ordering = ('name', )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингредиенты"""
    name = models.CharField(
        'Имя',
        max_length=200,
        help_text='Название ингредиента',
    )
    measurement_unit = models.ForeignKey(
        Unit,
        null=True,
        on_delete=models.SET_NULL,
        related_name='ingredients',
        help_text='Единица измерения',
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name', )

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    """Рецепты"""
    name = models.CharField(
        'Название',
        max_length=200,
        help_text='Название рецепта',
    )
    text = models.TextField(
        'Описание',
        help_text='Описание рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/images/', null=True, blank=True)
    cooking_time = models.PositiveIntegerField(
        'Время приготовления (в минутах)',
        help_text='Время в минутах, необходимое для приготовления',
        validators=[
            validators.MinValueValidator(1)
        ]
    )
    author = models.ForeignKey(
        CustomUser, related_name='recipes', on_delete=models.CASCADE)
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name', 'author', )

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    """Теги рецептов"""
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег',
        help_text='Тег',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Рецепт',
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'
        ordering = ('tag', 'recipe')

        constraints = models.UniqueConstraint(
            fields=('tag', 'recipe'),
            name='tag_recipe',
        ),

    def __str__(self):
        return f':Тег {self.tag} рецепта {self.recipe}'


class IngredientRecipe(models.Model):
    """"Ингредиенты рецептов"""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        help_text='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Рецепт',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        help_text='Количество ингредиента',
        validators=[
            validators.MinValueValidator(1)
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        ordering = ('ingredient', 'recipe')

        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='ingredient_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe} - {self.ingredient} ({self.amount})'


class ShoppingCart(models.Model):
    """Список покупок"""
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='shopping_cart')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='in_users_cart')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        ordering = ('user', 'recipe')

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в список покупок'


class Subscription(models.Model):
    """Подписки на авторов"""
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='follower')
    following = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='following')

    class Meta:
        verbose_name = 'Подписка на автора'
        verbose_name_plural = 'Подписки на авторов'
        ordering = ('user', 'following')

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_following'
            )
        ]

    def __str__(self):
        return f'Пользователь {self.user} подписан на {self.following}'


class Favorite(models.Model):
    """Избранные рецепты"""
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='choosing')

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('user', 'recipe')

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном {self.user}'

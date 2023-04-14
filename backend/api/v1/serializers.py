import base64

from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from django.db import transaction
from django.shortcuts import get_object_or_404
from recipes import models
from rest_framework import serializers, validators
from users.models import CustomUser


def check_user_authentication(context):
    """ Проверка авторизации пользователя"""
    return ('request' in context
            and context['request'].user.is_authenticated)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[
            validators.UniqueValidator(
                queryset=CustomUser.objects.all()
            ),
            RegexValidator(
                r'^[\w.@+-]+\Z',
                'Недопустимые символы в логине!'
            )]
    )
    email = serializers.EmailField(
        required=True,
        validators=[validators.UniqueValidator(
            queryset=CustomUser.objects.all()
        )]
    )
    is_subscribed = serializers.SerializerMethodField(
        method_name='_get_is_subscribed')

    def _get_is_subscribed(self, obj):
        if not check_user_authentication(self.context):
            return False

        return models.Subscription.objects.filter(
            user=self.context['request'].user,
            following=obj
        ).exists()

    def create(self, validated_data):
        return models.CustomUser.objects.create_user(**validated_data)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response.pop('password')
        if ('request' in self.context
                and self.context['request'].method == 'POST'):
            response.pop('is_subscribed')
        return response

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя зарегистрировать пользователя с таким именем!')
        return value

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'id',
            'email',
            'password',
            'first_name',
            'last_name',
            'is_subscribed',
        )


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)


class TokenSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    email = serializers.CharField(required=True)


class UnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Unit
        fields = (
            'id',
            'name',
        )


class TagSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    name = serializers.CharField(
        required=False,
        validators=[validators.UniqueValidator(
            queryset=models.Tag.objects.all()
        )])
    color = serializers.CharField(required=False)
    slug = serializers.SlugField(
        required=False,
        validators=[validators.UniqueValidator(
            queryset=models.Tag.objects.all()
        )])

    class Meta:
        model = models.Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    measurement_unit = serializers.SlugRelatedField(
        required=False,
        slug_field='name',
        queryset=models.Unit.objects.all()
    )

    class Meta:
        model = models.Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=models.Ingredient.objects.all()
    )
    name = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name',
        source='ingredient'
    )

    def to_representation(self, instance):
        measurement_unit = instance.ingredient.measurement_unit
        response = super().to_representation(instance)
        response['measurement_unit'] = measurement_unit.name
        return response

    class Meta:
        model = models.IngredientRecipe
        fields = (
            'id',
            'name',
            'amount'
        )


class RecipeBaseSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = models.Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class RecipeReadSerializer(RecipeBaseSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        source='ingredientrecipe_set',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='_get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='_get_is_in_shopping_cart')

    def _get_is_favorited(self, obj):
        if not check_user_authentication(self.context):
            return False

        return models.Favorite.objects.filter(
            user=self.context['request'].user,
            recipe=obj
        ).exists()

    def _get_is_in_shopping_cart(self, obj):
        if not check_user_authentication(self.context):
            return False

        return models.ShoppingCart.objects.filter(
            user=self.context['request'].user,
            recipe=obj
        ).exists()

    class Meta:
        model = models.Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = ('author', 'is_favorited', 'is_in_shopping_cart')


class RecipeSerializer(RecipeReadSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=models.Tag.objects.all(), many=True)
    ingredients = IngredientRecipeSerializer(many=True)

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        author = self.context['request'].user
        recipe = models.Recipe.objects.create(
            **validated_data,
            author=author
        )

        list_ingredient = []
        for position in ingredients:
            list_ingredient.append(
                models.IngredientRecipe(**position, recipe=recipe)
            )
        models.IngredientRecipe.objects.bulk_create(list_ingredient)

        list_tags = []
        for tag in tags:
            list_tags.append(models.TagRecipe(tag=tag, recipe=recipe))
        models.TagRecipe.objects.bulk_create(list_tags)
        return recipe

    def update(self, instance, validated_data):
        fields = ('name', 'text', 'cooking_time', 'image',)
        for field in fields:
            if field in validated_data:
                instance.__setattr__(field, validated_data.get(field))

        if 'tags' in validated_data:
            instance.tags.clear()
            for tag in validated_data.pop('tags'):
                instance.tags.add(tag)

        if 'ingredients' in validated_data:
            instance.ingredients.clear()
            for position in validated_data.pop('ingredients'):
                instance.ingredients.add(
                    position.pop('ingredient'),
                    through_defaults=position
                )

        instance.save()
        return instance

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(instance)
        return serializer.data


class CurrentRecipeDefault:
    requires_context = True

    def __call__(self, serializer_field):
        view = serializer_field.context['view']
        return get_object_or_404(models.Recipe, id=view.kwargs['recipe_id'])

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=CurrentRecipeDefault()
    )

    def to_representation(self, instance):
        serializer = RecipeBaseSerializer(instance.recipe)
        return serializer.data

    class Meta:
        model = models.Favorite
        fields = (
            'user',
            'recipe',
        )
        validators = [
            validators.UniqueTogetherValidator(
                queryset=models.Favorite.objects.all(),
                fields=('user', 'recipe')
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=CurrentRecipeDefault()
    )

    def to_representation(self, instance):
        serializer = RecipeBaseSerializer(instance.recipe)
        return serializer.data

    class Meta:
        fields = (
            'user',
            'recipe',
        )
        model = models.ShoppingCart
        validators = [
            validators.UniqueTogetherValidator(
                queryset=models.ShoppingCart.objects.all(),
                fields=('user', 'recipe')
            )
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='id',
        default=serializers.CurrentUserDefault()
    )

    def __get_user(self, view):
        """Получить экземпляр User по id из пути."""
        id = view.kwargs.get('user_id')
        return get_object_or_404(models.CustomUser, id=id)

    def to_representation(self, instance):
        author = instance.following
        recipes = author.recipes.all()
        if 'recipes_limit' in self.context:
            recipes = recipes[:self.context['recipes_limit']]
        serializer = RecipeBaseSerializer(recipes, many=True)
        response = UserSerializer(author).data
        response['is_subscribed'] = True
        response['recipes'] = serializer.data
        response['recipes_count'] = recipes.count()
        return response

    def validate(self, data):
        user = self.context.get('request').user
        following = self.__get_user(self.context.get('view'))
        if user == following:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!')
        elif models.Subscription.objects.filter(
                user=user,
                following=following).exists():
            raise serializers.ValidationError(
                'Такая подписка уже существует!')
        return data

    class Meta:
        exclude = ('following', )
        model = models.Subscription

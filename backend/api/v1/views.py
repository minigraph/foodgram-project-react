import os
import uuid

from django.conf import settings
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes import models
from rest_framework import mixins, pagination, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import CustomUser

from . import filters, permissions, serializers
from .pagination import PageLimitPagination


class CreateViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    pass


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (AllowAny,)
    retrieve_permission = (IsAuthenticated,)
    pagination_class = PageLimitPagination

    def get_permissions(self):
        if self.action == 'retrieve':
            return [permission() for permission in self.retrieve_permission]
        else:
            response = super().get_permissions()
            return response

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        """Посмотреть данные своего профиля"""
        user = request.user
        serializer = serializers.UserSerializer(user)
        return Response(serializer.data)

    @action(
        methods=['POST'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        """Изменить пароль"""
        serializer = serializers.ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if user.check_password(request.data.get('current_password')):
            user.set_password(request.data.get('new_password'))
            return Response(status=status.HTTP_204_NO_CONTENT)
        error = {'detail': 'Неверный пароль от учетной записи'}
        return Response(error, status=status.HTTP_401_UNAUTHORIZED)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        """Список подписок пользователя"""
        queryset = request.user.follower.all()

        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None:
            recipes_limit = pagination._positive_int(recipes_limit)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.SubscriptionSerializer(page, many=True)
            serializer.context['recipes_limit'] = recipes_limit
            return self.get_paginated_response(serializer.data)

        serializer = serializers.SubscriptionSerializer(queryset, many=True)
        serializer.context['recipes_limit'] = recipes_limit
        return Response(serializer.data)


class TokenViewSet(viewsets.ViewSet):
    @action(
        methods=['POST'],
        detail=False,
        permission_classes=(AllowAny,)
    )
    def login(self, request):
        """Получение токена"""
        serializer = serializers.TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            CustomUser,
            email=request.data.get('email')
        )
        raw_password = request.data.get('password')
        if user.check_password(raw_password):
            token, _ = Token.objects.get_or_create(user=user)
            result = {'auth_token': token.key}
            return Response(result, status=status.HTTP_200_OK)

        error = {'detail': 'Неверный пароль'}
        return Response(error, status=status.HTTP_401_UNAUTHORIZED)

    @action(
        methods=['POST'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def logout(self, request):
        """Удаление токена"""
        user = request.user
        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = models.Recipe.objects.all()
    pagination_class = PageLimitPagination
    permission_classes = (permissions.OwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = filters.RecipeFilter

    def _get_related_data(self, user, favorite):
        if favorite:
            return user.favorites.all().values_list('recipe_id', flat=True)
        else:
            return user.shopping_cart.all().values_list(
                'recipe_id', flat=True)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.RecipeReadSerializer
        else:
            return serializers.RecipeSerializer

    def get_queryset(self):
        user, data = self.request.user, models.Recipe.objects
        is_favorited = self.request.query_params.get('is_favorited')
        shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        if not is_favorited and not shopping_cart:
            return data.all()
        elif is_favorited and shopping_cart:
            list_favorite = set(self._get_related_data(user, True))
            list_shopping = set(self._get_related_data(user, False))
            list_id = list(list_favorite.intersection(list_shopping))
            return data.filter(id__in=list_id)
        else:
            list_id = list(self._get_related_data(user, is_favorited))
            return data.filter(id__in=list_id)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок"""
        shopping_list = models.ShoppingCart.objects.filter(
            user=request.user
        )
        if not shopping_list.exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        cart = {}
        for shop_position in shopping_list:
            composition = models.IngredientRecipe.objects.filter(
                recipe=shop_position.recipe)
            for line in composition:
                name = str(line.ingredient)
                if name in cart.keys():
                    cart[name] += line.amount
                else:
                    cart[name] = line.amount

        text = ['Список покупок:', ]
        for position in cart.items():
            text.append(f'{position[0]} - {position[1]}')

        name_file = uuid.uuid4().hex + '.txt'
        file_path = os.path.join(
            os.path.join(settings.BASE_DIR, 'temp'), name_file)
        f = open(file_path, "w+")
        f.write("\n".join(text))
        f.close()

        response = FileResponse(
            open(file_path, "rb"),
            as_attachment=True,
            filename='shopping_cart.txt'
        )
        os.remove(file_path)
        return response


class FavoriteViewSet(CreateViewSet):
    serializer_class = serializers.FavoriteSerializer
    permission_classes = (IsAuthenticated, )

    def __get_recipe(self):
        """Получить экземпляр Recipe по id из пути."""
        id = self.kwargs.get('recipe_id')
        return get_object_or_404(models.Recipe, id=id)

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user, recipe=self.__get_recipe())

    @action(methods=['DELETE'], detail=True)
    def delete(self, request, recipe_id=None):
        recipe = get_object_or_404(models.Recipe, id=recipe_id)
        result = models.Favorite.objects.filter(
            user=request.user,
            recipe=recipe,
        )
        if result.exists():
            result.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            context = {'errors': 'object does not exist'}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionViewSet(CreateViewSet):
    serializer_class = serializers.SubscriptionSerializer
    permission_classes = (IsAuthenticated, )

    def __get_user(self):
        """Получить экземпляр User по id из пути."""
        id = self.kwargs.get('user_id')
        return get_object_or_404(models.CustomUser, id=id)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, following=self.__get_user())

    @action(methods=['DELETE'], detail=True)
    def delete(self, request, user_id=None):
        following = get_object_or_404(models.CustomUser, id=user_id)
        result = models.Subscription.objects.filter(
            user=request.user,
            following=following,
        )
        if result.exists():
            result.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            context = {'errors': 'object does not exist'}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class ShoppingCartViewSet(CreateViewSet):
    serializer_class = serializers.ShoppingCartSerializer
    permission_classes = (IsAuthenticated, )

    def __get_recipe(self):
        """Получить экземпляр Recipe по id из пути."""
        id = self.kwargs.get('recipe_id')
        return get_object_or_404(models.Recipe, id=id)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, recipe=self.__get_recipe())

    @action(methods=['DELETE'], detail=True)
    def delete(self, request, recipe_id=None):
        recipe = get_object_or_404(models.Recipe, id=recipe_id)
        result = models.ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe,
        )
        if result.exists():
            result.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            context = {'errors': 'object does not exist'}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    permission_classes = (AllowAny, )
    pagination_class = None
    filter_backends = (filters.CustomNameSearch, )
    search_fields = ('^name', )

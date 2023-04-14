from django.urls import include, path
from rest_framework import routers

from .views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                    ShoppingCartViewSet, SubscriptionViewSet, TagViewSet,
                    TokenViewSet, UserViewSet)

v1_router = routers.DefaultRouter()
v1_router.register(r'users', UserViewSet)
v1_router.register(r'tags', TagViewSet)
v1_router.register(r'recipes', RecipeViewSet, basename='recipes')
v1_router.register(r'auth/token', TokenViewSet, basename='token')
v1_router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingCartViewSet,
    basename='shopping_cart')
v1_router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteViewSet,
    basename='favorite')
v1_router.register(
    r'users/(?P<user_id>\d+)/subscribe',
    SubscriptionViewSet,
    basename='subscribe')
v1_router.register(r'ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(v1_router.urls)),
]

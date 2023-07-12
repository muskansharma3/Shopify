from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'', views.RegistrationViewSet)

urlpatterns = [
    path("", views.index, name="home"),
    path("signup", views.sign_up, name="sign"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("cart", views.cart_details, name="cart"),
    path("checkout", views.checkout, name="checkout"),
    path("order", views.order_details, name="order"),
    path('rest-api', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

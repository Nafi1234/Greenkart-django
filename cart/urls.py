from django.urls import path
from . import views


urlpatterns = [
    path('', views.cart, name='cart'),
    path('add_cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('remove_cart/<int:product_id>/<int:cart_item_id>/', views.remove_cart, name='remove_cart'),
    path('remove_cart_items/<int:product_id>/<int:cart_item_id>/', views.remove_cart_items, name='remove_cart_items'),
    path('checkout/', views.checkout, name='checkout'),
    path('add_address/',views.add_address,name='add_address'),
    path('get_valid_coupons/', views.get_valid_coupons, name='get_valid_coupons'),

] 
from django.contrib import admin
from django.urls import path,include
from .import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('',views.storepage,name='store'),
    path('category/<slug:category_slug>/', views.storepage, name='products_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/',views.productdetails,name='productdetail'),
     path('search/', views.search, name='search'),
    
    
] 
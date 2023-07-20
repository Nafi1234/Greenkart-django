from django.urls import path
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('payments/',views.payments,name='payments'),
     path('successful/', views.successful, name='successful'),
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove_coupon/',views.remove_coupon,name='remove_coupon'),
    path('download/invoice/', views.download_invoice, name='download_invoice'),
]

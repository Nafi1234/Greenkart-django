from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('activate/<uidb64>/<token>/',views.activate,name='activate'),
    path('logout/',views.logout,name='logout'),
    path('kdashboard/',views.dashboard,name='userdashboard'),
    path('myorders/',views.my_orders,name='my_orders'),
    path('editprofile/', views.editprofile, name='editprofile'),
    path('change_password/', views.change_password, name='change_password'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('refferal/',views.refferal,name='refferal'),
    path('wallet/',views.wallet,name='wallet'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('inovicesucessfull/<int:order_number>/',views.inovicesucessfull,name='invoicesucessfull'),
    path('initiate_refund/<int:order_id>/',views.initiate_refund,name='initiate_refund'),


   

    
]
from django.urls import path
from .import views

urlpatterns = [
    path('adminlogin/',views.adminlogin,name='adminlogin'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('category/',views.category,name='category'),
    path('category/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    path('add-category/', views.add_category, name='add_category'),
    path('product/',views.adminproduct,name='adminproduct'),
    path('product/delete/<int:product_id>/', views.toggle_availability, name='toggle_availability'),
    path('addproduct/',views.add_product,name='add_product'),
    path('adminuser/',views.user_management,name='user_mangement'),
    path('adminorder/',views.adminorder,name='adminorder'),
    path('deleteorder/<order_number>/',views.delete_order,name='deleteorder'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('update-product/<int:product_id>/', views.update_product, name='update_product'),
    path('coupons/', views.coupon_list, name='coupon_list'),
    path('coupons/add/', views.add_coupon, name='add_coupon'),
    path('coupons/edit/', views.edit_coupon, name='edit_coupon'),
    path('coupons/<int:coupon_id>/delete/', views.delete_coupon, name='delete_coupon'),
    path('variations/',views.list_variations,name='list_variations'),
    path('add-variation/', views.add_variation, name='add_variation'),
    path('adminwallet/',views.adminwallet,name='adminwallet'),
    path('order-detail/<int:order_number>',views.order_detail,name='order-details'),
    path('update_refund_status/<int:order_id>',views.update_refund_status,name='update_refund_status'),
    path('adminchart/',views.adminchart,name='adminchart'),
    path('adminlogout/', views.adminlogout, name='adminlogout'),

]
     





    

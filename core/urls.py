from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('addresses/', views.address_list_view, name='address_list'),
    path('add-address/', views.save_address, name='save_address'),
    path('address/<int:address_id>/', views.address_detail, name='address_detail'),
    path('update-cart/', views.update_cart_ajax, name='update_cart_ajax'),
    path('place-order/', views.place_order_from_cart, name='place_order'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('set-selected-address/', views.set_selected_address, name='set_selected_address'),
    path('order-summary/', views.order_summary, name='order_summary'),


]

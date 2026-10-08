from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('catalog/', views.catalog_view, name='catalog'),
    path('product/<int:pk>/', views.product_detail_view, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add_view, name='cart_add'),
    path('cart/update/<int:item_id>/', views.cart_update_view, name='cart_update'),
    path('cart/remove/<int:item_id>/', views.cart_remove_view, name='cart_remove'),
    path('cart/clear/', views.cart_clear_view, name='cart_clear'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/confirmation/<int:order_id>/', views.order_confirmation_view, name='order_confirmation'),
    path('orders/', views.order_list_view, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('urgent-enquiry/', views.urgent_enquiry_view, name='urgent_enquiry'),
    path('urgent-enquiry/success/<int:enquiry_id>/', views.urgent_enquiry_success_view, name='urgent_enquiry_success'),
    path('certificate/verify/', views.certificate_verify_view, name='certificate_verify'),
    path('about/', views.about_view, name='about'),
    path('faq/', views.faq_view, name='faq'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('admin-portal/', views.admin_dashboard_view, name='admin_dashboard'),
]

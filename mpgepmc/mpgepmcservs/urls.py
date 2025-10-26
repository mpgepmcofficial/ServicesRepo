from django.urls import path
from . import views

urlpatterns = [
    # 1. Services Class List Page (Index)
    path('', views.service_class_list, name='index'), 
    
    # 2. Specific Service Class Page
    path('services/<slug:class_slug>/', views.service_class_detail, name='service_class_detail'),
    
    # 3. Specific Service Page (Packages List)
    path('services/<slug:class_slug>/<slug:service_slug>/', views.service_detail, name='service_detail'),
    
    # Cart Actions
    path('cart/add/<int:package_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:package_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # 4. Cart Page
    path('cart/', views.cart_detail, name='cart_detail'),
    
    # 5. Payment Page
    path('checkout/payment/', views.payment_page, name='payment_page'),
    
    # Checkout Action (Placeholder)
    path('checkout/complete/', views.checkout_complete, name='checkout_complete'),
]

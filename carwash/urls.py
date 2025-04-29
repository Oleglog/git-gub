from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('services/', views.services_page, name='services'),
    path('about/', views.about, name='about'),
    path('gallery/', views.gallery, name='gallery'),
    path('contacts/', views.contacts_page, name='contacts'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('get-spots/', views.get_spots, name='get_spots'),
    path('payment/<int:booking_id>/', views.payment_page, name='payment'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
]


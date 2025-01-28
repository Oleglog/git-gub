from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('services/', views.services_page, name='services'),
    path('prices/', views.prices_page, name='prices'),
    path('gallery/', views.gallery_page, name='gallery'),
    path('contacts/', views.contacts_page, name='contacts'),
]
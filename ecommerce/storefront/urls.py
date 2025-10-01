from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('products/', views.products, name='products'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('account/', views.account, name='account'),
]
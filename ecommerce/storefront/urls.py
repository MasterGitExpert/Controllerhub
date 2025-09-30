from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),       # homepage
    path('account/', views.account, name='account'),  # account page
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('account/', views.account, name='account'),
    
    # Contact message management URLs
    path('message/<int:message_id>/read/', views.mark_message_read, name='mark_message_read'),
    path('message/<int:message_id>/unread/', views.mark_message_unread, name='mark_message_unread'),
    path('message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
]
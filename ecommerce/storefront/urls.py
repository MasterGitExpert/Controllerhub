from django.urls import path, include
from django.http import HttpResponse
from django.urls import get_resolver
from . import views
from .views import SignUpView

def _routes(_request):
    names = sorted(k for k in get_resolver().reverse_dict.keys() if isinstance(k, str))
    return HttpResponse("<pre>" + "\n".join(names) + "</pre>")

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.products, name="products"),
    path("product/<int:pk>", views.product, name="product"),
    path('product/<int:product_id>/add_review/', views.add_review, name='add_review'),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("account/", views.account, name="account"),

    path("cart/", views.cart, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/clear/", views.clear_cart, name="clear_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/success/<int:order_id>/", views.checkoutsuccess, name="checkoutsuccess"),

    path("accounts/signup/", SignUpView.as_view(), name="signup"),
    path("accounts/", include("django.contrib.auth.urls")),

    path("_routes/", _routes, name="_routes"),

    # Contact message management URLs
    # path('message/<int:message_id>/read/', views.mark_message_read, name='mark_message_read'),
    # path('message/<int:message_id>/unread/', views.mark_message_unread, name='mark_message_unread'),
    # path('message/<int:message_id>/delete/', views.delete_message, name='delete_message')
]


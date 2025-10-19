from django.urls import path
from django.http import HttpResponse
from django.urls import get_resolver
from . import views

def _routes(_request):
    names = sorted(k for k in get_resolver().reverse_dict.keys() if isinstance(k, str))
    return HttpResponse("<pre>" + "\n".join(names) + "</pre>")

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.products, name="products"),
    path("product/<int:pk>", views.product, name="product"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("account/", views.account, name="account"),

    path("cart/", views.cart, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/clear/", views.clear_cart, name="clear_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/success/<int:order_id>/", views.checkoutsuccess, name="checkoutsuccess"),

    path("_routes/", _routes, name="_routes"),
    path("product/<int:pk>/customize/", views.customize, name="customize"),
]

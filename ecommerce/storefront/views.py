from django.shortcuts import render
from .models import Product

# Create your views here.


def home(request):
    return render(request, "index.html")


def products(request):
    products = Product.objects.all().order_by('name')
    return render(request, "products.html", {'products': products})


def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")


def account(request):
    return render(request, "account.html")

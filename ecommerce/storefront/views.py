from django.shortcuts import render
from .models import Product
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    products = Product.objects.all().order_by('name')
    return render(request, "index.html", {'products': products})

@login_required
def account(request):
    return render(request, "account.html")
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Product, Customer, Order, OrderItem, Review
from django.db import models
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.

CART_SESSION_KEY = "cart"


def home(request):
    return render(request, "index.html")


def products(request):
    """
        Returns a rendered view to display all products with search and
        sort functionality
    """
    # Get all products that are marked for display
    products = Product.objects.all().filter(display_item=True)
    # Update sale price to price for all products not on discount
    # this for price ordering purposes and check stock to update tagline
    # if any products is out of stock.
    for product in products:
        product.update_sale_price()
        product.check_stock()

    # Handle POST requests for search and sort requests
    if request.method == "POST":
        query = request.POST.get('search')
        sort = request.POST.get('sort')

        # Handles search query
        if query:
            products = products.filter(name__icontains=query)

        # Handles product sorting
        products = products.order_by('name')
        if sort == "non-alphabetical":
            products = products.order_by('-name')
        elif sort == "lowest-price":
            products = products.order_by('sale_price')
        elif sort == "highest-price":
            products = products.order_by('-sale_price')

        # Return the rendered view with the filtered products
        return render(request, "products.html", {'products': products,
                                                 "count": len(products),
                                                 "query": query,
                                                 "sort": sort})
    else:
        # Return all display-able products ordered alphabetically by default
        products = products.order_by('name')
        return render(request, "products.html", {'products': products,
                                                 "count": len(products)})


def product(request, pk):
    """
        Returns a rendered view for displaying a single product passed in
        the URL.
    """
    product = Product.objects.get(id=pk)
    review_count = Review.objects.filter(product=product).count()
    if review_count >= 1:
        review_per_star = {i: [Review.objects.filter(product=product, rating=i).count(
        ), f"{round((Review.objects.filter(product=product, rating=i).count()/review_count)*100)}%"] for i in range(5, 0, -1)}
        avg_rating = round(Review.objects.filter(
            product=product).aggregate(models.Avg('rating'))['rating__avg'], 1)
        stars = []
        counter = round(avg_rating * 2) / 2
        for _ in range(5):
            if counter - 1 >= 0:
                stars.append("fas fa-star")
                counter -= 1
            elif counter - 0.5 == 0:
                stars.append("fas fa-star-half-alt")
            else:
                stars.append("far fa-star")
        overall_review = [avg_rating, stars]
        reviews = Review.objects.all().filter(product=product)
        return render(request, "product.html", {'product': product,
                                                'review_per_star': review_per_star,
                                                'review_count': review_count,
                                                'overall_review': overall_review,
                                                'reviews': reviews})
    return render(request, "product.html", {'product': product,
                                            'review_count': review_count})


def about(request):
    return render(request, "about.html")


@login_required
def account(request):
    return render(request, "account.html")


def contact(request):
    return render(request, "contact.html")


def account(request):
    return render(request, "account.html")


def _get_cart(session):
    return session.setdefault(CART_SESSION_KEY, {})


def _cart_items(cart):
    if not cart:
        return []
    products = {p.id: p for p in Product.objects.filter(
        id__in=[int(pid) for pid in cart.keys()])}
    items = []
    for pid, qty in cart.items():
        p = products.get(int(pid))
        if not p:
            continue
        q = int(qty)
        unit_price = p.sale_price if getattr(p, "discount", False) else p.price
        items.append({"product": p, "quantity": q,
                     "unit_price": unit_price, "subtotal": q * unit_price})
    return items


def _totals(items):
    total = sum(i["subtotal"] for i in items)
    count = sum(i["quantity"] for i in items)
    return total, count


def cart(request):
    cart_dict = _get_cart(request.session)
    items = _cart_items(cart_dict)
    total, count = _totals(items)
    return render(request, "cart.html", {"items": items, "total": total, "count": count})


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    qty = max(1, int(request.POST.get("qty", 1)))

    if product.stock and qty > product.stock:
        qty = product.stock

    cart_dict = _get_cart(request.session)
    pid = str(product.id)
    new_qty = int(cart_dict.get(pid, 0)) + qty
    if product.stock and new_qty > product.stock:
        new_qty = product.stock

    cart_dict[pid] = new_qty
    request.session.modified = True

    messages.success(request, f"Added {qty} × {product.name} to cart.")
    return redirect("cart")


@require_POST
def remove_from_cart(request, product_id):
    cart_dict = _get_cart(request.session)
    pid = str(product_id)
    if pid in cart_dict:
        del cart_dict[pid]
        request.session.modified = True
        messages.info(request, "Item removed from cart.")
    return redirect("cart")


@require_POST
def clear_cart(request):
    request.session[CART_SESSION_KEY] = {}
    request.session.modified = True
    messages.info(request, "Cart cleared.")
    return redirect("cart")


def checkout(request):
    cart_dict = _get_cart(request.session)
    items = _cart_items(cart_dict)
    if not items:
        messages.warning(request, "Your cart is empty.")
        return redirect("home")

    total, _ = _totals(items)

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()

        if not all([first_name, last_name, email, phone, address]):
            messages.error(request, "Please fill in all fields.")
            return render(request, "checkout.html", {"items": items, "total": total})

        customer, _ = Customer.objects.get_or_create(
            email=email,
            defaults={"first_name": first_name, "last_name": last_name,
                      "phone": phone, "password": "guest"},
        )

        order = Order.objects.create(customer=customer, address=address)

        for i in items:
            p = i["product"]
            qty = i["quantity"]
            OrderItem.objects.create(order=order, product=p, quantity=qty)
            if p.stock is not None:
                p.stock = max(0, p.stock - qty)
                p.save(update_fields=["stock"])

        request.session[CART_SESSION_KEY] = {}
        request.session.modified = True

        return redirect("checkoutsuccess", order_id=order.id)

    return render(request, "checkout.html", {"items": items, "total": total})


def checkoutsuccess(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, "checkoutsuccess.html", {"order": order})

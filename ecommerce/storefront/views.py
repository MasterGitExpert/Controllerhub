
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import FormView
from .models import Customer, Product, Order, OrderItem, Review
from .models import ContactMessage
from .forms import ContactForm, ReviewForm, SignUpForm
import re
from .models import Customer, Product, Order, OrderItem, Review, ContactMessage


CART_SESSION_KEY = "cart"


def home(request):
    """
        Returns a rendered view for the home page
    """
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


def contact(request):
    """Display and handle contact form"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the contact message to database
            contact_message = form.save()

            # Send email notification to admin (need to fix this)
            try:
                send_mail(
                    subject=f'New Contact Form: {contact_message.subject}',
                    message=f'From: {contact_message.name} ({contact_message.email})\n\n{contact_message.message}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Email error: {e}")

            # Add success message
            messages.success(
                request, 'Thank you for contacting us! We will get back to you soon.')
            return redirect('contact')
        else:
            # Add error message
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})


@login_required
def account(request):
    if request.user.is_authenticated:
        all_messages = ContactMessage.objects.all()
        total_messages = ContactMessage.objects.count()
        unread_messages = ContactMessage.objects.filter(
            created_at__gte=request.user.last_login).count()
        orders = Order.objects.all().filter(
            user=request.user).order_by('id')
        return render(request, "account.html", {"user": request.user,
                                                "orders": orders,
                                                "contact_messages": all_messages,
                                                "total_messages": total_messages,
                                                "unread_messages": unread_messages})


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
        # Shipping
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()

        # Payment (demo)
        card_name = request.POST.get("card_name", "").strip()
        card_number = (request.POST.get("card_number", "")
                       or "").replace(" ", "")
        card_exp = request.POST.get("card_exp", "").strip()
        card_cvc = request.POST.get("card_cvc", "").strip()

        # Basic validation
        valid_num = re.fullmatch(r"\d{13,19}", card_number)
        valid_exp = re.fullmatch(r"(0[1-9]|1[0-2])\/(\d{2})", card_exp)
        valid_cvc = re.fullmatch(r"\d{3,4}", card_cvc)

        if not all([first_name, last_name, email, phone, address, card_name, valid_num, valid_exp, valid_cvc]):
            messages.error(
                request, "Please complete all fields with valid details.")
            return render(request, "checkout.html", {"items": items, "total": total})

        # Get or create a user
        try:
            user = User.objects.get(
                first_name=first_name, last_name=last_name, email=email)
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=email,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=f"guest{phone}",
            )

        # Keep customers phone up to date if we have their profile
        try:
            cust = Customer.objects.get(user=user)
            if phone and cust.phone != phone:
                cust.phone = phone
                cust.save(update_fields=["phone"])
        except Customer.DoesNotExist:
            pass

        # Derive minimal payment data for demo receipt
        brand = "visa" if card_number.startswith("4") else "card"
        last4 = card_number[-4:]
        exp_month = int(valid_exp.group(1))
        exp_year = 2000 + int(valid_exp.group(2))

        # Create order
        order = Order.objects.create(user=user, address=address)

        # Add items and update stock
        for i in items:
            p = i["product"]
            qty = i["quantity"]
            OrderItem.objects.create(order=order, product=p, quantity=qty)
            if p.stock is not None:
                p.stock = max(0, p.stock - qty)
                p.save(update_fields=["stock"])

        from django.apps import apps

        Payment = apps.get_model("storefront", "Payment")
        Payment.objects.create(
            order=order,
            provider="demo",
            brand=brand,
            last4=last4,
            exp_month=exp_month,
            exp_year=exp_year,
            status="succeeded",
        )

        # Clear cart & redirect
        request.session[CART_SESSION_KEY] = {}
        request.session.modified = True

        return redirect("checkoutsuccess", order_id=order.id)

    # GET
    return render(request, "checkout.html", {"items": items, "total": total})


def checkoutsuccess(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, "checkoutsuccess.html", {"order": order})


def add_review(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            if request.user.is_authenticated:
                review.user = request.user
            review.save()
            messages.success(
                request, "Thanks! Your review has been submitted.")
            return redirect(f"/product/{product.id}#reviews")
        messages.error(request, "Please fix the errors below.")
    else:
        form = ReviewForm()
    return render(request, "reviews/add_review.html", {"form": form, "product": product})


class SignUpView(FormView):
    template_name = "registration/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        user = form.save()
        raw_password = form.cleaned_data.get("password1")
        user = authenticate(
            self.request, username=user.username, password=raw_password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)


def customize(request, pk):
    product = get_object_or_404(Product, id=pk)
    return render(request, "customize.html", {"product": product})

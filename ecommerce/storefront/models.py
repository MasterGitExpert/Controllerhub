"""Django data models for the ecommerce storefront application."""
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# --------------------
# Customer
# --------------------
class Customer(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    phone = models.CharField(max_length=10, unique=True)
    unit = models.CharField(max_length=8, default="", blank=True, null=True)
    street_number = models.CharField(max_length=8, default="", blank=True, null=True)
    street = models.CharField(max_length=64, default="", blank=True, null=True)
    city = models.CharField(max_length=64, default="", blank=True, null=True)
    postcode = models.CharField(max_length=6, default="", blank=True, null=True)
    state = models.CharField(max_length=32, default="", blank=True, null=True)
    country = models.CharField(max_length=32, default="", blank=True, null=True)

    def get_name(self) -> str:
        return f"{self.user.get_full_name()}"

    def get_username(self) -> str:
        return f"{self.user.get_username()}"

    def get_address(self) -> str:
        if self.street_number and self.street and self.city and self.state and self.postcode and self.country:
            unit_no = f"{self.unit}/" if self.unit else ""
            return f"{unit_no}{self.street_number} {self.street}, {self.city}, {self.state}, {self.postcode}, {self.country}"

    def __str__(self) -> str:
        return f"{self.get_name()} - {self.phone} @ {self.get_address()} "


def create_customer(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)

post_save.connect(create_customer, sender=User)

# --------------------
# Catalogue
# --------------------
class ProductCategory(models.Model):



    name = models.CharField(max_length=16)

    class Meta:
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"

    def __str__(self) -> str:
        return f"{self.name}"
    

class ProductRange(models.Model):
    name = models.CharField(max_length=16)

    class Meta:
        verbose_name = "Product Range"
        verbose_name_plural = "Product Ranges"



    def __str__(self) -> str:
        return f"{self.name}"
    

class Product(models.Model):

    name = models.CharField(max_length=128)
    tagline = models.CharField(max_length=64, default="", blank=True)
    overview = models.TextField(max_length=512, default="One of the finest product.")
    description = models.TextField(max_length=2048, default="No description")
    specifications = models.TextField(max_length=2048, default="No specifications")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=5.00)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='uploads/products/', blank=True, null=True)
    display_item = models.BooleanField(default=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, null=True)
    range = models.ForeignKey(ProductRange, on_delete=models.CASCADE, null=True)
    discount = models.BooleanField(default=False)
    sale_price = models.DecimalField(max_digits=8, decimal_places=2)

    def is_in_stock(self) -> bool:

        return self.stock > 0

    def check_stock(self) -> None:

        if not self.is_in_stock():
            self.tagline = "Out of Stock"
            self.save()

    def update_sale_price(self) -> None:

        if not self.discount:
            self.sale_price = self.price
        self.save()

    def __str__(self) -> str:
        if self.discount:
            striked_price = "".join([f'{c}\u0336' for c in f"${self.price}"])
            price = f"{striked_price} -> ${self.sale_price}"
        else:
            price = f"${self.price}"
        return f"{self.name} - {self.stock} @ {price} (${self.sale_price}) [{self.category}, {self.range}]"

# --------------------
# Orders
# --------------------
class Order(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    address = models.CharField(max_length=256)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=32, default="Processing")

    def get_total_cost(self):
        total = 0.0
        order_items = OrderItem.objects.filter(order=self)
        for item in order_items:
            total += float(item.product.sale_price) * int(item.quantity)
        return total

    def __str__(self) -> str:
        try:
            username = self.user.get_username() if self.user else "Not Set"
        except Exception:
            username = "Not Set"
        return f"Order {self.pk} by {username} on {self.date} ({self.status}) Total: ${self.get_total_cost()}"

class OrderItem(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        return f"Order {self.order.pk} of {self.product.name}: {self.product.price} x {self.quantity} = ${self.product.price * self.quantity}"

# --------------------
# Reviews
# --------------------
class Review(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=100)
    body = models.TextField(max_length=2000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def get_reviewer_username(self):
        try:
            if self.user and self.user.get_username():
                return self.user.get_username()
        except Exception:
            pass
        return "Anonymous"

    def star_list(self):
        stars = []
        counter = round(self.rating * 2) / 2
        for _ in range(5):
            if counter - 1 >= 0:
                stars.append("fas fa-star"); counter -= 1
            elif counter - 0.5 == 0:
                stars.append("fas fa-star-half-alt"); counter -= 0.5
            else:
                stars.append("far fa-star")
        return stars

    def __str__(self):
        return f"{self.get_reviewer_username()} reviewed {self.product.name} at {self.rating}/5 - {self.title}"

# --------------------
# Contact
# --------------------
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"

class Payment(models.Model):
    order = models.OneToOneField("Order", on_delete=models.CASCADE, related_name="payment")
    provider = models.CharField(max_length=20, default="demo")
    brand = models.CharField(max_length=20, blank=True)
    last4 = models.CharField(max_length=4, blank=True)
    exp_month = models.PositiveSmallIntegerField(null=True, blank=True)
    exp_year  = models.PositiveSmallIntegerField(null=True, blank=True)
    status = models.CharField(max_length=30, default="succeeded")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} — {self.provider} (****{self.last4})"

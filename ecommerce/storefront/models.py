"""Django data models for the ecommerce storefront application."""
from tabnanny import verbose
from django.db import models
import datetime

# Create your models here.


class Customer(models.Model):
    """
        Customer table to store customer information
        - first_name
        - last_name
        - email
        - phone
        - password
    """
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(max_length=128, unique=True)
    phone = models.CharField(max_length=10)
    password = models.CharField(max_length=32)

    def __str__(self) -> str:
        return f"{self.last_name} {self.first_name} - {self.email}"


class ProductCategory(models.Model):
    """
        ProductCategory table to store product category information like 
        chairs, keyboards, mouse etc.

        - name
    """
    class Meta:
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"

    name = models.CharField(max_length=16)

    def __str__(self) -> str:
        return f"{self.name}"


class ProductRange(models.Model):
    """
        ProductRange table to store product range information like homebrand,
        premium, limited edition etc.
        - name
    """
    class Meta:
        verbose_name = "Product Range"
        verbose_name_plural = "Product Ranges"

    name = models.CharField(max_length=16)

    def __str__(self) -> str:
        return f"{self.name}"


class Product(models.Model):
    """
        Product table to store product information
        - name
        - tagline
        - overview
        - description
        - specifications
        - price
        - stock
        - image
        - display_item
        - category
        - range
        - discount
        - sale_price
    """
    name = models.CharField(max_length=128)
    tagline = models.CharField(max_length=64, default="", blank=True)
    overview = models.TextField(
        max_length=512, default="One of the finest product.")
    description = models.TextField(max_length=2048, default="No description")
    specifications = models.TextField(
        max_length=2048, default="No specifications")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=5.00)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(
        upload_to='uploads/products/', blank=True, null=True)
    display_item = models.BooleanField(default=True)
    # Product category and range (for filtering)
    category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE, null=True)
    range = models.ForeignKey(
        ProductRange, on_delete=models.CASCADE, null=True)
    # Sale information for discounted items
    discount = models.BooleanField(default=False)
    sale_price = models.DecimalField(
        max_digits=8, decimal_places=2, default=3.98)

    def __str__(self) -> str:
        if self.discount:
            striked_price = "".join(
                [f'{char}\u0336' for char in f"${self.price}"])
            price = f"{striked_price} -> ${self.sale_price}"
        else:
            price = f"${self.price}"
        return f"{self.name} - {self.stock} @ {price} " \
            f"[{self.category}, {self.range}]"


class Order(models.Model):
    """
        Order table to store order information
        - customer
        - address
        - date
        - status
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    address = models.CharField(max_length=256)
    date = models.DateTimeField(default=datetime.datetime.now)
    status = models.CharField(max_length=32, default="In Transit")

    def __str__(self) -> str:
        return f"Order {self.order_id} by {self.customer.first_name} {self.customer.last_name} - {self.status}"


class OrderItem(models.Model):
    """
        OrderItem (associative) table to store each item part of a given order
        - product
        - order
        - quantity
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        return f"Order Item {self.order.order_id}: {self.product.name} x {self.quantity} = ${self.product.price * self.quantity}"

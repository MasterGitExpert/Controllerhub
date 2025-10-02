from django.contrib import admin
from .models import Customer, ProductCategory, ProductRange, Product, Order
from .models import OrderItem

# Register your models here.
admin.site.register(Customer)
admin.site.register(ProductCategory)
admin.site.register(ProductRange)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)

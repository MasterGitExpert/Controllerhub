from django.contrib import admin
<<<<<<< HEAD
from .models import Customer, ProductCategory, ProductRange, Product
from .models import Order, Review, OrderItem, ContactMessage, ProductColor 
from .models import ProductSize
from django.contrib.auth.models import User
=======
from .models import Customer, ProductCategory, ProductRange, Product, Order
from .models import OrderItem, ProductColor, ProductSize
>>>>>>> b153a995f503094a86ba0e62fab236c1a51741a9

# Register your models here.
admin.site.register(Customer)
admin.site.register(ProductCategory)
admin.site.register(ProductRange)
admin.site.register(Product)
admin.site.register(Order, readonly_fields=['date'])
admin.site.register(OrderItem)
<<<<<<< HEAD
admin.site.register(Review, readonly_fields=['created_at'])
admin.site.register(ContactMessage, readonly_fields=['created_at'])
admin.site.register(ProductColor)
admin.site.register(ProductSize)


class CustomerInline(admin.StackedInline):
    model = Customer


class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ("username", "first_name", "last_name", "email")
    list_filter = ("is_staff", "is_superuser", "is_active")
    field = ["username", "first_name", "last_name", "email"]
    inlines = [CustomerInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
=======
admin.site.register(ProductColor)
admin.site.register(ProductSize)
>>>>>>> b153a995f503094a86ba0e62fab236c1a51741a9

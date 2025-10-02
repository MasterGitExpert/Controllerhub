
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm
from .models import ContactMessage
from django.shortcuts import render
from .models import Product


def contact_view(request):
    """Display and handle contact form"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the contact message to database
            contact_message = form.save()
            
            #Send email notification to admin (need to fix this)
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
            messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
            return redirect('contact')
        else:
            # Add error message
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})


from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected messages as unread"
    
    actions = [mark_as_read, mark_as_unread]


from django.urls import path
from . import views

urlpatterns = [

    path('contact/', views.contact_view, name='contact'),
]



# For development - prints emails to console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For production - configure with your email provider
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-app-password'
# DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
# ADMIN_EMAIL = 'admin@yoursite.com'
def home(request):
    return render(request, 'index.html')

def products(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})

def about(request):
    return render(request, 'about.html')

def account(request):
    return render(request, 'account.html')


def account(request):
    """Display contact messages"""
    contact_messages = ContactMessage.objects.all().order_by('-created_at')
    
    context = {
        'contact_messages': contact_messages,
        'total_messages': contact_messages.count(),
        'unread_messages': contact_messages.filter(is_read=False).count(),
    }
    return render(request, 'account.html', context)

def mark_message_read(request, message_id):
    """Mark a contact message as read"""
    message = get_object_or_404(ContactMessage, id=message_id)
    message.is_read = True
    message.save()
    return redirect('account')

def mark_message_unread(request, message_id):
    """Mark a contact message as unread"""
    message = get_object_or_404(ContactMessage, id=message_id)
    message.is_read = False
    message.save()
    return redirect('account')

def delete_message(request, message_id):
    """Delete a contact message"""
    message = get_object_or_404(ContactMessage, id=message_id)
    message.delete()
    return redirect('account')
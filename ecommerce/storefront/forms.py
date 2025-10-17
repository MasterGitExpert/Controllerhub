from django import forms
from .models import Review, ContactMessage
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


STAR_CHOICES = [
    (5, "5 – Excellent"),
    (4, "4 – Good"),
    (3, "3 – Average"),
    (2, "2 – Poor"),
    (1, "1 – Terrible"),
]

class ReviewForm(forms.ModelForm):
    # Explicit fields so we can control labels, widgets, and validation
    title = forms.CharField(
        label="Title",
        max_length=120,
        widget=forms.TextInput(attrs={
            "class": "form-control"
        })
    )

    rating = forms.ChoiceField(
        label="Rating",
        choices=STAR_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "star-rating"}),
    )

    body = forms.CharField(
        label="Your review",
        widget=forms.Textarea(attrs={
            "rows": 6,
            "class": "form-control"
        }),
        help_text="Be constructive and specific. Min 20 characters."
    )

    class Meta:
        model = Review

        fields = ["title", "rating", "body"]

    def clean_body(self):
        text = self.cleaned_data.get("body", "").strip()
        if len(text) < 20:
            raise forms.ValidationError("Please write at least 20 characters.")
        return text

    def clean_rating(self):
        val = int(self.cleaned_data["rating"])
        if val < 1 or val > 5:
            raise forms.ValidationError("Rating must be between 1 and 5 stars.")
        return val

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")# storefront/forms.py
# Create this new file



class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'your.email@example.com',
                'required': True
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'What can we help you with?',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Tell us more about your inquiry...',
                'rows': 6,
                'required': True
            }),
        }
        
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message) < 10:
            raise forms.ValidationError('Message must be at least 10 characters long.')
        return message
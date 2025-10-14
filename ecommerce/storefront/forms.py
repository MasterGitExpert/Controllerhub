from django import forms
from .models import Review

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

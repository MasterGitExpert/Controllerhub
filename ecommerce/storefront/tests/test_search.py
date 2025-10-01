import pytest
from django.urls import reverse
from storefront.models import Product, ProductCategory, ProductRange

@pytest.mark.django_db
def test_search_matches_name_only(client):

    category = ProductCategory.objects.create(name="mouce")
    product_range = ProductRange.objects.create(name="keyboard")

    Product.objects.create(name="Homebrand Mouse", category=category, range=product_range)
    Product.objects.create(name="Keyboard Pro", category=category, range=product_range)

    url = reverse("search")
    resp = client.get(url, {"q": "mouse"})
    assert resp.status_code == 200

    html = resp.content.decode()
    assert "Homebrand Mouse" in html
    assert "Keyboard Pro" not in html
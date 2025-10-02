# storefront/tests.py
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages

from .models import Product, Customer, Order, OrderItem


class StorefrontTests(TestCase):
    def setUp(self):
        # Two products: one regular, one on discount with limited stock
        self.p1 = Product.objects.create(
            name="Controller X",
            price=Decimal("10.00"),
            discount=False,
            sale_price=Decimal("10.00"),  # not used when discount=False
            stock=5,
        )
        self.p2 = Product.objects.create(
            name="Headset Pro",
            price=Decimal("20.00"),
            discount=True,
            sale_price=Decimal("15.00"),
            stock=2,
        )

    # ---------- Simple page renders ----------

    def test_home_renders(self):
        resp = self.client.get(reverse("home"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "index.html")

    def test_products_renders(self):
        resp = self.client.get(reverse("products"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "products.html")

    # ---------- Cart helpers ----------

    def test_cart_empty(self):
        resp = self.client.get(reverse("cart"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "cart.html")
        self.assertContains(resp, "Your cart")  # page loads

    def test_add_to_cart_accumulates_and_clamps_to_stock(self):
        # Try to add more than stock; should clamp to stock (2)
        resp = self.client.post(
            reverse("add_to_cart", args=[self.p2.id]),
            data={"qty": 10},
        )
        self.assertRedirects(resp, reverse("cart"))

        # Session should have qty == stock
        session = self.client.session
        self.assertIn("cart", session)
        self.assertEqual(int(session["cart"].get(str(self.p2.id))), 2)

        # Message is present
        messages = [m.message for m in get_messages(resp.wsgi_request)]
        self.assertTrue(any("Added" in m for m in messages))

    def test_add_to_cart_min_qty_is_one(self):
        resp = self.client.post(
            reverse("add_to_cart", args=[self.p1.id]),
            data={"qty": 0},  # should be treated as 1
        )
        self.assertRedirects(resp, reverse("cart"))
        session = self.client.session
        self.assertEqual(int(session["cart"].get(str(self.p1.id))), 1)

    def test_remove_from_cart(self):
        # Seed cart
        session = self.client.session
        session["cart"] = {str(self.p1.id): 3}
        session.save()

        resp = self.client.post(reverse("remove_from_cart", args=[self.p1.id]))
        self.assertRedirects(resp, reverse("cart"))

        session = self.client.session
        self.assertNotIn(str(self.p1.id), session.get("cart", {}))

    def test_clear_cart(self):
        session = self.client.session
        session["cart"] = {str(self.p1.id): 2, str(self.p2.id): 1}
        session.save()

        resp = self.client.post(reverse("clear_cart"))
        self.assertRedirects(resp, reverse("cart"))

        self.assertEqual(self.client.session.get("cart"), {})

    def test_cart_view_totals(self):
        # p1: 2 * 10.00 = 20.00
        # p2 (discounted): 1 * 15.00 = 15.00
        session = self.client.session
        session["cart"] = {str(self.p1.id): 2, str(self.p2.id): 1}
        session.save()

        resp = self.client.get(reverse("cart"))
        self.assertEqual(resp.status_code, 200)
        # Expect total 35.00 formatted
        self.assertContains(resp, "35.00")

    # ---------- Checkout (GET/POST) ----------

    def test_checkout_redirects_when_cart_empty(self):
        resp = self.client.get(reverse("checkout"))
        self.assertRedirects(resp, reverse("home"))

    def test_checkout_get_with_items_renders(self):
        session = self.client.session
        session["cart"] = {str(self.p1.id): 1}
        session.save()

        resp = self.client.get(reverse("checkout"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "checkout.html")
        self.assertContains(resp, "Checkout")
        self.assertContains(resp, "Controller X")

    def test_checkout_post_creates_order_and_clears_cart_and_updates_stock(self):
        # Seed cart: buy 3 of p1
        session = self.client.session
        session["cart"] = {str(self.p1.id): 3}
        session.save()

        form = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
            "phone": "0400000000",
            "address": "123 Street, City",
        }
        resp = self.client.post(reverse("checkout"), data=form)
        # Should redirect to success page with order id
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/checkout/success/", resp.url)

        # DB assertions
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)

        order = Order.objects.first()
        item = OrderItem.objects.first()
        self.assertEqual(item.order_id, order.id)
        self.assertEqual(item.product_id, self.p1.id)
        self.assertEqual(item.quantity, 3)

        # Stock reduced from 5 to 2
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.stock, 2)

        # Cart cleared
        self.assertEqual(self.client.session.get("cart"), {})

    def test_checkout_post_reuses_existing_customer(self):
        # Create existing customer with same email
        Customer.objects.create(
            first_name="Old",
            last_name="User",
            email="exists@example.com",
            phone="000",
            password="guest",
        )

        # Cart
        session = self.client.session
        session["cart"] = {str(self.p2.id): 1}
        session.save()

        form = {
            "first_name": "New",
            "last_name": "NameIgnoredBecauseGetOrCreate",
            "email": "exists@example.com",
            "phone": "111",
            "address": "456 Road",
        }
        resp = self.client.post(reverse("checkout"), data=form)
        self.assertEqual(resp.status_code, 302)

        # Still only one customer
        self.assertEqual(Customer.objects.filter(email="exists@example.com").count(), 1)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)

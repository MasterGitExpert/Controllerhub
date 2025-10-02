# storefront/tests.py
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.contrib.auth import get_user_model
from django.conf import settings

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
from .models import Product

# Create your tests here.


class ModelTests(TestCase):
    def setUp(self):
        self.xbox = Product(name="Xbox Plus",
                            tagline="New",
                            overview="The fastest, most powerful Xbox ever.",
                            description="Experience the new generation of " +
                            "games and entertainment with Xbox Series " +
                            "X. With its powerful hardware and " +
                            "innovative features, Xbox Series X " +
                            "delivers stunning graphics, faster load " +
                            "times, and immersive gameplay. Get ready " +
                            "to power your dreams and take your gaming " +
                            "to the next level.",
                            specifications="Processor: Custom AMD Zen 2 " +
                            "CPU, Graphics: Custom AMD RDNA 2 GPU, " +
                            "Memory: 16GB GDDR6, Storage: 1TB NVMe " +
                            "SSD, Optical Drive: 4K UHD Blu-ray, " +
                            "Ports: HDMI 2.1, USB 3.1, Ethernet, Wi-Fi 5",
                            price=549.86,
                            stock=1,
                            # image = "",
                            display_item=True,
                            category=None,
                            range=None,
                            discount=False,
                            sale_price=399.99)
        self.ps4 = Product(name="PS4 Pro Max",
                           tagline="While Stocks Last",
                           overview="The fastest, most powerful PS4 ever.",
                           description="Experience the new generation of " +
                           "games and entertainment with Xbox Series " +
                           "X. With its powerful hardware and " +
                           "innovative features, Xbox Series X " +
                           "delivers stunning graphics, faster load " +
                           "times, and immersive gameplay. Get ready " +
                           "to power your dreams and take your gaming " +
                           "to the next level.",
                           specifications="Processor: Custom AMD Zen 2 " +
                           "CPU, Graphics: Custom AMD RDNA 2 GPU, " +
                           "Memory: 16GB GDDR6, Storage: 1TB NVMe " +
                           "SSD, Optical Drive: 4K UHD Blu-ray, " +
                           "Ports: HDMI 2.1, USB 3.1, Ethernet, Wi-Fi 5",
                           price=649.64,
                           stock=0,
                           # image = "",
                           display_item=True,
                           category=None,
                           range=None,
                           discount=True,
                           sale_price=454.99)

    def test_sale_price_update_when_no_discount(self):
        """
            Tests that the sale price is updated correctly when discount is
            False sale price should be set to price.

            As sale price is used to sort on products page this test is
            important for ensuring product page sort capabilities work as
            expected.
        """

        print("Testing sale price update with no discount...")
        # Test product price prior to update to validate setup
        self.assertEqual(self.xbox.price, 549.86)
        self.assertEqual(self.xbox.sale_price, 399.99)
        # Call update sale price method
        self.xbox.update_sale_price()
        # Test that sale price is updated to price when discount is False
        self.assertEqual(self.xbox.price, 549.86)
        self.assertEqual(self.xbox.sale_price, 549.86)

    def test_sale_price_update_with_discount(self):
        """
            Tests that the sale price is updated correctly when discount is
            True sale price should remain unchanged

            As sale price is used to sort on products page this test is
            important for ensuring product page sort capabilities work as
            expected. But we also need to ensure that products that are on
            discount retain their sale price.
        """

        print("Testing sale price doesn't update during an active discount...")
        # Test product price prior to update to validate setup
        self.assertEqual(self.ps4.price, 649.64)
        self.assertEqual(self.ps4.sale_price, 454.99)
        # Call update sale price method
        self.ps4.update_sale_price()
        # Test that sale price is updated to price when discount is False
        self.assertEqual(self.ps4.price, 649.64)
        self.assertEqual(self.ps4.sale_price, 454.99)

    def test_when_product_is_in_stock(self):
        """
            Tests that is_in_stock function returns True when stock > 0.
        """
        print("Testing is_in_stock function when product is in stock...")
        # Test product stock value to validate setup
        self.assertEqual(self.xbox.stock, 1)
        # Test is_in_stock method correctly identifies product is in stock
        self.assertTrue(self.xbox.is_in_stock())
        # Test product stock value remains unchanged
        self.assertEqual(self.xbox.stock, 1)

    def test_when_product_is_out_of_stock(self):
        """
            Tests that is_in_stock function returns False when stock == 0.
        """
        print("Testing is_in_stock function when product is out of stock...")
        # Test product stock value to validate setup
        self.assertEqual(self.ps4.stock, 0)
        # Test is_in_stock method correctly identifies product is in stock
        self.assertFalse(self.ps4.is_in_stock())
        # Test product stock value remains unchanged
        self.assertEqual(self.ps4.stock, 0)

    def test_check_stock_when_product_is_in_stock(self):
        """
            Tests that check_stock doesn't update tagline when stock > 0.
        """
        print("Testing product is in stock and tagline remains unchanged...")
        # Test product price and tagline to update to validate setup
        self.assertEqual(self.xbox.stock, 1)
        self.assertEqual(self.xbox.tagline, "New")
        # Run check stock method
        self.xbox.check_stock()
        # Test product stock and tagline remains unchanged
        self.assertEqual(self.xbox.stock, 1)
        self.assertEqual(self.xbox.tagline, "New")

    def test_check_stock_when_product_is_out_of_stock(self):
        """
            Tests that check_stock updates tagline to Out of Stock when
            stock == 0.
        """
        print("Testing product is out of stock and tagline updates to \"Out " +
              "of Stock\"...")
        # Test product price and tagline to update to validate setup
        self.assertEqual(self.ps4.stock, 0)
        self.assertEqual(self.ps4.tagline, "While Stocks Last")
        # Run check stock method
        self.ps4.check_stock()
        # Test product stock remains unchanged and tagline is updated to
        # "Out of Stock"
        self.assertEqual(self.ps4.stock, 0)
        self.assertEqual(self.ps4.tagline, "Out of Stock")



User = get_user_model()

class U102LoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = "TestPass123!"
        self.user = User.objects.create_user(
            username="ayden",
            email="ayden@example.com",
            password=self.password,
            first_name="Ayden",
        )

    # U102-TC1: login page loads
    def test_login_page_renders(self):
        r = self.client.get(reverse("login"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Log in")

    # U102-TC2: successful login -> redirect to index
    def test_login_success_redirects_to_index(self):
        self.assertEqual(getattr(settings, "LOGIN_REDIRECT_URL", "/"), "/")
        r = self.client.post(reverse("login"), {
            "username": "ayden",
            "password": self.password,
            "next": "/",   # keep or omit; LOGIN_REDIRECT_URL = '/'
        })
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r["Location"], "/")

    # U102-TC3: navbar shows Account when authenticated
    def test_navbar_after_login(self):
        self.client.login(username="ayden", password=self.password)
        r = self.client.get(reverse("home"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'id="nav-account"')
        self.assertNotContains(r, 'id="nav-login"')

    # U102-TC4: negative credentials stay on login and show error
    def test_login_failure_shows_error(self):
        r = self.client.post(reverse("login"), {
            "username": "ayden",
            "password": "WrongPassword",
            "next": "/",
        })
        self.assertEqual(r.status_code, 200)  # stays on login page
        # Error message text depends on your template; assert something stable:
        self.assertContains(r, "try again", status_code=200)

    # U102-TC5: password reset page renders (R2 readiness)
    def test_password_reset_page_renders(self):
        r = self.client.get(reverse("password_reset"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Reset password")

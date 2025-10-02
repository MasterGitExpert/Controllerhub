from django.test import TestCase
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
        print("Testing product is in stock and tagline remains unchanged...")
        # Test product price and tagline to update to validate setup
        self.assertEqual(self.ps4.stock, 0)
        self.assertEqual(self.ps4.tagline, "While Stocks Last")
        # Run check stock method
        self.ps4.check_stock()
        # Test product stock remains unchanged and tagline is updated to
        # "Out of Stock"
        self.assertEqual(self.ps4.stock, 0)
        self.assertEqual(self.ps4.tagline, "Out of Stock")

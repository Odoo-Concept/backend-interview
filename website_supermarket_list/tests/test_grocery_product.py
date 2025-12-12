from odoo.tests import tagged
from odoo.tools import mute_logger

from .test_common import GroceryListTestCommon


@tagged("post_install", "-at_install")
class TestGroceryProduct(GroceryListTestCommon):
    def test_create_product_success(self):
        """Test creating a product with valid name"""
        product = self.env["grocery.product"].create(
            {
                "name": "Test Product",
                "active": True,
            }
        )
        self.assertTrue(product.id)
        self.assertEqual(product.name, "Test Product")
        self.assertTrue(product.active)

    @mute_logger("odoo.sql_db")
    def test_create_product_required_name(self):
        """Test that name is required"""
        # Required fields can raise different exceptions (ValueError, IntegrityError)
        with self.assertRaises((Exception, ValueError)):
            self.env["grocery.product"].create(
                {
                    "active": True,
                }
            )

    def test_create_product_with_category(self):
        """Test creating product with category"""
        product = self.env["grocery.product"].create(
            {
                "name": "Milk",
                "category": "Dairy",
                "active": True,
            }
        )
        self.assertEqual(product.category, "Dairy")

    def test_create_product_with_barcode(self):
        """Test creating product with barcode"""
        product = self.env["grocery.product"].create(
            {
                "name": "Product",
                "barcode": "123456789",
                "active": True,
            }
        )
        self.assertEqual(product.barcode, "123456789")

    def test_compute_usage_count(self):
        """Test computing usage count"""
        product = self.env["grocery.product"].create(
            {
                "name": "Test Product",
                "active": True,
            }
        )
        self.assertEqual(product.usage_count, 0)

        list1 = self.env["grocery.list"].create(
            {
                "name": "List 1",
                "store_id": self.store.id,
                "responsible_id": self.user_portal.id,
            }
        )
        self.env["grocery.list.line"].create(
            {
                "list_id": list1.id,
                "grocery_product_id": product.id,
                "quantity": 1.0,
            }
        )
        product._compute_usage_count()
        self.assertEqual(product.usage_count, 1)

        list2 = self.env["grocery.list"].create(
            {
                "name": "List 2",
                "store_id": self.store.id,
                "responsible_id": self.user_portal.id,
            }
        )
        self.env["grocery.list.line"].create(
            {
                "list_id": list2.id,
                "grocery_product_id": product.id,
                "quantity": 2.0,
            }
        )
        product._compute_usage_count()
        self.assertEqual(product.usage_count, 2)

    def test_compute_usage_count_zero(self):
        """Test usage count is 0 when product is not used"""
        product = self.env["grocery.product"].create(
            {
                "name": "Unused Product",
                "active": True,
            }
        )
        self.assertEqual(product.usage_count, 0)

    def test_compute_last_used_date(self):
        """Test computing last used date"""
        product = self.env["grocery.product"].create(
            {
                "name": "Test Product",
                "active": True,
            }
        )
        self.assertFalse(product.last_used_date)

        list1 = self.env["grocery.list"].create(
            {
                "name": "List 1",
                "store_id": self.store.id,
                "responsible_id": self.user_portal.id,
            }
        )
        self.env["grocery.list.line"].create(
            {
                "list_id": list1.id,
                "grocery_product_id": product.id,
                "quantity": 1.0,
            }
        )
        product._compute_last_used_date()
        self.assertTrue(product.last_used_date)
        self.assertEqual(product.last_used_date, list1.date_created)

    def test_compute_last_used_date_none(self):
        """Test last used date is False when product never used"""
        product = self.env["grocery.product"].create(
            {
                "name": "Unused Product",
                "active": True,
            }
        )
        self.assertFalse(product.last_used_date)

    def test_compute_has_real_product_true(self):
        """Test has_real_product when product is linked to Odoo product"""
        odoo_product = self.env["product.product"].create(
            {
                "name": "Odoo Product",
                "type": "consu",
            }
        )
        grocery_product = self.env["grocery.product"].create(
            {
                "name": "Grocery Product",
                "product_id": odoo_product.id,
                "active": True,
            }
        )
        grocery_product._compute_has_real_product()
        self.assertTrue(grocery_product.has_real_product)

    def test_compute_has_real_product_false(self):
        """Test has_real_product when product is not linked"""
        product = self.env["grocery.product"].create(
            {
                "name": "Test Product",
                "active": True,
            }
        )
        product._compute_has_real_product()
        self.assertFalse(product.has_real_product)

    def test_order_by_favorite_usage_name(self):
        """Test ordering by favorite, usage count, and name"""
        product1 = self.env["grocery.product"].create(
            {
                "name": "Z Order Test Product",
                "active": True,
            }
        )
        product2 = self.env["grocery.product"].create(
            {
                "name": "A Order Test Product",
                "is_favorite": True,
                "active": True,
            }
        )
        product3 = self.env["grocery.product"].create(
            {
                "name": "B Order Test Product",
                "active": True,
            }
        )
        list1 = self.env["grocery.list"].create(
            {
                "name": "Order Test List",
                "store_id": self.store.id,
                "responsible_id": self.user_portal.id,
            }
        )
        self.env["grocery.list.line"].create(
            {
                "list_id": list1.id,
                "grocery_product_id": product3.id,
                "quantity": 1.0,
            }
        )
        product3._compute_usage_count()

        products = self.env["grocery.product"].search(
            [("name", "like", "Order Test Product")],
            order="is_favorite desc, usage_count desc, name",
        )
        self.assertEqual(products[0].id, product2.id)
        self.assertEqual(products[1].id, product3.id)
        self.assertEqual(products[2].id, product1.id)

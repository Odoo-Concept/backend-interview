from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tools import mute_logger

from .test_common import GroceryListTestCommon


@tagged("post_install", "-at_install")
class TestGroceryStore(GroceryListTestCommon):
    def test_create_store_success(self):
        """Test creating a store with valid name"""
        store = self.env["grocery.store"].create(
            {
                "name": "Walmart Test Store",
                "active": True,
            }
        )
        self.assertTrue(store.id)
        self.assertEqual(store.name, "Walmart Test Store")
        self.assertTrue(store.active)
        self.assertTrue(store.name_normalized)

    @mute_logger("odoo.sql_db")
    def test_create_store_required_name(self):
        """Test that name is required"""
        # Required fields can raise different exceptions (ValueError, IntegrityError)
        with self.assertRaises((Exception, ValueError)):
            self.env["grocery.store"].create(
                {
                    "active": True,
                }
            )

    def test_create_store_name_normalized(self):
        """Test that name is normalized correctly"""
        store = self.env["grocery.store"].create(
            {
                "name": "  Test Store Normalized  ",
                "active": True,
            }
        )
        self.assertEqual(store.name, "  Test Store Normalized  ")
        self.assertEqual(store.name_normalized, "test store normalized")

    def test_create_store_duplicate_name(self):
        """Test that duplicate stores (same normalized name) cannot be created"""
        self.env["grocery.store"].create(
            {
                "name": "Duplicate Store Test",
                "active": True,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["grocery.store"].create(
                {
                    "name": "duplicate store test",
                    "active": True,
                }
            )

    def test_create_store_normalize_accents(self):
        """Test normalization of accents"""
        self.env["grocery.store"].create(
            {
                "name": "Café",
                "active": True,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["grocery.store"].create(
                {
                    "name": "Cafe",
                    "active": True,
                }
            )

    def test_create_store_normalize_special_chars(self):
        """Test normalization removes special characters"""
        store = self.env["grocery.store"].create(
            {
                "name": "Store & Co.",
                "active": True,
            }
        )
        self.assertNotIn("&", store.name_normalized)
        self.assertNotIn(".", store.name_normalized)

    def test_create_store_normalize_spaces(self):
        """Test normalization of multiple spaces"""
        store = self.env["grocery.store"].create(
            {
                "name": "Store   Name",
                "active": True,
            }
        )
        self.assertNotIn("   ", store.name_normalized)

    def test_create_store_case_insensitive(self):
        """Test that 'Walmart' and 'walmart' are considered duplicates"""
        self.env["grocery.store"].create(
            {
                "name": "Case Insensitive Store",
                "active": True,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["grocery.store"].create(
                {
                    "name": "CASE INSENSITIVE STORE",
                    "active": True,
                }
            )

    def test_write_store_name(self):
        """Test updating store name"""
        store = self.env["grocery.store"].create(
            {
                "name": "Old Name Test",
                "active": True,
            }
        )
        store.write({"name": "New Name Test"})
        self.assertEqual(store.name, "New Name Test")
        self.assertEqual(store.name_normalized, "new name test")

    def test_write_store_duplicate_name(self):
        """Test that updating to duplicate name is not allowed"""
        self.env["grocery.store"].create(
            {
                "name": "Store 1",
                "active": True,
            }
        )
        store2 = self.env["grocery.store"].create(
            {
                "name": "Store 2",
                "active": True,
            }
        )
        with self.assertRaises(ValidationError):
            store2.write({"name": "Store 1"})

    def test_find_or_create_existing(self):
        """Test finding existing store"""
        existing = self.env["grocery.store"].create(
            {
                "name": "Find Or Create Store",
                "active": True,
            }
        )
        found = self.env["grocery.store"].find_or_create("Find Or Create Store")
        self.assertEqual(found.id, existing.id)

    def test_find_or_create_new(self):
        """Test creating new store if not found"""
        count_before = self.env["grocery.store"].search_count([])
        new_store = self.env["grocery.store"].find_or_create("New Store")
        count_after = self.env["grocery.store"].search_count([])
        self.assertEqual(count_after, count_before + 1)
        self.assertEqual(new_store.name, "New Store")

    def test_find_or_create_empty_name(self):
        """Test that empty name returns empty recordset"""
        result = self.env["grocery.store"].find_or_create("")
        self.assertFalse(result)

    def test_find_or_create_case_insensitive(self):
        """Test finding store case-insensitively"""
        existing = self.env["grocery.store"].create(
            {
                "name": "Case Insensitive Find",
                "active": True,
            }
        )
        found = self.env["grocery.store"].find_or_create("case insensitive find")
        self.assertEqual(found.id, existing.id)

    def test_compute_total_lists(self):
        """Test computing total lists for a store"""
        store = self.env["grocery.store"].create(
            {
                "name": "Total Lists Test Store",
                "active": True,
            }
        )
        self.env["grocery.list"].create(
            {
                "name": "List 1",
                "store_id": store.id,
                "responsible_id": self.user_portal.id,
            }
        )
        self.env["grocery.list"].create(
            {
                "name": "List 2",
                "store_id": store.id,
                "responsible_id": self.user_portal.id,
            }
        )
        store._compute_total_lists()
        self.assertEqual(store.total_lists, 2)

    def test_compute_total_lists_no_lists(self):
        """Test computing total lists when store has no lists"""
        store = self.env["grocery.store"].create(
            {
                "name": "Empty Store",
                "active": True,
            }
        )
        store._compute_total_lists()
        self.assertEqual(store.total_lists, 0)

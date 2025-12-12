from psycopg2.errors import NotNullViolation

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tools import mute_logger

from .test_common import GroceryListTestCommon


@tagged("post_install", "-at_install")
class TestGroceryList(GroceryListTestCommon):
    def test_create_list_success(self):
        """Test creating a list with valid data"""
        list_record = self.env["grocery.list"].create(
            {
                "name": "Weekly Shopping",
                "store_id": self.store.id,
                "responsible_id": self.user_portal.id,
                "state": "draft",
            }
        )
        self.assertTrue(list_record.id)
        self.assertEqual(list_record.name, "Weekly Shopping")
        self.assertEqual(list_record.state, "draft")
        self.assertTrue(list_record.active)

    @mute_logger("odoo.sql_db")
    def test_create_list_required_name(self):
        """Test that name is required"""
        with self.assertRaises(NotNullViolation):
            self.env["grocery.list"].create(
                {
                    "store_id": self.store.id,
                    "responsible_id": self.user_portal.id,
                }
            )

    @mute_logger("odoo.sql_db")
    def test_create_list_required_store(self):
        """Test that store is required"""
        with self.assertRaises(NotNullViolation):
            self.env["grocery.list"].create(
                {
                    "name": "Test List",
                    "responsible_id": self.user_portal.id,
                }
            )

    def test_create_list_default_responsible(self):
        """Test that responsible defaults to current user"""
        list_record = (
            self.env["grocery.list"]
            .with_user(self.user_portal)
            .create(
                {
                    "name": "Test List",
                    "store_id": self.store.id,
                }
            )
        )
        self.assertEqual(list_record.responsible_id.id, self.user_portal.id)

    def test_create_list_default_state_draft(self):
        """Test that default state is draft"""
        list_record = self.env["grocery.list"].create(
            {
                "name": "Test List",
                "store_id": self.store.id,
                "responsible_id": self.user_portal.id,
            }
        )
        self.assertEqual(list_record.state, "draft")

    def test_create_list_default_active(self):
        """Test that active defaults to True"""
        list_record = self.env["grocery.list"].create(
            {
                "name": "Test List",
                "store_id": self.store.id,
                "responsible_id": self.user_portal.id,
            }
        )
        self.assertTrue(list_record.active)

    def test_compute_totals_empty_list(self):
        """Test computing totals for empty list"""
        list_record = self.env["grocery.list"].create(
            {
                "name": "Empty List",
                "store_id": self.store.id,
                "responsible_id": self.user_portal.id,
            }
        )
        list_record._compute_totals()
        self.assertEqual(list_record.total_items, 0)
        self.assertEqual(list_record.purchased_items, 0)
        self.assertEqual(list_record.pending_items, 0)
        self.assertEqual(list_record.progress, 0.0)

    def test_compute_totals_with_items(self):
        """Test computing totals with items"""
        list_record = self.env["grocery.list"].create(
            {
                "name": "Test List",
                "store_id": self.store.id,
                "responsible_id": self.user_portal.id,
            }
        )
        self.env["grocery.list.line"].create(
            {
                "list_id": list_record.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
                "is_purchased": False,
            }
        )
        self.env["grocery.list.line"].create(
            {
                "list_id": list_record.id,
                "grocery_product_id": self.product2.id,
                "quantity": 2.0,
                "is_purchased": True,
            }
        )
        list_record._compute_totals()
        self.assertEqual(list_record.total_items, 2)
        self.assertEqual(list_record.purchased_items, 1)
        self.assertEqual(list_record.pending_items, 1)
        self.assertEqual(list_record.progress, 50.0)

    def test_compute_totals_all_purchased(self):
        """Test computing totals when all items are purchased"""
        list_record = self.env["grocery.list"].create(
            {
                "name": "Test List",
                "store_id": self.store.id,
                "responsible_id": self.user_portal.id,
            }
        )
        self.env["grocery.list.line"].create(
            {
                "list_id": list_record.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
                "is_purchased": True,
            }
        )
        self.env["grocery.list.line"].create(
            {
                "list_id": list_record.id,
                "grocery_product_id": self.product2.id,
                "quantity": 2.0,
                "is_purchased": True,
            }
        )
        list_record._compute_totals()
        self.assertEqual(list_record.total_items, 2)
        self.assertEqual(list_record.purchased_items, 2)
        self.assertEqual(list_record.pending_items, 0)
        self.assertEqual(list_record.progress, 100.0)

    def test_compute_totals_no_purchased(self):
        """Test computing totals when no items are purchased"""
        list_record = self.env["grocery.list"].create(
            {
                "name": "Test List",
                "store_id": self.store.id,
                "responsible_id": self.user_portal.id,
            }
        )
        self.env["grocery.list.line"].create(
            {
                "list_id": list_record.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
                "is_purchased": False,
            }
        )
        list_record._compute_totals()
        self.assertEqual(list_record.total_items, 1)
        self.assertEqual(list_record.purchased_items, 0)
        self.assertEqual(list_record.pending_items, 1)
        self.assertEqual(list_record.progress, 0.0)

    def test_action_set_in_progress_success(self):
        """Test setting list to in_progress with items"""
        list_record = self.env["grocery.list"].create(
            {
                "name": "Test List",
                "store_id": self.store.id,
                "responsible_id": self.user_portal.id,
            }
        )
        self.env["grocery.list.line"].create(
            {
                "list_id": list_record.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
            }
        )
        list_record.action_set_in_progress()
        self.assertEqual(list_record.state, "in_progress")
        self.assertTrue(list_record.date_started)

    def test_action_set_in_progress_empty_list(self):
        """Test that empty list cannot be set to in_progress"""
        list_record = self.env["grocery.list"].create(
            {
                "name": "Empty List",
                "store_id": self.store.id,
                "responsible_id": self.user_portal.id,
            }
        )
        with self.assertRaises(UserError):
            list_record.action_set_in_progress()

    def test_action_set_in_progress_sets_date_started(self):
        """Test that date_started is set when starting"""
        list_record = self.env["grocery.list"].create(
            {
                "name": "Test List",
                "store_id": self.store.id,
                "responsible_id": self.user_portal.id,
            }
        )
        self.env["grocery.list.line"].create(
            {
                "list_id": list_record.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
            }
        )
        self.assertFalse(list_record.date_started)
        list_record.action_set_in_progress()
        self.assertTrue(list_record.date_started)

    def test_action_set_done_success(self):
        """Test setting list to done when all items are purchased"""
        list_record = self.env["grocery.list"].create(
            {
                "name": "Test List",
                "store_id": self.store.id,
                "responsible_id": self.user_portal.id,
            }
        )
        self.env["grocery.list.line"].create(
            {
                "list_id": list_record.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
                "is_purchased": True,
            }
        )
        list_record.action_set_done()
        self.assertEqual(list_record.state, "done")
        self.assertTrue(list_record.date_completed)

    def test_action_set_done_with_pending(self):
        """Test that list cannot be set to done with pending items"""
        list_record = self.env["grocery.list"].create(
            {
                "name": "Test List",
                "store_id": self.store.id,
                "responsible_id": self.user_portal.id,
            }
        )
        self.env["grocery.list.line"].create(
            {
                "list_id": list_record.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
                "is_purchased": False,
            }
        )
        with self.assertRaises(UserError):
            list_record.action_set_done()

    def test_action_set_done_sets_date_completed(self):
        """Test that date_completed is set when completing"""
        list_record = self.env["grocery.list"].create(
            {
                "name": "Test List",
                "store_id": self.store.id,
                "responsible_id": self.user_portal.id,
            }
        )
        self.env["grocery.list.line"].create(
            {
                "list_id": list_record.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
                "is_purchased": True,
            }
        )
        self.assertFalse(list_record.date_completed)
        list_record.action_set_done()
        self.assertTrue(list_record.date_completed)

    def test_constraint_completed_state_with_pending(self):
        """Test constraint prevents completing with pending items"""
        list_record = self.env["grocery.list"].create(
            {
                "name": "Test List",
                "store_id": self.store.id,
                "responsible_id": self.user_portal.id,
            }
        )
        self.env["grocery.list.line"].create(
            {
                "list_id": list_record.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
                "is_purchased": False,
            }
        )
        with self.assertRaises(ValidationError):
            list_record.write({"state": "done"})

    def test_constraint_completed_state_all_purchased(self):
        """Test constraint allows completing when all items are purchased"""
        list_record = self.env["grocery.list"].create(
            {
                "name": "Test List",
                "store_id": self.store.id,
                "responsible_id": self.user_portal.id,
            }
        )
        self.env["grocery.list.line"].create(
            {
                "list_id": list_record.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
                "is_purchased": True,
            }
        )
        list_record.write({"state": "done"})
        self.assertEqual(list_record.state, "done")

    def test_list_copy_with_lines(self):
        """Test that lines are copied when duplicating list"""
        list_record = self.env["grocery.list"].create(
            {
                "name": "Test List",
                "store_id": self.store.id,
                "responsible_id": self.user_portal.id,
            }
        )
        self.env["grocery.list.line"].create(
            {
                "list_id": list_record.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
            }
        )
        self.env["grocery.list.line"].create(
            {
                "list_id": list_record.id,
                "grocery_product_id": self.product2.id,
                "quantity": 2.0,
            }
        )
        copied_list = list_record.copy()
        self.assertEqual(len(copied_list.line_ids), 2)
        self.assertNotEqual(copied_list.id, list_record.id)

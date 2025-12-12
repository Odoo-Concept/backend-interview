from odoo.tests import tagged

from .test_common import GroceryListTestCommon


@tagged("post_install", "-at_install")
class TestGroceryListIntegrationFlows(GroceryListTestCommon):
    def test_integration_create_list_flow(self):
        """Test complete flow: create store, list, add products, start,
        mark purchased, complete"""
        store = self.env["grocery.store"].find_or_create("Integration Store")
        self.assertTrue(store.id)

        list_record = self.env["grocery.list"].create(
            {
                "name": "Integration Test List",
                "store_id": store.id,
                "responsible_id": self.user_portal.id,
                "state": "draft",
            }
        )
        self.assertEqual(list_record.state, "draft")

        line1 = self.env["grocery.list.line"].create(
            {
                "list_id": list_record.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
            }
        )
        line2 = self.env["grocery.list.line"].create(
            {
                "list_id": list_record.id,
                "grocery_product_id": self.product2.id,
                "quantity": 2.0,
            }
        )
        self.assertEqual(list_record.total_items, 2)
        self.assertEqual(list_record.pending_items, 2)

        list_record.action_set_in_progress()
        self.assertEqual(list_record.state, "in_progress")
        self.assertTrue(list_record.date_started)

        line1.write({"is_purchased": True})
        list_record._compute_totals()
        self.assertEqual(list_record.purchased_items, 1)
        self.assertEqual(list_record.pending_items, 1)

        line2.write({"is_purchased": True})
        list_record._compute_totals()
        self.assertEqual(list_record.purchased_items, 2)
        self.assertEqual(list_record.pending_items, 0)
        self.assertEqual(list_record.progress, 100.0)

        list_record.action_set_done()
        self.assertEqual(list_record.state, "done")
        self.assertTrue(list_record.date_completed)

    def test_integration_search_products_flow(self):
        """Test product search and usage tracking"""
        product1 = self.env["grocery.product"].create(
            {
                "name": "Apple",
                "category": "Fruits",
                "is_favorite": True,
                "active": True,
            }
        )
        product2 = self.env["grocery.product"].create(
            {
                "name": "Banana",
                "category": "Fruits",
                "active": True,
            }
        )
        product3 = self.env["grocery.product"].create(
            {
                "name": "Orange",
                "category": "Fruits",
                "active": True,
            }
        )

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
                "grocery_product_id": product1.id,
                "quantity": 1.0,
            }
        )
        self.env["grocery.list.line"].create(
            {
                "list_id": list1.id,
                "grocery_product_id": product2.id,
                "quantity": 2.0,
            }
        )

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
                "grocery_product_id": product1.id,
                "quantity": 3.0,
            }
        )

        product1._compute_usage_count()
        product2._compute_usage_count()
        product3._compute_usage_count()
        self.assertEqual(product1.usage_count, 2)
        self.assertEqual(product2.usage_count, 1)
        self.assertEqual(product3.usage_count, 0)

        products = self.env["grocery.product"].search(
            [
                ("category", "=", "Fruits"),
            ],
            order="is_favorite desc, usage_count desc, name",
        )
        self.assertEqual(products[0].id, product1.id)

    def test_integration_list_state_transitions(self):
        """Test complete state transition flow"""
        list_record = self.env["grocery.list"].create(
            {
                "name": "State Test List",
                "store_id": self.store.id,
                "responsible_id": self.user_portal.id,
                "state": "draft",
            }
        )

        line1 = self.env["grocery.list.line"].create(
            {
                "list_id": list_record.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
            }
        )
        line2 = self.env["grocery.list.line"].create(
            {
                "list_id": list_record.id,
                "grocery_product_id": self.product2.id,
                "quantity": 1.0,
            }
        )

        list_record.action_set_in_progress()
        self.assertEqual(list_record.state, "in_progress")
        self.assertTrue(list_record.date_started)

        from odoo.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            list_record.action_set_done()

        line1.write({"is_purchased": True})
        line2.write({"is_purchased": True})
        list_record._compute_totals()

        list_record.action_set_done()
        self.assertEqual(list_record.state, "done")
        self.assertTrue(list_record.date_completed)

    def test_integration_product_usage_tracking(self):
        """Test product usage tracking across multiple lists"""
        product = self.env["grocery.product"].create(
            {
                "name": "Tracking Product",
                "active": True,
            }
        )

        for i in range(5):
            list_record = self.env["grocery.list"].create(
                {
                    "name": f"List {i}",
                    "store_id": self.store.id,
                    "responsible_id": self.user_portal.id,
                }
            )
            self.env["grocery.list.line"].create(
                {
                    "list_id": list_record.id,
                    "grocery_product_id": product.id,
                    "quantity": 1.0,
                }
            )

        product._compute_usage_count()
        self.assertEqual(product.usage_count, 5)

        product._compute_last_used_date()
        self.assertTrue(product.last_used_date)

        product.write({"is_favorite": True})
        self.assertTrue(product.is_favorite)

    def test_integration_store_find_or_create(self):
        """Test store find_or_create in integration scenario"""
        store1 = self.env["grocery.store"].find_or_create("Integration Test Store")
        store2 = self.env["grocery.store"].find_or_create("integration test store")
        store3 = self.env["grocery.store"].find_or_create("INTEGRATION TEST STORE")

        self.assertEqual(store1.id, store2.id)
        self.assertEqual(store2.id, store3.id)

        self.env["grocery.list"].create(
            {
                "name": "Integration Find Create List",
                "store_id": store1.id,
                "responsible_id": self.user_portal.id,
            }
        )

        store1._compute_total_lists()
        actual_count = self.env["grocery.list"].search_count(
            [
                ("store_id", "=", store1.id),
                ("name", "=", "Integration Find Create List"),
            ]
        )
        self.assertEqual(actual_count, 1)

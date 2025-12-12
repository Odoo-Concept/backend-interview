import json

from odoo.http import Request
from odoo.tests import tagged

from .test_common import GroceryListHttpCase


@tagged("post_install", "-at_install")
class TestGroceryListControllers(GroceryListHttpCase):
    def test_route_portal_my_grocery_lists(self):
        """Test listing user's grocery lists"""
        self.authenticate("portal_user", "portal_user")
        response = self.url_open("/my/grocery-lists")
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.grocery_list.name.encode(), response.content)

    def test_route_portal_my_grocery_lists_search(self):
        """Test searching lists by name and store"""
        self.authenticate("portal_user", "portal_user")
        response = self.url_open("/my/grocery-lists?search=Test")
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.grocery_list.name.encode(), response.content)

    def test_route_portal_my_grocery_lists_filter(self):
        """Test filtering lists by state"""
        self.authenticate("portal_user", "portal_user")
        response = self.url_open("/my/grocery-lists?filterby=draft")
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.grocery_list.name.encode(), response.content)

    def test_route_portal_grocery_list_new_get(self):
        """Test showing new list form"""
        self.authenticate("portal_user", "portal_user")
        response = self.url_open("/my/grocery-lists/new")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Create New Grocery List", response.content)

    def test_route_portal_grocery_list_new_post_success(self):
        """Test creating new list via POST"""
        self.authenticate("portal_user", "portal_user")
        response = self.url_open(
            "/my/grocery-lists/new",
            data={
                "list_name": "New Test List",
                "store_name": "New Store",
                "csrf_token": Request.csrf_token(self),
            },
        )
        self.assertEqual(response.status_code, 200)
        new_list = self.env["grocery.list"].search(
            [
                ("name", "=", "New Test List"),
                ("responsible_id", "=", self.user_portal.id),
            ]
        )
        self.assertTrue(new_list)

    def test_route_portal_grocery_list_new_post_missing_name(self):
        """Test error when list name is missing"""
        self.authenticate("portal_user", "portal_user")
        response = self.url_open(
            "/my/grocery-lists/new",
            data={
                "store_name": "Test Store",
                "csrf_token": Request.csrf_token(self),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please provide a name for your list", response.content)

    def test_route_portal_grocery_list_view(self):
        """Test viewing a list"""
        self.authenticate("portal_user", "portal_user")
        response = self.url_open(f"/my/grocery-lists/{self.grocery_list.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.grocery_list.name.encode(), response.content)

    def test_route_portal_grocery_list_view_access_denied(self):
        """Test that only responsible user can view list"""
        self.authenticate("portal_user2", "portal_user2")
        response = self.url_open(f"/my/grocery-lists/{self.grocery_list.id}")
        self.assertIn(response.status_code, [200, 302, 403])
        if response.status_code == 302:
            self.assertIn("/my/grocery-lists", response.headers.get("Location", ""))
        elif response.status_code == 200:
            self.assertNotIn(self.grocery_list.name.encode(), response.content)

    def test_route_portal_grocery_list_action_set_in_progress(self):
        """Test setting list to in_progress"""
        self.env["grocery.list.line"].create(
            {
                "list_id": self.grocery_list.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
            }
        )
        self.authenticate("portal_user", "portal_user")
        response = self.url_open(
            f"/my/grocery-lists/{self.grocery_list.id}/action",
            data={
                "action": "set_in_progress",
                "mode": "view",
                "csrf_token": Request.csrf_token(self),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.grocery_list = self.env["grocery.list"].browse(self.grocery_list.id)
        self.assertEqual(self.grocery_list.state, "in_progress")

    def test_route_portal_grocery_list_action_set_done(self):
        """Test setting list to done"""
        self.env["grocery.list.line"].create(
            {
                "list_id": self.grocery_list.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
                "is_purchased": True,
            }
        )
        self.grocery_list.action_set_in_progress()
        self.authenticate("portal_user", "portal_user")
        response = self.url_open(
            f"/my/grocery-lists/{self.grocery_list.id}/action",
            data={
                "action": "set_done",
                "mode": "view",
                "csrf_token": Request.csrf_token(self),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.grocery_list = self.env["grocery.list"].browse(self.grocery_list.id)
        self.assertEqual(self.grocery_list.state, "done")

    def test_route_portal_grocery_list_add_product_success(self):
        """Test adding product to list"""
        self.authenticate("portal_user", "portal_user")
        response = self.url_open(
            f"/my/grocery-lists/{self.grocery_list.id}/add-product",
            data={
                "product_id": self.product1.id,
                "quantity": 2.0,
                "csrf_token": Request.csrf_token(self),
            },
        )
        self.assertEqual(response.status_code, 200)
        line = self.env["grocery.list.line"].search(
            [
                ("list_id", "=", self.grocery_list.id),
                ("grocery_product_id", "=", self.product1.id),
            ]
        )
        self.assertTrue(line)
        self.assertEqual(line.quantity, 2.0)

    def test_route_portal_grocery_list_add_product_missing_product(self):
        """Test error when product is missing"""
        self.authenticate("portal_user", "portal_user")
        response = self.url_open(
            f"/my/grocery-lists/{self.grocery_list.id}/add-product",
            data={
                "quantity": 1.0,
                "csrf_token": Request.csrf_token(self),
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_route_portal_grocery_list_delete_line_success(self):
        """Test deleting a line"""
        line = self.env["grocery.list.line"].create(
            {
                "list_id": self.grocery_list.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
            }
        )
        line_id = line.id
        self.authenticate("portal_user", "portal_user")
        response = self.url_open(
            f"/my/grocery-lists/{self.grocery_list.id}/delete-line",
            data={
                "line_id": line_id,
                "mode": "edit",
                "csrf_token": Request.csrf_token(self),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.env["grocery.list.line"].browse(line_id).exists())

    def test_route_toggle_purchased_success(self):
        """Test toggling purchased status via JSON"""
        line = self.env["grocery.list.line"].create(
            {
                "list_id": self.grocery_list.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
                "is_purchased": False,
            }
        )
        self.grocery_list.action_set_in_progress()
        self.authenticate("portal_user", "portal_user")
        response = self.url_open(
            f"/my/grocery-lists/{self.grocery_list.id}/toggle-purchased",
            data=json.dumps(
                {
                    "params": {
                        "list_id": self.grocery_list.id,
                        "line_id": line.id,
                    }
                }
            ),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertTrue(result.get("result", {}).get("success"))
        line = self.env["grocery.list.line"].browse(line.id)
        self.assertTrue(line.is_purchased)

    def test_route_search_products_success(self):
        """Test searching products via JSON"""
        self.authenticate("portal_user", "portal_user")
        response = self.url_open(
            "/grocery/search-products",
            data=json.dumps(
                {
                    "params": {
                        "term": "Milk",
                        "limit": 20,
                    }
                }
            ),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        products = result.get("result", {}).get("products", [])
        self.assertTrue(len(products) > 0)
        product_names = [p["name"] for p in products]
        self.assertIn("Milk", product_names)

    def test_route_search_products_empty_term(self):
        """Test that empty term returns empty results"""
        self.authenticate("portal_user", "portal_user")
        response = self.url_open(
            "/grocery/search-products",
            data=json.dumps(
                {
                    "params": {
                        "term": "",
                        "limit": 20,
                    }
                }
            ),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        products = result.get("result", {}).get("products", [])
        self.assertEqual(len(products), 0)

    def test_route_search_stores_success(self):
        """Test searching stores via JSON"""
        self.authenticate("portal_user", "portal_user")
        response = self.url_open(
            "/grocery/search-stores",
            data=json.dumps(
                {
                    "params": {
                        "term": "Test",
                        "limit": 20,
                    }
                }
            ),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        stores = result.get("result", {}).get("stores", [])
        self.assertTrue(len(stores) > 0)
        store_names = [s["name"] for s in stores]
        self.assertIn("Test Store", store_names)

    def test_route_create_product_success(self):
        """Test creating product via JSON"""
        self.authenticate("portal_user", "portal_user")
        response = self.url_open(
            "/grocery/create-product",
            data=json.dumps(
                {
                    "params": {
                        "name": "New Product",
                        "category": "Test Category",
                    }
                }
            ),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertTrue(result.get("result", {}).get("success"))
        product = self.env["grocery.product"].search(
            [
                ("name", "=", "New Product"),
            ]
        )
        self.assertTrue(product)

    def test_route_create_product_missing_name(self):
        """Test error when product name is missing"""
        self.authenticate("portal_user", "portal_user")
        response = self.url_open(
            "/grocery/create-product",
            data=json.dumps(
                {
                    "params": {
                        "name": "",
                        "category": "Test Category",
                    }
                }
            ),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertTrue(result.get("result", {}).get("error"))

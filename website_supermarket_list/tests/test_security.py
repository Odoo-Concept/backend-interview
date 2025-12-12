from odoo.exceptions import AccessError
from odoo.tests import tagged

from .test_common import GroceryListTestCommon


@tagged("post_install", "-at_install")
class TestGroceryListSecurity(GroceryListTestCommon):
    def test_only_responsible_can_modify_list(self):
        """Test that only responsible user can modify list"""
        other_user = self.env["res.users"].create(
            {
                "name": "Other User",
                "login": "other_user",
                "groups_id": [(6, 0, [self.env.ref("base.group_portal").id])],
            }
        )

        with self.assertRaises(AccessError):
            self.grocery_list.with_user(other_user).write(
                {
                    "name": "Modified Name",
                }
            )

        self.grocery_list.with_user(self.user_portal).write(
            {
                "name": "Modified Name",
            }
        )
        self.assertEqual(self.grocery_list.name, "Modified Name")

    def test_only_responsible_can_mark_purchased(self):
        """Test that only responsible user can mark items as purchased"""
        line = self.env["grocery.list.line"].create(
            {
                "list_id": self.grocery_list.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
            }
        )

        other_user = self.env["res.users"].create(
            {
                "name": "Other User",
                "login": "other_user",
                "groups_id": [(6, 0, [self.env.ref("base.group_portal").id])],
            }
        )

        # AccessError is raised first due to record rules, before constraint validation
        with self.assertRaises(AccessError):
            line.with_user(other_user).write({"is_purchased": True})

        line.with_user(self.user_portal).write({"is_purchased": True})
        self.assertTrue(line.is_purchased)

    def test_only_responsible_can_change_state(self):
        """Test that only responsible user can change list state"""
        self.env["grocery.list.line"].create(
            {
                "list_id": self.grocery_list.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
            }
        )

        other_user = self.env["res.users"].create(
            {
                "name": "Other User",
                "login": "other_user",
                "groups_id": [(6, 0, [self.env.ref("base.group_portal").id])],
            }
        )

        with self.assertRaises(AccessError):
            self.grocery_list.with_user(other_user).action_set_in_progress()

        self.grocery_list.with_user(self.user_portal).action_set_in_progress()
        self.assertEqual(self.grocery_list.state, "in_progress")

    def test_only_responsible_can_add_products(self):
        """Test that only responsible user can add products to list"""
        other_user = self.env["res.users"].create(
            {
                "name": "Other User",
                "login": "other_user",
                "groups_id": [(6, 0, [self.env.ref("base.group_portal").id])],
            }
        )

        with self.assertRaises(AccessError):
            self.env["grocery.list.line"].with_user(other_user).create(
                {
                    "list_id": self.grocery_list.id,
                    "grocery_product_id": self.product1.id,
                    "quantity": 1.0,
                }
            )

        line = (
            self.env["grocery.list.line"]
            .with_user(self.user_portal)
            .create(
                {
                    "list_id": self.grocery_list.id,
                    "grocery_product_id": self.product1.id,
                    "quantity": 1.0,
                }
            )
        )
        self.assertTrue(line.id)

    def test_only_responsible_can_delete_lines(self):
        """Test that only responsible user can delete lines"""
        line = self.env["grocery.list.line"].create(
            {
                "list_id": self.grocery_list.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
            }
        )

        other_user = self.env["res.users"].create(
            {
                "name": "Other User",
                "login": "other_user",
                "groups_id": [(6, 0, [self.env.ref("base.group_portal").id])],
            }
        )

        with self.assertRaises(AccessError):
            line.with_user(other_user).unlink()

        line.with_user(self.user_portal).unlink()
        self.assertFalse(line.exists())

    def test_only_admin_can_link_real_product(self):
        """Test that only admin can link real Odoo product"""
        odoo_product = self.env["product.product"].create(
            {
                "name": "Odoo Product",
                "type": "consu",
            }
        )

        grocery_product = self.env["grocery.product"].create(
            {
                "name": "Grocery Product",
                "active": True,
            }
        )
        with self.assertRaises(AccessError):
            grocery_product.with_user(self.user_portal).write(
                {
                    "product_id": odoo_product.id,
                }
            )

        grocery_product.sudo().write(
            {
                "product_id": odoo_product.id,
            }
        )
        self.assertEqual(grocery_product.product_id.id, odoo_product.id)

    def test_portal_user_cannot_link_real_product(self):
        """Test that portal user cannot link real product even if they try"""
        odoo_product = self.env["product.product"].create(
            {
                "name": "Odoo Product",
                "type": "consu",
            }
        )

        grocery_product = (
            self.env["grocery.product"]
            .with_user(self.user_portal)
            .create(
                {
                    "name": "Grocery Product",
                    "active": True,
                }
            )
        )

        with self.assertRaises(AccessError):
            grocery_product.with_user(self.user_portal).write(
                {"product_id": odoo_product.id}
            )

from odoo.exceptions import ValidationError, AccessError
from odoo.tests import tagged
from odoo.tools import mute_logger

from .test_common import GroceryListTestCommon


@tagged("post_install", "-at_install")
class TestGroceryListLine(GroceryListTestCommon):
    def test_create_line_success(self):
        """Test creating a line with valid data"""
        line = self.env["grocery.list.line"].create(
            {
                "list_id": self.grocery_list.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
            }
        )
        self.assertTrue(line.id)
        self.assertEqual(line.quantity, 1.0)
        self.assertFalse(line.is_purchased)

    @mute_logger("odoo.sql_db")
    def test_create_line_required_list(self):
        """Test that list_id is required"""
        # Required fields can raise different exceptions (ValueError, IntegrityError)
        with self.assertRaises(Exception):
            self.env["grocery.list.line"].create(
                {
                    "grocery_product_id": self.product1.id,
                    "quantity": 1.0,
                }
            )

    @mute_logger("odoo.sql_db")
    def test_create_line_required_product(self):
        """Test that grocery_product_id is required"""
        # Required fields can raise different exceptions (ValueError, IntegrityError)
        with self.assertRaises(Exception):
            self.env["grocery.list.line"].create(
                {
                    "list_id": self.grocery_list.id,
                    "quantity": 1.0,
                }
            )

    def test_create_line_default_quantity(self):
        """Test that quantity defaults to 1.0"""
        line = self.env["grocery.list.line"].create(
            {
                "list_id": self.grocery_list.id,
                "grocery_product_id": self.product1.id,
            }
        )
        self.assertEqual(line.quantity, 1.0)

    def test_create_line_default_is_purchased(self):
        """Test that is_purchased defaults to False"""
        line = self.env["grocery.list.line"].create(
            {
                "list_id": self.grocery_list.id,
                "grocery_product_id": self.product1.id,
            }
        )
        self.assertFalse(line.is_purchased)

    def test_create_line_default_sequence(self):
        """Test that sequence defaults to 10"""
        line = self.env["grocery.list.line"].create(
            {
                "list_id": self.grocery_list.id,
                "grocery_product_id": self.product1.id,
            }
        )
        self.assertEqual(line.sequence, 10)

    def test_compute_uom_id_from_product(self):
        """Test that UOM is computed from linked Odoo product"""
        uom_kg = self.env.ref("uom.product_uom_kgm")
        odoo_product = self.env["product.product"].create(
            {
                "name": "Odoo Product",
                "type": "consu",
                "uom_id": uom_kg.id,
            }
        )
        grocery_product = self.env["grocery.product"].create(
            {
                "name": "Grocery Product",
                "product_id": odoo_product.id,
                "active": True,
            }
        )
        line = self.env["grocery.list.line"].create(
            {
                "list_id": self.grocery_list.id,
                "grocery_product_id": grocery_product.id,
                "quantity": 1.0,
            }
        )
        line._compute_uom_id()
        self.assertEqual(line.uom_id.id, uom_kg.id)

    def test_compute_uom_id_default(self):
        """Test that default UOM (Units) is used if no product linked"""
        uom_unit = self.env.ref("uom.product_uom_unit")
        line = self.env["grocery.list.line"].create(
            {
                "list_id": self.grocery_list.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
            }
        )
        line._compute_uom_id()
        self.assertEqual(line.uom_id.id, uom_unit.id)

    def test_compute_uom_id_keep_existing(self):
        """Test that existing UOM is kept if already set"""
        uom_kg = self.env.ref("uom.product_uom_kgm")
        line = self.env["grocery.list.line"].create(
            {
                "list_id": self.grocery_list.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
                "uom_id": uom_kg.id,
            }
        )
        self.assertEqual(line.uom_id.id, uom_kg.id)

    def test_related_product_name(self):
        """Test related field product_name"""
        line = self.env["grocery.list.line"].create(
            {
                "list_id": self.grocery_list.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
            }
        )
        self.assertEqual(line.product_name, self.product1.name)

    def test_related_product_category(self):
        """Test related field product_category"""
        line = self.env["grocery.list.line"].create(
            {
                "list_id": self.grocery_list.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
            }
        )
        self.assertEqual(line.product_category, self.product1.category)

    def test_related_has_real_product(self):
        """Test related field has_real_product"""
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
        line = self.env["grocery.list.line"].create(
            {
                "list_id": self.grocery_list.id,
                "grocery_product_id": grocery_product.id,
                "quantity": 1.0,
            }
        )
        self.assertTrue(line.has_real_product)

    def test_related_list_state(self):
        """Test related field list_state"""
        line = self.env["grocery.list.line"].create(
            {
                "list_id": self.grocery_list.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
            }
        )
        self.assertEqual(line.list_state, "draft")
        self.grocery_list.write({"state": "in_progress"})
        self.assertEqual(line.list_state, "in_progress")

    def test_get_uom_name_with_uom(self):
        """Test get_uom_name returns UOM name when exists"""
        uom_kg = self.env.ref("uom.product_uom_kgm")
        line = self.env["grocery.list.line"].create(
            {
                "list_id": self.grocery_list.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
                "uom_id": uom_kg.id,
            }
        )
        uom_name = line.get_uom_name()
        self.assertEqual(uom_name, uom_kg.name)

    def test_get_uom_name_without_uom(self):
        """Test get_uom_name returns empty string when no UOM"""
        line = self.env["grocery.list.line"].create(
            {
                "list_id": self.grocery_list.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
                "uom_id": False,
            }
        )
        uom_name = line.get_uom_name()
        self.assertEqual(uom_name, "")

    def test_constraint_purchase_permission_responsible(self):
        """Test that responsible user can mark items as purchased"""
        line = self.env["grocery.list.line"].create(
            {
                "list_id": self.grocery_list.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
            }
        )
        line.with_user(self.user_portal).write({"is_purchased": True})
        self.assertTrue(line.is_purchased)

    def test_constraint_purchase_permission_not_responsible(self):
        """Test that non-responsible user cannot mark items as purchased"""

        other_user = self.env["res.users"].create(
            {
                "name": "Other User",
                "login": "other_user",
                "groups_id": [(6, 0, [self.env.ref("base.group_portal").id])],
            }
        )
        line = self.env["grocery.list.line"].create(
            {
                "list_id": self.grocery_list.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
            }
        )
        # AccessError is raised first due to record rules, before constraint validation
        with self.assertRaises(AccessError):
            line.with_user(other_user).write({"is_purchased": True})

    def test_constraint_purchase_permission_sudo(self):
        """Test that sudo (admin) can mark items as purchased"""
        line = self.env["grocery.list.line"].create(
            {
                "list_id": self.grocery_list.id,
                "grocery_product_id": self.product1.id,
                "quantity": 1.0,
            }
        )
        line.sudo().write({"is_purchased": True})
        self.assertTrue(line.is_purchased)

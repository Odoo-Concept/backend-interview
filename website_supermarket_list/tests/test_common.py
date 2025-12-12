from odoo.tests.common import HttpCase, TransactionCase

from odoo.addons.mail.tests.common import mail_new_test_user


class GroceryListTestCommon(TransactionCase):
    """Common test class for grocery list tests"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_portal = mail_new_test_user(
            cls.env,
            login="portal_user",
            name="Portal User",
            groups="base.group_portal",
        )
        cls.user_internal = mail_new_test_user(
            cls.env,
            login="internal_user",
            name="Internal User",
            groups="base.group_user",
        )
        cls.user_admin = cls.env.ref("base.user_admin")

        cls.store = cls.env["grocery.store"].create(
            {
                "name": "Test Store",
                "active": True,
            }
        )

        cls.product1 = cls.env["grocery.product"].create(
            {
                "name": "Milk",
                "category": "Dairy",
                "active": True,
            }
        )
        cls.product2 = cls.env["grocery.product"].create(
            {
                "name": "Bread",
                "category": "Bakery",
                "active": True,
            }
        )
        cls.product3 = cls.env["grocery.product"].create(
            {
                "name": "Eggs",
                "category": "Dairy",
                "active": True,
            }
        )

        cls.grocery_list = cls.env["grocery.list"].create(
            {
                "name": "Test List",
                "store_id": cls.store.id,
                "responsible_id": cls.user_portal.id,
                "state": "draft",
            }
        )


class GroceryListHttpCase(HttpCase):
    """Common HTTP test class for grocery list controller tests"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_portal = mail_new_test_user(
            cls.env,
            login="portal_user",
            name="Portal User",
            groups="base.group_portal",
        )
        cls.user_portal2 = mail_new_test_user(
            cls.env,
            login="portal_user2",
            name="Portal User 2",
            groups="base.group_portal",
        )
        cls.user_internal = mail_new_test_user(
            cls.env,
            login="internal_user",
            name="Internal User",
            groups="base.group_user",
        )

        cls.store = cls.env["grocery.store"].create(
            {
                "name": "Test Store",
                "active": True,
            }
        )

        cls.product1 = cls.env["grocery.product"].create(
            {
                "name": "Milk",
                "category": "Dairy",
                "active": True,
            }
        )
        cls.product2 = cls.env["grocery.product"].create(
            {
                "name": "Bread",
                "category": "Bakery",
                "active": True,
            }
        )

        cls.grocery_list = cls.env["grocery.list"].create(
            {
                "name": "Test List",
                "store_id": cls.store.id,
                "responsible_id": cls.user_portal.id,
                "state": "draft",
            }
        )

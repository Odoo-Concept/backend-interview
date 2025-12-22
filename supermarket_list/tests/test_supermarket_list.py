from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import TransactionCase, new_test_user


class TestSupermarketList(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_responsible = new_test_user(
            cls.env,
            login="responsible_user",
            name="Responsible User",
            groups="base.group_user",
        )
        cls.user_other = new_test_user(
            cls.env,
            login="other_user",
            name="Other User",
            groups="base.group_user",
        )
        cls.List = cls.env["supermarket.list"]
        cls.Line = cls.env["supermarket.list.line"]

        cls.portal_user = new_test_user(
            cls.env,
            login="portal_user",
            name="Portal User",
            groups="base.group_portal",
            share=True,
        )

    def test_done_requires_all_purchased(self):
        list_record = self.List.with_user(self.user_responsible).create(
            {
                "name": "Weekly",
                "responsible_id": self.user_responsible.id,
            }
        )
        line = self.Line.with_user(self.user_responsible).create(
            {
                "list_id": list_record.id,
                "product_name": "Milk",
                "quantity": 1.0,
            }
        )
        with self.assertRaises(ValidationError):
            list_record.with_user(self.user_responsible).action_mark_done()
        line.with_user(self.user_responsible).write({"is_purchased": True})
        list_record.with_user(self.user_responsible).action_mark_done()
        self.assertEqual(list_record.state, "done")

    def test_non_responsible_cannot_toggle_purchased(self):
        list_record = self.List.with_user(self.user_responsible).create(
            {
                "name": "Household",
                "responsible_id": self.user_responsible.id,
            }
        )
        line = self.Line.with_user(self.user_responsible).create(
            {
                "list_id": list_record.id,
                "product_name": "Bread",
                "quantity": 1.0,
            }
        )
        with self.assertRaises(AccessError):
            line.with_user(self.user_other).write({"is_purchased": True})

    def test_cannot_unpurchase_in_done(self):
        list_record = self.List.with_user(self.user_responsible).create(
            {
                "name": "Quick",
                "responsible_id": self.user_responsible.id,
            }
        )
        line = self.Line.with_user(self.user_responsible).create(
            {
                "list_id": list_record.id,
                "product_name": "Eggs",
                "quantity": 12.0,
                "is_purchased": True,
            }
        )
        list_record.with_user(self.user_responsible).action_mark_done()
        with self.assertRaises(ValidationError):
            line.with_user(self.user_responsible).write({"is_purchased": False})

    def test_portal_user_workflow(self):
        list_record = self.List.with_user(self.portal_user).create(
            {
                "name": "Portal List",
                "responsible_id": self.portal_user.id,
            }
        )
        list_record.with_user(self.portal_user).action_start()
        line = self.Line.with_user(self.portal_user).create(
            {
                "list_id": list_record.id,
                "product_name": "Apples",
                "quantity": 2.0,
            }
        )
        line.with_user(self.portal_user).write({"is_purchased": True})
        list_record.with_user(self.portal_user).action_mark_done()
        self.assertEqual(list_record.state, "done")

    def test_portal_user_cannot_access_other_lists(self):
        list_record = self.List.with_user(self.user_responsible).create(
            {
                "name": "Private List",
                "responsible_id": self.user_responsible.id,
            }
        )
        with self.assertRaises(AccessError):
            list_record.with_user(self.portal_user).check_access_rule("read")

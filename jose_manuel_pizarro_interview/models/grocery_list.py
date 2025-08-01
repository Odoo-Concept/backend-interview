from odoo import fields, models
from odoo.exceptions import ValidationError

GROCERY_LIST_STATE = [
    ("draft", "Draft"),
    ("in_progress", "In Progress"),
    ("done", "Completed"),
]

class GroceryList(models.Model):
    _name = 'grocery.list'
    _description = 'Grocery List'

    name = fields.Char(copy=False)
    user_responsible_id = fields.Many2one("res.users", "Responsible",
                                          default=lambda self: self.env.user,
                                          readonly=True)
    state = fields.Selection(
        GROCERY_LIST_STATE,
        "Status",
        readonly=True,
        copy=False,
        default="draft")
    grocery_lines = fields.One2many("grocery.line", "grocery_list_id", "Grocery List")


    # action methods

    def action_set_in_progress(self):
        self.ensure_one()
        if not self.grocery_lines:
            raise ValidationError(self.env._(
                "Your grocery list is empty. Add items in order to change the state"
                "to In Progress"))
        if self.state != "draft":
            raise ValidationError(
                self.env._("Your grocery list must be in Draft state in order to "
                           "change to In "
                  "Progress State"))
        self.state = "in_progress"

    def action_set_done(self):
        self.ensure_one()
        if not self.state == "in_progress":
            raise ValidationError(
                self.env._("Your grocery list must be in Progress state in order to "
                      "complete "
                  "it"))
        if not all(self.grocery_lines.mapped("is_purchased")):
            raise ValidationError(
                    self.env._("You need to purchase all the items in order to "
                               "complete the "
                      "grocery list, remaining items:")
                    + "\n" + "\n".join(self.env._(
                        "- %(name)s",
                        name=name,
                    ) for name in self.grocery_lines.filtered(lambda line: not
                    line.is_purchased).mapped("product_id").mapped("name"))
                )
        self.state = "done"

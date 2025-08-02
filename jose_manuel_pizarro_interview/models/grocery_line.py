from odoo import api, fields, models


class GroceryLine(models.Model):
    _name = "grocery.line"
    _description = "Grocery Line"

    product_id = fields.Many2one("product.product", string="Product", required=True)
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
        compute="_compute_product_uom",
        store=True,
        readonly=False,
        precompute=True,
    )
    quantity = fields.Float(required=True)
    is_purchased = fields.Boolean(copy=False)
    can_edit_is_purchased = fields.Boolean(compute="_compute_can_edit_is_purchased")
    grocery_list_id = fields.Many2one("grocery.list", "Grocery List")
    user_responsible_id = fields.Many2one(related="grocery_list_id.user_responsible_id")
    state = fields.Selection(related="grocery_list_id.state")
    # computed methods

    @api.depends("user_responsible_id", "state")
    def _compute_can_edit_is_purchased(self):
        for line in self:
            user_have_access = line.user_responsible_id.id == self.env.user.id
            progress_state = line.state == "in_progress"
            line.can_edit_is_purchased = user_have_access and progress_state

    @api.depends("product_id")
    def _compute_product_uom(self):
        for line in self:
            different_uom = line.product_id.uom_id.id != line.product_uom_id.id
            if not line.product_uom_id or different_uom:
                line.product_uom_id = line.product_id.uom_id

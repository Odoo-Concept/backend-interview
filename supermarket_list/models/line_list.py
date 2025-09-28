from odoo import models, fields, _


class ListLine(models.Model):
    _name = "list.line"
    _description = "List Line"
    list_id = fields.Many2one(
        "supermarket.list",
        readonly=True,
        auto_join=True,
        string="List",
        ondelete="cascade",
        required=True,
    )
    product_id = fields.Many2one("product.product", string="Product", required=True, tracking=True)
    quantity = fields.Float(string="Quantity", required=True, default=1.0, tracking=True)
    state = fields.Selection(
        [
            ("not_purchased", "Not Purchased"),
            ("purchased", "Purchased"),
        ],
        default="not_purchased",
        string="State", required=True,
        tracking=True,
    )
from odoo import _, fields, models
from odoo.exceptions import ValidationError


class MarketListProduct(models.Model):
    _name = "market.list.product"
    _description = "Market List Product"

    market_list_id = fields.Many2one(
        comodel_name="market.list",
        required=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        comodel_name="product.template",
        required=True,
    )
    quantity = fields.Float(required=True, default=1.0)
    is_purchased = fields.Boolean(default=False, store=True)
    responsible_id = fields.Many2one(
        "res.users",
        related="market_list_id.responsible_id",
        store=True,
    )

    def write(self, vals):
        """Override write method to add custom logic if needed."""
        if "is_purchased" in vals:
            for record in self:
                if self.env.user != record.responsible_id:
                    raise ValidationError(
                        _("You do not have permission to change the purchase status.")
                    )
        return super().write(vals)

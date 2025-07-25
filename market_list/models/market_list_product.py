from odoo import api, fields, models
from odoo.exceptions import ValidationError

class MarketListProduct(models.Model):
    _name = 'market.list.product'
    _description = 'Market List Product'

    market_list_id = fields.Many2one(
        comodel_name='market.list',
        string='Market List',
        required=True,
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        comodel_name='product.template',
        string='Product',
        required=True,
    )
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    is_purchased = fields.Boolean(string='Is Purchased', default=False, store=True)
    responsible_id = fields.Many2one('res.users', string='Responsible User', related='market_list_id.responsible_id', store=True)

    def write(self, vals):
        """Override write method to add custom logic if needed."""
        if 'is_purchased' in vals:
            for record in self:
                if self.env.user != record.responsible_id:
                    raise models.ValidationError("You do not have permission to change the purchase status.")
            res = super().write(vals)
            self.mapped('market_list_id')._compute_state()
            return res
        return super().write(vals)

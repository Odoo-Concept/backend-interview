from odoo import api, fields, models
from odoo.exceptions import UserError

class MarketList(models.Model):
    _name = 'market.list'
    _description = 'Market List'

    name = fields.Char(string='List Name', required=True)
    responsible_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        required=True
    )
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Completed'),
    ], default='draft', string='State', computed='_compute_state', store=True)
    product_ids = fields.One2many('market.list.product', 'market_list_id', string='Products')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    is_confirmed = fields.Boolean(string='Purchase Confirmed', default=False, store=True)

    @api.depends('product_ids.is_purchased', 'product_ids')
    def _compute_state(self):
        """Compute the state of the market list based on purchased products."""
        for record in self:
            if all(product.is_purchased for product in record.product_ids):
                record.state = 'done'
            elif any(product.is_purchased for product in record.product_ids):
                record.state = 'in_progress'
            else:
                record.state = 'draft'

    def action_confirm_purchase(self):
        for record in self:
            if record.state != 'done':
                raise UserError("You can only confirm purchases when the list is completed.")
            if record.is_confirmed:
                raise UserError("The purchase has already been confirmed.")
            record.is_confirmed = True

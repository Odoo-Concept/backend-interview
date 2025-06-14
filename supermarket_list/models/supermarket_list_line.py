from odoo import models, fields, api
from odoo.exceptions import UserError


class SupermarketListLine(models.Model):
    _name = 'supermarket.list.line'
    _description = 'Line of Supermarket List'

    list_id = fields.Many2one(
        comodel_name='supermarket.list', 
        string='List',
        required=True, 
        ondelete='cascade'
    )
    quantity = fields.Float(
        string='Quantity',
        default=1.0
    )

    product_id = fields.Many2one(
        comodel_name='product.template', 
        string='Product',
        required=True
    )

    is_purchased = fields.Boolean(
        string='Purchased', 
        default=False
    )

    @api.constrains('is_purchased')
    def _check_user_permission(self):
        if self.list_id and self.env.user != self.list_id.user_id:
            raise UserError(
                "You do not have permission to change the purchased state of this line."
            )

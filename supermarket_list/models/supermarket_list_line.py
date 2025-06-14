from odoo import models, fields, api
from odoo.exceptions import UserError


class SupermarketListLine(models.Model):
    """
    Model representing a single product line in a supermarket list.
    """
    _name = 'supermarket.list.line'
    _description = 'Line of Supermarket List'

    list_id = fields.Many2one(
        comodel_name='supermarket.list',
        string='List',
        required=True,
        ondelete='cascade',
        help="The shopping list this item belongs to."
    )

    product_id = fields.Many2one(
        comodel_name='product.template',
        string='Product',
        required=True,
        help="Product to be purchased."
    )

    quantity = fields.Float(
        string='Quantity',
        default=1.0,
        help="Quantity of the product to purchase."
    )

    is_purchased = fields.Boolean(
        string='Purchased',
        default=False,
        help="Indicates whether the product has been purchased."
    )

    @api.constrains('product_id', 'quantity', 'is_purchased')
    def _check_user_permission(self):
        """
        Constraint to ensure only the responsible user of the list
        can change the purchased status of a product.
        """
        for record in self:
            if record.list_id and self.env.user != record.list_id.user_id:
                raise UserError(
                    "You do not have permission to change the purchased state of this item."
                )

    def action_mark_as_purchased(self):
        """
        Mark this product as purchased (only if not already marked).
        """
        self.ensure_one()
        if not self.is_purchased:
            self.is_purchased = True

    def unlink(self):
        """
        Override unlink to restrict deletion to the responsible user only.
        """
        for record in self:
            if record.env.user != record.list_id.user_id:
                raise UserError(
                    "You do not have permission to delete this item."
                )
        return super(SupermarketListLine, self).unlink()

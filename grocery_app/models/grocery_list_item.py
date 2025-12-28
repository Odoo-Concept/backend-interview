from odoo import models, fields, api
from odoo.exceptions import UserError


class GroceryListItem(models.Model):
    _name = 'grocery.list.item'
    _description = 'Grocery List Item'
    _order = 'sequence, id'

    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Used to order items'
    )

    list_id = fields.Many2one(
        'grocery.list',
        string='Grocery List',
        required=True,
        ondelete='cascade',
        help='The grocery list this item belongs to'
    )

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        help='Product to purchase'
    )

    quantity = fields.Float(
        string='Quantity',
        required=True,
        default=1.0,
        help='Quantity to purchase'
    )

    purchased = fields.Boolean(
        string='Purchased',
        default=False,
        help='Indicates if this item has been purchased'
    )

    responsible_user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        related='list_id.responsible_user_id',
        store=True,
        help='User responsible for the list'
    )

    list_status = fields.Selection(
        related='list_id.status',
        string='List Status',
        store=True,
        help='Status of the parent grocery list'
    )

    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        related='product_id.uom_id',
        help='Unit of measure for the product'
    )

    @api.constrains('quantity')
    def _check_quantity(self):
        """Ensure quantity is positive"""
        for record in self:
            if record.quantity <= 0:
                raise UserError('Quantity must be greater than zero.')

    def write(self, vals):
        """Override write to check permissions and trigger auto status update"""
        # Check if purchased field is being modified
        if 'purchased' in vals:
            for record in self:
                # Only the responsible user can modify the purchased status
                if record.responsible_user_id != self.env.user and not self.env.user.has_group('base.group_system'):
                    raise UserError(
                        f'Only {record.responsible_user_id.name} (the responsible user) '
                        'can mark items as purchased or unpurchased.'
                    )

        # Perform the write operation
        result = super(GroceryListItem, self).write(vals)

        # If purchased status was changed, update parent list status
        if 'purchased' in vals:
            self._update_list_status()

        return result

    @api.model
    def create(self, vals):
        """Override create to trigger status update"""
        result = super(GroceryListItem, self).create(vals)
        result._update_list_status()
        return result

    def unlink(self):
        """Override unlink to trigger status update after deletion"""
        lists_to_update = self.mapped('list_id')
        result = super(GroceryListItem, self).unlink()

        # Update status of affected lists
        for grocery_list in lists_to_update:
            if grocery_list.exists():
                grocery_list._auto_update_status()

        return result

    def _update_list_status(self):
        """Automatically update the parent list status based on item purchase status"""
        for record in self:
            if record.list_id:
                record.list_id._auto_update_status()

    def toggle_purchased(self):
        """Toggle the purchased status of the item"""
        for record in self:
            # Check permission
            if record.responsible_user_id != self.env.user and not self.env.user.has_group('base.group_system'):
                raise UserError(
                    f'Only {record.responsible_user_id.name} (the responsible user) '
                    'can mark items as purchased or unpurchased.'
                )
            record.purchased = not record.purchased
        return True

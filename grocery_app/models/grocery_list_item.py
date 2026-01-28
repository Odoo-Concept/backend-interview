from odoo import api, fields, models
from odoo.exceptions import UserError


class GroceryListItem(models.Model):
    """Individual item within a grocery list"""
    _name = 'grocery.list.item'
    _description = 'Grocery List Item'
    _order = 'sequence, id'

    # Relations
    list_id = fields.Many2one(
        comodel_name='grocery.list',
        string='Grocery List',
        required=True,
        ondelete='cascade',
        help='The grocery list this item belongs to'
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
        help='Product to purchase'
    )

    # Item details
    quantity = fields.Float(string='Quantity', required=True, default=1.0, help='Quantity to purchase')
    sequence = fields.Integer(string='Sequence', default=10, help='Used to order items')
    purchased = fields.Boolean(string='Purchased', default=False, help='Indicates if this item has been purchased')

    # Related fields
    uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Unit of Measure',
        related='product_id.uom_id',
        readonly=True,
        help='Unit of measure for the product'
    )
    responsible_user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible User',
        related='list_id.responsible_user_id',
        store=True,
        readonly=True,
        help='User responsible for the list'
    )

    # Validation
    @api.constrains('quantity')
    def _check_quantity(self):
        """Validate that quantity is greater than zero"""
        for item in self:
            if item.quantity <= 0:
                raise UserError('Quantity must be greater than zero.')

    # Permission checks
    def _check_purchase_permission(self):
        """Verify user has permission to modify purchase status"""
        current_user = self.env.user
        is_system_admin = current_user.has_group('base.group_system')
        
        for item in self:
            if item.responsible_user_id != current_user and not is_system_admin:
                responsible_name = item.responsible_user_id.name
                raise UserError(
                    'Only {} (the responsible user) can mark items as purchased or unpurchased.'.format(responsible_name)
                )

    # Override methods
    def write(self, vals):
        """Override write to enforce permissions and update parent list status"""
        if 'purchased' in vals:
            self._check_purchase_permission()
        
        result = super().write(vals)
        
        if 'purchased' in vals:
            self._update_list_status()
        
        return result

    @api.model
    def create(self, vals):
        """Override create to update parent list status"""
        item = super().create(vals)
        item._update_list_status()
        return item

    def unlink(self):
        """Override unlink to update parent list status after deletion"""
        parent_lists = self.mapped('list_id')
        result = super().unlink()
        
        for grocery_list in parent_lists:
            if grocery_list.exists():
                grocery_list._auto_update_status()
        
        return result

    # Helper methods
    def _update_list_status(self):
        """Trigger status update on parent grocery list"""
        for item in self:
            if item.list_id:
                item.list_id._auto_update_status()

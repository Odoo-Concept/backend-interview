from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError


class ShoppingListItem(models.Model):
    _name = 'shopping.list.item'
    _description = 'Shopping List Item'
    _order = 'sequence, create_date'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ==================== Basic Fields ====================
    shopping_list_id = fields.Many2one(
        comodel_name='shopping.list',
        string='Shopping List',
        required=True,
        ondelete='cascade',
        help='Shopping list this item belongs to'
    )

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        help='Reference to the product (if applicable)'
    )

    quantity = fields.Float(
        string='Quantity',
        required=True,
        default=1.0,
        help='Desired quantity of the product'
    )

    quantity_done = fields.Float(
        string='Quantity Purchased',
        default=0.0,
        help='Quantity of the product that has been purchased'
    )

    unit_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Unit of Measure',
        help='Unit of measurement for the product'
    )

    unit_purchased_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Unit of Measure Purchased',
        help='Unit of measurement for the purchased quantity'
    )

    is_purchased = fields.Boolean(
        string='Purchased',
        default=False,
        help='Check if the product has been purchased'
    )
    purchased_date = fields.Datetime(
        string='Purchase Date',
        readonly=True,
        help='Date and time when the product was marked as purchased'
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Display order in the list'
    )

    notes = fields.Text(
        string='Notes',
        translate=True,
        help='Additional notes about the product (brand, preferences, etc.)'
    )

    # ==================== Relationship Fields ====================
    responsible_id = fields.Many2one(
        related='shopping_list_id.responsible_id',
        string='List Responsible',
        store=True,
        readonly=True
    )

    # ==================== Status Fields ====================
    list_state = fields.Selection(
        related='shopping_list_id.state',
        string='List State',
        store=True,
        readonly=True
    )

    # ==================== Validation Methods ====================
    @api.constrains('quantity')
    def _check_quantity(self):
        """Validate that quantity is positive"""
        for record in self:
            if record.quantity <= 0:
                raise UserError(
                    _('Quantity must be greater than 0.')
                )

    # ==================== Onchange Methods ====================
    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Set default unit of measure based on selected product"""
        for record in self:
            if record.product_id:
                record.unit_id = record.product_id.uom_id.id

    @api.onchange("is_purchased")
    def _onchange_is_purchased(self):
        """Set quantity_done to quantity when marked as purchased"""
        for record in self:
            if record.is_purchased:
                record.quantity_done = record.quantity
                record.unit_purchased_id = record.unit_id
            else:
                record.quantity_done = 0.0
                record.unit_purchased_id = False

    # ==================== Permission and Logic Methods ====================
    def write(self, vals):
        """
        Control permissions: Only responsible user can mark items as purchased.
        When marking as purchased, automatically set the purchase date.
        When marking as unpurchased, clear the purchase date.
        """
        for record in self:
            # If trying to change is_purchased, validate permissions
            if 'is_purchased' in vals:
                # Only responsible or admin can change purchase status
                is_responsible = record.responsible_id == self.env.user
                is_admin = self.env.user.has_group('base.group_system')

                if not (is_responsible or is_admin):
                    raise AccessError(
                        _('Only the list responsible can mark items as purchased.')
                    )
        return super().write(vals)

    def unlink(self):
        """Only the list responsible user can delete items"""
        for record in self:
            is_responsible = record.responsible_id == self.env.user
            is_admin = self.env.user.has_group('base.group_system')

            if record.shopping_list_id.state != 'draft':
                raise UserError(
                    _('Only items from shopping lists in Draft state can be deleted.')
                )

            if not (is_responsible or is_admin):
                raise AccessError(
                    _('Only the list responsible can delete items.')
                )

        return super().unlink()

    # ==================== Action Methods ====================
    def action_mark_purchased(self):
        """Mark item as purchased"""
        self._check_permission_to_modify()
        self.write({
            'is_purchased': True,
            'purchased_date': fields.Datetime.now(),
            'quantity_done': self.quantity,
            'unit_purchased_id': self.unit_id.id
        })
        return True

    def action_mark_unpurchased(self):
        """Mark item as unpurchased"""
        self._check_permission_to_modify()
        self.write({
            'is_purchased': False,
            'purchased_date': False,
            'quantity_done': 0.0,
            'unit_purchased_id': False
        })
        return True

    def _check_permission_to_modify(self):
        """Verify that current user is the list responsible"""
        for record in self:
            is_responsible = record.responsible_id == self.env.user
            is_admin = self.env.user.has_group('base.group_system')

            if not (is_responsible or is_admin):
                raise AccessError(
                    _('Only the list responsible can modify items.')
                )

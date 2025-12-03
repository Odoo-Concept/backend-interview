from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError

from odoo.odoo.api import readonly


class ShoppingList(models.Model):
    _name = 'shopping.list'
    _description = 'Shopping List'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ==================== Basic Fields ====================
    name = fields.Char(
        string='Name',
        required=True,
        translate=True,
        help='Descriptive name of the shopping list'
    )

    responsible_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        required=True,
        default=lambda self: self.env.user,
        help='User responsible for this shopping list'
    )

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('completed', 'Done'),
        ],
        default='draft',
        required=True,
        readonly=True,
        tracking=True,
        help='Current state of the shopping list'
    )

    description = fields.Text(
        string='Description',
        translate=True,
        help='Additional notes or details about the shopping list'
    )

    # ==================== Relationship Fields ====================
    item_ids = fields.One2many(
        comodel_name='shopping.list.item',
        inverse_name='shopping_list_id',
        string='Items',
        copy=True,
        help='Shopping items/products in this list'
    )


    # ==================== Action Methods ====================
    def action_draft(self):
        """Change state to Draft"""
        self.write({'state': 'draft'})
        return True

    def action_in_progress(self):
        """Change state to In Progress"""
        if not self.item_ids:
            raise UserError(
                _('Cannot start a shopping list without items.')
            )
        self.write({'state': 'in_progress'})
        return True

    def action_completed(self):
        """Change state to Done"""
        unpurchased = self.item_ids.filtered(lambda x: not x.is_purchased)
        if unpurchased:
            raise UserError(
                _('Cannot complete the list. There are still unpurchased products.')
            )
        self.write({'state': 'completed'})
        return True

    def action_reset(self):
        """Reset all items to unpurchased and return to draft"""
        self.item_ids.write({'is_purchased': False})
        self.write({'state': 'draft'})
        return True

    # ==================== Permission Methods ====================
    def write(self, vals):
        """
        Control write permissions based on user role.
        Only the responsible user or system admin can edit the list.
        """
        for record in self:
            # Check if user is responsible or admin
            is_responsible = record.responsible_id == self.env.user
            is_admin = self.env.user.has_group('base.group_system')

            if not (is_responsible or is_admin):
                raise AccessError(
                    _('Only the responsible user can modify this shopping list.')
                )

        return super().write(vals)

    def unlink(self):
        """
        Only responsible user or admin can delete the list.
        """
        for record in self:
            is_responsible = record.responsible_id == self.env.user
            is_admin = self.env.user.has_group('base.group_system')

            if record.state != 'draft':
                raise UserError(
                    _('Only shopping lists in Draft state can be deleted.')
                )


            if not (is_responsible or is_admin):
                raise AccessError(
                    _('Only the responsible user can delete this shopping list.')
                )

        return super().unlink()

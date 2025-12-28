from odoo import models, fields, api
from odoo.exceptions import ValidationError


class GroceryList(models.Model):
    _name = 'grocery.list'
    _description = 'Grocery List'
    _order = 'create_date desc'

    active = fields.Boolean(
        string='Active',
        default=True,
        help='Set to false to archive the grocery list'
    )

    name = fields.Char(
        string='List Name',
        required=True,
        help='Descriptive name of the grocery list'
    )

    responsible_user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        required=True,
        default=lambda self: self.env.user,
        help='User responsible for managing and completing the list'
    )

    status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed')
        ],
        string='Status',
        required=True,
        default='draft',
        help='Current status of the grocery list'
    )

    item_ids = fields.One2many(
        'grocery.list.item',
        'list_id',
        string='Items',
        help='Products associated with this list'
    )

    item_count = fields.Integer(
        string='Total Items',
        compute='_compute_item_stats',
        store=True,
        help='Total number of items in the list'
    )

    purchased_count = fields.Integer(
        string='Purchased Items',
        compute='_compute_item_stats',
        store=True,
        help='Number of items marked as purchased'
    )

    pending_count = fields.Integer(
        string='Pending Items',
        compute='_compute_item_stats',
        store=True,
        help='Number of items not yet purchased'
    )

    completion_percentage = fields.Float(
        string='Completion %',
        compute='_compute_item_stats',
        store=True,
        help='Percentage of items purchased'
    )

    @api.depends('item_ids', 'item_ids.purchased')
    def _compute_item_stats(self):
        """Compute item statistics for the grocery list"""
        for record in self:
            total = len(record.item_ids)
            purchased = len(record.item_ids.filtered('purchased'))

            record.item_count = total
            record.purchased_count = purchased
            record.pending_count = total - purchased
            record.completion_percentage = (purchased / total * 100) if total > 0 else 0.0

    @api.depends('item_ids', 'item_ids.purchased')
    def _compute_all_items_purchased(self):
        """Check if all items are purchased"""
        for record in self:
            if not record.item_ids:
                record.all_items_purchased = False
            else:
                record.all_items_purchased = all(item.purchased for item in record.item_ids)

    all_items_purchased = fields.Boolean(
        compute='_compute_all_items_purchased',
        store=True,
        help='Indicates if all items have been purchased'
    )

    @api.constrains('status')
    def _check_completed_status(self):
        """Ensure list cannot be completed unless all items are purchased"""
        for record in self:
            if record.status == 'completed':
                if not record.item_ids:
                    raise ValidationError(
                        'Cannot complete a grocery list with no items.'
                    )
                if not all(item.purchased for item in record.item_ids):
                    raise ValidationError(
                        'Cannot complete the list. All items must be marked as purchased first.'
                    )

    def _auto_update_status(self):
        """Automatically update list status based on item purchase status"""
        for record in self:
            if not record.item_ids:
                continue

            all_purchased = all(item.purchased for item in record.item_ids)
            any_purchased = any(item.purchased for item in record.item_ids)

            # Auto-complete when all items are purchased and list is in progress
            if all_purchased and record.status == 'in_progress':
                record.status = 'completed'

            # Move back to in progress if completed list has unpurchased items
            elif not all_purchased and record.status == 'completed':
                record.status = 'in_progress'

    def action_start_progress(self):
        """Move list from draft to in progress"""
        for record in self:
            if record.status == 'draft':
                record.status = 'in_progress'
        return True

    def action_complete(self):
        """Complete the grocery list"""
        for record in self:
            if not record.item_ids:
                raise ValidationError('Cannot complete a list with no items.')
            if not all(item.purchased for item in record.item_ids):
                raise ValidationError(
                    'Cannot complete the list. All items must be marked as purchased.'
                )
            record.status = 'completed'
        return True

    def action_reset_to_draft(self):
        """Reset list back to draft"""
        for record in self:
            record.status = 'draft'
        return True

    def action_back_to_progress(self):
        """Move list back to in progress"""
        for record in self:
            record.status = 'in_progress'
        return True

    @api.model
    def create(self, vals):
        """Override create to set default responsible user"""
        if 'responsible_user_id' not in vals:
            vals['responsible_user_id'] = self.env.user.id
        return super(GroceryList, self).create(vals)

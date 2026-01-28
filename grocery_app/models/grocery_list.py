from odoo import api, fields, models
from odoo.exceptions import ValidationError


class GroceryList(models.Model):
    """Grocery shopping list management model"""
    _name = 'grocery.list'
    _description = 'Grocery List'
    _order = 'create_date desc'

    # Basic fields
    name = fields.Char(string='List Name', required=True, help='Descriptive name of the grocery list')
    active = fields.Boolean(string='Active', default=True, help='Set to false to archive the grocery list')
    
    # User and status
    responsible_user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible User',
        required=True,
        default=lambda self: self.env.user,
        help='User responsible for managing and completing the list'
    )
    status = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed')
        ],
        string='Status',
        required=True,
        default='draft',
        help='Current status of the grocery list'
    )

    # Relations
    item_ids = fields.One2many(
        comodel_name='grocery.list.item',
        inverse_name='list_id',
        string='Items',
        help='Products associated with this list'
    )

    # Computed statistics fields
    item_count = fields.Integer(
        compute='_compute_item_stats',
        store=True,
        string='Total Items',
        help='Total number of items in the list'
    )
    purchased_count = fields.Integer(
        compute='_compute_item_stats',
        store=True,
        string='Purchased Items',
        help='Number of items marked as purchased'
    )
    pending_count = fields.Integer(
        compute='_compute_item_stats',
        store=True,
        string='Pending Items',
        help='Number of items not yet purchased'
    )
    completion_percentage = fields.Float(
        compute='_compute_item_stats',
        store=True,
        string='Completion %',
        help='Percentage of items purchased'
    )

    # Computed methods
    @api.depends('item_ids', 'item_ids.purchased')
    def _compute_item_stats(self):
        """Calculate statistics for items in the list"""
        for grocery_list in self:
            items = grocery_list.item_ids
            total_items = len(items)
            purchased_items = len(items.filtered('purchased'))
            
            grocery_list.item_count = total_items
            grocery_list.purchased_count = purchased_items
            grocery_list.pending_count = total_items - purchased_items
            grocery_list.completion_percentage = (purchased_items / total_items * 100) if total_items > 0 else 0.0

    # Validation methods
    @api.constrains('status')
    def _check_completed_status(self):
        """Validate that completed lists have all items purchased"""
        for grocery_list in self:
            if grocery_list.status == 'completed':
                if not grocery_list.item_ids:
                    raise ValidationError('Cannot complete a grocery list with no items.')
                unpurchased_items = [item for item in grocery_list.item_ids if not item.purchased]
                if unpurchased_items:
                    raise ValidationError('Cannot complete the list. All items must be marked as purchased first.')

    # Status management methods
    def _auto_update_status(self):
        """Update list status automatically based on item purchase status"""
        for grocery_list in self:
            if not grocery_list.item_ids:
                continue
            
            items = grocery_list.item_ids
            all_items_purchased = all(item.purchased for item in items)
            current_status = grocery_list.status
            
            # Auto-complete: all items purchased and status is in_progress
            if all_items_purchased and current_status == 'in_progress':
                grocery_list.status = 'completed'
            # Revert to in_progress: completed list has unpurchased items
            elif not all_items_purchased and current_status == 'completed':
                grocery_list.status = 'in_progress'

    # Action methods
    def action_start_progress(self):
        """Transition list from draft to in progress status"""
        self.filtered(lambda l: l.status == 'draft').write({'status': 'in_progress'})
        return True

    def action_complete(self):
        """Manually complete the grocery list"""
        for grocery_list in self:
            if not grocery_list.item_ids:
                raise ValidationError('Cannot complete a list with no items.')
            if not all(item.purchased for item in grocery_list.item_ids):
                raise ValidationError('Cannot complete the list. All items must be marked as purchased.')
            grocery_list.status = 'completed'
        return True

    def action_reset_to_draft(self):
        """Reset list status back to draft"""
        self.write({'status': 'draft'})
        return True

    def action_back_to_progress(self):
        """Move list back to in progress status"""
        self.write({'status': 'in_progress'})
        return True

    # Override methods
    @api.model
    def create(self, vals):
        """Set default responsible user if not provided"""
        if 'responsible_user_id' not in vals:
            vals['responsible_user_id'] = self.env.user.id
        return super().create(vals)

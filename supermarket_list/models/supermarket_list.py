from odoo import models, fields, api, _


class SupermarketList(models.Model):
    """Model representing a supermarket shopping list."""
    _name = 'supermarket.list'
    _description = 'Supermarket List'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="List Name",
        required=True,
        help="Name or title of the shopping list."
    )

    user_id = fields.Many2one(
        comodel_name='res.users',
        string="Responsible User",
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
        help="User responsible for this shopping list."
    )

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('done', 'Completed'),
        ],
        string="State",
        compute='_compute_state',
        store=True,
        tracking=True,
        help="Current state of the shopping list."
    )

    supermarket_line_ids = fields.One2many(
        comodel_name='supermarket.list.line',
        inverse_name='list_id',
        string="Items",
        copy=True,
        help="Products included in this shopping list."
    )

    count_products = fields.Integer(
        string="Product Count",
        compute='_compute_count_products',
        help="Number of products in the shopping list."
    )

    @api.depends('supermarket_line_ids.is_purchased')
    def _compute_state(self):
        """Compute the state of the list based on item purchase status."""
        for record in self:
            lines = record.supermarket_line_ids
            if not lines:
                record.state = 'draft'
            elif all(line.is_purchased for line in lines):
                record.state = 'done'
            else:
                record.state = 'in_progress'

    def _compute_count_products(self):
        """Compute the number of products in the shopping list."""
        for record in self:
            record.count_products = len(record.supermarket_line_ids)

    def action_add_product(self):
        """
        Open a wizard to add products to the shopping list.
        Returns a form view of the wizard.
        """
        self.ensure_one()

        view = self.env.ref('supermarket_list.wizard_add_product_list_view_form')
        wizard = self.env['wizard.add.product.list'].create({
            'list_id': self.id,
        })

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': wizard._name,
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'res_id': wizard.id,
            'target': 'new',
            'context': dict(self.env.context),
        }
    
    def action_go_to_products(self):
        """
        Open the list of products in the supermarket list.
        Returns an action to display the product list.
        """
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Products in List'),
            'res_model': 'supermarket.list.line',
            'views': [[False, 'list'], [False, 'form']],
            'domain': [('id', 'in', self.supermarket_line_ids.ids)],
        }

from odoo import models, fields, api

class SupermarketList(models.Model):
    _name = 'supermarket.list'
    _description = 'Supermarket List'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="List name",
        required=True
    )
    user_id = fields.Many2one(
        comodel_name='res.users', 
        string="Responsible user",
        default=lambda self: self.env.user, 
        required=True,
        tracking=True
    )

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('in_progress', 'In progress'),
            ('done', 'Done'),
        ], 
        string='State', 
        compute='_compute_state',
        tracking=True,
        store=True,
    )

    supermarket_line_ids = fields.One2many(
        comodel_name='supermarket.list.line', 
        inverse_name='list_id', 
        string='Lines',
        copy=True
    )

    @api.depends('supermarket_line_ids.is_purchased')
    def _compute_state(self):
        for record in self:
            if not record.supermarket_line_ids:
                record.state = 'draft'
            elif all(line.is_purchased for line in record.supermarket_line_ids):
                record.state = 'done'
            else:
                record.state = 'in_progress'

    def action_add_product(self):
        self.ensure_one()
        ctx = dict(self.env.context)
        view = self.env.ref('supermarket_list.wizard_add_product_list_view_form')

        wizard = self.env['wizard.add.product.list'].create({
            'list_id': self.id,
        })

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': wizard._name,
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'res_id': wizard.id,
            'target': 'new',
            'context': ctx,
        }
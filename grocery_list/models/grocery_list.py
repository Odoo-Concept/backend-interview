from odoo import models, fields, api
from odoo.exceptions import ValidationError


class GroceryList(models.Model):
    _name = 'grocery.list'
    _description = 'Lista de Supermercado'
    _order = 'create_date desc'

    name = fields.Char(string='Nombre', required=True)
    responsible_id = fields.Many2one('res.users', string='Responsable', required=True, default=lambda self: self.env.user)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completada'),
    ], string='Estado', default='draft', required=True)
    item_ids = fields.One2many('grocery.list.item', 'list_id', string='Items')
    items_count = fields.Integer(string='Total Items', compute='_compute_items_count', store=True)
    items_purchased_count = fields.Integer(string='Items Comprados', compute='_compute_items_purchased_count', store=True)
    progress_percentage = fields.Float(string='Progreso (%)', compute='_compute_progress_percentage')

    @api.depends('item_ids')
    def _compute_items_count(self):
        for record in self:
            record.items_count = len(record.item_ids)

    @api.depends('item_ids.is_purchased')
    def _compute_items_purchased_count(self):
        for record in self:
            record.items_purchased_count = len(record.item_ids.filtered(lambda i: i.is_purchased))

    @api.depends('items_count', 'items_purchased_count')
    def _compute_progress_percentage(self):
        for record in self:
            if record.items_count > 0:
                record.progress_percentage = (record.items_purchased_count / record.items_count) * 100
            else:
                record.progress_percentage = 0.0

    def action_set_draft(self):
        self.write({'state': 'draft'})

    def action_set_in_progress(self):
        if not self.item_ids:
            raise ValidationError('No se puede poner en progreso una lista sin items.')
        self.write({'state': 'in_progress'})

    def action_set_completed(self):
        if not self.item_ids:
            raise ValidationError('No se puede completar una lista sin items.')
        unpurchased_items = self.item_ids.filtered(lambda i: not i.is_purchased)
        if unpurchased_items:
            raise ValidationError('No se puede completar la lista. Hay items sin comprar.')
        self.write({'state': 'completed'})

    @api.constrains('state')
    def _check_state_completed(self):
        for record in self:
            if record.state == 'completed':
                unpurchased_items = record.item_ids.filtered(lambda i: not i.is_purchased)
                if unpurchased_items:
                    raise ValidationError('Una lista no puede estar completada si hay items sin comprar.')


from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class SupermarketChecklistItem(models.Model):

    _name = 'supermarket.checklist.item'
    _description = 'Item de la Lista de Supermercado'

    product_id = fields.Many2one('supermarket.product', string='Producto', required=True)
    product_description = fields.Text(related='product_id.description')
    quantity = fields.Integer(string='Cantidad', required=True)
    purchased = fields.Boolean(string='Comprado', default=False)
    checklist_id = fields.Many2one('supermarket.checklist', string='Lista de Supermercado', required=True, ondelete="cascade")


    @api.model
    def write(self, vals):
        for record in self:
            if self.env.user != record.checklist_id.user_id:
                raise UserError("No puedes alterar la lista de otro usuario")
            if 'product_id' in vals and record.checklist_id.state != 'draft':
                raise ValidationError("No puedes editar los items de la lista cuando la lista no está en estado 'Borrador'")
            if 'purchased' in vals:
                record.checklist_id.state = 'in_progress'
        return super().write(vals)

    def check_purchased(self):
        for record in self:
            record.purchased = not record.purchased
from odoo import models, fields


class SupermarketChecklistItem(models.Model):

    _name = 'supermarket.checklist.item'
    _description = 'Item de la Lista de Supermercado'

    product_id = fields.Many2one('supermarket.product', string='Producto', required=True)
    quantity = fields.Integer(string='Cantidad', required=True)
    bought = fields.Boolean(string='Comprado', default=False)
    checklist_id = fields.Many2one('supermarket.checklist', string='Lista de Supermercado', required=True)

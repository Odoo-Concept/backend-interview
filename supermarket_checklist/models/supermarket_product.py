from odoo import fields, models


class SupermarketProduct(models.Model):
    _name = "supermarket.product"
    _description = "Producto de la Lista de Supermercado"

    name = fields.Char(string="Nombre del Producto", required=True)
    description = fields.Text(string="Descripción")

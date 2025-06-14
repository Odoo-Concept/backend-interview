from odoo import models, fields, api
from odoo.exceptions import UserError

class WizardAddProductList(models.TransientModel):
    _name = 'wizard.add.product.list'
    _description = 'Wizard to add product to supermarket list'

    list_id = fields.Many2one(
        comodel_name='supermarket.list',
        string='Supermarket List',
        required=True,
        default=lambda self: self.env.context.get('active_id')
    )

    product_id = fields.Many2one(
        comodel_name='product.template',
        string='Product',
    )
    
    quantity = fields.Float(
        string='Quantity',
        default=1.0,
    )

    def execute_add_product(self):
        self.ensure_one()
        self.validate_data()

        self.env['supermarket.list.line'].create({
            'list_id': self.list_id.id,
            'product_id': self.product_id.id,
            'quantity': self.quantity,
        })

        return True

    def validate_data(self):
        if not self.product_id:
            raise UserError("Product must be selected.")
        if self.quantity <= 0:
            raise UserError("Quantity must be greater than zero.")

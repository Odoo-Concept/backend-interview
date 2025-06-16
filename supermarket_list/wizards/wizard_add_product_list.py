from odoo import models, fields, api
from odoo.exceptions import UserError


class WizardAddProductList(models.TransientModel):
    """
    Wizard to add a product to a supermarket list.
    """
    _name = 'wizard.add.product.list'
    _description = 'Wizard to Add Product to Supermarket List'

    list_id = fields.Many2one(
        comodel_name='supermarket.list',
        string='Supermarket List',
        required=True,
        default=lambda self: self.env.context.get('active_id'),
        help="The shopping list to which the product will be added."
    )

    product_id = fields.Many2one(
        comodel_name='product.template',
        string='Product',
        help="Product to be added to the list."
    )

    quantity = fields.Float(
        string='Quantity',
        default=1.0,
        required=True,
        help="Quantity of the product to add."
    )

    def execute_add_product(self):
        """
        Create a new line in the supermarket list with the selected product and quantity.
        """
        self.ensure_one()
        self._validate_data()

        self.env['supermarket.list.line'].create({
            'list_id': self.list_id.id,
            'product_id': self.product_id.id,
            'quantity': self.quantity,
        })

        return True

    def _validate_data(self):
        """
        Perform validation for product selection and quantity.
        """
        if not self.product_id:
            raise UserError("You must select a product.")
        if self.quantity <= 0:
            raise UserError("Quantity must be greater than zero.")

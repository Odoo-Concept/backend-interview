from odoo import fields, models, api, _
from odoo.exceptions import UserError

class GroceryLine(models.Model):
    _name = 'grocery.line'
    _description = 'Grocery Line'

    product_id = fields.Many2one('product.product', string='Product')
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string="Unit of Measure",
        compute='_compute_product_uom',
        store=True, readonly=False, precompute=True)
    quantity = fields.Float(string='Quantity', required=True)
    is_purchased = fields.Boolean(string='Is Purchased', copy=False)
    can_edit_is_purchased = fields.Boolean(string='Can Edit Is Purchased',
                                           compute='_compute_can_edit_is_purchased')
    grocery_list_id = fields.Many2one('grocery.list', string='Grocery')
    user_responsible_id = fields.Many2one(related='grocery_list_id.user_responsible_id',
                                          string='Responsible')
    state = fields.Selection(related='grocery_list_id.state', string='State')
    #computed methods

    @api.depends('user_responsible_id','state')
    def _compute_can_edit_is_purchased(self):
        for line in self:
            line.can_edit_is_purchased = line.user_responsible_id.id == self.env.user.id and \
                                         line.state == 'in_progress'
    @api.depends('product_id')
    def _compute_product_uom(self):
        for line in self:
            if not line.product_uom_id or (line.product_id.uom_id.id != line.product_uom_id.id):
                line.product_uom_id = line.product_id.uom_id

    #Validation methods

    def unlink(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError(_('You cannot delete an item from a confirmed grocery list'))
        return super(GroceryLine, self).unlink()

from odoo import models, fields, api
from odoo.exceptions import UserError


class SupermarketChecklist(models.Model):

    _name = 'supermarket.checklist'
    _description = 'Lista de Supermercado'

    name = fields.Char(string='Nombre de la lista', required=True)
    description = fields.Text(string='Descripción')
    user_id = fields.Many2one('res.users', string='Responsable', required=True)
    item_ids = fields.One2many('supermarket.checklist.item', 'checklist_id', string='Productos')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('in_progress', 'En Progreso'),
        ('done', 'Completada'),
    ], string='Estado', default='draft')


    def add_product(self):
        """ Método para agregar un producto a la lista de supermercado """

        return {
            'type': 'ir.actions.act_window',
            'name': 'Agregar Producto',
            'res_model': 'supermarket.checklist.item',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_checklist_id': self.id},
        }

    def back_to_draft(self):
        """ Método para volver estado de la lista a borrador """

        self.state = 'draft'

    @api.model
    def write(self, vals):
        """ Sobreescritura del método write para realizar validaciones """

        for record in self:
            if self.env.user != record.user_id:
                raise UserError("No puedes alterar la lista de otro usuario")
        return super().write(vals)

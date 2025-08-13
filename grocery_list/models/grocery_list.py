from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class GroceryList(models.Model):
    _name = 'grocery.list'
    _description = 'Lista de Supermercado'

    name = fields.Char(
        string='Nombre de la Lista',
        required=True,
        help='Nombre descriptivo para identificar la lista'
    )

    responsible_id = fields.Many2one(
        'res.users',
        string='Responsable',
        required=True,
        default=lambda self: self.env.user,
        help='Usuario responsable de esta lista'
    )

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completada')
    ],
        string='Estado',
        default='draft',
        required=True
    )

    item_ids = fields.One2many(
        'grocery.list.item',
        'list_id',
        string='Productos',
        help='Productos en esta lista'
    )

    item_count = fields.Integer(
        string='Total de Productos',
        compute='_compute_item_count',
    )

    completed_items_count = fields.Integer(
        string='Productos Comprados',
        compute='_compute_completed_items_count',
    )

    progress_percentage = fields.Float(
        string='Progreso (%)',
        compute='_compute_progress_percentage',
        help='Porcentaje de productos comprados'
    )

    @api.depends('item_ids')
    def _compute_item_count(self):
        for record in self:
            record.item_count = len(record.item_ids)

    @api.depends('item_ids.is_purchased')
    def _compute_completed_items_count(self):
        for record in self:
            record.completed_items_count = len(record.item_ids.filtered(lambda x: x.is_purchased))

    @api.depends('item_count', 'completed_items_count')
    def _compute_progress_percentage(self):
        for record in self:
            if record.item_count > 0:
                record.progress_percentage = (record.completed_items_count / record.item_count) * 100
            else:
                record.progress_percentage = 0.0


    def _check_responsibility(self):
        """Comprueba que el usuario actual sea el responsable de cada lista."""
        for record in self:
            if record.responsible_id != self.env.user:
                raise ValidationError(_("Solo el responsable de la lista puede realizar esta acción."))

    def write(self, vals):
        """Sobreescribe el metodo write para comprobar que el usuario actual sea el responsable de cada lista."""
        self._check_responsibility()
        return super().write(vals)

    def unlink(self):
        """Sobreescribe el metodo unlink para comprobar que el usuario actual sea el responsable de cada lista."""
        self._check_responsibility()
        return super().unlink()


    def action_set_draft(self):
        """ Action para cambiar el estado de la lista a Borrador"""
        self.state = 'draft'

    def action_set_in_progress(self):
        """ Action para cambiar el estado de la lista a En Progreso"""
        if not self.item_ids:
            raise ValidationError(_('No se puede cambiar a "En Progreso" una lista sin productos.'))
        self.state = 'in_progress'

    def action_set_completed(self):
        """Action para marcar una lista como completada."""

        # Comprobar si el usuario que intenta realizar la acción es el responsable de la lista
        self._check_responsibility()

        # Validar que haya productos
        if not self.item_ids:
            raise ValidationError(_('No se puede marcar como completada una lista sin productos.'))

        # Validar que todos los productos estén marcados como comprados
        unpurchased_items = self.item_ids.filtered(lambda x: not x.is_purchased)
        if unpurchased_items:
            raise ValidationError(_('No se puede marcar como completada una lista que tiene productos sin comprar.'))

        self.state = 'completed'

    def action_add_item(self):
        """Action para añadir un nuevo producto"""
        return {
            'name': _('Añadir Producto'),
            'type': 'ir.actions.act_window',
            'res_model': 'grocery.list.item',
            'view_mode': 'form',
            'views': [(self.env.ref('grocery_list.view_grocery_list_item_form_compact').id, 'form')],
            'target': 'new',
            'context': {
                'default_list_id': self.id,
            }
        }




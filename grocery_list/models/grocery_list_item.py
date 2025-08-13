from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class GroceryListItem(models.Model):
    _name = 'grocery.list.item'
    _description = 'Producto de Lista de Supermercado'

    name = fields.Char(
        string='Nombre del Producto',
        required=True,
        help='Nombre del producto a comprar'
    )

    description = fields.Text(string="Descripción del producto")

    list_id = fields.Many2one(
        'grocery.list',
        string='Lista a la que pertenece',
        required=True,
        ondelete='cascade',
        help='Lista a la que pertenece este producto'
    )

    quantity = fields.Float(
        string='Cantidad',
        required=True,
        default=1.0,
        help='Cantidad deseada del producto'
    )

    is_purchased = fields.Boolean(
        string='Comprado',
        default=False,
        help='Marcar cuando el producto haya sido comprado'
    )

    # Campos relacionados
    responsible_id = fields.Many2one(
        'res.users',
        string='Responsable',
        related='list_id.responsible_id',
        help='Usuario responsable de esta lista'
    )

    list_state = fields.Selection(
        string='Estado de la Lista',
        related='list_id.state',
        help='Estado actual de la lista a la que pertenece este producto'
    )

    def _check_responsibility(self):
        """Comprueba que el usuario actual sea el responsable de cada lista."""
        for record in self:
            if record.list_id.responsible_id != self.env.user:
                raise ValidationError(_("Solo el responsable de la lista puede realizar esta acción."))

    def write(self, vals):
        """Sobreescribe el metodo write para comprobar que el usuario actual sea el responsable de cada lista."""
        self._check_responsibility()
        return super().write(vals)

    def unlink(self):
        """Sobreescribe el metodo unlink para comprobar que el usuario actual sea el responsable de cada lista."""
        self._check_responsibility()
        return super().unlink()

    def action_set_purchased(self):
        """"Action para marcar un producto como comprado."""
        self._check_responsibility()

        self.is_purchased = True

    def action_remove_purchased(self):
        """"Action para desmarcar un producto como comprado."""
        self._check_responsibility()

        self.is_purchased = False

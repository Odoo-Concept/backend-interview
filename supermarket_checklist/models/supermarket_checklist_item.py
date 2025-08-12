from odoo import api, fields, models
from odoo.exceptions import ValidationError

MAX_QUANTITY = 10


class SupermarketChecklistItem(models.Model):
    _name = "supermarket.checklist.item"
    _description = "Item de la Lista de Supermercado"

    sequence = fields.Integer(default=10)
    product_id = fields.Many2one(
        "supermarket.product", string="Producto", required=True
    )
    product_description = fields.Text(related="product_id.description")
    quantity = fields.Integer(string="Cantidad", required=True, default=1)
    purchased = fields.Boolean(string="Comprado", default=False)
    checklist_id = fields.Many2one(
        "supermarket.checklist",
        string="Lista de Supermercado",
        required=True,
        ondelete="cascade",
    )

    _sql_constraints = [
        (
            "unique_product_per_checklist",
            "UNIQUE(checklist_id, product_id)",
            "Hay productos duplicados en la lista.",
        )
    ]

    def _get_max_quantity(self):
        """Método para obtener el máximo para la cantidad de un item"""

        max_items = int(
            self.env["ir.config_parameter"].get_param(
                "supermarket_checklist_items.max_quantity"
            )
        )
        if not max_items:
            max_items = MAX_QUANTITY
        return max_items

    def write(self, vals):
        """Sobreescritura del método write para realizar validaciones"""

        for record in self:
            self.env["supermarket.checklist"]._check_user(record.checklist_id.user_id)
            if "product_id" in vals and record.checklist_id.state != "draft":
                raise ValidationError(
                    "No puedes editar los items de la lista cuando la lista no está en estado 'Borrador'"
                )
            if "purchased" in vals and record.checklist_id.state == "draft":
                record.checklist_id.state = "in_progress"
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        """Sobreescritura del método create para realizar validaciones"""

        records = super().create(vals_list)
        max_items = self._get_max_quantity()
        for record in records:
            if not record.quantity or record.quantity <= 0:
                raise ValidationError("El item debe tener al menos una unidad")
            if record.quantity > max_items:
                raise ValidationError(
                    "No se pueden agregar más de 10 items de un mismo producto"
                )
        return records

    def check_purchased(self):
        """Método para marcar que se ha comprado el item"""

        for record in self:
            self.env["supermarket.checklist"]._check_user(record.checklist_id.user_id)
            record.purchased = not record.purchased
            if all(item.purchased for item in record.checklist_id.item_ids):
                record.checklist_id.state = "done"

    def decrement_quantity(self):
        """Método para decrementar el valor de cantidad"""

        for record in self:
            if record.quantity == 1:
                raise ValidationError("La cantidad no puede ser menor a 1")
            record.quantity -= 1

    def increment_quantity(self):
        """Método para incrementar el valor de cantidad"""

        max_items = self._get_max_quantity()
        for record in self:
            if record.quantity == max_items:
                raise ValidationError(
                    "No se pueden agregar más de 10 items de un mismo producto"
                )
            record.quantity += 1

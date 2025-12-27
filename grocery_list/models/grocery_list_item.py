from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError


class GroceryListItem(models.Model):
    _name = "grocery.list.item"
    _description = "Item de Lista de Supermercado"
    _order = "is_purchased, product_id"

    list_id = fields.Many2one(
        "grocery.list", string="Lista", required=True, ondelete="cascade"
    )
    product_id = fields.Many2one("product.product", string="Producto", required=True)
    quantity = fields.Float(string="Cantidad", required=True, default=1.0)
    is_purchased = fields.Boolean(string="Comprado", default=False)
    responsible_id = fields.Many2one(
        "res.users",
        string="Responsable",
        related="list_id.responsible_id",
        store=True,
        readonly=True,
    )
    can_edit_purchased = fields.Boolean(
        string="Puede Editar Comprado",
        compute="_compute_can_edit_purchased",
        store=False,
    )

    @api.depends_context("uid")
    @api.depends("responsible_id")
    def _compute_can_edit_purchased(self):
        for record in self:
            record.can_edit_purchased = record.responsible_id.id == self.env.user.id

    @api.model
    def create(self, vals):
        record = super().create(vals)
        return record

    def write(self, vals):
        if "is_purchased" in vals:
            for record in self:
                if record.list_id.responsible_id != self.env.user:
                    raise AccessError(
                        "Solo el responsable de la lista puede marcar items como comprados o no comprados."
                    )
        return super().write(vals)

    @api.constrains("quantity")
    def _check_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError("La cantidad debe ser mayor a cero.")

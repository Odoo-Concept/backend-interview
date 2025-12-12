from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class GroceryListLine(models.Model):
    _name = "grocery.list.line"
    _description = "Grocery List Line"
    _order = "sequence, id"

    list_id = fields.Many2one(
        "grocery.list", string="List", required=True, ondelete="cascade", index=True
    )
    grocery_product_id = fields.Many2one(
        "grocery.product",
        string="Product",
        required=True,
        ondelete="restrict",
        index=True,
    )
    quantity = fields.Float(
        default=1.0,
        required=True,
        digits=(16, 2),
        help="Quantity to purchase (e.g., 12, 1, 3, 2)",
    )
    uom_id = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        help="Unit of measure",
        compute="_compute_uom_id",
        store=True,
        readonly=False,
    )
    notes = fields.Text(help="Additional notes about this product")
    is_purchased = fields.Boolean(default=False, tracking=True)
    sequence = fields.Integer(default=10, help="Display order in the list")
    product_name = fields.Char(
        related="grocery_product_id.name",
        readonly=True,
        store=False,
    )
    product_category = fields.Char(
        string="Category",
        related="grocery_product_id.category",
        readonly=True,
        store=True,
    )
    has_real_product = fields.Boolean(
        string="Has Real Product",
        related="grocery_product_id.has_real_product",
        readonly=True,
        store=True,
    )
    real_product_id = fields.Many2one(
        "product.product",
        string="Real Product",
        related="grocery_product_id.product_id",
        readonly=True,
        store=False,
    )
    list_state = fields.Selection(
        related="list_id.state", string="List State", readonly=True, store=True
    )

    def get_uom_name(self):
        """Get UOM name using sudo to avoid access errors for portal users"""
        self.ensure_one()
        if self.uom_id:
            return self.uom_id.sudo().name
        return ""

    @api.depends("grocery_product_id.product_id.uom_id", "grocery_product_id")
    def _compute_uom_id(self):
        """Compute unit of measure from related product or use default.

        If the grocery product is linked to an Odoo product with a UOM,
        use that UOM. Otherwise, use the default UOM (Units).
        """
        default_uom = self.env.ref("uom.product_uom_unit", raise_if_not_found=False)
        for line in self:
            if (
                line.grocery_product_id.product_id
                and line.grocery_product_id.product_id.uom_id
            ):
                line.uom_id = line.grocery_product_id.product_id.uom_id
            elif not line.uom_id:
                line.uom_id = default_uom

    @api.constrains("is_purchased", "list_id")
    def _check_purchase_permission(self):
        """Ensure only responsible user can mark items as purchased.

        Allows marking as purchased in sudo mode (for admins) or
        if the current user is the responsible user of the list.
        """
        for line in self:
            if line.is_purchased and line.list_id.responsible_id != self.env.user:
                if not self.env.su and line.list_id.responsible_id != self.env.user:
                    raise ValidationError(
                        _(
                            "Only the responsible user of the list can mark "
                            "products as purchased."
                        )
                    )

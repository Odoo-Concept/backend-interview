from odoo import api, fields, models


class GroceryProduct(models.Model):
    _name = "grocery.product"
    _description = "Grocery Product"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "is_favorite desc, usage_count desc, name"

    name = fields.Char(
        string="Product Name",
        required=True,
        index=True,
        translate=True,
        help="Name of the product (e.g., Eggs, Rice, Milk, Coca Cola 3 liters)",
    )
    description = fields.Text(translate=True)
    category = fields.Char(
        help="Simple category (e.g., Fruits, Vegetables, Dairy, Beverages)",
    )
    barcode = fields.Char(
        index=True,
        help="Product barcode (optional, for quick scanning)",
    )
    product_id = fields.Many2one(
        "product.product",
        help=(
            "Optional link to real Odoo product. "
            "Only administrators can set this relationship."
        ),
        ondelete="set null",
        domain="[('type', '=', 'consu')]",
        groups="base.group_system",
    )
    usage_count = fields.Integer(
        string="Times Used",
        compute="_compute_usage_count",
        store=True,
        help="Number of times this product has been added to lists",
    )
    last_used_date = fields.Datetime(
        string="Last Used", compute="_compute_last_used_date", store=True
    )
    is_favorite = fields.Boolean(
        string="Favorite",
        default=False,
        help="Favorite products appear first in searches",
    )
    has_real_product = fields.Boolean(compute="_compute_has_real_product", store=True)
    product_uom = fields.Char(
        string="Unit of Measure",
        related="product_id.uom_id.name",
        readonly=True,
        store=False,
        help="Unit of measure from the real product (if linked)",
    )
    active = fields.Boolean(default=True)

    line_ids = fields.One2many(
        "grocery.list.line", "grocery_product_id", string="List Lines"
    )

    @api.depends("product_id")
    def _compute_has_real_product(self):
        """Compute if product has a linked real product"""
        for product in self:
            product.has_real_product = bool(product.product_id)

    @api.depends("line_ids")
    def _compute_usage_count(self):
        """Compute number of times product has been used"""
        for product in self:
            product.usage_count = len(product.line_ids)

    @api.depends("line_ids.list_id.date_created")
    def _compute_last_used_date(self):
        """Compute last date product was used"""
        for product in self:
            lines = product.line_ids.sorted(
                key=lambda line: line.list_id.date_created or False,
                reverse=True,
            )
            product.last_used_date = (
                lines[0].list_id.date_created if lines and lines[0].list_id else False
            )

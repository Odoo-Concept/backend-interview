from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

STATE_SELECTION = [
    ("draft", "Draft"),
    ("in_progress", "In Progress"),
    ("done", "Completed"),
]


class GroceryList(models.Model):
    _name = "grocery.list"
    _description = "Grocery List"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, tracking=True)
    
    responsible_id = fields.Many2one(
        "res.users",
          string="Responsible", 
          tracking=True , 
          required=True
    )

    state = fields.Selection(STATE_SELECTION, default="draft", tracking=True)
    line_ids = fields.One2many("grocery.list.item", "list_id", string="Items")

    total_items = fields.Integer(compute="_compute_stats", store=True)
    purchased_items = fields.Integer(compute="_compute_stats", store=True)
    progress = fields.Float(string="Progress (%)", compute="_compute_stats", store=True, digits=(16, 2))
    total_amount = fields.Monetary(string="Total Amount", compute="_compute_total_amount", store=True, currency_field="currency_id")
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id.id)
    color = fields.Integer("Color Index")

    def action_complete(self):
        self.write({"state": "done"})

    @api.depends("line_ids.subtotal")
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = sum(line.subtotal for line in rec.line_ids)

    @api.depends("line_ids.purchased", "line_ids.quantity")
    def _compute_stats(self):
        for rec in self:
            total = len(rec.line_ids)
            purchased = sum(1 for l in rec.line_ids if l.purchased)
            rec.total_items = total
            rec.purchased_items = purchased
            rec.progress = (purchased * 100.0 / total) if total else 0.0

    def action_set_draft(self):
        self.write({"state": "draft"})

    def action_start(self):
        self.write({"state": "in_progress"})


class GroceryListItem(models.Model):
    _name = "grocery.list.item"
    _description = "Grocery List Item"

    list_id = fields.Many2one("grocery.list", required=True, ondelete="cascade")
    product_id = fields.Many2one("product.product", required=True)
    quantity = fields.Float(default=1.0, required=True)
    price_unit = fields.Float(string="Unit Price", digits="Product Price")
    subtotal = fields.Monetary(string="Subtotal", compute="_compute_subtotal", store=True, currency_field="currency_id")

    
    purchased = fields.Boolean(string="Purchased", default=False)
    purchased_by = fields.Many2one("res.users", readonly=True)
    purchased_at = fields.Datetime(readonly=True)

    toggle_purchase_action = fields.Boolean(string="Mark / Unmark Purchase", compute="_compute_toggle_purchase", inverse="_inverse_toggle_purchase")

    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id.id)

    @api.depends("purchased")
    def _compute_toggle_purchase(self):
        """Refleja el estado actual de 'purchased'."""
        for rec in self:
            rec.toggle_purchase_action = rec.purchased

    def _inverse_toggle_purchase(self):
        """Cuando el usuario cambia el checkbox, ejecuta la acción."""
        for rec in self:
            rec.toggle_purchased()

    @api.depends("quantity", "price_unit")
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.quantity * rec.price_unit

    def toggle_purchased(self):
        """Valida permisos y alterna el estado de compra."""
        self._check_can_toggle()
        for line in self:
            if line.purchased:
                vals = {
                    "purchased": False,
                    "purchased_by": False,
                    "purchased_at": False,
                }
            else:
                vals = {
                    "purchased": True,
                    "purchased_by": self.env.user.id,
                    "purchased_at": fields.Datetime.now(),
                }
            super(GroceryListItem, line).write(vals)
        return True


    def _check_can_toggle(self):
        """Bloquea si el usuario no tiene permisos para marcar como comprado."""
        user = self.env.user
        is_manager = user.has_group("grocery_list.group_grocery_list_manager")
        is_user = user.has_group("grocery_list.group_grocery_list_user")

        for line in self:
            if is_user and not is_manager and line.list_id.responsible_id != user:
                raise AccessError(_(
                    "You cannot mark this item as purchased because you are not the responsible user."
                ))
            if not (is_user or is_manager):
                raise AccessError(_(
                    "You do not have permission to perform this action."
                ))
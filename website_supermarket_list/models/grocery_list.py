from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _


class GroceryList(models.Model):
    _name = "grocery.list"
    _description = "Grocery List"
    _order = "date_created desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="List Name",
        required=True,
        index=True,
        help="Descriptive name for the list (e.g., Weekly Shopping, Christmas List)",
    )
    responsible_id = fields.Many2one(
        "res.users",
        string="Responsible",
        required=True,
        default=lambda self: self.env.user,
        index=True,
        tracking=True,
        help="User responsible for this list",
    )
    store_id = fields.Many2one(
        "grocery.store",
        string="Store",
        required=True,
        index=True,
        tracking=True,
        help="Grocery store where the shopping will be done",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("in_progress", "In Progress"), ("done", "Completed")],
        default="draft",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many(
        "grocery.list.line", "list_id", string="Products", copy=True
    )
    total_items = fields.Integer(compute="_compute_totals", store=True)
    purchased_items = fields.Integer(compute="_compute_totals", store=True)
    pending_items = fields.Integer(compute="_compute_totals", store=True)
    progress = fields.Float(
        string="Progress (%)", compute="_compute_totals", store=True, digits=(12, 2)
    )
    date_created = fields.Datetime(default=fields.Datetime.now, readonly=True)
    date_started = fields.Datetime(readonly=True)
    date_completed = fields.Datetime(readonly=True)
    active = fields.Boolean(default=True)

    @api.depends("line_ids", "line_ids.is_purchased")
    def _compute_totals(self):
        """Compute totals and progress"""
        for record in self:
            record.total_items = len(record.line_ids)
            record.purchased_items = len(record.line_ids.filtered("is_purchased"))
            record.pending_items = record.total_items - record.purchased_items
            if record.total_items > 0:
                record.progress = (record.purchased_items / record.total_items) * 100.0
            else:
                record.progress = 0.0

    def action_set_in_progress(self):
        """Set list state to in progress"""
        for record in self:
            if not record.line_ids:
                raise UserError(
                    _(
                        "Cannot start shopping with an empty list. "
                        "Please add at least one product to the list first."
                    )
                )
            record.write(
                {"state": "in_progress", "date_started": fields.Datetime.now()}
            )

    def action_set_done(self):
        """Set list state to done"""
        for record in self:
            if any(not line.is_purchased for line in record.line_ids):
                raise UserError(
                    _(
                        "Cannot complete the list if there are pending items. "
                        "Please mark all items as purchased first."
                    )
                )
            record.write({"state": "done", "date_completed": fields.Datetime.now()})

    @api.constrains("state", "line_ids")
    def _check_completed_state(self):
        """Ensure list cannot be completed if there are pending items"""
        for record in self:
            if record.state == "done":
                pending = record.line_ids.filtered(lambda line: not line.is_purchased)
                if pending:
                    raise ValidationError(
                        _(
                            "Cannot complete the list if there are pending items. "
                            "Please mark all items as purchased first."
                        )
                    )

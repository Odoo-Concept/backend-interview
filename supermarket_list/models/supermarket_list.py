# models/supermarket_list.py
from odoo import models, fields, _
from odoo.exceptions import ValidationError

class SupermarketList(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = "supermarket.list"
    _description = "Supermarket List"

    name = fields.Char(string="Name", required=True)

    user_id = fields.Many2one(
        "res.users", string="User", tracking=True, required=True, default=lambda self: self.env.user
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
        ],
        string="State",
        default="draft",
        required=True,
        tracking=True,
    )

    line_ids = fields.One2many("list.line", "list_id", string="List Lines")

    is_responsible = fields.Boolean(
        string="Is Responsible",
        compute="_compute_is_responsible",
        store=False,
    )

    def _compute_is_responsible(self):
        for record in self:
            record.is_responsible = record.user_id == self.env.user

    def action_set_in_progress(self):
        for record in self:
            if record.user_id != self.env.user:
                raise ValidationError(_("Only the responsible user can start the list."))
            if not record.line_ids:
                raise ValidationError(_("Cannot start a list without items."))
            record.write({'state': "in_progress"})

    def action_confirm(self):
        for record in self: 
            if record.user_id != self.env.user:
                raise ValidationError(_("Only the responsible user can complete the list."))
            if record.write({'state': "done"}):
                continue
            if not record.line_ids:
                raise ValidationError(_("Cannot complete a list with no items."))
            not_purchased = record.line_ids.filtered(lambda l: l.state != "purchased")
            if not not_purchased:
                record.write({'state': "done"})
            else:
                products = ', '.join(not_purchased.mapped('product_id.name'))
                raise ValidationError(_(
                    "All items must be purchased to complete the list. Pending: %s" % products
                ))
    def action_reset_to_draft(self):
        for record in self:
            if record.user_id != self.env.user:
                raise ValidationError(_("Only the responsible user can reset the list to draft."))
            record.write({'state': "draft"})
            record.line_ids.write({'state': 'not_purchased'})
# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError


class SupermarketList(models.Model):
    _name = "supermarket.list"
    _description = "Supermarket List"
    _order = "id desc"

    name = fields.Char(required=True)
    responsible_id = fields.Many2one(
        "res.users",
        string="Responsible",
        required=True,
        default=lambda self: self.env.user,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
        ],
        default="draft",
        required=True,
    )
    line_ids = fields.One2many(
        "supermarket.list.line",
        "list_id",
        string="Items",
    )

    @api.constrains("state")
    def _check_done_requires_purchased(self):
        for record in self:
            if record.state == "done" and record.line_ids.filtered(
                lambda line: not line.is_purchased
            ):
                raise ValidationError(
                    _("A list cannot be completed while it has unpurchased items.")
                )

    def action_set_draft(self):
        self.write({"state": "draft"})
        return True

    def action_start(self):
        self.write({"state": "in_progress"})
        return True

    def action_mark_done(self):
        for record in self:
            if record.line_ids.filtered(lambda line: not line.is_purchased):
                raise ValidationError(
                    _("All items must be purchased before completing the list.")
                )
        self.write({"state": "done"})
        return True


class SupermarketListLine(models.Model):
    _name = "supermarket.list.line"
    _description = "Supermarket List Item"
    _order = "sequence, id"

    list_id = fields.Many2one(
        "supermarket.list",
        string="List",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(default=10)
    product_name = fields.Char(string="Product", required=True)
    quantity = fields.Float(string="Quantity", default=1.0)
    is_purchased = fields.Boolean(string="Purchased")
    is_responsible = fields.Boolean(
        string="Is Responsible",
        compute="_compute_is_responsible",
    )

    @api.depends("list_id.responsible_id")
    def _compute_is_responsible(self):
        current_user = self.env.user
        for line in self:
            line.is_responsible = line.list_id.responsible_id == current_user

    def _is_responsible_user(self, list_record):
        if self.env.su or self.env.user.has_group("base.group_system"):
            return True
        return list_record.responsible_id == self.env.user

    def _ensure_purchased_write_allowed(self):
        for line in self:
            if not self._is_responsible_user(line.list_id):
                raise AccessError(
                    _("Only the responsible user can mark items as purchased or not purchased.")
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            list_id = vals.get("list_id") or self.env.context.get("default_list_id")
            list_record = (
                self.env["supermarket.list"].browse(list_id).exists()
                if list_id
                else self.env["supermarket.list"]
            )
            if list_record:
                if vals.get("is_purchased") and not self._is_responsible_user(list_record):
                    raise AccessError(
                        _(
                            "Only the responsible user can mark items as purchased or not purchased."
                        )
                    )
                if list_record.state == "done" and not vals.get("is_purchased", False):
                    raise ValidationError(
                        _("Cannot add unpurchased items to a completed list.")
                    )
        return super().create(vals_list)

    def write(self, vals):
        if "is_purchased" in vals:
            self._ensure_purchased_write_allowed()
            if not vals.get("is_purchased", False):
                for line in self:
                    if line.list_id.state == "done":
                        raise ValidationError(
                            _("Cannot unpurchase items on a completed list.")
                        )
        return super().write(vals)

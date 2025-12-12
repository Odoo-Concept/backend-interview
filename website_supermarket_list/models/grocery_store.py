import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import remove_accents
from odoo.tools.translate import _
import logging

_logger = logging.getLogger(__name__)


class GroceryStore(models.Model):
    _name = "grocery.store"
    _description = "Grocery Store"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(
        string="Store Name",
        required=True,
        index=True,
        translate=True,
        help="Name of the grocery store (e.g., Walmart, Carrefour, Local Market)",
    )
    name_normalized = fields.Char(
        string="Normalized Name",
        compute="_compute_name_normalized",
        store=True,
        index=True,
        help="Normalized name for uniqueness verification",
    )
    description = fields.Text(translate=True)
    address = fields.Text(help="Main address of the grocery store")
    website = fields.Char()
    phone = fields.Char()
    email = fields.Char()
    active = fields.Boolean(default=True)
    total_lists = fields.Integer(
        compute="_compute_total_lists",
        help="Number of lists for this store",
    )

    _sql_constraints = [
        (
            "name_normalized_unique",
            "UNIQUE(name_normalized)",
            "A store with this name already exists. Please verify the name.",
        ),
    ]

    @api.depends("name")
    def _compute_name_normalized(self):
        """Compute normalized name for uniqueness checking"""
        for record in self:
            if record.name:
                record.name_normalized = self._normalize_name(record.name)
            else:
                record.name_normalized = False

    def _compute_total_lists(self):
        """Compute total number of lists for this store"""
        for record in self:
            record.total_lists = self.env["grocery.list"].search_count(
                [("store_id", "=", record.id)]
            )

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to validate uniqueness.

        Checks if a store with the same normalized name already exists
        before creating a new one.
        """
        for vals in vals_list:
            if "name" in vals and vals["name"]:
                normalized = self._normalize_name(vals["name"])
                vals["name_normalized"] = normalized

                existing = self.search([("name_normalized", "=", normalized)], limit=1)
                if existing:
                    raise ValidationError(
                        _(
                            'A store with the name "%s" already exists. '
                            "Please verify if it is the same store or "
                            "use a different name."
                        )
                        % existing.name
                    )

        return super().create(vals_list)

    def write(self, vals):
        """Override write to validate uniqueness.

        Checks if another store with the same normalized name exists,
        excluding the current record.
        """
        if "name" in vals and vals["name"]:
            normalized = self._normalize_name(vals["name"])
            vals["name_normalized"] = normalized

            existing = self.search(
                [("name_normalized", "=", normalized), ("id", "!=", self.id)], limit=1
            )
            if existing:
                raise ValidationError(
                    _(
                        'A store with the name "%s" already exists. '
                        "Please verify if it is the same store or use a different name."
                    )
                    % existing.name
                )

        return super().write(vals)

    @api.model
    def _normalize_name(self, name):
        """Normalize store name for uniqueness verification.

        Normalizes the name by:
        - Converting to lowercase
        - Trimming whitespace
        - Removing multiple spaces
        - Removing accents
        - Removing special characters (keeps letters, numbers, spaces)

        Args:
            name (str): Store name to normalize

        Returns:
            str: Normalized name or False if name is empty
        """
        if not name:
            return False

        normalized = name.lower().strip()
        normalized = re.sub(r"\s+", " ", normalized)

        try:
            normalized = remove_accents(normalized)
        except (ImportError, AttributeError):
            _logger.error("Error removing accents: %s", name)

        normalized = re.sub(r"[^\w\s]", "", normalized)

        return normalized

    @api.model
    def find_or_create(self, name):
        """Find existing store by name or create new one

        Args:
            name (str): Store name to find or create

        Returns:
            recordset: Found or newly created store
        """
        if not name:
            return self.browse()

        normalized = self._normalize_name(name)
        existing = self.search([("name_normalized", "=", normalized)], limit=1)

        if existing:
            return existing

        return self.sudo().create({"name": name})

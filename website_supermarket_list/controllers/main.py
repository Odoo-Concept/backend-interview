import logging

from odoo import http
from odoo.exceptions import AccessError, MissingError, UserError, ValidationError
from odoo.http import request
from odoo.tools.translate import _

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager

_logger = logging.getLogger(__name__)


class GroceryListPortal(CustomerPortal):
    _items_per_page = 20

    def _prepare_home_portal_values(self, counters):
        """Add grocery list count to portal home values"""
        values = super()._prepare_home_portal_values(counters)
        if "grocery_list_count" in counters or not counters:
            values["grocery_list_count"] = request.env["grocery.list"].search_count(
                [("responsible_id", "=", request.env.user.id)]
            )
        return values

    def _prepare_grocery_list_domain(self):
        """Prepare domain for grocery lists - only user's lists"""
        return [("responsible_id", "=", request.env.user.id)]

    def _prepare_searchbar_sortings(self):
        """Prepare sorting options for grocery lists"""
        return {
            "date": {"label": _("Newest"), "order": "date_created desc"},
            "name": {"label": _("Name"), "order": "name"},
            "store": {"label": _("Store"), "order": "store_id, name"},
            "state": {"label": _("State"), "order": "state, date_created desc"},
        }

    @http.route(
        ["/my/grocery-lists", "/my/grocery-lists/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_grocery_lists(
        self, page=1, sortby=None, filterby=None, search=None, **kw
    ):
        """Display user's grocery lists"""
        values = self._prepare_portal_layout_values()
        GroceryList = request.env["grocery.list"]
        domain = self._prepare_grocery_list_domain()
        if search:
            domain += [
                "|",
                ("name", "ilike", search),
                ("store_id.name", "ilike", search),
            ]

        if filterby == "draft":
            domain += [("state", "=", "draft")]
        elif filterby == "in_progress":
            domain += [("state", "=", "in_progress")]
        elif filterby == "done":
            domain += [("state", "=", "done")]

        searchbar_sortings = self._prepare_searchbar_sortings()
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]

        list_count = GroceryList.search_count(domain)

        pager = portal_pager(
            url="/my/grocery-lists",
            url_args={"sortby": sortby, "filterby": filterby, "search": search},
            total=list_count,
            page=page,
            step=self._items_per_page,
        )

        lists = GroceryList.search(
            domain, order=order, limit=self._items_per_page, offset=pager["offset"]
        )

        searchbar_filters = {
            "all": {"label": _("All"), "domain": []},
            "draft": {"label": _("Draft"), "domain": [("state", "=", "draft")]},
            "in_progress": {
                "label": _("In Progress"),
                "domain": [("state", "=", "in_progress")],
            },
            "done": {"label": _("Completed"), "domain": [("state", "=", "done")]},
        }

        values.update(
            {
                "lists": lists,
                "page_name": "grocery_list",
                "pager": pager,
                "searchbar_sortings": searchbar_sortings,
                "searchbar_filters": searchbar_filters,
                "sortby": sortby,
                "filterby": filterby or "all",
                "search": search,
                "default_url": "/my/grocery-lists",
            }
        )

        return request.render(
            "website_supermarket_list.portal_my_grocery_lists", values
        )

    @http.route(
        ["/my/grocery-lists/new"],
        type="http",
        auth="user",
        website=True,
        methods=["GET", "POST"],
    )
    def portal_grocery_list_new(self, **kw):
        """Create new grocery list"""
        values = self._prepare_portal_layout_values()
        GroceryList = request.env["grocery.list"]
        GroceryStore = request.env["grocery.store"]

        if request.httprequest.method == "POST":
            store_name = kw.get("store_name", "").strip()
            list_name = kw.get("list_name", "").strip()

            if not list_name:
                values["error"] = _("List name is required.")
                values["error_message"] = _("Please provide a name for your list.")
            elif not store_name:
                values["error"] = _("Store is required.")
                values["error_message"] = _("Please select or create a store.")
            else:
                try:
                    store = GroceryStore.find_or_create(store_name)
                    new_list = GroceryList.create(
                        {
                            "name": list_name,
                            "store_id": store.id,
                            "responsible_id": request.env.user.id,
                            "state": "draft",
                        }
                    )

                    return request.redirect(
                        f"/my/grocery-lists/{new_list.id}?mode=edit"
                    )

                except ValidationError as e:
                    values["error"] = str(e)
                    values["error_message"] = str(e)
                except Exception as e:
                    values["error"] = _("Error creating list.")
                    values["error_message"] = str(e)

        stores = GroceryStore.search([("active", "=", True)], limit=50, order="name")
        uoms = (
            request.env["uom.uom"]
            .sudo()
            .search([("active", "=", True)], limit=50, order="name")
        )

        values.update(
            {
                "page_name": "grocery_list",
                "stores": stores,
                "uoms": uoms,
                "list_name": kw.get("list_name", ""),
                "store_name": kw.get("store_name", ""),
            }
        )

        return request.render(
            "website_supermarket_list.portal_grocery_list_new", values
        )

    @http.route(
        ["/my/grocery-lists/<int:list_id>"],
        type="http",
        auth="user",
        website=True,
        methods=["GET"],
    )
    def portal_grocery_list(self, list_id=None, mode="view", **kw):
        """View or edit grocery list"""
        values = self._prepare_portal_layout_values()
        list_record = request.env["grocery.list"].browse(list_id)
        if list_record.responsible_id != request.env.user:
            return request.redirect("/my/grocery-lists")
        uoms = (
            request.env["uom.uom"]
            .sudo()
            .search([("active", "=", True)], limit=50, order="name")
        )

        effective_mode = mode or "view"
        if list_record.state == "in_progress":
            effective_mode = "view"

        values.update(
            {
                "grocery_list": list_record,
                "page_name": "grocery_list",
                "mode": effective_mode,
                "uoms": uoms,
            }
        )

        return request.render("website_supermarket_list.portal_grocery_list", values)

    @http.route(
        ["/my/grocery-lists/<int:list_id>/action"],
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def portal_grocery_list_action(self, list_id=None, action=None, **kw):
        """Change list state (set_in_progress, set_done)"""
        list_record = request.env["grocery.list"].browse(list_id)
        if list_record.responsible_id != request.env.user:
            return request.redirect("/my/grocery-lists")

        mode = kw.get("mode", "view")
        try:
            if action == "set_in_progress":
                list_record.action_set_in_progress()
            elif action == "set_done":
                list_record.action_set_done()
        except UserError as e:
            return request.redirect(
                f"/my/grocery-lists/{list_id}?mode={mode}&error={str(e)}"
            )

        return request.redirect(f"/my/grocery-lists/{list_id}?mode={mode}")

    @http.route(
        ["/my/grocery-lists/<int:list_id>/add-product"],
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def portal_grocery_list_add_product(self, list_id=None, **kw):
        """Add product to list"""
        GroceryList = request.env["grocery.list"]

        try:
            list_record = GroceryList.browse(list_id)
            if list_record.responsible_id != request.env.user:
                return request.redirect("/my/grocery-lists")

            if list_record.state == "done":
                redirect_mode = "view" if list_record.state == "in_progress" else "edit"
                return request.redirect(
                    f"/my/grocery-lists/{list_id}?mode={redirect_mode}&error="
                    + _("Cannot add products to a completed list.")
                )

            product_id = kw.get("product_id")
            if not product_id:
                redirect_mode = "view" if list_record.state == "in_progress" else "edit"
                return request.redirect(
                    f"/my/grocery-lists/{list_id}?mode={redirect_mode}&error="
                    + _("Please select or create a product.")
                )

            try:
                quantity = float(kw.get("quantity", 1.0))
                uom_id = kw.get("uom_id")
                notes = kw.get("notes", "").strip()

                if not uom_id:
                    default_uom = request.env.ref(
                        "uom.product_uom_unit", raise_if_not_found=False
                    )
                    uom_id = default_uom.id if default_uom else False

                GroceryListLine = request.env["grocery.list.line"]
                GroceryListLine.sudo().create(
                    {
                        "list_id": list_id,
                        "grocery_product_id": int(product_id),
                        "quantity": quantity,
                        "uom_id": int(uom_id) if uom_id else False,
                        "notes": notes,
                    }
                )
            except (ValueError, TypeError):
                redirect_mode = "view" if list_record.state == "in_progress" else "edit"
                return request.redirect(
                    f"/my/grocery-lists/{list_id}?mode={redirect_mode}&error="
                    + _("Invalid quantity value.")
                )
            except Exception:
                redirect_mode = "view" if list_record.state == "in_progress" else "edit"
                return request.redirect(
                    f"/my/grocery-lists/{list_id}?mode={redirect_mode}&error="
                    + _("Error adding product to list.")
                )

            redirect_mode = "view" if list_record.state == "in_progress" else "edit"
            return request.redirect(f"/my/grocery-lists/{list_id}?mode={redirect_mode}")

        except (AccessError, MissingError):
            return request.redirect("/my/grocery-lists")
        except Exception as e:
            return request.redirect(f"/my/grocery-lists/{list_id}?error={str(e)}")

    @http.route(
        ["/my/grocery-lists/<int:list_id>/delete-line"],
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def portal_grocery_list_delete_line(self, list_id=None, line_id=None, **kw):
        """Delete line from list"""
        GroceryList = request.env["grocery.list"]

        try:
            list_record = GroceryList.browse(list_id)
            if list_record.responsible_id != request.env.user:
                return request.redirect("/my/grocery-lists")

            if list_record.state == "in_progress":
                return request.redirect(
                    f"/my/grocery-lists/{list_id}?mode=view&error="
                    + _(
                        "Cannot delete list items while shopping is in progress. "
                        "You can only add new products."
                    )
                )

            if line_id:
                request.env["grocery.list.line"].browse(int(line_id)).unlink()

            mode = kw.get("mode", "edit")
            return request.redirect(f"/my/grocery-lists/{list_id}?mode={mode}")

        except (AccessError, MissingError):
            return request.redirect("/my/grocery-lists")
        except Exception as e:
            return request.redirect(f"/my/grocery-lists/{list_id}?error={str(e)}")

    @http.route(
        ["/my/grocery-lists/<int:list_id>/update-lines"],
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def portal_grocery_list_update_lines(self, list_id=None, **kw):
        """Update line quantities and UOMs"""
        GroceryList = request.env["grocery.list"]

        try:
            list_record = GroceryList.browse(list_id)
            if list_record.responsible_id != request.env.user:
                return request.redirect("/my/grocery-lists")

            if list_record.state == "in_progress":
                return request.redirect(
                    f"/my/grocery-lists/{list_id}?mode=view&error="
                    + _(
                        "Cannot edit list items while shopping is in progress. "
                        "You can only add new products."
                    )
                )

            GroceryListLine = request.env["grocery.list.line"]
            for key, value in kw.items():
                if key.startswith("quantity_"):
                    line_id = int(key.replace("quantity_", ""))
                    line = GroceryListLine.browse(line_id)
                    if line.list_id == list_record:
                        try:
                            line.quantity = float(value)
                        except (ValueError, TypeError):
                            _logger.error("Invalid quantity value: %s", value)
                elif key.startswith("uom_id_"):
                    line_id = int(key.replace("uom_id_", ""))
                    line = GroceryListLine.browse(line_id)
                    if line.list_id == list_record:
                        try:
                            uom_id = int(value.strip()) if value.strip() else False
                            if uom_id:
                                uom = request.env["uom.uom"].browse(uom_id)
                                if uom.exists():
                                    line.uom_id = uom_id
                            else:
                                default_uom = request.env.ref(
                                    "uom.product_uom_unit", raise_if_not_found=False
                                )
                                if default_uom:
                                    line.uom_id = default_uom.id
                        except (ValueError, TypeError):
                            _logger.error("Invalid UOM value: %s", value)

            mode = kw.get("mode", "edit")
            return request.redirect(f"/my/grocery-lists/{list_id}?mode={mode}")

        except (AccessError, MissingError):
            return request.redirect("/my/grocery-lists")
        except Exception as e:
            return request.redirect(f"/my/grocery-lists/{list_id}?error={str(e)}")

    @http.route(
        ["/my/grocery-lists/<int:list_id>/toggle-purchased"],
        type="json",
        auth="user",
        website=True,
        methods=["POST"],
        csrf=False,
    )
    def toggle_purchased(self, list_id=None, line_id=None, **kw):
        """Toggle purchased status of a line item"""
        try:
            GroceryList = request.env["grocery.list"]
            list_record = GroceryList.browse(list_id)

            if list_record.responsible_id != request.env.user:
                return {
                    "error": {
                        "message": _(
                            "Only the responsible user can mark items as purchased."
                        )
                    }
                }

            line = request.env["grocery.list.line"].browse(line_id)
            if line.list_id != list_record:
                return {"error": {"message": _("Invalid line.")}}

            line.is_purchased = not line.is_purchased

            list_record.invalidate_recordset(
                ["total_items", "purchased_items", "pending_items", "progress"]
            )

            return {
                "success": True,
                "is_purchased": line.is_purchased,
                "total_items": list_record.total_items,
                "purchased_items": list_record.purchased_items,
                "pending_items": list_record.pending_items,
                "progress": list_record.progress,
            }
        except Exception as e:
            return {"error": {"message": str(e)}}

    @http.route(
        ["/grocery/search-products"],
        type="json",
        auth="user",
        website=True,
        methods=["POST"],
        csrf=False,
    )
    def search_products(self, term="", limit=20, **kw):
        """Search products for autocomplete"""
        if not term or len(term) < 2:
            return {"products": []}

        GroceryProduct = request.env["grocery.product"]
        domain = [
            ("active", "=", True),
            "|",
            ("name", "ilike", term),
            ("category", "ilike", term),
        ]

        products = GroceryProduct.search(
            domain, limit=limit, order="is_favorite desc, usage_count desc, name"
        )

        return {
            "products": [
                {
                    "id": p.id,
                    "name": p.name,
                    "category": p.category or "",
                    "is_favorite": p.is_favorite,
                    "usage_count": p.usage_count,
                }
                for p in products
            ]
        }

    @http.route(
        ["/grocery/search-stores"],
        type="json",
        auth="user",
        website=True,
        methods=["POST"],
        csrf=False,
    )
    def search_stores(self, term="", limit=20, **kw):
        """Search stores for autocomplete"""
        if not term or len(term) < 2:
            return {"stores": []}

        GroceryStore = request.env["grocery.store"]
        domain = [("active", "=", True), ("name", "ilike", term)]

        stores = GroceryStore.search(domain, limit=limit, order="name")

        return {
            "stores": [
                {
                    "id": s.id,
                    "name": s.name,
                    "address": s.address or "",
                }
                for s in stores
            ]
        }

    @http.route(
        ["/grocery/create-product"],
        type="json",
        auth="user",
        website=True,
        methods=["POST"],
        csrf=False,
    )
    def create_product(self, name="", category="", **kw):
        """Create a new grocery product"""
        if not name or not name.strip():
            return {"error": {"message": _("Product name is required.")}}

        try:
            GroceryProduct = request.env["grocery.product"]
            product = GroceryProduct.create(
                {
                    "name": name.strip(),
                    "category": category.strip() if category else False,
                }
            )

            return {
                "success": True,
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "category": product.category or "",
                },
            }
        except Exception as e:
            return {"error": {"message": str(e)}}
